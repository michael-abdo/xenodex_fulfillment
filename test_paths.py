#!/usr/bin/env python3
"""Test script to verify all paths are correctly configured"""

import os
import sys
from pathlib import Path

# Add original project directory to path
sys.path.insert(0, '/home/Mike/projects/xenodx/typing-clients-ingestion-minimal')

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    try:
        from utils.config import get_config
        print("✓ utils.config imported successfully")
        
        from utils.validation import validate_youtube_url
        print("✓ utils.validation imported successfully")
        
        from utils.csv_manager import CSVManager
        print("✓ utils.csv_manager imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_paths():
    """Test that all data paths exist or can be created"""
    print("\nTesting data paths...")
    
    data_paths = [
        "/home/Mike/Xenodx/fulfillment/data",
        "/home/Mike/Xenodx/fulfillment/data/drive_downloads",
        "/home/Mike/Xenodx/fulfillment/data/youtube_downloads",
        "/home/Mike/Xenodx/fulfillment/data/simple_downloads",
        "/home/Mike/Xenodx/fulfillment/data/downloads"
    ]
    
    all_good = True
    for path in data_paths:
        p = Path(path)
        if p.exists():
            print(f"✓ {path} exists")
        else:
            try:
                p.mkdir(parents=True, exist_ok=True)
                print(f"✓ {path} created successfully")
            except Exception as e:
                print(f"✗ Could not create {path}: {e}")
                all_good = False
    
    return all_good

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        # First check if config file exists in new location
        config_path = Path("/home/Mike/Xenodx/fulfillment/process_data/config/config.yaml")
        if config_path.exists():
            print(f"✓ Config file exists at {config_path}")
        else:
            print(f"✗ Config file not found at {config_path}")
            return False
            
        # Try to load config
        from utils.config import get_config
        config = get_config()
        
        # Check some key paths
        output_csv = config.get('paths', {}).get('output_csv')
        print(f"  Output CSV: {output_csv}")
        
        drive_downloads = config.get('paths', {}).get('drive_downloads')
        print(f"  Drive downloads: {drive_downloads}")
        
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Path Configuration Test ===\n")
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Data Paths", test_paths()))
    results.append(("Configuration", test_config()))
    
    print("\n=== Test Summary ===")
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✓ All tests passed! The new file structure is correctly configured.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())