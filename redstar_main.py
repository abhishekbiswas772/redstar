import sys
import time
from redstar_server.redstar_server import RedstarServer
from redstar_tests.test_suite import run_comprehensive_test, print_tutorial_summary


def main():
    """Main entry point for Redstar server"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            print("🧪 Running test suite...")
            print("Make sure Redstar server is running first!")
            time.sleep(1)
            success = run_comprehensive_test()
            sys.exit(0 if success else 1)
            
        elif command == "tutorial":
            print_tutorial_summary()
            sys.exit(0)
            
        elif command == "help":
            print("Redstar From Scratch - Usage:")
            print("  python redstar_main.py          # Start server")
            print("  python redstar_main.py test     # Run tests")
            print("  python redstar_main.py tutorial # Show tutorial")
            sys.exit(0)
    
    # Start Redstar server
    server = RedstarServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()