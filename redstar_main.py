import sys
import os
from redstar_server.redstar_server import RedstarServer

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            print("Running comprehensive test suite...")
            try:
                run_individual_tests()
            except ImportError:
                print("Test suite not found. Running individual tests...")
                run_individual_tests()
        
        elif command == "tutorial":
            print("Redstar Tutorial Summary:")
            print("========================")
            print("1. Start server: python main.py")
            print("2. Connect with Redis client: redis-cli -p 6379")
            print("3. Run tests: python main.py test")
            print("4. Supported commands:")
            print("   - Strings: GET, SET, DEL, EXISTS, EXPIRE, TTL, INCR, DECR")
            print("   - Lists: LPUSH, RPUSH, LPOP, RPOP, LLEN, LRANGE")
            print("   - Sets: SADD, SREM, SMEMBERS, SCARD, SISMEMBER")
            print("   - Hashes: HSET, HGET, HDEL, HGETALL, HKEYS, HVALS")
            print("   - Pub/Sub: SUBSCRIBE, PUBLISH, UNSUBSCRIBE")
            print("   - Server: PING, INFO, FLUSHALL")
            
        elif command == "help":
            print("Redstar Server Usage:")
            print("====================")
            print("python main.py           - Start the Redstar server")
            print("python main.py test      - Run comprehensive test suite")
            print("python main.py tutorial  - Display tutorial summary")
            print("python main.py help      - Show this help")
        
        else:
            print(f"Unknown command: {command}")
            print("Use 'python main.py help' for usage information")
    
    else:
        # Start the server
        server = RedstarServer(host='127.0.0.1', port=6379)
        server.start()


def run_individual_tests():
    """Run individual test files."""
    test_files = [
        "test_core_structures.py",
        "test_datastore.py", 
        "test_integration.py",
        "test_list_operations.py",
        "test_redstar_value.py",
        "test_resp_protocol.py",
        "test_set_operations.py",
        "test_string_operations.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nRunning {test_file}...")
            try:
                os.system(f"python {test_file}")
            except Exception as e:
                print(f"Error running {test_file}: {e}")


if __name__ == "__main__":
    main()