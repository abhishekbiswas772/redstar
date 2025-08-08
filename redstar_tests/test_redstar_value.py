#!/usr/bin/env python3
"""
Comprehensive test suite for RedStarValue wrapper.
Tests value storage, type tracking, and expiration functionality.
"""

import time
from redstar_core.redstar_value import RedStarValue
from core_datastructures.dynamic_array import DArray
from core_datastructures.hashset import HashSet
from core_datastructures.hash_table import HashTable


def test_basic_value_creation():
    """Test basic RedStarValue creation and attribute access."""
    print("=== Testing Basic Value Creation ===")
    
    # Test string value without expiration
    str_val = RedStarValue("hello", "string")
    assert str_val.value == "hello"
    assert str_val.type == "string"
    assert str_val.expiry_time is None
    print("PASS: String value without expiration")
    
    # Test integer value without expiration
    int_val = RedStarValue(42, "int")
    assert int_val.value == 42
    assert int_val.type == "int"
    assert int_val.expiry_time is None
    print("PASS: Integer value without expiration")
    
    # Test with expiration time
    future_time = time.time() + 3600  # 1 hour from now
    val_with_exp = RedStarValue("data", "string", future_time)
    assert val_with_exp.value == "data"
    assert val_with_exp.type == "string"
    assert val_with_exp.expiry_time == future_time
    print("PASS: Value with expiration time")
    
    print("Basic value creation tests passed!\n")


def test_expiration_logic():
    """Test expiration functionality."""
    print("=== Testing Expiration Logic ===")
    
    # Test non-expiring value
    no_exp_val = RedStarValue("persistent", "string")
    assert not no_exp_val.is_expired()
    print("PASS: Non-expiring value")
    
    # Test future expiration
    future_time = time.time() + 10  # 10 seconds from now
    future_val = RedStarValue("future", "string", future_time)
    assert not future_val.is_expired()
    print("PASS: Future expiration (not expired)")
    
    # Test past expiration
    past_time = time.time() - 10  # 10 seconds ago
    past_val = RedStarValue("expired", "string", past_time)
    assert past_val.is_expired()
    print("PASS: Past expiration (expired)")
    
    # Test boundary condition - current time
    current_time = time.time()
    current_val = RedStarValue("boundary", "string", current_time)
    # This might be expired or not depending on precise timing
    # But the method should not crash
    is_exp = current_val.is_expired()
    assert isinstance(is_exp, bool)
    print("PASS: Boundary condition (current time)")
    
    # Test very small expiration window
    tiny_future = time.time() + 0.001  # 1ms from now
    tiny_val = RedStarValue("tiny", "string", tiny_future)
    time.sleep(0.002)  # Wait 2ms
    assert tiny_val.is_expired()
    print("PASS: Very small expiration window")
    
    print("Expiration logic tests passed!\n")


def test_different_value_types():
    """Test RedStarValue with different data types."""
    print("=== Testing Different Value Types ===")
    
    # Test string
    str_val = RedStarValue("hello world", "string")
    assert str_val.value == "hello world"
    assert str_val.type == "string"
    print("PASS: String type")
    
    # Test integer
    int_val = RedStarValue(-123, "int")
    assert int_val.value == -123
    assert int_val.type == "int"
    print("PASS: Integer type")
    
    # Test float
    float_val = RedStarValue(3.14159, "float")
    assert str_val.value == "hello world"
    assert float_val.type == "float"
    print("PASS: Float type")
    
    # Test boolean
    bool_val = RedStarValue(True, "bool")
    assert bool_val.value is True
    assert bool_val.type == "bool"
    print("PASS: Boolean type")
    
    # Test None value
    none_val = RedStarValue(None, "none")
    assert none_val.value is None
    assert none_val.type == "none"
    print("PASS: None type")
    
    # Test DArray
    arr = DArray()
    arr.append("item1")
    arr.append("item2")
    arr_val = RedStarValue(arr, "list")
    assert len(arr_val.value) == 2
    assert arr_val.value[0] == "item1"
    assert arr_val.type == "list"
    print("PASS: DArray type")
    
    # Test HashSet
    hs = HashSet()
    hs.add("member1")
    hs.add("member2")
    set_val = RedStarValue(hs, "set")
    assert len(set_val.value) == 2
    assert "member1" in set_val.value
    assert set_val.type == "set"
    print("PASS: HashSet type")
    
    # Test HashTable
    ht = HashTable()
    ht["key1"] = "value1"
    ht["key2"] = "value2"
    hash_val = RedStarValue(ht, "hash")
    assert len(hash_val.value) == 2
    assert hash_val.value["key1"] == "value1"
    assert hash_val.type == "hash"
    print("PASS: HashTable type")
    
    print("Different value types tests passed!\n")


