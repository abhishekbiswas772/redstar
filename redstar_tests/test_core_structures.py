#!/usr/bin/env python3
"""
Comprehensive test suite for all core data structures.
Tests every method, edge case, and functionality.
"""

from core_datastructures.dynamic_array import DArray
from core_datastructures.linked_list import DLList, DLLNode
from core_datastructures.hash_table import HashTable
from core_datastructures.hashset import HashSet


def test_dynamic_array():
    """Test DArray functionality comprehensively."""
    print("=== Testing DArray ===")
    
    # Test initialization
    arr = DArray()
    assert len(arr) == 0
    assert arr.capacity == 4
    print("PASS: Initialization")
    
    # Test custom init size
    arr2 = DArray(8)
    assert arr2.capacity == 8
    print("PASS: Custom initialization size")
    
    # Test append and automatic resizing
    for i in range(10):
        arr.append(i)
    assert len(arr) == 10
    assert arr.capacity >= 10  # Should have resized
    print("PASS: Append and auto-resize")
    
    # Test indexing (positive and negative)
    assert arr[0] == 0
    assert arr[9] == 9
    assert arr[-1] == 9
    assert arr[-10] == 0
    print("PASS: Indexing (positive/negative)")
    
    # Test index out of bounds
    try:
        _ = arr[10]
        assert False, "Should raise IndexError"
    except IndexError:
        pass
    
    try:
        _ = arr[-11]
        assert False, "Should raise IndexError"  
    except IndexError:
        pass
    print("PASS: Index bounds checking")
    
    # Test setitem
    arr[0] = 100
    assert arr[0] == 100
    arr[-1] = 999
    assert arr[9] == 999
    print("PASS: Item assignment")
    
    # Test pop from end
    val = arr.pop()
    assert val == 999
    assert len(arr) == 9
    print("PASS: Pop from end")
    
    # Test pop from specific index
    val = arr.pop(0)
    assert val == 100
    assert len(arr) == 8
    assert arr[0] == 1  # Next element shifted
    print("PASS: Pop from specific index")
    
    # Test pop from empty array
    empty_arr = DArray()
    try:
        empty_arr.pop()
        assert False, "Should raise IndexError"
    except IndexError:
        pass
    print("PASS: Pop from empty array error")
    
    # Test insert
    arr.insert(0, 0)  # Insert at beginning
    assert arr[0] == 0
    assert len(arr) == 9
    
    arr.insert(5, 500)  # Insert in middle
    assert arr[5] == 500
    assert len(arr) == 10
    
    arr.insert(-1, -100)  # Negative index insert
    assert arr[9] == -100  # Should be inserted before last element
    print("PASS: Insert operations")
    
    # Test iteration
    values = list(arr)
    assert len(values) == len(arr)
    print("PASS: Iteration")
    
    # Test repr
    repr_str = repr(arr)
    assert "DArray" in repr_str
    print("PASS: String representation")
    
    # Test shrinking on pop
    small_arr = DArray()
    for i in range(20):
        small_arr.append(i)
    original_capacity = small_arr.capacity
    
    # Pop most elements to trigger shrinking
    while len(small_arr) > original_capacity // 8:
        small_arr.pop()
    
    # Should have shrunk
    assert small_arr.capacity < original_capacity
    print("PASS: Array shrinking on pop")
    
    print("DArray tests passed!\n")


def test_doubly_linked_list():
    """Test DLList functionality comprehensively."""
    print("=== Testing DLList ===")
    
    # Test initialization
    dll = DLList()
    assert len(dll) == 0
    assert dll.is_empty()
    print("PASS: Initialization")
    
    # Test add_first
    dll.add_first(1)
    assert len(dll) == 1
    assert not dll.is_empty()
    assert dll.peek_first() == 1
    assert dll.peek_last() == 1
    print("PASS: Add first element")
    
    # Test add_last
    dll.add_last(2)
    assert len(dll) == 2
    assert dll.peek_first() == 1
    assert dll.peek_last() == 2
    print("PASS: Add last element")
    
    # Test multiple additions
    for i in range(3, 8):
        dll.add_last(i)
    assert len(dll) == 7
    assert dll.peek_first() == 1
    assert dll.peek_last() == 7
    print("PASS: Multiple additions")
    
    # Test remove_first
    val = dll.remove_first()
    assert val == 1
    assert len(dll) == 6
    assert dll.peek_first() == 2
    print("PASS: Remove first")
    
    # Test remove_last
    val = dll.remove_last()
    assert val == 7
    assert len(dll) == 5
    assert dll.peek_last() == 6
    print("PASS: Remove last")
    
    # Test iteration
    values = list(dll)
    expected = [2, 3, 4, 5, 6]
    assert values == expected
    print("PASS: Iteration")
    
    # Test empty operations
    empty_dll = DLList()
    
    try:
        empty_dll.remove_first()
        assert False, "Should raise IndexError"
    except IndexError:
        pass
        
    try:
        empty_dll.remove_last()
        assert False, "Should raise IndexError"
    except IndexError:
        pass
        
    try:
        empty_dll.peek_first()
        assert False, "Should raise IndexError"
    except IndexError:
        pass
        
    try:
        empty_dll.peek_last()
        assert False, "Should raise IndexError"
    except IndexError:
        pass
    print("PASS: Empty list error handling")
    
    # Test repr
    repr_str = repr(dll)
    assert "DLList" in repr_str
    print("PASS: String representation")
    
    # Test clear by removing all
    while not dll.is_empty():
        dll.remove_first()
    assert len(dll) == 0
    assert dll.is_empty()
    print("PASS: Complete clearing")
    
    print("DLList tests passed!\n")


