# Redstar C++ Client SDK

A comprehensive C++ client library for connecting to Redstar Redis-compatible servers.

## Features

- **Full Redis Command Support**: Strings, Lists, Sets, Hashes, Pub/Sub
- **Modern C++ Design**: C++11/14/17 compatible with RAII principles
- **Thread-Safe Operations**: Safe for concurrent use across multiple threads
- **Cross-Platform**: Works on Windows, Linux, macOS
- **Auto-Reconnection**: Automatic reconnection with configurable retries
- **Pub/Sub Support**: Subscribe to channels and patterns with callbacks
- **Zero Dependencies**: No external runtime dependencies
- **Exception Safety**: Comprehensive error handling with specific exception types

## Requirements

- **C++11** or higher
- **CMake 3.10** or higher
- **Platform-specific**:
  - Windows: Winsock2 (included in Windows SDK)
  - Linux/macOS: POSIX sockets (system libraries)

## Installation

### Building from Source

```bash
# Clone repository
git clone <repository-url>
cd client-sdks/cpp

# Create build directory
mkdir build
cd build

# Configure with CMake
cmake ..

# Build
cmake --build .

# Install (optional)
cmake --install .
```

### CMake Integration

Add to your `CMakeLists.txt`:

```cmake
find_package(RedstarClient REQUIRED)
target_link_libraries(your_target redstar_client)
```

Or as a subdirectory:

```cmake
add_subdirectory(path/to/redstar-cpp-client)
target_link_libraries(your_target redstar_client)
```

## Quick Start

### Basic Usage

```cpp
#include "RedstarClient.h"
#include <iostream>

using namespace redstar;

int main() {
    try {
        // Create and connect client
        RedstarClient client("localhost", 6379);
        client.connect();
        
        // String operations
        client.set("hello", "world");
        std::string value = client.get("hello");
        std::cout << "Value: " << value << std::endl;
        
        // List operations
        client.lpush("mylist", {"item1", "item2"});
        auto items = client.lrange("mylist", 0, -1);
        
        // Hash operations
        client.hset("user:1", "name", "Alice");
        auto user = client.hgetall("user:1");
        
        std::cout << "Success!" << std::endl;
        
    } catch (const RedstarException& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
```

### RAII Resource Management

```cpp
void example() {
    RedstarClient client("localhost", 6379);
    client.connect();
    
    // Client automatically disconnects when going out of scope
    client.set("key", "value");
} // Automatic cleanup here
```

## API Reference

### Connection Management

```cpp
// Constructor options
RedstarClient client();                              // localhost:6379
RedstarClient client("host", 6379);                  // Custom host/port
RedstarClient client("host", 6379, 30000, true, 3);  // Full configuration

// Connection control
client.connect();           // Connect to server
client.disconnect();        // Disconnect from server
bool connected = client.isConnected(); // Check connection status
```

### String Operations

```cpp
client.set("key", "value");                    // Set key-value
std::string value = client.get("key");         // Get value
int deleted = client.del({"key1", "key2"});    // Delete keys
int exists = client.exists({"key"});           // Check existence
int64_t newVal = client.incr("counter");       // Increment
int64_t newVal = client.decr("counter");       // Decrement
int success = client.expire("key", 60);        // Set expiration
int ttl = client.ttl("key");                   // Get TTL
```

### List Operations

```cpp
int64_t len = client.lpush("list", {"item1", "item2"}); // Push left
int64_t len = client.rpush("list", {"item3"});          // Push right
std::string item = client.lpop("list");                 // Pop left
std::string item = client.rpop("list");                 // Pop right
int64_t length = client.llen("list");                   // Get length
auto items = client.lrange("list", 0, -1);              // Get range
```

### Set Operations

```cpp
int64_t added = client.sadd("set", {"member1", "member2"}); // Add members
int64_t removed = client.srem("set", {"member1"});         // Remove members
auto members = client.smembers("set");                     // Get all members
int64_t count = client.scard("set");                       // Get cardinality
int isMember = client.sismember("set", "member1");         // Check membership
```

### Hash Operations

```cpp
int added = client.hset("hash", "field", "value");      // Set field
std::string value = client.hget("hash", "field");       // Get field
int deleted = client.hdel("hash", {"field1", "field2"}); // Delete fields
auto hash = client.hgetall("hash");                     // Get all fields
auto fields = client.hkeys("hash");                     // Get field names
auto values = client.hvals("hash");                     // Get values
```

### Server Operations

```cpp
std::string pong = client.ping();              // Ping server
std::string echo = client.ping("message");     // Ping with message
std::string info = client.info();              // Get server info
std::string ok = client.flushall();            // Clear all data
auto keys = client.keys("pattern*");           // Get matching keys
```

### Pub/Sub Operations

```cpp
// Define callback function
auto callback = [](const std::string& channel, const std::string& message) {
    std::cout << "[" << channel << "] " << message << std::endl;
};

// Subscribe to channels
client.subscribe("news", callback);
client.psubscribe("news.*", callback);

// Publish messages
int64_t subscribers = client.publish("news", "Breaking news!");

// Unsubscribe
client.unsubscribe("news");
client.punsubscribe("news.*");
```

## Error Handling

The client uses a hierarchy of exception types:

```cpp
#include "RedstarClient.h"

try {
    RedstarClient client("localhost", 6379);
    client.connect();
    client.set("key", "value");
    
} catch (const RedstarConnectionException& e) {
    std::cerr << "Connection error: " << e.what() << std::endl;
} catch (const RedstarCommandException& e) {
    std::cerr << "Command error: " << e.what() << std::endl;
} catch (const RedstarException& e) {
    std::cerr << "General error: " << e.what() << std::endl;
}
```

### Exception Types

