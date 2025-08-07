class DLLNode:
    def __init__(self, data=None):
        self.data = data
        self.next = None
        self.prev = None


class DLList:
    def __init__(self):
        self.head = DLLNode()
        self.tail = DLLNode()
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def __len__(self):
        return self._size

    def _add_between(self, data, prevNode, nextNode):
        new_node = DLLNode(data)
        new_node.prev = prevNode
        new_node.next = nextNode
        prevNode.next = new_node
        nextNode.prev = new_node
        self._size += 1
        return new_node

    def _remove_node(self, node: DLLNode):
        if node == self.head or node == self.tail:
            raise ValueError("Cannot remove sentinel node")

        prevNode = node.prev
        nextNode = node.next
        prevNode.next = nextNode
        nextNode.prev = prevNode
        self._size -= 1
        data = node.data
        node.prev = node.next = node.data = None
        return data

    def add_first(self, data):
        return self._add_between(data, self.head, self.head.next)

    def add_last(self, data):
        return self._add_between(data, self.tail.prev, self.tail)

    def remove_first(self):
        if self._size == 0:
            raise IndexError("remove from empty list")
        return self._remove_node(self.head.next)

    def remove_last(self):
        if self._size == 0:
            raise IndexError("remove from empty list")
        return self._remove_node(self.tail.prev)

    def peek_first(self):
        if self._size == 0:
            raise IndexError("peek from empty list")
        return self.head.next.data

    def peek_last(self):
        if self._size == 0:
            raise IndexError("peek from empty list")
        return self.tail.prev.data

    def is_empty(self):
        return self._size == 0

    def __iter__(self):
        current = self.head.next
        while current != self.tail:
            yield current.data
            current = current.next

    def __repr__(self):
        return f"DLList([{', '.join(repr(item) for item in self)}])"


