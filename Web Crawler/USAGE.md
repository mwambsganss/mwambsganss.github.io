# Web Crawler - Usage Guide

## Quick Start

The web crawler now supports **any URL** at runtime! Choose the right script for your needs:

### 1. Simple Crawl (No Authentication)
For public websites that don't require login:

```bash
# Interactive mode
python3 crawl_simple.py

# Command-line mode
python3 crawl_simple.py https://example.com

# With custom settings
python3 crawl_simple.py https://example.com 200 5 1.5
#                        URL                  max_pages max_depth delay(s)
```

### 2. Authenticated Crawl (Playwright Browser)
For websites requiring login (Microsoft SSO, any authentication):

```bash
# Interactive mode
python3 crawl_authenticated.py

# Command-line mode
python3 crawl_authenticated.py https://ai.lilly.com

# With custom settings
python3 crawl_authenticated.py https://ai.lilly.com 500 5
#                              URL                    max_pages max_depth
```

**How it works:**
1. Opens a browser window automatically
2. You login manually (handles MFA, SSO, etc.)
3. Script auto-detects when login completes
4. Extracts cookies automatically
5. Starts crawling with your authenticated session

## Scripts Overview

| Script | Purpose | Authentication | Use Case |
|--------|---------|----------------|----------|
| **crawl_simple.py** | Basic crawler | None | Public websites |
| **crawl_authenticated.py** | Browser automation | Playwright | Sites requiring login |
| **crawl_with_playwright.py** | ai.lilly.com specific | Playwright | Legacy (ai.lilly.com only) |
| **crawl_with_login.py** | ai.lilly.com specific | Playwright | Legacy (ai.lilly.com only) |
| **web_crawler.py** | Core crawler class | Flexible | Direct Python usage |

## Installation

### Basic Installation
```bash
pip install -r requirements.txt
```

### For Authenticated Crawling (Playwright)
```bash
pip install playwright
playwright install chromium
```

## Usage Examples

### Example 1: Crawl a Documentation Site
```bash
python3 crawl_simple.py https://docs.python.org 50 3
```
- Crawls up to 50 pages
- Maximum depth of 3 levels
- Output: `docs.python.org_crawl/`

### Example 2: Crawl Internal Company Site
```bash
python3 crawl_authenticated.py https://internal.company.com
```
- Opens browser for you to login
- Auto-detects login completion
- Crawls up to 500 pages (default)
- Output: `internal.company.com_crawl/`

### Example 3: Custom Configuration
```bash
python3 crawl_simple.py https://blog.example.com 1000 10 0.5
```
- Crawls up to 1000 pages
- Maximum depth of 10 levels
- 0.5-second delay between requests
- Output: `blog.example.com_crawl/`

## Output Structure

All crawls generate the same output structure:

```
{domain}_crawl/
├── sitemap_YYYYMMDD_HHMMSS.json    # Complete sitemap with all content
├── urls_YYYYMMDD_HHMMSS.json       # Categorized URL list
├── report_YYYYMMDD_HHMMSS.txt      # Human-readable summary
└── [page files]                     # Individual pages in multiple formats
    ├── page-name.html               # Raw HTML
    ├── page-name.json               # Structured data
    └── page-name.txt                # Plain text content
```

## Command-Line Arguments

### crawl_simple.py
```bash
python3 crawl_simple.py <URL> [max_pages] [max_depth] [delay]
```
- `URL` (required): Website to crawl
- `max_pages` (optional): Maximum pages to crawl (default: 100)
- `max_depth` (optional): Maximum depth levels (default: 3)
- `delay` (optional): Delay between requests in seconds (default: 1.0)

### crawl_authenticated.py
```bash
python3 crawl_authenticated.py <URL> [max_pages] [max_depth]
```
- `URL` (required): Website to crawl
- `max_pages` (optional): Maximum pages to crawl (default: 500)
- `max_depth` (optional): Maximum depth levels (default: 5)

## Advanced Usage

### Using the Core Crawler Directly (Python Code)

```python
from web_crawler import WebCrawler

config = {
    'max_pages': 100,
    'max_depth': 3,
    'delay': 1.0,
    'output_dir': 'my_crawl',
    'include_subdomains': True,
    'save_content': True
}

crawler = WebCrawler('https://example.com', config)

# Add custom headers
crawler.session.headers['User-Agent'] = 'MyBot/1.0'

# Add authentication (if needed)
crawler.session.headers['Authorization'] = 'Bearer YOUR_TOKEN'

# Start crawling
crawler.crawl()
```

### Custom Authentication (Manual Cookies)

If you have authentication cookies from another source:

```python
from web_crawler import WebCrawler

crawler = WebCrawler('https://example.com', config)

# Add cookies manually
crawler.session.cookies.set('session_id', 'abc123', domain='example.com')
crawler.session.cookies.set('auth_token', 'xyz789', domain='example.com')

crawler.crawl()
```

## Tips

### For Best Results
1. **Start small**: Test with low max_pages first (10-20)
2. **Respect rate limits**: Use appropriate delays (1-2 seconds)
3. **Check robots.txt**: Respect website crawling policies
4. **Monitor progress**: Watch console output for errors

### Troubleshooting

**Problem: "Playwright is not installed"**
```bash
pip install playwright
playwright install chromium
```

**Problem: Crawler hits login page**
- Use `crawl_authenticated.py` instead of `crawl_simple.py`
- Ensure you complete the login process in the browser

**Problem: Too many pages**
- Reduce `max_pages` parameter
- Reduce `max_depth` parameter
- Add URL exclusions in config

**Problem: Getting blocked**
- Increase `delay` parameter (2-3 seconds)
- Check website's robots.txt
- Use authenticated crawling if you have permission

## Comparison: Browser Tool vs Python Crawler

| Feature | Browser Tool (Sitemap Extractor) | Python Crawler |
|---------|----------------------------------|----------------|
| Installation | None | Python + packages |
| Speed | Instant | Minutes to hours |
| Content | URLs only | Full content |
| Authentication | Uses browser session | Playwright automation |
| Best for | Quick URL lists | Full site backups |

## Related Tools

- [Sitemap Extractor](../Sitemap%20Extractor/) - Browser-based quick URL extraction
- [Interactive Crawler](crawl_interactive.py) - Wizard-based crawler setup

## Support

For issues or questions:
1. Check the documentation in [WEB-CRAWLER-GUIDE.md](WEB-CRAWLER-GUIDE.md)
2. Review [QUICK-REFERENCE.md](QUICK-REFERENCE.md)
3. See authentication help in [AUTH-QUICK-START.md](AUTH-QUICK-START.md)

---

**Last Updated:** 2026-02-25
**Version:** 3.0 (Runtime URL Support)
