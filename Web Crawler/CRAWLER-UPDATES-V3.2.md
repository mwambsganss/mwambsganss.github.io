# Web Crawler Updates - Smart Authentication & Markdown Summaries

**Date:** 2026-02-25
**Version:** 3.2

---

## 🎯 Updates Summary

### 1. Maximum Depth Limit: 4 Layers
All crawlers now default to a maximum depth of **4 layers** to prevent excessive crawling.

### 2. Markdown Summary Files
Every crawl now generates a **SUMMARY.md** file with:
- Table of contents with links to each page
- Page-by-page summaries with key information
- Content previews (first 500 characters)
- Heading structures (H1, H2)
- Link counts
- Failed URLs (if any)

### 3. Smart Authentication (Recommended Approach)
For sites requiring authentication, the recommended approach is now:
1. Try cookie-based authentication first (faster)
2. Fall back to headful browser if needed (slower but handles complex auth)

---

## 📊 Changes Made

### File: `web_crawler.py`

**Max Depth Default:**
```python
'max_depth': 4,  # Maximum 4 layers deep (was 10)
```

**New Method: `save_markdown_summary()`**
- Generates comprehensive SUMMARY.md file
- Includes table of contents with anchor links
- Page-by-page summaries with metadata
- Content previews and heading structures
- Automatically called during `save_results()`

**Command-line Argument Updated:**
```python
parser.add_argument('--max-depth', type=int, default=4, help='Maximum crawl depth (default: 4)')
```

---

### File: `crawl_headful.py`

**Max Depth Default:**
```python
max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 4  # Default max depth 4
```

**Added Markdown Generation:**
- Generates SUMMARY.md after crawl completes
- Includes same comprehensive information as web_crawler.py
- Works with Playwright-captured content

---

## 📁 New Output Files

Each crawl now generates:

```
{domain}_crawl/
├── sitemap.json           # Complete sitemap data
├── urls.json              # Categorized URL lists
├── report.txt             # Text summary
├── SUMMARY.md             # ✨ NEW - Markdown summary
├── page1.json/.html/.txt  # Individual pages
├── page2.json/.html/.txt
└── ...
```

---

## 📖 SUMMARY.md Contents

### Structure:
1. **Header** - Domain, timestamp, page count
2. **Table of Contents** - Clickable links to each page
3. **Page Summaries** - For each page:
   - URL and title
   - Description (if available)
   - Depth level
   - Main topics (H1 headings, up to 5)
   - Sections (H2 headings, up to 10)
   - Content preview (first 500 characters)
   - Link count
4. **Resources** - PDF and document links
5. **Subsites** - Related subdomain links
6. **Failed URLs** - Errors encountered

### Example Entry:
```markdown
### lilly-ai-guidance

<a id="lilly-ai-guidance"></a>

**URL:** [https://ai.lilly.com/lilly-ai-guidance](https://ai.lilly.com/lilly-ai-guidance)
**Title:** Lilly AI Guidance | ai.lilly.com
**Depth:** 1

**Main Topics (H1):**
- Using AI Responsibly at Lilly

**Sections (H2):**
- What is Covered
- Key Guidelines
- Resources

**Content Preview:**

> Lilly AI Guidance provides comprehensive guidance on responsible...

**Links Found:** 7

---
```

---

## 🚀 Usage Examples

### Simple Crawl (4 layers max by default)
```bash
python3 crawl_simple.py https://example.com
# Output: example.com_crawl/SUMMARY.md
```

### Custom Depth
```bash
python3 web_crawler.py https://example.com --max-depth 6
# Crawls up to 6 layers instead of default 4
```

### Authenticated Crawl
```bash
python3 crawl_headful.py https://internal.company.com 100 4
# max_pages=100, max_depth=4, generates SUMMARY.md
```

---

## 📊 Markdown Summary Benefits

1. **Human-Readable** - Easy to browse in any markdown viewer
2. **Searchable** - Ctrl+F to find specific content
3. **Navigable** - Table of contents with clickable links
4. **Comprehensive** - All key information in one file
5. **GitHub-Friendly** - Renders beautifully on GitHub
6. **Version Control** - Easy to diff between crawl updates

---

## 🔄 Existing Crawls Updated

Generated SUMMARY.md for existing crawls:

### ✅ ai.lilly.com_crawl/SUMMARY.md
- 20 pages summarized
- Includes all AI products, registry, and guidance pages
- Table of contents with 15 unique pages
- Content previews for each page

### ✅ techhq.dc.lilly.com_crawl/SUMMARY.md
- 100 pages summarized
- Complete Tech HQ documentation structure
- AI solutions, cloud, data, engineering sections
- Comprehensive navigation

---

## 💡 Recommendations

### For Authentication Sites:

**Option 1: Headful (Recommended for Complex Auth)**
```bash
python3 crawl_headful.py https://internal.site.com
```
- Keeps browser open
- Handles MFA, SSO, redirects
- JavaScript execution
- Best for Microsoft SSO

**Option 2: Cookie-Based (Faster for Simple Auth)**
```bash
python3 crawl_authenticated.py https://internal.site.com
```
- Extracts cookies first
- Closes browser
- Uses requests library
- Good for simple cookie auth

---

## 🎯 Max Depth Explanation

**Why 4 layers?**
- **Layer 0:** Homepage
- **Layer 1:** Main sections (Products, Docs, Blog)
- **Layer 2:** Subsections (AI, Cloud, Data)
- **Layer 3:** Specific pages (Individual guides, articles)
- **Layer 4:** Deep content (Detailed docs, examples)

**Beyond 4 layers:**
- Usually redundant or duplicate content
- Significantly increases crawl time
- Can hit pagination or infinite loops
- Most site structures fit within 4 layers

**To increase if needed:**
```bash
# Command-line
python3 web_crawler.py https://site.com --max-depth 6

# Or in script
crawler = WebCrawler('https://site.com', {'max_depth': 6})
```

---

## 📝 Migration Guide

### No changes needed!
All existing scripts work the same way, they just:
1. Default to max_depth=4 (was 10)
2. Auto-generate SUMMARY.md files

### To see the new summaries:
```bash
# View in terminal
cat ai.lilly.com_crawl/SUMMARY.md

# View in browser (if you have a markdown viewer)
open ai.lilly.com_crawl/SUMMARY.md

# View in VS Code
code ai.lilly.com_crawl/SUMMARY.md
```

---

## ✅ Testing

Tested on existing crawls:
- ✅ ai.lilly.com (20 pages)
- ✅ techhq.dc.lilly.com (100 pages)

Both generated clean, well-formatted SUMMARY.md files with:
- Working table of contents
- Proper anchor links
- Content previews
- Heading structures

---

## 📦 Summary

| Feature | Before | After |
|---------|--------|-------|
| **Max Depth Default** | 10 layers | 4 layers |
| **Markdown Summary** | ❌ None | ✅ SUMMARY.md |
| **Auth Approach** | One method | Headful (recommended) |
| **Output Files** | 3 + pages | 4 + pages (added SUMMARY.md) |

---

**Status:** ✅ Complete
**Version:** 3.2
**Files Updated:** `web_crawler.py`, `crawl_headful.py`
**New Files Generated:** `SUMMARY.md` (auto-generated per crawl)
