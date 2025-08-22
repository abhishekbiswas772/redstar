# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Server Operations
- `python main.py` or `python redstar_main.py` - Start the Redstar server on 127.0.0.1:6379
- `python main.py help` - Show usage information
- `python main.py tutorial` - Display command tutorial

### Testing
- `python run_comprehensive_tests.py` - Run complete test suite (requires server running)
- `python main.py test` - Run built-in individual tests
- `python test_[feature].py` - Run specific test files (e.g., `test_hash_operations.py`)

### Client Connection
- `redis-cli -h 127.0.0.1 -p 6379` - Connect with Redis CLI

## Architecture Overview

### Core Components
- **redstar_server/redstar_server.py** - Main server with networking, threading, signal handling
- **redstar_core/redstar_datastore.py** - Thread-safe data storage using custom data structures
- **redstar_core/pubsub_manager.py** - Pub/Sub messaging system with pattern matching
- **redstar_commands/command_processor.py** - Redis command implementations and RESP protocol handling

### Data Layer
- **core_datastructures/** - Custom implementations (DArray, HashTable, LinkedList, HashSet, etc.)
- Uses DArray instead of Python lists throughout the codebase
- All data structures are thread-safe and built from scratch

### Protocol
- **redstar_core/redstar_protocol.py** - RESP (Redis Serialization Protocol) parser
- **redstar_core/redstar_value.py** - Value wrapper with TTL/expiration support
- Full Redis protocol compatibility for client connections

### Client SDKs
- **client-sdks/python/** - Python client with async support
- **client-sdks/java/** - Java client with Maven build
- **client-sdks/cpp/** - C++ client with CMake build

## Key Design Principles

### Custom Data Structures
- **No external dependencies** for core functionality - everything built from scratch
- **DArray usage** - Use `DArray` instead of Python lists in all implementations
- **HashTable** - Custom hash table with linear probing collision resolution
- **Thread safety** - All shared data protected with `threading.RLock()`

### Redis Compatibility
- **RESP protocol compliance** - All responses must follow Redis protocol format
- **Error format** - Use `-ERR message\r\n` for errors
- **Command naming** - Follow exact Redis command names (HGETALL, LPUSH, etc.)

### Code Conventions
- Use RedStarDataSource for data operations, not direct data structure access
- Command handlers return RESP-formatted strings
- Thread safety required for all shared data modifications
- Type checking with `redstar_value.type` for command validation

## Testing Strategy

Tests require the server to be running on port 6379. The comprehensive test runner checks server connectivity before running tests.

### Test Categories
- **Protocol compliance** - RESP format validation
- **Command functionality** - All Redis commands work correctly  
- **Thread safety** - Concurrent operations testing
- **Edge cases** - Error handling and malformed input
- **Pub/Sub** - Channel and pattern subscription testing

### Adding New Tests
1. Create `test_[feature].py` in root directory
2. Follow existing test class patterns with `test_assert()` method
3. Add to `run_comprehensive_tests.py` test_files list
4. Include basic functionality, edge cases, and error handling tests

## Common Patterns

### Adding New Commands
1. Add command handler to `RedstarCommandProcessor` class
2. Implement RESP protocol response format
3. Use data store methods (`get_string`, `set_string`, etc.)
4. Handle type validation and expiration
5. Add comprehensive tests

### Data Structure Operations
```python
# Use data store methods, not direct structure access
value = self.data_store.get_string(key)  # Correct
# value = self.data_store.data[key]      # Avoid direct access
```

### Thread Safety
```python
with self.lock:
    # All shared data modifications here
    self.data[key] = value
```

### Error Handling
```python
if len(args) < required_args:
    return "-ERR wrong number of arguments for 'COMMAND' command\r\n"
```

## Repository Structure
- **Core data structures**: `core_datastructures/`
- **Server logic**: `redstar_core/`, `redstar_server/`  
- **Commands**: `redstar_commands/`
- **Tests**: `redstar_tests/` and root-level test files
- **Client SDKs**: `client-sdks/[language]/`
- **Entry points**: `main.py`, `redstar_main.py`