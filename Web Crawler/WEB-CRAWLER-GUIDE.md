# Web Crawler - Complete Guide

## 🕷️ Overview

This is a powerful Python-based web crawler that:
- **Scrapes all content** from websites (text, metadata, links, images)
- **Maps all URLs** (pages, subsites, resources, external links)
- **Saves everything** in multiple formats (JSON, HTML, TXT)
- **Respects rate limits** with configurable delays
- **Handles authentication** when provided credentials

## 🚀 Quick Start

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

### Usage

#### Option 1: Interactive Mode (Recommended for beginners)
```bash
python crawl_interactive.py
```

Follow the prompts to configure and start crawling.

#### Option 2: Command Line
```bash
python web_crawler.py https://example.com
```

#### Option 3: With Custom Options
```bash
python web_crawler.py https://example.com \
  --max-pages 500 \
  --max-depth 5 \
  --delay 2.0 \
  --output-dir my_crawl
```

## 📋 Command Line Options

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

## 📂 Output Structure

After crawling, you'll get:

```
crawl_output/
├── sitemap_20260225_143022.json    # Complete sitemap with all content
├── urls_20260225_143022.json       # Categorized URL list
├── report_20260225_143022.txt      # Human-readable report
├── index.json                      # Homepage content
├── index.html                      # Homepage HTML
├── index.txt                       # Homepage text
├── about.json                      # About page content
├── about.html                      # About page HTML
├── about.txt                       # About page text
└── ... (one set per page)
```

## 📊 Output Files Explained

### 1. Complete Sitemap (`sitemap_*.json`)

Full details of every page crawled:

```json
{
  "https://example.com/": {
    "url": "https://example.com/",
    "title": "Home Page",
    "description": "Meta description",
    "keywords": "keyword1, keyword2",
    "h1": ["Main Heading"],
    "h2": ["Subheading 1", "Subheading 2"],
    "text_content": "Full page text...",
    "links": [
      {"text": "About", "href": "/about"}
    ],
    "images": [
      {"alt": "Logo", "src": "/logo.png"}
    ],
    "meta": {
      "description": "...",
      "keywords": "..."
    },
    "depth": 0,
    "status_code": 200,
    "crawled_at": "2026-02-25T14:30:22"
  }
}
```

### 2. URL List (`urls_*.json`)

Categorized URLs with summary:

```json
{
  "root_url": "https://example.com",
  "base_domain": "example.com",
  "crawled_at": "2026-02-25T14:30:22",
  "summary": {
    "total_urls": 150,
    "pages": 120,
    "subsites": 10,
    "resources": 15,
    "external": 5,
    "failed": 2
  },
  "urls": {
    "pages": ["https://example.com/", "https://example.com/about"],
    "subsites": ["https://blog.example.com/"],
    "resources": ["https://example.com/doc.pdf"],
    "external": ["https://external-site.com/"]
  },
  "failed": {
    "https://example.com/broken": "404 Not Found"
  }
}
```

### 3. Text Report (`report_*.txt`)

Human-readable summary and complete URL list.

### 4. Page Content Files

For each page:
- **`.json`** - Structured metadata and content
- **`.html`** - Original HTML source
- **`.txt`** - Plain text content

## 🎯 Use Cases

### 1. Website Migration
```bash
# Crawl entire site before migration
python web_crawler.py https://oldsite.com --max-pages 5000
```

### 2. Content Audit
```bash
# Crawl and analyze content
python web_crawler.py https://yoursite.com --max-depth 5
```

### 3. SEO Analysis
```bash
# Map all pages and resources
python web_crawler.py https://yoursite.com --include-external
```

### 4. Documentation Backup
```bash
# Save all documentation pages
python web_crawler.py https://docs.example.com
```

### 5. Competitor Analysis
```bash
# Analyze competitor site structure (respect robots.txt!)
python web_crawler.py https://competitor.com --max-pages 200
```

## ⚙️ Configuration File

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

## 🔧 Advanced Features

### Custom User Agent

Edit `web_crawler.py` to change the User-Agent:

```python
'user_agent': 'Mozilla/5.0 (YourBot/1.0; +http://yoursite.com/bot)'
```

### Authentication

For sites requiring login, modify the session headers:

