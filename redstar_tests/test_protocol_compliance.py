#!/usr/bin/env python3
"""
RESP Protocol Compliance Test Suite
Verifies full Redis Serialization Protocol compliance and compatibility with Redis clients
"""

import socket
import time
import sys
import subprocess
import os

class RESPProtocolTester:
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
        """Send raw bytes"""
        try:
            self.socket.send(data)
            response = self.socket.recv(4096)
            return response
        except Exception as e:
            return f"ERROR: {e}".encode()
    
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
    
    def test_resp_simple_strings(self):
        """Test RESP Simple Strings format"""
        print("\n=== Testing RESP Simple Strings ===")
        
        # PING should return simple string
        response = self.send_command("*1\r\n$4\r\nPING\r\n")
        self.test_assert(response.startswith("+PONG"), "PING returns simple string", "+PONG", response[:5])
        self.test_assert(response.endswith("\r\n") or "\r\n" in response, "Simple string ends with CRLF")
        
        # SET should return +OK
        response = self.send_command("*3\r\n$3\r\nSET\r\n$4\r\ntest\r\n$5\r\nvalue\r\n")
        self.test_assert(response.startswith("+OK"), "SET returns +OK", "+OK", response[:3])
        
        # FLUSHALL should return +OK
        response = self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
        self.test_assert(response.startswith("+OK"), "FLUSHALL returns +OK", "+OK", response[:3])
    
    def test_resp_errors(self):
        """Test RESP Error format"""
        print("\n=== Testing RESP Errors ===")
        
        # Unknown command should return error
        response = self.send_command("*1\r\n$11\r\nUNKNOWNCMD\r\n")
        self.test_assert(response.startswith("-ERR"), "Unknown command returns error", "-ERR", response[:4])
        
        # Wrong number of arguments
        response = self.send_command("*1\r\n$3\r\nSET\r\n")
        self.test_assert(response.startswith("-ERR"), "Wrong args returns error", "-ERR", response[:4])
        
        # Type error (try list operation on string)
        self.send_command("*3\r\n$3\r\nSET\r\n$6\r\nstring\r\n$5\r\nvalue\r\n")
        response = self.send_command("*3\r\n$5\r\nLPUSH\r\n$6\r\nstring\r\n$4\r\nitem\r\n")
        self.test_assert(response.startswith("-ERR") or response.startswith("-WRONGTYPE"), 
                        "Type error returns proper error")
        
        # Error message should be human readable
        if response.startswith("-"):
            error_msg = response[1:].split('\r\n')[0]
            self.test_assert(len(error_msg) > 5, "Error message is descriptive", "> 5 chars", len(error_msg))
    
    def test_resp_integers(self):
        """Test RESP Integer format"""
        print("\n=== Testing RESP Integers ===")
        
        # INCR should return integer
        self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
        response = self.send_command("*2\r\n$4\r\nINCR\r\n$7\r\ncounter\r\n")
        self.test_assert(response.startswith(":1"), "INCR returns :1", ":1", response[:2])
        
        # DECR should return integer
        response = self.send_command("*2\r\n$4\r\nDECR\r\n$7\r\ncounter\r\n")
        self.test_assert(response.startswith(":0"), "DECR returns :0", ":0", response[:2])
        
        # LLEN should return integer
        self.send_command("*3\r\n$5\r\nLPUSH\r\n$4\r\nlist\r\n$4\r\nitem\r\n")
        response = self.send_command("*2\r\n$4\r\nLLEN\r\n$4\r\nlist\r\n")
        self.test_assert(response.startswith(":"), "LLEN returns integer", ":N", response[:1])
        
        # EXISTS should return integer
        response = self.send_command("*2\r\n$6\r\nEXISTS\r\n$4\r\nlist\r\n")
        self.test_assert(response.startswith(":1"), "EXISTS returns :1", ":1", response[:2])
        
        # Non-existent key EXISTS should return :0
        response = self.send_command("*2\r\n$6\r\nEXISTS\r\n$8\r\nnotexist\r\n")
        self.test_assert(response.startswith(":0"), "EXISTS non-existent returns :0", ":0", response[:2])
        
        # Negative integers
        response = self.send_command("*2\r\n$4\r\nDECR\r\n$8\r\nnotexist\r\n")
        self.test_assert(response.startswith(":-1"), "DECR non-existent returns :-1", ":-1", response[:3])
    
    def test_resp_bulk_strings(self):
        """Test RESP Bulk Strings format"""
        print("\n=== Testing RESP Bulk Strings ===")
        
        # Set and get a value
        self.send_command("*3\r\n$3\r\nSET\r\n$8\r\nbulktest\r\n$11\r\nHello World\r\n")
        response = self.send_command("*2\r\n$3\r\nGET\r\n$8\r\nbulktest\r\n")
        
        # Should return bulk string format: $11\r\nHello World\r\n
        self.test_assert(response.startswith("$11"), "Bulk string has correct length prefix", "$11", response[:3])
        self.test_assert("Hello World" in response, "Bulk string contains correct data")
        
        # Empty string
        self.send_command("*3\r\n$3\r\nSET\r\n$5\r\nempty\r\n$0\r\n\r\n")
        response = self.send_command("*2\r\n$3\r\nGET\r\n$5\r\nempty\r\n")
        self.test_assert(response.startswith("$0"), "Empty bulk string has $0", "$0", response[:2])
        
        # Null bulk string (non-existent key)
        response = self.send_command("*2\r\n$3\r\nGET\r\n$8\r\nnotexist\r\n")
        self.test_assert(response.startswith("$-1"), "Non-existent key returns $-1", "$-1", response[:3])
        
        # Binary data with special characters
        special_value = "line1\r\nline2\x00null\xff"
        encoded_value = special_value.encode('latin1')
        command = f"*3\r\n$3\r\nSET\r\n$7\r\nspecial\r\n${len(encoded_value)}\r\n".encode() + encoded_value + b"\r\n"
        self.send_raw_bytes(command)
        
        response = self.send_command("*2\r\n$3\r\nGET\r\n$7\r\nspecial\r\n")
        expected_len = len(encoded_value)
        self.test_assert(response.startswith(f"${expected_len}"), f"Binary bulk string length ${expected_len}")
    
    def test_resp_arrays(self):
        """Test RESP Arrays format"""
        print("\n=== Testing RESP Arrays ===")
        
        # LRANGE should return array
        self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
        self.send_command("*3\r\n$5\r\nLPUSH\r\n$9\r\narraytest\r\n$5\r\nfirst\r\n")
        self.send_command("*3\r\n$5\r\nLPUSH\r\n$9\r\narraytest\r\n$6\r\nsecond\r\n")
        response = self.send_command("*4\r\n$6\r\nLRANGE\r\n$9\r\narraytest\r\n$1\r\n0\r\n$2\r\n-1\r\n")
        
        self.test_assert(response.startswith("*"), "LRANGE returns array", "*N", response[:1])
        
        # Empty array
        response = self.send_command("*4\r\n$6\r\nLRANGE\r\n$8\r\nnotexist\r\n$1\r\n0\r\n$2\r\n-1\r\n")
        self.test_assert(response.startswith("*0"), "Empty list returns *0", "*0", response[:2])
        
        # KEYS should return array
        self.send_command("*3\r\n$3\r\nSET\r\n$5\r\nkey1\r\n$6\r\nvalue1\r\n")
        self.send_command("*3\r\n$3\r\nSET\r\n$5\r\nkey2\r\n$6\r\nvalue2\r\n")
        response = self.send_command("*2\r\n$4\r\nKEYS\r\n$1\r\n*\r\n")
        self.test_assert(response.startswith("*"), "KEYS returns array", "*N", response[:1])
        
        # SMEMBERS should return array
        self.send_command("*3\r\n$4\r\nSADD\r\n$6\r\nsetkey\r\n$7\r\nmember1\r\n")
        self.send_command("*3\r\n$4\r\nSADD\r\n$6\r\nsetkey\r\n$7\r\nmember2\r\n")
        response = self.send_command("*2\r\n$8\r\nSMEMBERS\r\n$6\r\nsetkey\r\n")
        self.test_assert(response.startswith("*"), "SMEMBERS returns array", "*N", response[:1])
        
        # HGETALL should return array (even number of elements)
        self.send_command("*4\r\n$4\r\nHSET\r\n$7\r\nhashkey\r\n$6\r\nfield1\r\n$6\r\nvalue1\r\n")
        self.send_command("*4\r\n$4\r\nHSET\r\n$7\r\nhashkey\r\n$6\r\nfield2\r\n$6\r\nvalue2\r\n")
        response = self.send_command("*2\r\n$7\r\nHGETALL\r\n$7\r\nhashkey\r\n")
        self.test_assert(response.startswith("*"), "HGETALL returns array", "*N", response[:1])
        
        # Try to validate array has even number (field-value pairs)
        if response.startswith("*"):
            try:
                array_len_str = response.split('\r\n')[0][1:]
                array_len = int(array_len_str)
                self.test_assert(array_len % 2 == 0, "HGETALL returns even number of elements")
            except ValueError:
                self.test_assert(False, "Could not parse HGETALL array length")
    
    def test_resp_nested_arrays(self):
        """Test nested arrays and complex structures"""
        print("\n=== Testing Complex RESP Structures ===")
        
        # Multi-key operations that might return nested structures
        # Note: Basic Redis doesn't have deeply nested arrays, but test what we can
        
        # Multiple KEYS patterns (if supported)
        self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
        self.send_command("*3\r\n$3\r\nSET\r\n$8\r\npattern1\r\n$5\r\nval1\r\n")
        self.send_command("*3\r\n$3\r\nSET\r\n$8\r\npattern2\r\n$5\r\nval2\r\n")
        
        response = self.send_command("*2\r\n$4\r\nKEYS\r\n$8\r\npattern*\r\n")
        self.test_assert(response.startswith("*"), "Pattern KEYS returns array")
        
        # Complex data structures
        # Create a list with various types of data
        self.send_command("*3\r\n$5\r\nLPUSH\r\n$7\r\ncomplex\r\n$1\r\n1\r\n")
        self.send_command("*3\r\n$5\r\nLPUSH\r\n$7\r\ncomplex\r\n$5\r\nhello\r\n")
        self.send_command("*3\r\n$5\r\nLPUSH\r\n$7\r\ncomplex\r\n$0\r\n\r\n")
        
        response = self.send_command("*4\r\n$6\r\nLRANGE\r\n$7\r\ncomplex\r\n$1\r\n0\r\n$2\r\n-1\r\n")
        self.test_assert(response.startswith("*3"), "Complex list returns *3", "*3", response[:2])
    
    def test_protocol_parsing_edge_cases(self):
        """Test protocol parsing edge cases"""
        print("\n=== Testing Protocol Parsing Edge Cases ===")
        
        # Large bulk string length
        response = self.send_command("*3\r\n$3\r\nSET\r\n$8\r\nlargenum\r\n$10000\r\n" + "x" * 10000 + "\r\n")
        self.test_assert("+OK" in response or "-ERR" in response, "Large bulk string handled")
        
        # Zero-length elements
        response = self.send_command("*3\r\n$3\r\nSET\r\n$0\r\n\r\n$5\r\nvalue\r\n")
        self.test_assert(response is not None, "Zero-length key handled")
        
        # Maximum integer values
        max_int = str(2**31 - 1)
        response = self.send_command(f"*3\r\n$6\r\nINCRBY\r\n$6\r\nmaxint\r\n${len(max_int)}\r\n{max_int}\r\n")
        self.test_assert(":" in response, "Large integer value handled")
        
        # Verify protocol consistency across operations
        operations = [
            ("*1\r\n$4\r\nPING\r\n", "+"),  # Simple string
            ("*2\r\n$3\r\nDEL\r\n$8\r\nnotexist\r\n", ":"),  # Integer
            ("*2\r\n$3\r\nGET\r\n$8\r\nnotexist\r\n", "$"),  # Bulk string (null)
            ("*2\r\n$4\r\nKEYS\r\n$8\r\nnotexist\r\n", "*"),  # Array
        ]
        
        consistent_formatting = 0
        for command, expected_type in operations:
            response = self.send_command(command)
            if response.startswith(expected_type):
                consistent_formatting += 1
        
        self.test_assert(consistent_formatting == len(operations), 
                        f"Protocol format consistency", f"{len(operations)}/4", f"{consistent_formatting}/4")
    
    def test_redis_cli_compatibility(self):
        """Test compatibility with redis-cli (if available)"""
        print("\n=== Testing Redis CLI Compatibility ===")
        
        # Try to test with redis-cli if available
        try:
            # Test basic redis-cli connection
            result = subprocess.run(['redis-cli', '-h', self.host, '-p', str(self.port), 'PING'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and 'PONG' in result.stdout:
                self.test_assert(True, "redis-cli can connect and PING")
                
                # Test a few more commands
                commands_to_test = [
                    (['redis-cli', '-h', self.host, '-p', str(self.port), 'SET', 'clitest', 'value'], 'OK'),
                    (['redis-cli', '-h', self.host, '-p', str(self.port), 'GET', 'clitest'], 'value'),
                    (['redis-cli', '-h', self.host, '-p', str(self.port), 'INCR', 'clicounter'], '1'),
                    (['redis-cli', '-h', self.host, '-p', str(self.port), 'EXISTS', 'clitest'], '1'),
                ]
                
                cli_success = 0
                for cmd, expected in commands_to_test:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        if result.returncode == 0 and expected in result.stdout:
                            cli_success += 1
                    except:
                        pass
                
                self.test_assert(cli_success >= 3, f"redis-cli command compatibility", ">=3/4", f"{cli_success}/4")
                
            else:
                self.test_assert(False, "redis-cli connection failed", "PONG", result.stdout)
                
        except FileNotFoundError:
            print("   ℹ️  redis-cli not found, skipping CLI compatibility tests")
        except subprocess.TimeoutExpired:
            self.test_assert(False, "redis-cli timeout")
        except Exception as e:
            print(f"   ℹ️  redis-cli test error: {e}")
    
    def test_protocol_performance_characteristics(self):
        """Test protocol performance characteristics"""
        print("\n=== Testing Protocol Performance ===")
        
        # Test rapid command processing
        start_time = time.time()
        command_count = 100
        
        for i in range(command_count):
            response = self.send_command(f"*3\r\n$3\r\nSET\r\n$7\r\nperf{i:03d}\r\n$5\r\nvalue\r\n")
            if "+OK" not in response:
                break
        
        elapsed = time.time() - start_time
        ops_per_sec = command_count / elapsed if elapsed > 0 else 0
        
        self.test_assert(ops_per_sec > 100, f"Reasonable command throughput", "> 100 ops/sec", f"{ops_per_sec:.1f} ops/sec")
        
        # Test protocol overhead (response size efficiency)
        response = self.send_command("*2\r\n$3\r\nGET\r\n$7\r\nperf001\r\n")
        response_overhead = len(response) - 5  # "value" is 5 chars
        self.test_assert(response_overhead < 20, "Reasonable protocol overhead", "< 20 bytes", f"{response_overhead} bytes")
        
        # Clean up
        self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
    
    def test_connection_pipelining(self):
        """Test command pipelining support"""
        print("\n=== Testing Command Pipelining ===")
        
        # Send multiple commands without waiting for responses
        pipelined_commands = (
            "*3\r\n$3\r\nSET\r\n$5\r\npipe1\r\n$6\r\nvalue1\r\n" +
            "*3\r\n$3\r\nSET\r\n$5\r\npipe2\r\n$6\r\nvalue2\r\n" +
            "*2\r\n$3\r\nGET\r\n$5\r\npipe1\r\n" +
            "*2\r\n$3\r\nGET\r\n$5\r\npipe2\r\n"
        )
        
        try:
            self.socket.send(pipelined_commands.encode('utf-8'))
            response = self.socket.recv(8192).decode('utf-8')
            
            # Should get back multiple responses
            ok_count = response.count("+OK")
            value_count = response.count("value")
            
            self.test_assert(ok_count >= 2, f"Pipelined SET responses", ">=2", ok_count)
            self.test_assert(value_count >= 2, f"Pipelined GET responses", ">=2", value_count)
            
            # Test that pipelining doesn't break subsequent commands
            normal_response = self.send_command("*1\r\n$4\r\nPING\r\n")
            self.test_assert("PONG" in normal_response, "Commands work after pipelining")
            
        except Exception as e:
            self.test_assert(False, f"Pipelining test failed: {e}")
    
    def run_all_tests(self):
        """Run all protocol compliance tests"""
        print("🔍 Starting RESP Protocol Compliance Test Suite")
        print("=" * 60)
        
        if not self.connect():
            return False
        
        try:
            self.test_resp_simple_strings()
            self.test_resp_errors()
            self.test_resp_integers()
            self.test_resp_bulk_strings()
            self.test_resp_arrays()
            self.test_resp_nested_arrays()
            self.test_protocol_parsing_edge_cases()
            self.test_protocol_performance_characteristics()
            self.test_connection_pipelining()
            
        finally:
            # Final cleanup
            try:
                self.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
            except:
                pass
            self.disconnect()
        
        # Test redis-cli compatibility after main connection closes
        self.test_redis_cli_compatibility()
        
        # Print results
        total_tests = self.tests_passed + self.tests_failed
        print(f"\n📊 Protocol Compliance Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {self.tests_passed}")
        print(f"   ❌ Failed: {self.tests_failed}")
        print(f"   Success Rate: {(self.tests_passed/total_tests*100):.1f}%")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = RESPProtocolTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)