import time
from core_datastructures.dynamic_array import DArray
from core_datastructures.hash_table import HashTable


class StreamEntry:
    """Single entry in a Redis stream"""
    
    def __init__(self, stream_id, fields):
        self.id = stream_id
        self.fields = fields  # HashTable of field->value mappings
        self.timestamp = None
        self.sequence = None
        
        # Parse ID (format: timestamp-sequence)
        if '-' in stream_id:
            parts = stream_id.split('-')
            if len(parts) == 2:
                try:
                    self.timestamp = int(parts[0])
                    self.sequence = int(parts[1])
                except ValueError:
                    pass


class StreamConsumerGroup:
    """Consumer group for Redis streams"""
    
    def __init__(self, name, stream, last_delivered_id="0-0"):
        self.name = name
        self.stream = stream
        self.last_delivered_id = last_delivered_id
        self.consumers = HashTable()  # consumer_name -> consumer_info
        self.pending = HashTable()   # entry_id -> consumer_name
    
    def add_consumer(self, consumer_name):
        """Add a consumer to the group"""
        if consumer_name not in self.consumers:
            self.consumers[consumer_name] = {
                'pending_count': 0,
                'idle_time': 0,
                'last_seen': int(time.time() * 1000)
            }
            return True
        return False
    
    def remove_consumer(self, consumer_name):
        """Remove a consumer from the group"""
        if consumer_name in self.consumers:
            del self.consumers[consumer_name]
            return True
        return False


