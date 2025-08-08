from core_datastructures.dynamic_array import DArray
from core_datastructures.hash_table import HashTable


class RedstarDataTypeCommands:
    """
    Commands for advanced Redis data types:
    Sorted Sets, Bitmaps, HyperLogLogs, Geospatial, and Streams
    """
    
    def __init__(self, data_store):
        self.store = data_store
    
    # =============================================================================
    # SORTED SET COMMANDS
    # =============================================================================
    
    def cmd_zadd(self, args):
        """ZADD key score member [score member ...]"""
        if len(args) < 3 or len(args) % 2 == 0:
            return Exception("ERR wrong number of arguments for 'zadd' command")
        
        key = args[0]
        zset = self.store.get_sorted_set(key, create_if_not_exists=True)
        
        added_count = 0
        for i in range(1, len(args), 2):
            try:
                score = float(args[i])
            except ValueError:
                return Exception("ERR value is not a valid float")
            
            member = args[i + 1]
            if zset.add(member, score):
                added_count += 1
        
        return added_count
    
    def cmd_zrem(self, args):
        """ZREM key member [member ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'zrem' command")
        
        key = args[0]
        zset = self.store.get_sorted_set(key)
        
        if zset is None:
            return 0
        
        removed_count = 0
        for i in range(1, len(args)):
            if zset.remove(args[i]):
                removed_count += 1
        
        return removed_count
    
    def cmd_zscore(self, args):
        """ZSCORE key member"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'zscore' command")
        
        key, member = args[0], args[1]
        zset = self.store.get_sorted_set(key)
        
        if zset is None:
            return None
        
        score = zset.get_score(member)
        return str(score) if score is not None else None
    
    def cmd_zrange(self, args):
        """ZRANGE key start stop [WITHSCORES]"""
        if len(args) < 3 or len(args) > 4:
            return Exception("ERR wrong number of arguments for 'zrange' command")
        
        key = args[0]
        try:
            start = int(args[1])
            stop = int(args[2])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        withscores = False
        if len(args) == 4 and args[3].upper() == "WITHSCORES":
            withscores = True
        
        zset = self.store.get_sorted_set(key)
        if zset is None:
            return DArray()
        
        if withscores:
            return zset.get_range_with_scores(start, stop)
        else:
            return zset.get_range(start, stop)
    
    def cmd_zrevrange(self, args):
        """ZREVRANGE key start stop [WITHSCORES]"""
        if len(args) < 3 or len(args) > 4:
            return Exception("ERR wrong number of arguments for 'zrevrange' command")
        
        key = args[0]
        try:
            start = int(args[1])
            stop = int(args[2])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        withscores = False
        if len(args) == 4 and args[3].upper() == "WITHSCORES":
            withscores = True
        
        zset = self.store.get_sorted_set(key)
        if zset is None:
            return DArray()
        
        if withscores:
            return zset.get_range_with_scores(start, stop, reverse=True)
        else:
            return zset.get_range(start, stop, reverse=True)
    
    def cmd_zcard(self, args):
        """ZCARD key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'zcard' command")
        
        zset = self.store.get_sorted_set(args[0])
        return len(zset) if zset is not None else 0
    
    def cmd_zrank(self, args):
        """ZRANK key member"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'zrank' command")
        
        key, member = args[0], args[1]
        zset = self.store.get_sorted_set(key)
        
        if zset is None:
            return None
        
        return zset.get_rank(member)
    
    # =============================================================================
    # BITMAP COMMANDS
    # =============================================================================
    
    def cmd_setbit(self, args):
        """SETBIT key offset value"""
        if len(args) != 3:
            return Exception("ERR wrong number of arguments for 'setbit' command")
        
        key = args[0]
        try:
            offset = int(args[1])
            value = int(args[2])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        if value not in (0, 1):
            return Exception("ERR bit is not an integer or out of range")
        
        bitmap = self.store.get_bitmap(key, create_if_not_exists=True)
        return bitmap.setbit(offset, value)
    
    def cmd_getbit(self, args):
        """GETBIT key offset"""
        if len(args) != 2:
            return Exception("ERR wrong number of arguments for 'getbit' command")
        
        key = args[0]
        try:
            offset = int(args[1])
        except ValueError:
            return Exception("ERR value is not an integer")
        
        bitmap = self.store.get_bitmap(key)
        if bitmap is None:
            return 0
        
        return bitmap.getbit(offset)
    
    def cmd_bitcount(self, args):
        """BITCOUNT key [start end]"""
        if len(args) < 1 or len(args) > 3:
            return Exception("ERR wrong number of arguments for 'bitcount' command")
        
        key = args[0]
        start, end = None, None
        
        if len(args) >= 2:
            try:
                start = int(args[1])
            except ValueError:
                return Exception("ERR value is not an integer")
        
        if len(args) == 3:
            try:
                end = int(args[2])
            except ValueError:
                return Exception("ERR value is not an integer")
        
        bitmap = self.store.get_bitmap(key)
        if bitmap is None:
            return 0
        
        return bitmap.bitcount(start, end)
    
    def cmd_bitop(self, args):
        """BITOP operation destkey key [key ...]"""
        if len(args) < 3:
            return Exception("ERR wrong number of arguments for 'bitop' command")
        
        operation = args[0].upper()
        destkey = args[1]
        
        if operation not in ["AND", "OR", "XOR", "NOT"]:
            return Exception("ERR syntax error")
        
        if operation == "NOT" and len(args) != 3:
            return Exception("ERR BITOP NOT must be called with a single source key")
        
        if operation == "NOT":
            # NOT operation
            source_bitmap = self.store.get_bitmap(args[2])
            if source_bitmap is None:
                from core_datastructures.bitmap import Bitmap
                source_bitmap = Bitmap()
            
            result_bitmap = source_bitmap.bitop_not()
            
            # Store result
            from redstar_core.redstar_value import RedStarValue
            self.store.data[destkey] = RedStarValue(result_bitmap, 'bitmap')
            
            return len(result_bitmap)
        
        else:
            # AND, OR, XOR operations
            from core_datastructures.bitmap import Bitmap
            
            first_bitmap = self.store.get_bitmap(args[2])
            if first_bitmap is None:
                first_bitmap = Bitmap()
            
            result_bitmap = first_bitmap
            
            for i in range(3, len(args)):
                other_bitmap = self.store.get_bitmap(args[i])
                if other_bitmap is None:
                    other_bitmap = Bitmap()
                
                if operation == "AND":
                    result_bitmap = result_bitmap.bitop_and(other_bitmap)
                elif operation == "OR":
                    result_bitmap = result_bitmap.bitop_or(other_bitmap)
                elif operation == "XOR":
                    result_bitmap = result_bitmap.bitop_xor(other_bitmap)
            
            # Store result
            from redstar_core.redstar_value import RedStarValue
            self.store.data[destkey] = RedStarValue(result_bitmap, 'bitmap')
            
            return len(result_bitmap)
    
    # =============================================================================
    # HYPERLOGLOG COMMANDS
    # =============================================================================
    
    def cmd_pfadd(self, args):
        """PFADD key element [element ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'pfadd' command")
        
        key = args[0]
        hll = self.store.get_hyperloglog(key, create_if_not_exists=True)
        
        changed = False
        for i in range(1, len(args)):
            if hll.add(args[i]):
                changed = True
        
        return 1 if changed else 0
    
    def cmd_pfcount(self, args):
        """PFCOUNT key [key ...]"""
        if len(args) == 0:
            return Exception("ERR wrong number of arguments for 'pfcount' command")
        
        if len(args) == 1:
            # Single key
            hll = self.store.get_hyperloglog(args[0])
            return int(hll.count()) if hll is not None else 0
        
        else:
            # Multiple keys - merge and count
            from core_datastructures.hyperloglog import HyperLogLog
            merged_hll = HyperLogLog()
            
            for i in range(len(args)):
                hll = self.store.get_hyperloglog(args[i])
                if hll is not None:
                    merged_hll = merged_hll.merge(hll)
            
            return int(merged_hll.count())
    
    def cmd_pfmerge(self, args):
        """PFMERGE destkey sourcekey [sourcekey ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'pfmerge' command")
        
        destkey = args[0]
        
        # Get or create destination HLL
        dest_hll = self.store.get_hyperloglog(destkey, create_if_not_exists=True)
        
        # Merge all source HLLs
        for i in range(1, len(args)):
            source_hll = self.store.get_hyperloglog(args[i])
            if source_hll is not None:
                dest_hll = dest_hll.merge(source_hll)
        
        # Store merged result
        from redstar_core.redstar_value import RedStarValue
        self.store.data[destkey] = RedStarValue(dest_hll, 'hyperloglog')
        
        return "OK"
    
    # =============================================================================
    # GEOSPATIAL COMMANDS
    # =============================================================================
    
    def cmd_geoadd(self, args):
        """GEOADD key longitude latitude member [longitude latitude member ...]"""
        if len(args) < 4 or (len(args) - 1) % 3 != 0:
            return Exception("ERR wrong number of arguments for 'geoadd' command")
        
        key = args[0]
        geo = self.store.get_geospatial(key, create_if_not_exists=True)
        
        added_count = 0
        for i in range(1, len(args), 3):
            try:
                longitude = float(args[i])
                latitude = float(args[i + 1])
            except ValueError:
                return Exception("ERR value is not a valid float")
            
            member = args[i + 2]
            
            try:
                if geo.add(longitude, latitude, member):
                    added_count += 1
            except ValueError as e:
                return Exception(f"ERR {str(e)}")
        
        return added_count
    
    def cmd_geodist(self, args):
        """GEODIST key member1 member2 [m|km|ft|mi]"""
        if len(args) < 3 or len(args) > 4:
            return Exception("ERR wrong number of arguments for 'geodist' command")
        
        key = args[0]
        member1 = args[1]
        member2 = args[2]
        unit = args[3] if len(args) == 4 else 'm'
        
        geo = self.store.get_geospatial(key)
        if geo is None:
            return None
        
        try:
            distance = geo.distance(member1, member2, unit)
            return str(distance) if distance is not None else None
        except ValueError as e:
            return Exception(f"ERR {str(e)}")
    
    def cmd_geopos(self, args):
        """GEOPOS key member [member ...]"""
        if len(args) < 2:
            return Exception("ERR wrong number of arguments for 'geopos' command")
        
        key = args[0]
        geo = self.store.get_geospatial(key)
        
        result = DArray()
        for i in range(1, len(args)):
            member = args[i]
            if geo is None:
                result.append(None)
            else:
                pos = geo.get_position(member)
                if pos is None:
                    result.append(None)
                else:
                    coord_array = DArray()
                    coord_array.append(str(pos[0]))  # longitude
                    coord_array.append(str(pos[1]))  # latitude
                    result.append(coord_array)
        
        return result
    
    def cmd_georadius(self, args):
        """GEORADIUS key longitude latitude radius m|km|ft|mi [WITHCOORD] [WITHDIST] [COUNT count]"""
        if len(args) < 5:
            return Exception("ERR wrong number of arguments for 'georadius' command")
        
        key = args[0]
        try:
            longitude = float(args[1])
            latitude = float(args[2])
            radius = float(args[3])
        except ValueError:
            return Exception("ERR value is not a valid float")
        
        unit = args[4]
        
        # Parse options
        withcoord = False
        withdist = False
        count = None
        
        i = 5
        while i < len(args):
            option = args[i].upper()
            if option == "WITHCOORD":
                withcoord = True
                i += 1
            elif option == "WITHDIST":
                withdist = True
                i += 1
            elif option == "COUNT":
                if i + 1 < len(args):
                    try:
                        count = int(args[i + 1])
                        i += 2
                    except ValueError:
                        return Exception("ERR value is not an integer")
                else:
                    return Exception("ERR syntax error")
            else:
                i += 1
        
        geo = self.store.get_geospatial(key)
        if geo is None:
            return DArray()
        
        try:
            if withdist:
                members_with_dist = geo.radius_with_dist(longitude, latitude, radius, unit, count)
                
                if withcoord:
                    # Return member, distance, coordinates
                    result = DArray()
                    for i in range(0, len(members_with_dist), 2):
                        member = members_with_dist[i]
                        distance = members_with_dist[i + 1]
                        pos = geo.get_position(member)
                        
                        member_info = DArray()
                        member_info.append(member)
                        member_info.append(distance)
                        
                        coords = DArray()
                        coords.append(str(pos[0]))
                        coords.append(str(pos[1]))
                        member_info.append(coords)
                        
                        result.append(member_info)
                    
                    return result
                else:
                    return members_with_dist
            else:
                members = geo.radius(longitude, latitude, radius, unit, count)
                
                if withcoord:
                    # Return member and coordinates
                    result = DArray()
                    for i in range(len(members)):
                        member = members[i]
                        pos = geo.get_position(member)
                        
                        member_info = DArray()
                        member_info.append(member)
                        
                        coords = DArray()
                        coords.append(str(pos[0]))
                        coords.append(str(pos[1]))
                        member_info.append(coords)
                        
                        result.append(member_info)
                    
                    return result
                else:
                    return members
        
        except ValueError as e:
            return Exception(f"ERR {str(e)}")
    
    # =============================================================================
    # STREAM COMMANDS (Basic implementation)
    # =============================================================================
    
    def cmd_xadd(self, args):
        """XADD key ID field value [field value ...]"""
        if len(args) < 4 or (len(args) - 2) % 2 != 0:
            return Exception("ERR wrong number of arguments for 'xadd' command")
        
        key = args[0]
        stream_id = args[1]
        
        stream = self.store.get_stream(key, create_if_not_exists=True)
        
        # Parse fields
        fields = {}
        for i in range(2, len(args), 2):
            field = args[i]
            value = args[i + 1]
            fields[field] = value
        
        try:
            return stream.xadd(stream_id, fields)
        except ValueError as e:
            return Exception(f"ERR {str(e)}")
    
    def cmd_xlen(self, args):
        """XLEN key"""
        if len(args) != 1:
            return Exception("ERR wrong number of arguments for 'xlen' command")
        
        stream = self.store.get_stream(args[0])
        return stream.xlen() if stream is not None else 0
    
    def cmd_xrange(self, args):
        """XRANGE key start end [COUNT count]"""
        if len(args) < 3 or len(args) > 5:
            return Exception("ERR wrong number of arguments for 'xrange' command")
        
        key = args[0]
        start = args[1]
        end = args[2]
        count = None
        
        if len(args) >= 4 and args[3].upper() == "COUNT":
            if len(args) == 5:
                try:
                    count = int(args[4])
                except ValueError:
                    return Exception("ERR value is not an integer")
        
        stream = self.store.get_stream(key)
        if stream is None:
            return DArray()
        
        return stream.xrange(start, end, count)
    
    def cmd_xread(self, args):
        """XREAD [COUNT count] [BLOCK milliseconds] STREAMS key [key ...] ID [ID ...]"""
        # Simplified XREAD implementation
        if len(args) < 3:
            return Exception("ERR wrong number of arguments for 'xread' command")
        
        # Find STREAMS keyword
        streams_idx = -1
        for i in range(len(args)):
            if args[i].upper() == "STREAMS":
                streams_idx = i
                break
        
        if streams_idx == -1 or streams_idx + 1 >= len(args):
            return Exception("ERR syntax error")
        
        # Parse keys and IDs
        remaining_args = len(args) - streams_idx - 1
        if remaining_args % 2 != 0:
            return Exception("ERR syntax error")
        
        num_streams = remaining_args // 2
        result = DArray()
        
        for i in range(num_streams):
            key = args[streams_idx + 1 + i]
            last_id = args[streams_idx + 1 + num_streams + i]
            
            stream = self.store.get_stream(key)
            if stream is not None:
                entries = stream.xread(last_id)
                if len(entries) > 0:
                    stream_result = DArray()
                    stream_result.append(key)
                    stream_result.append(entries)
                    result.append(stream_result)
        
        return result