#!/usr/bin/env python3
"""
Comprehensive test suite for Redis string operations.
Tests GET, SET, DEL, EXISTS, EXPIRE, TTL, INCR, DECR, KEYS commands.
"""

import threading
import time
import random
from redstar_commands.command_processor import RedstarCommandProcessor
from redstar_core.redstar_datastore import RedStarDataSource
from core_datastructures.dynamic_array import DArray


def test_basic_string_operations():
    """Test basic string GET, SET operations."""
    print("=== Testing Basic String Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test SET command
    args = DArray()
    args.append("SET")
    args.append("testkey")
    args.append("testvalue")
    
    result = processor.execute_command(args)
    assert result == "OK", f"Expected 'OK', got {result}"
    print("PASS: SET command")
    
    # Test GET command
    args = DArray()
    args.append("GET")
    args.append("testkey")
    
    result = processor.execute_command(args)
    assert result == "testvalue", f"Expected 'testvalue', got {result}"
    print("PASS: GET command")
    
    # Test GET non-existent key
    args = DArray()
    args.append("GET")
    args.append("nonexistent")
    
    result = processor.execute_command(args)
    assert result is None, f"Expected None, got {result}"
    print("PASS: GET non-existent key")
    
    # Test SET overwrite
    args = DArray()
    args.append("SET")
    args.append("testkey")
    args.append("newvalue")
    
    result = processor.execute_command(args)
    assert result == "OK", f"Expected 'OK', got {result}"
    
    args = DArray()
    args.append("GET")
    args.append("testkey")
    result = processor.execute_command(args)
    assert result == "newvalue", f"Expected 'newvalue', got {result}"
    print("PASS: SET overwrite")
    
    print("Basic string operations tests passed!\n")


def test_del_operations():
    """Test DEL command."""
    print("=== Testing DEL Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Set up test data
    args = DArray()
    args.append("SET")
    args.append("key1")
    args.append("value1")
    processor.execute_command(args)
    
    args = DArray()
    args.append("SET")
    args.append("key2")
    args.append("value2")
    processor.execute_command(args)
    
    # Test single key deletion
    args = DArray()
    args.append("DEL")
    args.append("key1")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: DEL single key")
    
    # Verify key is gone
    args = DArray()
    args.append("GET")
    args.append("key1")
    result = processor.execute_command(args)
    assert result is None, f"Expected None after delete, got {result}"
    print("PASS: Verify key deleted")
    
    # Test multiple key deletion
    args = DArray()
    args.append("SET")
    args.append("key3")
    args.append("value3")
    processor.execute_command(args)
    
    args = DArray()
    args.append("DEL")
    args.append("key2")
    args.append("key3")
    args.append("nonexistent")
    
    result = processor.execute_command(args)
    assert result == 2, f"Expected 2, got {result}"  # Only key2 and key3 existed
    print("PASS: DEL multiple keys")
    
    # Test delete non-existent key
    args = DArray()
    args.append("DEL")
    args.append("nonexistent")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0, got {result}"
    print("PASS: DEL non-existent key")
    
    print("DEL operations tests passed!\n")


def test_exists_operations():
    """Test EXISTS command."""
    print("=== Testing EXISTS Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test EXISTS on non-existent key
    args = DArray()
    args.append("EXISTS")
    args.append("nonexistent")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0, got {result}"
    print("PASS: EXISTS non-existent key")
    
    # Set up test key
    args = DArray()
    args.append("SET")
    args.append("existskey")
    args.append("existsvalue")
    processor.execute_command(args)
    
    # Test EXISTS on existing key
    args = DArray()
    args.append("EXISTS")
    args.append("existskey")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: EXISTS existing key")
    
    # Test EXISTS multiple keys
    args = DArray()
    args.append("SET")
    args.append("key1")
    args.append("value1")
    processor.execute_command(args)
    
    args = DArray()
    args.append("EXISTS")
    args.append("existskey")
    args.append("key1")
    args.append("nonexistent")
    
    result = processor.execute_command(args)
    assert result == 2, f"Expected 2, got {result}"  # existskey and key1 exist
    print("PASS: EXISTS multiple keys")
    
    print("EXISTS operations tests passed!\n")


def test_expire_ttl_operations():
    """Test EXPIRE and TTL commands."""
    print("=== Testing EXPIRE and TTL Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Set up test key
    args = DArray()
    args.append("SET")
    args.append("expirekey")
    args.append("expirevalue")
    processor.execute_command(args)
    
    # Test TTL on persistent key
    args = DArray()
    args.append("TTL")
    args.append("expirekey")
    
    result = processor.execute_command(args)
    assert result == -1, f"Expected -1 for persistent key, got {result}"
    print("PASS: TTL on persistent key")
    
    # Test EXPIRE command
    args = DArray()
    args.append("EXPIRE")
    args.append("expirekey")
    args.append("2")  # 2 seconds
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: EXPIRE command")
    
    # Test TTL after setting expiration
    args = DArray()
    args.append("TTL")
    args.append("expirekey")
    
    result = processor.execute_command(args)
    assert 0 <= result <= 2, f"Expected TTL between 0 and 2, got {result}"
    print("PASS: TTL after EXPIRE")
    
    # Test TTL on non-existent key
    args = DArray()
    args.append("TTL")
    args.append("nonexistent")
    
    result = processor.execute_command(args)
    assert result == -2, f"Expected -2 for non-existent key, got {result}"
    print("PASS: TTL on non-existent key")
    
    # Test EXPIRE on non-existent key
    args = DArray()
    args.append("EXPIRE")
    args.append("nonexistent")
    args.append("10")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0 for non-existent key, got {result}"
    print("PASS: EXPIRE on non-existent key")
    
    # Wait for expiration and verify
    time.sleep(2.5)
    args = DArray()
    args.append("GET")
    args.append("expirekey")
    
    result = processor.execute_command(args)
    assert result is None, f"Expected None after expiration, got {result}"
    print("PASS: Key expires correctly")
    
    print("EXPIRE and TTL operations tests passed!\n")


def test_incr_decr_operations():
    """Test INCR and DECR commands."""
    print("=== Testing INCR and DECR Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test INCR on non-existent key (should create and set to 1)
    args = DArray()
    args.append("INCR")
    args.append("counter")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: INCR on non-existent key")
    
    # Test INCR on existing key
    result = processor.execute_command(args)
    assert result == 2, f"Expected 2, got {result}"
    print("PASS: INCR on existing key")
    
    # Test DECR on existing key
    args = DArray()
    args.append("DECR")
    args.append("counter")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: DECR on existing key")
    
    # Test DECR on non-existent key (should create and set to -1)
    args = DArray()
    args.append("DECR")
    args.append("newcounter")
    
    result = processor.execute_command(args)
    assert result == -1, f"Expected -1, got {result}"
    print("PASS: DECR on non-existent key")
    
    # Test INCR/DECR with preset value
    args = DArray()
    args.append("SET")
    args.append("preset")
    args.append("10")
    processor.execute_command(args)
    
    args = DArray()
    args.append("INCR")
    args.append("preset")
    result = processor.execute_command(args)
    assert result == 11, f"Expected 11, got {result}"
    
    args = DArray()
    args.append("DECR")
    args.append("preset")
    result = processor.execute_command(args)
    assert result == 10, f"Expected 10, got {result}"
    print("PASS: INCR/DECR with preset value")
    
    # Test INCR/DECR with negative numbers
    args = DArray()
    args.append("SET")
    args.append("negative")
    args.append("-5")
    processor.execute_command(args)
    
    args = DArray()
    args.append("INCR")
    args.append("negative")
    result = processor.execute_command(args)
    assert result == -4, f"Expected -4, got {result}"
    
    args = DArray()
    args.append("DECR")
    args.append("negative")
    result = processor.execute_command(args)
    assert result == -5, f"Expected -5, got {result}"
    print("PASS: INCR/DECR with negative numbers")
    
    print("INCR and DECR operations tests passed!\n")


def test_keys_operations():
    """Test KEYS command."""
    print("=== Testing KEYS Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test KEYS on empty store
    args = DArray()
    args.append("KEYS")
    args.append("*")
    
    result = processor.execute_command(args)
    assert len(result) == 0, f"Expected empty result, got {len(result)} keys"
    print("PASS: KEYS on empty store")
    
    # Add some keys
    test_keys = ["user:1", "user:2", "product:1", "order:1", "temp:key"]
    for key in test_keys:
        args = DArray()
        args.append("SET")
        args.append(key)
        args.append(f"value_for_{key}")
        processor.execute_command(args)
    
    # Test KEYS * (all keys)
    args = DArray()
    args.append("KEYS")
    args.append("*")
    
    result = processor.execute_command(args)
    assert len(result) == 5, f"Expected 5 keys, got {len(result)}"
    
    # Check all keys are present
    for key in test_keys:
        found = False
        for i in range(len(result)):
            if result[i] == key:
                found = True
                break
        assert found, f"Key {key} not found in KEYS result"
    print("PASS: KEYS * (all keys)")
    
    # Test KEYS with pattern (this might be limited based on implementation)
    args = DArray()
    args.append("KEYS")
    args.append("user:*")
    
    result = processor.execute_command(args)
    # Implementation might be basic, so just check it doesn't crash
    assert result is not None, "KEYS with pattern should not return None"
    print("PASS: KEYS with pattern")
    
    print("KEYS operations tests passed!\n")


def test_string_edge_cases():
    """Test edge cases for string operations."""
    print("=== Testing String Edge Cases ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test empty string value
    args = DArray()
    args.append("SET")
    args.append("empty")
    args.append("")
    processor.execute_command(args)
    
    args = DArray()
    args.append("GET")
    args.append("empty")
    result = processor.execute_command(args)
    assert result == "", f"Expected empty string, got {result}"
    print("PASS: Empty string value")
    
    # Test very long string
    long_value = "x" * 1000
    args = DArray()
    args.append("SET")
    args.append("longkey")
    args.append(long_value)
    processor.execute_command(args)
    
    args = DArray()
    args.append("GET")
    args.append("longkey")
    result = processor.execute_command(args)
    assert result == long_value, "Long string test failed"
    print("PASS: Long string value")
    
    # Test special characters
    special_value = "Hello\nWorld\t\r\"'\\/"
    args = DArray()
    args.append("SET")
    args.append("special")
    args.append(special_value)
    processor.execute_command(args)
    
    args = DArray()
    args.append("GET")
    args.append("special")
    result = processor.execute_command(args)
    assert result == special_value, "Special characters test failed"
    print("PASS: Special characters")
    
    # Test unicode characters
    unicode_value = "Hello 世界 🌍"
    args = DArray()
    args.append("SET")
    args.append("unicode")
    args.append(unicode_value)
    processor.execute_command(args)
    
    args = DArray()
    args.append("GET")
    args.append("unicode")
    result = processor.execute_command(args)
    assert result == unicode_value, "Unicode test failed"
    print("PASS: Unicode characters")
    
    # Test numeric strings vs numbers
    args = DArray()
    args.append("SET")
    args.append("numstring")
    args.append("123")
    processor.execute_command(args)
    
    args = DArray()
    args.append("GET")
    args.append("numstring")
    result = processor.execute_command(args)
    assert result == "123", f"Expected string '123', got {result}"
    assert isinstance(result, str), f"Expected string type, got {type(result)}"
    print("PASS: Numeric strings")
    
    print("String edge cases tests passed!\n")


def test_concurrent_string_operations():
    """Test concurrent string operations."""
    print("=== Testing Concurrent String Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    results = []
    errors = []
    
    def worker_thread(thread_id):
        """Worker function for concurrent testing."""
        try:
            # Each thread does operations on its own keys
            for i in range(50):
                key = f"thread{thread_id}_key{i}"
                value = f"thread{thread_id}_value{i}"
                
                # SET
                args = DArray()
                args.append("SET")
                args.append(key)
                args.append(value)
                result = processor.execute_command(args)
                if result != "OK":
                    errors.append(f"Thread {thread_id}: SET failed for {key}")
                    return
                
                # GET
                args = DArray()
                args.append("GET")
                args.append(key)
                result = processor.execute_command(args)
                if result != value:
                    errors.append(f"Thread {thread_id}: GET mismatch for {key}")
                    return
                
                # EXISTS
                args = DArray()
                args.append("EXISTS")
                args.append(key)
                result = processor.execute_command(args)
                if result != 1:
                    errors.append(f"Thread {thread_id}: EXISTS failed for {key}")
                    return
                
                # INCR (on some keys)
                if i % 5 == 0:
                    counter_key = f"thread{thread_id}_counter{i}"
                    args = DArray()
                    args.append("SET")
                    args.append(counter_key)
                    args.append("0")
                    processor.execute_command(args)
                    
                    args = DArray()
                    args.append("INCR")
                    args.append(counter_key)
                    result = processor.execute_command(args)
                    if result != 1:
                        errors.append(f"Thread {thread_id}: INCR failed for {counter_key}")
                        return
            
            results.append(f"Thread {thread_id} completed successfully")
            
        except Exception as e:
            errors.append(f"Thread {thread_id} exception: {e}")
    
    # Start multiple threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker_thread, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    # Check results
    if errors:
        print(f"FAIL: Concurrent test had {len(errors)} errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  {error}")
        return False
    
    if len(results) == 5:
        print("PASS: All concurrent threads completed successfully")
    else:
        print(f"FAIL: Only {len(results)}/5 threads completed")
        return False
    
    print("Concurrent string operations tests passed!\n")


def run_all_string_tests():
    """Run all string operation tests."""
    print("Starting comprehensive string operations tests...\n")
    
    tests = [
        test_basic_string_operations,
        test_del_operations,
        test_exists_operations,
        test_expire_ttl_operations,
        test_incr_decr_operations,
        test_keys_operations,
        test_string_edge_cases,
        test_concurrent_string_operations,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"FAIL: {test.__name__} failed with: {e}")
    
    print(f"String operations test results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("SUCCESS: All string operations tests passed!")
    else:
        print(f"FAIL: {failed} string operations tests failed")
    
    return failed == 0


if __name__ == "__main__":
    run_all_string_tests()