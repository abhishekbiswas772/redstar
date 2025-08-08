#!/usr/bin/env python3
"""
Comprehensive test suite for hash operations
Tests HSET, HGET, HDEL, HGETALL, HKEYS, HVALS operations
"""

import socket
import time
import sys

class RedstarHashTester:
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
            # Send command
            self.socket.send(command.encode('utf-8'))
            
            # Receive response
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
    
    def test_basic_hash_operations(self):
        """Test basic hash set/get operations"""
        print("\n=== Testing Basic Hash Operations ===")
        
        # HSET - Set single field
        response = self.send_command("*4\r\n$4\r\nHSET\r\n$4\r\nuser\r\n$4\r\nname\r\n$5\r\nAlice\r\n")
        self.test_assert(":1" in response, "HSET new field", ":1", response)
        
        # HSET - Update existing field
        response = self.send_command("*4\r\n$4\r\nHSET\r\n$4\r\nuser\r\n$4\r\nname\r\n$3\r\nBob\r\n")
        self.test_assert(":0" in response, "HSET existing field", ":0", response)
        
        # HGET - Get existing field
        response = self.send_command("*3\r\n$4\r\nHGET\r\n$4\r\nuser\r\n$4\r\nname\r\n")
        self.test_assert("$3\r\nBob" in response, "HGET existing field", "Bob", response)
        
        # HGET - Get non-existent field
        response = self.send_command("*3\r\n$4\r\nHGET\r\n$4\r\nuser\r\n$3\r\nage\r\n")
        self.test_assert("$-1" in response, "HGET non-existent field", "nil", response)
        
        # HGET - Get from non-existent hash
        response = self.send_command("*3\r\n$4\r\nHGET\r\n$8\r\nnoexist\r\n$4\r\nname\r\n")
        self.test_assert("$-1" in response, "HGET from non-existent hash", "nil", response)
    
    def test_multiple_hash_fields(self):
        """Test operations with multiple hash fields"""
        print("\n=== Testing Multiple Hash Fields ===")
        
        # Set multiple fields
        self.send_command("*6\r\n$4\r\nHSET\r\n$7\r\nprofile\r\n$4\r\nname\r\n$4\r\nJohn\r\n$3\r\nage\r\n$2\r\n25\r\n")
        self.send_command("*4\r\n$4\r\nHSET\r\n$7\r\nprofile\r\n$5\r\nemail\r\n$15\r\njohn@example.com\r\n")
        
        # HGETALL - Get all fields and values
        response = self.send_command("*2\r\n$7\r\nHGETALL\r\n$7\r\nprofile\r\n")
        self.test_assert("name" in response and "John" in response and "age" in response and "25" in response and "email" in response, 
                        "HGETALL with multiple fields")
        
        # HKEYS - Get all field names
        response = self.send_command("*2\r\n$5\r\nHKEYS\r\n$7\r\nprofile\r\n")
        self.test_assert("name" in response and "age" in response and "email" in response, 
                        "HKEYS returns all field names")
        
        # HVALS - Get all values
        response = self.send_command("*2\r\n$5\r\nHVALS\r\n$7\r\nprofile\r\n")
        self.test_assert("John" in response and "25" in response and "john@example.com" in response, 
                        "HVALS returns all values")
    
    def test_hash_deletion(self):
        """Test hash field deletion operations"""
        print("\n=== Testing Hash Deletion ===")
        
        # Setup test data
        self.send_command("*6\r\n$4\r\nHSET\r\n$8\r\ntestdel\r\n$2\r\nf1\r\n$2\r\nv1\r\n$2\r\nf2\r\n$2\r\nv2\r\n")
        self.send_command("*4\r\n$4\r\nHSET\r\n$8\r\ntestdel\r\n$2\r\nf3\r\n$2\r\nv3\r\n")
        
        # HDEL - Delete existing field
        response = self.send_command("*3\r\n$4\r\nHDEL\r\n$8\r\ntestdel\r\n$2\r\nf1\r\n")
        self.test_assert(":1" in response, "HDEL existing field", ":1", response)
        
        # Verify field was deleted
        response = self.send_command("*3\r\n$4\r\nHGET\r\n$8\r\ntestdel\r\n$2\r\nf1\r\n")
        self.test_assert("$-1" in response, "Verify field deleted")
        
        # HDEL - Delete non-existent field
        response = self.send_command("*3\r\n$4\r\nHDEL\r\n$8\r\ntestdel\r\n$8\r\nnotexist\r\n")
        self.test_assert(":0" in response, "HDEL non-existent field", ":0", response)
        
        # HDEL - Multiple fields at once
        response = self.send_command("*4\r\n$4\r\nHDEL\r\n$8\r\ntestdel\r\n$2\r\nf2\r\n$2\r\nf3\r\n")
        self.test_assert(":2" in response, "HDEL multiple fields", ":2", response)
    
    def test_hash_edge_cases(self):
        """Test hash edge cases and error conditions"""
        print("\n=== Testing Hash Edge Cases ===")
        
        # Empty field name
        response = self.send_command("*4\r\n$4\r\nHSET\r\n$5\r\nedge1\r\n$0\r\n\r\n$5\r\nvalue\r\n")
        self.test_assert(":1" in response, "HSET with empty field name")
        
        # Empty value
        response = self.send_command("*4\r\n$4\r\nHSET\r\n$5\r\nedge2\r\n$5\r\nfield\r\n$0\r\n\r\n")
        self.test_assert(":1" in response, "HSET with empty value")
        
        # Very long field name and value
        long_field = "x" * 1000
        long_value = "y" * 1000
        response = self.send_command(f"*4\r\n$4\r\nHSET\r\n$5\r\nedge3\r\n${len(long_field)}\r\n{long_field}\r\n${len(long_value)}\r\n{long_value}\r\n")
        self.test_assert(":1" in response, "HSET with very long field/value")
        
        # Operations on non-existent hash
        response = self.send_command("*2\r\n$7\r\nHGETALL\r\n$8\r\nnotexist\r\n")
        self.test_assert("*0" in response, "HGETALL on non-existent hash")
        
        response = self.send_command("*2\r\n$5\r\nHKEYS\r\n$8\r\nnotexist\r\n")
        self.test_assert("*0" in response, "HKEYS on non-existent hash")
        
        response = self.send_command("*2\r\n$5\r\nHVALS\r\n$8\r\nnotexist\r\n")
        self.test_assert("*0" in response, "HVALS on non-existent hash")
    
    def test_hash_type_conflicts(self):
        """Test hash operations on non-hash types"""
        print("\n=== Testing Hash Type Conflicts ===")
        
        # Set a string value
        self.send_command("*3\r\n$3\r\nSET\r\n$6\r\nstring\r\n$5\r\nvalue\r\n")
        
        # Try hash operations on string
        response = self.send_command("*4\r\n$4\r\nHSET\r\n$6\r\nstring\r\n$5\r\nfield\r\n$5\r\nvalue\r\n")
        self.test_assert("-ERR" in response or "-WRONGTYPE" in response, "HSET on string type")
        
        response = self.send_command("*3\r\n$4\r\nHGET\r\n$6\r\nstring\r\n$5\r\nfield\r\n")
        self.test_assert("-ERR" in response or "-WRONGTYPE" in response, "HGET on string type")
    
    def cleanup(self):
        """Clean up test data"""
        print("\n=== Cleaning Up ===")
        self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
    
    def run_all_tests(self):
        """Run all hash operation tests"""
        print("🔍 Starting Hash Operations Test Suite")
        print("=" * 50)
        
        if not self.connect():
            return False
        
        try:
            self.test_basic_hash_operations()
            self.test_multiple_hash_fields()
            self.test_hash_deletion()
            self.test_hash_edge_cases()
            self.test_hash_type_conflicts()
            self.cleanup()
            
        finally:
            self.disconnect()
        
        # Print results
        total_tests = self.tests_passed + self.tests_failed
        print(f"\n📊 Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {self.tests_passed}")
        print(f"   ❌ Failed: {self.tests_failed}")
        print(f"   Success Rate: {(self.tests_passed/total_tests*100):.1f}%")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = RedstarHashTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)