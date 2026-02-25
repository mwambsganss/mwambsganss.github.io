# Authentication Setup Guide for AI.LILLY.COM

## 📋 Quick Setup (5 Minutes)

### Step 1: Login and Extract ALL Cookies

1. **Open your browser** (Chrome or Edge recommended)

2. **Navigate to** https://ai.lilly.com

3. **Login** with your Eli Lilly credentials

4. **IMPORTANT:** Make sure you're on the actual site (URL shows ai.lilly.com), not the login page

5. **Open Developer Tools:**
   - Press `F12` OR
   - Right-click → Inspect

6. **Go to Console tab** (not Application tab)

7. **Run the automatic cookie extractor:**
   - Open the file: `Web Crawler/extract_cookies.js`
   - Copy ALL the code
   - Paste into the Console
   - Press Enter

8. **Copy the generated Python code:**
   - The script will output ready-to-use Python code
   - Copy all the lines that start with `crawler.session.cookies.set`
   - These are your actual cookies from ai.lilly.com!

### Step 2: Add Cookies to Script

1. **Open the file:**
   ```
   Web Crawler/crawl_ai_lilly_authenticated.py
   ```

2. **Find the section** that says:
   ```python
   # ADD YOUR COOKIES HERE
   ```

3. **Paste the cookie lines** from Step 1:
   - You already have ready-to-use Python code from extract_cookies.js
   - Just paste them directly (no need to uncomment or edit)
   - It will look like:
   ```python
   crawler.session.cookies.set('__cf_bm', 'abc123...', domain='ai.lilly.com')
   crawler.session.cookies.set('session_token', 'xyz789...', domain='ai.lilly.com')
   # ... etc for all your cookies
   ```

4. **Save the file**

### Step 3: Run the Authenticated Crawler

```bash
cd "Web Crawler"
python3 crawl_ai_lilly_authenticated.py
```

The crawler will now use your authentication!

---

## 🖼️ Visual Guide

### Finding Cookies in Chrome/Edge

```
1. Press F12
   ┌─────────────────────────────────────────────────┐
   │  Elements  Console  Sources  [Application]  ... │
   ├─────────────────────────────────────────────────┤
   │  Application                                     │
   │  ├─ Storage                                      │
   │  │  ├─ Local Storage                             │
   │  │  ├─ Session Storage                           │
   │  │  └─ [Cookies] ◄── Click here                 │
   │  │     └─ https://ai.lilly.com ◄── Then here   │
   │  │                                               │
   │  Cookies table:                                  │
   │  Name              | Value          | Domain     │
   │  ─────────────────────────────────────────────  │
   │  .AspNet.Cookies  | CfDJ8KjH...    | ai.lilly...│ ◄─ Copy this
   │  FedAuth          | 77u/PD94bW...  | ai.lilly...│ ◄─ And this
   │  FedAuth1         | 77u/PD94bW...  | ai.lilly...│ ◄─ And this
   └─────────────────────────────────────────────────┘
```

### Finding Cookies in Firefox

```
1. Press F12
   ┌─────────────────────────────────────────────────┐
   │  Inspector  Console  Debugger  [Storage]  ...   │
   ├─────────────────────────────────────────────────┤
   │  Storage                                         │
   │  ├─ Cache Storage                                │
   │  ├─ [Cookies] ◄── Click here                    │
   │  │  └─ https://ai.lilly.com ◄── Then here      │
   │  │                                               │
   │  Cookies table:                                  │
   │  Name              | Value                       │
   │  ────────────────────────────────────────────── │
   │  .AspNet.Cookies  | CfDJ8KjH...                 │ ◄─ Copy value
   │  FedAuth          | 77u/PD94bW...               │ ◄─ Copy value
   └─────────────────────────────────────────────────┘
```

---

## 📝 Complete Example

Here's what your edited script should look like:

```python
# ========================================
# ADD YOUR COOKIES HERE
# ========================================

# Replace with YOUR actual cookie values from the browser:
crawler.session.cookies.set('.AspNet.Cookies', 'CfDJ8KjHyW8n3J7wQZX...', domain='ai.lilly.com')
crawler.session.cookies.set('FedAuth', '77u/PD94bWwgdmVyc2lvbj0i...', domain='ai.lilly.com')
crawler.session.cookies.set('FedAuth1', '77u/PD94bWwgdmVyc2lvbj0i...', domain='ai.lilly.com')
```

---

## ⚠️ Important Notes

### Cookie Expiration
- **Cookies expire** - Usually after a few hours or days
- If the crawler stops working, get fresh cookies
- You'll need to repeat this process when cookies expire

### Security
- **Never share** your cookie values with anyone
- **Don't commit** this file to git with real cookies
- **Consider using environment variables** for extra security:

```python
import os
cookie_value = os.environ.get('AI_LILLY_COOKIE')
if cookie_value:
    crawler.session.cookies.set('.AspNet.Cookies', cookie_value, domain='ai.lilly.com')
```

Then run:
```bash
export AI_LILLY_COOKIE="your-cookie-value"
python3 crawl_ai_lilly_authenticated.py
```

---

## 🔍 Troubleshooting

### "No cookies added yet"
- You forgot to uncomment the lines
- Make sure to remove the `#` at the start of the line

### "Authentication failed" or "Redirected to login"
- Your cookies have expired - get fresh ones
- You may have copied the wrong cookies
- Try copying ALL cookies from ai.lilly.com

### "Still seeing login page"
- Make sure you copied the correct domain cookies
- Some sites need multiple cookies together
- Try including more cookies from the browser

### "Connection errors"
- Check your VPN connection
- Verify you can access ai.lilly.com in your browser
- Try reducing `max_pages` and `delay` settings

---

## 🎯 After Setup

Once authenticated, the crawler will:
- ✅ Access all pages you have permission to view
- ✅ Scrape full content from each page
- ✅ Map all URLs (pages, subsites, resources)
- ✅ Save everything in multiple formats
- ✅ Generate comprehensive sitemap

Output location: `Web Crawler/ai_lilly_crawl_auth/`

---

## 🚀 Alternative: Use Browser Tool

If this seems complex, remember you can use the **browser tool** which automatically uses your session:

1. Login to ai.lilly.com in browser
2. Press F12 → Console
3. Paste code from `../Sitemap Extractor/sitemap-extractor.js`
4. Get instant results!

No cookie copying needed! 😊

---

**Need help?** Check if:
- You're logged in to ai.lilly.com
- Developer Tools are open
- You're looking at the right domain's cookies
- You uncommented the lines in the script
