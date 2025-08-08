# Redstar Python Client SDK

A comprehensive Python client library for connecting to Redstar Redis-compatible servers.

## Features

- **Full Redis Command Support**: Strings, Lists, Sets, Hashes, Pub/Sub
- **Thread-Safe Operations**: Safe for concurrent use
- **Auto-Reconnection**: Automatic reconnection with configurable retries
- **Pub/Sub Support**: Subscribe to channels and patterns with callbacks
- **Context Manager**: Easy resource management with `with` statements
- **Type Hints**: Full type annotation support
- **Zero Dependencies**: No external dependencies required

## Installation

```bash
pip install redstar-client
```

Or install from source:

```bash
git clone <repository-url>
cd client-sdks/python
pip install -e .
```

## Quick Start

```python
from redstar_client import RedstarClient

# Basic usage with context manager
with RedstarClient(host='localhost', port=6379) as client:
    # String operations
    client.set('hello', 'world')
    value = client.get('hello')
    print(f"Value: {value}")
    
    # List operations
    client.lpush('mylist', 'item1', 'item2')
    items = client.lrange('mylist', 0, -1)
    print(f"List: {items}")
    
    # Hash operations
    client.hset('user:1', 'name', 'Alice')
    user = client.hgetall('user:1')
    print(f"User: {user}")
```

## API Reference

### Connection Management

```python
# Initialize client
client = RedstarClient(
    host='localhost',
    port=6379,
    timeout=30,
    auto_reconnect=True,
    max_retries=3
)

# Manual connection management
client.connect()
client.disconnect()

# Context manager (recommended)
with RedstarClient() as client:
    # operations here
    pass
```

### String Operations

```python
client.set('key', 'value')           # Set key-value
value = client.get('key')            # Get value
count = client.delete('key1', 'key2') # Delete keys
exists = client.exists('key')        # Check existence
client.expire('key', 60)             # Set expiration
ttl = client.ttl('key')              # Get TTL
client.incr('counter')               # Increment
client.decr('counter')               # Decrement
```

### List Operations

```python
client.lpush('list', 'item1', 'item2')  # Push left
client.rpush('list', 'item3')           # Push right
item = client.lpop('list')              # Pop left
item = client.rpop('list')              # Pop right
length = client.llen('list')            # Get length
items = client.lrange('list', 0, -1)    # Get range
```

### Set Operations

```python
client.sadd('set', 'member1', 'member2') # Add members
client.srem('set', 'member1')            # Remove members
members = client.smembers('set')         # Get all members
count = client.scard('set')              # Get cardinality
is_member = client.sismember('set', 'member1') # Check membership
```

### Hash Operations

```python
client.hset('hash', 'field', 'value')   # Set field
value = client.hget('hash', 'field')    # Get field
client.hdel('hash', 'field1', 'field2') # Delete fields
hash_data = client.hgetall('hash')      # Get all fields
fields = client.hkeys('hash')           # Get field names
values = client.hvals('hash')           # Get values
```

### Pub/Sub Operations

```python
# Define callback function
def message_handler(channel, message):
    print(f"Received on {channel}: {message}")

# Subscribe to channels
client.subscribe('news', callback=message_handler)
client.psubscribe('news.*', callback=message_handler)

# Publish messages
subscribers = client.publish('news', 'Breaking news!')

# Unsubscribe
client.unsubscribe('news')
client.punsubscribe('news.*')
```

### Server Operations

```python
response = client.ping()             # Ping server
response = client.ping('hello')      # Ping with message
info = client.info()                 # Get server info
client.flushall()                    # Clear all data
keys = client.keys('pattern*')       # Get matching keys
```

## Error Handling

```python
from redstar_client import RedstarClient, RedstarConnectionError, RedstarCommandError

try:
    with RedstarClient() as client:
        client.set('key', 'value')
except RedstarConnectionError as e:
    print(f"Connection error: {e}")
except RedstarCommandError as e:
    print(f"Command error: {e}")
```

## Advanced Usage

### Custom Configuration

```python
client = RedstarClient(
    host='redis-server.example.com',
    port=6379,
    timeout=10,
    auto_reconnect=True,
    max_retries=5
)
```

### Pub/Sub with Multiple Channels

```python
def news_handler(channel, message):
    print(f"News: {message}")

def alerts_handler(channel, message):
    print(f"Alert: {message}")

with RedstarClient() as client:
    client.subscribe('news', callback=news_handler)
    client.subscribe('alerts', callback=alerts_handler)
    client.psubscribe('system.*', callback=alerts_handler)
    
    # Keep alive for pub/sub
    import time
    time.sleep(60)
```

### Convenience Functions

```python
from redstar_client import quick_set, quick_get

# Quick operations without managing connections
quick_set('temp_key', 'temp_value')
value = quick_get('temp_key')
```

## Examples

### Basic Data Operations

```python
with RedstarClient() as client:
    # Counter example
    client.set('page_views', '0')
    for _ in range(10):
        views = client.incr('page_views')
    print(f"Total views: {views}")
    
    # Shopping cart example
    client.hset('cart:123', 'item1', '2')
    client.hset('cart:123', 'item2', '1')
    cart = client.hgetall('cart:123')
    print(f"Cart contents: {cart}")
```

### Pub/Sub Chat Example

```python
import threading
import time

def chat_handler(channel, message):
    print(f"[{channel}] {message}")

# Subscriber
with RedstarClient() as subscriber:
    subscriber.subscribe('chat', callback=chat_handler)
    
    # Publisher in separate thread
    def publish_messages():
        with RedstarClient() as publisher:
            for i in range(5):
                publisher.publish('chat', f"Message {i+1}")
                time.sleep(1)
    
    threading.Thread(target=publish_messages).start()
    time.sleep(10)  # Listen for messages
```

## Testing

```python
# Run tests
python -m pytest tests/

# With coverage
python -m pytest --cov=redstar_client tests/
```

## Requirements

- Python 3.7+
- No external dependencies

## License

MIT License - see LICENSE file for details.