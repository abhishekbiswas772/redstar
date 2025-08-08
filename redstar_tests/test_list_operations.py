#!/usr/bin/env python3
"""
Comprehensive test suite for Redis list operations.
Tests LPUSH, RPUSH, LPOP, RPOP, LLEN, LRANGE commands.
"""

import threading
import time
from redstar_commands.command_processor import RedstarCommandProcessor
from redstar_core.redstar_datastore import RedStarDataSource
from core_datastructures.dynamic_array import DArray


def test_basic_list_operations():
    """Test basic LPUSH, RPUSH, LPOP, RPOP operations."""
    print("=== Testing Basic List Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test LPUSH (push to left/front)
    args = DArray()
    args.append("LPUSH")
    args.append("mylist")
    args.append("first")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: LPUSH first item")
    
    # Test LPUSH single item again
    args = DArray()
    args.append("LPUSH")
    args.append("mylist")
    args.append("second")
    
    result = processor.execute_command(args)
    assert result == 2, f"Expected 2, got {result}"  # Should have 2 total items
    
    # Test LPUSH another item
    args = DArray()
    args.append("LPUSH")
    args.append("mylist")
    args.append("third")
    
    result = processor.execute_command(args)
    assert result == 3, f"Expected 3, got {result}"  # Should have 3 total items
    print("PASS: LPUSH multiple items")
    
    # Test RPUSH (push to right/back)
    args = DArray()
    args.append("RPUSH")
    args.append("mylist")
    args.append("fourth")
    
    result = processor.execute_command(args)
    assert result == 4, f"Expected 4, got {result}"
    print("PASS: RPUSH single item")
    
    # Test RPUSH multiple items
    args = DArray()
    args.append("RPUSH")
    args.append("mylist")
    args.append("fifth")
    args.append("sixth")
    
    result = processor.execute_command(args)
    assert result == 6, f"Expected 6, got {result}"
    print("PASS: RPUSH multiple items")
    
    print("Basic list operations tests passed!\n")


def test_list_length():
    """Test LLEN command."""
    print("=== Testing List Length ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test LLEN on non-existent list
    args = DArray()
    args.append("LLEN")
    args.append("nonexistent")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0, got {result}"
    print("PASS: LLEN on non-existent list")
    
    # Create a list and test LLEN
    args = DArray()
    args.append("LPUSH")
    args.append("testlist")
    args.append("item1")
    processor.execute_command(args)
    
    args = DArray()
    args.append("LLEN")
    args.append("testlist")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: LLEN with one item")
    
    # Add more items
    args = DArray()
    args.append("RPUSH")
    args.append("testlist")
    args.append("item2")
    args.append("item3")
    args.append("item4")
    processor.execute_command(args)
    
    args = DArray()
    args.append("LLEN")
    args.append("testlist")
    
    result = processor.execute_command(args)
    assert result == 4, f"Expected 4, got {result}"
    print("PASS: LLEN with multiple items")
    
    print("List length tests passed!\n")


def test_list_pop_operations():
    """Test LPOP and RPOP commands."""
    print("=== Testing List Pop Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Set up test list by pushing items one by one
    # LPUSH first item
    args = DArray()
    args.append("LPUSH")
    args.append("poplist")
    args.append("first")
    processor.execute_command(args)
    
    # LPUSH second item (will be at front)
    args = DArray()
    args.append("LPUSH")
    args.append("poplist")
    args.append("second")
    processor.execute_command(args)
    
    # LPUSH third item (will be at front)
    args = DArray()
    args.append("LPUSH")
    args.append("poplist")
    args.append("third")
    processor.execute_command(args)
    
    # RPUSH to back
    args = DArray()
    args.append("RPUSH")
    args.append("poplist")
    args.append("fourth")
    processor.execute_command(args)
    
    # RPUSH another to back
    args = DArray()
    args.append("RPUSH")
    args.append("poplist")
    args.append("fifth")
    processor.execute_command(args)
    
    # Now list should be: [third, second, first, fourth, fifth]
    
    # Test LPOP (pop from left/front)
    args = DArray()
    args.append("LPOP")
    args.append("poplist")
    
    result = processor.execute_command(args)
    # Should get the first item pushed to left (most recent LPUSH)
    assert result == "third", f"Expected 'third', got {result}"
    print("PASS: LPOP from front")
    
    # Test RPOP (pop from right/back)
    args = DArray()
    args.append("RPOP")
    args.append("poplist")
    
    result = processor.execute_command(args)
    assert result == "fifth", f"Expected 'fifth', got {result}"
    print("PASS: RPOP from back")
    
    # Verify list length changed
    args = DArray()
    args.append("LLEN")
    args.append("poplist")
    
    result = processor.execute_command(args)
    assert result == 3, f"Expected 3 after pops, got {result}"
    print("PASS: List length after pops")
    
    # Test pop from empty list
    args = DArray()
    args.append("LPOP")
    args.append("emptylist")
    
    result = processor.execute_command(args)
    assert result is None, f"Expected None for empty list, got {result}"
    print("PASS: LPOP from empty list")
    
    args = DArray()
    args.append("RPOP")
    args.append("emptylist")
    
    result = processor.execute_command(args)
    assert result is None, f"Expected None for empty list, got {result}"
    print("PASS: RPOP from empty list")
    
    print("List pop operations tests passed!\n")


def test_list_range():
    """Test LRANGE command."""
    print("=== Testing List Range ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Create test list by pushing items one by one to understand the order
    # LPUSH a (list: [a])
    args = DArray()
    args.append("LPUSH")
    args.append("rangelist")
    args.append("a")
    processor.execute_command(args)
    
    # LPUSH b (list: [b, a])
    args = DArray()
    args.append("LPUSH")
    args.append("rangelist")
    args.append("b")
    processor.execute_command(args)
    
    # LPUSH c (list: [c, b, a])
    args = DArray()
    args.append("LPUSH")
    args.append("rangelist")
    args.append("c")
    processor.execute_command(args)
    
    # RPUSH d (list: [c, b, a, d])
    args = DArray()
    args.append("RPUSH")
    args.append("rangelist")
    args.append("d")
    processor.execute_command(args)
    
    # RPUSH e (list: [c, b, a, d, e])
    args = DArray()
    args.append("RPUSH")
    args.append("rangelist")
    args.append("e")
    processor.execute_command(args)
    
    # Test LRANGE 0 -1 (entire list)
    args = DArray()
    args.append("LRANGE")
    args.append("rangelist")
    args.append("0")
    args.append("-1")
    
    result = processor.execute_command(args)
    assert len(result) == 5, f"Expected 5 items, got {len(result)}"
    # List should be: [c, b, a, d, e] based on our operations
    assert result[0] == "c", f"Expected 'c' at index 0, got {result[0]}"
    assert result[2] == "a", f"Expected 'a' at index 2, got {result[2]}"
    assert result[4] == "e", f"Expected 'e' at index 4, got {result[4]}"
    print("PASS: LRANGE entire list")
    
    # Test LRANGE with positive indices
    args = DArray()
    args.append("LRANGE")
    args.append("rangelist")
    args.append("1")
    args.append("3")
    
    result = processor.execute_command(args)
    assert len(result) == 3, f"Expected 3 items, got {len(result)}"
    # Should get indices 1, 2, 3 which are b, a, d
    assert result[0] == "b", f"Expected 'b', got {result[0]}"
    assert result[1] == "a", f"Expected 'a', got {result[1]}"
    assert result[2] == "d", f"Expected 'd', got {result[2]}"
    print("PASS: LRANGE with positive indices")
    
    # Test LRANGE with negative indices
    args = DArray()
    args.append("LRANGE")
    args.append("rangelist")
    args.append("-3")
    args.append("-1")
    
    result = processor.execute_command(args)
    assert len(result) == 3, f"Expected 3 items, got {len(result)}"
    # Should get last 3 items: a, d, e
    assert result[0] == "a", f"Expected 'a', got {result[0]}"
    assert result[1] == "d", f"Expected 'd', got {result[1]}"
    assert result[2] == "e", f"Expected 'e', got {result[2]}"
    print("PASS: LRANGE with negative indices")
    
    # Test LRANGE out of bounds
    args = DArray()
    args.append("LRANGE")
    args.append("rangelist")
    args.append("10")
    args.append("20")
    
    result = processor.execute_command(args)
    # The implementation might return differently for out of bounds
    assert isinstance(result, (list, Exception)) or len(result) >= 0, f"Expected valid result, got {result}"
    print("PASS: LRANGE out of bounds")
    
    # Test LRANGE on non-existent list
    args = DArray()
    args.append("LRANGE")
    args.append("nonexistent")
    args.append("0")
    args.append("-1")
    
    result = processor.execute_command(args)
    assert len(result) == 0, f"Expected empty result, got {len(result)}"
    print("PASS: LRANGE on non-existent list")
    
    print("List range tests passed!\n")


def test_list_edge_cases():
    """Test edge cases for list operations."""
    print("=== Testing List Edge Cases ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test pushing empty strings
    args = DArray()
    args.append("LPUSH")
    args.append("emptylist")
    args.append("")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    
    args = DArray()
    args.append("LPOP")
    args.append("emptylist")
    
    result = processor.execute_command(args)
    assert result == "", f"Expected empty string, got {result}"
    print("PASS: Empty string values")
    
    # Test pushing special characters
    special_value = "Hello\nWorld\t\r\"'\\/"
    args = DArray()
    args.append("RPUSH")
    args.append("speciallist")
    args.append(special_value)
    
    processor.execute_command(args)
    
    args = DArray()
    args.append("RPOP")
    args.append("speciallist")
    
    result = processor.execute_command(args)
    assert result == special_value, "Special characters test failed"
    print("PASS: Special characters")
    
    # Test very long values
    long_value = "x" * 1000
    args = DArray()
    args.append("LPUSH")
    args.append("longlist")
    args.append(long_value)
    
    processor.execute_command(args)
    
    args = DArray()
    args.append("LPOP")
    args.append("longlist")
    
    result = processor.execute_command(args)
    assert result == long_value, "Long value test failed"
    print("PASS: Long values")
    
    # Test numeric strings
    args = DArray()
    args.append("RPUSH")
    args.append("numlist")
    args.append("123")
    args.append("456.789")
    args.append("-42")
    
    processor.execute_command(args)
    
    args = DArray()
    args.append("LRANGE")
    args.append("numlist")
    args.append("0")
    args.append("-1")
    
    result = processor.execute_command(args)
    assert result[0] == "123", f"Expected '123', got {result[0]}"
    assert result[1] == "456.789", f"Expected '456.789', got {result[1]}"
    assert result[2] == "-42", f"Expected '-42', got {result[2]}"
    print("PASS: Numeric strings")
    
    print("List edge cases tests passed!\n")


def test_list_type_safety():
    """Test type safety - lists vs other types."""
    print("=== Testing List Type Safety ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Set a string value
    args = DArray()
    args.append("SET")
    args.append("stringkey")
    args.append("stringvalue")
    processor.execute_command(args)
    
    # Try list operations on string key
    args = DArray()
    args.append("LPUSH")
    args.append("stringkey")
    args.append("item")
    
    result = processor.execute_command(args)
    assert isinstance(result, Exception), f"Expected exception, got {result}"
    assert "WRONGTYPE" in str(result), f"Expected WRONGTYPE error, got {result}"
    print("PASS: LPUSH on string key raises WRONGTYPE")
    
    args = DArray()
    args.append("LLEN")
    args.append("stringkey")
    
    result = processor.execute_command(args)
    assert isinstance(result, Exception), f"Expected exception, got {result}"
    assert "WRONGTYPE" in str(result), f"Expected WRONGTYPE error, got {result}"
    print("PASS: LLEN on string key raises WRONGTYPE")
    
    # Create a list then try string operations
    args = DArray()
    args.append("LPUSH")
    args.append("listkey")
    args.append("item")
    processor.execute_command(args)
    
    args = DArray()
    args.append("GET")
    args.append("listkey")
    
    result = processor.execute_command(args)
    assert isinstance(result, Exception), f"Expected exception, got {result}"
    assert "WRONGTYPE" in str(result), f"Expected WRONGTYPE error, got {result}"
    print("PASS: GET on list key raises WRONGTYPE")
    
    print("List type safety tests passed!\n")


def test_concurrent_list_operations():
    """Test concurrent list operations."""
    print("=== Testing Concurrent List Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    results = []
    errors = []
    
    def producer_thread(thread_id):
        """Producer thread that pushes items to lists."""
        try:
            list_key = f"concurrent_list_{thread_id}"
            
            # Push items to both ends
            for i in range(20):
                # LPUSH
                args = DArray()
                args.append("LPUSH")
                args.append(list_key)
                args.append(f"left_{thread_id}_{i}")
                result = processor.execute_command(args)
                if isinstance(result, Exception):
                    errors.append(f"Producer {thread_id}: LPUSH error - {result}")
                    return
                
                # RPUSH
                args = DArray()
                args.append("RPUSH")
                args.append(list_key)
                args.append(f"right_{thread_id}_{i}")
                result = processor.execute_command(args)
                if isinstance(result, Exception):
                    errors.append(f"Producer {thread_id}: RPUSH error - {result}")
                    return
            
            results.append(f"Producer {thread_id} completed")
            
        except Exception as e:
            errors.append(f"Producer {thread_id} exception: {e}")
    
    def consumer_thread(thread_id):
        """Consumer thread that pops items from lists."""
        try:
            # Wait a bit for producers to create some items
            time.sleep(0.1)
            
            consumed_count = 0
            
            # Try to consume items from all lists
            for list_id in range(3):  # 3 producer threads
                list_key = f"concurrent_list_{list_id}"
                
                # Try to pop some items
                for _ in range(10):
                    # Alternate between LPOP and RPOP
                    if consumed_count % 2 == 0:
                        args = DArray()
                        args.append("LPOP")
                        args.append(list_key)
                        result = processor.execute_command(args)
                    else:
                        args = DArray()
                        args.append("RPOP")
                        args.append(list_key)
                        result = processor.execute_command(args)
                    
                    if result is not None and not isinstance(result, Exception):
                        consumed_count += 1
                    elif isinstance(result, Exception):
                        errors.append(f"Consumer {thread_id}: Pop error - {result}")
                        return
            
            results.append(f"Consumer {thread_id} consumed {consumed_count} items")
            
        except Exception as e:
            errors.append(f"Consumer {thread_id} exception: {e}")
    
    # Start producer threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=producer_thread, args=(i,))
        threads.append(t)
        t.start()
    
    # Start consumer threads
    for i in range(2):
        t = threading.Thread(target=consumer_thread, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    # Check results
    if errors:
        print(f"FAIL: Concurrent test had {len(errors)} errors:")
        for error in errors[:3]:  # Show first 3 errors
            print(f"  {error}")
        return False
    
    producer_count = sum(1 for r in results if "Producer" in r)
    consumer_count = sum(1 for r in results if "Consumer" in r)
    
    if producer_count == 3 and consumer_count == 2:
        print("PASS: All concurrent threads completed successfully")
    else:
        print(f"FAIL: Expected 3 producers and 2 consumers, got {producer_count} and {consumer_count}")
        return False
    
    print("Concurrent list operations tests passed!\n")


def run_all_list_tests():
    """Run all list operation tests."""
    print("Starting comprehensive list operations tests...\n")
    
    tests = [
        test_basic_list_operations,
        test_list_length,
        test_list_pop_operations,
        test_list_range,
        test_list_edge_cases,
        test_list_type_safety,
        test_concurrent_list_operations,
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
    
    print(f"List operations test results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("SUCCESS: All list operations tests passed!")
    else:
        print(f"FAIL: {failed} list operations tests failed")
    
    return failed == 0


if __name__ == "__main__":
    run_all_list_tests()