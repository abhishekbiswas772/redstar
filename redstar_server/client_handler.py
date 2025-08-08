import socket
import threading
import fnmatch
from redstar_core.redstar_protocol import RedStarParsor
from core_datastructures.dynamic_array import DArray


class RedstarClientHandler:
    """
    Handle individual client connections
    Each client gets its own handler running in a separate thread
    """
    
    def __init__(self, client_socket, client_address, command_processor, pubsub_manager=None):
        self.socket = client_socket
        self.address = client_address
        self.command_processor = command_processor
        self.pubsub_manager = pubsub_manager
        self.buffer = bytearray()  # Buffer for incoming data
        self.running = True
        self.pubsub_mode = False  # Track if client is in pub/sub mode
        self.send_lock = threading.Lock()  # Lock for sending responses
    
    def handle_client(self):
        """Main client handling loop"""
        print(f"Client connected from {self.address}")
        
        try:
            while self.running:
                # Receive data from client
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        break  # Client disconnected
                    
                    self.buffer.extend(data)
                    self._process_buffer()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error receiving data from {self.address}: {e}")
                    break
        
        finally:
            print(f"Client {self.address} disconnected")
            # Clean up pub/sub subscriptions
            if self.pubsub_manager:
                self.pubsub_manager.cleanup_client(self)
            self.socket.close()
    
    def _process_buffer(self):
        """Process commands in the buffer"""
        while True:
            # Try to parse a complete RESP command
            try:
                command, bytes_consumed = RedStarParsor.decode(bytes(self.buffer))
                
                if bytes_consumed == 0:
                    # Need more data
                    break
                
                # Remove processed bytes from buffer
                self.buffer = self.buffer[bytes_consumed:]
                
                if command is not None:
                    # Execute the command
                    result = self.command_processor.execute_command(command, self)
                    
                    # Handle pub/sub command responses
                    if self._is_pubsub_command(command[0].upper()):
                        # Pub/sub commands put client into pub/sub mode
                        if command[0].upper() in ['SUBSCRIBE', 'PSUBSCRIBE']:
                            self.pubsub_mode = True
                        
                        # Handle unsubscribe - exit pub/sub mode if no subscriptions left
                        elif command[0].upper() in ['UNSUBSCRIBE', 'PUNSUBSCRIBE']:
                            if self.pubsub_manager and not self.pubsub_manager.is_subscribed(self):
                                self.pubsub_mode = False
                    
                    # Send response back to client
                    if result is not None:
                        self._send_response(result)
            
            except Exception as e:
                # Send error response
                error_response = RedStarParsor.encode(Exception(f"Protocol error: {str(e)}"))
                self._send_raw(error_response)
                break
    
    def _is_pubsub_command(self, command):
        """Check if a command is a pub/sub command"""
        pubsub_commands = ['SUBSCRIBE', 'UNSUBSCRIBE', 'PSUBSCRIBE', 'PUNSUBSCRIBE', 'PUBLISH', 'PUBSUB']
        return command.upper() in pubsub_commands
    
    def _send_response(self, result):
        """Send a response to the client (thread-safe)"""
        if isinstance(result, DArray):
            # Handle multiple responses (like from SUBSCRIBE commands)
            for i in range(len(result)):
                response = RedStarParsor.encode(result[i])
                self._send_raw(response)
        else:
            # Single response
            response = RedStarParsor.encode(result)
            self._send_raw(response)
    
    def _send_raw(self, data):
        """Send raw data to client (thread-safe)"""
        with self.send_lock:
            if self.running:
                try:
                    self.socket.send(data)
                except Exception as e:
                    print(f"Error sending to client {self.address}: {e}")
                    self.running = False
    
    def send_pubsub_message(self, channel, message):
        """
        Send a pub/sub message to this client
        Called by the pub/sub manager when a message is published
        """
        if not self.running or not self.pubsub_mode:
            return
        
        # Determine if this is a pattern match or direct channel subscription
        pattern_matched = None
        if self.pubsub_manager:
            # Check if client has pattern subscriptions that match this channel
            if hasattr(self.pubsub_manager, 'client_patterns') and self in self.pubsub_manager.client_patterns:
                client_patterns = self.pubsub_manager.client_patterns[self]
                for pattern in client_patterns:
                    if fnmatch.fnmatch(channel, pattern):
                        pattern_matched = pattern
                        break
        
        # Create appropriate message response
        if pattern_matched:
            # Pattern-matched message: ["pmessage", pattern, channel, message]
            response = DArray()
            response.append("pmessage")
            response.append(pattern_matched)
            response.append(channel)
            response.append(message)
        else:
            # Regular message: ["message", channel, message]
            response = DArray()
            response.append("message")
            response.append(channel)
            response.append(message)
        
        # Send the message
        encoded_response = RedStarParsor.encode(response)
        self._send_raw(encoded_response)
    
    def close(self):
        """Close the client connection"""
        self.running = False
        # Clean up pub/sub subscriptions
        if self.pubsub_manager:
            self.pubsub_manager.cleanup_client(self)
        try:
            self.socket.close()
        except:
            pass