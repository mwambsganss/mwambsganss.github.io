#!/usr/bin/env python3
"""
Authenticated Web Crawler for ai.lilly.com
Requires manual setup of authentication cookies/tokens
"""

from web_crawler import WebCrawler
import os

# Configuration
config = {
    'max_pages': 100,
    'max_depth': 5,
    'delay': 2.0,
    'output_dir': 'ai_lilly_crawl',
    'include_subdomains': True,
    'save_content': True
}

# Create crawler
crawler = WebCrawler("https://ai.lilly.com", config)

# ========================================
# AUTHENTICATION SETUP (CHOOSE ONE METHOD)
# ========================================

# Method 1: Cookie Authentication (Most Common for Microsoft SSO)
# ----------------------------------------------------------
# 1. Login to ai.lilly.com in your browser
# 2. Open DevTools (F12) → Application → Cookies
# 3. Copy the session cookie values
# 4. Uncomment and update these lines:

# crawler.session.cookies.set('.AspNet.Cookies', 'YOUR_COOKIE_VALUE_HERE', domain='ai.lilly.com')
# crawler.session.cookies.set('FedAuth', 'YOUR_FEDAUTH_VALUE_HERE', domain='ai.lilly.com')
# crawler.session.cookies.set('FedAuth1', 'YOUR_FEDAUTH1_VALUE_HERE', domain='ai.lilly.com')

# Method 2: Bearer Token
# ----------------------------------------------------------
# If the site uses Bearer tokens:
# crawler.session.headers['Authorization'] = 'Bearer YOUR_TOKEN_HERE'

# Method 3: Basic Authentication
# ----------------------------------------------------------
# If the site uses basic auth:
# crawler.session.auth = ('username', 'password')

# Method 4: Environment Variables (More Secure)
# ----------------------------------------------------------
# Set environment variables and use them:
# AUTH_COOKIE = os.environ.get('AI_LILLY_AUTH_COOKIE')
# if AUTH_COOKIE:
#     crawler.session.cookies.set('.AspNet.Cookies', AUTH_COOKIE, domain='ai.lilly.com')

print("""
╔════════════════════════════════════════════════════════════════╗
║        AI.LILLY.COM Authenticated Crawler                      ║
╚════════════════════════════════════════════════════════════════╝

⚠️  AUTHENTICATION REQUIRED

This script needs authentication setup before running.

STEPS:
1. Login to https://ai.lilly.com in your browser
2. Open DevTools (F12) → Application → Cookies
3. Copy the cookie values
4. Edit this file and add cookies (see Method 1 above)
5. Run this script again

OR

Use the browser-based tool which automatically uses your session:
  → ../Sitemap Extractor/sitemap-extractor.js

════════════════════════════════════════════════════════════════
""")

# Uncomment to run after adding authentication:
# print("Starting authenticated crawl...")
# crawler.crawl()
