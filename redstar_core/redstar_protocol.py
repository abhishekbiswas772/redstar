import re
from core_datastructures.dynamic_array import DArray


class RedStarParsor:

    @staticmethod
    def encode(data):
        if data is None:
            return b"$-1\r\n"
        
        elif isinstance(data, str):
            encoded = data.encode('utf-8')
            return f"${len(encoded)}\r\n".encode() + encoded + b"\r\n"
        
        elif isinstance(data, bytes):
            return f"${len(data)}\r\n".encode() + data + b"\r\n"
        
        elif isinstance(data, bool):  # Check bool BEFORE int
            return f":{1 if data else 0}\r\n".encode()
        
        elif isinstance(data, int):
            return f":{data}\r\n".encode()
        
        elif isinstance(data, DArray) or isinstance(data, list):
            result = f"*{len(data)}\r\n".encode()
            for item in data:
                result += RedStarParsor.encode(item)
            return result
        
        elif isinstance(data, Exception):
            return f"-{str(data)}\r\n".encode()
        
        else:
            # Simple string for other types
            return f"+{str(data)}\r\n".encode()
    
    @staticmethod
    def decode(buffer, offset=0):
        if offset >= len(buffer):
            return None, 0
        
        type_byte = chr(buffer[offset])
        
        if type_byte == '+':
            return RedStarParsor._decode_simple_string(buffer, offset)
        
        elif type_byte == '-':
            return RedStarParsor._decode_error(buffer, offset)
        
        elif type_byte == ':': 
            return RedStarParsor._decode_integer(buffer, offset)
        
        elif type_byte == '$':  
            return RedStarParsor._decode_bulk_string(buffer, offset)
        
        elif type_byte == '*': 
            return RedStarParsor._decode_array(buffer, offset)
        
        else:
            raise ValueError(f"Unknown RESP type: {type_byte}")
    
    @staticmethod
    def _find_crlf(buffer, start):
        for i in range(start, len(buffer) - 1):
            if buffer[i] == ord('\r') and buffer[i + 1] == ord('\n'):
                return i
        return -1
    
    @staticmethod
    def _decode_simple_string(buffer, offset):
        crlf_pos = RedStarParsor._find_crlf(buffer, offset)
        if crlf_pos == -1:
            return None, 0 
        
        data = buffer[offset + 1:crlf_pos].decode('utf-8')
        return data, crlf_pos - offset + 2
    
    @staticmethod
    def _decode_error(buffer, offset):
        crlf_pos = RedStarParsor._find_crlf(buffer, offset)
        if crlf_pos == -1:
            return None, 0
        
        error_msg = buffer[offset + 1:crlf_pos].decode('utf-8')
        return Exception(error_msg), crlf_pos - offset + 2
    
    @staticmethod
    def _decode_integer(buffer, offset):
        crlf_pos = RedStarParsor._find_crlf(buffer, offset)
        if crlf_pos == -1:
            return None, 0
        
        int_str = buffer[offset + 1:crlf_pos].decode('utf-8')
        return int(int_str), crlf_pos - offset + 2
    
    @staticmethod
    def _decode_bulk_string(buffer, offset):
        crlf_pos = RedStarParsor._find_crlf(buffer, offset)
        if crlf_pos == -1:
            return None, 0
        
        length_str = buffer[offset + 1:crlf_pos].decode('utf-8')
        length = int(length_str)
        
        if length == -1:
            return None, crlf_pos - offset + 2  
        
        data_start = crlf_pos + 2
        if len(buffer) < data_start + length + 2:
            return None, 0  # Need more data
        
        data = buffer[data_start:data_start + length].decode('utf-8')
        return data, data_start - offset + length + 2
    
    @staticmethod
    def _decode_array(buffer, offset):
        crlf_pos = RedStarParsor._find_crlf(buffer, offset)
        if crlf_pos == -1:
            return None, 0
        
        count_str = buffer[offset + 1:crlf_pos].decode('utf-8')
        count = int(count_str)
        
        if count == -1:
            return None, crlf_pos - offset + 2  # Null array
        
        # Decode each element
        result = DArray()
        pos = crlf_pos + 2
        total_consumed = pos - offset
        
        for _ in range(count):
            element, consumed = RedStarParsor.decode(buffer, pos)
            if consumed == 0:
                return None, 0  # Need more data
            
            result.append(element)
            pos += consumed
            total_consumed += consumed
        
        return result, total_consumed