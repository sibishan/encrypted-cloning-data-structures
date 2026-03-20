from protocol import Protocol

A = 1
S = 3

protocol = Protocol(A, S)
qc = protocol.build_circuit()
qc.draw('mpl', filename='misc/circuit.png')
print(qc.draw(fold=-1))
print("\n\n")

