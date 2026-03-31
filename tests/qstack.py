import os
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import random_statevector

from qstack import QStack

OUT_DIR = "tests/out/qstack"


def make_state(label: str) -> QuantumCircuit:
    """Create a 1-qubit circuit initialized to a random state.
    Adds a label so you can visually distinguish different states."""
    qc = QuantumCircuit(1)
    psi = random_statevector(2)
    qc.initialize(psi, 0)
    qc.metadata = {"label": label}
    return qc


def save(stack, test_name: str, step: str):
    """Draw the stack circuit and save to tests/out/qstack/<test>/<step>.png"""
    path = os.path.join(OUT_DIR, test_name)
    os.makedirs(path, exist_ok=True)
    fig = stack.draw()
    fig.savefig(os.path.join(path, f"{step}.png"), bbox_inches="tight")
    plt.close(fig)
    print(f"  saved: {path}/{step}.png")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 1 — Push single
#  Expected: empty → [A]
# ═══════════════════════════════════════════════════════════════════════════

def test_01_push_single():
    print("\n── Test 01: Push single ──")
    s = QStack(num_qubits=3, num_clones=1)
    A = make_state("A")

    save(s, "01_push_single", "0_empty")

    s.push(A)
    save(s, "01_push_single", "1_A")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 2 — Push multiple (LIFO order)
#  Expected: push A, B, C → stack top is C
#            [A] → [A, B] → [A, B, C]
# ═══════════════════════════════════════════════════════════════════════════

def test_02_push_multiple():
    print("\n── Test 02: Push multiple ──")
    s = QStack(num_qubits=3, num_clones=1)
    A, B, C = [make_state(l) for l in "ABC"]

    s.push(A)
    save(s, "02_push_multiple", "0_A")

    s.push(B)
    save(s, "02_push_multiple", "1_A_B")

    s.push(C)
    save(s, "02_push_multiple", "2_A_B_C")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 3 — Pop single
#  Expected: [A, B, C] → pop → [A, B]  (C removed from top)
# ═══════════════════════════════════════════════════════════════════════════

def test_03_pop_single():
    print("\n── Test 03: Pop single ──")
    s = QStack(num_qubits=3, num_clones=1)
    A, B, C = [make_state(l) for l in "ABC"]

    s.push(A)
    s.push(B)
    s.push(C)
    save(s, "03_pop_single", "0_A_B_C")

    s.pop()
    save(s, "03_pop_single", "1_A_B")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 4 — Pop all (drain the stack)
#  Expected: [A, B, C] → [A, B] → [A] → []
# ═══════════════════════════════════════════════════════════════════════════

def test_04_pop_all():
    print("\n── Test 04: Pop all ──")
    s = QStack(num_qubits=3, num_clones=1)
    A, B, C = [make_state(l) for l in "ABC"]

    s.push(A)
    s.push(B)
    s.push(C)
    save(s, "04_pop_all", "0_A_B_C")

    s.pop()
    save(s, "04_pop_all", "1_A_B")

    s.pop()
    save(s, "04_pop_all", "2_A")

    s.pop()
    save(s, "04_pop_all", "3_empty")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 5 — Push after pop (reuse freed slot)
#  Expected: [A, B] → pop → [A] → push C → [A, C]
# ═══════════════════════════════════════════════════════════════════════════

def test_05_push_after_pop():
    print("\n── Test 05: Push after pop ──")
    s = QStack(num_qubits=3, num_clones=1)
    A, B, C = [make_state(l) for l in "ABC"]

    s.push(A)
    s.push(B)
    save(s, "05_push_after_pop", "0_A_B")

    s.pop()
    save(s, "05_push_after_pop", "1_A")

    s.push(C)
    save(s, "05_push_after_pop", "2_A_C")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 6 — Push-pop-push cycle
#  Expected: push A → pop → push B → stack has only [B]
#            Verifies old state A is gone, not lingering
# ═══════════════════════════════════════════════════════════════════════════

def test_06_push_pop_push_cycle():
    print("\n── Test 06: Push-pop-push cycle ──")
    s = QStack(num_qubits=3, num_clones=1)
    A, B = make_state("A"), make_state("B")

    s.push(A)
    save(s, "06_cycle", "0_A")

    s.pop()
    save(s, "06_cycle", "1_empty")

    s.push(B)
    save(s, "06_cycle", "2_B")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 7 — Fill to capacity
#  Expected: push A, B, C, D into a size-4 stack → all slots filled
# ═══════════════════════════════════════════════════════════════════════════

