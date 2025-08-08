import hashlib
import math
from core_datastructures.dynamic_array import DArray


class HyperLogLog:
    """
    Redis-compatible HyperLogLog implementation
    Probabilistic data structure for counting unique elements
    Uses 16384 buckets (2^14) for ~1.625% accuracy
    """
    
    def __init__(self, precision=14):
        self.precision = precision
        self.num_buckets = 2 ** precision
        self.buckets = [0] * self.num_buckets
        
        # Alpha constant for bias correction
        if self.num_buckets == 16:
            self.alpha = 0.673
        elif self.num_buckets == 32:
            self.alpha = 0.697
        elif self.num_buckets == 64:
            self.alpha = 0.709
        else:
            self.alpha = 0.7213 / (1 + 1.079 / self.num_buckets)
    
    def _hash(self, value):
        """Hash a value to get bucket and leading zeros"""
        if isinstance(value, str):
            data = value.encode('utf-8')
        elif isinstance(value, bytes):
            data = value
        else:
            data = str(value).encode('utf-8')
        
        # Use SHA-1 for consistent hashing
        hash_obj = hashlib.sha1(data)
        hash_bytes = hash_obj.digest()
        
        # Convert first 8 bytes to integer
        hash_int = int.from_bytes(hash_bytes[:8], byteorder='big')
        
        # Get bucket index from first `precision` bits
        bucket = hash_int >> (64 - self.precision)
        
        # Get remaining bits for leading zero count
        remaining_bits = hash_int & ((1 << (64 - self.precision)) - 1)
        
        # Count leading zeros in remaining bits + 1
        if remaining_bits == 0:
            leading_zeros = 64 - self.precision + 1
        else:
            leading_zeros = self._count_leading_zeros(remaining_bits, 64 - self.precision) + 1
        
        return bucket, min(leading_zeros, 50)  # Cap at 50 to prevent overflow
    
    def _count_leading_zeros(self, value, bit_width):
        """Count leading zeros in a value"""
        if value == 0:
            return bit_width
        
        count = 0
        mask = 1 << (bit_width - 1)
        
        while count < bit_width and (value & mask) == 0:
            count += 1
            mask >>= 1
        
        return count
    
    def add(self, element):
        """Add an element to the HyperLogLog"""
        bucket, leading_zeros = self._hash(element)
        
        # Update bucket with maximum leading zeros seen
        if leading_zeros > self.buckets[bucket]:
            self.buckets[bucket] = leading_zeros
            return True
        return False
    
    def count(self):
        """Estimate the number of unique elements"""
        # Calculate raw estimate
        raw_estimate = self.alpha * (self.num_buckets ** 2) / sum(2 ** (-bucket) for bucket in self.buckets)
        
        # Apply bias correction for small estimates
        if raw_estimate <= 2.5 * self.num_buckets:
            # Small range correction
            zeros = self.buckets.count(0)
            if zeros != 0:
                return self.num_buckets * math.log(self.num_buckets / zeros)
        
        if raw_estimate <= (1.0/30.0) * (2 ** 32):
            # No correction needed in intermediate range
            return raw_estimate
        else:
            # Large range correction
            return -2 ** 32 * math.log(1 - raw_estimate / (2 ** 32))
        
        return raw_estimate
    
    def merge(self, other_hll):
        """
        Merge another HyperLogLog into this one
        Returns a new HyperLogLog with merged data
        """
        if not isinstance(other_hll, HyperLogLog):
            raise TypeError("Can only merge with another HyperLogLog")
        
        if other_hll.num_buckets != self.num_buckets:
            raise ValueError("Cannot merge HyperLogLogs with different precision")
        
        # Create new HLL with merged buckets
        result = HyperLogLog(self.precision)
        for i in range(self.num_buckets):
            result.buckets[i] = max(self.buckets[i], other_hll.buckets[i])
        
        return result
    
    def get_buckets(self):
        """Get copy of internal buckets for serialization"""
        return list(self.buckets)
    
    def set_buckets(self, bucket_data):
        """Set internal buckets from serialized data"""
        if len(bucket_data) != self.num_buckets:
            raise ValueError(f"Expected {self.num_buckets} buckets, got {len(bucket_data)}")
        
        self.buckets = list(bucket_data)
    
    def reset(self):
        """Reset all buckets to zero"""
        self.buckets = [0] * self.num_buckets
    
    def __len__(self):
        """Return estimated count"""
        return int(self.count())
    
    def size(self):
        """Return estimated count"""
        return int(self.count())