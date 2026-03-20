#Being built by Joshua the Architect, master of all creation

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.quantum_info import (
    random_statevector, Statevector,
    partial_trace, state_fidelity
)
import numpy as np

class Protocol:
    def __init__(self, n_qubits_to_clone: int, n_clones: int):
        self.n_qubits_to_clone = n_qubits_to_clone
        self.n_clones = n_clones
        self.noise_qubits = n_clones
        self.sigma = [
            np.eye(2, dtype=complex),                          # σ_0 = I
            np.array([[0, 1], [1, 0]], dtype=complex),         # σ_1 = X
            np.array([[0, -1j], [1j, 0]], dtype=complex),      # σ_2 = Y
            np.array([[1, 0], [0, -1]], dtype=complex)          # σ_3 = Z
        ]
        self.A = QuantumRegister(n_qubits_to_clone, 'A')
        self.S = QuantumRegister(n_qubits_to_clone * n_clones, 'S')
        self.N = QuantumRegister(n_qubits_to_clone * n_clones, 'N')
        self.qc = None
    
    def build_circuit(self, psi=None, seed=42) -> QuantumCircuit:
        if psi is None:
            psi = random_statevector(2, seed=seed)

        self.qc = QuantumCircuit(self.A, self.S, self.N)

        # === Initialize A ===
        for i in range(self.n_qubits_to_clone):
            self.qc.initialize(psi, self.A[i])

        # === Bell pairs (S[idx], N[idx]) ===
        for i in range(self.n_qubits_to_clone):
            for j in range(self.n_clones):
                idx = i * self.n_clones + j
                self.qc.h(self.S[idx])
                self.qc.cx(self.S[idx], self.N[idx])

        self.qc.barrier(label='encrypt')
        self._build_cycle()
        self._build_cycle()
        self.qc.barrier(label='decrypt')

        for i in range(self.n_qubits_to_clone):
            base = i * self.n_clones
            U_dec = self._build_decryption_unitary(self.n_clones)

            # Qiskit LSB ordering: [N[self.n_clones - 1], ..., N[0], S[base]]
            if self.n_clones > 1:
                dec_qubits = [self.N[base + k] for k in range(self.n_clones - 1, -1, -1)] + [self.S[base]]
            else:
                dec_qubits = [self.N[base], self.S[base]]

            self.qc.unitary(U_dec, dec_qubits, label=f'U_dec({self.n_clones})')

        return self.qc

    def _build_cycle(self):
        for i in range(self.n_qubits_to_clone):
            base = i * self.n_clones

            # Forward pass
            self.qc.cx(self.A[i], self.S[base])
            for j in range(self.n_clones - 1):
                self.qc.cx(self.S[base + j], self.S[base + j + 1])

            # Rz on last S in group
            self.qc.rz(np.pi / 2, self.S[base + self.n_clones - 1])

            # Backward pass
            for j in reversed(range(self.n_clones - 1)):
                self.qc.cx(self.S[base + j], self.S[base + j + 1])
            self.qc.cx(self.A[i], self.S[base])

            # Ending gates — applied bottom to top
            self.qc.h(self.S[base + self.n_clones - 1])             # H on last S
            for j in range(self.n_clones - 1):
                self.qc.h(self.S[base + j])
            self.qc.h(self.A[i])

    def _build_decryption_unitary(self, n: int) -> np.ndarray:
        alpha = np.array([1, 1j, -(1j) ** (n + 1), 1j], dtype=complex)
        phi_vec = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

        dim = 2 ** (n + 1)
        U_dec = np.zeros((dim, dim), dtype=complex)

        for mu in range(4):
            phi_mu = np.kron(self.sigma[mu], np.eye(2)) @ phi_vec
            proj_mu = np.outer(phi_mu, phi_mu.conj())

            if n > 1:
                noise_op = self.sigma[mu].T.copy()
                for _ in range(n - 2):
                    noise_op = np.kron(noise_op, self.sigma[mu].T)
            else:
                noise_op = np.array([[1]], dtype=complex)

            U_dec += alpha[mu] * np.kron(proj_mu, noise_op)

        return U_dec