def test_07_fill_to_capacity():
    print("\n── Test 07: Fill to capacity ──")
    s = QStack(num_qubits=4, num_clones=1)
    A, B, C, D = [make_state(l) for l in "ABCD"]

    s.push(A)
    s.push(B)
    s.push(C)
    s.push(D)
    save(s, "07_full", "0_A_B_C_D")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 8 — LIFO ordering check
#  Expected: push A, B, C → pop should remove C first
#            then pop removes B → only A remains
# ═══════════════════════════════════════════════════════════════════════════

def test_08_lifo_order():
    print("\n── Test 08: LIFO ordering ──")
    s = QStack(num_qubits=4, num_clones=1)
    A, B, C = [make_state(l) for l in "ABC"]

    s.push(A)
    s.push(B)
    s.push(C)
    save(s, "08_lifo", "0_A_B_C")

    s.pop()  # removes C
    save(s, "08_lifo", "1_A_B")

    s.pop()  # removes B
    save(s, "08_lifo", "2_A")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 9 — Interleaved push and pop
#  Expected: push A → push B → pop → push C → push D → pop
#            [A] → [A,B] → [A] → [A,C] → [A,C,D] → [A,C]
# ═══════════════════════════════════════════════════════════════════════════

def test_09_interleaved():
    print("\n── Test 09: Interleaved push/pop ──")
    s = QStack(num_qubits=4, num_clones=1)
    A, B, C, D = [make_state(l) for l in "ABCD"]

    s.push(A)
    save(s, "09_interleaved", "0_A")

    s.push(B)
    save(s, "09_interleaved", "1_A_B")

    s.pop()
    save(s, "09_interleaved", "2_A")

    s.push(C)
    save(s, "09_interleaved", "3_A_C")

    s.push(D)
    save(s, "09_interleaved", "4_A_C_D")

    s.pop()
    save(s, "09_interleaved", "5_A_C")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 10 — Same state pushed twice
#  Expected: push A, push A → two identical states on the stack
#            pop → one A remains
# ═══════════════════════════════════════════════════════════════════════════

def test_10_duplicate_state():
    print("\n── Test 10: Same state pushed twice ──")
    s = QStack(num_qubits=3, num_clones=1)
    A = make_state("A")

    s.push(A)
    s.push(A)
    save(s, "10_duplicate", "0_A_A")

    s.pop()
    save(s, "10_duplicate", "1_A")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 11 — With clones
#  Expected: same as basic push/pop but with clone slots visible
# ═══════════════════════════════════════════════════════════════════════════

def test_11_with_clones():
    print("\n── Test 11: With clones ──")
    s = QStack(num_qubits=3, num_clones=2)
    A, B = make_state("A"), make_state("B")

    s.push(A)
    s.push(B)
    save(s, "11_clones", "0_A_B")

    s.pop()
    save(s, "11_clones", "1_A")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST 12 — Full drain and refill
#  Expected: fill → drain completely → refill with different states
#            Verifies no stale state leaks through
# ═══════════════════════════════════════════════════════════════════════════

def test_12_drain_and_refill():
    print("\n── Test 12: Drain and refill ──")
    s = QStack(num_qubits=3, num_clones=1)
    A, B, C = [make_state(l) for l in "ABC"]
    X, Y = make_state("X"), make_state("Y")

    s.push(A)
    s.push(B)
    s.push(C)
    save(s, "12_drain_refill", "0_A_B_C")

    s.pop()
    s.pop()
    s.pop()
    save(s, "12_drain_refill", "1_empty")

    s.push(X) # this should work because when we pop the stored qubit comes back A{index} so it is still occupied
    s.push(Y) # this should work because when we pop the stored qubit comes back A{index} so it is still occupied
    save(s, "12_drain_refill", "2_X_Y")


# ═══════════════════════════════════════════════════════════════════════════
#  RUN ALL
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        test_01_push_single,
        test_02_push_multiple,
        test_03_pop_single,
        test_04_pop_all,
        test_05_push_after_pop,
        test_06_push_pop_push_cycle,
        test_07_fill_to_capacity,
        test_08_lifo_order,
        test_09_interleaved,
        test_10_duplicate_state,
        test_11_with_clones,
        test_12_drain_and_refill,
    ]

    os.makedirs(OUT_DIR, exist_ok=True)
    passed, failed = 0, 0

    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  ✗ FAILED: {e}")

    print(f"\n{'='*50}")
    print(f"  {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"  Images saved to: {OUT_DIR}/")
    print(f"{'='*50}")