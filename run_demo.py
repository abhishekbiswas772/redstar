#!/usr/bin/env python3
"""
Quick Demo Runner
Starts the Redstar server and runs the demonstration
Perfect for one-command video demos
"""

import subprocess
import sys
import time
from datetime import datetime

class DemoRunner:
    def __init__(self):
        self.server_process = None
        self.server_ready = False
    
    def start_server(self):
        """Start the Redstar server in background"""
        try:
            print("Starting Redstar server...")
            self.server_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Wait for server to be ready
            start_time = time.time()
            while time.time() - start_time < 10:  # 10 second timeout
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', 6379))
                    sock.close()
                    
                    if result == 0:
                        self.server_ready = True
                        print("Redstar server is ready!")
                        return True
                except:
                    pass
                
                time.sleep(0.5)
            
            print("Server failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def run_demo(self):
        """Run the demo script"""
        try:
            print("\nRunning comprehensive demo...")
            result = subprocess.run(
                [sys.executable, 'redstar_demo.py'],
                timeout=300  # 5 minute timeout
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("Demo timed out")
            return False
        except Exception as e:
            print(f"Demo failed: {e}")
            return False
    
    def stop_server(self):
        """Stop the server gracefully"""
        if self.server_process:
            print("\nStopping Redstar server...")
            try:
                # Try graceful shutdown first
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.server_process.kill()
                self.server_process.wait()
            print("Server stopped")
    
    def run_complete_demo(self):
        """Run complete demo with server management"""
        print("REDSTAR COMPLETE DEMONSTRATION")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        success = False
        
        try:
            # Start server
            if not self.start_server():
                return False
            
            # Brief pause for server to fully initialize
            time.sleep(2)
            
            # Run demo
            success = self.run_demo()
            
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
            
        finally:
            # Always stop server
            self.stop_server()
        
        if success:
            print("\nCOMPLETE DEMO FINISHED SUCCESSFULLY!")
            print("Perfect for showcasing Redstar capabilities!")
        else:
            print("\nDemo completed with issues")
        
        return success

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Redstar Complete Demo Runner")
        print("")
        print("Usage: python run_demo.py")
        print("")
        print("This script will:")
        print("  1. Start the Redstar server automatically")
        print("  2. Run the comprehensive feature demonstration") 
        print("  3. Stop the server when complete")
        print("")
        return 0
    
    runner = DemoRunner()
    success = runner.run_complete_demo()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())