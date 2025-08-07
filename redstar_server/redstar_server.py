import socket
import threading
import signal
from core_datastructures.dynamic_array import DArray
from redstar_core.redstar_datastore import RedStarDataSource
from redstar_commands.command_processor import RedstarCommandProcessor
from redstar_server.client_handler import RedstarClientHandler


class RedstarServer:
    """
    The main Redstar server
    Handles all networking, threading, and coordination
    """
    
    def __init__(self, host='127.0.0.1', port=6379, max_connections=1000):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        
        # Core components
        self.data_store = RedStarDataSource()
        self.command_processor = RedstarCommandProcessor(self.data_store)
        
        # Server state
        self.running = False
        self.server_socket = None
        self.client_threads = DArray()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down...")
        self.shutdown()
    
    def start(self):
        """Start the Redstar server"""
        try:
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind and listen
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            
            self.running = True
            
            print(f"🚀 Redstar Server (from scratch) started!")
            print(f"📡 Listening on {self.host}:{self.port}")
            print(f"🔌 Max connections: {self.max_connections}")
            print(f"⚡ All data structures implemented from scratch!")
            print(f"🛑 Press Ctrl+C to shutdown")
            print("-" * 50)
            
            # Main server loop
            while self.running:
                try:
                    # Accept new client connections
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Create client handler
                    client_handler = RedstarClientHandler(
                        client_socket, 
                        client_address, 
                        self.command_processor
                    )
                    
                    # Start client handler in new thread
                    client_thread = threading.Thread(
                        target=client_handler.handle_client,
                        daemon=True
                    )
                    client_thread.start()
                    
                    # Keep track of threads (for cleanup)
                    self.client_threads.append((client_handler, client_thread))
                    
                    # Clean up finished threads
                    self._cleanup_threads()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            
        finally:
            self.shutdown()
    
    def _cleanup_threads(self):
        """Remove finished client threads"""
        active_threads = DArray()
        
        for i in range(len(self.client_threads)):
            handler, thread = self.client_threads[i]
            if thread.is_alive():
                active_threads.append((handler, thread))
            else:
                handler.close()
        
        self.client_threads = active_threads
    
    def shutdown(self):
        """Gracefully shutdown the server"""
        if not self.running:
            return
        
        print("\n🛑 Shutting down Redstar server...")
        self.running = False
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        # Close all client connections
        for i in range(len(self.client_threads)):
            handler, thread = self.client_threads[i]
            handler.close()
        
        print("✅ Redstar server shutdown complete!")