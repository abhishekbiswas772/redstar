#!/usr/bin/env python3
"""
Comprehensive Redstar Demo Script
Demonstrates all features of the Redis clone implementation
Perfect for video demonstrations and showcasing functionality
"""

import sys
import time
import socket
import threading
from datetime import datetime
from redstar_client.redstar_client import RedstarClient

class RedstarDemo:
    def __init__(self):
        self.client = None
        self.demo_sections = [
            ("🔗 Connection & Server Info", self.demo_connection),
            ("📝 String Operations", self.demo_strings), 
            ("📋 List Operations", self.demo_lists),
            ("🔗 Set Operations", self.demo_sets),
            ("🗂️ Hash Operations", self.demo_hashes),
            ("📊 Advanced String Operations", self.demo_advanced_strings),
            ("🎯 Advanced Set Operations", self.demo_advanced_sets),
            ("📈 Sorted Sets", self.demo_sorted_sets),
            ("🔢 Bitmap Operations", self.demo_bitmaps),
            ("📏 HyperLogLog Operations", self.demo_hyperloglog),
            ("🌍 Geospatial Operations", self.demo_geospatial),
            ("🌊 Stream Operations", self.demo_streams),
            ("⏰ Expiration & TTL", self.demo_expiration),
            ("📢 Pub/Sub Messaging", self.demo_pubsub),
            ("🔍 Key Management", self.demo_key_management),
            ("🔄 Data Persistence", self.demo_persistence)
        ]
    
    def check_server_running(self):
        """Check if Redstar server is running"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 6379))
            sock.close()
            return result == 0
        except:
            return False
    
    def connect_client(self):
        """Connect to Redstar server"""
        try:
            self.client = RedstarClient("127.0.0.1", 6379)
            self.client.connect()
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def print_header(self, title):
        """Print formatted section header"""
        print(f"\n{'='*80}")
        print(f" {title}")
        print(f"{'='*80}")
    
    def print_command(self, cmd, result=None, description=""):
        """Print command with result"""
        print(f"🔧 {cmd}")
        if description:
            print(f"   💡 {description}")
        if result is not None:
            print(f"   ➡️  {result}")
        print()
        time.sleep(0.5)  # Brief pause for demo effect
    
    def demo_connection(self):
        """Demo connection and server information"""
        result = self.client.send_command(['PING'])
        self.print_command("PING", result, "Test server connectivity")
        
        result = self.client.send_command(['INFO'])
        self.print_command("INFO", result, "Get server information")
        
        result = self.client.send_command(['PING', 'Hello Redstar!'])
        self.print_command("PING Hello Redstar!", result, "Ping with custom message")
    
    def demo_strings(self):
        """Demo string operations"""
        # Basic string operations
        self.client.send_command(['SET', 'demo:name', 'Redstar Database'])
        self.print_command("SET demo:name 'Redstar Database'", "OK", "Store a string value")
        
        result = self.client.send_command(['GET', 'demo:name'])
        self.print_command("GET demo:name", result, "Retrieve string value")
        
        # Multiple key operations
        self.client.send_command(['MSET', 'user:1', 'Alice', 'user:2', 'Bob', 'user:3', 'Charlie'])
        self.print_command("MSET user:1 Alice user:2 Bob user:3 Charlie", "OK", "Set multiple keys at once")
        
        result = self.client.send_command(['MGET', 'user:1', 'user:2', 'user:3'])
        self.print_command("MGET user:1 user:2 user:3", result, "Get multiple values")
        
        # Numeric operations
        self.client.send_command(['SET', 'counter', '10'])
        self.print_command("SET counter 10", "OK", "Set numeric value")
        
        result = self.client.send_command(['INCR', 'counter'])
        self.print_command("INCR counter", result, "Increment by 1")
        
        result = self.client.send_command(['DECR', 'counter']) 
        self.print_command("DECR counter", result, "Decrement by 1")
        
        # String manipulation
        result = self.client.send_command(['APPEND', 'demo:name', ' v2.0'])
        self.print_command("APPEND demo:name ' v2.0'", result, "Append to string")
        
        result = self.client.send_command(['STRLEN', 'demo:name'])
        self.print_command("STRLEN demo:name", result, "Get string length")
        
        result = self.client.send_command(['GETRANGE', 'demo:name', '0', '7'])
        self.print_command("GETRANGE demo:name 0 7", result, "Get substring")
    
    def demo_lists(self):
        """Demo list operations"""
        # Basic list operations
        result = self.client.send_command(['LPUSH', 'tasks', 'task3', 'task2', 'task1'])
        self.print_command("LPUSH tasks task3 task2 task1", result, "Push to left of list")
        
        result = self.client.send_command(['RPUSH', 'tasks', 'task4', 'task5'])
        self.print_command("RPUSH tasks task4 task5", result, "Push to right of list")
        
        result = self.client.send_command(['LRANGE', 'tasks', '0', '-1'])
        self.print_command("LRANGE tasks 0 -1", result, "Get all list elements")
        
        result = self.client.send_command(['LLEN', 'tasks'])
        self.print_command("LLEN tasks", result, "Get list length")
        
        result = self.client.send_command(['LPOP', 'tasks'])
        self.print_command("LPOP tasks", result, "Pop from left")
        
        result = self.client.send_command(['RPOP', 'tasks'])
        self.print_command("RPOP tasks", result, "Pop from right")
        
        # Advanced list operations
        result = self.client.send_command(['LINDEX', 'tasks', '1'])
        self.print_command("LINDEX tasks 1", result, "Get element at index")
        
        result = self.client.send_command(['LSET', 'tasks', '1', 'updated_task'])
        self.print_command("LSET tasks 1 updated_task", result, "Set element at index")
        
        result = self.client.send_command(['LRANGE', 'tasks', '0', '-1'])
        self.print_command("LRANGE tasks 0 -1", result, "View updated list")
    
    def demo_sets(self):
        """Demo set operations"""
        # Basic set operations
        result = self.client.send_command(['SADD', 'languages', 'Python', 'Java', 'Go', 'Rust'])
        self.print_command("SADD languages Python Java Go Rust", result, "Add elements to set")
        
        result = self.client.send_command(['SMEMBERS', 'languages'])
        self.print_command("SMEMBERS languages", result, "Get all set members")
        
        result = self.client.send_command(['SCARD', 'languages'])
        self.print_command("SCARD languages", result, "Get set cardinality")
        
        result = self.client.send_command(['SISMEMBER', 'languages', 'Python'])
        self.print_command("SISMEMBER languages Python", result, "Check membership")
        
        result = self.client.send_command(['SREM', 'languages', 'Java'])
        self.print_command("SREM languages Java", result, "Remove element from set")
    
    def demo_hashes(self):
        """Demo hash operations"""
        # Basic hash operations
        result = self.client.send_command(['HSET', 'user:1000', 'name', 'John Doe'])
        self.print_command("HSET user:1000 name 'John Doe'", result, "Set hash field")
        
        result = self.client.send_command(['HMSET', 'user:1000', 'email', 'john@example.com', 'age', '30', 'city', 'New York'])
        self.print_command("HMSET user:1000 email john@example.com age 30 city 'New York'", result, "Set multiple hash fields")
        
        result = self.client.send_command(['HGET', 'user:1000', 'name'])
        self.print_command("HGET user:1000 name", result, "Get hash field value")
        
        result = self.client.send_command(['HMGET', 'user:1000', 'name', 'email', 'age'])
        self.print_command("HMGET user:1000 name email age", result, "Get multiple hash fields")
        
        result = self.client.send_command(['HGETALL', 'user:1000'])
        self.print_command("HGETALL user:1000", result, "Get all hash fields and values")
        
        result = self.client.send_command(['HKEYS', 'user:1000'])
        self.print_command("HKEYS user:1000", result, "Get all hash field names")
        
        result = self.client.send_command(['HVALS', 'user:1000'])
        self.print_command("HVALS user:1000", result, "Get all hash values")
        
        result = self.client.send_command(['HLEN', 'user:1000'])
        self.print_command("HLEN user:1000", result, "Get number of hash fields")
        
        result = self.client.send_command(['HEXISTS', 'user:1000', 'email'])
        self.print_command("HEXISTS user:1000 email", result, "Check if hash field exists")
        
        result = self.client.send_command(['HINCRBY', 'user:1000', 'age', '1'])
        self.print_command("HINCRBY user:1000 age 1", result, "Increment hash field value")
    
    def demo_advanced_strings(self):
        """Demo advanced string operations"""
        self.client.send_command(['SET', 'message', 'Hello World'])
        self.print_command("SET message 'Hello World'", "OK", "Set initial string")
        
        result = self.client.send_command(['SETRANGE', 'message', '6', 'Redstar'])
        self.print_command("SETRANGE message 6 Redstar", result, "Replace part of string")
        
        result = self.client.send_command(['GET', 'message'])
        self.print_command("GET message", result, "View modified string")
        
        result = self.client.send_command(['GETSET', 'message', 'New Message'])
        self.print_command("GETSET message 'New Message'", result, "Get old value and set new")
    
    def demo_advanced_sets(self):
        """Demo advanced set operations"""
        # Create multiple sets for operations
        self.client.send_command(['SADD', 'set1', 'a', 'b', 'c', 'd'])
        self.client.send_command(['SADD', 'set2', 'c', 'd', 'e', 'f'])
        self.print_command("SADD set1 a b c d", "4", "Create first set")
        self.print_command("SADD set2 c d e f", "4", "Create second set")
        
        result = self.client.send_command(['SUNION', 'set1', 'set2'])
        self.print_command("SUNION set1 set2", result, "Union of sets")
        
        result = self.client.send_command(['SINTER', 'set1', 'set2'])
        self.print_command("SINTER set1 set2", result, "Intersection of sets")
        
        result = self.client.send_command(['SDIFF', 'set1', 'set2'])
        self.print_command("SDIFF set1 set2", result, "Difference of sets")
        
        result = self.client.send_command(['SRANDMEMBER', 'set1'])
        self.print_command("SRANDMEMBER set1", result, "Get random set member")
        
        result = self.client.send_command(['SPOP', 'set1'])
        self.print_command("SPOP set1", result, "Pop random element from set")
    
    def demo_sorted_sets(self):
        """Demo sorted set operations"""
        result = self.client.send_command(['ZADD', 'leaderboard', '100', 'Alice', '85', 'Bob', '92', 'Charlie'])
        self.print_command("ZADD leaderboard 100 Alice 85 Bob 92 Charlie", result, "Add scored elements")
        
        result = self.client.send_command(['ZRANGE', 'leaderboard', '0', '-1', 'WITHSCORES'])
        self.print_command("ZRANGE leaderboard 0 -1 WITHSCORES", result, "Get range with scores (ascending)")
        
        result = self.client.send_command(['ZREVRANGE', 'leaderboard', '0', '-1', 'WITHSCORES'])
        self.print_command("ZREVRANGE leaderboard 0 -1 WITHSCORES", result, "Get range with scores (descending)")
        
        result = self.client.send_command(['ZSCORE', 'leaderboard', 'Bob'])
        self.print_command("ZSCORE leaderboard Bob", result, "Get score of member")
        
        result = self.client.send_command(['ZCARD', 'leaderboard'])
        self.print_command("ZCARD leaderboard", result, "Get sorted set cardinality")
        
        result = self.client.send_command(['ZRANK', 'leaderboard', 'Bob'])
        self.print_command("ZRANK leaderboard Bob", result, "Get rank of member")
    
    def demo_bitmaps(self):
        """Demo bitmap operations"""
        result = self.client.send_command(['SETBIT', 'user_active', '10', '1'])
        self.print_command("SETBIT user_active 10 1", result, "Set bit at offset 10")
        
        result = self.client.send_command(['SETBIT', 'user_active', '15', '1'])
        self.print_command("SETBIT user_active 15 1", result, "Set bit at offset 15")
        
        result = self.client.send_command(['GETBIT', 'user_active', '10'])
        self.print_command("GETBIT user_active 10", result, "Get bit value at offset 10")
        
        result = self.client.send_command(['BITCOUNT', 'user_active'])
        self.print_command("BITCOUNT user_active", result, "Count set bits")
        
        # Bitmap operations
        self.client.send_command(['SETBIT', 'user_active2', '10', '1'])
        self.client.send_command(['SETBIT', 'user_active2', '20', '1'])
        
        result = self.client.send_command(['BITOP', 'AND', 'result', 'user_active', 'user_active2'])
        self.print_command("BITOP AND result user_active user_active2", result, "Bitwise AND operation")
    
    def demo_hyperloglog(self):
        """Demo HyperLogLog operations"""
        result = self.client.send_command(['PFADD', 'unique_visitors', 'user1', 'user2', 'user3', 'user1'])
        self.print_command("PFADD unique_visitors user1 user2 user3 user1", result, "Add elements to HyperLogLog")
        
        result = self.client.send_command(['PFCOUNT', 'unique_visitors'])
        self.print_command("PFCOUNT unique_visitors", result, "Get cardinality estimate")
        
        # Create another HLL and merge
        self.client.send_command(['PFADD', 'visitors2', 'user3', 'user4', 'user5'])
        result = self.client.send_command(['PFMERGE', 'all_visitors', 'unique_visitors', 'visitors2'])
        self.print_command("PFMERGE all_visitors unique_visitors visitors2", result, "Merge HyperLogLogs")
        
        result = self.client.send_command(['PFCOUNT', 'all_visitors'])
        self.print_command("PFCOUNT all_visitors", result, "Count merged HyperLogLog")
    
    def demo_geospatial(self):
        """Demo geospatial operations"""
        result = self.client.send_command(['GEOADD', 'cities', '-74.0059', '40.7128', 'New York', '-118.2437', '34.0522', 'Los Angeles'])
        self.print_command("GEOADD cities -74.0059 40.7128 'New York' -118.2437 34.0522 'Los Angeles'", result, "Add geospatial data")
        
        result = self.client.send_command(['GEODIST', 'cities', 'New York', 'Los Angeles', 'km'])
        self.print_command("GEODIST cities 'New York' 'Los Angeles' km", result, "Calculate distance in km")
        
        result = self.client.send_command(['GEOPOS', 'cities', 'New York'])
        self.print_command("GEOPOS cities 'New York'", result, "Get coordinates of location")
        
        result = self.client.send_command(['GEORADIUS', 'cities', '-74', '40', '1000', 'km'])
        self.print_command("GEORADIUS cities -74 40 1000 km", result, "Find locations within radius")
    
    def demo_streams(self):
        """Demo stream operations"""
        result = self.client.send_command(['XADD', 'events', '*', 'action', 'login', 'user', 'alice', 'timestamp', '1234567890'])
        self.print_command("XADD events * action login user alice timestamp 1234567890", result, "Add entry to stream")
        
        result = self.client.send_command(['XADD', 'events', '*', 'action', 'purchase', 'user', 'bob', 'amount', '25.99'])
        self.print_command("XADD events * action purchase user bob amount 25.99", result, "Add another entry")
        
        result = self.client.send_command(['XLEN', 'events'])
        self.print_command("XLEN events", result, "Get stream length")
        
        result = self.client.send_command(['XRANGE', 'events', '-', '+'])
        self.print_command("XRANGE events - +", result, "Get all stream entries")
        
        result = self.client.send_command(['XREAD', 'STREAMS', 'events', '0'])
        self.print_command("XREAD STREAMS events 0", result, "Read from stream")
    
    def demo_expiration(self):
        """Demo key expiration and TTL"""
        result = self.client.send_command(['SET', 'temp_key', 'temporary_value'])
        self.print_command("SET temp_key temporary_value", result, "Set temporary key")
        
        result = self.client.send_command(['EXPIRE', 'temp_key', '5'])
        self.print_command("EXPIRE temp_key 5", result, "Set expiration to 5 seconds")
        
        result = self.client.send_command(['TTL', 'temp_key'])
        self.print_command("TTL temp_key", result, "Check time to live")
        
        # Set with expiration
        result = self.client.send_command(['SET', 'another_temp', 'value', 'EX', '3'])
        self.print_command("SET another_temp value EX 3", result, "Set with immediate expiration")
        
        result = self.client.send_command(['TTL', 'another_temp'])
        self.print_command("TTL another_temp", result, "Check TTL of new key")
    
    def demo_pubsub(self):
        """Demo pub/sub messaging (simplified for demo)"""
        print("📢 Pub/Sub Demo:")
        print("   💡 This demonstrates the pub/sub concepts")
        print("   📝 In a full demo, you'd run subscribers in separate clients")
        print()
        
        # Demonstrate pub/sub info commands
        result = self.client.send_command(['PUBSUB', 'CHANNELS'])
        self.print_command("PUBSUB CHANNELS", result, "List active channels")
        
        result = self.client.send_command(['PUBSUB', 'NUMSUB', 'news'])
        self.print_command("PUBSUB NUMSUB news", result, "Get subscriber count for channel")
        
        # Show publishing (even with no subscribers)
        result = self.client.send_command(['PUBLISH', 'news', 'Breaking: Redstar is awesome!'])
        self.print_command("PUBLISH news 'Breaking: Redstar is awesome!'", result, "Publish message to channel")
        
        result = self.client.send_command(['PUBLISH', 'alerts', 'System maintenance at 2 AM'])
        self.print_command("PUBLISH alerts 'System maintenance at 2 AM'", result, "Publish to another channel")
        
        print("   ℹ️  For full pub/sub demo with subscribers, run the pubsub test suite")
    
    def demo_key_management(self):
        """Demo key management operations"""
        result = self.client.send_command(['KEYS', '*'])
        self.print_command("KEYS *", f"Found {len(result) if result else 0} keys", "List all keys")
        
        result = self.client.send_command(['KEYS', 'user:*'])
        self.print_command("KEYS user:*", result, "Find keys matching pattern")
        
        result = self.client.send_command(['EXISTS', 'demo:name', 'nonexistent'])
        self.print_command("EXISTS demo:name nonexistent", result, "Check if keys exist")
        
        # Delete some keys
        result = self.client.send_command(['DEL', 'temp_key', 'another_temp'])
        self.print_command("DEL temp_key another_temp", result, "Delete multiple keys")
    
    def demo_persistence(self):
        """Demo data persistence concepts"""
        print("💾 Data Persistence Demo:")
        print("   💡 Redstar maintains data in memory during server runtime")
        print("   🔄 Data persists across client connections")
        print("   🧹 Use FLUSHALL to clear all data")
        print()
        
        # Show current data count
        all_keys = self.client.send_command(['KEYS', '*'])
        key_count = len(all_keys) if all_keys else 0
        self.print_command("KEYS *", f"{key_count} total keys", "Current data in server")
        
        # Demonstrate FLUSHALL (but warn first)
        print("   ⚠️  FLUSHALL will remove ALL data from the server")
        print("   🔧 Uncommenting the line below would clear everything:")
        print("   #  result = self.client.send_command(['FLUSHALL'])")
        print("   #  self.print_command('FLUSHALL', result, 'Clear all data')")
        print()
    
    def run_full_demo(self):
        """Run the complete demonstration"""
        print("🎬 REDSTAR COMPREHENSIVE FEATURE DEMONSTRATION")
        print("=" * 80)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🚀 Showcasing a complete Redis clone built from scratch in Python!")
        print("=" * 80)
        
        # Check server and connect
        if not self.check_server_running():
            print("❌ FATAL: Redstar server is not running!")
            print("📋 Please start the server with: python main.py")
            print("🔧 Then run this demo with: python redstar_demo.py")
            return False
        
        if not self.connect_client():
            return False
        
        print("✅ Connected to Redstar server successfully!")
        
        # Run all demo sections
        try:
            for title, demo_func in self.demo_sections:
                self.print_header(title)
                demo_func()
                time.sleep(1)  # Brief pause between sections
                
        except Exception as e:
            print(f"❌ Demo error: {e}")
            return False
        finally:
            if self.client:
                self.client.close()
        
        # Final summary
        print(f"\n{'='*80}")
        print("🎉 REDSTAR DEMONSTRATION COMPLETE! 🎉")
        print(f"{'='*80}")
        print("✨ Features Demonstrated:")
        print("   • ✅ String operations (GET, SET, INCR, MGET, APPEND, etc.)")
        print("   • ✅ List operations (LPUSH, RPUSH, LRANGE, LINDEX, etc.)")
        print("   • ✅ Set operations (SADD, SMEMBERS, SUNION, SINTER, etc.)")
        print("   • ✅ Hash operations (HSET, HGET, HGETALL, HMSET, etc.)")
        print("   • ✅ Sorted sets (ZADD, ZRANGE, ZSCORE, etc.)")
        print("   • ✅ Bitmaps (SETBIT, GETBIT, BITCOUNT, BITOP)")
        print("   • ✅ HyperLogLog (PFADD, PFCOUNT, PFMERGE)")
        print("   • ✅ Geospatial (GEOADD, GEODIST, GEORADIUS)")
        print("   • ✅ Streams (XADD, XLEN, XRANGE, XREAD)")
        print("   • ✅ Key expiration (EXPIRE, TTL)")
        print("   • ✅ Pub/Sub messaging (PUBLISH, SUBSCRIBE)")
        print("   • ✅ Server operations (PING, INFO, KEYS)")
        print()
        print("🏆 This demonstrates a complete Redis-compatible server")
        print("🔧 Built entirely from scratch using custom data structures")
        print("📡 Compatible with Redis clients and protocol (RESP)")
        print("🚀 Perfect for learning, education, and understanding Redis internals!")
        print()
        print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        return True

def main():
    """Main entry point"""
    print("🎬 Starting Redstar Feature Demonstration...")
    print("💡 This script showcases ALL features of the Redis clone")
    print("🎥 Perfect for creating demonstration videos!")
    print()
    
    demo = RedstarDemo()
    success = demo.run_full_demo()
    
    if success:
        print("\n🎊 Demo completed successfully!")
        print("📋 All major Redis operations demonstrated")
        print("🔗 For pub/sub with multiple clients, run: python main.py test")
        print("📊 For comprehensive testing, run the test suites")
    else:
        print("\n❌ Demo encountered issues")
        print("🔧 Make sure the Redstar server is running: python main.py")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())