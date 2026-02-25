# Universal Website Sitemap Generator - Instructions

## Overview
These scripts will help you build a comprehensive sitemap of any website by running JavaScript in your browser console. The scripts automatically detect the current domain and extract all links.

## Features
- ✅ **Automatic domain detection** - Works on any website
- ✅ **Subdomain support** - Includes or excludes subdomains
- ✅ **Link categorization** - Pages, subsites, resources, external links
- ✅ **Multiple export formats** - JSON and TXT
- ✅ **Safe defaults** - Excludes logout/delete/signout links
- ✅ **Authentication support** - Works with password-protected sites

## Files
1. **sitemap-extractor.js** - Extracts all links from a single page
2. **sitemap-deep-crawler.js** - Discovers links and provides a list to manually visit

## Method 1: Quick Single Page Extract

### Steps:
1. Open your browser and navigate to any website you want to map
2. Log in if authentication is required
3. Open Browser Developer Tools:
   - **Chrome/Edge**: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - **Firefox**: Press `F12` or `Ctrl+Shift+K` (Windows) / `Cmd+Option+K` (Mac)
4. Click on the **Console** tab
5. Open `sitemap-extractor.js` and copy all the code
6. Paste the code into the console and press Enter
7. The script will:
   - Automatically detect the current domain
   - Extract all links from the current page
   - Categorize them (pages, subsites, resources, external)
   - Automatically download 2 files:
     - `sitemap-YYYY-MM-DD.json` (structured data)
     - `sitemap-YYYY-MM-DD.txt` (readable list)

### Configuration Options
At the top of `sitemap-extractor.js`, you can modify:
```javascript
includeExternalLinks: true,  // Set to false to exclude external links
includeSubdomains: true,      // Set to false to only include exact domain match
```

## Method 2: Deep Crawl (Multiple Pages)

### Steps:
1. Follow steps 1-4 from Method 1
2. Open `sitemap-deep-crawler.js` and copy all the code
3. Paste into console and press Enter
4. The script will:
   - Automatically detect the current domain
   - Extract all links from the current page
   - Provide a numbered list of URLs to visit
   - Download a JSON file with discovered URLs
5. **Manual Step**: Visit each URL in the list and run `sitemap-extractor.js` on each

### Configuration Options
At the top of `sitemap-deep-crawler.js`, you can modify:
```javascript
includeSubdomains: true,      // Include all subdomains
excludePatterns: [            // URL patterns to skip
    /logout/i,
    /signout/i,
    /delete/i,
    /remove/i
]
```

## Method 3: Comprehensive Manual Crawl

For the most complete sitemap:

1. Start at the website's homepage
2. Run `sitemap-extractor.js` on the homepage
3. Review the navigation structure in the console output
4. Visit each main section/page:
   - About
   - Services
   - Products
   - Tools
   - Documentation
   - Resources
   - Help/Support
   - Any other main navigation items
5. On each page, run `sitemap-extractor.js` again
6. Repeat for subsections
7. Combine all the downloaded files

## Output Format

### JSON Output (sitemap-YYYY-MM-DD.json)
```json
{
  "config": {
    "domain": "example.com",
    "includeSubdomains": true,
    "includeExternalLinks": true
  },
  "currentPage": {
    "url": "https://example.com/page",
    "domain": "example.com",
    "title": "Page Title",
    "description": "Meta description",
    "keywords": "meta, keywords",
    "h1": ["Main Heading"],
    "h2": ["Subheading 1", "Subheading 2"]
  },
  "navigation": [
    {
      "type": "NAV",
      "class": "main-nav",
      "links": [
        {"text": "Home", "url": "https://example.com/"},
        {"text": "About", "url": "https://example.com/about"}
      ]
    }
  ],
  "summary": {
    "totalLinks": 50,
    "pages": 30,
    "subsites": 10,
    "resources": 5,
    "external": 15
  },
  "categorizedUrls": {
    "pages": ["url1", "url2"],
    "subsites": ["subsite1"],
    "resources": ["pdf1", "doc1"],
    "external": ["external1"]
  }
}
```

