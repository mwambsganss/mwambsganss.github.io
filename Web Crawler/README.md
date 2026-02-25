# Python Web Crawler

> Powerful server-side web crawler for complete content scraping and site mapping

**✨ NEW: Runtime URL Support - Crawl any website without modifying code!**

## 🚀 Quick Start

### Simple Crawl (No Authentication)
```bash
pip install -r requirements.txt
python3 crawl_simple.py https://example.com
```

### Authenticated Crawl (Browser Automation)
```bash
pip install playwright
playwright install chromium
python3 crawl_authenticated.py https://your-site.com
```

**📖 See [USAGE.md](USAGE.md) for detailed examples and options.**

## 📦 What's Included

| File | Purpose |
|------|---------|
| **web_crawler.py** | Main crawler script (full featured) |
| **crawl_interactive.py** | Interactive setup wizard |
| **test_crawler.py** | Test on safe example site |
| **examples.py** | 8 usage examples with code |
| **start_crawler.sh** | Quick start bash script |
| **requirements.txt** | Python dependencies |
| **config.example.json** | Configuration template |

## ✨ Features

- ✅ **Scrapes full content** - HTML, text, metadata, images, links
- ✅ **Maps all URLs** - Pages, subsites, resources, external links
- ✅ **Multiple formats** - Saves JSON, HTML, and TXT for each page
- ✅ **Configurable** - Control depth, rate limits, scope, exclusions
- ✅ **Respectful** - Built-in delays, user-agent, error handling
- ✅ **Progress tracking** - Real-time console updates
- ✅ **Resume capability** - Saves partial results on interrupt
- ✅ **Universal** - Works on any website
- ✅ **Smart categorization** - Automatically categorizes URLs

## 📊 What You Get

After crawling `https://example.com`:

```
crawl_output/
├── sitemap_20260225_143022.json    # Complete sitemap with all content
├── urls_20260225_143022.json       # Categorized URL list
├── report_20260225_143022.txt      # Human-readable report
├── index.json / .html / .txt       # Homepage content
├── about.json / .html / .txt       # About page content
└── ... (one set per page crawled)
```

### Output Files Explained

1. **sitemap_*.json** - Complete data for every page:
   - URL, title, description, keywords
   - All headings (h1, h2, h3)
   - Full text content
   - All links and images
   - Metadata and crawl info

2. **urls_*.json** - Categorized URL lists:
   - Pages (regular HTML pages)
   - Subsites (different subdomains)
   - Resources (PDFs, docs, etc.)
   - External links
   - Failed URLs with errors

3. **report_*.txt** - Human-readable summary

4. **Individual page files** - For each page:
   - `.json` - Structured content
   - `.html` - Original HTML
   - `.txt` - Plain text content

## 🎯 Use Cases

- **Website migration** - Full backup before rebuilding
- **Content audit** - Analyze all pages and content
- **SEO analysis** - Comprehensive site mapping
- **Competitor research** - Analyze site structure
- **Documentation backup** - Save all docs locally
- **Data extraction** - Collect specific information at scale
- **Site archival** - Preserve website content
- **Link analysis** - Find all internal/external links

## 🚀 Usage Examples

### Basic Crawl
```bash
python web_crawler.py https://example.com
```

### Custom Options
```bash
python web_crawler.py https://example.com \
  --max-pages 500 \
  --max-depth 5 \
  --delay 2.0 \
  --output-dir my_crawl
```

### Quick URL Scan (No Content)
```bash
python web_crawler.py https://example.com \
  --max-pages 1000 \
  --no-save
```

### Targeted Crawl
```bash
python web_crawler.py https://docs.example.com \
  --max-pages 300 \
  --max-depth 5 \
  --no-subdomains
```

## ⚙️ Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `url` | Required | Root URL to start crawling |
| `--max-pages` | 1000 | Maximum number of pages to crawl |
| `--max-depth` | 10 | Maximum depth from root (levels) |
| `--delay` | 1.0 | Seconds to wait between requests |
| `--output-dir` | crawl_output | Directory to save results |
| `--no-subdomains` | False | Exclude subdomains from crawl |
| `--include-external` | False | Include external links in results |
| `--no-save` | False | Don't save page content (faster) |

## 🔧 Installation & Requirements

### Requirements
- Python 3.7 or higher
- pip (Python package manager)

### Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast HTML parser

## 📖 Interactive Mode

For the easiest experience, use the interactive wizard:

```bash
python crawl_interactive.py
```

It will guide you through:
1. Entering the URL
2. Setting crawl limits
3. Configuring scope
4. Choosing output options
5. Starting the crawl

## 🧪 Test Installation

Test that everything works:

```bash
python test_crawler.py
```

This will crawl a safe example site with limited scope.

## 📚 Learn by Example

Check out `examples.py` for 8 different usage patterns:

```bash
python examples.py
```

Examples include:
1. Basic crawl with defaults
2. Custom configuration
3. Quick scan (URLs only)
4. Deep content crawl
5. Single domain only
6. Authenticated sites
7. Custom exclusions
8. Documentation site optimized

## 🛡️ Best Practices

### Legal & Ethical
- ⚠️ **Check robots.txt** before crawling
- ⚠️ **Respect rate limits** - Use appropriate delays
- ⚠️ **Read terms of service** - Some sites prohibit scraping
- ⚠️ **Don't overload servers** - Be a good internet citizen

### Technical
- ✅ **Test first** - Start with `--max-pages 10`
- ✅ **Use delays** - Default 1.0s, increase for large sites
- ✅ **Monitor output** - Watch console for errors
- ✅ **Identify your bot** - Customize User-Agent in code
- ✅ **Handle errors** - Built-in, but check failed URLs

## 🔍 Configuration File

Create a `config.json` for reusable settings:

```json
{
  "max_pages": 1000,
  "max_depth": 10,
  "delay": 1.0,
  "include_subdomains": true,
  "include_external": false,
  "save_content": true,
  "output_dir": "crawl_output"
}
```

See `config.example.json` for a complete template.

## 🆚 vs Browser Tools

| Feature | Browser Tools | Python Crawler |
|---------|---------------|----------------|
| Installation | None | Python + packages |
| Speed | Manual per page | Automated |
| Content depth | Links only | Full HTML/text |
| Authentication | Uses browser session | Manual setup |
| Best for | Quick exploration | Full scraping |
| Scale | Small (1-20 pages) | Large (100+ pages) |

**Also Available:** [Browser-Based Sitemap Extractor](../Sitemap%20Extractor/) for quick link extraction

## 📖 Full Documentation

See [WEB-CRAWLER-GUIDE.md](WEB-CRAWLER-GUIDE.md) for:
- Detailed usage instructions
- Advanced configuration
- Authentication setup
- Troubleshooting guide
- Performance optimization
- Custom exclusion patterns

See [QUICK-REFERENCE.md](QUICK-REFERENCE.md) for:
- Quick command reference
- Common tasks
- Troubleshooting fixes
- Configuration cheat sheet

## 🚨 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### Crawler is too slow
```bash
python web_crawler.py URL --delay 0.5 --no-save
```

### Getting blocked (403/429)
```bash
python web_crawler.py URL --delay 5.0
```

### Out of memory
```bash
python web_crawler.py URL --max-pages 50 --no-save
```

## 🤝 Contributing

Feel free to modify and adapt this crawler for your needs!

## 📝 License

Free to use and modify for any purpose.

---

**Tool:** Python Web Crawler
**Version:** 1.0
**Last Updated:** 2026-02-25
**Also Available:** [Browser-Based Tools](../Sitemap%20Extractor/) for quick extraction
