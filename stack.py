from protocol import Protocol

class QStack:
    def __init__(self, num_qubits=0, num_clones=0):
        self.num_qubits = num_qubits
        self.num_clones = num_clones
        self.capacity = 0
        self.protocol = Protocol(self.num_qubits, self.num_clones)
    
    def draw(self):
        return self.protocol.qc.draw(fold=-1)

    def push(self, qc=None):
        if qc is None:
            raise ValueError("Input circuit cannot be None")
        if qc.num_qubits != 1:
            raise ValueError("Input must be a single-qubit circuit")
        if self.capacity >= (self.num_qubits):
            raise OverflowError("QStack Overflow")
        
        self.protocol.store_qubit(qc, self.capacity)
        self.capacity += 1

    def pop(self, index=0):
        if self.isEmpty():
            raise IndexError("QStack is empty")
        if index >= self.num_clones:
            raise ValueError("Invalid clone index")
        self.protocol.decrypt_clone(self.capacity)
        self.capacity -= 1
        return self.items.pop()

    # def isEmpty(self):
    #     return len(self.items) == 0

    # def size(self):
    #     return len(self.items)
