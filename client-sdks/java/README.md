# Redstar Java Client SDK

A comprehensive Java client library for connecting to Redstar Redis-compatible servers.

## Features

- **Full Redis Command Support**: Strings, Lists, Sets, Hashes, Pub/Sub
- **Thread-Safe Operations**: Safe for concurrent use across multiple threads
- **Auto-Reconnection**: Automatic reconnection with configurable retries
- **Pub/Sub Support**: Subscribe to channels and patterns with callbacks
- **Connection Management**: Automatic resource management with try-with-resources
- **Java 8+ Compatible**: Works with Java 8 and above
- **Zero Dependencies**: No external runtime dependencies

## Installation

### Maven

Add to your `pom.xml`:

```xml
<dependency>
    <groupId>com.redstar</groupId>
    <artifactId>redstar-client</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Gradle

Add to your `build.gradle`:

```gradle
implementation 'com.redstar:redstar-client:1.0.0'
```

### Manual Installation

1. Download the JAR from releases
2. Add to your classpath
3. Import in your Java code

## Quick Start

```java
import com.redstar.client.RedstarClient;
import java.util.List;
import java.util.Map;

public class RedstarExample {
    public static void main(String[] args) {
        // Using try-with-resources for automatic connection management
        try (RedstarClient client = new RedstarClient("localhost", 6379)) {
            client.connect();
            
            // String operations
            client.set("hello", "world");
            String value = client.get("hello");
            System.out.println("Value: " + value);
            
            // List operations
            client.lpush("mylist", "item1", "item2");
            List<String> items = client.lrange("mylist", 0, -1);
            System.out.println("List: " + items);
            
            // Hash operations
            client.hset("user:1", "name", "Alice");
            client.hset("user:1", "age", "30");
            Map<String, String> user = client.hgetall("user:1");
            System.out.println("User: " + user);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

## API Reference

### Connection Management

```java
// Create client with default settings (localhost:6379)
RedstarClient client = new RedstarClient();

// Create client with custom host/port
RedstarClient client = new RedstarClient("redis-server.com", 6379);

// Create client with full configuration
RedstarClient client = new RedstarClient(
    "localhost",  // host
    6379,         // port
    30000,        // timeout (ms)
    true,         // auto reconnect
    3             // max retries
);

// Connect and disconnect
client.connect();
client.disconnect();

// Use try-with-resources (recommended)
try (RedstarClient client = new RedstarClient()) {
    client.connect();
    // operations here
} // automatically closed
```

### String Operations

```java
client.set("key", "value");           // Set key-value
String value = client.get("key");     // Get value
int count = client.delete("key1", "key2"); // Delete keys
int exists = client.exists("key");    // Check existence
client.expire("key", 60);             // Set expiration (seconds)
int ttl = client.ttl("key");          // Get TTL
int newValue = client.incr("counter"); // Increment
int newValue = client.decr("counter"); // Decrement
```

### List Operations

```java
int length = client.lpush("list", "item1", "item2"); // Push left
int length = client.rpush("list", "item3");          // Push right
String item = client.lpop("list");                   // Pop left
String item = client.rpop("list");                   // Pop right
int length = client.llen("list");                    // Get length
List<String> items = client.lrange("list", 0, -1);   // Get range
```

### Set Operations

```java
int added = client.sadd("set", "member1", "member2"); // Add members
int removed = client.srem("set", "member1");          // Remove members
List<String> members = client.smembers("set");        // Get all members
int count = client.scard("set");                      // Get cardinality
int isMember = client.sismember("set", "member1");    // Check membership
```

### Hash Operations

```java
int added = client.hset("hash", "field", "value");   // Set field
String value = client.hget("hash", "field");         // Get field
int deleted = client.hdel("hash", "field1", "field2"); // Delete fields
Map<String, String> hash = client.hgetall("hash");   // Get all fields
List<String> fields = client.hkeys("hash");          // Get field names
List<String> values = client.hvals("hash");          // Get values
```

### Pub/Sub Operations

```java
// Define callback
BiConsumer<String, String> callback = (channel, message) -> {
    System.out.println("Received on " + channel + ": " + message);
};

// Subscribe to channels
client.subscribe("news", callback);
client.psubscribe("news.*", callback);

// Publish messages
int subscribers = client.publish("news", "Breaking news!");

// Unsubscribe
client.unsubscribe("news");
client.punsubscribe("news.*");
```

### Server Operations

```java
String response = client.ping();           // Ping server
String response = client.ping("hello");    // Ping with message
String info = client.info();               // Get server info
String result = client.flushall();         // Clear all data
List<String> keys = client.keys("pattern*"); // Get matching keys
```

## Error Handling

The client throws specific exceptions for different types of errors:

```java
import com.redstar.client.RedstarClient.*;

try (RedstarClient client = new RedstarClient()) {
    client.connect();
    client.set("key", "value");
} catch (RedstarConnectionException e) {
    System.err.println("Connection error: " + e.getMessage());
} catch (RedstarCommandException e) {
    System.err.println("Command error: " + e.getMessage());
} catch (RedstarException e) {
    System.err.println("General error: " + e.getMessage());
}
```

## Advanced Usage

### Connection Configuration

```java
RedstarClient client = new RedstarClient(
    "redis-cluster.example.com",  // host
    6379,                         // port
    10000,                        // 10 second timeout
    true,                         // auto reconnect enabled
    5                             // max 5 retry attempts
);
```

### Pub/Sub Example

```java
public class PubSubExample {
    public static void main(String[] args) throws Exception {
        // Subscriber
        try (RedstarClient subscriber = new RedstarClient()) {
            subscriber.connect();
            
            // Subscribe with callback
            subscriber.subscribe("chat", (channel, message) -> {
                System.out.println("[" + channel + "] " + message);
            });
            
            // Publisher in separate thread
            new Thread(() -> {
                try (RedstarClient publisher = new RedstarClient()) {
                    publisher.connect();
                    
                    for (int i = 1; i <= 5; i++) {
                        publisher.publish("chat", "Message " + i);
                        Thread.sleep(1000);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }).start();
            
            // Keep subscriber alive
            Thread.sleep(10000);
        }
    }
}
```

### Batch Operations

```java
try (RedstarClient client = new RedstarClient()) {
    client.connect();
    
    // Batch string operations
    for (int i = 0; i < 1000; i++) {
        client.set("key:" + i, "value:" + i);
    }
    
    // Batch list operations
    String[] items = {"item1", "item2", "item3", "item4"};
    client.lpush("batch_list", items);
    
    // Batch set operations
    client.sadd("batch_set", "member1", "member2", "member3");
}
```

### Connection Pool Example

```java
import java.util.concurrent.ConcurrentLinkedQueue;

public class RedstarConnectionPool {
    private final ConcurrentLinkedQueue<RedstarClient> pool = new ConcurrentLinkedQueue<>();
    private final String host;
    private final int port;
    private final int maxConnections;
    
    public RedstarConnectionPool(String host, int port, int maxConnections) {
        this.host = host;
        this.port = port;
        this.maxConnections = maxConnections;
        
        // Pre-populate pool
        for (int i = 0; i < maxConnections; i++) {
            try {
                RedstarClient client = new RedstarClient(host, port);
                client.connect();
                pool.offer(client);
            } catch (Exception e) {
                // Handle connection errors
            }
        }
    }
    
    public RedstarClient getConnection() {
        return pool.poll();
    }
    
    public void returnConnection(RedstarClient client) {
        if (client != null) {
            pool.offer(client);
        }
    }
    
    public void close() {
        RedstarClient client;
        while ((client = pool.poll()) != null) {
            client.disconnect();
        }
    }
}
```

## Building from Source

```bash
# Clone repository
git clone <repository-url>
cd client-sdks/java

# Build with Maven
mvn clean compile

# Run tests
mvn test

# Create JAR
mvn package

# Install to local repository
mvn install
```

## Testing

```bash
# Run all tests
mvn test

# Run with coverage
mvn clean test jacoco:report

# Run specific test
mvn test -Dtest=RedstarClientTest
```

## Requirements

- **Java**: 8 or higher
- **Maven**: 3.6+ (for building)
- **Redstar Server**: Running instance for connections

## Performance Considerations

- **Connection Reuse**: Reuse client instances when possible
- **Connection Pooling**: Use connection pooling for high-throughput applications
- **Batch Operations**: Use batch methods for multiple operations
- **Async Operations**: Consider using separate threads for pub/sub

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check JavaDoc for detailed API documentation
- **Examples**: See examples directory for more usage patterns