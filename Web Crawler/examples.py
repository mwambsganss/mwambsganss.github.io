#!/usr/bin/env python3
"""
Example Usage Script for Web Crawler
Shows various ways to use the crawler with different configurations
"""

from web_crawler import WebCrawler

# Example 1: Basic crawl with defaults
def example_basic():
    """Most simple usage - just provide URL"""
    print("\n" + "="*80)
    print("Example 1: Basic Crawl")
    print("="*80)

    crawler = WebCrawler("https://example.com")
    crawler.crawl()


# Example 2: Custom configuration
def example_custom_config():
    """Crawl with custom settings"""
    print("\n" + "="*80)
    print("Example 2: Custom Configuration")
    print("="*80)

    config = {
        'max_pages': 100,           # Stop after 100 pages
        'max_depth': 5,             # Go 5 levels deep
        'delay': 2.0,               # 2 second delay (respectful)
        'output_dir': 'my_crawl',   # Custom output directory
        'include_subdomains': True, # Include subdomains
        'include_external': False,  # Don't save external links
        'save_content': True        # Save page content
    }

    crawler = WebCrawler("https://example.com", config)
    crawler.crawl()


# Example 3: Quick scan (no content saving)
def example_quick_scan():
    """Quick scan - just get URLs, don't save content"""
    print("\n" + "="*80)
    print("Example 3: Quick URL Scan")
    print("="*80)

    config = {
        'max_pages': 500,
        'max_depth': 10,
        'delay': 0.5,               # Faster
        'save_content': False,      # Don't save content (faster)
        'output_dir': 'url_scan'
    }

    crawler = WebCrawler("https://example.com", config)
    crawler.crawl()


# Example 4: Deep content crawl
def example_deep_crawl():
    """Deep crawl with full content saving"""
    print("\n" + "="*80)
    print("Example 4: Deep Content Crawl")
    print("="*80)

    config = {
        'max_pages': 1000,
        'max_depth': 15,
        'delay': 1.5,
        'include_subdomains': True,
        'include_external': True,   # Include external for analysis
        'save_content': True,
        'output_dir': 'deep_crawl'
    }

    crawler = WebCrawler("https://example.com", config)
    crawler.crawl()


# Example 5: Subdomain-only crawl
def example_subdomain_only():
    """Crawl only the exact domain, no subdomains"""
    print("\n" + "="*80)
    print("Example 5: Single Domain Only")
    print("="*80)

    config = {
        'max_pages': 200,
        'include_subdomains': False,  # Only exact domain
        'output_dir': 'single_domain'
    }

    crawler = WebCrawler("https://example.com", config)
    crawler.crawl()


# Example 6: Authenticated site (manual setup required)
def example_authenticated():
    """Crawl an authenticated site - requires manual cookie/token setup"""
    print("\n" + "="*80)
    print("Example 6: Authenticated Site (Setup Required)")
    print("="*80)

    config = {
        'max_pages': 100,
        'delay': 2.0,
        'output_dir': 'auth_crawl'
    }

    crawler = WebCrawler("https://authenticated-site.com", config)

    # Add authentication (you need to get these values)
    # Option 1: Bearer token
    # crawler.session.headers['Authorization'] = 'Bearer YOUR_TOKEN'

    # Option 2: Cookie
    # crawler.session.cookies.set('session', 'YOUR_SESSION_COOKIE')

    # Option 3: Basic auth
    # crawler.session.auth = ('username', 'password')

    # crawler.crawl()
    print("⚠️  Authentication setup required. See comments in code.")


# Example 7: Custom exclusions
def example_custom_exclusions():
    """Crawl with custom URL exclusions"""
    print("\n" + "="*80)
    print("Example 7: Custom Exclusions")
    print("="*80)

    config = {
        'max_pages': 200,
        'exclude_patterns': [
            r'/logout',
            r'/admin',
            r'/private',
            r'/temp',
            r'\?print=',         # Skip print versions
            r'/download/',       # Skip download pages
            r'/cart',            # Skip shopping cart
            r'/checkout'         # Skip checkout
        ],
        'output_dir': 'filtered_crawl'
    }

    crawler = WebCrawler("https://example.com", config)
    crawler.crawl()


# Example 8: Documentation site crawl
def example_docs_crawl():
    """Optimized for documentation sites"""
    print("\n" + "="*80)
    print("Example 8: Documentation Site Crawl")
    print("="*80)

    config = {
        'max_pages': 500,
        'max_depth': 10,
        'delay': 1.0,
        'include_subdomains': False,  # Usually docs are single domain
        'save_content': True,
        'output_dir': 'docs_backup',
        'exclude_patterns': [
            r'/search',          # Skip search pages
            r'/edit',            # Skip edit pages
            r'/history',         # Skip history pages
        ]
    }

    crawler = WebCrawler("https://docs.example.com", config)
    crawler.crawl()


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════╗
║          Web Crawler - Example Usage Demonstrations           ║
╚════════════════════════════════════════════════════════════════╝

This script shows different ways to use the web crawler.
Uncomment the example you want to run below.

Available examples:
  1. Basic crawl with defaults
  2. Custom configuration
  3. Quick scan (URLs only, no content)
  4. Deep content crawl
  5. Subdomain-only crawl
  6. Authenticated site (requires setup)
  7. Custom URL exclusions
  8. Documentation site crawl

To run an example, uncomment it below and run:
  python examples.py
    """)

    # Uncomment one example to run:

    # example_basic()
    # example_custom_config()
    # example_quick_scan()
    # example_deep_crawl()
    # example_subdomain_only()
    # example_authenticated()
    # example_custom_exclusions()
    # example_docs_crawl()

    print("\n💡 Tip: Edit this file and uncomment an example to run it.")
    print("   Or use the main crawler directly:")
    print("     python web_crawler.py https://example.com")
    print("     python crawl_interactive.py")
