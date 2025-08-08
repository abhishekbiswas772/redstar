# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Redstar clone implementation (Redis-compatible) built entirely from scratch in Python. The project implements all core data structures, the RESP protocol, networking, and Redis-compatible commands without using any external libraries for the core functionality.

## Key Commands

### Running the Server
```bash
python main.py                    # Start the Redstar server on localhost:6379
python main.py test              # Run comprehensive test suite (requires server to be running)
python main.py tutorial         # Display tutorial summary
python main.py help              # Show usage information
```

### Testing the Implementation
```bash
# Start server in one terminal
python main.py

# Run tests in another terminal  
python main.py test
```

## Architecture Overview

The project is organized into multiple packages for better modularity:

### `core_datastructures/`
Contains all fundamental data structures implemented from scratch:
- **`dynamic_array.py`**: Auto-resizing array with amortized O(1) append operations (DArray)
- **`linked_list.py`**: Doubly-linked list implementation for efficient insertion/deletion
- **`hash_table.py`**: Hash table with linear probing collision resolution
- **`hashset.py`**: Set implementation using the custom hash table
- **`deque.py`**: Double-ended queue built on the linked list for Redstar list operations

### `redstar_core/`
Contains the core Redstar-specific implementation:
- **`redstar_protocol.py`**: Complete RESP (Redis Serialization Protocol) parser with encode/decode functionality
- **`redstar_value.py`**: Value wrapper that handles expiration times and type information
- **`redstar_datastore.py`**: Thread-safe data storage with automatic key expiration
- **`pubsub_manager.py`**: Pub/Sub messaging system with channel and pattern subscriptions

### `redstar_commands/`
Contains the command processing logic:
- **`command_processor.py`**: Command processor with full Redis-compatible command implementations
- **`pubsub_commands.py`**: Pub/Sub command implementations (SUBSCRIBE, PUBLISH, etc.)

### `redstar_server/`
Contains the server implementation:
- **`redstar_server.py`**: Main server implementation with threading and networking
- **`client_handler.py`**: Client connection handler for processing individual client sessions

### `redstar_client/`
Contains the client implementation:
- **`redstar_client.py`**: Simple client for testing the server

### `redstar_tests/`
Contains the test suite:
- **`test_suite.py`**: Comprehensive test suite and tutorial functionality
- **`pubsub_test_suite.py`**: Dedicated pub/sub testing with multi-client scenarios

### `main.py` and `redstar_main.py`
Entry points for starting the server and running tests.

## Data Structure Dependencies

The codebase uses a custom `DArray` (from `dynamic_array.py`) throughout instead of Python's built-in list. When working with this codebase:
- Use `DArray()` instead of `[]` for new arrays
- Use `DArray.append()` for adding items
- All data structures return `DArray` instances for consistency

## Redstar Commands Implemented

**String Operations**: GET, SET, DEL, EXISTS, EXPIRE, TTL, KEYS, INCR, DECR
**List Operations**: LPUSH, RPUSH, LPOP, RPOP, LLEN, LRANGE  
**Set Operations**: SADD, SREM, SMEMBERS, SCARD, SISMEMBER
**Hash Operations**: HSET, HGET, HDEL, HGETALL, HKEYS, HVALS
**Pub/Sub Operations**: SUBSCRIBE, UNSUBSCRIBE, PSUBSCRIBE, PUNSUBSCRIBE, PUBLISH, PUBSUB
**Server Operations**: PING, INFO, FLUSHALL

## Thread Safety

The `RedStarDataSource` class uses threading.RLock() for thread-safe operations. All data access should go through this class to maintain consistency.

The `RedstarPubSubManager` also uses threading.RLock() for thread-safe pub/sub operations, enabling concurrent subscriptions, publications, and message delivery.

## Pub/Sub System

The pub/sub system supports:
- **Channel subscriptions**: Direct channel-to-subscriber messaging
- **Pattern subscriptions**: Wildcard pattern matching for channels  
- **Multiple subscribers**: Many clients can subscribe to the same channel
- **Message delivery**: Automatic routing of published messages to subscribers
- **Introspection**: Commands to inspect active channels and subscription counts
- **Client isolation**: Each client maintains independent subscription state

## Protocol Implementation

The RESP parser handles all Redis protocol types:
- Simple Strings (+)
- Errors (-)  
- Integers (:)
- Bulk Strings ($)
- Arrays (*)

## Development Notes

- The server runs on port 6379 by default (Redis-compatible port)
- All components are built from scratch for educational purposes
- No external dependencies are used for core functionality
- The implementation includes automatic memory management and cleanup
- Signal handlers (SIGINT, SIGTERM) enable graceful shutdown
- Compatible with Redis clients and protocols