import socket
from core_datastructures.dynamic_array import DArray
from redstar_core.redstar_protocol import RedStarParsor


class RedstarClient:
    """
    A simple Redstar client for testing our server
    Also built from scratch!
    """
    
    def __init__(self, host='127.0.0.1', port=6379):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self):
        """Connect to Redstar server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to Redstar server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
        return True
    
    def execute(self, *args):
        """Execute Redstar command"""
        if not self.connected:
            raise Exception("Not connected to server")
        
        # Convert args to DArray
        command = DArray()
        for arg in args:
            command.append(str(arg))
        
        # Encode and send command
        request = RedStarParsor.encode(command)
        self.socket.send(request)
        
        # Receive and decode response
        response_data = self.socket.recv(4096)
        result, _ = RedStarParsor.decode(response_data)
        
        return result
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.connected = False