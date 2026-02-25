# Universal Website Sitemap Extractor

> Browser-based JavaScript tools to extract and map website structure

## 🚀 Quick Start

1. Open any website in your browser
2. Press `F12` to open Developer Tools
3. Go to the **Console** tab
4. Copy & paste code from `sitemap-extractor.js`
5. Press Enter
6. Download your sitemap (JSON + TXT)

## 📦 What's Included

| File | Purpose |
|------|---------|
| **sitemap-extractor.js** | Single-page link extractor (main tool) |
| **sitemap-deep-crawler.js** | Multi-page URL discovery helper |
| **SITEMAP-INSTRUCTIONS.md** | Complete documentation |

## ✨ Features

- ✅ **Universal** - Works on any website
- ✅ **No installation** - Just browser console
- ✅ **Auto-detection** - Automatically detects current domain
- ✅ **Smart categorization** - Pages, subsites, resources, external links
- ✅ **Multiple formats** - Exports JSON and TXT
- ✅ **Safe** - Excludes logout/delete/signout links
- ✅ **Authenticated sites** - Works with login-protected sites
- ✅ **Configurable** - Easy config options at top of scripts

## 🎯 Use Cases

- **Quick URL mapping** - Get all links from a page in seconds
- **Website auditing** - Document site structure
- **SEO analysis** - Find all pages and resources
- **Migration planning** - Map existing site before rebuild
- **Content inventory** - List all content pages
- **Link checking** - Discover all internal/external links

## 📊 Output Examples

### Console Output
```
🔍 Starting sitemap extraction...
📍 Extracting sitemap for: example.com
✅ Extraction complete!
Summary: {totalLinks: 47, pages: 30, subsites: 5, resources: 8, external: 4}
📥 Sitemap downloaded as JSON file
📥 Sitemap downloaded as TXT file
```

### Downloaded Files
- `sitemap-2026-02-25.json` - Structured data with full details
- `sitemap-2026-02-25.txt` - Human-readable link list

## 📖 Usage Instructions

### Method 1: Single Page Extract

1. Navigate to any website
2. Open Developer Tools (`F12`)
3. Go to Console tab
4. Copy all code from `sitemap-extractor.js`
5. Paste and press Enter
6. Two files will auto-download

### Method 2: Multi-Page Discovery

1. Navigate to any website
2. Open Developer Tools (`F12`)
3. Go to Console tab
4. Copy all code from `sitemap-deep-crawler.js`
5. Paste and press Enter
6. Get a list of URLs to visit
7. Visit each URL and run `sitemap-extractor.js`

## ⚙️ Configuration

Both scripts have config sections at the top:

```javascript
const config = {
    includeExternalLinks: true,  // Include links to other domains
    includeSubdomains: true,      // Include subdomains
};
```

Edit these values before running to customize behavior.

## 🔧 Requirements

- Any modern browser (Chrome, Firefox, Edge, Safari)
- JavaScript enabled
- Access to browser Developer Tools (F12)

## 🛡️ Privacy & Security

- ✅ No data leaves your browser
- ✅ No external requests made
- ✅ Only sees what you can see
- ✅ Respects authentication
- ✅ Open source - review the code

## 💡 Pro Tips

1. **Start at homepage** - Best starting point for complete map
2. **Run on multiple pages** - Combine results for full coverage
3. **Check navigation menus** - May reveal hidden sections
4. **Look for sitemap.xml** - Many sites have one already
5. **Watch for dynamic content** - Scroll pages before extracting

## 🆚 Need More Power?

For full content scraping and automated crawling, check out the **[Web Crawler](../Web%20Crawler/)** folder which includes a Python-based crawler that:
- Scrapes complete page content
- Automatically crawls multiple pages
- Saves HTML, JSON, and TXT formats
- Handles authentication and rate limiting
- Uses Playwright for browser automation

## 📖 Full Documentation

See [SITEMAP-INSTRUCTIONS.md](SITEMAP-INSTRUCTIONS.md) for:
- Detailed usage instructions
- Multiple extraction methods
- Platform-specific tips (SharePoint, WordPress, etc.)
- Troubleshooting guide
- Advanced customization options

## 🤝 Contributing

Feel free to modify and adapt these scripts for your needs!

## 📝 License

Free to use and modify for any purpose.

---

**Tool:** Browser-Based Sitemap Extractor
**Last Updated:** 2026-02-25
**Also Available:** [Python Web Crawler](../Web%20Crawler/) for advanced scraping
