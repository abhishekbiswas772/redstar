from linked_list import DLList
from dynamic_array import DArray

class Deque:
    def __init__(self):
        self._list : DLList = DLList()

    def append_left(self, item):
        self._list.add_first(item)

    def append_right(self, item):
        self._list.add_last(item)

    def pop_left(self):
        return self._list.remove_first()
    
    def pop_right(self):
        return self._list.remove_last()
    
    def peek_left(self):
        return self._list.peek_first()
    
    def peek_right(self):
        return self._list.peek_last()
    
    def is_empty(self):
        return self._list.is_empty()
    
    def __len__(self):
        return len(self._list)
    
    def __iter__(self):
        return iter(self._list)
    
    def to_list(self, start = 0, end = None):
        result = DArray()
        items = list(self._list)
        if end is None or end >= len(items):
            end = len(items) - 1

        if start < 0:
            start += len(items)
        if end < 0:
            end += len(items)

        for i in range(max(0, start), min(len(items), end + 1)):
            result.append(items[i])
        return result
    

    def __repr__(self):
        return f"Deque([{', '.join(repr(item) for item in self)}])"


