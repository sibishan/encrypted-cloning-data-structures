from qiskit import QuantumRegister, QuantumCircuit

import numpy as np


class Protocol:
    def __init__(self, num_qubits=0, num_clones=0):
        self.num_qubits = num_qubits
        self.num_clones = num_clones
        self.sigma = [
            np.eye(2, dtype=complex),                           # σ_0 = I
            np.array([[0, 1],  [1, 0]],  dtype=complex),        # σ_1 = X
            np.array([[0, -1j],[1j, 0]], dtype=complex),        # σ_2 = Y
            np.array([[1, 0],  [0, -1]], dtype=complex),        # σ_3 = Z
        ]
        
        self.A = {}
        for i in range(self.num_qubits):
            self.A[i] = {
                'reg': QuantumRegister(1, name=f'A{i}'),
                'in_use': False
            }

        self.S = {}
        self.N = {}
        for i in range(self.num_qubits):
            for j in range(self.num_clones):
                self.S[i, j] = {
                    'reg': QuantumRegister(1, name=f'S_{i}_{j}'),
                    'in_use': False
                }
                self.N[i, j] = {
                    'reg': QuantumRegister(1, name=f'N_{i}_{j}'),
                    'in_use': False
                }

        self.qc = self._init_circuit()


    def _init_circuit(self):
        qc = QuantumCircuit(
            *[self.A[i]['reg'] for i in self.A],
            *[self.S[k]['reg'] for k in self.S],
            *[self.N[k]['reg'] for k in self.N]
        )
        for i in range(self.num_qubits):
            for j in range(self.num_clones):
                qc.h(self._s(i, j))
                qc.cx(self._s(i, j), self._n(i, j))
        qc.barrier()
        return qc

    def store_qubit(self, qc, index):
        if index >= self.num_qubits or index < 0:
            raise IndexError(f"{index} of Qubit A is out of bounds")
        if self._a_in_use(index):
            raise IndexError(f"Qubit A_{index} already in use")

        for i in range(self.num_clones):
            if self._s_in_use(index, i) or self._n_in_use(index, i):
                raise IndexError(f"Clone S_{index}_{i} qubits already in use")

        self.qc = self.qc.compose(qc, qubits=[self._a(index)])
        self._a_in_use(index, True)

        # Encrypted Cloning  U_enc = exp(-iπ/4 σ1^A⊗σ1^S…) · exp(-iπ/4 σ3^A⊗σ3^S…)
        self._apply_zz_factor(index)
        self._apply_xx_factor(index)

        for i in range(self.num_clones):
            self._s_in_use(index, i, True)
            self._n_in_use(index, i, True)

    def _apply_zz_factor(self, index):
        self.qc.cx(self._a(index), self._s(index, 0))
        for i in range(self.num_clones - 1):
            self.qc.cx(self._s(index, i), self._s(index, i + 1))

        self.qc.rz(np.pi / 2, self._s(index, self.num_clones - 1))

        for i in range(self.num_clones - 1, 0, -1):
            self.qc.cx(self._s(index, i - 1), self._s(index, i))
        self.qc.cx(self._a(index), self._s(index, 0))

    def _apply_xx_factor(self, index):
        # H on A and all S in this group
        self.qc.h(self._a(index))
        for i in range(self.num_clones):
            self.qc.h(self._s(index, i))

        self._apply_zz_factor(index)

        # H again to return to Z basis
        self.qc.h(self._a(index))
        for i in range(self.num_clones):
            self.qc.h(self._s(index, i))

    def _a(self, i):
        return self.A[i]['reg'][0]

    def _s(self, i, j):
        return self.S[i, j]['reg'][0]

    def _n(self, i, j):
        return self.N[i, j]['reg'][0]
    
    def _a_in_use(self, i, val=None):
        if val is not None:
            self.A[i]['in_use'] = val
        return self.A[i]['in_use']

    def _s_in_use(self, i, j, val=None):
        if val is not None:
            self.S[i, j]['in_use'] = val
        return self.S[i, j]['in_use']

    def _n_in_use(self, i, j, val=None):
        if val is not None:
            self.N[i, j]['in_use'] = val
        return self.N[i, j]['in_use']
    