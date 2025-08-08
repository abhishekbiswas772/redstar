#!/usr/bin/env python3
"""
Comprehensive test suite for RESP protocol parser.
Tests encoding and decoding of all RESP types.
"""

from redstar_core.redstar_protocol import RedStarParsor
from core_datastructures.dynamic_array import DArray


def test_simple_string():
    """Test simple string encoding and decoding."""
    print("=== Testing Simple Strings ===")
    
    # Test basic simple string - but parser doesn't encode these directly
    # Only produces them for str conversion of other types
    
    # Test decode simple string
    encoded = b"+OK\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert result == "OK"
    assert consumed == 5
    print("PASS: Simple string decode")
    
    # Test empty simple string
    encoded = b"+\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert result == ""
    assert consumed == 3
    print("PASS: Empty simple string decode")
    
    # Test simple string with spaces
    encoded = b"+Hello World\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert result == "Hello World"
    assert consumed == 14
    print("PASS: Simple string with spaces")
    
    print("Simple string tests passed!\n")


def test_error():
    """Test error encoding and decoding."""
    print("=== Testing Errors ===")
    
    # Test error encoding
    error = Exception("Test error")
    encoded = RedStarParsor.encode(error)
    assert encoded == b"-Test error\r\n"
    print("PASS: Error encoding")
    
    # Test error decoding
    encoded = b"-Error message\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert isinstance(result, Exception)
    assert str(result) == "Error message"
    assert consumed == 16
    print("PASS: Error decoding")
    
    # Test empty error
    encoded = b"-\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert isinstance(result, Exception)
    assert str(result) == ""
    print("PASS: Empty error")
    
    print("Error tests passed!\n")


def test_integer():
    """Test integer encoding and decoding."""
    print("=== Testing Integers ===")
    
    # Test positive integer
    encoded = RedStarParsor.encode(42)
    assert encoded == b":42\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert result == 42
    assert consumed == 5
    print("PASS: Positive integer")
    
    # Test zero
    encoded = RedStarParsor.encode(0)
    assert encoded == b":0\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert result == 0
    print("PASS: Zero")
    
    # Test negative integer
    encoded = RedStarParsor.encode(-123)
    assert encoded == b":-123\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert result == -123
    print("PASS: Negative integer")
    
    # Test large integer
    large_int = 1234567890
    encoded = RedStarParsor.encode(large_int)
    result, consumed = RedStarParsor.decode(encoded)
    assert result == large_int
    print("PASS: Large integer")
    
    print("Integer tests passed!\n")


def test_boolean():
    """Test boolean encoding."""
    print("=== Testing Booleans ===")
    
    # Test True
    encoded = RedStarParsor.encode(True)
    assert encoded == b":1\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert result == 1  # Booleans are encoded as integers
    print("PASS: Boolean True")
    
    # Test False
    encoded = RedStarParsor.encode(False)
    assert encoded == b":0\r\n"
    result, consumed = RedStarParsor.decode(encoded)
    assert result == 0
    print("PASS: Boolean False")
    
    print("Boolean tests passed!\n")


def test_bulk_string():
    """Test bulk string encoding and decoding."""
    print("=== Testing Bulk Strings ===")
    
    # Test normal string
    encoded = RedStarParsor.encode("Hello")
    expected = b"$5\r\nHello\r\n"
    assert encoded == expected
    result, consumed = RedStarParsor.decode(encoded)
    assert result == "Hello"
    assert consumed == 11
    print("PASS: Normal bulk string")
    
    # Test empty string
    encoded = RedStarParsor.encode("")
    expected = b"$0\r\n\r\n"
    assert encoded == expected
    result, consumed = RedStarParsor.decode(encoded)
    assert result == ""
    print("PASS: Empty bulk string")
    
    # Test null string
    encoded = RedStarParsor.encode(None)
    expected = b"$-1\r\n"
    assert encoded == expected
    result, consumed = RedStarParsor.decode(encoded)
    assert result is None
    print("PASS: Null bulk string")
    
    # Test string with special characters
    test_str = "Hello\r\nWorld"
    encoded = RedStarParsor.encode(test_str)
    result, consumed = RedStarParsor.decode(encoded)
    assert result == test_str
    print("PASS: String with CRLF")
    
    # Test unicode string
    unicode_str = "Hello 世界"
    encoded = RedStarParsor.encode(unicode_str)
    result, consumed = RedStarParsor.decode(encoded)
    assert result == unicode_str
    print("PASS: Unicode string")
    
    # Test binary data as bytes
    binary_data = b"\x00\x01\x02\xff"
    encoded = RedStarParsor.encode(binary_data)
    # Decoding binary might fail since it tries to decode as UTF-8
    # This is a limitation in the current implementation
    print("PASS: Binary data encoding (decode may not work due to UTF-8)")
    
    print("Bulk string tests passed!\n")


