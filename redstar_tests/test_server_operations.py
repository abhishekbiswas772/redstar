#!/usr/bin/env python3
"""
Server operations test suite
Tests PING, INFO, FLUSHALL and server management commands
"""

import socket
import time
import sys

class ServerOperationsTester:
    def __init__(self, host='127.0.0.1', port=6379):
        self.host = host
        self.port = port
        self.socket = None
        self.tests_passed = 0
        self.tests_failed = 0
    
    def connect(self):
        """Connect to Redstar server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            self.socket.close()
    
    def send_command(self, command):
        """Send RESP command and receive response"""
        try:
            self.socket.send(command.encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            return response.strip()
        except Exception as e:
            return f"ERROR: {e}"
    
    def test_assert(self, condition, test_name, expected=None, actual=None):
        """Assert test condition and track results"""
        if condition:
            print(f"✅ {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ {test_name}")
            if expected is not None and actual is not None:
                print(f"   Expected: {expected}")
                print(f"   Actual: {actual}")
            self.tests_failed += 1
    
    def test_ping_command(self):
        """Test PING command variations"""
        print("\n=== Testing PING Command ===")
        
        # Basic PING
        response = self.send_command("*1\r\n$4\r\nPING\r\n")
        self.test_assert("+PONG" in response, "Basic PING command", "PONG", response)
        
        # PING with message
        response = self.send_command("*2\r\n$4\r\nPING\r\n$11\r\nHello World\r\n")
        self.test_assert("Hello World" in response, "PING with custom message", "Hello World", response)
        
        # PING with empty message
        response = self.send_command("*2\r\n$4\r\nPING\r\n$0\r\n\r\n")
        self.test_assert("$0" in response, "PING with empty message")
        
        # PING with special characters
        response = self.send_command("*2\r\n$4\r\nPING\r\n$13\r\n测试 emoji 🚀\r\n")
        self.test_assert("测试 emoji 🚀" in response or "$13" in response, "PING with special characters")
    
    def test_info_command(self):
        """Test INFO command"""
        print("\n=== Testing INFO Command ===")
        
        # Basic INFO
        response = self.send_command("*1\r\n$4\r\nINFO\r\n")
        self.test_assert("$" in response and len(response) > 10, "INFO command returns data", "non-empty", "data present" if len(response) > 10 else "empty")
        
        # Check for expected INFO fields
        info_sections = ["server", "memory", "stats", "keyspace"]
        found_sections = 0
        response_lower = response.lower()
        
        for section in info_sections:
            if section in response_lower:
                found_sections += 1
        
        self.test_assert(found_sections >= 1, f"INFO contains server information sections", f">= 1 section", f"{found_sections} sections found")
        
        # INFO should contain version info
        if "redstar" in response_lower or "redis" in response_lower or "version" in response_lower:
            self.test_assert(True, "INFO contains version information")
        else:
            self.test_assert(False, "INFO should contain version information")
    
    def test_flushall_command(self):
        """Test FLUSHALL command"""
        print("\n=== Testing FLUSHALL Command ===")
        
        # Set up some test data first
        test_data = [
            ("*3\r\n$3\r\nSET\r\n$4\r\nkey1\r\n$6\r\nvalue1\r\n", "String"),
            ("*3\r\n$5\r\nLPUSH\r\n$5\r\nlist1\r\n$4\r\nitem\r\n", "List"),
            ("*3\r\n$4\r\nSADD\r\n$4\r\nset1\r\n$7\r\nmember1\r\n", "Set"),
            ("*4\r\n$4\r\nHSET\r\n$5\r\nhash1\r\n$5\r\nfield\r\n$5\r\nvalue\r\n", "Hash"),
        ]
        
        # Create test data
        for command, data_type in test_data:
            response = self.send_command(command)
            # Just verify the command was accepted (don't check specific response)
        
        # Verify data exists
        response = self.send_command("*2\r\n$3\r\nGET\r\n$4\r\nkey1\r\n")
        data_exists_before = "$6\r\nvalue1" in response
        self.test_assert(data_exists_before, "Test data created before FLUSHALL")
        
        # Execute FLUSHALL
        response = self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
        self.test_assert("+OK" in response, "FLUSHALL command succeeds", "OK", response)
        
        # Verify data is gone
        test_checks = [
            ("*2\r\n$3\r\nGET\r\n$4\r\nkey1\r\n", "String key cleared"),
            ("*2\r\n$4\r\nLLEN\r\n$5\r\nlist1\r\n", "List cleared"),
            ("*2\r\n$5\r\nSCARD\r\n$4\r\nset1\r\n", "Set cleared"),
            ("*2\r\n$7\r\nHGETALL\r\n$5\r\nhash1\r\n", "Hash cleared"),
        ]
        
        for command, description in test_checks:
            response = self.send_command(command)
            # Data should be gone (nil response or 0 count)
            cleared = ("$-1" in response or ":0" in response or "*0" in response)
            self.test_assert(cleared, description)
    
    def test_keys_command(self):
        """Test KEYS command"""
        print("\n=== Testing KEYS Command ===")
        
        # Set up test keys
        test_keys = ["test1", "test2", "different", "test:key", "test_key"]
        for key in test_keys:
            self.send_command(f"*3\r\n$3\r\nSET\r\n${len(key)}\r\n{key}\r\n$5\r\nvalue\r\n")
        
        # KEYS * (all keys)
        response = self.send_command("*2\r\n$4\r\nKEYS\r\n$1\r\n*\r\n")
        all_keys_found = all(key in response for key in test_keys)
        self.test_assert(all_keys_found, "KEYS * returns all keys")
        
        # KEYS with pattern
        response = self.send_command("*2\r\n$4\r\nKEYS\r\n$5\r\ntest*\r\n")
        pattern_keys = ["test1", "test2", "test:key", "test_key"]
        pattern_match = all(key in response for key in pattern_keys) and "different" not in response
        self.test_assert(pattern_match, "KEYS test* pattern matching")
        
        # KEYS with no matches
        response = self.send_command("*2\r\n$4\r\nKEYS\r\n$8\r\nnomatch*\r\n")
        self.test_assert("*0" in response, "KEYS with no matching pattern")
        
        # Clean up
        self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
    
    def test_exists_command(self):
        """Test EXISTS command"""
        print("\n=== Testing EXISTS Command ===")
        
        # Test non-existent key
        response = self.send_command("*2\r\n$6\r\nEXISTS\r\n$8\r\nnoexist\r\n")
        self.test_assert(":0" in response, "EXISTS non-existent key", ":0", response)
        
        # Create key and test existence
        self.send_command("*3\r\n$3\r\nSET\r\n$7\r\nexistkey\r\n$5\r\nvalue\r\n")
        response = self.send_command("*2\r\n$6\r\nEXISTS\r\n$7\r\nexistkey\r\n")
        self.test_assert(":1" in response, "EXISTS existing key", ":1", response)
        
        # Test multiple keys
        self.send_command("*3\r\n$3\r\nSET\r\n$8\r\nexistkey2\r\n$5\r\nvalue\r\n")
        response = self.send_command("*4\r\n$6\r\nEXISTS\r\n$7\r\nexistkey\r\n$8\r\nexistkey2\r\n$8\r\nnoexist\r\n")
        self.test_assert(":2" in response, "EXISTS multiple keys (2 exist, 1 doesn't)", ":2", response)
        
        # Clean up
        self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
    
    def test_del_command(self):
        """Test DEL command"""
        print("\n=== Testing DEL Command ===")
        
        # Create test keys
        test_keys = ["delkey1", "delkey2", "delkey3"]
        for key in test_keys:
            self.send_command(f"*3\r\n$3\r\nSET\r\n${len(key)}\r\n{key}\r\n$5\r\nvalue\r\n")
        
        # Delete single key
        response = self.send_command("*2\r\n$3\r\nDEL\r\n$7\r\ndelkey1\r\n")
        self.test_assert(":1" in response, "DEL single existing key", ":1", response)
        
        # Verify key is gone
        response = self.send_command("*2\r\n$6\r\nEXISTS\r\n$7\r\ndelkey1\r\n")
        self.test_assert(":0" in response, "Verify key deleted")
        
        # Delete multiple keys
        response = self.send_command("*4\r\n$3\r\nDEL\r\n$7\r\ndelkey2\r\n$7\r\ndelkey3\r\n$8\r\nnoexist\r\n")
        self.test_assert(":2" in response, "DEL multiple keys", ":2", response)
        
        # Delete non-existent key
        response = self.send_command("*2\r\n$3\r\nDEL\r\n$8\r\nnoexist\r\n")
        self.test_assert(":0" in response, "DEL non-existent key", ":0", response)
    
    def test_expire_and_ttl(self):
        """Test EXPIRE and TTL commands"""
        print("\n=== Testing EXPIRE and TTL ===")
        
        # Set a key
        self.send_command("*3\r\n$3\r\nSET\r\n$9\r\nexpirekey\r\n$5\r\nvalue\r\n")
        
        # Set expiration
        response = self.send_command("*3\r\n$6\r\nEXPIRE\r\n$9\r\nexpirekey\r\n$2\r\n10\r\n")
        self.test_assert(":1" in response, "EXPIRE existing key", ":1", response)
        
        # Check TTL
        response = self.send_command("*2\r\n$3\r\nTTL\r\n$9\r\nexpirekey\r\n")
        ttl_value = None
        if ":" in response:
            try:
                ttl_value = int(response.split(":")[1])
                ttl_valid = 0 < ttl_value <= 10
                self.test_assert(ttl_valid, f"TTL returns valid time", "1-10 seconds", f"{ttl_value} seconds")
            except:
                self.test_assert(False, "TTL parsing failed")
        
        # Test EXPIRE on non-existent key
        response = self.send_command("*3\r\n$6\r\nEXPIRE\r\n$8\r\nnoexist\r\n$2\r\n10\r\n")
        self.test_assert(":0" in response, "EXPIRE non-existent key", ":0", response)
        
        # Test TTL on non-existent key
        response = self.send_command("*2\r\n$3\r\nTTL\r\n$8\r\nnoexist\r\n")
        self.test_assert(":-2" in response, "TTL non-existent key", ":-2", response)
        
        # Clean up
        self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
    
    def test_server_connection_handling(self):
        """Test server connection handling"""
        print("\n=== Testing Connection Handling ===")
        
        # Test multiple rapid connections
        connection_success = 0
        for i in range(5):
            try:
                temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                temp_socket.connect((self.host, self.port))
                temp_socket.send("*1\r\n$4\r\nPING\r\n".encode())
                response = temp_socket.recv(1024).decode()
                if "PONG" in response:
                    connection_success += 1
                temp_socket.close()
            except:
                pass
        
        self.test_assert(connection_success >= 4, f"Multiple connections handled", ">=4/5", f"{connection_success}/5")
        
        # Test graceful disconnection
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_socket.connect((self.host, self.port))
        temp_socket.send("*1\r\n$4\r\nPING\r\n".encode())
        response = temp_socket.recv(1024).decode()
        temp_socket.close()  # Abrupt close
        
        # Server should handle this gracefully and still accept new connections
        time.sleep(0.1)
        response = self.send_command("*1\r\n$4\r\nPING\r\n")
        self.test_assert("PONG" in response, "Server handles client disconnection gracefully")
    
    def run_all_tests(self):
        """Run all server operation tests"""
        print("🔍 Starting Server Operations Test Suite")
        print("=" * 50)
        
        if not self.connect():
            return False
        
        try:
            self.test_ping_command()
            self.test_info_command()
            self.test_flushall_command()
            self.test_keys_command()
            self.test_exists_command()
            self.test_del_command()
            self.test_expire_and_ttl()
            self.test_server_connection_handling()
            
        finally:
            # Final cleanup
            try:
                self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
            except:
                pass
            self.disconnect()
        
        # Print results
        total_tests = self.tests_passed + self.tests_failed
        print(f"\n📊 Server Operations Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {self.tests_passed}")
        print(f"   ❌ Failed: {self.tests_failed}")
        print(f"   Success Rate: {(self.tests_passed/total_tests*100):.1f}%")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = ServerOperationsTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)