# MWambsganss Tools Repository

> Web scraping, sitemap extraction, and automation tools

## 📦 Tools Included

### 1. [Sitemap Extractor](Sitemap%20Extractor/)
Browser-based JavaScript tools for quick website mapping

**Features:**
- ✅ No installation required
- ✅ Works on any website
- ✅ Auto-detects domain
- ✅ Quick link extraction
- ✅ Works with authenticated sites

**Quick Start:**
1. Open any website
2. Press F12 → Console
3. Paste `sitemap-extractor.js`
4. Done!

[📖 Full Documentation](Sitemap%20Extractor/)

---

### 2. [Web Crawler](Web%20Crawler/)
Python-based full content scraper with Playwright integration

**Features:**
- ✅ Complete content scraping (HTML, text, metadata)
- ✅ Automated multi-page crawling
- ✅ Playwright browser automation
- ✅ Authentication support (cookies + login)
- ✅ Configurable depth and rate limits
- ✅ Multiple output formats (JSON, HTML, TXT)

**Quick Start:**
```bash
cd "Web Crawler"
pip install -r requirements.txt
pip install playwright
playwright install chromium

# With authentication:
python3 crawl_with_login.py

# Or direct crawl:
python3 web_crawler.py https://example.com
```

[📖 Full Documentation](Web%20Crawler/)

---

## 🆚 Which Tool to Use?

| Need | Browser Tool | Python Crawler |
|------|--------------|----------------|
| Quick URL list | ✅ Best | ❌ Overkill |
| Authenticated sites | ✅ Easy | ⚠️ Requires setup |
| Full content | ❌ Limited | ✅ Complete |
| No installation | ✅ Just browser | ❌ Needs Python |
| Large sites (100+) | ⚠️ Manual | ✅ Automated |
| Browser automation | ❌ | ✅ Playwright |

---

## 📚 Documentation

- [Sitemap Extractor Guide](Sitemap%20Extractor/SITEMAP-INSTRUCTIONS.md)
- [Web Crawler Guide](Web%20Crawler/WEB-CRAWLER-GUIDE.md)
- [Quick Reference](Web%20Crawler/QUICK-REFERENCE.md)
- [Authentication Setup](Web%20Crawler/AUTH-SETUP-GUIDE.md)
- [Playwright Integration](Web%20Crawler/PLAYWRIGHT-INTEGRATION.md)

---

## 🚀 Common Workflows

### Quick Site Map
```bash
# Use browser tool - takes 10 seconds
Open browser → F12 → Console → Paste sitemap-extractor.js
```

### Full Site Backup
```bash
cd "Web Crawler"
python3 web_crawler.py https://example.com --max-pages 500
```

### Authenticated Site Crawl
```bash
cd "Web Crawler"
python3 crawl_with_login.py
# Browser opens, you login, then it crawls automatically
```

---

## 🛠️ Technologies

- **Sitemap Extractor**: Vanilla JavaScript
- **Web Crawler**: Python 3.7+
  - requests
  - beautifulsoup4
  - lxml
  - playwright (optional, for authentication)

---

## 📝 License

Free to use and modify for any purpose.

---

## 🔗 Links

- [GitHub Repository](https://github.com/mwambsganss/mwambsganss.github.io)
- [Issue Tracker](https://github.com/mwambsganss/mwambsganss.github.io/issues)

---

**Last Updated:** 2026-02-25
**Version:** 2.0
