#!/usr/bin/env python3
"""
Quick Start Guide - Test the Test Suite
Run this to verify the test suite is working correctly
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print(f"\n✅ {description} - PASSED")
        return True
    else:
        print(f"\n❌ {description} - FAILED")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║        Web Crawler Test Suite - Quick Start               ║
╚════════════════════════════════════════════════════════════╝

This script will run a few quick tests to verify the test suite
is set up correctly.
    """)

    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ pytest is installed (version {pytest.__version__})")
    except ImportError:
        print("❌ pytest is not installed")
        print("\nPlease install test requirements:")
        print("  pip install -r test_requirements.txt")
        sys.exit(1)

    # Check if parent web_crawler module is accessible
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import web_crawler
        print(f"✅ web_crawler module is accessible")
    except ImportError as e:
        print(f"❌ Cannot import web_crawler: {e}")
        sys.exit(1)

    results = []

    # Test 1: Run secret sanitization tests
    results.append(run_command(
        ['pytest', '-v', '-k', 'test_sanitize_azure_client_secret', '--tb=short'],
        "Test 1: Secret Sanitization"
    ))

    # Test 2: Run URL handling tests
    results.append(run_command(
        ['pytest', '-v', '-k', 'TestWebCrawlerURLHandling', '--tb=short', '-x'],
        "Test 2: URL Handling"
    ))

    # Test 3: Check fixtures are loading
    results.append(run_command(
        ['pytest', '-v', '-k', 'test_extract_content_title', '--tb=short'],
        "Test 3: Fixture Loading"
    ))

    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All quick start tests passed!")
        print("\nYou can now run the full test suite:")
        print("  pytest                          # All tests")
        print("  pytest -v                       # Verbose")
        print("  pytest -m unit                  # Unit tests only")
        print("  ./run_tests.sh coverage         # With coverage report")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        print("\nTroubleshooting:")
        print("  1. Make sure you're in the Tester directory")
        print("  2. Install test requirements: pip install -r test_requirements.txt")
        print("  3. Check that web_crawler.py exists in parent directory")
        sys.exit(1)

    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    main()
