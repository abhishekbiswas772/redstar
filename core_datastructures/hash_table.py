from core_datastructures.dynamic_array import DArray


class HashTable:
    class _Entry:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.deleted = False
    
    def __init__(self, initial_capacity=8):
        self.capacity = initial_capacity
        self.size = 0
        self.deleted_count = 0
        self._buckets = [None] * self.capacity
        self._load_factor_threshold = 0.75
    
    def _hash(self, key):
        if isinstance(key, str):
            h = 0
            for char in key:
                h = (h * 31 + ord(char)) % self.capacity
            return h
        elif isinstance(key, int):
            return key % self.capacity
        else:
            return hash(key) % self.capacity
    
    def _find_slot(self, key):
        index = self._hash(key)
        original_index = index
        first_deleted_index = None

        while True:
            entry = self._buckets[index]
            if entry is None:
                return (first_deleted_index if first_deleted_index is not None else index), None

            if entry.deleted:
                if first_deleted_index is None:
                    first_deleted_index = index
            elif entry.key == key:
                return index, entry

            index = (index + 1) % self.capacity
            if index == original_index:
                return -1, None
        
    def _resize(self):
        old_buckets = self._buckets
        old_capacity = self.capacity
        
        self.capacity *= 2
        self.size = 0
        self.deleted_count = 0
        self._buckets = [None] * self.capacity
        
        for entry in old_buckets:
            if entry is not None and not entry.deleted:
                self._put_entry(entry.key, entry.value)
    
    def _put_entry(self, key, value):
        index, existing_entry = self._find_slot(key)
        
        if index == -1:
            self._resize()
            return self._put_entry(key, value)
        
        if existing_entry is None:
            self._buckets[index] = self._Entry(key, value)
            self.size += 1
        else:
            existing_entry.value = value
        
        load_factor = (self.size + self.deleted_count) / self.capacity
        if load_factor > self._load_factor_threshold:
            self._resize()
    
    def put(self, key, value):
        self._put_entry(key, value)
    
    def get(self, key):
        index, entry = self._find_slot(key)
        if entry is None:
            raise KeyError(key)
        return entry.value
    
    def get_or_default(self, key, default=None):
        try:
            return self.get(key)
        except KeyError:
            return default
    
    def remove(self, key):
        index, entry = self._find_slot(key)
        if entry is None:
            raise KeyError(key)
        
        entry.deleted = True
        self.size -= 1
        self.deleted_count += 1
        return entry.value
    
    def contains(self, key):
        _, entry = self._find_slot(key)
        return entry is not None
    
    def keys(self):
        result = DArray()
        for entry in self._buckets:
            if entry is not None and not entry.deleted:
                result.append(entry.key)
        return result
    
    def values(self):
        result = DArray()
        for entry in self._buckets:
            if entry is not None and not entry.deleted:
                result.append(entry.value)
        return result
    
    def items(self):
        result = DArray()
        for entry in self._buckets:
            if entry is not None and not entry.deleted:
                result.append((entry.key, entry.value))
        return result
    
    def __len__(self):
        return self.size
    
    def __getitem__(self, key):
        return self.get(key)
    
    def __setitem__(self, key, value):
        self.put(key, value)
    
    def __delitem__(self, key):
        self.remove(key)
    
    def __contains__(self, key):
        return self.contains(key)
    
    def __iter__(self):
        for entry in self._buckets:
            if entry is not None and not entry.deleted:
                yield entry.key
    
    def __repr__(self):
        items = []
        for entry in self._buckets:
            if entry is not None and not entry.deleted:
                items.append(f"{repr(entry.key)}: {repr(entry.value)}")
        return f"HashTable({{{', '.join(items)}}})"
    


