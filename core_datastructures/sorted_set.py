from core_datastructures.dynamic_array import DArray
import bisect


class SortedSetNode:
    """Node for skip list implementation"""
    def __init__(self, member, score, level):
        self.member = member
        self.score = score
        self.forward = [None] * (level + 1)


class SortedSet:
    """
    Redis-compatible sorted set implementation using skip list
    Maintains elements sorted by score with O(log n) operations
    """
    
    def __init__(self, max_level=16):
        self.max_level = max_level
        self.level = 0
        # Header node with minimum possible score
        self.header = SortedSetNode(None, float('-inf'), max_level)
        self.length = 0
        # Member to node mapping for O(1) member lookups
        self.members = {}
    
    def _random_level(self):
        """Generate random level for skip list"""
        level = 0
        while level < self.max_level and hash(level) % 4 == 0:
            level += 1
        return level
    
    def add(self, member, score):
        """
        Add member with score to sorted set
        Returns True if new element, False if score was updated
        """
        # Check if member already exists
        if member in self.members:
            old_node = self.members[member]
            if old_node.score == score:
                return False  # No change needed
            
            # Remove old node and add new one
            self.remove(member)
        
        # Create new node
        level = self._random_level()
        new_node = SortedSetNode(member, score, level)
        
        # Find insertion point
        update = [None] * (self.max_level + 1)
        current = self.header
        
        # Search from top level down
        for i in range(self.level, -1, -1):
            while (current.forward[i] and 
                   (current.forward[i].score < score or 
                    (current.forward[i].score == score and current.forward[i].member < member))):
                current = current.forward[i]
            update[i] = current
        
        # Insert new node
        for i in range(level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node
        
        # Update skip list level if necessary
        if level > self.level:
            for i in range(self.level + 1, level + 1):
                update[i] = self.header
            self.level = level
        
        # Add to members mapping
        self.members[member] = new_node
        self.length += 1
        return True
    
    def remove(self, member):
        """Remove member from sorted set"""
        if member not in self.members:
            return False
        
        node_to_remove = self.members[member]
        
        # Find the node and update pointers
        update = [None] * (self.max_level + 1)
        current = self.header
        
        for i in range(self.level, -1, -1):
            while (current.forward[i] and 
                   (current.forward[i].score < node_to_remove.score or
                    (current.forward[i].score == node_to_remove.score and 
                     current.forward[i].member < member))):
                current = current.forward[i]
            update[i] = current
        
        current = current.forward[0]
        if current and current.member == member:
            # Remove node from all levels
            for i in range(self.level + 1):
                if update[i].forward[i] != current:
                    break
                update[i].forward[i] = current.forward[i]
            
            # Update level if necessary
            while self.level > 0 and self.header.forward[self.level] is None:
                self.level -= 1
            
            # Remove from members mapping
            del self.members[member]
            self.length -= 1
            return True
        
        return False
    
    def get_score(self, member):
        """Get score of member"""
        if member in self.members:
            return self.members[member].score
        return None
    
    def get_rank(self, member):
        """Get 0-based rank of member (0 = highest score)"""
        if member not in self.members:
            return None
        
        target_node = self.members[member]
        rank = 0
        current = self.header
        
        for i in range(self.level, -1, -1):
            while current.forward[i]:
                if (current.forward[i].score < target_node.score or
                    (current.forward[i].score == target_node.score and 
                     current.forward[i].member < member)):
                    # Count nodes traversed at this level
                    current = current.forward[i]
                    rank += 1
                else:
                    break
        
        return rank
    
    def get_range(self, start, stop, reverse=False):
        """
        Get members in rank range [start, stop]
        If reverse=True, return in descending score order
        """
        if self.length == 0:
            return DArray()
        
        # Normalize negative indices
        if start < 0:
            start = max(0, self.length + start)
        if stop < 0:
            stop = max(-1, self.length + stop)
        
        if start > stop or start >= self.length:
            return DArray()
        
        stop = min(stop, self.length - 1)
        
        result = DArray()
        current = self.header.forward[0]  # Start from first real node
        
        # Skip to start position
        for _ in range(start):
            if current:
                current = current.forward[0]
        
        # Collect elements in range
        count = stop - start + 1
        nodes = []
        for _ in range(count):
            if current:
                nodes.append((current.member, current.score))
                current = current.forward[0]
        
        if reverse:
            nodes.reverse()
        
        for member, score in nodes:
            result.append(member)
        
        return result
    
    def get_range_with_scores(self, start, stop, reverse=False):
        """Get members and scores in rank range"""
        if self.length == 0:
            return DArray()
        
        # Normalize negative indices
        if start < 0:
            start = max(0, self.length + start)
        if stop < 0:
            stop = max(-1, self.length + stop)
        
        if start > stop or start >= self.length:
            return DArray()
        
        stop = min(stop, self.length - 1)
        
        result = DArray()
        current = self.header.forward[0]
        
        # Skip to start position
        for _ in range(start):
            if current:
                current = current.forward[0]
        
        # Collect elements in range
        count = stop - start + 1
        nodes = []
        for _ in range(count):
            if current:
                nodes.append((current.member, current.score))
                current = current.forward[0]
        
        if reverse:
            nodes.reverse()
        
        for member, score in nodes:
            result.append(member)
            result.append(str(score))
        
        return result
    
    def get_range_by_score(self, min_score, max_score, offset=0, count=None, reverse=False):
        """Get members with scores in range [min_score, max_score]"""
        result = DArray()
        current = self.header.forward[0]
        
        # Skip to first node with score >= min_score
        while current and current.score < min_score:
            current = current.forward[0]
        
        # Skip offset nodes
        for _ in range(offset):
            if current and current.score <= max_score:
                current = current.forward[0]
        
        # Collect nodes in score range
        collected = 0
        nodes = []
        while current and current.score <= max_score:
            if count is not None and collected >= count:
                break
            nodes.append((current.member, current.score))
            current = current.forward[0]
            collected += 1
        
        if reverse:
            nodes.reverse()
        
        for member, score in nodes:
            result.append(member)
        
        return result
    
    def count_by_score(self, min_score, max_score):
        """Count members with scores in range"""
        count = 0
        current = self.header.forward[0]
        
        while current:
            if min_score <= current.score <= max_score:
                count += 1
            elif current.score > max_score:
                break
            current = current.forward[0]
        
        return count
    
    def remove_range_by_rank(self, start, stop):
        """Remove members in rank range"""
        if self.length == 0:
            return 0
        
        # Normalize indices
        if start < 0:
            start = max(0, self.length + start)
        if stop < 0:
            stop = max(-1, self.length + stop)
        
        if start > stop or start >= self.length:
            return 0
        
        stop = min(stop, self.length - 1)
        
        # Collect members to remove
        members_to_remove = DArray()
        current = self.header.forward[0]
        
        for i in range(self.length):
            if current:
                if start <= i <= stop:
                    members_to_remove.append(current.member)
                current = current.forward[0]
        
        # Remove collected members
        removed_count = 0
        for i in range(len(members_to_remove)):
            if self.remove(members_to_remove[i]):
                removed_count += 1
        
        return removed_count
    
    def remove_range_by_score(self, min_score, max_score):
        """Remove members with scores in range"""
        members_to_remove = DArray()
        current = self.header.forward[0]
        
        while current:
            if min_score <= current.score <= max_score:
                members_to_remove.append(current.member)
            current = current.forward[0]
        
        removed_count = 0
        for i in range(len(members_to_remove)):
            if self.remove(members_to_remove[i]):
                removed_count += 1
        
        return removed_count
    
    def __len__(self):
        return self.length
    
    def __contains__(self, member):
        return member in self.members
    
    def size(self):
        return self.length
    
    def is_empty(self):
        return self.length == 0