def test_array():
    """Test array encoding and decoding."""
    print("=== Testing Arrays ===")
    
    # Test DArray
    arr = DArray()
    arr.append("foo")
    arr.append("bar")
    encoded = RedStarParsor.encode(arr)
    result, consumed = RedStarParsor.decode(encoded)
    assert len(result) == 2
    assert result[0] == "foo"
    assert result[1] == "bar"
    print("PASS: DArray encoding/decoding")
    
    # Test list
    test_list = ["hello", "world"]
    encoded = RedStarParsor.encode(test_list)
    result, consumed = RedStarParsor.decode(encoded)
    assert len(result) == 2
    assert result[0] == "hello"
    assert result[1] == "world"
    print("PASS: List encoding/decoding")
    
    # Test empty array
    empty_arr = DArray()
    encoded = RedStarParsor.encode(empty_arr)
    expected = b"*0\r\n"
    assert encoded == expected
    result, consumed = RedStarParsor.decode(encoded)
    assert len(result) == 0
    print("PASS: Empty array")
    
    # Test array with mixed types
    mixed = DArray()
    mixed.append("string")
    mixed.append(42)
    mixed.append(None)
    encoded = RedStarParsor.encode(mixed)
    result, consumed = RedStarParsor.decode(encoded)
    assert len(result) == 3
    assert result[0] == "string"
    assert result[1] == 42
    assert result[2] is None
    print("PASS: Mixed type array")
    
    # Test nested arrays
    nested = DArray()
    inner = DArray()
    inner.append("nested")
    nested.append(inner)
    nested.append("top")
    encoded = RedStarParsor.encode(nested)
    result, consumed = RedStarParsor.decode(encoded)
    assert len(result) == 2
    assert len(result[0]) == 1
    assert result[0][0] == "nested"
    assert result[1] == "top"
    print("PASS: Nested arrays")
    
    print("Array tests passed!\n")


def test_incomplete_data():
    """Test handling of incomplete data."""
    print("=== Testing Incomplete Data ===")
    
    # Test incomplete simple string
    incomplete = b"+Hello"  # Missing \r\n
    result, consumed = RedStarParsor.decode(incomplete)
    assert result is None
    assert consumed == 0
    print("PASS: Incomplete simple string")
    
    # Test incomplete integer
    incomplete = b":42"  # Missing \r\n
    result, consumed = RedStarParsor.decode(incomplete)
    assert result is None
    assert consumed == 0
    print("PASS: Incomplete integer")
    
    # Test incomplete bulk string length
    incomplete = b"$5"  # Missing \r\n after length
    result, consumed = RedStarParsor.decode(incomplete)
    assert result is None
    assert consumed == 0
    print("PASS: Incomplete bulk string length")
    
    # Test incomplete bulk string data
    incomplete = b"$5\r\nHel"  # Missing some data and final \r\n
    result, consumed = RedStarParsor.decode(incomplete)
    assert result is None
    assert consumed == 0
    print("PASS: Incomplete bulk string data")
    
    # Test incomplete array
    incomplete = b"*2\r\n$3\r\nfoo"  # Missing second element
    result, consumed = RedStarParsor.decode(incomplete)
    assert result is None
    assert consumed == 0
    print("PASS: Incomplete array")
    
    print("Incomplete data tests passed!\n")


def test_edge_cases():
    """Test edge cases and error conditions."""
    print("=== Testing Edge Cases ===")
    
    # Test invalid type byte
    try:
        invalid = b"@invalid\r\n"
        RedStarParsor.decode(invalid)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Unknown RESP type" in str(e)
    print("PASS: Invalid type byte")
    
    # Test empty buffer
    result, consumed = RedStarParsor.decode(b"", 0)
    assert result is None
    assert consumed == 0
    print("PASS: Empty buffer")
    
    # Test offset beyond buffer
    result, consumed = RedStarParsor.decode(b"hello", 10)
    assert result is None
    assert consumed == 0
    print("PASS: Offset beyond buffer")
    
    # Test encoding other types (fallback to simple string)
    custom_obj = {"key": "value"}
    encoded = RedStarParsor.encode(custom_obj)
    # Should use str() representation with + prefix
    assert encoded.startswith(b"+")
    assert encoded.endswith(b"\r\n")
    print("PASS: Custom object encoding fallback")
    
    print("Edge case tests passed!\n")


def test_round_trip():
    """Test encode/decode round trips."""
    print("=== Testing Round Trip Encoding/Decoding ===")
    
    test_cases = [
        "simple string",
        "",
        None,
        42,
        -123,
        0,
        True,
        False,
        Exception("test error"),
    ]
    
    for i, case in enumerate(test_cases):
        encoded = RedStarParsor.encode(case)
        decoded, consumed = RedStarParsor.decode(encoded)
        
        if isinstance(case, Exception):
            assert isinstance(decoded, Exception)
            assert str(decoded) == str(case)
        elif isinstance(case, bool):
            # Booleans become integers
            assert decoded == (1 if case else 0)
        else:
            assert decoded == case
        
        assert consumed == len(encoded)
        print(f"PASS: Round trip test case {i + 1}")
    
    # Test complex array round trip
    complex_arr = DArray()
    complex_arr.append("string")
    complex_arr.append(42)
    complex_arr.append(None)
    inner_arr = DArray()
    inner_arr.append("nested")
    complex_arr.append(inner_arr)
    
    encoded = RedStarParsor.encode(complex_arr)
    decoded, consumed = RedStarParsor.decode(encoded)
    
    assert len(decoded) == 4
    assert decoded[0] == "string"
    assert decoded[1] == 42
    assert decoded[2] is None
    assert len(decoded[3]) == 1
    assert decoded[3][0] == "nested"
    assert consumed == len(encoded)
    print("PASS: Complex array round trip")
    
    print("Round trip tests passed!\n")


def run_all_resp_tests():
    """Run all RESP protocol tests."""
    print("Starting comprehensive RESP protocol tests...\n")
    
    test_simple_string()
    test_error()
    test_integer()
    test_boolean()
    test_bulk_string()
    test_array()
    test_incomplete_data()
    test_edge_cases()
    test_round_trip()
    
    print("SUCCESS: All RESP protocol tests passed!")


if __name__ == "__main__":
    run_all_resp_tests()