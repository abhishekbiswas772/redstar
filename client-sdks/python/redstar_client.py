#!/usr/bin/env python3
"""
Redstar Python Client SDK
A comprehensive Python client for connecting to Redstar Redis-compatible server
"""

import socket
import threading
import time
from typing import List, Dict, Any, Optional, Union

class RedstarException(Exception):
    """Base exception for Redstar client errors"""
    pass

class RedstarConnectionError(RedstarException):
    """Connection related errors"""
    pass

class RedstarCommandError(RedstarException):
    """Command execution errors"""
    pass

class RedstarClient:
    """
    Redstar Python Client SDK
    
    A comprehensive client for interacting with Redstar server with support for:
    - All basic Redis commands (strings, lists, sets, hashes)
    - Pub/Sub operations with callbacks
    - Connection management and reconnection
    - Thread-safe operations
    - Pipelining support
    """
    
    def __init__(self, host='localhost', port=6379, timeout=30, 
                 auto_reconnect=True, max_retries=3):
        """
        Initialize Redstar client
        
        Args:
            host (str): Server hostname
            port (int): Server port
            timeout (float): Socket timeout in seconds
            auto_reconnect (bool): Enable automatic reconnection
            max_retries (int): Maximum reconnection attempts
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.auto_reconnect = auto_reconnect
        self.max_retries = max_retries
        
        self.socket = None
        self.connected = False
        self.lock = threading.RLock()
        
        # Pub/Sub support
        self.pubsub_thread = None
        self.pubsub_callbacks = {}
        self.pattern_callbacks = {}
        self.is_subscribed = False
    
    def connect(self):
        """Connect to Redstar server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            raise RedstarConnectionError(f"Failed to connect to {self.host}:{self.port} - {e}")
    
    def disconnect(self):
        """Disconnect from server"""
        with self.lock:
            if self.pubsub_thread and self.pubsub_thread.is_alive():
                self.is_subscribed = False
                self.pubsub_thread.join(timeout=1)
            
            if self.socket:
                self.socket.close()
                self.socket = None
            self.connected = False
    
    def _ensure_connected(self):
        """Ensure client is connected, reconnect if needed"""
        if not self.connected:
            if self.auto_reconnect:
                for attempt in range(self.max_retries):
                    try:
                        self.connect()
                        return
                    except RedstarConnectionError:
                        if attempt == self.max_retries - 1:
                            raise
                        time.sleep(0.5 * (attempt + 1))
            else:
                raise RedstarConnectionError("Not connected to server")
    
    def _send_command(self, *args) -> str:
        """Send RESP command and return response"""
        with self.lock:
            self._ensure_connected()
            
            # Build RESP command
            command_parts = [str(arg) for arg in args]
            command = f"*{len(command_parts)}\r\n"
            
            for part in command_parts:
                part_bytes = str(part).encode('utf-8')
                command += f"${len(part_bytes)}\r\n{part.decode('utf-8') if isinstance(part_bytes, bytes) else part}\r\n"
            
            try:
                self.socket.send(command.encode('utf-8'))
                response = self.socket.recv(4096).decode('utf-8')
                return response.strip()
            except Exception as e:
                self.connected = False
                raise RedstarConnectionError(f"Command failed: {e}")
    
    def _parse_response(self, response: str) -> Any:
        """Parse RESP response"""
        if not response:
            return None
        
        if response.startswith('+'):
            return response[1:].split('\r\n')[0]
        elif response.startswith('-'):
            error_msg = response[1:].split('\r\n')[0]
            raise RedstarCommandError(error_msg)
        elif response.startswith(':'):
            return int(response[1:].split('\r\n')[0])
        elif response.startswith('$'):
            lines = response.split('\r\n')
            length = int(lines[0][1:])
            if length == -1:
                return None
            return lines[1] if len(lines) > 1 else ""
        elif response.startswith('*'):
            lines = response.split('\r\n')
            array_len = int(lines[0][1:])
            if array_len == 0:
                return []
            
            result = []
            line_idx = 1
            for _ in range(array_len):
                if line_idx < len(lines) and lines[line_idx].startswith('$'):
                    length = int(lines[line_idx][1:])
                    line_idx += 1
                    if line_idx < len(lines):
                        result.append(lines[line_idx])
                    line_idx += 1
                else:
                    line_idx += 1
            return result
        
        return response
    
    # String Operations
    def set(self, key: str, value: str) -> str:
        """Set a key-value pair"""
        response = self._send_command('SET', key, value)
        return self._parse_response(response)
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        response = self._send_command('GET', key)
        return self._parse_response(response)
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys"""
        response = self._send_command('DEL', *keys)
        return self._parse_response(response)
    
    def exists(self, *keys: str) -> int:
        """Check if keys exist"""
        response = self._send_command('EXISTS', *keys)
        return self._parse_response(response)
    
    def incr(self, key: str) -> int:
        """Increment integer value"""
        response = self._send_command('INCR', key)
        return self._parse_response(response)
    
    def decr(self, key: str) -> int:
        """Decrement integer value"""
        response = self._send_command('DECR', key)
        return self._parse_response(response)
    
    def expire(self, key: str, seconds: int) -> int:
        """Set key expiration"""
        response = self._send_command('EXPIRE', key, seconds)
        return self._parse_response(response)
    
    def ttl(self, key: str) -> int:
        """Get time to live"""
        response = self._send_command('TTL', key)
        return self._parse_response(response)
    
    # List Operations
    def lpush(self, key: str, *values: str) -> int:
        """Push values to left of list"""
        response = self._send_command('LPUSH', key, *values)
        return self._parse_response(response)
    
    def rpush(self, key: str, *values: str) -> int:
        """Push values to right of list"""
        response = self._send_command('RPUSH', key, *values)
        return self._parse_response(response)
    
    def lpop(self, key: str) -> Optional[str]:
        """Pop value from left of list"""
        response = self._send_command('LPOP', key)
        return self._parse_response(response)
    
    def rpop(self, key: str) -> Optional[str]:
        """Pop value from right of list"""
        response = self._send_command('RPOP', key)
        return self._parse_response(response)
    
    def llen(self, key: str) -> int:
        """Get list length"""
        response = self._send_command('LLEN', key)
        return self._parse_response(response)
    
    def lrange(self, key: str, start: int, stop: int) -> List[str]:
        """Get list elements in range"""
        response = self._send_command('LRANGE', key, start, stop)
        result = self._parse_response(response)
        return result if isinstance(result, list) else []
    
    # Set Operations
    def sadd(self, key: str, *members: str) -> int:
        """Add members to set"""
        response = self._send_command('SADD', key, *members)
        return self._parse_response(response)
    
    def srem(self, key: str, *members: str) -> int:
        """Remove members from set"""
        response = self._send_command('SREM', key, *members)
        return self._parse_response(response)
    
    def smembers(self, key: str) -> List[str]:
        """Get all set members"""
        response = self._send_command('SMEMBERS', key)
        result = self._parse_response(response)
        return result if isinstance(result, list) else []
    
    def scard(self, key: str) -> int:
        """Get set cardinality"""
        response = self._send_command('SCARD', key)
        return self._parse_response(response)
    
    def sismember(self, key: str, member: str) -> int:
        """Check if member is in set"""
        response = self._send_command('SISMEMBER', key, member)
        return self._parse_response(response)
    
    # Hash Operations
    def hset(self, key: str, field: str, value: str) -> int:
        """Set hash field"""
        response = self._send_command('HSET', key, field, value)
        return self._parse_response(response)
    
    def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field value"""
        response = self._send_command('HGET', key, field)
        return self._parse_response(response)
    
    def hdel(self, key: str, *fields: str) -> int:
        """Delete hash fields"""
        response = self._send_command('HDEL', key, *fields)
        return self._parse_response(response)
    
    def hgetall(self, key: str) -> Dict[str, str]:
        """Get all hash fields and values"""
        response = self._send_command('HGETALL', key)
        result = self._parse_response(response)
        
        if isinstance(result, list) and len(result) % 2 == 0:
            hash_dict = {}
            for i in range(0, len(result), 2):
                hash_dict[result[i]] = result[i + 1]
            return hash_dict
        return {}
    
    def hkeys(self, key: str) -> List[str]:
        """Get all hash field names"""
        response = self._send_command('HKEYS', key)
        result = self._parse_response(response)
        return result if isinstance(result, list) else []
    
    def hvals(self, key: str) -> List[str]:
        """Get all hash values"""
        response = self._send_command('HVALS', key)
        result = self._parse_response(response)
        return result if isinstance(result, list) else []
    
    # Server Operations
    def ping(self, message: str = None) -> str:
        """Ping server"""
        if message:
            response = self._send_command('PING', message)
        else:
            response = self._send_command('PING')
        return self._parse_response(response)
    
    def info(self) -> str:
        """Get server info"""
        response = self._send_command('INFO')
        return self._parse_response(response)
    
    def flushall(self) -> str:
        """Flush all data"""
        response = self._send_command('FLUSHALL')
        return self._parse_response(response)
    
    def keys(self, pattern: str = '*') -> List[str]:
        """Get keys matching pattern"""
        response = self._send_command('KEYS', pattern)
        result = self._parse_response(response)
        return result if isinstance(result, list) else []
    
    # Pub/Sub Operations
    def subscribe(self, channel: str, callback=None):
        """Subscribe to channel"""
        if not self.is_subscribed:
            self.is_subscribed = True
            self.pubsub_thread = threading.Thread(target=self._pubsub_listener)
            self.pubsub_thread.daemon = True
            self.pubsub_thread.start()
        
        self.pubsub_callbacks[channel] = callback
        response = self._send_command('SUBSCRIBE', channel)
        return self._parse_response(response)
    
    def psubscribe(self, pattern: str, callback=None):
        """Subscribe to pattern"""
        if not self.is_subscribed:
            self.is_subscribed = True
            self.pubsub_thread = threading.Thread(target=self._pubsub_listener)
            self.pubsub_thread.daemon = True
            self.pubsub_thread.start()
        
        self.pattern_callbacks[pattern] = callback
        response = self._send_command('PSUBSCRIBE', pattern)
        return self._parse_response(response)
    
    def unsubscribe(self, channel: str = None):
        """Unsubscribe from channel"""
        if channel:
            self.pubsub_callbacks.pop(channel, None)
            response = self._send_command('UNSUBSCRIBE', channel)
        else:
            self.pubsub_callbacks.clear()
            response = self._send_command('UNSUBSCRIBE')
        return self._parse_response(response)
    
    def punsubscribe(self, pattern: str = None):
        """Unsubscribe from pattern"""
        if pattern:
            self.pattern_callbacks.pop(pattern, None)
            response = self._send_command('PUNSUBSCRIBE', pattern)
        else:
            self.pattern_callbacks.clear()
            response = self._send_command('PUNSUBSCRIBE')
        return self._parse_response(response)
    
    def publish(self, channel: str, message: str) -> int:
        """Publish message to channel"""
        response = self._send_command('PUBLISH', channel, message)
        return self._parse_response(response)
    
    def _pubsub_listener(self):
        """Background thread for handling pub/sub messages"""
        while self.is_subscribed:
            try:
                if self.socket:
                    self.socket.settimeout(1.0)
                    data = self.socket.recv(4096).decode('utf-8')
                    if data:
                        # Parse pub/sub message and call callbacks
                        # This is a simplified implementation
                        lines = data.split('\r\n')
                        if len(lines) >= 6:
                            msg_type = lines[1]
                            channel = lines[3]
                            message = lines[5]
                            
                            if msg_type == 'message' and channel in self.pubsub_callbacks:
                                callback = self.pubsub_callbacks[channel]
                                if callback:
                                    callback(channel, message)
            except socket.timeout:
                continue
            except Exception:
                break
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Convenience functions for quick operations
def quick_set(key: str, value: str, host='localhost', port=6379) -> str:
    """Quick set operation"""
    with RedstarClient(host, port) as client:
        return client.set(key, value)

def quick_get(key: str, host='localhost', port=6379) -> Optional[str]:
    """Quick get operation"""
    with RedstarClient(host, port) as client:
        return client.get(key)

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    try:
        # Using context manager
        with RedstarClient() as client:
            # String operations
            print("Setting key...")
            client.set('hello', 'world')
            print(f"Getting key: {client.get('hello')}")
            
            # List operations
            print("List operations...")
            client.lpush('mylist', 'item1', 'item2')
            print(f"List length: {client.llen('mylist')}")
            print(f"List range: {client.lrange('mylist', 0, -1)}")
            
            # Hash operations
            print("Hash operations...")
            client.hset('user:1', 'name', 'Alice')
            client.hset('user:1', 'age', '30')
            print(f"Hash: {client.hgetall('user:1')}")
            
            # Server info
            print(f"Ping: {client.ping()}")
            print("Connection successful!")
            
    except Exception as e:
        print(f"Error: {e}")