from core_datastructures.hash_table import HashTable
from core_datastructures.dynamic_array import DArray


class RedstarCommandProcessor:
    def __init__(self, data_store):
        self.store = data_store
        
        # Command registry - maps command names to methods
        self.commands = HashTable()
        self._register_commands()
    
    def _register_commands(self):
        """Register all available commands"""
        # String commands
        self.commands['GET'] = self.cmd_get
        self.commands['SET'] = self.cmd_set
        self.commands['DEL'] = self.cmd_del
        self.commands['EXISTS'] = self.cmd_exists
        self.commands['EXPIRE'] = self.cmd_expire
        self.commands['TTL'] = self.cmd_ttl
        self.commands['KEYS'] = self.cmd_keys
        self.commands['INCR'] = self.cmd_incr
        self.commands['DECR'] = self.cmd_decr
        
        # List commands
        self.commands['LPUSH'] = self.cmd_lpush
        self.commands['RPUSH'] = self.cmd_rpush
        self.commands['LPOP'] = self.cmd_lpop
        self.commands['RPOP'] = self.cmd_rpop
        self.commands['LLEN'] = self.cmd_llen
        self.commands['LRANGE'] = self.cmd_lrange
        
        # Set commands
        self.commands['SADD'] = self.cmd_sadd
        self.commands['SREM'] = self.cmd_srem
        self.commands['SMEMBERS'] = self.cmd_smembers
        self.commands['SCARD'] = self.cmd_scard
        self.commands['SISMEMBER'] = self.cmd_sismember
        
        # Hash commands
        self.commands['HSET'] = self.cmd_hset
        self.commands['HGET'] = self.cmd_hget
        self.commands['HDEL'] = self.cmd_hdel
        self.commands['HGETALL'] = self.cmd_hgetall
        self.commands['HKEYS'] = self.cmd_hkeys
        self.commands['HVALS'] = self.cmd_hvals
        
        # Server commands
        self.commands['PING'] = self.cmd_ping
        self.commands['INFO'] = self.cmd_info
        self.commands['FLUSHALL'] = self.cmd_flushall
    
    def execute_command(self, command_array):
        """Execute a Redstar command"""
        if not command_array or len(command_array) == 0:
            return Exception("ERR empty command")
        
        cmd_name = command_array[0].upper()
        
        if not self.commands.contains(cmd_name):
            return Exception(f"ERR unknown command '{cmd_name}'")
        
        try:
            command_func = self.commands[cmd_name]
            args = DArray()
            for i in range(1, len(command_array)):
                args.append(command_array[i])
            
            return command_func(args)
        except Exception as e:
            return Exception(f"ERR {str(e)}")
    
    # =============================================================================
    # STRING COMMANDS
    # =============================================================================
    
    def cmd_get(self, args):
        """GET key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'get' command")
        
        value = self.store.get_string(args[0])
        return value
    
    def cmd_set(self, args):
        """SET key value [EX seconds]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'set' command")
        
        key, value = args[0], args[1]
        expiry_seconds = None
        
        # Parse optional EX parameter
        i = 2
        while i < len(args):
            if args[i].upper() == 'EX':
                if i + 1 >= len(args):
                    return Exception("ERR syntax error")
                try:
                    expiry_seconds = int(args[i + 1])
                except ValueError:
                    return Exception("ERR value is not an integer")
                i += 2
            else:
                i += 1
        
        self.store.set_string(key, value, expiry_seconds)
        return "OK"
    
    def cmd_del(self, args):
        """DEL key [key ...]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'del' command")
        
        deleted_count = 0
        for i in range(len(args)):
            if self.store.delete_key(args[i]):
                deleted_count += 1
        
        return deleted_count
    
    def cmd_exists(self, args):
        """EXISTS key [key ...]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'exists' command")
        
        exists_count = 0
        for i in range(len(args)):
            if self.store.exists_key(args[i]):
                exists_count += 1
        
        return exists_count
    
    def cmd_expire(self, args):
        """EXPIRE key seconds"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'expire' command")
        
        try:
            seconds = int(args[1])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        if self.store.set_expiry(args[0], seconds):
            return 1
        else:
            return 0
    
    def cmd_ttl(self, args):
        """TTL key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'ttl' command")
        
        return self.store.get_ttl(args[0])
    
    def cmd_keys(self, args):
        """KEYS pattern"""
        pattern = "*" if len(args) == 0 else args[0]
        return self.store.get_all_keys(pattern)
    
    def cmd_incr(self, args):
        """INCR key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'incr' command")
        
        key = args[0]
        current_value = self.store.get_string(key)
        
        if current_value is None:
            new_value = 1
        else:
            try:
                new_value = int(current_value) + 1
            except ValueError:
                return Exception("ERR value is not an integer")
        
        self.store.set_string(key, str(new_value))
        return new_value
    
    def cmd_decr(self, args):
        """DECR key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'decr' command")
        
        key = args[0]
        current_value = self.store.get_string(key)
        
        if current_value is None:
            new_value = -1
        else:
            try:
                new_value = int(current_value) - 1
            except ValueError:
                return Exception("ERR value is not an integer")
        
        self.store.set_string(key, str(new_value))
        return new_value
    
    # =============================================================================
    # LIST COMMANDS
    # =============================================================================
    
    def cmd_lpush(self, args):
        """LPUSH key element [element ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'lpush' command")
        
        key = args[0]
        deque = self.store.get_list(key, create_if_not_exists=True)
        
        # Push elements in reverse order (last argument becomes first)
        for i in range(len(args) - 1, 0, -1):
            deque.append_left(args[i])
        
        return len(deque)
    
    def cmd_rpush(self, args):
        """RPUSH key element [element ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'rpush' command")
        
        key = args[0]
        deque = self.store.get_list(key, create_if_not_exists=True)
        
        for i in range(1, len(args)):
            deque.append_right(args[i])
        
        return len(deque)
    
    def cmd_lpop(self, args):
        """LPOP key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'lpop' command")
        
        deque = self.store.get_list(args[0])
        if deque is None or deque.is_empty():
            return None
        
        return deque.pop_left()
    
    def cmd_rpop(self, args):
        """RPOP key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'rpop' command")
        
        deque = self.store.get_list(args[0])
        if deque is None or deque.is_empty():
            return None
        
        return deque.pop_right()
    
    def cmd_llen(self, args):
        """LLEN key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'llen' command")
        
        deque = self.store.get_list(args[0])
        if deque is None:
            return 0
        
        return len(deque)
    
    def cmd_lrange(self, args):
        """LRANGE key start stop"""
        if len(args) != 3:
            return Exception("ERR wrong number of arguments for 'lrange' command")
        
        try:
            start = int(args[1])
            stop = int(args[2])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        deque = self.store.get_list(args[0])
        if deque is None:
            return DArray()
        
        return deque.to_list(start, stop)
    
    # =============================================================================
    # SET COMMANDS
    # =============================================================================
    
    def cmd_sadd(self, args):
        """SADD key member [member ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'sadd' command")
        
        key = args[0]
        hash_set = self.store.get_set(key, create_if_not_exists=True)
        
        added_count = 0
        for i in range(1, len(args)):
            if hash_set.add(args[i]):
                added_count += 1
        
        return added_count
    
    def cmd_srem(self, args):
        """SREM key member [member ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'srem' command")
        
        hash_set = self.store.get_set(args[0])
        if hash_set is None:
            return 0
        
        removed_count = 0
        for i in range(1, len(args)):
            if hash_set.remove(args[i]):
                removed_count += 1
        
        return removed_count
    
    def cmd_smembers(self, args):
        """SMEMBERS key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'smembers' command")
        
        hash_set = self.store.get_set(args[0])
        if hash_set is None:
            return DArray()
        
        return hash_set.to_list()
    
    def cmd_scard(self, args):
        """SCARD key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'scard' command")
        
        hash_set = self.store.get_set(args[0])
        if hash_set is None:
            return 0
        
        return hash_set.size()
    
    def cmd_sismember(self, args):
        """SISMEMBER key member"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'sismember' command")
        
        hash_set = self.store.get_set(args[0])
        if hash_set is None:
            return 0
        
        return 1 if hash_set.contains(args[1]) else 0
    
    # =============================================================================
    # HASH COMMANDS
    # =============================================================================
    
    def cmd_hset(self, args):
        """HSET key field value"""
        if len(args) != 3:
            return Exception("ERR wrong number of arguments for 'hset' command")
        
        key, field, value = args[0], args[1], args[2]
        hash_table = self.store.get_hash(key, create_if_not_exists=True)
        
        was_new = not hash_table.contains(field)
        hash_table.put(field, value)
        
        return 1 if was_new else 0
    
    def cmd_hget(self, args):
        """HGET key field"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'hget' command")
        
        hash_table = self.store.get_hash(args[0])
        if hash_table is None:
            return None
        
        try:
            return hash_table.get(args[1])
        except KeyError:
            return None
    
    def cmd_hdel(self, args):
        """HDEL key field [field ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'hdel' command")
        
        hash_table = self.store.get_hash(args[0])
        if hash_table is None:
            return 0
        
        deleted_count = 0
        for i in range(1, len(args)):
            try:
                hash_table.remove(args[i])
                deleted_count += 1
            except KeyError:
                pass
        
        return deleted_count
    
    def cmd_hgetall(self, args):
        """HGETALL key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'hgetall' command")
        
        hash_table = self.store.get_hash(args[0])
        if hash_table is None:
            return DArray()
        
        result = DArray()
        items = hash_table.items()
        for i in range(len(items)):
            key, value = items[i]
            result.append(key)
            result.append(value)
        
        return result
    
    def cmd_hkeys(self, args):
        """HKEYS key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'hkeys' command")
        
        hash_table = self.store.get_hash(args[0])
        if hash_table is None:
            return DArray()
        
        return hash_table.keys()
    
    def cmd_hvals(self, args):
        """HVALS key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'hvals' command")
        
        hash_table = self.store.get_hash(args[0])
        if hash_table is None:
            return DArray()
        
        return hash_table.values()
    
    # =============================================================================
    # SERVER COMMANDS
    # =============================================================================
    
    def cmd_ping(self, args):
        """PING [message]"""
        if len(args) == 0:
            return "PONG"
        else:
            return args[0]
    
    def cmd_info(self, args):
        """INFO"""
        return "redstar_version:1.0.0-scratch\nos:Python\narch_bits:64"
    
    def cmd_flushall(self, args):
        """FLUSHALL"""
        self.store.clear_all()
        return "OK"