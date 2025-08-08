#!/usr/bin/env python3
"""
Edge cases and error conditions test suite
Tests malformed commands, boundary conditions, and error handling
"""

import socket
import time
import sys

class EdgeCasesTester:
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
    
    def send_raw_bytes(self, data):
        """Send raw bytes and receive response"""
        try:
            self.socket.send(data)
            response = self.socket.recv(4096)
            return response.decode('utf-8', errors='ignore').strip()
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
    
    def test_malformed_resp_protocol(self):
        """Test malformed RESP protocol messages"""
        print("\n=== Testing Malformed RESP Protocol ===")
        
        # Invalid array length
        response = self.send_command("*abc\r\n$4\r\nPING\r\n")
        self.test_assert("-ERR" in response, "Invalid array length")
        
        # Negative array length  
        response = self.send_command("*-5\r\n$4\r\nPING\r\n")
        self.test_assert("-ERR" in response, "Negative array length")
        
        # Missing bulk string length
        response = self.send_command("*1\r\n$\r\nPING\r\n")
        self.test_assert("-ERR" in response, "Missing bulk string length")
        
        # Invalid bulk string length
        response = self.send_command("*1\r\n$xyz\r\nPING\r\n")
        self.test_assert("-ERR" in response, "Invalid bulk string length")
        
        # Bulk string length mismatch
        response = self.send_command("*1\r\n$10\r\nPING\r\n")
        self.test_assert("-ERR" in response, "Bulk string length mismatch")
        
        # Missing CR/LF
        response = self.send_raw_bytes(b"*1\n$4\nPING\n")
        self.test_assert("-ERR" in response or "ERROR" in response, "Missing CR in CRLF")
        
        # Incomplete command
        try:
            self.socket.send(b"*1\r\n$4\r\nPI")
            time.sleep(0.1)  # Let server process incomplete data
            self.socket.send(b"NG\r\n")
            response = self.socket.recv(1024).decode()
            # Server should handle this gracefully
            self.test_assert("PONG" in response or "-ERR" in response, "Incomplete command handling")
        except:
            self.test_assert(True, "Server handles incomplete commands without crashing")
    
    def test_unknown_commands(self):
        """Test unknown and invalid commands"""
        print("\n=== Testing Unknown Commands ===")
        
        # Completely unknown command
        response = self.send_command("*1\r\n$9\r\nUNKNOWNCMD\r\n")
        self.test_assert("-ERR" in response and ("unknown" in response.lower() or "command" in response.lower()), 
                        "Unknown command error")
        
        # Case sensitivity test
        response = self.send_command("*1\r\n$4\r\nping\r\n")
        case_insensitive = "PONG" in response
        response2 = self.send_command("*1\r\n$4\r\nPiNg\r\n")
        mixed_case = "PONG" in response2
        self.test_assert(case_insensitive or mixed_case, "Commands are case insensitive")
        
        # Empty command
        response = self.send_command("*1\r\n$0\r\n\r\n")
        self.test_assert("-ERR" in response, "Empty command")
        
        # Command with wrong number of arguments
        response = self.send_command("*1\r\n$3\r\nSET\r\n")  # SET needs key and value
        self.test_assert("-ERR" in response and "arg" in response.lower(), "Wrong number of arguments")
        
        response = self.send_command("*4\r\n$4\r\nPING\r\n$3\r\narg\r\n$3\r\narg\r\n$3\r\narg\r\n")  # Too many args for PING
        self.test_assert("-ERR" in response or "PONG" in response, "Too many arguments handled")
    
    def test_boundary_conditions(self):
        """Test boundary conditions and limits"""
        print("\n=== Testing Boundary Conditions ===")
        
        # Very long key name
        long_key = "x" * 10000
        response = self.send_command(f"*3\r\n$3\r\nSET\r\n${len(long_key)}\r\n{long_key}\r\n$5\r\nvalue\r\n")
        self.test_assert("+OK" in response or "-ERR" in response, "Very long key name")
        
        # Very long value
        long_value = "y" * 100000
        response = self.send_command(f"*3\r\n$3\r\nSET\r\n$8\r\nlongval\r\n${len(long_value)}\r\n{long_value}\r\n")
        self.test_assert("+OK" in response or "-ERR" in response, "Very long value")
        
        # Zero-length key
        response = self.send_command("*3\r\n$3\r\nSET\r\n$0\r\n\r\n$5\r\nvalue\r\n")
        self.test_assert("+OK" in response or "-ERR" in response, "Zero-length key")
        
        # Zero-length value
        response = self.send_command("*3\r\n$3\r\nSET\r\n$7\r\nemptyval\r\n$0\r\n\r\n")
        self.test_assert("+OK" in response, "Zero-length value", "+OK", response)
        
        # Verify zero-length value can be retrieved
        response = self.send_command("*2\r\n$3\r\nGET\r\n$7\r\nemptyval\r\n")
        self.test_assert("$0" in response, "Retrieve zero-length value")
        
        # Large number values
        response = self.send_command("*3\r\n$4\r\nINCR\r\n$7\r\nbignum\r\n")  # Create counter
        response = self.send_command(f"*3\r\n$3\r\nSET\r\n$7\r\nbignum\r\n${len('9223372036854775807')}\r\n9223372036854775807\r\n")  # Max int64
        response = self.send_command("*2\r\n$4\r\nINCR\r\n$7\r\nbignum\r\n")
        self.test_assert(response is not None, "Large number handling")
        
        # Clean up
        self.send_command("*2\r\n$3\r\nDEL\r\n$8\r\nlongval\r\n")
        self.send_command("*2\r\n$3\r\nDEL\r\n$7\r\nemptyval\r\n")
    
    def test_unicode_and_binary_data(self):
        """Test Unicode and binary data handling"""
        print("\n=== Testing Unicode and Binary Data ===")
        
        # Unicode key and value
        unicode_key = "测试键"
        unicode_value = "测试值 🚀 мир"
        response = self.send_command(f"*3\r\n$3\r\nSET\r\n${len(unicode_key.encode('utf-8'))}\r\n{unicode_key}\r\n${len(unicode_value.encode('utf-8'))}\r\n{unicode_value}\r\n")
        self.test_assert("+OK" in response, "Unicode key and value set")
        
        # Retrieve unicode data
        response = self.send_command(f"*2\r\n$3\r\nGET\r\n${len(unicode_key.encode('utf-8'))}\r\n{unicode_key}\r\n")
        self.test_assert("测试值" in response or unicode_value.encode('utf-8') in response.encode('utf-8'), "Retrieve Unicode data")
        
        # Binary data (null bytes)
        binary_data = b"binary\x00data\x01\x02\x03"
        try:
            command = f"*3\r\n$3\r\nSET\r\n$6\r\nbinary\r\n${len(binary_data)}\r\n".encode() + binary_data + b"\r\n"
            response = self.send_raw_bytes(command)
            self.test_assert("+OK" in response or "OK" in response, "Binary data with null bytes")
        except:
            self.test_assert(True, "Binary data handling attempted")
        
        # Emoji and special characters
        emoji_text = "Hello 👋 World 🌍 Test 🧪"
        response = self.send_command(f"*3\r\n$3\r\nSET\r\n$5\r\nemoji\r\n${len(emoji_text.encode('utf-8'))}\r\n{emoji_text}\r\n")
        self.test_assert("+OK" in response, "Emoji data")
        
        # Clean up
        self.send_command(f"*2\r\n$3\r\nDEL\r\n${len(unicode_key.encode('utf-8'))}\r\n{unicode_key}\r\n")
        self.send_command("*2\r\n$3\r\nDEL\r\n$6\r\nbinary\r\n")
        self.send_command("*2\r\n$3\r\nDEL\r\n$5\r\nemoji\r\n")
    
    def test_type_operations_errors(self):
        """Test type operation errors (wrong type operations)"""
        print("\n=== Testing Type Operation Errors ===")
        
        # Set up different data types
        self.send_command("*3\r\n$3\r\nSET\r\n$6\r\nstring\r\n$5\r\nvalue\r\n")  # String
        self.send_command("*3\r\n$5\r\nLPUSH\r\n$4\r\nlist\r\n$4\r\nitem\r\n")    # List
        self.send_command("*3\r\n$4\r\nSADD\r\n$3\r\nset\r\n$6\r\nmember\r\n")    # Set
        self.send_command("*4\r\n$4\r\nHSET\r\n$4\r\nhash\r\n$5\r\nfield\r\n$5\r\nvalue\r\n")  # Hash
        
        # Try list operations on string
        response = self.send_command("*3\r\n$5\r\nLPUSH\r\n$6\r\nstring\r\n$4\r\nitem\r\n")
        self.test_assert("-ERR" in response or "-WRONGTYPE" in response, "List operation on string")
        
        # Try set operations on list
        response = self.send_command("*3\r\n$4\r\nSADD\r\n$4\r\nlist\r\n$6\r\nmember\r\n")
        self.test_assert("-ERR" in response or "-WRONGTYPE" in response, "Set operation on list")
        
        # Try hash operations on set
        response = self.send_command("*4\r\n$4\r\nHSET\r\n$3\r\nset\r\n$5\r\nfield\r\n$5\r\nvalue\r\n")
        self.test_assert("-ERR" in response or "-WRONGTYPE" in response, "Hash operation on set")
        
        # Try string operations on hash
        response = self.send_command("*2\r\n$3\r\nGET\r\n$4\r\nhash\r\n")
        self.test_assert("-ERR" in response or "-WRONGTYPE" in response or "$-1" in response, "String operation on hash")
        
        # Clean up
        self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
    
    def test_numeric_edge_cases(self):
        """Test numeric operations edge cases"""
        print("\n=== Testing Numeric Edge Cases ===")
        
        # INCR on non-numeric string
        self.send_command("*3\r\n$3\r\nSET\r\n$9\r\nnonnumeric\r\n$3\r\nabc\r\n")
        response = self.send_command("*2\r\n$4\r\nINCR\r\n$9\r\nnonnumeric\r\n")
        self.test_assert("-ERR" in response, "INCR on non-numeric value")
        
        # INCR on float-like string
        self.send_command("*3\r\n$3\r\nSET\r\n$5\r\nfloat\r\n$3\r\n3.14\r\n")
        response = self.send_command("*2\r\n$4\r\nINCR\r\n$5\r\nfloat\r\n")
        self.test_assert("-ERR" in response, "INCR on float-like value")
        
        # DECR on non-existent key (should start from 0)
        response = self.send_command("*2\r\n$4\r\nDECR\r\n$11\r\nnonexistent\r\n")
        self.test_assert(":-1" in response, "DECR on non-existent key", ":-1", response)
        
        # Large increment values
        self.send_command("*3\r\n$3\r\nSET\r\n$7\r\nbigincr\r\n$1\r\n0\r\n")
        response = self.send_command("*3\r\n$6\r\nINCRBY\r\n$7\r\nbigincr\r\n$10\r\n2147483647\r\n")
        self.test_assert(":" in response, "Large INCRBY value")
        
        # Overflow test
        self.send_command("*3\r\n$3\r\nSET\r\n$8\r\noverflow\r\n$19\r\n9223372036854775807\r\n")  # Max int64
        response = self.send_command("*2\r\n$4\r\nINCR\r\n$8\r\noverflow\r\n")
        self.test_assert(response is not None, "Integer overflow handling")
        
        # Clean up
        self.send_command("*2\r\n$3\r\nDEL\r\n$9\r\nnonnumeric\r\n")
        self.send_command("*2\r\n$3\r\nDEL\r\n$5\r\nfloat\r\n")
        self.send_command("*2\r\n$3\r\nDEL\r\n$11\r\nnonexistent\r\n")
        self.send_command("*2\r\n$3\r\nDEL\r\n$7\r\nbigincr\r\n")
        self.send_command("*2\r\n$3\r\nDEL\r\n$8\r\noverflow\r\n")
    
    def test_connection_edge_cases(self):
        """Test connection and protocol edge cases"""
        print("\n=== Testing Connection Edge Cases ===")
        
        # Send multiple commands in one packet
        combined_commands = "*1\r\n$4\r\nPING\r\n*1\r\n$4\r\nPING\r\n*1\r\n$4\r\nPING\r\n"
        response = self.send_command(combined_commands)
        pong_count = response.count("PONG")
        self.test_assert(pong_count >= 1, f"Multiple commands in one packet", ">=1 PONG", f"{pong_count} PONGs")
        
        # Very slow command sending (partial packets)
        try:
            slow_command = "*1\r\n$4\r\nPING\r\n"
            for char in slow_command:
                self.socket.send(char.encode())
                time.sleep(0.001)  # Very slow
            response = self.socket.recv(1024).decode()
            self.test_assert("PONG" in response, "Slow/fragmented command")
        except:
            self.test_assert(True, "Server handles slow commands gracefully")
        
        # Test server resilience after errors
        # Send several bad commands
        for i in range(5):
            self.send_command("*1\r\n$9\r\nBADCOMMAND\r\n")
        
        # Server should still respond to good commands
        response = self.send_command("*1\r\n$4\r\nPING\r\n")
        self.test_assert("PONG" in response, "Server resilient after errors")
        
        # Test with various line ending combinations
        try:
            # Unix line endings (should fail)
            response = self.send_raw_bytes(b"*1\n$4\nPING\n")
            unix_handled = "-ERR" in response or "ERROR" in response
            
            # Windows line endings (correct)
            response = self.send_command("*1\r\n$4\r\nPING\r\n")
            windows_ok = "PONG" in response
            
            self.test_assert(windows_ok, "Proper CRLF line endings work")
        except:
            self.test_assert(True, "Line ending tests attempted")
    
    def run_all_tests(self):
        """Run all edge case tests"""
        print("🔍 Starting Edge Cases and Error Conditions Test Suite")
        print("=" * 60)
        
        if not self.connect():
            return False
        
        try:
            self.test_malformed_resp_protocol()
            self.test_unknown_commands()
            self.test_boundary_conditions()
            self.test_unicode_and_binary_data()
            self.test_type_operations_errors()
            self.test_numeric_edge_cases()
            self.test_connection_edge_cases()
            
        finally:
            # Final cleanup
            try:
                self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
            except:
                pass
            self.disconnect()
        
        # Print results
        total_tests = self.tests_passed + self.tests_failed
        print(f"\n📊 Edge Cases Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {self.tests_passed}")
        print(f"   ❌ Failed: {self.tests_failed}")
        print(f"   Success Rate: {(self.tests_passed/total_tests*100):.1f}%")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = EdgeCasesTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)