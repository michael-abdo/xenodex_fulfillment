#!/usr/bin/env python3
"""Run all tests for shared services"""
import sys
import subprocess
from pathlib import Path

def main():
    """Run all test files"""
    test_dir = Path(__file__).parent
    test_files = list(test_dir.glob("test_*.py"))
    
    print("Running tests for shared services...")
    print(f"Found {len(test_files)} test files")
    print("-" * 50)
    
    failed_tests = []
    
    for test_file in sorted(test_files):
        print(f"\nRunning {test_file.name}...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            failed_tests.append(test_file.name)
            print(f"❌ {test_file.name} FAILED")
            print(result.stdout)
            print(result.stderr)
        else:
            print(f"✅ {test_file.name} PASSED")
    
    print("\n" + "=" * 50)
    if failed_tests:
        print(f"❌ {len(failed_tests)} test files failed:")
        for test in failed_tests:
            print(f"  - {test}")
        return 1
    else:
        print(f"✅ All {len(test_files)} test files passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())