def test_expiration_edge_cases():
    """Test edge cases for expiration."""
    print("=== Testing Expiration Edge Cases ===")
    
    # Test with 0 as expiry time (epoch)
    epoch_val = RedStarValue("epoch", "string", 0)
    assert epoch_val.is_expired()  # Should be expired
    print("PASS: Zero expiry time")
    
    # Test with negative expiry time
    negative_val = RedStarValue("negative", "string", -1)
    assert negative_val.is_expired()  # Should be expired
    print("PASS: Negative expiry time")
    
    # Test with very large expiry time (far future)
    far_future = time.time() + (365 * 24 * 3600)  # 1 year from now
    future_val = RedStarValue("far_future", "string", far_future)
    assert not future_val.is_expired()
    print("PASS: Far future expiry time")
    
    # Test modifying expiry time after creation
    val = RedStarValue("mutable", "string", time.time() + 10)
    assert not val.is_expired()
    
    # Change expiry to past
    val.expiry_time = time.time() - 10
    assert val.is_expired()
    print("PASS: Modifying expiry time")
    
    # Test removing expiry (set to None)
    val.expiry_time = None
    assert not val.is_expired()
    print("PASS: Removing expiry time")
    
    print("Expiration edge cases tests passed!\n")


def test_value_modification():
    """Test modifying value and type after creation."""
    print("=== Testing Value Modification ===")
    
    # Test modifying value
    val = RedStarValue("original", "string")
    assert val.value == "original"
    
    val.value = "modified"
    assert val.value == "modified"
    assert val.type == "string"  # Type should remain the same
    print("PASS: Value modification")
    
    # Test modifying type
    val.type = "modified_string"
    assert val.type == "modified_string"
    assert val.value == "modified"  # Value should remain the same
    print("PASS: Type modification")
    
    # Test modifying both value and type
    val.value = 42
    val.type = "int"
    assert val.value == 42
    assert val.type == "int"
    print("PASS: Both value and type modification")
    
    print("Value modification tests passed!\n")


def test_complex_data_with_expiration():
    """Test complex data structures with expiration."""
    print("=== Testing Complex Data with Expiration ===")
    
    # Create complex data structure
    complex_data = HashTable()
    complex_data["users"] = DArray()
    complex_data["users"].append("user1")
    complex_data["users"].append("user2")
    complex_data["count"] = 42
    
    # Store with expiration
    future_time = time.time() + 5
    complex_val = RedStarValue(complex_data, "hash", future_time)
    
    # Verify data integrity
    assert not complex_val.is_expired()
    assert len(complex_val.value) == 2
    assert "users" in complex_val.value
    assert complex_val.value["count"] == 42
    assert len(complex_val.value["users"]) == 2
    print("PASS: Complex data structure with expiration")
    
    # Test that data is still accessible after modification
    complex_val.value["new_field"] = "added"
    assert "new_field" in complex_val.value
    assert complex_val.value["new_field"] == "added"
    print("PASS: Modifying complex data")
    
    print("Complex data with expiration tests passed!\n")


def test_time_based_expiration():
    """Test time-based expiration scenarios."""
    print("=== Testing Time-based Expiration Scenarios ===")
    
    # Test multiple values with different expiration times
    now = time.time()
    
    val1 = RedStarValue("expires_first", "string", now + 0.1)   # 100ms
    val2 = RedStarValue("expires_second", "string", now + 0.2)  # 200ms
    val3 = RedStarValue("expires_third", "string", now + 0.3)   # 300ms
    
    # Initially none should be expired
    assert not val1.is_expired()
    assert not val2.is_expired()
    assert not val3.is_expired()
    print("PASS: Initial state - none expired")
    
    # Wait for first to expire
    time.sleep(0.15)
    assert val1.is_expired()
    assert not val2.is_expired()
    assert not val3.is_expired()
    print("PASS: First value expired")
    
    # Wait for second to expire
    time.sleep(0.1)
    assert val1.is_expired()
    assert val2.is_expired()
    assert not val3.is_expired()
    print("PASS: Second value expired")
    
    # Wait for third to expire
    time.sleep(0.1)
    assert val1.is_expired()
    assert val2.is_expired()
    assert val3.is_expired()
    print("PASS: Third value expired")
    
    print("Time-based expiration scenarios tests passed!\n")


def run_all_redstar_value_tests():
    """Run all RedStarValue tests."""
    print("Starting comprehensive RedStarValue tests...\n")
    
    test_basic_value_creation()
    test_expiration_logic()
    test_different_value_types()
    test_expiration_edge_cases()
    test_value_modification()
    test_complex_data_with_expiration()
    test_time_based_expiration()
    
    print("SUCCESS: All RedStarValue tests passed!")


if __name__ == "__main__":
    run_all_redstar_value_tests()