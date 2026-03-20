# callum will work on this array data structure class
class Array:
    def __init__(self, elements, size, capacity, dtype, address, dimensions, stride):
        self.elements = elements        # The actual stored values
        self.size = size                # Num of elements in the array
        self.capacity = capacity        # Total allocated space
        self.dtype = dtype              # Element data type
        self.address = address          # Memory address for first element
        self.dimensions = dimensions    # If multidimensional, axis size
        self.stride = stride            # Byte offset between elements in each dimension

    def get(self, index):
        return self.elements[index]

    def set(self, index, value):
        self.elements[index] = value

    def insert(self, index, value):
        self.elements.insert(index, value)

    def append(self, value):
        self.elements.append(value)

    def remove(self, value):
        self.elements.remove(value)

    def search(self, value):
        return self.elements.index(value)

    def sort(self):
        self.elements.sort()

    def reverse(self):
        self.elements.reverse()

    def slice(self, start, end):
        return self.elements.slice(start, end)

    def merge(self, other):
        return self.elements.merge(other)

    def traverse(self, value):
        self.elements.traverse(value)

    def resize(self, new_size):
        self.elements.resize(new_size)

    def clear(self):
        self.elements.clear()

    def isEmpty(self):
        return self.elements.isEmpty()

    def contains(self, value):
        return self.elements.contains(value)

my_array = Array([1, 2, 3, 4], 4, 5, 6, 7)
my_array.access()