### TXT Output (sitemap-YYYY-MM-DD.txt)
```
SITEMAP FOR https://example.com/page
Domain: example.com
Generated: 2026-02-25T13:30:00.000Z

=== SUMMARY ===
Total Links: 50
Pages: 30
Subsites: 10
Resources: 5
External: 15

=== PAGES ===
https://example.com/page1
https://example.com/page2
...

=== SUBSITES ===
https://sub.example.com/

=== RESOURCES ===
https://example.com/doc.pdf
https://example.com/data.xlsx

=== EXTERNAL LINKS ===
https://external-site.com/
```

## Use Cases

### E-commerce Sites
- Map product categories and pages
- Find all product detail pages
- Discover checkout flow pages

### Corporate Websites
- Document internal portal structure
- Map department sites and subsites
- Catalog resources and documents

### Documentation Sites
- Create complete docs inventory
- Find all API endpoints
- Map tutorial and guide pages

### Blogs/Content Sites
- Discover all article pages
- Map category and tag pages
- Find archive pages

## Tips

1. **Start from the homepage** - This gives you the main navigation structure
2. **Check common paths**:
   - /about
   - /contact
   - /help or /support
   - /docs or /documentation
   - /blog
   - /products or /services
   - /api
   - /sitemap.xml (if available)
3. **Look for sitemaps**: Check if there's a visible sitemap link in the footer
4. **Navigation menus**: Pay attention to dropdown menus and mega menus
5. **Breadcrumbs**: These show the site hierarchy
6. **Pagination**: Don't forget paginated lists
7. **Search results**: Some content may only appear through search

### Platform-Specific Tips

**SharePoint Sites:**
- Site Contents link
- Site Settings (if you have access)
- All Site Content link
- Libraries and Lists

**WordPress Sites:**
- Category archives
- Tag archives
- Author archives
- Date archives

**Single Page Apps (React/Vue/Angular):**
- Make sure to wait for content to load
- Check browser network tab for API endpoints
- Navigation may be client-side only

## Combining Results

After collecting multiple JSON files:

1. Save all files in the same folder
2. You can manually merge the URLs, or
3. Use a script/tool to combine them into a single comprehensive sitemap

## Troubleshooting

- **Script doesn't run**:
  - Make sure you're on the actual website (not a login redirect page)
  - Check for Content Security Policy (CSP) restrictions
  - Try refreshing the page and running again

- **No download**:
  - Check your browser's download settings/permissions
  - Look in your Downloads folder
  - Try a different browser

- **Too many links**:
  - Set `includeExternalLinks: false` to reduce noise
  - Set `includeSubdomains: false` to limit scope
  - Add patterns to `excludePatterns` array

- **Missing links**:
  - Check if links are dynamically loaded (scroll down first)
  - Try running on different pages
  - Look for links in iframes or shadow DOM

- **Access denied**:
  - Some pages may require additional permissions
  - Make sure you're logged in
  - Check if you have the right access level

## Privacy & Security

- ⚠️ These scripts only extract links visible to you in the browser
- ⚠️ They do not bypass authentication or access controls
- ⚠️ They do not make additional network requests
- ⚠️ All processing happens locally in your browser
- ⚠️ Review the code before running if you have concerns

## Next Steps

After running the scripts, you can:
- Create a visual sitemap diagram
- Generate an XML sitemap for SEO
- Create a hierarchical structure diagram
- Build a searchable index
- Export to various formats (CSV, Markdown, HTML)
- Analyze site structure and navigation
- Identify broken links or orphaned pages
- Document API endpoints

## Advanced Usage

### Custom Domain Detection
If you want to override the automatic domain detection, edit the script:
```javascript
const config = {
    baseDomain: 'custom-domain.com',  // Override auto-detection
    // ... rest of config
};
```

### Custom File Types
Add more file extensions to capture:
```javascript
if (path.match(/\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|csv|txt|json|xml|mp4|mp3|svg|ai|psd)$/i)) {
```

### Custom Exclusion Patterns
Add more patterns to skip:
```javascript
excludePatterns: [
    /logout/i,
    /signout/i,
    /delete/i,
    /remove/i,
    /admin/i,        // Skip admin pages
    /temp/i,         // Skip temporary pages
    /draft/i         // Skip draft pages
]
```

---

**Need Help?** If you encounter any issues or have questions, feel free to ask!
