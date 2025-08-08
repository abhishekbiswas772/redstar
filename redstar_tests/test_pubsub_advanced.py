#!/usr/bin/env python3
"""
Advanced Pub/Sub test suite with pattern matching and multi-client scenarios
Tests SUBSCRIBE, PUBLISH, PSUBSCRIBE, PUNSUBSCRIBE, pattern matching
"""

import socket
import threading
import time
import sys
import queue

class PubSubClient:
    def __init__(self, name, host='127.0.0.1', port=6379):
        self.name = name
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.received_messages = queue.Queue()
        self.listener_thread = None
    
    def connect(self):
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_for_messages)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            return True
        except Exception as e:
            print(f"❌ {self.name} failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.listener_thread:
            self.listener_thread.join(timeout=1)
    
    def send_command(self, command):
        """Send command to server"""
        try:
            self.socket.send(command.encode('utf-8'))
        except Exception as e:
            print(f"❌ {self.name} send error: {e}")
    
    def _listen_for_messages(self):
        """Listen for incoming messages"""
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data
                
                # Parse complete RESP messages
                while True:
                    message, remaining = self._parse_resp_message(buffer)
                    if message is None:
                        break
                    buffer = remaining
                    self.received_messages.put(message)
                    
            except Exception as e:
                if self.running:
                    print(f"❌ {self.name} listen error: {e}")
                break
    
    def _parse_resp_message(self, buffer):
        """Parse a single RESP message from buffer"""
        if not buffer:
            return None, buffer
            
        lines = buffer.split('\r\n')
        if len(lines) < 2:
            return None, buffer
            
        # Handle arrays (pub/sub messages)
        if buffer.startswith('*'):
            try:
                array_len = int(lines[0][1:])
                needed_elements = array_len * 2  # Each element needs type + data line
                
                if len(lines) < 1 + needed_elements + 1:  # +1 for final empty line
                    return None, buffer
                
                elements = []
                line_idx = 1
                for _ in range(array_len):
                    if line_idx >= len(lines):
                        return None, buffer
                    
                    elem_type = lines[line_idx]
                    if elem_type.startswith('$'):
                        # Bulk string
                        length = int(elem_type[1:])
                        line_idx += 1
                        if line_idx >= len(lines):
                            return None, buffer
                        elements.append(lines[line_idx])
                    elif elem_type.startswith(':'):
                        # Integer
                        elements.append(int(elem_type[1:]))
                    else:
                        elements.append(lines[line_idx])
                    line_idx += 1
                
                # Calculate consumed bytes
                consumed_lines = 1 + needed_elements + 1
                consumed = '\r\n'.join(lines[:consumed_lines]) + '\r\n'
                remaining = buffer[len(consumed):]
                
                return elements, remaining
                
            except (ValueError, IndexError):
                return None, buffer
        
        return None, buffer
    
    def get_message(self, timeout=1):
        """Get a message from the queue"""
        try:
            return self.received_messages.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def subscribe(self, channel):
        """Subscribe to a channel"""
        self.send_command(f"*2\r\n$9\r\nSUBSCRIBE\r\n${len(channel)}\r\n{channel}\r\n")
    
    def psubscribe(self, pattern):
        """Subscribe to a pattern"""
        self.send_command(f"*2\r\n$10\r\nPSUBSCRIBE\r\n${len(pattern)}\r\n{pattern}\r\n")
    
    def unsubscribe(self, channel):
        """Unsubscribe from a channel"""
        self.send_command(f"*2\r\n$11\r\nUNSUBSCRIBE\r\n${len(channel)}\r\n{channel}\r\n")
    
    def punsubscribe(self, pattern):
        """Unsubscribe from a pattern"""
        self.send_command(f"*2\r\n$12\r\nPUNSUBSCRIBE\r\n${len(pattern)}\r\n{pattern}\r\n")
    
    def publish(self, channel, message):
        """Publish a message to a channel"""
        self.send_command(f"*3\r\n$7\r\nPUBLISH\r\n${len(channel)}\r\n{channel}\r\n${len(message)}\r\n{message}\r\n")

class PubSubTester:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test_assert(self, condition, test_name, expected=None, actual=None):
        """Assert test condition and track results"""
        if condition:
            print(f"✅ {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ {test_name}")
            if expected is not None and actual is not None:
                print(f"   Expected: {expected}")
                print(f"   Actual: {actual}")
            self.tests_failed += 1
    
    def test_basic_pubsub(self):
        """Test basic publish/subscribe functionality"""
        print("\n=== Testing Basic Pub/Sub ===")
        
        subscriber = PubSubClient("Subscriber")
        publisher = PubSubClient("Publisher")
        
        if not subscriber.connect() or not publisher.connect():
            self.test_assert(False, "Connect clients for basic pub/sub")
            return
        
        try:
            # Subscribe to channel
            subscriber.subscribe("news")
            time.sleep(0.1)
            
            # Check subscription confirmation
            msg = subscriber.get_message()
            self.test_assert(msg is not None and "subscribe" in str(msg).lower(), "Subscription confirmation")
            
            # Publish message
            publisher.publish("news", "Breaking news!")
            time.sleep(0.1)
            
            # Check received message
            msg = subscriber.get_message()
            self.test_assert(msg is not None and "Breaking news!" in str(msg), "Received published message")
            
            # Publish to different channel (should not receive)
            publisher.publish("sports", "Goal scored!")
            time.sleep(0.1)
            
            msg = subscriber.get_message(timeout=0.5)
            self.test_assert(msg is None, "No message from unsubscribed channel")
            
        finally:
            subscriber.disconnect()
            publisher.disconnect()
    
    def test_pattern_subscription(self):
        """Test pattern-based subscriptions"""
        print("\n=== Testing Pattern Subscriptions ===")
        
        subscriber = PubSubClient("PatternSubscriber")
        publisher = PubSubClient("PatternPublisher")
        
        if not subscriber.connect() or not publisher.connect():
            self.test_assert(False, "Connect clients for pattern subscription")
            return
        
        try:
            # Subscribe to pattern
            subscriber.psubscribe("news.*")
            time.sleep(0.1)
            
            # Check subscription confirmation
            msg = subscriber.get_message()
            self.test_assert(msg is not None and "psubscribe" in str(msg).lower(), "Pattern subscription confirmation")
            
            # Publish to matching channels
            publisher.publish("news.sports", "Sports update")
            time.sleep(0.1)
            msg = subscriber.get_message()
            self.test_assert(msg is not None and "Sports update" in str(msg), "Pattern match: news.sports")
            
            publisher.publish("news.weather", "Weather update")
            time.sleep(0.1)
            msg = subscriber.get_message()
            self.test_assert(msg is not None and "Weather update" in str(msg), "Pattern match: news.weather")
            
            # Publish to non-matching channel
            publisher.publish("entertainment", "Movie news")
            time.sleep(0.1)
            msg = subscriber.get_message(timeout=0.5)
            self.test_assert(msg is None, "No message from non-matching pattern")
            
            # Test wildcard pattern
            subscriber.psubscribe("*.important")
            time.sleep(0.1)
            subscriber.get_message()  # Consume subscription confirmation
            
            publisher.publish("system.important", "System alert")
            time.sleep(0.1)
            msg = subscriber.get_message()
            self.test_assert(msg is not None and "System alert" in str(msg), "Wildcard pattern match")
            
        finally:
            subscriber.disconnect()
            publisher.disconnect()
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same channel"""
        print("\n=== Testing Multiple Subscribers ===")
        
        sub1 = PubSubClient("Subscriber1")
        sub2 = PubSubClient("Subscriber2")
        sub3 = PubSubClient("Subscriber3")
        publisher = PubSubClient("MultiPublisher")
        
        clients = [sub1, sub2, sub3, publisher]
        connected = all(client.connect() for client in clients)
        
        if not connected:
            self.test_assert(False, "Connect multiple clients")
            return
        
        try:
            # All subscribe to same channel
            for sub in [sub1, sub2, sub3]:
                sub.subscribe("broadcast")
                time.sleep(0.05)
                sub.get_message()  # Consume subscription confirmation
            
            # Publish message
            publisher.publish("broadcast", "Hello everyone!")
            time.sleep(0.2)
            
            # All subscribers should receive the message
            received_count = 0
            for i, sub in enumerate([sub1, sub2, sub3], 1):
                msg = sub.get_message()
                if msg is not None and "Hello everyone!" in str(msg):
                    received_count += 1
                    print(f"   Subscriber{i} received message")
            
            self.test_assert(received_count == 3, f"All 3 subscribers received message", 3, received_count)
            
        finally:
            for client in clients:
                client.disconnect()
    
    def test_unsubscribe_operations(self):
        """Test unsubscribe functionality"""
        print("\n=== Testing Unsubscribe Operations ===")
        
        subscriber = PubSubClient("UnsubTest")
        publisher = PubSubClient("UnsubPublisher")
        
        if not subscriber.connect() or not publisher.connect():
            self.test_assert(False, "Connect clients for unsubscribe test")
            return
        
        try:
            # Subscribe to multiple channels
            subscriber.subscribe("channel1")
            subscriber.subscribe("channel2")
            time.sleep(0.1)
            subscriber.get_message()  # Consume confirmations
            subscriber.get_message()
            
            # Unsubscribe from one channel
            subscriber.unsubscribe("channel1")
            time.sleep(0.1)
            msg = subscriber.get_message()
            self.test_assert(msg is not None and "unsubscribe" in str(msg).lower(), "Unsubscribe confirmation")
            
            # Publish to both channels
            publisher.publish("channel1", "Message 1")
            publisher.publish("channel2", "Message 2")
            time.sleep(0.1)
            
            # Should only receive from channel2
            msg = subscriber.get_message()
            self.test_assert(msg is not None and "Message 2" in str(msg), "Receive from subscribed channel only")
            
            # Should not receive from channel1
            msg = subscriber.get_message(timeout=0.5)
            if msg is not None and "Message 1" in str(msg):
                self.test_assert(False, "Should not receive from unsubscribed channel")
            else:
                self.test_assert(True, "No message from unsubscribed channel")
            
            # Test pattern unsubscribe
            subscriber.psubscribe("test.*")
            time.sleep(0.1)
            subscriber.get_message()  # Consume confirmation
            
            publisher.publish("test.alpha", "Pattern message")
            time.sleep(0.1)
            msg = subscriber.get_message()
            self.test_assert(msg is not None and "Pattern message" in str(msg), "Receive pattern message")
            
            subscriber.punsubscribe("test.*")
            time.sleep(0.1)
            subscriber.get_message()  # Consume unsubscribe confirmation
            
            publisher.publish("test.beta", "Should not receive")
            time.sleep(0.1)
            msg = subscriber.get_message(timeout=0.5)
            self.test_assert(msg is None, "No message after pattern unsubscribe")
            
        finally:
            subscriber.disconnect()
            publisher.disconnect()
    
    def test_pubsub_edge_cases(self):
        """Test pub/sub edge cases"""
        print("\n=== Testing Pub/Sub Edge Cases ===")
        
        client = PubSubClient("EdgeTest")
        
        if not client.connect():
            self.test_assert(False, "Connect client for edge case testing")
            return
        
        try:
            # Empty message
            client.subscribe("empty")
            time.sleep(0.1)
            client.get_message()  # Consume subscription
            
            client.publish("empty", "")
            time.sleep(0.1)
            msg = client.get_message()
            self.test_assert(msg is not None, "Publish/receive empty message")
            
            # Very long message
            long_message = "x" * 10000
            client.publish("empty", long_message)
            time.sleep(0.1)
            msg = client.get_message()
            self.test_assert(msg is not None and long_message in str(msg), "Publish/receive long message")
            
            # Special characters in channel name
            special_channel = "test:channel-name_with.special"
            client.subscribe(special_channel)
            time.sleep(0.1)
            client.get_message()  # Consume subscription
            
            client.publish(special_channel, "Special channel message")
            time.sleep(0.1)
            msg = client.get_message()
            self.test_assert(msg is not None and "Special channel message" in str(msg), 
                           "Channel with special characters")
            
            # Unicode message
            unicode_message = "Hello 世界 🌍 мир"
            client.publish(special_channel, unicode_message)
            time.sleep(0.1)
            msg = client.get_message()
            self.test_assert(msg is not None and "世界" in str(msg), "Unicode message support")
            
        finally:
            client.disconnect()
    
    def run_all_tests(self):
        """Run all pub/sub tests"""
        print("🔍 Starting Advanced Pub/Sub Test Suite")
        print("=" * 50)
        
        self.test_basic_pubsub()
        self.test_pattern_subscription()
        self.test_multiple_subscribers()
        self.test_unsubscribe_operations()
        self.test_pubsub_edge_cases()
        
        # Print results
        total_tests = self.tests_passed + self.tests_failed
        print(f"\n📊 Pub/Sub Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {self.tests_passed}")
        print(f"   ❌ Failed: {self.tests_failed}")
        print(f"   Success Rate: {(self.tests_passed/total_tests*100):.1f}%")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = PubSubTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)