# 🔐 Quick Authentication Setup

## 📍 You Are Here
You need to add your authentication credentials to crawl ai.lilly.com

## ⚡ EASY 4-Step Setup (Updated!)

### 1️⃣ Login & Open Console
```
1. Login to https://ai.lilly.com
2. Press F12 → Console tab
```

### 2️⃣ Run Cookie Extractor
```
1. Open: Web Crawler/extract_cookies.js
2. Copy ALL the code
3. Paste into browser Console
4. Press Enter
```

### 3️⃣ Copy Generated Code
```
The script outputs Python code like:
  crawler.session.cookies.set('__cf_bm', 'abc123...', domain='ai.lilly.com')
  crawler.session.cookies.set('session', 'xyz789...', domain='ai.lilly.com')

Copy all these lines!
```

### 4️⃣ Paste & Run
```
1. Open: Web Crawler/crawl_ai_lilly_authenticated.py
2. Find: "# ADD YOUR COOKIES HERE"
3. Paste the cookie lines
4. Save file
5. Run: python3 crawl_ai_lilly_authenticated.py
```

## 📚 Full Guide
See [AUTH-SETUP-GUIDE.md](AUTH-SETUP-GUIDE.md) for:
- Detailed step-by-step instructions
- Visual screenshots
- Troubleshooting
- Security best practices

## 🎯 Files You Need

| File | Purpose |
|------|---------|
| [crawl_ai_lilly_authenticated.py](crawl_ai_lilly_authenticated.py) | Main script - Edit this! |
| [AUTH-SETUP-GUIDE.md](AUTH-SETUP-GUIDE.md) | Complete setup guide |

## 💡 Too Complex?

Use the **browser tool** instead (no setup needed):
1. Login to ai.lilly.com
2. F12 → Console
3. Run `../Sitemap Extractor/sitemap-extractor.js`
4. Done! ✅

Browser tool automatically uses your session!

---

**Status:** ⚠️ Authentication required before crawling
**Next Step:** Follow steps above or read [AUTH-SETUP-GUIDE.md](AUTH-SETUP-GUIDE.md)
