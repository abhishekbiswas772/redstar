from core_datastructures.hash_table import HashTable
from core_datastructures.dynamic_array import DArray
from redstar_commands.pubsub_commands import RedstarPubSubCommands
from redstar_commands.advanced_commands import RedstarAdvancedCommands
from redstar_commands.datatype_commands import RedstarDataTypeCommands


class RedstarCommandProcessor:
    def __init__(self, data_store, pubsub_manager=None):
        self.store = data_store
        self.pubsub_manager = pubsub_manager
        
        # Initialize pub/sub commands if manager is provided
        self.pubsub_commands = None
        if pubsub_manager:
            self.pubsub_commands = RedstarPubSubCommands(pubsub_manager)
        
        # Initialize advanced commands
        self.advanced_commands = RedstarAdvancedCommands(data_store)
        self.datatype_commands = RedstarDataTypeCommands(data_store)
        
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
        
        # Pub/Sub commands (if pub/sub manager is available)
        if self.pubsub_commands:
            self.commands['SUBSCRIBE'] = self.cmd_subscribe
            self.commands['UNSUBSCRIBE'] = self.cmd_unsubscribe
            self.commands['PSUBSCRIBE'] = self.cmd_psubscribe
            self.commands['PUNSUBSCRIBE'] = self.cmd_punsubscribe
            self.commands['PUBLISH'] = self.cmd_publish
            self.commands['PUBSUB'] = self.cmd_pubsub
        
        # Advanced String commands
        self.commands['APPEND'] = self.cmd_append
        self.commands['STRLEN'] = self.cmd_strlen
        self.commands['GETRANGE'] = self.cmd_getrange
        self.commands['SETRANGE'] = self.cmd_setrange
        self.commands['MGET'] = self.cmd_mget
        self.commands['MSET'] = self.cmd_mset
        self.commands['GETSET'] = self.cmd_getset
        
        # Advanced List commands
        self.commands['LINDEX'] = self.cmd_lindex
        self.commands['LSET'] = self.cmd_lset
        
        # Advanced Set commands
        self.commands['SPOP'] = self.cmd_spop
        self.commands['SRANDMEMBER'] = self.cmd_srandmember
        self.commands['SUNION'] = self.cmd_sunion
        self.commands['SINTER'] = self.cmd_sinter
        self.commands['SDIFF'] = self.cmd_sdiff
        
        # Advanced Hash commands
        self.commands['HMSET'] = self.cmd_hmset
        self.commands['HMGET'] = self.cmd_hmget
        self.commands['HEXISTS'] = self.cmd_hexists
        self.commands['HLEN'] = self.cmd_hlen
        self.commands['HINCRBY'] = self.cmd_hincrby
        
        # Sorted Set commands
        self.commands['ZADD'] = self.cmd_zadd
        self.commands['ZREM'] = self.cmd_zrem
        self.commands['ZSCORE'] = self.cmd_zscore
        self.commands['ZRANGE'] = self.cmd_zrange
        self.commands['ZREVRANGE'] = self.cmd_zrevrange
        self.commands['ZCARD'] = self.cmd_zcard
        self.commands['ZRANK'] = self.cmd_zrank
        
        # Bitmap commands
        self.commands['SETBIT'] = self.cmd_setbit
        self.commands['GETBIT'] = self.cmd_getbit
        self.commands['BITCOUNT'] = self.cmd_bitcount
        self.commands['BITOP'] = self.cmd_bitop
        
        # HyperLogLog commands
        self.commands['PFADD'] = self.cmd_pfadd
        self.commands['PFCOUNT'] = self.cmd_pfcount
        self.commands['PFMERGE'] = self.cmd_pfmerge
        
        # Geospatial commands
        self.commands['GEOADD'] = self.cmd_geoadd
        self.commands['GEODIST'] = self.cmd_geodist
        self.commands['GEOPOS'] = self.cmd_geopos
        self.commands['GEORADIUS'] = self.cmd_georadius
        
        # Stream commands
        self.commands['XADD'] = self.cmd_xadd
        self.commands['XLEN'] = self.cmd_xlen
        self.commands['XRANGE'] = self.cmd_xrange
        self.commands['XREAD'] = self.cmd_xread
    
    def execute_command(self, command_array, client_handler=None):
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
            
            # Check if this is a pub/sub command that needs client_handler
            if cmd_name in ['SUBSCRIBE', 'UNSUBSCRIBE', 'PSUBSCRIBE', 'PUNSUBSCRIBE', 'PUBLISH', 'PUBSUB']:
                if client_handler is None:
                    return Exception("ERR pub/sub commands require client context")
                return command_func(args, client_handler)
            else:
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
    
    # =============================================================================
    # PUB/SUB COMMANDS
    # =============================================================================
    
    def cmd_subscribe(self, args, client_handler):
        """SUBSCRIBE channel [channel ...]"""
        if not self.pubsub_commands:
            return Exception("ERR pub/sub not available")
        return self.pubsub_commands.cmd_subscribe(args, client_handler)
    
    def cmd_unsubscribe(self, args, client_handler):
        """UNSUBSCRIBE [channel [channel ...]]"""
        if not self.pubsub_commands:
            return Exception("ERR pub/sub not available")
        return self.pubsub_commands.cmd_unsubscribe(args, client_handler)
    
    def cmd_psubscribe(self, args, client_handler):
        """PSUBSCRIBE pattern [pattern ...]"""
        if not self.pubsub_commands:
            return Exception("ERR pub/sub not available")
        return self.pubsub_commands.cmd_psubscribe(args, client_handler)
    
    def cmd_punsubscribe(self, args, client_handler):
        """PUNSUBSCRIBE [pattern [pattern ...]]"""
        if not self.pubsub_commands:
            return Exception("ERR pub/sub not available")
        return self.pubsub_commands.cmd_punsubscribe(args, client_handler)
    
    def cmd_publish(self, args, client_handler):
        """PUBLISH channel message"""
        if not self.pubsub_commands:
            return Exception("ERR pub/sub not available")
        return self.pubsub_commands.cmd_publish(args, client_handler)
    
    def cmd_pubsub(self, args, client_handler):
        """PUBSUB subcommand [argument [argument ...]]"""
        if not self.pubsub_commands:
            return Exception("ERR pub/sub not available")
        return self.pubsub_commands.cmd_pubsub(args, client_handler)
    
    # =============================================================================
    # ADVANCED STRING COMMANDS
    # =============================================================================
    
    def cmd_append(self, args):
        return self.advanced_commands.cmd_append(args)
    
    def cmd_strlen(self, args):
        return self.advanced_commands.cmd_strlen(args)
    
    def cmd_getrange(self, args):
        return self.advanced_commands.cmd_getrange(args)
    
    def cmd_setrange(self, args):
        return self.advanced_commands.cmd_setrange(args)
    
    def cmd_mget(self, args):
        return self.advanced_commands.cmd_mget(args)
    
    def cmd_mset(self, args):
        return self.advanced_commands.cmd_mset(args)
    
    def cmd_getset(self, args):
        return self.advanced_commands.cmd_getset(args)
    
    # =============================================================================
    # ADVANCED LIST COMMANDS
    # =============================================================================
    
    def cmd_lindex(self, args):
        return self.advanced_commands.cmd_lindex(args)
    
    def cmd_lset(self, args):
        return self.advanced_commands.cmd_lset(args)
    
    # =============================================================================
    # ADVANCED SET COMMANDS
    # =============================================================================
    
    def cmd_spop(self, args):
        return self.advanced_commands.cmd_spop(args)
    
    def cmd_srandmember(self, args):
        return self.advanced_commands.cmd_srandmember(args)
    
    def cmd_sunion(self, args):
        return self.advanced_commands.cmd_sunion(args)
    
    def cmd_sinter(self, args):
        return self.advanced_commands.cmd_sinter(args)
    
    def cmd_sdiff(self, args):
        return self.advanced_commands.cmd_sdiff(args)
    
    # =============================================================================
    # ADVANCED HASH COMMANDS
    # =============================================================================
    
    def cmd_hmset(self, args):
        return self.advanced_commands.cmd_hmset(args)
    
    def cmd_hmget(self, args):
        return self.advanced_commands.cmd_hmget(args)
    
    def cmd_hexists(self, args):
        return self.advanced_commands.cmd_hexists(args)
    
    def cmd_hlen(self, args):
        return self.advanced_commands.cmd_hlen(args)
    
    def cmd_hincrby(self, args):
        return self.advanced_commands.cmd_hincrby(args)
    
    # =============================================================================
    # SORTED SET COMMANDS
    # =============================================================================
    
    def cmd_zadd(self, args):
        return self.datatype_commands.cmd_zadd(args)
    
    def cmd_zrem(self, args):
        return self.datatype_commands.cmd_zrem(args)
    
    def cmd_zscore(self, args):
        return self.datatype_commands.cmd_zscore(args)
    
    def cmd_zrange(self, args):
        return self.datatype_commands.cmd_zrange(args)
    
    def cmd_zrevrange(self, args):
        return self.datatype_commands.cmd_zrevrange(args)
    
    def cmd_zcard(self, args):
        return self.datatype_commands.cmd_zcard(args)
    
    def cmd_zrank(self, args):
        return self.datatype_commands.cmd_zrank(args)
    
    # =============================================================================
    # BITMAP COMMANDS
    # =============================================================================
    
    def cmd_setbit(self, args):
        return self.datatype_commands.cmd_setbit(args)
    
    def cmd_getbit(self, args):
        return self.datatype_commands.cmd_getbit(args)
    
    def cmd_bitcount(self, args):
        return self.datatype_commands.cmd_bitcount(args)
    
    def cmd_bitop(self, args):
        return self.datatype_commands.cmd_bitop(args)
    
    # =============================================================================
    # HYPERLOGLOG COMMANDS
    # =============================================================================
    
    def cmd_pfadd(self, args):
        return self.datatype_commands.cmd_pfadd(args)
    
    def cmd_pfcount(self, args):
        return self.datatype_commands.cmd_pfcount(args)
    
    def cmd_pfmerge(self, args):
        return self.datatype_commands.cmd_pfmerge(args)
    
    # =============================================================================
    # GEOSPATIAL COMMANDS
    # =============================================================================
    
    def cmd_geoadd(self, args):
        return self.datatype_commands.cmd_geoadd(args)
    
    def cmd_geodist(self, args):
        return self.datatype_commands.cmd_geodist(args)
    
    def cmd_geopos(self, args):
        return self.datatype_commands.cmd_geopos(args)
    
    def cmd_georadius(self, args):
        return self.datatype_commands.cmd_georadius(args)
    
    # =============================================================================
    # STREAM COMMANDS
    # =============================================================================
    
    def cmd_xadd(self, args):
        return self.datatype_commands.cmd_xadd(args)
    
    def cmd_xlen(self, args):
        return self.datatype_commands.cmd_xlen(args)
    
    def cmd_xrange(self, args):
        return self.datatype_commands.cmd_xrange(args)
    
    def cmd_xread(self, args):
        return self.datatype_commands.cmd_xread(args)