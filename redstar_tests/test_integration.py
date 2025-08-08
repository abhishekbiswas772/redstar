#!/usr/bin/env python3
"""
Comprehensive integration test suite for Redstar server.
Tests all Redis operations through client-server communication.
"""

import threading
import time
import subprocess
import socket
from redstar_client.redstar_client import RedstarClient


def is_port_open(host, port):
    """Check if a port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0


def start_server_background():
    """Start the server in the background."""
    try:
        # Start server process
        process = subprocess.Popen([
            "python", "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        for _ in range(10):  # Wait up to 10 seconds
            if is_port_open("127.0.0.1", 6379):
                print("PASS: Server started successfully")
                return process
            time.sleep(1)
        
        print("FAIL: Server failed to start in time")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"FAIL: Error starting server: {e}")
        return None


def test_server_connection():
    """Test basic server connection."""
    print("=== Testing Server Connection ===")
    
    client = RedstarClient()
    connected = client.connect()
    
    if not connected:
        print("FAIL: Could not connect to server")
        return False
    
    try:
        # Test PING command
        response = client.execute("PING")
        assert response == "PONG", f"Expected PONG, got {response}"
        print("PASS: PING command")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Connection test failed: {e}")
        return False
        
    finally:
        client.close()


def test_string_operations():
    """Test all string operations."""
    print("=== Testing String Operations ===")
    
    client = RedstarClient()
    if not client.connect():
        return False
    
    try:
        # Test SET and GET
        client.execute("SET", "testkey", "testvalue")
        result = client.execute("GET", "testkey")
        assert result == "testvalue", f"Expected 'testvalue', got {result}"
        print("PASS: SET and GET")
        
        # Test GET non-existent key
        result = client.execute("GET", "nonexistent")
        assert result is None, f"Expected None, got {result}"
        print("PASS: GET non-existent key")
        
        # Test EXISTS
        result = client.execute("EXISTS", "testkey")
        assert result == 1, f"Expected 1, got {result}"
        result = client.execute("EXISTS", "nonexistent")
        assert result == 0, f"Expected 0, got {result}"
        print("PASS: EXISTS")
        
        # Test DEL
        result = client.execute("DEL", "testkey")
        assert result == 1, f"Expected 1, got {result}"
        result = client.execute("EXISTS", "testkey")
        assert result == 0, f"Expected 0, got {result}"
        print("PASS: DEL")
        
        # Test EXPIRE and TTL
        client.execute("SET", "expkey", "expvalue")
        client.execute("EXPIRE", "expkey", "2")
        ttl = client.execute("TTL", "expkey")
        assert ttl > 0, f"Expected positive TTL, got {ttl}"
        print("PASS: EXPIRE and TTL")
        
        # Test INCR and DECR
        client.execute("SET", "counter", "10")
        result = client.execute("INCR", "counter")
        assert result == 11, f"Expected 11, got {result}"
        result = client.execute("DECR", "counter")
        assert result == 10, f"Expected 10, got {result}"
        print("PASS: INCR and DECR")
        
        return True
        
    except Exception as e:
        print(f"FAIL: String operations test failed: {e}")
        return False
        
    finally:
        client.close()


def test_list_operations():
    """Test all list operations."""
    print("=== Testing List Operations ===")
    
    client = RedstarClient()
    if not client.connect():
        return False
    
    try:
        # Test LPUSH and RPUSH
        client.execute("LPUSH", "mylist", "left1")
        client.execute("RPUSH", "mylist", "right1")
        client.execute("LPUSH", "mylist", "left2")
        
        # Test LLEN
        length = client.execute("LLEN", "mylist")
        assert length == 3, f"Expected 3, got {length}"
        print("PASS: LPUSH, RPUSH, LLEN")
        
        # Test LRANGE
        items = client.execute("LRANGE", "mylist", "0", "-1")
        expected = ["left2", "left1", "right1"]  # left2 was pushed last to left
        assert len(items) == 3, f"Expected 3 items, got {len(items)}"
        print("PASS: LRANGE")
        
        # Test LPOP and RPOP
        left_item = client.execute("LPOP", "mylist")
        right_item = client.execute("RPOP", "mylist")
        assert left_item == "left2", f"Expected 'left2', got {left_item}"
        assert right_item == "right1", f"Expected 'right1', got {right_item}"
        print("PASS: LPOP and RPOP")
        
        return True
        
    except Exception as e:
        print(f"FAIL: List operations test failed: {e}")
        return False
        
    finally:
        client.close()


def test_set_operations():
    """Test all set operations."""
    print("=== Testing Set Operations ===")
    
    client = RedstarClient()
    if not client.connect():
        return False
    
    try:
        # Test SADD
        result = client.execute("SADD", "myset", "member1")
        assert result == 1, f"Expected 1, got {result}"
        result = client.execute("SADD", "myset", "member2", "member3")
        assert result == 2, f"Expected 2, got {result}"
        
        # Test SCARD
        size = client.execute("SCARD", "myset")
        assert size == 3, f"Expected 3, got {size}"
        print("PASS: SADD and SCARD")
        
        # Test SISMEMBER
        result = client.execute("SISMEMBER", "myset", "member1")
        assert result == 1, f"Expected 1, got {result}"
        result = client.execute("SISMEMBER", "myset", "nonmember")
        assert result == 0, f"Expected 0, got {result}"
        print("PASS: SISMEMBER")
        
        # Test SMEMBERS
        members = client.execute("SMEMBERS", "myset")
        assert len(members) == 3, f"Expected 3 members, got {len(members)}"
        assert "member1" in members, "member1 not in result"
        print("PASS: SMEMBERS")
        
        # Test SREM
        result = client.execute("SREM", "myset", "member1")
        assert result == 1, f"Expected 1, got {result}"
        size = client.execute("SCARD", "myset")
        assert size == 2, f"Expected 2, got {size}"
        print("PASS: SREM")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Set operations test failed: {e}")
        return False
        
    finally:
        client.close()


def test_hash_operations():
    """Test all hash operations."""
    print("=== Testing Hash Operations ===")
    
    client = RedstarClient()
    if not client.connect():
        return False
    
    try:
        # Test HSET
        result = client.execute("HSET", "myhash", "field1", "value1")
        assert result == 1, f"Expected 1, got {result}"
        client.execute("HSET", "myhash", "field2", "value2", "field3", "value3")
        
        # Test HGET
        value = client.execute("HGET", "myhash", "field1")
        assert value == "value1", f"Expected 'value1', got {value}"
        print("PASS: HSET and HGET")
        
        # Test HGETALL
        all_fields = client.execute("HGETALL", "myhash")
        assert len(all_fields) >= 6, f"Expected at least 6 items, got {len(all_fields)}"  # field-value pairs
        print("PASS: HGETALL")
        
        # Test HKEYS and HVALS
        keys = client.execute("HKEYS", "myhash")
        vals = client.execute("HVALS", "myhash")
        assert len(keys) == 3, f"Expected 3 keys, got {len(keys)}"
        assert len(vals) == 3, f"Expected 3 values, got {len(vals)}"
        assert "field1" in keys, "field1 not in keys"
        assert "value1" in vals, "value1 not in values"
        print("PASS: HKEYS and HVALS")
        
        # Test HDEL
        result = client.execute("HDEL", "myhash", "field1")
        assert result == 1, f"Expected 1, got {result}"
        value = client.execute("HGET", "myhash", "field1")
        assert value is None, f"Expected None, got {value}"
        print("PASS: HDEL")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Hash operations test failed: {e}")
        return False
        
    finally:
        client.close()


def test_server_operations():
    """Test server operations."""
    print("=== Testing Server Operations ===")
    
    client = RedstarClient()
    if not client.connect():
        return False
    
    try:
        # Test PING
        result = client.execute("PING")
        assert result == "PONG", f"Expected PONG, got {result}"
        print("PASS: PING")
        
        # Test INFO
        info = client.execute("INFO")
        assert info is not None, "INFO returned None"
        print("PASS: INFO")
        
        # Add some data then test FLUSHALL
        client.execute("SET", "testkey", "testvalue")
        client.execute("SADD", "testset", "member")
        
        result = client.execute("FLUSHALL")
        assert result == "OK", f"Expected OK, got {result}"
        
        # Verify data is gone
        value = client.execute("GET", "testkey")
        assert value is None, f"Expected None after FLUSHALL, got {value}"
        print("PASS: FLUSHALL")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Server operations test failed: {e}")
        return False
        
    finally:
        client.close()


def test_concurrent_clients():
    """Test multiple concurrent clients."""
    print("=== Testing Concurrent Clients ===")
    
    results = []
    
    def client_worker(client_id):
        """Worker function for concurrent client testing."""
        try:
            client = RedstarClient()
            if not client.connect():
                results.append(f"Client {client_id}: Failed to connect")
                return
            
            # Each client does some operations
            for i in range(10):
                key = f"client{client_id}_key{i}"
                value = f"client{client_id}_value{i}"
                
                # Set value
                client.execute("SET", key, value)
                
                # Get value and verify
                retrieved = client.execute("GET", key)
                if retrieved != value:
                    results.append(f"Client {client_id}: Value mismatch for {key}")
                    return
                
                # Delete key
                client.execute("DEL", key)
            
            client.close()
            results.append(f"Client {client_id}: SUCCESS")
            
        except Exception as e:
            results.append(f"Client {client_id}: ERROR - {e}")
    
    # Start multiple client threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=client_worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    # Check results
    success_count = sum(1 for r in results if "SUCCESS" in r)
    if success_count == 5:
        print("PASS: All concurrent clients succeeded")
        return True
    else:
        print(f"FAIL: Only {success_count}/5 clients succeeded")
        for result in results:
            print(f"  {result}")
        return False


def test_edge_cases():
    """Test edge cases and error conditions."""
    print("=== Testing Edge Cases ===")
    
    client = RedstarClient()
    if not client.connect():
        return False
    
    try:
        # Test invalid commands
        try:
            client.execute("INVALIDCOMMAND")
            print("FAIL: Invalid command should have failed")
            return False
        except:
            print("PASS: Invalid command properly rejected")
        
        # Test type errors
        client.execute("SET", "stringkey", "stringvalue")
        try:
            client.execute("LPUSH", "stringkey", "item")  # Should fail
            print("FAIL: Type error should have occurred")
            return False
        except:
            print("PASS: Type error properly handled")
        
        # Test large values
        large_value = "x" * 1000
        client.execute("SET", "largekey", large_value)
        result = client.execute("GET", "largekey")
        assert result == large_value, "Large value test failed"
        print("PASS: Large value handling")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Edge cases test failed: {e}")
        return False
        
    finally:
        client.close()


def run_all_integration_tests():
    """Run all integration tests."""
    print("Starting comprehensive Redstar integration tests...\n")
    
    # Start server
    print("Starting Redstar server...")
    server_process = start_server_background()
    
    if not server_process:
        print("FAIL: Could not start server for testing")
        return False
    
    try:
        # Give server time to fully start
        time.sleep(2)
        
        # Run all tests
        tests = [
            test_server_connection,
            test_string_operations,
            test_list_operations,
            test_set_operations,
            test_hash_operations,
            test_server_operations,
            test_concurrent_clients,
            test_edge_cases,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                    print(f"{test.__name__} PASSED\n")
                else:
                    failed += 1
                    print(f"{test.__name__} FAILED\n")
            except Exception as e:
                failed += 1
                print(f"{test.__name__} FAILED with exception: {e}\n")
        
        print(f"Integration test results: {passed} PASSED, {failed} FAILED")
        
        if failed == 0:
            print("SUCCESS: All integration tests passed!")
            return True
        else:
            print(f"FAIL: {failed} integration tests failed")
            return False
        
    finally:
        # Stop server
        print("Stopping server...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            server_process.kill()


if __name__ == "__main__":
    run_all_integration_tests()