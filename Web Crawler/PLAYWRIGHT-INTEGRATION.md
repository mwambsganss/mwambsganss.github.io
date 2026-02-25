# Integrating Playwright Framework with Web Crawler

## Overview

You have two tools:
1. **ASO-Test-Automation-Playwright** (Node.js/TypeScript) - For browser automation and authentication
2. **Web Crawler** (Python) - For content scraping

## Integration Strategy

### Option 1: Use Playwright to Get Cookies, Then Python Crawler

**Step 1:** Create a Playwright script to authenticate and save cookies
**Step 2:** Python crawler loads those cookies and crawls

### Option 2: Use Python Playwright (Recommended)

Install Python Playwright and integrate directly with the web crawler.

---

## Quick Setup

### Install Python Playwright

```bash
pip install playwright
playwright install chromium
```

### Run the Login Script

```bash
cd "Web Crawler"
python3 crawl_with_login.py
```

This will:
1. Open a browser
2. Let you login to ai.lilly.com
3. Automatically extract cookies
4. Start crawling with authentication

---

## Using Your Existing ASO Framework

If you want to leverage your existing TypeScript framework, here's the approach:

### 1. Create Cookie Export Script in Your Framework

Add this to your ASO framework:

```typescript
// tests/export-cookies.ts
import { chromium } from '@playwright/test';
import * as fs from 'fs';

async function exportCookies() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Navigate to ai.lilly.com
  await page.goto('https://ai.lilly.com');

  // Wait for user to login (manual)
  console.log('Please login in the browser...');
  await page.waitForURL('**/ai.lilly.com/**', { timeout: 300000 });

  // Get cookies
  const cookies = await context.cookies();

  // Save to file
  fs.writeFileSync(
    '../Web Crawler/cookies.json',
    JSON.stringify(cookies, null, 2)
  );

  console.log(`Saved ${cookies.length} cookies to cookies.json`);
  await browser.close();
}

exportCookies();
```

### 2. Run Cookie Export

```bash
cd ../ASO-Test-Automation-Playwright/playwright_cucumber
npx ts-node tests/export-cookies.ts
```

### 3. Use Cookies in Python Crawler

The Python crawler will automatically load `cookies.json` if it exists.

---

## Recommended Approach

**Use the Python Playwright script** I created: `crawl_with_login.py`

It's simpler and doesn't require bridging two frameworks.

### Run it:

```bash
cd "Web Crawler"
pip install playwright
playwright install chromium
python3 crawl_with_login.py
```

This will:
- ✅ Open browser
- ✅ Let you login
- ✅ Auto-extract cookies
- ✅ Start crawling

---

## Next Steps

1. **Install Playwright for Python:**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Run the login crawler:**
   ```bash
   python3 "Web Crawler/crawl_with_login.py"
   ```

3. **Login when browser opens**

4. **Watch it crawl automatically!**

---

## Files Created

- **crawl_with_login.py** - Main script with Playwright authentication
- **PLAYWRIGHT-INTEGRATION.md** - This guide
