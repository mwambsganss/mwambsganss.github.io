# Crawler Update: Persistent Folders Per URL

**Date:** 2026-02-25
**Update:** Persistent folder structure with updates instead of timestamped copies

---

## What Changed

The crawler now creates **one folder per domain** and **updates it** when you re-crawl the same site, instead of creating timestamped duplicates.

## Before vs After

### Before (Timestamped Files)
```
Web Crawler/
└── ai.lilly.com_crawl/
    ├── sitemap_20260225_091155.json
    ├── sitemap_20260225_094804.json    ← Multiple versions
    ├── urls_20260225_091155.json
    ├── urls_20260225_094804.json        ← Multiple versions
    ├── report_20260225_091155.txt
    └── report_20260225_094804.txt       ← Multiple versions
```

### After (Single Updated Files) ✨
```
Web Crawler/
└── ai.lilly.com_crawl/
    ├── sitemap.json                     ← Always current
    ├── urls.json                        ← Always current
    ├── report.txt                       ← Always current
    ├── index.json / .html / .txt        ← Page files
    ├── about.json / .html / .txt
    └── ...
```

## Benefits

### 1. Clean Structure
- ✅ One file per type (sitemap.json, urls.json, report.txt)
- ✅ No timestamp clutter
- ✅ Easy to find latest data

### 2. Updates Instead of Duplicates
- ✅ Re-crawling the same site updates the folder
- ✅ No manual cleanup needed
- ✅ Always see the latest crawl results

### 3. Smart Detection
- 🔄 If folder exists → Updates files
- ✨ If folder is new → Creates new folder

## File Structure

Each crawled domain gets its own folder:

```
Web Crawler/
├── ai.lilly.com_crawl/
│   ├── sitemap.json              # Complete sitemap with all pages
│   ├── urls.json                 # Categorized URL lists
│   ├── report.txt                # Human-readable summary
│   ├── index.json / .html / .txt # Homepage
│   ├── about.json / .html / .txt # About page
│   └── ...                       # All other pages
│
├── docs.python.org_crawl/
│   ├── sitemap.json
│   ├── urls.json
│   ├── report.txt
│   └── ...
│
└── portal.company.com_crawl/
    ├── sitemap.json
    ├── urls.json
    ├── report.txt
    └── ...
```

## Updated Files

### Core Changes
**web_crawler.py** - `save_results()` method:
- ❌ Removed: `timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')`
- ❌ Removed: `sitemap_{timestamp}.json` naming
- ✅ Added: Update detection (checks if files exist)
- ✅ Added: Update/create messages
- ✅ Changed: Files now named `sitemap.json`, `urls.json`, `report.txt`

**Note:** Individual page files already used non-timestamped names, so no changes needed there.

## Behavior Examples

### Example 1: First Crawl (New Domain)
```bash
python3 crawl_authenticated.py https://ai.lilly.com
```

**Output:**
```
✨ Creating new crawl data for ai.lilly.com...
📄 Saved complete sitemap: ai.lilly.com_crawl/sitemap.json
📄 Saved URL list: ai.lilly.com_crawl/urls.json
📄 Saved text report: ai.lilly.com_crawl/report.txt
```

**Folder created:** `Web Crawler/ai.lilly.com_crawl/`

---

### Example 2: Re-crawl (Update Existing)
```bash
# Crawl the same site again
python3 crawl_authenticated.py https://ai.lilly.com
```

**Output:**
```
🔄 Updating existing crawl data for ai.lilly.com...
📄 Saved complete sitemap: ai.lilly.com_crawl/sitemap.json
📄 Saved URL list: ai.lilly.com_crawl/urls.json
📄 Saved text report: ai.lilly.com_crawl/report.txt
```

**Folder updated:** `Web Crawler/ai.lilly.com_crawl/` (overwrites previous data)

---

### Example 3: Different Domain (New Folder)
```bash
python3 crawl_simple.py https://docs.python.org
```

**Output:**
```
✨ Creating new crawl data for docs.python.org...
📄 Saved complete sitemap: docs.python.org_crawl/sitemap.json
```

**New folder created:** `Web Crawler/docs.python.org_crawl/`

## Migration: Cleaning Up Old Files

If you have old timestamped files from previous crawls, you can clean them up:

### Option 1: Manual Cleanup
Delete old timestamped files, keep the newest:
```bash
cd "Web Crawler/ai.lilly.com_crawl"

# Keep newest timestamped files, rename to new format
mv sitemap_20260225_094804.json sitemap.json
mv urls_20260225_094804.json urls.json
mv report_20260225_094804.txt report.txt

# Delete old timestamped versions
rm sitemap_202602*.json  # (if multiple exist)
rm urls_202602*.json
rm report_202602*.txt
```

### Option 2: Fresh Start
Just re-crawl and the new format will be used:
```bash
python3 crawl_authenticated.py https://ai.lilly.com
# New files will be created without timestamps
# Old timestamped files will remain but won't be updated
```

### Option 3: Clean Slate
Remove the entire folder and re-crawl:
```bash
rm -rf ai.lilly.com_crawl/
python3 crawl_authenticated.py https://ai.lilly.com
```

## Timestamp Information

While main files no longer have timestamps in their names, the **crawl timestamp is preserved** inside the files:

**In `urls.json`:**
```json
{
  "root_url": "https://ai.lilly.com",
  "base_domain": "ai.lilly.com",
  "crawled_at": "2026-02-25T09:48:04.635227",  ← Timestamp here
  "summary": { ... }
}
```

**In `report.txt`:**
```
Web Crawl Report
================================================================================

Root URL: https://ai.lilly.com
Base Domain: ai.lilly.com
Crawled: 2026-02-25 09:48:04          ← Timestamp here
```

## Backward Compatibility

- ✅ Old timestamped files still readable (just not generated anymore)
- ✅ Existing folder structure unchanged
- ✅ All crawlers (simple, authenticated, legacy) updated
- ✅ No breaking changes to data format

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Main files** | `sitemap_20260225_094804.json` | `sitemap.json` |
| **On re-crawl** | Creates new timestamped files | Updates existing files |
| **Folder per domain** | Yes | Yes |
| **Timestamp info** | In filename | Inside file content |
| **Cleanup needed** | Manual | Automatic (overwrites) |

---

**Status:** ✅ Updated
**Files Modified:** `web_crawler.py` (save_results method)
**Version:** 3.1
**Date:** 2026-02-25