```python
self.session.headers.update({
    'User-Agent': self.config['user_agent'],
    'Authorization': 'Bearer YOUR_TOKEN',
    'Cookie': 'session=YOUR_SESSION'
})
```

### Custom Exclusions

Add URL patterns to skip:

```python
'exclude_patterns': [
    r'/logout',
    r'/admin',
    r'/private',
    r'/temp',
    r'\?print=true'  # Skip print versions
]
```

### Rate Limiting

Adjust crawl speed:

```bash
# Faster (use cautiously)
python web_crawler.py https://example.com --delay 0.5

# Slower (more respectful)
python web_crawler.py https://example.com --delay 3.0
```

## 🛡️ Best Practices

### 1. Respect robots.txt
Check the site's robots.txt before crawling:
```
https://example.com/robots.txt
```

### 2. Use Appropriate Delays
- **1-2 seconds**: Small personal sites
- **2-5 seconds**: Medium sites
- **5+ seconds**: Large commercial sites

### 3. Limit Scope
Don't crawl everything at once:
```bash
python web_crawler.py https://example.com --max-pages 100 --max-depth 3
```

### 4. Identify Your Bot
Use a descriptive User-Agent with contact info.

### 5. Monitor Progress
Watch the console output for errors and adjust settings.

## 🚨 Troubleshooting

### Crawler is Too Slow
```bash
# Increase speed (carefully)
python web_crawler.py URL --delay 0.5 --no-save
```

### Getting Blocked (403/429 errors)
```bash
# Slow down
python web_crawler.py URL --delay 5.0
```

### Out of Memory
```bash
# Reduce scope
python web_crawler.py URL --max-pages 100 --no-save
```

### SSL Certificate Errors
Add this to the script:
```python
self.session.verify = False  # Not recommended for production
```

### Timeout Errors
Increase timeout in config:
```python
'timeout': 60  # seconds
```

## 📊 Performance Tips

### Speed Up Crawling
1. **Disable content saving**: `--no-save`
2. **Reduce max depth**: `--max-depth 3`
3. **Exclude external links**: (default)
4. **Lower delay**: `--delay 0.5` (use responsibly)

### Save Disk Space
1. **Don't save content**: `--no-save`
2. **Limit pages**: `--max-pages 100`
3. **Remove HTML files** after crawl if you only need JSON

## 🔐 Security & Privacy

### For Authenticated Sites

**Option 1: Environment Variables**
```python
import os
token = os.environ.get('AUTH_TOKEN')
self.session.headers['Authorization'] = f'Bearer {token}'
```

Run with:
```bash
AUTH_TOKEN=your_token python web_crawler.py URL
```

**Option 2: Cookie Authentication**
1. Login via browser
2. Copy cookies from DevTools
3. Add to crawler:
```python
self.session.cookies.set('session', 'YOUR_SESSION_COOKIE')
```

## 📈 Example Workflows

### Workflow 1: Small Site Complete Crawl
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Interactive setup
python crawl_interactive.py

# 3. Enter URL and settings when prompted

# 4. Review output in crawl_output/
```

### Workflow 2: Large Site Targeted Crawl
```bash
# Crawl only 3 levels deep, save 200 pages
python web_crawler.py https://example.com \
  --max-pages 200 \
  --max-depth 3 \
  --delay 2.0 \
  --output-dir example_crawl
```

### Workflow 3: Documentation Backup
```bash
# Crawl docs site, save everything
python web_crawler.py https://docs.example.com \
  --max-pages 500 \
  --delay 1.0 \
  --output-dir docs_backup
```

## 🆘 Getting Help

### Common Issues

**Q: Can I resume an interrupted crawl?**
A: Not currently, but partial results are saved on interrupt (Ctrl+C).

**Q: Can I crawl multiple sites at once?**
A: Run multiple terminal windows with different output directories.

**Q: Does this work on JavaScript-heavy sites?**
A: No, it only gets server-rendered HTML. For JS sites, use Selenium or Playwright.

**Q: Can I crawl authenticated sites?**
A: Yes, but you need to add authentication headers/cookies manually.

**Q: Is this legal?**
A: Respect robots.txt, terms of service, and rate limits. Don't crawl private data.

## 📝 License

Free to use and modify for any purpose.

---

**Need more help?** Check the code comments or modify the script for your specific needs!
