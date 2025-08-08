# 🚀 Redstar - Redis Clone Implementation

![Language](https://img.shields.io/badge/Language-Python-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)
![Tests](https://img.shields.io/badge/Tests-Comprehensive-success.svg)

> A complete Redis-compatible server implementation built entirely from scratch in Python, featuring all core data structures, RESP protocol, networking, and Redis-compatible commands without any external dependencies for core functionality.

## ✨ Features

### 🏗️ **Built From Scratch**
- **No External Dependencies**: All core data structures implemented from scratch
- **Custom Dynamic Array**: High-performance auto-resizing array (DArray)
- **Custom Hash Table**: Linear probing collision resolution
- **Custom Linked List**: Doubly-linked list for efficient operations
- **Custom Data Structures**: Sets, deques, and more

### 📡 **Full RESP Protocol Support**
- Complete Redis Serialization Protocol (RESP) implementation
- Compatible with `redis-cli` and other Redis clients
- Support for all RESP data types (Simple Strings, Errors, Integers, Bulk Strings, Arrays)
- Protocol pipelining support

### 💾 **Redis-Compatible Commands**
- **String Operations**: `GET`, `SET`, `DEL`, `EXISTS`, `EXPIRE`, `TTL`, `KEYS`, `INCR`, `DECR`
- **List Operations**: `LPUSH`, `RPUSH`, `LPOP`, `RPOP`, `LLEN`, `LRANGE`
- **Set Operations**: `SADD`, `SREM`, `SMEMBERS`, `SCARD`, `SISMEMBER`
- **Hash Operations**: `HSET`, `HGET`, `HDEL`, `HGETALL`, `HKEYS`, `HVALS`
- **Pub/Sub Operations**: `SUBSCRIBE`, `UNSUBSCRIBE`, `PSUBSCRIBE`, `PUNSUBSCRIBE`, `PUBLISH`, `PUBSUB`
- **Server Operations**: `PING`, `INFO`, `FLUSHALL`

### 🔄 **Advanced Pub/Sub System**
- **Channel Subscriptions**: Direct channel-to-subscriber messaging
- **Pattern Subscriptions**: Wildcard pattern matching for channels
- **Multiple Subscribers**: Concurrent subscriptions to the same channel
- **Message Delivery**: Automatic routing and delivery
- **Client Isolation**: Independent subscription state per client

### 🧵 **Thread Safety & Concurrency**
- Thread-safe data operations using `threading.RLock()`
- Concurrent client handling with automatic cleanup
- Atomic operations for counters and shared data
- Graceful client disconnection handling

### ⚡ **Performance & Reliability**
- Automatic key expiration and memory management
- Efficient data structure operations
- High-performance networking with threading
- Graceful shutdown with signal handlers (Ctrl+C support)

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ (no additional dependencies required)

### Installation & Running

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd redstar
   ```

2. **Start the Server**
   ```bash
   python redstar_main.py
   # or
   python main.py
   ```

3. **Connect with Redis CLI**
   ```bash
   redis-cli -h 127.0.0.1 -p 6379
   ```

4. **Run Tests**
   ```bash
   # In another terminal
   python main.py test
   # or run comprehensive tests
   python run_comprehensive_tests.py
   ```

### Basic Usage Examples

```bash
# Connect with redis-cli
redis-cli -p 6379

# String operations
127.0.0.1:6379> SET mykey "Hello World"
OK
127.0.0.1:6379> GET mykey
"Hello World"
127.0.0.1:6379> INCR counter
(integer) 1

# List operations
127.0.0.1:6379> LPUSH mylist "item1" "item2"
(integer) 2
127.0.0.1:6379> LRANGE mylist 0 -1
1) "item2"
2) "item1"

# Hash operations
127.0.0.1:6379> HSET user:1 name "Alice" age 30
(integer) 2
127.0.0.1:6379> HGETALL user:1
1) "name"
2) "Alice"
3) "age"
4) "30"

# Pub/Sub
127.0.0.1:6379> SUBSCRIBE news
Reading messages...
# In another terminal:
127.0.0.1:6379> PUBLISH news "Breaking news!"
```

## 📁 Project Structure

```
redstar/
├── core_datastructures/          # Custom data structures
│   ├── dynamic_array.py         # Auto-resizing array (DArray)
│   ├── linked_list.py           # Doubly-linked list
│   ├── hash_table.py            # Hash table with linear probing
│   ├── hashset.py               # Set implementation
│   ├── deque.py                 # Double-ended queue
│   └── ...                      # Additional structures
├── redstar_core/                 # Core Redstar implementation
│   ├── redstar_protocol.py      # RESP protocol parser
│   ├── redstar_value.py         # Value wrapper with expiration
│   ├── redstar_datastore.py     # Thread-safe data storage
│   └── pubsub_manager.py        # Pub/Sub messaging system
├── redstar_commands/             # Command processing
│   ├── command_processor.py     # Redis-compatible commands
│   ├── pubsub_commands.py       # Pub/Sub command implementations
│   ├── datatype_commands.py     # Data type specific commands
│   └── advanced_commands.py     # Advanced operations
├── redstar_server/               # Server implementation
│   ├── redstar_server.py        # Main server with networking
│   └── client_handler.py        # Client connection handler
├── redstar_client/               # Client implementation
│   └── redstar_client.py        # Simple test client
├── tests/                        # Comprehensive test suite
│   ├── test_hash_operations.py  # Hash operations testing
│   ├── test_pubsub_advanced.py  # Advanced pub/sub testing
│   ├── test_concurrency.py      # Thread safety testing
│   ├── test_protocol_compliance.py # RESP protocol testing
│   └── run_comprehensive_tests.py # Master test runner
├── main.py                       # Entry point
├── redstar_main.py              # Alternative entry point
├── CLAUDE.md                     # Development documentation
└── README.md                     # This file
```

## 🧪 Testing

### Comprehensive Test Suite

The project includes an extensive test suite covering:

- **Hash Operations**: All hash commands, type conflicts, edge cases
- **Pub/Sub System**: Channel subscriptions, pattern matching, multi-client scenarios
- **Server Operations**: PING, INFO, FLUSHALL, connection handling
- **Edge Cases**: Protocol errors, malformed commands, Unicode/binary data
- **Concurrency**: Multi-client scenarios, thread safety, atomic operations
- **Protocol Compliance**: Full RESP protocol validation, redis-cli compatibility

### Running Tests

```bash
# Run all tests
python run_comprehensive_tests.py

