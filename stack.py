from protocol import Protocol

class QStack:
    def __init__(self, num_qubits=0, num_clones=0):
        self.num_qubits = num_qubits
        self.num_clones = num_clones
        self.capacity = 0

        self.protocol = Protocol(self.num_qubits, self.num_clones)
    
    def draw(self):
        return self.protocol.qc.draw(fold=-1)

    def push(self, qc):
        if self.capacity >= (self.num_qubits - 1):
            raise OverflowError("Stack Overflow")
        self.protocol.store_qubit(qc)
        self.capacity += 1

    # def pop(self):
    #     if self.isEmpty():
    #         raise IndexError("Stack Underflow")
    #     self.top -= 1
    #     return self.items.pop()

    # def isEmpty(self):
    #     return len(self.items) == 0

    # def size(self):
    #     return len(self.items)
