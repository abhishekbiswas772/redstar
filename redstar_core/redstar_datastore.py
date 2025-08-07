from core_datastructures.deque import Deque
from core_datastructures.hash_table import HashTable
from core_datastructures.hashset import HashSet
from redstar_core.redstar_value import RedStarValue
from core_datastructures.dynamic_array import DArray
import threading
import time

class RedStarDataSource:
    def __init__(self):
        self.data = HashTable()
        self.lock = threading.RLock()

    def _clean_expired(self, key):
        with self.lock:
            if key in self.data:
                redstar_value = self.data[key]
                if redstar_value.is_expired():
                    del self.data[key]
                    return True
                
        return False
    

    def set_string(self, key, value, expire_seconds = None):
        expiry_time = None
        if expire_seconds:
            expiry_time = time.time() + expire_seconds
        
        with self.lock:
            redstar_value = RedStarValue(value, "string", expiry_time)
            self.data[key] = redstar_value
    
    def get_string(self, key):
        if self._clean_expired(key):
            return None
        
        if key not in self.data:
            return None 
        
        redstar_value = self.data[key]
        if redstar_value.type != 'string':
            raise TypeError(f"WRONGTYPE: key {key} is not a string")
        
        return redstar_value.value
    

    def delete_key(self, key):
        if self._clean_expired(key):
            return None
        
        if key not in self.data:
            return None 
        
        redstar_value = self.data[key]
        if redstar_value.type != 'string':
            raise TypeError(f"Wrong Type: key {key} is not a string")
        return redstar_value.value
    

    def delete_key(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                return True 
        return False
    
    def exists_key(self, key):
        if self._clean_expired(key):
            return False
        return key in self.data
    
    def set_expiry(self, key, second):
        if self._clean_expired(key) or key not in self.data:
            return False
        
        with self.lock:
            redstar_value = self.data[key]
            redstar_value.expiry_time = time.time() + second
        return True
    


    def get_ttl(self, key):
        if self._clean_expired(key):
            return -2  
        
        if key not in self.data:
            return -2
        
        redstar_value = self.data[key]
        if redstar_value.expiry_time is None:
            return -1  # No expiry
        
        ttl = int(redstar_value.expiry_time - time.time())
        return max(0, ttl)
    
    def get_all_keys(self, pattern="*"):
        expired_keys = DArray()
        for key in self.data:
            if self._clean_expired(key):
                expired_keys.append(key)
        
        result = DArray()
        for key in self.data:
            if pattern == "*" or self._match_pattern(key, pattern):
                result.append(key)
        
        return result
    
    def _match_pattern(self, key, pattern):
        if pattern == "*":
            return True
        return key.startswith(pattern.replace("*", ""))
    
    def get_list(self, key, create_if_not_exists=False):
        if self._clean_expired(key):
            if not create_if_not_exists:
                return None
        
        if key not in self.data:
            if create_if_not_exists:
                with self.lock:
                    redstar_value = RedStarValue(Deque(), 'list')
                    self.data[key] = redstar_value
                    return redstar_value.value
            return None
        
        redstar_value = self.data[key]
        if redstar_value.type != 'list':
            raise TypeError(f"WRONGTYPE: key {key} is not a list")
        
        return redstar_value.value
    
    def get_set(self, key, create_if_not_exists=False):
        if self._clean_expired(key):
            if not create_if_not_exists:
                return None
        
        if key not in self.data:
            if create_if_not_exists:
                with self.lock:
                    redstar_value = RedStarValue(HashSet(), 'set')
                    self.data[key] = redstar_value
                    return redstar_value.value
            return None
        
        redstar_value = self.data[key]
        if redstar_value.type != 'set':
            raise TypeError(f"WRONGTYPE: key {key} is not a set")
        
        return redstar_value.value
    
    def get_hash(self, key, create_if_not_exists=False):
        if self._clean_expired(key):
            if not create_if_not_exists:
                return None
        
        if key not in self.data:
            if create_if_not_exists:
                with self.lock:
                    redstar_value = RedStarValue(HashTable(), 'hash')
                    self.data[key] = redstar_value
                    return redstar_value.value
            return None
        
        redstar_value = self.data[key]
        if redstar_value.type != 'hash':
            raise TypeError(f"WRONGTYPE: key {key} is not a hash")
        
        return redstar_value.value
    
    def clear_all(self):
        with self.lock:
            self.data.clear()