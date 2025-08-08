#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all Redis operation test suites in sequence
"""

import subprocess
import sys
import time
import os
from datetime import datetime

class ComprehensiveTestRunner:
    def __init__(self):
        self.test_files = [
            ("Hash Operations", "test_hash_operations.py"),
            ("Pub/Sub Advanced", "test_pubsub_advanced.py"), 
            ("Server Operations", "test_server_operations.py"),
            ("Edge Cases", "test_edge_cases.py"),
            ("Concurrency", "test_concurrency.py"),
            ("Protocol Compliance", "test_protocol_compliance.py"),
        ]
        self.results = []
        self.total_start_time = None
    
    def run_test_suite(self, name, filename):
        """Run a single test suite"""
        print(f"\n{'='*80}")
        print(f"🧪 RUNNING: {name}")
        print(f"{'='*80}")
        
        if not os.path.exists(filename):
            print(f"❌ Test file {filename} not found!")
            return False, 0, 0
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, filename],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test suite
            )
            
            elapsed_time = time.time() - start_time
            
            # Parse output for test results
            output_lines = result.stdout.split('\n')
            passed = 0
            failed = 0
            
            for line in output_lines:
                if "✅ Passed:" in line:
                    try:
                        passed = int(line.split("✅ Passed:")[1].strip())
                    except:
                        pass
                elif "❌ Failed:" in line:
                    try:
                        failed = int(line.split("❌ Failed:")[1].strip())
                    except:
                        pass
            
            success = result.returncode == 0
            
            if success:
                print(f"✅ {name} PASSED")
                print(f"   Results: {passed} passed, {failed} failed")
                print(f"   Duration: {elapsed_time:.2f}s")
            else:
                print(f"❌ {name} FAILED")
                print(f"   Results: {passed} passed, {failed} failed")
                print(f"   Duration: {elapsed_time:.2f}s")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
            
            # Print last few lines of output for context
            if output_lines:
                print(f"   Last output:")
                for line in output_lines[-5:]:
                    if line.strip():
                        print(f"     {line}")
            
            return success, passed, failed
            
        except subprocess.TimeoutExpired:
            elapsed_time = time.time() - start_time
            print(f"⏰ {name} TIMED OUT after {elapsed_time:.2f}s")
            return False, 0, 0
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ {name} ERROR: {e}")
            return False, 0, 0
    
    def check_server_running(self):
        """Check if Redstar server is running"""
        print("🔍 Checking if Redstar server is running...")
        
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 6379))
            sock.close()
            
            if result == 0:
                print("✅ Server is running on port 6379")
                return True
            else:
                print("❌ Server is not running on port 6379")
                return False
        except Exception as e:
            print(f"❌ Error checking server: {e}")
            return False
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 COMPREHENSIVE REDIS OPERATIONS TEST SUITE")
        print("=" * 80)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Check if server is running
        if not self.check_server_running():
            print("\n❌ FATAL: Redstar server is not running!")
            print("Please start the server with: python redstar_main.py")
            return False
        
        self.total_start_time = time.time()
        total_passed = 0
        total_failed = 0
        suites_passed = 0
        suites_failed = 0
        
        # Run each test suite
        for name, filename in self.test_files:
            success, passed, failed = self.run_test_suite(name, filename)
            
            self.results.append({
                'name': name,
                'filename': filename,
                'success': success,
                'passed': passed,
                'failed': failed
            })
            
            total_passed += passed
            total_failed += failed
            
            if success:
                suites_passed += 1
            else:
                suites_failed += 1
            
            # Brief pause between test suites
            time.sleep(1)
        
        # Print comprehensive results
        self.print_final_results(total_passed, total_failed, suites_passed, suites_failed)
        
        return suites_failed == 0
    
    def print_final_results(self, total_passed, total_failed, suites_passed, suites_failed):
        """Print final comprehensive results"""
        total_time = time.time() - self.total_start_time
        total_tests = total_passed + total_failed
        total_suites = len(self.test_files)
        
        print(f"\n{'='*80}")
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print(f"{'='*80}")
        
        # Overall statistics
        print(f"⏱️  Total Duration: {total_time:.2f} seconds")
        print(f"📦 Test Suites: {suites_passed}/{total_suites} passed")
        print(f"🧪 Individual Tests: {total_passed}/{total_tests} passed")
        
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"📈 Overall Success Rate: {success_rate:.1f}%")
        
        print(f"\n{'='*80}")
        print("📋 DETAILED RESULTS BY TEST SUITE:")
        print(f"{'='*80}")
        
        # Detailed results for each suite
        for result in self.results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            suite_total = result['passed'] + result['failed']
            suite_rate = (result['passed'] / suite_total * 100) if suite_total > 0 else 0
            
            print(f"{status} {result['name']:<25} "
                  f"({result['passed']}/{suite_total} tests, {suite_rate:.1f}%)")
        
        print(f"\n{'='*80}")
        
        # Final verdict
        if suites_failed == 0:
            print("🎉 ALL TEST SUITES PASSED! 🎉")
            print("🏆 Your Redstar server implementation is working excellently!")
        elif suites_failed <= 2:
            print("⚠️  MOSTLY SUCCESSFUL - Some tests failed")
            print(f"💪 {suites_passed}/{total_suites} test suites passed")
            print("🔧 Check the failed tests above for specific issues to address")
        else:
            print("🚨 MULTIPLE FAILURES DETECTED")
            print(f"❌ {suites_failed}/{total_suites} test suites failed")
            print("🔍 Significant issues found - review server implementation")
        
        print(f"\n📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Recommendations
        if suites_failed > 0:
            print("\n💡 RECOMMENDATIONS:")
            failed_suites = [r['name'] for r in self.results if not r['success']]
            for suite in failed_suites:
                print(f"   • Review and fix issues in: {suite}")
            print("   • Check server logs for error messages")
            print("   • Verify RESP protocol implementation")
            print("   • Test individual failing commands manually")
        
        print("")

if __name__ == "__main__":
    runner = ComprehensiveTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)