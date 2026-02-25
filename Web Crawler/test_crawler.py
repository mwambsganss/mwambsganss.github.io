#!/usr/bin/env python3
"""
Test and Demo Script for Web Crawler
Tests the crawler on a safe example site
"""

import sys
import os

# Test with example.com (safe, respects robots)
TEST_URL = "http://example.com"
TEST_CONFIG = {
    'max_pages': 5,  # Small limit for testing
    'max_depth': 2,
    'delay': 1.0,
    'output_dir': 'test_crawl',
    'include_subdomains': False,
    'include_external': False,
    'save_content': True
}

print("=" * 80)
print("Web Crawler - Test Mode")
print("=" * 80)
print(f"Testing with: {TEST_URL}")
print("This is a safe test that will crawl a few pages only.")
print("=" * 80)
print()

try:
    from web_crawler import WebCrawler

    crawler = WebCrawler(TEST_URL, TEST_CONFIG)
    crawler.crawl()

    print("\n✅ Test successful!")
    print(f"Results saved to: {TEST_CONFIG['output_dir']}/")
    print("\nNow try with your own URL:")
    print("  python web_crawler.py https://your-site.com")
    print("or")
    print("  python crawl_interactive.py")

except ImportError as e:
    print("❌ Error: Missing dependencies")
    print("Please install requirements:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
