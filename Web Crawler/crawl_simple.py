#!/usr/bin/env python3
"""
Simple Web Crawler - No Authentication
Crawl any public website without needing login credentials
"""

import sys
import re
from urllib.parse import urlparse
from web_crawler import WebCrawler

def get_domain_name(url):
    """Extract clean domain name from URL for display and folder naming"""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    # Clean for folder name (remove special chars)
    clean_domain = re.sub(r'[^\w\-.]', '_', domain)
    return domain, clean_domain

# Get target URL from command line or prompt user
target_url = None
if len(sys.argv) > 1:
    target_url = sys.argv[1]
else:
    print("""
╔════════════════════════════════════════════════════════════════╗
║                  Simple Web Crawler                            ║
╚════════════════════════════════════════════════════════════════╝

Crawl any public website (no authentication required).

For sites requiring login, use: crawl_authenticated.py
""")
    target_url = input("\nEnter the URL to crawl (e.g., https://example.com): ").strip()

# Validate URL
if not target_url:
    print("❌ Error: No URL provided")
    sys.exit(1)

if not target_url.startswith(('http://', 'https://')):
    target_url = 'https://' + target_url

# Extract domain info
display_domain, folder_domain = get_domain_name(target_url)

# Configuration (can be overridden with command-line args)
config = {
    'max_pages': int(sys.argv[2]) if len(sys.argv) > 2 else 100,
    'max_depth': int(sys.argv[3]) if len(sys.argv) > 3 else 3,
    'delay': float(sys.argv[4]) if len(sys.argv) > 4 else 1.0,
    'output_dir': f'{folder_domain}_crawl',
    'include_subdomains': True,
    'save_content': True
}

print(f"""
╔════════════════════════════════════════════════════════════════╗
║                  Starting Web Crawl                            ║
╚════════════════════════════════════════════════════════════════╝

Target: {target_url}
Domain: {display_domain}
Output: {config['output_dir']}/
Max Pages: {config['max_pages']}
Max Depth: {config['max_depth']}
Delay: {config['delay']}s

════════════════════════════════════════════════════════════════
""")

# Create and run crawler
print("🕷️  Initializing crawler...\n")
crawler = WebCrawler(target_url, config)

print("🚀 Starting crawl...\n")
print("="*80 + "\n")

try:
    crawler.crawl()

    print("\n" + "="*80)
    print("✅ CRAWL COMPLETE!")
    print("="*80)
    print(f"Results saved to: {config['output_dir']}/")
    print(f"\nFiles generated:")
    print(f"  • sitemap_*.json - Complete sitemap with all content")
    print(f"  • urls_*.json - Categorized URL list")
    print(f"  • report_*.txt - Human-readable summary")
    print(f"  • Individual page files (*.html, *.json, *.txt)")

except KeyboardInterrupt:
    print("\n\n⚠️  Interrupted by user")
    print("Partial results saved.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