def test_hash_table():
    """Test HashTable functionality comprehensively."""
    print("=== Testing HashTable ===")
    
    # Test initialization
    ht = HashTable()
    assert len(ht) == 0
    print("PASS: Initialization")
    
    # Test custom initial capacity
    ht_custom = HashTable(16)
    assert ht_custom.capacity == 16
    print("PASS: Custom initial capacity")
    
    # Test put and get
    ht.put("key1", "value1")
    assert ht.get("key1") == "value1"
    assert len(ht) == 1
    print("PASS: Put and get")
    
    # Test get_or_default
    assert ht.get_or_default("key1") == "value1"
    assert ht.get_or_default("nonexistent") is None
    assert ht.get_or_default("nonexistent", "default") == "default"
    print("PASS: Get or default")
    
    # Test contains
    assert ht.contains("key1")
    assert not ht.contains("nonexistent")
    print("PASS: Contains")
    
    # Test bracket notation
    ht["key2"] = "value2"
    assert ht["key2"] == "value2"
    assert "key2" in ht
    print("PASS: Bracket notation")
    
    # Test key error on nonexistent
    try:
        _ = ht["nonexistent"]
        assert False, "Should raise KeyError"
    except KeyError:
        pass
    print("PASS: KeyError on nonexistent")
    
    # Test update existing key
    ht["key1"] = "updated_value1"
    assert ht["key1"] == "updated_value1"
    assert len(ht) == 2  # Should not increase size
    print("PASS: Update existing key")
    
    # Test different key types
    ht.put(42, "int_key")
    ht.put((1, 2), "tuple_key")
    assert ht.get(42) == "int_key"
    assert ht.get((1, 2)) == "tuple_key"
    print("PASS: Different key types")
    
    # Test many insertions (trigger resize)
    for i in range(50):
        ht.put(f"bulk_key_{i}", f"bulk_value_{i}")
    
    assert len(ht) == 54  # 2 original + 2 different types + 50 bulk
    assert ht.capacity > 8  # Should have resized
    
    # Verify all bulk keys exist
    for i in range(50):
        assert ht.get(f"bulk_key_{i}") == f"bulk_value_{i}"
    print("PASS: Bulk insertions and resize")
    
    # Test keys, values, items
    keys = ht.keys()
    values = ht.values()
    items = ht.items()
    
    assert len(keys) == len(ht)
    assert len(values) == len(ht)
    assert len(items) == len(ht)
    
    assert "key1" in keys
    assert "updated_value1" in values
    print("PASS: Keys, values, items")
    
    # Test remove
    removed_val = ht.remove("key1")
    assert removed_val == "updated_value1"
    assert len(ht) == 53
    assert not ht.contains("key1")
    
    # Test remove nonexistent
    try:
        ht.remove("nonexistent")
        assert False, "Should raise KeyError"
    except KeyError:
        pass
    print("PASS: Remove operations")
    
    # Test del operator
    del ht["key2"]
    assert not ht.contains("key2")
    assert len(ht) == 52
    print("PASS: Del operator")
    
    # Test iteration
    key_count = 0
    for key in ht:
        key_count += 1
    assert key_count == len(ht)
    print("PASS: Iteration over keys")
    
    # Test repr
    repr_str = repr(ht)
    assert "HashTable" in repr_str
    print("PASS: String representation")
    
    print("HashTable tests passed!\n")


def test_hash_set():
    """Test HashSet functionality comprehensively."""
    print("=== Testing HashSet ===")
    
    # Test initialization
    hs = HashSet()
    assert len(hs) == 0
    print("PASS: Initialization")
    
    # Test add
    added = hs.add("item1")
    assert added  # Should return True for new item
    assert len(hs) == 1
    assert hs.contains("item1")
    print("PASS: Add new item")
    
    # Test add duplicate
    added = hs.add("item1")
    assert not added  # Should return False for existing item
    assert len(hs) == 1
    print("PASS: Add duplicate item")
    
    # Test contains
    assert "item1" in hs
    assert "nonexistent" not in hs
    print("PASS: Contains")
    
    # Test multiple adds
    items = ["item2", "item3", "item4", "item5"]
    for item in items:
        hs.add(item)
    
    assert len(hs) == 5
    for item in items:
        assert item in hs
    print("PASS: Multiple additions")
    
    # Test to_list
    item_list = hs.to_list()
    assert len(item_list) == 5
    assert "item1" in item_list
    print("PASS: To list conversion")
    
    # Test iteration
    found_items = set()
    for item in hs:
        found_items.add(item)
    
    assert len(found_items) == 5
    assert "item1" in found_items
    print("PASS: Iteration")
    
    # Test size method
    assert hs.size() == 5
    print("PASS: Size method")
    
    # Test clear
    hs.clear()
    assert len(hs) == 0
    assert not hs.contains("item1")
    print("PASS: Clear")
    
    # Test different data types
    hs.add(42)
    hs.add(3.14)
    hs.add((1, 2, 3))
    assert 42 in hs
    assert 3.14 in hs
    assert (1, 2, 3) in hs
    assert len(hs) == 3
    print("PASS: Different data types")
    
    # Test repr
    repr_str = repr(hs)
    assert "HashSet" in repr_str
    print("PASS: String representation")
    
    print("HashSet tests passed!\n")


def run_all_core_structure_tests():
    """Run all core data structure tests."""
    print("Starting comprehensive core data structure tests...\n")
    
    test_dynamic_array()
    test_doubly_linked_list() 
    test_hash_table()
    test_hash_set()
    
    print("SUCCESS: All core data structure tests passed!")


if __name__ == "__main__":
    run_all_core_structure_tests()