- **`RedstarException`**: Base exception class
- **`RedstarConnectionException`**: Connection-related errors
- **`RedstarCommandException`**: Command execution errors

## Advanced Usage

### Custom Configuration

```cpp
RedstarClient client(
    "redis-server.example.com",  // host
    6379,                        // port
    10000,                       // timeout (ms)
    true,                        // auto reconnect
    5                            // max retries
);
```

### Pub/Sub Example

```cpp
#include <thread>
#include <chrono>

void pubsubExample() {
    // Subscriber
    RedstarClient subscriber("localhost", 6379);
    subscriber.connect();
    
    // Subscribe with lambda callback
    subscriber.subscribe("chat", [](const std::string& channel, const std::string& msg) {
        std::cout << "[" << channel << "] " << msg << std::endl;
    });
    
    // Publisher in separate thread
    std::thread publisher_thread([&]() {
        RedstarClient publisher("localhost", 6379);
        publisher.connect();
        
        for (int i = 1; i <= 5; i++) {
            publisher.publish("chat", "Message " + std::to_string(i));
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    });
    
    // Keep subscriber alive
    std::this_thread::sleep_for(std::chrono::seconds(10));
    publisher_thread.join();
}
```

### Batch Operations

```cpp
void batchOperations() {
    RedstarClient client;
    client.connect();
    
    // Batch string operations
    for (int i = 0; i < 1000; i++) {
        client.set("key:" + std::to_string(i), "value:" + std::to_string(i));
    }
    
    // Batch list operations
    std::vector<std::string> items = {"item1", "item2", "item3", "item4"};
    client.lpush("batch_list", items);
    
    // Batch set operations
    client.sadd("batch_set", {"member1", "member2", "member3"});
}
```

### Connection Pool Pattern

```cpp
#include <queue>
#include <mutex>

class RedstarConnectionPool {
private:
    std::queue<std::unique_ptr<RedstarClient>> pool_;
    std::mutex mutex_;
    std::string host_;
    int port_;
    size_t max_connections_;
    
public:
    RedstarConnectionPool(const std::string& host, int port, size_t max_conn)
        : host_(host), port_(port), max_connections_(max_conn) {
        
        // Pre-populate pool
        for (size_t i = 0; i < max_connections_; ++i) {
            auto client = std::make_unique<RedstarClient>(host_, port_);
            try {
                client->connect();
                pool_.push(std::move(client));
            } catch (const RedstarException&) {
                // Handle connection errors
            }
        }
    }
    
    std::unique_ptr<RedstarClient> getConnection() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!pool_.empty()) {
            auto client = std::move(pool_.front());
            pool_.pop();
            return client;
        }
        return nullptr;
    }
    
    void returnConnection(std::unique_ptr<RedstarClient> client) {
        if (client && client->isConnected()) {
            std::lock_guard<std::mutex> lock(mutex_);
            pool_.push(std::move(client));
        }
    }
};
```

### Move Semantics

```cpp
// Move construction and assignment supported
RedstarClient createClient() {
    RedstarClient client("localhost", 6379);
    client.connect();
    return client; // Move semantics automatically applied
}

void useClient() {
    auto client = createClient(); // Move construction
    client.set("key", "value");
    
    RedstarClient another_client = std::move(client); // Move assignment
    // 'client' is now in moved-from state, 'another_client' owns the connection
}
```

## Building Examples

```bash
# In build directory
cmake --build . --target redstar_example

# Run example
./redstar_example  # Linux/macOS
.\redstar_example.exe  # Windows
```

## Testing

```bash
# Build tests
cmake --build . --target redstar_test

# Run tests
./redstar_test  # Linux/macOS
.\redstar_test.exe  # Windows
```

## Platform-Specific Notes

### Windows

- Requires Windows SDK with Winsock2
- Automatically links with `ws2_32.lib`
- Supports both Debug and Release configurations

### Linux

- Requires POSIX-compliant system
- Links with pthread library
- Tested on Ubuntu, CentOS, Alpine

### macOS

- Requires macOS 10.12 or later
- Uses system BSD sockets
- Compatible with both Intel and Apple Silicon

## Performance Considerations

- **Connection Reuse**: Keep connections alive for multiple operations
- **Batch Operations**: Use vector parameters for multi-item operations
- **Thread Safety**: Safe for concurrent use across threads
- **Memory Management**: RAII ensures proper cleanup
- **Exception Safety**: Strong exception safety guarantee

## Integration Examples

### With CMake Project

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyRedisApp)

# Find or include Redstar client
find_package(RedstarClient REQUIRED)
# OR: add_subdirectory(redstar-cpp-client)

# Create your application
add_executable(myapp main.cpp)
target_link_libraries(myapp redstar_client)

# Platform-specific linking handled automatically
```

### With pkg-config

```bash
# Compile with pkg-config (if installed)
g++ -std=c++14 main.cpp $(pkg-config --cflags --libs redstar-client) -o myapp
```

## Utility Functions

For simple, one-off operations:

```cpp
#include "RedstarClient.h"

// Quick operations without connection management
std::string result = redstar::utils::quickSet("key", "value");
std::string value = redstar::utils::quickGet("key");
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```cpp
   // Ensure Redstar server is running
   // Check host and port settings
   ```

2. **Timeout Errors**
   ```cpp
   // Increase timeout value
   RedstarClient client("host", 6379, 60000); // 60 second timeout
   ```

3. **Platform-Specific Build Issues**
   ```bash
   # Windows: Ensure Visual Studio or MinGW is properly configured
   # Linux: Install development packages (build-essential, cmake)
   # macOS: Ensure Xcode command line tools are installed
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure cross-platform compatibility
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive API documentation in headers
- **Examples**: See `example.cpp` for usage patterns