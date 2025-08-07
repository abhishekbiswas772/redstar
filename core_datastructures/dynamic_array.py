


class DArray:
    def __init__(self, init_size = 4):
        self.capacity = init_size
        self.size = 0
        self._data = [None] * self.capacity


    def __len__(self):
        return self.size
    
    def __getitem__(self, index):
        if index < 0:
            index += self.size
        if not (0 <= index < self.size):
            raise IndexError("Array index is out of range")

        return self._data[index]
    

    def __setitem__(self, index, value):
        if index < 0:
            index += self.size
        if not (0 <= index < self.size):
            raise IndexError("Array index is out of range")
        self._data[index] = value


    def _resize(self, new_capacity):
        old_data = self._data
        self._data = [None] * new_capacity
        for i in range(self.size):
            self._data[i] = old_data[i]
        self.capacity = new_capacity

    def append(self, value):
        if self.size >= self.capacity:
            self._resize(self.capacity * 2)
        self._data[self.size] = value
        self.size += 1

    def pop(self, index = -1):
        if self.size == 0:
            raise IndexError("pop from empty array")
        
        if index < 0:
            index += self.size
        if not (0 <= index < self.size):
            raise IndexError("pop index out of range")
        value = self._data[index]

        for i in range(index, self.size - 1):
            self._data[i] = self._data[i + 1]

        self.size -= 1
        if self.size <= self.capacity // 4 and self.capacity > 4:
            self._resize(self.capacity // 2)
        return value
    

    def insert(self, index, value):
        if index < 0:
            index += self.size
        if index < 0:
            index = 0
        if index > self.size:
            index = self.size

        if self.size >= self.capacity:
            self._resize(self.capacity * 2)

        for i in range(self.size, index, -1):
            self._data[i] = self._data[i - 1]

        self._data[index] = value
        self.size += 1


    def __iter__(self):
        for i in range(self.size):
            yield self._data[i]

    def __repr__(self) -> str:
        return f"DArray([{', '.join(repr(item) for item in self)}])"
        