# Run specific test suites
python test_hash_operations.py
python test_pubsub_advanced.py
python test_concurrency.py
python test_protocol_compliance.py
python test_edge_cases.py
python test_server_operations.py

# Run built-in test suite
python main.py test
```

### Test Results Example

```
🧪 COMPREHENSIVE TEST RESULTS SUMMARY
================================================================================
⏱️  Total Duration: 45.23 seconds
📦 Test Suites: 6/6 passed
🧪 Individual Tests: 127/127 passed
📈 Overall Success Rate: 100.0%

✅ PASS Hash Operations        (23/23 tests, 100.0%)
✅ PASS Pub/Sub Advanced       (18/18 tests, 100.0%)
✅ PASS Server Operations      (22/22 tests, 100.0%)
✅ PASS Edge Cases            (25/25 tests, 100.0%)
✅ PASS Concurrency           (19/19 tests, 100.0%)
✅ PASS Protocol Compliance   (20/20 tests, 100.0%)

🎉 ALL TEST SUITES PASSED! 🎉
```

## 🏗️ Architecture

### Data Structure Design

The project uses custom implementations throughout:

- **DArray**: Custom dynamic array used instead of Python lists
- **Consistent API**: All data structures return DArray instances
- **Memory Efficient**: Optimized for Redis-like workloads
- **Thread Safe**: Proper locking mechanisms for concurrent access

### Protocol Implementation

- **Complete RESP Support**: All Redis protocol types supported
- **Error Handling**: Proper error responses for invalid commands
- **Performance Optimized**: Efficient parsing and response generation
- **Client Compatible**: Works with standard Redis clients

### Concurrency Model

- **Multi-threaded**: Each client connection handled in separate thread
- **Thread Safety**: RLock-based synchronization for data operations
- **Graceful Shutdown**: Signal handlers for clean server termination
- **Resource Management**: Automatic cleanup of finished threads

## ⚙️ Configuration

### Server Configuration

```python
# Default configuration
HOST = '127.0.0.1'        # Server bind address
PORT = 6379               # Server port (Redis compatible)
MAX_CONNECTIONS = 1000    # Maximum concurrent connections
SOCKET_TIMEOUT = 1.0      # Socket timeout for signal handling
```

### Command Line Options

```bash
python main.py              # Start server
python main.py test         # Run test suite
python main.py tutorial     # Show tutorial
python main.py help         # Show help
```

## 🚦 Performance

### Benchmarks

The server is designed for educational purposes but includes performance optimizations:

- **High Throughput**: Capable of thousands of operations per second
- **Low Latency**: Efficient data structure operations
- **Memory Efficient**: Custom data structures optimized for Redis workloads
- **Concurrent Safe**: Thread-safe operations with minimal locking overhead

### Performance Testing

```bash
# Run performance tests
python test_concurrency.py

# Example output:
# 🚀 5000 operations in 2.34s = 2137.6 ops/sec
# 💪 12 errors (0.24%)
```

## 🔧 Development

### Adding New Commands

1. Implement the command in `redstar_commands/command_processor.py`
2. Add any new data structures to `core_datastructures/`
3. Update the protocol handler if needed
4. Add comprehensive tests

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Code style and conventions
- Testing requirements
- Pull request process
- Development setup

## 📖 Educational Value

This project serves as an excellent educational resource for understanding:

- **Database Internals**: How Redis-like databases work internally
- **Network Programming**: Server-client architecture and protocol design
- **Data Structures**: Implementation of fundamental computer science data structures
- **Concurrency**: Thread-safe programming and concurrent system design
- **Protocol Design**: How network protocols like RESP are implemented
- **Testing**: Comprehensive testing strategies for distributed systems

## 🐛 Known Limitations

- **Performance**: Built for education, not production performance
- **Memory**: No persistent storage (in-memory only)
- **Clustering**: No cluster support
- **Advanced Features**: Some advanced Redis features not implemented
- **Production Use**: Not intended for production deployments

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Redis Team**: For the amazing Redis database and RESP protocol
- **Educational Purpose**: This implementation is for learning and understanding Redis internals
- **Community**: Thanks to all contributors and testers

## 📞 Support

- **Issues**: Report bugs and issues on GitHub
- **Questions**: Ask questions in GitHub Discussions
- **Documentation**: Check CLAUDE.md for development details

---

**Note**: This is an educational implementation of Redis. For production use, please use the official Redis server.