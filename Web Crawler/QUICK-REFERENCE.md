# Quick Reference Guide

## 📚 All Files Overview

### Core Files
- **web_crawler.py** - Main Python crawler (full scraping)
- **sitemap-extractor.js** - Browser tool (quick extraction)
- **sitemap-deep-crawler.js** - Browser tool (multi-page discovery)

### Helper Scripts
- **crawl_interactive.py** - Interactive setup wizard
- **start_crawler.sh** - Quick start bash script
- **test_crawler.py** - Test on safe example site
- **examples.py** - Usage examples with code

### Documentation
- **README.md** - Main overview and comparison
- **WEB-CRAWLER-GUIDE.md** - Complete Python crawler guide
- **SITEMAP-INSTRUCTIONS.md** - Complete browser tools guide
- **QUICK-REFERENCE.md** - This file

### Configuration
- **requirements.txt** - Python dependencies
- **config.example.json** - Configuration template
- **.gitignore** - Ignore output files

---

## 🚀 Quick Commands

### First Time Setup
```bash
pip install -r requirements.txt
```

### Browser Tools (No Installation)
1. Open website in browser
2. Press F12 → Console tab
3. Copy/paste code from `sitemap-extractor.js`
4. Press Enter

### Python Crawler - Simple
```bash
# Interactive mode (easiest)
python crawl_interactive.py

# Direct command
python web_crawler.py https://example.com

# With options
python web_crawler.py https://example.com --max-pages 100 --delay 2.0
```

### Quick Start Script
```bash
./start_crawler.sh
```

### Test Installation
```bash
python test_crawler.py
```

---

## 🎯 Common Tasks

### Task: Quick URL List
**Tool:** Browser (sitemap-extractor.js)
**Time:** 10 seconds
**Output:** JSON + TXT with all links

### Task: Full Site Backup
**Tool:** Python crawler
**Command:**
```bash
python web_crawler.py https://example.com --max-pages 500
```
**Time:** 5-30 minutes (depending on size)
**Output:** Complete content + URLs

### Task: Test New Site
**Command:**
```bash
python web_crawler.py https://example.com --max-pages 10 --delay 2.0
```

### Task: Documentation Backup
**Command:**
```bash
python web_crawler.py https://docs.example.com \
  --max-pages 500 \
  --max-depth 10 \
  --output-dir docs_backup
```

### Task: URL Scan (No Content)
**Command:**
```bash
python web_crawler.py https://example.com \
  --max-pages 1000 \
  --no-save
```

---

## 📊 Output Locations

### Python Crawler
```
crawl_output/
├── sitemap_TIMESTAMP.json    # All pages with full content
├── urls_TIMESTAMP.json        # URL list by category
├── report_TIMESTAMP.txt       # Human-readable report
└── [page files].json/.html/.txt
```

### Browser Tools
```
Downloads/
├── sitemap-YYYY-MM-DD.json    # From browser
└── sitemap-YYYY-MM-DD.txt     # From browser
```

---

## ⚙️ Configuration Cheat Sheet

### Python Crawler Options

| Option | Default | Description |
|--------|---------|-------------|
| `url` | Required | Starting URL |
| `--max-pages` | 1000 | Max pages to crawl |
| `--max-depth` | 10 | Max levels from root |
| `--delay` | 1.0 | Seconds between requests |
| `--output-dir` | crawl_output | Save location |
| `--no-subdomains` | False | Skip subdomains |
| `--include-external` | False | Include external links |
| `--no-save` | False | Skip content saving |

### Browser Tools Config

Edit at top of `.js` files:

```javascript
const config = {
    includeExternalLinks: true,  // true/false
    includeSubdomains: true,     // true/false
};
```

---

## 🔍 Troubleshooting Quick Fixes

### Problem: "Module not found"
```bash
pip install -r requirements.txt
```

### Problem: "Permission denied"
```bash
chmod +x *.py *.sh
```

### Problem: Crawler is slow
```bash
python web_crawler.py URL --delay 0.5 --no-save
```

### Problem: Getting blocked (403/429)
```bash
python web_crawler.py URL --delay 5.0
```

### Problem: Out of memory
```bash
python web_crawler.py URL --max-pages 50 --no-save
```

### Problem: Browser script doesn't work
- Make sure you're logged in (if required)
- Make sure you're on the actual page (not login redirect)
- Try refreshing and running again

---

## 💡 Best Practices

### ✅ Do
- Start with small limits (`--max-pages 10`) to test
- Use appropriate delays (1-5 seconds)
- Check robots.txt before crawling
- Identify your crawler with User-Agent
- Monitor output for errors

### ❌ Don't
- Crawl without delays
- Ignore robots.txt
- Crawl private/internal data without permission
- Use default User-Agent for production
- Crawl entire site at once without testing

---

## 📞 Getting Help

### Check Documentation
1. **README.md** - Overview and comparison
2. **WEB-CRAWLER-GUIDE.md** - Detailed Python guide
3. **SITEMAP-INSTRUCTIONS.md** - Detailed browser guide
4. **examples.py** - Code examples

### Test Your Setup
```bash
python test_crawler.py
```

### Verify Installation
```bash
python -c "import requests, bs4; print('✅ All dependencies installed')"
```

---

## 🎓 Learning Path

### Beginner
1. Use browser tool on a few pages
2. Run `test_crawler.py`
3. Try `crawl_interactive.py`

### Intermediate
1. Use command line with options
2. Customize config for your needs
3. Try different exclusion patterns

### Advanced
1. Modify source code
2. Add authentication
3. Create custom processing logic
4. Integrate with other tools

---

## 📝 Quick Syntax Examples

### Minimal
```bash
python web_crawler.py https://example.com
```

### Conservative (slow, safe)
```bash
python web_crawler.py https://example.com \
  --max-pages 100 \
  --delay 3.0
```

### Aggressive (fast, risky)
```bash
python web_crawler.py https://example.com \
  --max-pages 5000 \
  --delay 0.5 \
  --no-save
```

### Targeted
```bash
python web_crawler.py https://docs.example.com \
  --max-pages 300 \
  --max-depth 5 \
  --output-dir docs
```

---

**Last Updated:** 2026-02-25
