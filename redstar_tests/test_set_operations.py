#!/usr/bin/env python3
"""
Comprehensive test suite for Redis set operations.
Tests SADD, SREM, SMEMBERS, SCARD, SISMEMBER commands.
"""

import threading
import random
from redstar_commands.command_processor import RedstarCommandProcessor
from redstar_core.redstar_datastore import RedStarDataSource
from core_datastructures.dynamic_array import DArray


def test_basic_set_operations():
    """Test basic SADD and SMEMBERS operations."""
    print("=== Testing Basic Set Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test SADD single member
    args = DArray()
    args.append("SADD")
    args.append("myset")
    args.append("member1")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: SADD single member")
    
    # Test SADD multiple members
    args = DArray()
    args.append("SADD")
    args.append("myset")
    args.append("member2")
    args.append("member3")
    args.append("member4")
    
    result = processor.execute_command(args)
    assert result == 3, f"Expected 3, got {result}"  # 3 new members added
    print("PASS: SADD multiple members")
    
    # Test SADD duplicate member
    args = DArray()
    args.append("SADD")
    args.append("myset")
    args.append("member1")  # Already exists
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0, got {result}"  # No new members added
    print("PASS: SADD duplicate member")
    
    # Test SMEMBERS
    args = DArray()
    args.append("SMEMBERS")
    args.append("myset")
    
    result = processor.execute_command(args)
    assert len(result) == 4, f"Expected 4 members, got {len(result)}"
    
    # Check all members are present (order doesn't matter in sets)
    members = set()
    for i in range(len(result)):
        members.add(result[i])
    
    expected_members = {"member1", "member2", "member3", "member4"}
    assert members == expected_members, f"Expected {expected_members}, got {members}"
    print("PASS: SMEMBERS")
    
    print("Basic set operations tests passed!\n")


def test_set_cardinality():
    """Test SCARD command."""
    print("=== Testing Set Cardinality ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test SCARD on non-existent set
    args = DArray()
    args.append("SCARD")
    args.append("nonexistent")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0, got {result}"
    print("PASS: SCARD on non-existent set")
    
    # Create a set and test SCARD
    args = DArray()
    args.append("SADD")
    args.append("cardset")
    args.append("item1")
    processor.execute_command(args)
    
    args = DArray()
    args.append("SCARD")
    args.append("cardset")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: SCARD with one member")
    
    # Add more members
    args = DArray()
    args.append("SADD")
    args.append("cardset")
    args.append("item2")
    args.append("item3")
    args.append("item4")
    args.append("item5")
    processor.execute_command(args)
    
    args = DArray()
    args.append("SCARD")
    args.append("cardset")
    
    result = processor.execute_command(args)
    assert result == 5, f"Expected 5, got {result}"
    print("PASS: SCARD with multiple members")
    
    print("Set cardinality tests passed!\n")


def test_set_membership():
    """Test SISMEMBER command."""
    print("=== Testing Set Membership ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Create test set
    args = DArray()
    args.append("SADD")
    args.append("memberset")
    args.append("apple")
    args.append("banana")
    args.append("cherry")
    processor.execute_command(args)
    
    # Test SISMEMBER for existing member
    args = DArray()
    args.append("SISMEMBER")
    args.append("memberset")
    args.append("apple")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: SISMEMBER existing member")
    
    # Test SISMEMBER for non-existing member
    args = DArray()
    args.append("SISMEMBER")
    args.append("memberset")
    args.append("orange")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0, got {result}"
    print("PASS: SISMEMBER non-existing member")
    
    # Test SISMEMBER on non-existent set
    args = DArray()
    args.append("SISMEMBER")
    args.append("nonexistent")
    args.append("apple")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0, got {result}"
    print("PASS: SISMEMBER on non-existent set")
    
    print("Set membership tests passed!\n")


def test_set_removal():
    """Test SREM command."""
    print("=== Testing Set Removal ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Create test set
    args = DArray()
    args.append("SADD")
    args.append("remset")
    args.append("item1")
    args.append("item2")
    args.append("item3")
    args.append("item4")
    args.append("item5")
    processor.execute_command(args)
    
    # Test SREM single member
    args = DArray()
    args.append("SREM")
    args.append("remset")
    args.append("item1")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    print("PASS: SREM single member")
    
    # Verify member was removed
    args = DArray()
    args.append("SISMEMBER")
    args.append("remset")
    args.append("item1")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0 after removal, got {result}"
    print("PASS: Verify member removed")
    
    # Test SREM multiple members
    args = DArray()
    args.append("SREM")
    args.append("remset")
    args.append("item2")
    args.append("item3")
    args.append("nonexistent")  # This shouldn't count
    
    result = processor.execute_command(args)
    assert result == 2, f"Expected 2, got {result}"  # Only item2 and item3 removed
    print("PASS: SREM multiple members")
    
    # Test SREM non-existent member
    args = DArray()
    args.append("SREM")
    args.append("remset")
    args.append("nonexistent")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0, got {result}"
    print("PASS: SREM non-existent member")
    
    # Test SREM from non-existent set
    args = DArray()
    args.append("SREM")
    args.append("nonexistent")
    args.append("item")
    
    result = processor.execute_command(args)
    assert result == 0, f"Expected 0, got {result}"
    print("PASS: SREM from non-existent set")
    
    # Check final cardinality
    args = DArray()
    args.append("SCARD")
    args.append("remset")
    
    result = processor.execute_command(args)
    assert result == 2, f"Expected 2 remaining members, got {result}"  # item4, item5
    print("PASS: Final cardinality after removals")
    
    print("Set removal tests passed!\n")


def test_set_edge_cases():
    """Test edge cases for set operations."""
    print("=== Testing Set Edge Cases ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Test empty string member
    args = DArray()
    args.append("SADD")
    args.append("edgeset")
    args.append("")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1, got {result}"
    
    args = DArray()
    args.append("SISMEMBER")
    args.append("edgeset")
    args.append("")
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1 for empty string member, got {result}"
    print("PASS: Empty string member")
    
    # Test special characters
    special_member = "Hello\nWorld\t\r\"'\\/"
    args = DArray()
    args.append("SADD")
    args.append("edgeset")
    args.append(special_member)
    
    processor.execute_command(args)
    
    args = DArray()
    args.append("SISMEMBER")
    args.append("edgeset")
    args.append(special_member)
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1 for special characters, got {result}"
    print("PASS: Special characters")
    
    # Test very long member
    long_member = "x" * 1000
    args = DArray()
    args.append("SADD")
    args.append("edgeset")
    args.append(long_member)
    
    processor.execute_command(args)
    
    args = DArray()
    args.append("SISMEMBER")
    args.append("edgeset")
    args.append(long_member)
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1 for long member, got {result}"
    print("PASS: Long member")
    
    # Test numeric strings
    args = DArray()
    args.append("SADD")
    args.append("numset")
    args.append("123")
    args.append("456.789")
    args.append("-42")
    
    processor.execute_command(args)
    
    args = DArray()
    args.append("SMEMBERS")
    args.append("numset")
    
    result = processor.execute_command(args)
    assert len(result) == 3, f"Expected 3 numeric members, got {len(result)}"
    
    # Convert to set for comparison (order doesn't matter)
    members = set()
    for i in range(len(result)):
        members.add(result[i])
    
    expected = {"123", "456.789", "-42"}
    assert members == expected, f"Expected {expected}, got {members}"
    print("PASS: Numeric strings")
    
    # Test unicode
    unicode_member = "Hello 世界 🌍"
    args = DArray()
    args.append("SADD")
    args.append("edgeset")
    args.append(unicode_member)
    
    processor.execute_command(args)
    
    args = DArray()
    args.append("SISMEMBER")
    args.append("edgeset")
    args.append(unicode_member)
    
    result = processor.execute_command(args)
    assert result == 1, f"Expected 1 for unicode member, got {result}"
    print("PASS: Unicode characters")
    
    print("Set edge cases tests passed!\n")


def test_set_type_safety():
    """Test type safety - sets vs other types."""
    print("=== Testing Set Type Safety ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    # Set a string value
    args = DArray()
    args.append("SET")
    args.append("stringkey")
    args.append("stringvalue")
    processor.execute_command(args)
    
    # Try set operations on string key
    args = DArray()
    args.append("SADD")
    args.append("stringkey")
    args.append("member")
    
    result = processor.execute_command(args)
    assert isinstance(result, Exception), f"Expected exception, got {result}"
    assert "WRONGTYPE" in str(result), f"Expected WRONGTYPE error, got {result}"
    print("PASS: SADD on string key raises WRONGTYPE")
    
    args = DArray()
    args.append("SCARD")
    args.append("stringkey")
    
    result = processor.execute_command(args)
    assert isinstance(result, Exception), f"Expected exception, got {result}"
    assert "WRONGTYPE" in str(result), f"Expected WRONGTYPE error, got {result}"
    print("PASS: SCARD on string key raises WRONGTYPE")
    
    # Create a set then try string operations
    args = DArray()
    args.append("SADD")
    args.append("setkey")
    args.append("member")
    processor.execute_command(args)
    
    args = DArray()
    args.append("GET")
    args.append("setkey")
    
    result = processor.execute_command(args)
    assert isinstance(result, Exception), f"Expected exception, got {result}"
    assert "WRONGTYPE" in str(result), f"Expected WRONGTYPE error, got {result}"
    print("PASS: GET on set key raises WRONGTYPE")
    
    print("Set type safety tests passed!\n")


def test_concurrent_set_operations():
    """Test concurrent set operations."""
    print("=== Testing Concurrent Set Operations ===")
    
    store = RedStarDataSource()
    processor = RedstarCommandProcessor(store)
    
    results = []
    errors = []
    
    def adder_thread(thread_id):
        """Thread that adds members to sets."""
        try:
            set_key = f"concurrent_set_{thread_id}"
            
            # Add members
            for i in range(30):
                args = DArray()
                args.append("SADD")
                args.append(set_key)
                args.append(f"member_{thread_id}_{i}")
                
                result = processor.execute_command(args)
                if isinstance(result, Exception):
                    errors.append(f"Adder {thread_id}: SADD error - {result}")
                    return
                
                # Verify membership
                args = DArray()
                args.append("SISMEMBER")
                args.append(set_key)
                args.append(f"member_{thread_id}_{i}")
                
                result = processor.execute_command(args)
                if result != 1:
                    errors.append(f"Adder {thread_id}: Member not found after adding")
                    return
            
            results.append(f"Adder {thread_id} completed")
            
        except Exception as e:
            errors.append(f"Adder {thread_id} exception: {e}")
    
    def remover_thread(thread_id):
        """Thread that removes members from sets."""
        try:
            # Wait a bit for adders to create some members
            import time
            time.sleep(0.1)
            
            removed_count = 0
            
            # Try to remove members from all sets
            for set_id in range(3):  # 3 adder threads
                set_key = f"concurrent_set_{set_id}"
                
                # Try to remove some members
                for i in range(10):
                    member_key = f"member_{set_id}_{i}"
                    
                    args = DArray()
                    args.append("SREM")
                    args.append(set_key)
                    args.append(member_key)
                    
                    result = processor.execute_command(args)
                    if isinstance(result, Exception):
                        errors.append(f"Remover {thread_id}: SREM error - {result}")
                        return
                    
                    if result == 1:  # Successfully removed
                        removed_count += 1
            
            results.append(f"Remover {thread_id} removed {removed_count} members")
            
        except Exception as e:
            errors.append(f"Remover {thread_id} exception: {e}")
    
    def reader_thread(thread_id):
        """Thread that reads set information."""
        try:
            read_count = 0
            
            # Continuously read set information
            for _ in range(20):
                for set_id in range(3):
                    set_key = f"concurrent_set_{set_id}"
                    
                    # Get cardinality
                    args = DArray()
                    args.append("SCARD")
                    args.append(set_key)
                    
                    result = processor.execute_command(args)
                    if isinstance(result, Exception):
                        errors.append(f"Reader {thread_id}: SCARD error - {result}")
                        return
                    
                    read_count += 1
                    
                    # Get members occasionally
                    if read_count % 10 == 0:
                        args = DArray()
                        args.append("SMEMBERS")
                        args.append(set_key)
                        
                        result = processor.execute_command(args)
                        if isinstance(result, Exception):
                            errors.append(f"Reader {thread_id}: SMEMBERS error - {result}")
                            return
            
            results.append(f"Reader {thread_id} completed {read_count} reads")
            
        except Exception as e:
            errors.append(f"Reader {thread_id} exception: {e}")
    
    # Start threads
    threads = []
    
    # Start adder threads
    for i in range(3):
        t = threading.Thread(target=adder_thread, args=(i,))
        threads.append(t)
        t.start()
    
    # Start remover threads
    for i in range(2):
        t = threading.Thread(target=remover_thread, args=(i,))
        threads.append(t)
        t.start()
    
    # Start reader threads
    for i in range(2):
        t = threading.Thread(target=reader_thread, args=(i,))
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
    
    adder_count = sum(1 for r in results if "Adder" in r)
    remover_count = sum(1 for r in results if "Remover" in r)
    reader_count = sum(1 for r in results if "Reader" in r)
    
    if adder_count == 3 and remover_count == 2 and reader_count == 2:
        print("PASS: All concurrent threads completed successfully")
    else:
        print(f"FAIL: Expected 3 adders, 2 removers, 2 readers, got {adder_count}, {remover_count}, {reader_count}")
        return False
    
    print("Concurrent set operations tests passed!\n")


def run_all_set_tests():
    """Run all set operation tests."""
    print("Starting comprehensive set operations tests...\n")
    
    tests = [
        test_basic_set_operations,
        test_set_cardinality,
        test_set_membership,
        test_set_removal,
        test_set_edge_cases,
        test_set_type_safety,
        test_concurrent_set_operations,
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
    
    print(f"Set operations test results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("SUCCESS: All set operations tests passed!")
    else:
        print(f"FAIL: {failed} set operations tests failed")
    
    return failed == 0


if __name__ == "__main__":
    run_all_set_tests()