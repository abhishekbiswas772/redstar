from core_datastructures.hash_table import HashTable


class HashSet:
    def __init__(self):
        self._table = HashTable()

    def add(self, item):
        was_present = self._table.contains(item)
        self._table.put(item, True)
        return not was_present
    

    def contains(self, item):
        return self._table.contains(item)
    
    def size(self):
        return len(self._table)
    
    def clear(self):
        self._table = HashTable()

    def to_list(self):
        return self._table.keys()
    
    def __len__(self):
        return len(self._table)
    
    def __contains__(self, item):
        return self.contains(item)
    
    def __iter__(self):
        return iter(self._table)
    
    def __repr__(self):
        return f"HashSet({{{', '.join(repr(item) for item in self)}}})" 
    
