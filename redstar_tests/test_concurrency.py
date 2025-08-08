#!/usr/bin/env python3
"""
Concurrency and thread safety test suite
Tests multiple simultaneous clients and thread safety of operations
"""

import socket
import threading
import time
import random
import sys
from queue import Queue

class ConcurrentClient:
    def __init__(self, client_id, host='127.0.0.1', port=6379):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.results = Queue()
        self.errors = []
    
    def connect(self):
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            self.errors.append(f"Client {self.client_id} connect error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            self.socket.close()
        self.connected = False
    
    def send_command(self, command):
        """Send command and get response"""
        try:
            if not self.connected:
                return "ERROR: Not connected"
            
            self.socket.send(command.encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            return response.strip()
        except Exception as e:
            self.errors.append(f"Client {self.client_id} command error: {e}")
            return f"ERROR: {e}"
    
    def perform_operations(self, operation_count=100):
        """Perform a series of operations"""
        operations = []
        
        for i in range(operation_count):
            op_type = random.choice(['set', 'get', 'incr', 'del'])
            key = f"client{self.client_id}_key{i % 20}"  # Reuse keys for contention
            
            if op_type == 'set':
                value = f"value_{self.client_id}_{i}"
                cmd = f"*3\r\n$3\r\nSET\r\n${len(key)}\r\n{key}\r\n${len(value)}\r\n{value}\r\n"
                response = self.send_command(cmd)
                operations.append(('SET', key, response))
            
            elif op_type == 'get':
                cmd = f"*2\r\n$3\r\nGET\r\n${len(key)}\r\n{key}\r\n"
                response = self.send_command(cmd)
                operations.append(('GET', key, response))
            
            elif op_type == 'incr':
                incr_key = f"counter_{self.client_id}_{i % 5}"
                cmd = f"*2\r\n$4\r\nINCR\r\n${len(incr_key)}\r\n{incr_key}\r\n"
                response = self.send_command(cmd)
                operations.append(('INCR', incr_key, response))
            
            elif op_type == 'del':
                cmd = f"*2\r\n$3\r\nDEL\r\n${len(key)}\r\n{key}\r\n"
                response = self.send_command(cmd)
                operations.append(('DEL', key, response))
            
            # Small random delay to create more realistic load
            if random.random() < 0.1:
                time.sleep(0.001)
        
        self.results.put(operations)
        return operations

class ConcurrencyTester:
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
    
    def test_multiple_clients_basic(self):
        """Test multiple clients performing basic operations"""
        print("\n=== Testing Multiple Clients Basic Operations ===")
        
        client_count = 10
        clients = []
        threads = []
        
        # Create and connect clients
        for i in range(client_count):
            client = ConcurrentClient(i)
            if client.connect():
                clients.append(client)
            else:
                print(f"❌ Failed to connect client {i}")
        
        connected_count = len(clients)
        self.test_assert(connected_count >= client_count - 2, f"Most clients connected", f">= {client_count-2}", connected_count)
        
        # Start concurrent operations
        def client_worker(client):
            client.perform_operations(50)
        
        start_time = time.time()
        
        for client in clients:
            thread = threading.Thread(target=client_worker, args=(client,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10)
        
        elapsed_time = time.time() - start_time
        
        # Collect results
        total_operations = 0
        error_count = 0
        
        for client in clients:
            if not client.results.empty():
                operations = client.results.get()
                total_operations += len(operations)
            error_count += len(client.errors)
            client.disconnect()
        
        self.test_assert(total_operations > 0, f"Operations completed", "> 0", total_operations)
        self.test_assert(error_count < total_operations * 0.1, f"Low error rate", "< 10%", f"{error_count}/{total_operations}")
        self.test_assert(elapsed_time < 30, f"Reasonable completion time", "< 30s", f"{elapsed_time:.2f}s")
        
        print(f"   📈 {total_operations} operations completed in {elapsed_time:.2f}s")
        print(f"   📊 {error_count} errors out of {total_operations} operations")
    
    def test_concurrent_counter_increments(self):
        """Test concurrent increments on shared counters"""
        print("\n=== Testing Concurrent Counter Increments ===")
        
        # Clean up first
        cleanup_client = ConcurrentClient(999)
        cleanup_client.connect()
        cleanup_client.send_command("*1\r\n$8\r\nFLUSHALL\r\n")
        cleanup_client.disconnect()
        
        client_count = 5
        increments_per_client = 20
        counter_keys = ["shared_counter1", "shared_counter2"]
        
        clients = []
        threads = []
        
        # Create clients
        for i in range(client_count):
            client = ConcurrentClient(i)
            if client.connect():
                clients.append(client)
        
        def increment_worker(client):
            operations = []
            for _ in range(increments_per_client):
                for counter_key in counter_keys:
                    cmd = f"*2\r\n$4\r\nINCR\r\n${len(counter_key)}\r\n{counter_key}\r\n"
                    response = client.send_command(cmd)
                    operations.append(('INCR', counter_key, response))
            client.results.put(operations)
        
        # Start concurrent increments
        for client in clients:
            thread = threading.Thread(target=increment_worker, args=(client,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)
        
        # Verify final counter values
        check_client = ConcurrentClient(888)
        check_client.connect()
        
        expected_total = len(clients) * increments_per_client
        
        for counter_key in counter_keys:
            cmd = f"*2\r\n$3\r\nGET\r\n${len(counter_key)}\r\n{counter_key}\r\n"
            response = check_client.send_command(cmd)
            
            # Extract number from response
            try:
                if "$" in response and "\r\n" in response:
                    lines = response.split('\r\n')
                    if len(lines) > 1:
                        final_count = int(lines[1])
                    else:
                        final_count = 0
                else:
                    final_count = 0
                
                self.test_assert(final_count == expected_total, 
                               f"Counter {counter_key} atomic increments", expected_total, final_count)
            except (ValueError, IndexError):
                self.test_assert(False, f"Could not parse counter {counter_key} value: {response}")
        
        # Clean up
        for client in clients:
            client.disconnect()
        check_client.disconnect()
    
    def test_concurrent_list_operations(self):
        """Test concurrent list operations"""
        print("\n=== Testing Concurrent List Operations ===")
        
        client_count = 8
        operations_per_client = 25
        list_keys = ["shared_list1", "shared_list2"]
        
        clients = []
        threads = []
        
        # Create clients
        for i in range(client_count):
            client = ConcurrentClient(i)
            if client.connect():
                clients.append(client)
        
        def list_worker(client):
            operations = []
            for i in range(operations_per_client):
                for list_key in list_keys:
                    # Random list operations
                    op = random.choice(['LPUSH', 'RPUSH', 'LPOP', 'RPOP', 'LLEN'])
                    
                    if op in ['LPUSH', 'RPUSH']:
                        value = f"item_{client.client_id}_{i}"
                        cmd = f"*3\r\n${len(op)}\r\n{op}\r\n${len(list_key)}\r\n{list_key}\r\n${len(value)}\r\n{value}\r\n"
                        response = client.send_command(cmd)
                        operations.append((op, list_key, response))
                    
                    elif op in ['LPOP', 'RPOP', 'LLEN']:
                        cmd = f"*2\r\n${len(op)}\r\n{op}\r\n${len(list_key)}\r\n{list_key}\r\n"
                        response = client.send_command(cmd)
                        operations.append((op, list_key, response))
            
            client.results.put(operations)
        
        # Start concurrent list operations
        for client in clients:
            thread = threading.Thread(target=list_worker, args=(client,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=15)
        
        # Check that lists still exist and have reasonable state
        check_client = ConcurrentClient(777)
        check_client.connect()
        
        for list_key in list_keys:
            cmd = f"*2\r\n$4\r\nLLEN\r\n${len(list_key)}\r\n{list_key}\r\n"
            response = check_client.send_command(cmd)
            
            # List should exist (length >= 0)
            self.test_assert(":" in response, f"List {list_key} length query works")
        
        # Clean up
        for client in clients:
            client.disconnect()
        check_client.disconnect()
    
    def test_concurrent_hash_operations(self):
        """Test concurrent hash operations"""
        print("\n=== Testing Concurrent Hash Operations ===")
        
        client_count = 6
        operations_per_client = 30
        hash_keys = ["shared_hash1", "shared_hash2"]
        
        clients = []
        threads = []
        
        # Create clients
        for i in range(client_count):
            client = ConcurrentClient(i)
            if client.connect():
                clients.append(client)
        
        def hash_worker(client):
            operations = []
            for i in range(operations_per_client):
                for hash_key in hash_keys:
                    # Random hash operations
                    op = random.choice(['HSET', 'HGET', 'HDEL', 'HKEYS', 'HGETALL'])
                    field = f"field_{client.client_id}_{i % 10}"
                    
                    if op == 'HSET':
                        value = f"value_{client.client_id}_{i}"
                        cmd = f"*4\r\n$4\r\nHSET\r\n${len(hash_key)}\r\n{hash_key}\r\n${len(field)}\r\n{field}\r\n${len(value)}\r\n{value}\r\n"
                        response = client.send_command(cmd)
                        operations.append((op, hash_key, response))
                    
                    elif op in ['HGET', 'HDEL']:
                        cmd = f"*3\r\n${len(op)}\r\n{op}\r\n${len(hash_key)}\r\n{hash_key}\r\n${len(field)}\r\n{field}\r\n"
                        response = client.send_command(cmd)
                        operations.append((op, hash_key, response))
                    
                    elif op in ['HKEYS', 'HGETALL']:
                        cmd = f"*2\r\n${len(op)}\r\n{op}\r\n${len(hash_key)}\r\n{hash_key}\r\n"
                        response = client.send_command(cmd)
                        operations.append((op, hash_key, response))
            
            client.results.put(operations)
        
        # Start concurrent hash operations
        for client in clients:
            thread = threading.Thread(target=hash_worker, args=(client,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=15)
        
        # Verify hash integrity
        check_client = ConcurrentClient(666)
        check_client.connect()
        
        hash_operations_completed = 0
        for client in clients:
            if not client.results.empty():
                operations = client.results.get()
                hash_operations_completed += len(operations)
        
        self.test_assert(hash_operations_completed > 0, "Hash operations completed", "> 0", hash_operations_completed)
        
        for hash_key in hash_keys:
            cmd = f"*2\r\n$5\r\nHKEYS\r\n${len(hash_key)}\r\n{hash_key}\r\n"
            response = check_client.send_command(cmd)
            
            # Hash should be queryable (even if empty)
            self.test_assert("*" in response, f"Hash {hash_key} structure intact")
        
        # Clean up
        for client in clients:
            client.disconnect()
        check_client.disconnect()
    
    def test_concurrent_pubsub(self):
        """Test concurrent pub/sub operations"""
        print("\n=== Testing Concurrent Pub/Sub ===")
        
        publisher_count = 3
        subscriber_count = 5
        messages_per_publisher = 10
        
        publishers = []
        subscribers = []
        threads = []
        
        # Create publishers
        for i in range(publisher_count):
            client = ConcurrentClient(f"pub_{i}")
            if client.connect():
                publishers.append(client)
        
        # Create subscribers
        for i in range(subscriber_count):
            client = ConcurrentClient(f"sub_{i}")
            if client.connect():
                subscribers.append(client)
        
        channels = ["test_channel1", "test_channel2"]
        
        # Subscribe all subscribers to all channels
        for subscriber in subscribers:
            for channel in channels:
                cmd = f"*2\r\n$9\r\nSUBSCRIBE\r\n${len(channel)}\r\n{channel}\r\n"
                subscriber.send_command(cmd)
        
        time.sleep(0.5)  # Allow subscriptions to register
        
        def publisher_worker(publisher):
            for i in range(messages_per_publisher):
                for channel in channels:
                    message = f"msg_{publisher.client_id}_{i}"
                    cmd = f"*3\r\n$7\r\nPUBLISH\r\n${len(channel)}\r\n{channel}\r\n${len(message)}\r\n{message}\r\n"
                    response = publisher.send_command(cmd)
                time.sleep(0.01)  # Small delay between messages
        
        def subscriber_worker(subscriber):
            received_messages = []
            start_time = time.time()
            while time.time() - start_time < 5:  # Listen for 5 seconds
                try:
                    subscriber.socket.settimeout(0.5)
                    response = subscriber.socket.recv(1024).decode('utf-8')
                    if response and len(response) > 10:
                        received_messages.append(response)
                except:
                    pass
            subscriber.results.put(received_messages)
        
        # Start subscribers listening
        for subscriber in subscribers:
            thread = threading.Thread(target=subscriber_worker, args=(subscriber,))
            thread.start()
            threads.append(thread)
        
        time.sleep(0.5)  # Let subscribers start
        
        # Start publishers
        for publisher in publishers:
            thread = threading.Thread(target=publisher_worker, args=(publisher,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)
        
        # Check results
        total_messages_received = 0
        for subscriber in subscribers:
            if not subscriber.results.empty():
                messages = subscriber.results.get()
                total_messages_received += len(messages)
        
        expected_messages = publisher_count * messages_per_publisher * len(channels) * subscriber_count
        received_ratio = total_messages_received / expected_messages if expected_messages > 0 else 0
        
        self.test_assert(received_ratio > 0.5, f"Pub/sub message delivery", "> 50%", f"{received_ratio:.1%}")
        
        # Clean up
        for client in publishers + subscribers:
            client.disconnect()
    
    def test_server_stability_under_load(self):
        """Test server stability under high concurrent load"""
        print("\n=== Testing Server Stability Under Load ===")
        
        client_count = 15
        operation_duration = 3  # seconds
        
        clients = []
        threads = []
        
        # Create clients
        for i in range(client_count):
            client = ConcurrentClient(i)
            if client.connect():
                clients.append(client)
        
        connected_count = len(clients)
        self.test_assert(connected_count >= client_count - 3, f"High client connection count", f">= {client_count-3}", connected_count)
        
        def stress_worker(client):
            operations = []
            start_time = time.time()
            op_count = 0
            
            while time.time() - start_time < operation_duration:
                # Mix of different operations
                op_type = random.choice(['set', 'get', 'incr', 'lpush', 'sadd', 'hset'])
                key = f"stress_{client.client_id}_{op_count % 50}"
                
                try:
                    if op_type == 'set':
                        value = f"val_{op_count}"
                        cmd = f"*3\r\n$3\r\nSET\r\n${len(key)}\r\n{key}\r\n${len(value)}\r\n{value}\r\n"
                    elif op_type == 'get':
                        cmd = f"*2\r\n$3\r\nGET\r\n${len(key)}\r\n{key}\r\n"
                    elif op_type == 'incr':
                        cmd = f"*2\r\n$4\r\nINCR\r\n${len(key)}\r\n{key}\r\n"
                    elif op_type == 'lpush':
                        value = f"item_{op_count}"
                        cmd = f"*3\r\n$5\r\nLPUSH\r\n${len(key)}\r\n{key}\r\n${len(value)}\r\n{value}\r\n"
                    elif op_type == 'sadd':
                        value = f"member_{op_count}"
                        cmd = f"*3\r\n$4\r\nSADD\r\n${len(key)}\r\n{key}\r\n${len(value)}\r\n{value}\r\n"
                    elif op_type == 'hset':
                        field = f"field_{op_count}"
                        value = f"value_{op_count}"
                        cmd = f"*4\r\n$4\r\nHSET\r\n${len(key)}\r\n{key}\r\n${len(field)}\r\n{field}\r\n${len(value)}\r\n{value}\r\n"
                    
                    response = client.send_command(cmd)
                    operations.append((op_type, key, response))
                    op_count += 1
                    
                except Exception as e:
                    client.errors.append(f"Stress test error: {e}")
            
            client.results.put(operations)
        
        # Start stress test
        start_time = time.time()
        
        for client in clients:
            thread = threading.Thread(target=stress_worker, args=(client,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=operation_duration + 5)
        
        elapsed_time = time.time() - start_time
        
        # Collect results
        total_operations = 0
        total_errors = 0
        
        for client in clients:
            if not client.results.empty():
                operations = client.results.get()
                total_operations += len(operations)
            total_errors += len(client.errors)
            client.disconnect()
        
        self.test_assert(total_operations > client_count * 50, f"High operation throughput", f"> {client_count * 50}", total_operations)
        self.test_assert(total_errors < total_operations * 0.05, f"Low error rate under load", "< 5%", f"{total_errors}/{total_operations}")
        
        # Test server still responds after stress
        test_client = ConcurrentClient(999)
        test_client.connect()
        response = test_client.send_command("*1\r\n$4\r\nPING\r\n")
        self.test_assert("PONG" in response, "Server responsive after stress test")
        test_client.disconnect()
        
        print(f"   🚀 {total_operations} operations in {elapsed_time:.2f}s = {total_operations/elapsed_time:.1f} ops/sec")
        print(f"   💪 {total_errors} errors ({total_errors/total_operations*100:.2f}%)")
    
    def run_all_tests(self):
        """Run all concurrency tests"""
        print("🔍 Starting Concurrency and Thread Safety Test Suite")
        print("=" * 60)
        
        self.test_multiple_clients_basic()
        self.test_concurrent_counter_increments()
        self.test_concurrent_list_operations()
        self.test_concurrent_hash_operations()
        self.test_concurrent_pubsub()
        self.test_server_stability_under_load()
        
        # Print results
        total_tests = self.tests_passed + self.tests_failed
        print(f"\n📊 Concurrency Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {self.tests_passed}")
        print(f"   ❌ Failed: {self.tests_failed}")
        print(f"   Success Rate: {(self.tests_passed/total_tests*100):.1f}%")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = ConcurrencyTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)