class Stream:
    """
    Redis-compatible Stream data structure
    Append-only log with unique IDs and consumer groups
    """
    
    def __init__(self):
        self.entries = DArray()  # Ordered list of StreamEntry objects
        self.length = 0
        self.last_id = "0-0"
        self.consumer_groups = HashTable()  # group_name -> StreamConsumerGroup
        
        # For efficient ID-based lookups
        self.id_to_index = HashTable()  # stream_id -> index in entries
    
    def _generate_id(self, id_pattern=None):
        """
        Generate a stream ID
        Format: timestamp-sequence or * for auto-generation
        """
        current_time = int(time.time() * 1000)
        
        if id_pattern is None or id_pattern == "*":
            # Auto-generate ID
            if self.last_id == "0-0":
                return f"{current_time}-0"
            
            last_parts = self.last_id.split('-')
            last_timestamp = int(last_parts[0])
            last_sequence = int(last_parts[1])
            
            if current_time > last_timestamp:
                return f"{current_time}-0"
            elif current_time == last_timestamp:
                return f"{current_time}-{last_sequence + 1}"
            else:
                # Current time is less than last timestamp, use last timestamp
                return f"{last_timestamp}-{last_sequence + 1}"
        
        # Validate provided ID
        if '-' not in id_pattern:
            raise ValueError("Invalid stream ID format")
        
        parts = id_pattern.split('-')
        if len(parts) != 2:
            raise ValueError("Invalid stream ID format")
        
        try:
            timestamp = int(parts[0])
            sequence = int(parts[1])
        except ValueError:
            raise ValueError("Invalid stream ID format")
        
        # Check if ID is greater than last ID
        if self._compare_ids(id_pattern, self.last_id) <= 0:
            raise ValueError("The ID specified in XADD is equal or smaller than the target stream top item")
        
        return id_pattern
    
    def _compare_ids(self, id1, id2):
        """
        Compare two stream IDs
        Returns: -1 if id1 < id2, 0 if equal, 1 if id1 > id2
        """
        parts1 = id1.split('-')
        parts2 = id2.split('-')
        
        ts1, seq1 = int(parts1[0]), int(parts1[1])
        ts2, seq2 = int(parts2[0]), int(parts2[1])
        
        if ts1 < ts2:
            return -1
        elif ts1 > ts2:
            return 1
        else:
            if seq1 < seq2:
                return -1
            elif seq1 > seq2:
                return 1
            else:
                return 0
    
    def xadd(self, stream_id, fields_dict):
        """
        Add entry to stream
        Returns the generated/validated stream ID
        """
        # Generate or validate ID
        actual_id = self._generate_id(stream_id)
        
        # Create fields HashTable
        fields = HashTable()
        for key, value in fields_dict.items():
            fields[key] = value
        
        # Create entry
        entry = StreamEntry(actual_id, fields)
        
        # Add to stream
        self.entries.append(entry)
        self.id_to_index[actual_id] = len(self.entries) - 1
        self.length += 1
        self.last_id = actual_id
        
        return actual_id
    
    def xlen(self):
        """Return number of entries in stream"""
        return self.length
    
    def xrange(self, start="0-0", end="+", count=None):
        """
        Get entries in ID range [start, end]
        Special values: - (minimum ID), + (maximum ID)
        """
        if start == "-":
            start = "0-0"
        if end == "+":
            end = None  # No upper limit
        
        result = DArray()
        collected = 0
        
        for i in range(len(self.entries)):
            entry = self.entries[i]
            
            # Check if entry is in range
            if self._compare_ids(entry.id, start) >= 0:
                if end is None or self._compare_ids(entry.id, end) <= 0:
                    # Convert entry to result format
                    entry_data = DArray()
                    entry_data.append(entry.id)
                    
                    fields_array = DArray()
                    for field in entry.fields:
                        fields_array.append(field)
                        fields_array.append(entry.fields[field])
                    
                    entry_data.append(fields_array)
                    result.append(entry_data)
                    
                    collected += 1
                    if count is not None and collected >= count:
                        break
        
        return result
    
    def xrevrange(self, start="+", end="-", count=None):
        """
        Get entries in reverse ID range [start, end]
        Like XRANGE but in reverse order
        """
        if start == "+":
            start = None  # No upper limit
        if end == "-":
            end = "0-0"
        
        result = DArray()
        collected = 0
        
        # Iterate in reverse order
        for i in range(len(self.entries) - 1, -1, -1):
            entry = self.entries[i]
            
            # Check if entry is in range
            if start is None or self._compare_ids(entry.id, start) <= 0:
                if self._compare_ids(entry.id, end) >= 0:
                    # Convert entry to result format
                    entry_data = DArray()
                    entry_data.append(entry.id)
                    
                    fields_array = DArray()
                    for field in entry.fields:
                        fields_array.append(field)
                        fields_array.append(entry.fields[field])
                    
                    entry_data.append(fields_array)
                    result.append(entry_data)
                    
                    collected += 1
                    if count is not None and collected >= count:
                        break
        
        return result
    
    def xread(self, last_id="0-0", count=None, block=None):
        """
        Read entries after last_id
        If block is specified, this would block (not implemented here)
        """
        result = DArray()
        collected = 0
        
        for i in range(len(self.entries)):
            entry = self.entries[i]
            
            if self._compare_ids(entry.id, last_id) > 0:
                entry_data = DArray()
                entry_data.append(entry.id)
                
                fields_array = DArray()
                for field in entry.fields:
                    fields_array.append(field)
                    fields_array.append(entry.fields[field])
                
                entry_data.append(fields_array)
                result.append(entry_data)
                
                collected += 1
                if count is not None and collected >= count:
                    break
        
        return result
    
    def xtrim(self, strategy="MAXLEN", threshold=1000, approximate=False):
        """
        Trim stream to specified length
        Strategy can be MAXLEN (by count) or MINID (by ID)
        """
        if strategy.upper() == "MAXLEN":
            if self.length <= threshold:
                return 0
            
            entries_to_remove = self.length - threshold
            
            # Remove entries from beginning
            for i in range(entries_to_remove):
                if len(self.entries) > 0:
                    removed_entry = self.entries[0]
                    
                    # Remove from entries (shift all elements)
                    new_entries = DArray()
                    for j in range(1, len(self.entries)):
                        new_entries.append(self.entries[j])
                    self.entries = new_entries
                    
                    # Remove from index
                    if removed_entry.id in self.id_to_index:
                        del self.id_to_index[removed_entry.id]
                    
                    self.length -= 1
            
            # Update indices
            for i in range(len(self.entries)):
                self.id_to_index[self.entries[i].id] = i
            
            return entries_to_remove
        
        return 0
    
    def xgroup_create(self, group_name, start_id="$"):
        """Create a consumer group"""
        if group_name in self.consumer_groups:
            return False  # Group already exists
        
        if start_id == "$":
            start_id = self.last_id
        
        self.consumer_groups[group_name] = StreamConsumerGroup(group_name, self, start_id)
        return True
    
    def xgroup_destroy(self, group_name):
        """Destroy a consumer group"""
        if group_name in self.consumer_groups:
            del self.consumer_groups[group_name]
            return True
        return False
    
    def xgroup_delconsumer(self, group_name, consumer_name):
        """Delete a consumer from a group"""
        if group_name not in self.consumer_groups:
            return False
        
        group = self.consumer_groups[group_name]
        return group.remove_consumer(consumer_name)
    
    def __len__(self):
        return self.length
    
    def size(self):
        return self.length