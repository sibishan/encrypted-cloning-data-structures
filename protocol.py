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
            self.A[i] = QuantumRegister(1, name=f'A{i}')

        self.S = {}
        self.N = {}
        for i in range(self.num_qubits):
            for j in range(self.num_clones):
                self.S[i,j] = QuantumRegister(1, name=f'S_{i}_{j}')
                self.N[i,j] = QuantumRegister(1, name=f'N_{i}_{j}')

        self.qc = self._init_circuit()
        self.count = 0


    def _init_circuit(self):
        qc = QuantumCircuit(*self.A.values(), *self.S.values(), *self.N.values())
        # Bell pairs  |ϕ⟩_{S_j N_j}  for every (i, j) group
        for i in range(self.num_qubits):
            for j in range(self.num_clones):
                qc.h(self.S[i, j][0])
                qc.cx(self.S[i, j][0], self.N[i, j][0])
        qc.barrier(label='init')
        return qc

    def store_qubit(self, qc):
        if qc.num_qubits != 1:
            raise ValueError("Input must be a single-qubit circuit")
        if self.count >= self.num_qubits-1:
            raise OverflowError("No more qubits can be stored")
        
        self.qc = self.qc.compose(qc, qubits=[self.A[self.count][0]])
        # Encrypted Cloning  U_enc = exp(-iπ/4 σ1^A⊗σ1^S…) · exp(-iπ/4 σ3^A⊗σ3^S…)
        self._apply_zz_factor(self.count)   # exp(-iπ/4 σ3⊗σ3⊗…)  — ZZ interaction
        self._apply_xx_factor(self.count)   # exp(-iπ/4 σ1⊗σ1⊗…)  — XX interaction (H-sandwiched)
        self.count += 1
    
    def decrypt_clone(self, qc):
        pass

    def _apply_zz_factor(self, index):
        # Forward: fan parity of A into the S chain
        self.qc.cx(self.A[index][0], self.S[index, 0][0])
        for i in range(self.num_clones-1):
            self.qc.cx(self.S[index, i][0], self.S[index, i + 1][0])
        
        # Rz(2t) with t = π/4  →  Rz(π/2) on the last S qubit
        self.qc.rz(np.pi/2, self.S[index, self.num_clones - 1][0])

        # Backward: uncompute the parity ladder
        for i in range(self.num_clones-1, 0, -1):
            self.qc.cx(self.S[index, i - 1][0], self.S[index, i][0])
        self.qc.cx(self.A[index][0], self.S[index, 0][0])

    def _apply_xx_factor(self, index):
        # H on A and all S in this group
        self.qc.h(self.A[index][0])
        for i in range(self.num_clones):
            self.qc.h(self.S[index, i][0])

        self._apply_zz_factor(index)

        # H again to return to Z basis
        self.qc.h(self.A[index][0])
        for i in range(self.num_clones):
            self.qc.h(self.S[index, i][0])

    # def _build_decryption_unitary(self, n: int) -> np.ndarray:
    #     alpha = np.array([1, 1j, -(1j) ** (n + 1), 1j], dtype=complex)
    #     phi_vec = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

    #     dim = 2 ** (n + 1)
    #     U_dec = np.zeros((dim, dim), dtype=complex)

    #     for mu in range(4):
    #         # |ϕ_μ⟩ = (σ_μ ⊗ I)|ϕ⟩
    #         phi_mu = np.kron(self.sigma[mu], np.eye(2)) @ phi_vec
    #         proj_mu = np.outer(phi_mu, phi_mu.conj())

    #         # ⊗_{j=2}^{n} σ_μ^T  (scalar identity if n=1)
    #         if n > 1:
    #             noise_op = self.sigma[mu].T.copy()
    #             for _ in range(n - 2):
    #                 noise_op = np.kron(noise_op, self.sigma[mu].T)
    #         else:
    #             noise_op = np.array([[1]], dtype=complex)

    #         U_dec += alpha[mu] * np.kron(proj_mu, noise_op)

    #     return U_dec

    # def _apply_decryption(self):
    #     for i in range(self.num_qubits):
    #         base = i * self.num_clones
    #         U_dec = self._build_decryption_unitary(self.num_clones)

    #         if self.num_clones > 1:
    #             dec_qubits = [self.N[base + k] for k in range(self.num_clones - 1, -1, -1)] + [self.S[base]]
    #         else:
    #             dec_qubits = [self.N[base], self.S[base]]

    #         self.qc.unitary(U_dec, dec_qubits, label=f'U_dec({self.num_clones})')