from core_datastructures.linked_list import DLList

class Deque:
    """Double-ended queue implementation using doubly linked list."""
    
    def __init__(self):
        self._dll = DLList()
    
    def push_left(self, item):
        """Add item to the left (front) of the deque."""
        return self._dll.add_first(item)
    
    def push_right(self, item):
        """Add item to the right (back) of the deque."""
        return self._dll.add_last(item)
    
    def pop_left(self):
        """Remove and return item from the left (front) of the deque."""
        if self._dll.is_empty():
            raise IndexError("pop from empty deque")
        return self._dll.remove_first()
    
    def pop_right(self):
        """Remove and return item from the right (back) of the deque."""
        if self._dll.is_empty():
            raise IndexError("pop from empty deque")
        return self._dll.remove_last()
    
    def peek_left(self):
        """Return item from the left (front) without removing it."""
        return self._dll.peek_first()
    
    def peek_right(self):
        """Return item from the right (back) without removing it."""
        return self._dll.peek_last()
    
    def __len__(self):
        return len(self._dll)
    
    def is_empty(self):
        return self._dll.is_empty()
    
    def __iter__(self):
        return iter(self._dll)
    
    def append_left(self, item):
        """Add item to the left (front) of the deque. Alias for push_left."""
        return self.push_left(item)
    
    def append_right(self, item):
        """Add item to the right (back) of the deque. Alias for push_right.""" 
        return self.push_right(item)
    
    def get_range(self, start, end):
        """Get a range of items from the deque."""
        from core_datastructures.dynamic_array import DArray
        result = DArray()
        
        length = len(self)
        if length == 0:
            return result
        
        # Handle negative indices
        if start < 0:
            start = length + start
        if end < 0:
            end = length + end
            
        # Bounds checking
        start = max(0, min(start, length - 1))
        end = max(0, min(end, length - 1))
        
        if start > end:
            return result
        
        # Convert deque to list for easier indexing
        items = list(self)
        for i in range(start, end + 1):
            if i < len(items):
                result.append(items[i])
        
        return result
    
    def to_list(self, start=0, stop=-1):
        """Convert deque to list with optional range."""
        return self.get_range(start, stop)
    
    def __repr__(self):
        return f"Deque([{', '.join(repr(item) for item in self)}])"