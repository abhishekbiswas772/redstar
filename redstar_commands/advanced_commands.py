from core_datastructures.dynamic_array import DArray
from core_datastructures.hash_table import HashTable
from core_datastructures.bitmap import Bitmap
import random


class RedstarAdvancedCommands:
    """
    Advanced Redis commands for all data types
    Includes extended operations for strings, lists, sets, hashes, and new data types
    """
    
    def __init__(self, data_store):
        self.store = data_store
    
    # =============================================================================
    # ADVANCED STRING OPERATIONS
    # =============================================================================
    
    def cmd_append(self, args):
        """APPEND key value"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'append' command")
        
        key, value = args[0], args[1]
        current = self.store.get_string(key)
        
        if current is None:
            self.store.set_string(key, value)
            return len(value)
        else:
            new_value = current + value
            self.store.set_string(key, new_value)
            return len(new_value)
    
    def cmd_strlen(self, args):
        """STRLEN key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'strlen' command")
        
        value = self.store.get_string(args[0])
        return len(value) if value is not None else 0
    
    def cmd_getrange(self, args):
        """GETRANGE key start end"""
        if len(args) != 3:
            return Exception("ERR wrong number of arguments for 'getrange' command")
        
        key = args[0]
        try:
            start = int(args[1])
            end = int(args[2])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        value = self.store.get_string(key)
        if value is None:
            return ""
        
        # Handle negative indices
        if start < 0:
            start = max(0, len(value) + start)
        if end < 0:
            end = max(-1, len(value) + end)
        
        if start > end or start >= len(value):
            return ""
        
        end = min(end, len(value) - 1)
        return value[start:end + 1]
    
    def cmd_setrange(self, args):
        """SETRANGE key offset value"""
        if len(args) != 3:
            return Exception("ERR wrong number of arguments for 'setrange' command")
        
        key = args[0]
        try:
            offset = int(args[1])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        if offset < 0:
            return Exception("ERR offset is out of range")
        
        new_part = args[2]
        current = self.store.get_string(key) or ""
        
        # Extend string with nulls if needed
        if offset > len(current):
            current += '\x00' * (offset - len(current))
        
        # Replace part of string
        if offset + len(new_part) > len(current):
            result = current[:offset] + new_part
        else:
            result = current[:offset] + new_part + current[offset + len(new_part):]
        
        self.store.set_string(key, result)
        return len(result)
    
    def cmd_mget(self, args):
        """MGET key [key ...]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'mget' command")
        
        result = DArray()
        for i in range(len(args)):
            value = self.store.get_string(args[i])
            result.append(value)
        
        return result
    
    def cmd_mset(self, args):
        """MSET key value [key value ...]"""
        if len(args) == 0 or len(args) % 2 != 0:
            return Exception("ERR wrong number of arguments for 'mset' command")
        
        for i in range(0, len(args), 2):
            key = args[i]
            value = args[i + 1]
            self.store.set_string(key, value)
        
        return "OK"
    
    def cmd_getset(self, args):
        """GETSET key value"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'getset' command")
        
        key, value = args[0], args[1]
        old_value = self.store.get_string(key)
        self.store.set_string(key, value)
        
        return old_value
    
    # =============================================================================
    # ADVANCED LIST OPERATIONS
    # =============================================================================
    
    def cmd_lindex(self, args):
        """LINDEX key index"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'lindex' command")
        
        key = args[0]
        try:
            index = int(args[1])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        deque = self.store.get_list(key)
        if deque is None or deque.is_empty():
            return None
        
        # Handle negative indices
        if index < 0:
            index = len(deque) + index
        
        if 0 <= index < len(deque):
            # Convert to list to access by index
            items = deque.to_list(0, -1)
            return items[index]
        
        return None
    
    def cmd_lset(self, args):
        """LSET key index element"""
        if len(args) != 3:
            return Exception("ERR wrong number of arguments for 'lset' command")
        
        key = args[0]
        try:
            index = int(args[1])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        element = args[2]
        deque = self.store.get_list(key)
        
        if deque is None or deque.is_empty():
            return Exception("ERR no such key")
        
        # Handle negative indices
        if index < 0:
            index = len(deque) + index
        
        if not (0 <= index < len(deque)):
            return Exception("ERR index out of range")
        
        # For now, we'll rebuild the deque (not optimal but works)
        items = deque.to_list(0, -1)
        items[index] = element
        
        # Clear and rebuild deque
        while not deque.is_empty():
            deque.pop_left()
        
        for item in items:
            deque.append_right(item)
        
        return "OK"
    
    # =============================================================================
    # ADVANCED SET OPERATIONS
    # =============================================================================
    
    def cmd_spop(self, args):
        """SPOP key [count]"""
        if len(args) < 1 or len(args) > 2:
            return Exception("ERR wrong number of arguments for 'spop' command")
        
        key = args[0]
        count = 1
        
        if len(args) == 2:
            try:
                count = int(args[1])
            except ValueError:
                return Exception("ERR value is not an integer")
        
        hash_set = self.store.get_set(key)
        if hash_set is None or hash_set.size() == 0:
            return None if count == 1 else DArray()
        
        # Get all members and randomly select
        members = hash_set.to_list()
        result = DArray()
        
        actual_count = min(count, len(members))
        
        # Simple random selection (not cryptographically secure)
        selected_indices = set()
        while len(selected_indices) < actual_count:
            idx = hash(str(len(selected_indices))) % len(members)
            selected_indices.add(idx)
        
        for idx in selected_indices:
            member = members[idx]
            hash_set.remove(member)
            result.append(member)
        
        if count == 1:
            return result[0] if len(result) > 0 else None
        else:
            return result
    
    def cmd_srandmember(self, args):
        """SRANDMEMBER key [count]"""
        if len(args) < 1 or len(args) > 2:
            return Exception("ERR wrong number of arguments for 'srandmember' command")
        
        key = args[0]
        count = 1
        
        if len(args) == 2:
            try:
                count = int(args[1])
            except ValueError:
                return Exception("ERR value is not an integer")
        
        hash_set = self.store.get_set(key)
        if hash_set is None or hash_set.size() == 0:
            return None if count == 1 else DArray()
        
        members = hash_set.to_list()
        result = DArray()
        
        if count > 0:
            # Unique random members
            actual_count = min(count, len(members))
            selected_indices = set()
            
            while len(selected_indices) < actual_count:
                idx = hash(str(len(selected_indices))) % len(members)
                selected_indices.add(idx)
            
            for idx in selected_indices:
                result.append(members[idx])
        else:
            # Allow duplicates
            for i in range(abs(count)):
                idx = hash(str(i)) % len(members)
                result.append(members[idx])
        
        if len(args) == 1:
            return result[0] if len(result) > 0 else None
        else:
            return result
    
    def cmd_sunion(self, args):
        """SUNION key [key ...]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'sunion' command")
        
        from core_datastructures.hashset import HashSet
        result_set = HashSet()
        
        for i in range(len(args)):
            hash_set = self.store.get_set(args[i])
            if hash_set is not None:
                members = hash_set.to_list()
                for j in range(len(members)):
                    result_set.add(members[j])
        
        return result_set.to_list()
    
    def cmd_sinter(self, args):
        """SINTER key [key ...]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'sinter' command")
        
        # Start with first set
        first_set = self.store.get_set(args[0])
        if first_set is None:
            return DArray()
        
        result = DArray()
        first_members = first_set.to_list()
        
        for i in range(len(first_members)):
            member = first_members[i]
            in_all = True
            
            # Check if member exists in all other sets
            for j in range(1, len(args)):
                other_set = self.store.get_set(args[j])
                if other_set is None or not other_set.contains(member):
                    in_all = False
                    break
            
            if in_all:
                result.append(member)
        
        return result
    
    def cmd_sdiff(self, args):
        """SDIFF key [key ...]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'sdiff' command")
        
        # Start with first set
        first_set = self.store.get_set(args[0])
        if first_set is None:
            return DArray()
        
        result = DArray()
        first_members = first_set.to_list()
        
        for i in range(len(first_members)):
            member = first_members[i]
            in_other = False
            
            # Check if member exists in any other set
            for j in range(1, len(args)):
                other_set = self.store.get_set(args[j])
                if other_set is not None and other_set.contains(member):
                    in_other = True
                    break
            
            if not in_other:
                result.append(member)
        
        return result
    
    # =============================================================================
    # ADVANCED HASH OPERATIONS
    # =============================================================================
    
    def cmd_hmset(self, args):
        """HMSET key field value [field value ...]"""
        if len(args) < 3 or len(args) % 2 == 0:
            return Exception("ERR wrong number of arguments for 'hmset' command")
        
        key = args[0]
        hash_table = self.store.get_hash(key, create_if_not_exists=True)
        
        for i in range(1, len(args), 2):
            field = args[i]
            value = args[i + 1]
            hash_table.put(field, value)
        
        return "OK"
    
    def cmd_hmget(self, args):
        """HMGET key field [field ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'hmget' command")
        
        key = args[0]
        hash_table = self.store.get_hash(key)
        
        result = DArray()
        for i in range(1, len(args)):
            field = args[i]
            if hash_table is None:
                result.append(None)
            else:
                try:
                    value = hash_table.get(field)
                    result.append(value)
                except KeyError:
                    result.append(None)
        
        return result
    
    def cmd_hexists(self, args):
        """HEXISTS key field"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'hexists' command")
        
        key, field = args[0], args[1]
        hash_table = self.store.get_hash(key)
        
        if hash_table is None:
            return 0
        
        return 1 if hash_table.contains(field) else 0
    
    def cmd_hlen(self, args):
        """HLEN key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'hlen' command")
        
        hash_table = self.store.get_hash(args[0])
        return len(hash_table) if hash_table is not None else 0
    
    def cmd_hincrby(self, args):
        """HINCRBY key field increment"""
        if len(args) != 3:
            return Exception("ERR wrong number of arguments for 'hincrby' command")
        
        key, field = args[0], args[1]
        try:
            increment = int(args[2])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        hash_table = self.store.get_hash(key, create_if_not_exists=True)
        
        try:
            current_value = hash_table.get(field)
            current_int = int(current_value)
        except (KeyError, ValueError):
            current_int = 0
        
        new_value = current_int + increment
        hash_table.put(field, str(new_value))
        
        return new_value