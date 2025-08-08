class Bitmap:
    """
    Redis-compatible bitmap implementation
    Efficiently stores and manipulates bits using bytearray
    """
    
    def __init__(self, initial_data=None):
        if initial_data is None:
            self.data = bytearray()
        elif isinstance(initial_data, bytes):
            self.data = bytearray(initial_data)
        elif isinstance(initial_data, bytearray):
            self.data = initial_data
        elif isinstance(initial_data, str):
            self.data = bytearray(initial_data.encode('utf-8'))
        else:
            self.data = bytearray()
    
    def _ensure_capacity(self, bit_offset):
        """Ensure bitmap has enough capacity for the given bit offset"""
        byte_offset = bit_offset // 8
        while len(self.data) <= byte_offset:
            self.data.append(0)
    
    def setbit(self, offset, value):
        """
        Set bit at offset to value (0 or 1)
        Returns the previous bit value
        """
        if offset < 0:
            raise ValueError("Bit offset cannot be negative")
        
        self._ensure_capacity(offset)
        
        byte_offset = offset // 8
        bit_offset = offset % 8
        
        # Get current bit value
        current_bit = (self.data[byte_offset] >> (7 - bit_offset)) & 1
        
        # Set new bit value
        if value:
            self.data[byte_offset] |= (1 << (7 - bit_offset))
        else:
            self.data[byte_offset] &= ~(1 << (7 - bit_offset))
        
        return current_bit
    
    def getbit(self, offset):
        """Get bit value at offset"""
        if offset < 0:
            raise ValueError("Bit offset cannot be negative")
        
        byte_offset = offset // 8
        
        # If offset is beyond current data, return 0
        if byte_offset >= len(self.data):
            return 0
        
        bit_offset = offset % 8
        return (self.data[byte_offset] >> (7 - bit_offset)) & 1
    
    def bitcount(self, start=None, end=None):
        """
        Count number of bits set to 1
        If start/end provided, count only in byte range [start, end]
        """
        if not self.data:
            return 0
        
        data_to_count = self.data
        
        if start is not None or end is not None:
            if start is None:
                start = 0
            if end is None:
                end = len(self.data) - 1
            
            # Handle negative indices
            if start < 0:
                start = max(0, len(self.data) + start)
            if end < 0:
                end = max(-1, len(self.data) + end)
            
            if start > end or start >= len(self.data):
                return 0
            
            end = min(end, len(self.data) - 1)
            data_to_count = self.data[start:end + 1]
        
        # Count bits using Brian Kernighan's algorithm
        count = 0
        for byte in data_to_count:
            while byte:
                count += 1
                byte &= byte - 1  # Clear the lowest set bit
        
        return count
    
    def bitop_and(self, other_bitmap):
        """Bitwise AND with another bitmap"""
        if not isinstance(other_bitmap, Bitmap):
            raise TypeError("Expected Bitmap instance")
        
        # Create result bitmap
        max_len = max(len(self.data), len(other_bitmap.data))
        result = Bitmap()
        result.data = bytearray(max_len)
        
        for i in range(max_len):
            byte1 = self.data[i] if i < len(self.data) else 0
            byte2 = other_bitmap.data[i] if i < len(other_bitmap.data) else 0
            result.data[i] = byte1 & byte2
        
        return result
    
    def bitop_or(self, other_bitmap):
        """Bitwise OR with another bitmap"""
        if not isinstance(other_bitmap, Bitmap):
            raise TypeError("Expected Bitmap instance")
        
        max_len = max(len(self.data), len(other_bitmap.data))
        result = Bitmap()
        result.data = bytearray(max_len)
        
        for i in range(max_len):
            byte1 = self.data[i] if i < len(self.data) else 0
            byte2 = other_bitmap.data[i] if i < len(other_bitmap.data) else 0
            result.data[i] = byte1 | byte2
        
        return result
    
    def bitop_xor(self, other_bitmap):
        """Bitwise XOR with another bitmap"""
        if not isinstance(other_bitmap, Bitmap):
            raise TypeError("Expected Bitmap instance")
        
        max_len = max(len(self.data), len(other_bitmap.data))
        result = Bitmap()
        result.data = bytearray(max_len)
        
        for i in range(max_len):
            byte1 = self.data[i] if i < len(self.data) else 0
            byte2 = other_bitmap.data[i] if i < len(other_bitmap.data) else 0
            result.data[i] = byte1 ^ byte2
        
        return result
    
    def bitop_not(self):
        """Bitwise NOT"""
        result = Bitmap()
        result.data = bytearray(len(self.data))
        
        for i in range(len(self.data)):
            result.data[i] = ~self.data[i] & 0xFF  # Keep only 8 bits
        
        return result
    
    def bitpos(self, bit_value, start=None, end=None):
        """
        Find position of first bit set to bit_value (0 or 1)
        Returns -1 if not found
        """
        if bit_value not in (0, 1):
            raise ValueError("Bit value must be 0 or 1")
        
        if not self.data:
            return -1 if bit_value == 1 else 0
        
        data_range = self.data
        byte_start = 0
        
        if start is not None or end is not None:
            if start is None:
                start = 0
            if end is None:
                end = len(self.data) - 1
            
            # Handle negative indices
            if start < 0:
                start = max(0, len(self.data) + start)
            if end < 0:
                end = max(-1, len(self.data) + end)
            
            if start > end or start >= len(self.data):
                return -1
            
            end = min(end, len(self.data) - 1)
            data_range = self.data[start:end + 1]
            byte_start = start
        
        # Search for bit
        for byte_idx, byte in enumerate(data_range):
            for bit_idx in range(8):
                current_bit = (byte >> (7 - bit_idx)) & 1
                if current_bit == bit_value:
                    return (byte_start + byte_idx) * 8 + bit_idx
        
        return -1
    
    def get_bytes(self):
        """Get bitmap as bytes"""
        return bytes(self.data)
    
    def get_string(self):
        """Get bitmap as string"""
        try:
            return self.data.decode('utf-8')
        except UnicodeDecodeError:
            return str(self.data)
    
    def __len__(self):
        """Return number of bytes"""
        return len(self.data)
    
    def bit_length(self):
        """Return number of bits (including trailing zeros)"""
        return len(self.data) * 8