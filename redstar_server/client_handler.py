import socket
from redstar_core.redstar_protocol import RedStarParsor


class RedstarClientHandler:
    """
    Handle individual client connections
    Each client gets its own handler running in a separate thread
    """
    
    def __init__(self, client_socket, client_address, command_processor):
        self.socket = client_socket
        self.address = client_address
        self.command_processor = command_processor
        self.buffer = bytearray()  # Buffer for incoming data
        self.running = True
    
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
                    result = self.command_processor.execute_command(command)
                    
                    # Send response back to client
                    response = RedStarParsor.encode(result)
                    self.socket.send(response)
            
            except Exception as e:
                # Send error response
                error_response = RedStarParsor.encode(Exception(f"Protocol error: {str(e)}"))
                self.socket.send(error_response)
                break
    
    def close(self):
        """Close the client connection"""
        self.running = False
        try:
            self.socket.close()
        except:
            pass