import os
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import random_statevector

# ── Output directory ──
OUT_DIR = "presentation/out"
os.makedirs(OUT_DIR, exist_ok=True)


def make_state(label: str) -> QuantumCircuit:
    """Create a 1-qubit circuit initialised to a random state with a label."""
    qc = QuantumCircuit(1)
    psi = random_statevector(2)
    qc.initialize(psi, 0)
    qc.metadata = {"label": label}
    return qc


def save_fig(obj, filename: str, subfolder: str = ""):
    """Draw a circuit from a Protocol/QStack/QArray and save as PNG.
    
    Args:
        obj: Protocol, QStack, or QArray instance (must have .draw())
        filename: output filename without extension
        subfolder: optional subfolder inside OUT_DIR (e.g. 'protocol', 'qstack', 'qarray')
    """
    path = os.path.join(OUT_DIR, subfolder) if subfolder else OUT_DIR
    os.makedirs(path, exist_ok=True)
    fig = obj.draw()
    filepath = os.path.join(path, f"{filename}.png")
    fig.savefig(filepath, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  saved: {filepath}")


# ═══════════════════════════════════════════════════════════
# PROTOCOL FIGURES
# ═══════════════════════════════════════════════════════════
def gen_protocol_init():
    """Figure: Protocol after initialisation (Bell pairs only)."""
    from protocol import Protocol
    p = Protocol(1, 2)
    save_fig(p, "protocol_init", "protocol")


def gen_protocol_store():
    """Figure: Protocol after storing one quantum state."""
    from protocol import Protocol
    p = Protocol(1, 2)
    qc = make_state("psi")
    p.store_qubit(qc, 0)
    save_fig(p, "protocol_store", "protocol")


def gen_protocol_retrieve():
    """Figure: Protocol after storing then retrieving (clone 0)."""
    from protocol import Protocol
    p = Protocol(1, 2)
    qc = make_state("psi")
    p.store_qubit(qc, 0)
    p.retrieve_qubit(0, 0)
    save_fig(p, "protocol_retrieve", "protocol")


def gen_protocol_swap_a():
    """Figure: Protocol after swapping two A registers."""
    from protocol import Protocol
    p = Protocol(2, 2)
    p.swap_a(0, 1)
    save_fig(p, "protocol_swap_a", "protocol")


def gen_protocol_uncompute_a():
    """Figure: Protocol after uncomputing a slot."""
    from protocol import Protocol
    p = Protocol(2, 2)
    p.store_qubit(make_state("psi0"), 0)
    p.store_qubit(make_state("psi1"), 1)
    p.uncompute_a(0)
    save_fig(p, "protocol_uncompute_a", "protocol")


# ═══════════════════════════════════════════════════════════
# QSTACK FIGURES
# ═══════════════════════════════════════════════════════════
def gen_qstack_init():
    """Figure: QStack after initialisation."""
    from qstack import QStack
    qs = QStack(2, 2)
    save_fig(qs, "qstack_init", "qstack")


def gen_qstack_push():
    """Figure: QStack after two pushes."""
    from qstack import QStack
    qs = QStack(2, 2)
    qs.push(make_state("psi0"))
    qs.push(make_state("psi1"))
    save_fig(qs, "qstack_push_x2", "qstack")


def gen_qstack_pop():
    """Figure: QStack after two pushes then one pop."""
    from qstack import QStack
    qs = QStack(2, 2)
    qs.push(make_state("psi0"))
    qs.push(make_state("psi1"))
    qs.pop(0)
    save_fig(qs, "qstack_push_x2_pop", "qstack")


# ═══════════════════════════════════════════════════════════
# QARRAY FIGURES
# ═══════════════════════════════════════════════════════════
def gen_qarray_init():
    """Figure: QArray after initialisation."""
    from qarray import QArray
    qa = QArray(3, 2)
    save_fig(qa, "qarray_init", "qarray")


def gen_qarray_set():
    """Figure: QArray after setting two elements."""
    from qarray import QArray
    qa = QArray(3, 2)
    qa.set(0, make_state("psi0"))
    qa.set(1, make_state("psi1"))
    save_fig(qa, "qarray_set_x2", "qarray")


def gen_qarray_get():
    """Figure: QArray after set then get."""
    from qarray import QArray
    qa = QArray(3, 2)
    qa.set(0, make_state("psi0"))
    qa.set(1, make_state("psi1"))
    qa.get(0, 0)
    save_fig(qa, "qarray_set_x2_get", "qarray")


def gen_qarray_insert():
    """Figure: QArray after two sets then insert at index 0."""
    from qarray import QArray
    qa = QArray(4, 2)
    qa.set(0, make_state("psi0"))
    qa.set(1, make_state("psi1"))
    qa.insert(0, make_state("psi_new"))
    save_fig(qa, "qarray_insert", "qarray")


def gen_qarray_append():
    """Figure: QArray after two sets then append."""
    from qarray import QArray
    qa = QArray(4, 2)
    qa.set(0, make_state("psi0"))
    qa.set(1, make_state("psi1"))
    qa.append(make_state("psi2"))
    save_fig(qa, "qarray_append", "qarray")


def gen_qarray_remove():
    """Figure: QArray after three sets then remove index 0."""
    from qarray import QArray
    qa = QArray(4, 2)
    qa.set(0, make_state("psi0"))
    qa.set(1, make_state("psi1"))
    qa.set(2, make_state("psi2"))
    qa.remove(0)
    save_fig(qa, "qarray_remove", "qarray")


def gen_qarray_reverse():
    """Figure: QArray after three sets then reverse."""
    from qarray import QArray
    qa = QArray(3, 2)
    qa.set(0, make_state("psi0"))
    qa.set(1, make_state("psi1"))
    qa.set(2, make_state("psi2"))
    qa.reverse()
    save_fig(qa, "qarray_reverse", "qarray")


# ═══════════════════════════════════════════════════════════
# GENERATE ALL
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    generators = [
        # Protocol
        ("Protocol Init",         gen_protocol_init),
        ("Protocol Store",        gen_protocol_store),
        ("Protocol Retrieve",     gen_protocol_retrieve),
        ("Protocol Swap A",       gen_protocol_swap_a),
        ("Protocol Uncompute A",  gen_protocol_uncompute_a),
        # QStack
        ("QStack Init",           gen_qstack_init),
        ("QStack Push x2",        gen_qstack_push),
        ("QStack Push x2 + Pop",  gen_qstack_pop),
        # QArray
        ("QArray Init",           gen_qarray_init),
        ("QArray Set x2",         gen_qarray_set),
        ("QArray Set x2 + Get",   gen_qarray_get),
        ("QArray Insert",         gen_qarray_insert),
        ("QArray Append",         gen_qarray_append),
        ("QArray Remove",         gen_qarray_remove),
        ("QArray Reverse",        gen_qarray_reverse),
    ]

    for name, fn in generators:
        print(f"\n[{name}]")
        try:
            fn()
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nAll figures saved to ./{OUT_DIR}/")