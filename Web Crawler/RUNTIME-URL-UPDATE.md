# Web Crawler Update - Runtime URL Support ✨

**Date:** 2026-02-25
**Version:** 3.0

## What's New

The web crawler now supports **any URL at runtime** - no more hardcoded URLs!

## New Scripts

### 1. `crawl_simple.py` - Public Websites
For websites that don't require authentication:

```bash
# Interactive mode
python3 crawl_simple.py

# Command-line mode
python3 crawl_simple.py https://example.com

# With options
python3 crawl_simple.py https://example.com 200 5 1.5
```

**Features:**
- ✅ Works with any public URL
- ✅ No authentication required
- ✅ Configurable via command-line arguments
- ✅ Clean output folder naming (domain-based)

### 2. `crawl_authenticated.py` - Authenticated Websites
For websites that require login (SSO, MFA, etc.):

```bash
# Interactive mode
python3 crawl_authenticated.py

# Command-line mode
python3 crawl_authenticated.py https://internal.company.com

# With options
python3 crawl_authenticated.py https://internal.company.com 500 5
```

**Features:**
- ✅ Works with any authenticated URL
- ✅ Browser automation with Playwright
- ✅ Auto-detects login completion
- ✅ Handles Microsoft SSO, MFA, and other auth methods
- ✅ Generic login detection (works with any site)
- ✅ Clean output folder naming

## Key Improvements

### 1. Runtime URL Support
```bash
# Before (hardcoded)
# Had to edit crawl_with_playwright.py to change target

# After (runtime)
python3 crawl_authenticated.py https://any-site.com
```

### 2. Clean Output Folders
```bash
# Output folders automatically named by domain
https://ai.lilly.com        → ai.lilly.com_crawl/
https://docs.python.org     → docs.python.org_crawl/
https://internal.company.com → internal.company.com_crawl/
```

### 3. Generic Login Detection
The authenticated crawler now detects login completion for **any website**, not just ai.lilly.com:
- Checks for common login indicators ("sign in", "log in", "login", "authenticate")
- Monitors URL changes (login.microsoft.com → actual site)
- Works with SSO, MFA, basic auth, and custom login pages

### 4. Command-Line Flexibility
```bash
# All parameters customizable
python3 crawl_simple.py <URL> [max_pages] [max_depth] [delay]
python3 crawl_authenticated.py <URL> [max_pages] [max_depth]
```

## Usage Examples

### Example 1: Public Documentation Site
```bash
python3 crawl_simple.py https://docs.python.org 50 3
```
Output: `docs.python.org_crawl/`

### Example 2: Internal Company Portal
```bash
python3 crawl_authenticated.py https://portal.company.com
# Browser opens → You login → Auto-detects completion → Crawls site
```
Output: `portal.company.com_crawl/`

### Example 3: Quick Test
```bash
python3 crawl_simple.py https://example.com 10 2 0.5
# Crawls 10 pages, depth 2, 0.5s delay
```
Output: `example.com_crawl/`

## Migration Guide

### Old Way (Hardcoded)
```python
# Edit crawl_with_playwright.py
page.goto("https://ai.lilly.com", ...)  # Change this line
crawler = WebCrawler("https://ai.lilly.com", config)  # And this
```

### New Way (Runtime)
```bash
# Just pass the URL
python3 crawl_authenticated.py https://ai.lilly.com
python3 crawl_authenticated.py https://other-site.com
```

## File Structure

### New Files
- ✅ `crawl_simple.py` - No-auth crawler for any URL
- ✅ `crawl_authenticated.py` - Playwright auth crawler for any URL
- ✅ `USAGE.md` - Comprehensive usage guide
- ✅ `RUNTIME-URL-UPDATE.md` - This file

### Existing Files (Still Work)
- `crawl_with_playwright.py` - Legacy (ai.lilly.com only)
- `crawl_with_login.py` - Legacy (ai.lilly.com only)
- `crawl_ai_lilly.py` - Legacy (ai.lilly.com only)
- `web_crawler.py` - Core crawler (unchanged)

## Documentation

- **[USAGE.md](USAGE.md)** - Quick start guide with examples
- **[README.md](README.md)** - Main documentation (updated)
- **[WEB-CRAWLER-GUIDE.md](WEB-CRAWLER-GUIDE.md)** - Detailed guide
- **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** - Quick reference
- **[AUTH-QUICK-START.md](AUTH-QUICK-START.md)** - Authentication setup

## Testing

### Test Public Site
```bash
python3 crawl_simple.py https://example.com 5
```

### Test Authenticated Site
```bash
python3 crawl_authenticated.py https://ai.lilly.com 10
# Login when browser opens, wait for auto-detection
```

## Benefits

1. **Flexibility** - Use with any website without code changes
2. **Convenience** - No editing scripts, just pass URL
3. **Reusability** - Same script works for all sites
4. **Clarity** - Clear separation between public and authenticated crawling
5. **Maintainability** - Easier to update and test

## Backward Compatibility

All existing scripts still work:
- `crawl_with_playwright.py` - Still works for ai.lilly.com
- `crawl_ai_lilly.py` - Still works (manual cookie setup)
- `web_crawler.py` - Core class unchanged

New scripts are **additions**, not replacements.

## Summary

| Script | Auth | Target | Use Case |
|--------|------|--------|----------|
| `crawl_simple.py` | No | Any URL | Public sites |
| `crawl_authenticated.py` | Yes | Any URL | Login required sites |
| `crawl_with_playwright.py` | Yes | ai.lilly.com | Legacy (specific) |
| `web_crawler.py` | Flexible | Any URL | Direct Python usage |

---

**Recommended:** Use `crawl_simple.py` or `crawl_authenticated.py` for all new crawls.

**Status:** ✅ Ready to use
**Tested:** ✅ ai.lilly.com authentication working
**Version:** 3.0
