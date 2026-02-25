#!/usr/bin/env python3
"""
AI.LILLY.COM Authenticated Crawler
Step-by-step guide to add your authentication
"""

from web_crawler import WebCrawler

# Configuration
config = {
    'max_pages': 500,
    'max_depth': 5,
    'delay': 2.0,
    'output_dir': 'ai_lilly_crawl_auth',
    'include_subdomains': True,
    'save_content': True
}

print("""
╔════════════════════════════════════════════════════════════════╗
║        HOW TO ADD YOUR AUTHENTICATION CREDENTIALS             ║
╚════════════════════════════════════════════════════════════════╝

STEP 1: Get ALL Your Cookies
-----------------------------
1. Open Chrome/Edge browser
2. Go to https://ai.lilly.com
3. Log in with your Eli Lilly credentials
4. Press F12 to open Developer Tools
5. Go to "Console" tab
6. Paste this command and press Enter:

   document.cookie.split('; ').forEach(c => console.log(c.split('=')[0]))

7. This will list ALL cookie names. Copy them all!
8. Then go to "Application" tab → Cookies → ai.lilly.com
9. Find the cookies that look like authentication:
   - Anything with "session", "auth", "token", "user", "login"
   - Microsoft cookies: often start with "__" or have "msft", "office"
   - Cloudflare: __cf_bm, cf_clearance
   - Any long Base64-looking values

10. Copy the NAME and VALUE of each authentication cookie

STEP 2: Add ALL Cookies to This Script
---------------------------------------
Scroll down to "ADD YOUR COOKIES HERE" section
Add every cookie you found with this format:
  crawler.session.cookies.set('COOKIE_NAME', 'COOKIE_VALUE', domain='ai.lilly.com')

STEP 3: Run This Script
------------------------
After adding your cookies:
  python3 crawl_ai_lilly_authenticated.py

💡 TIP: When in doubt, add ALL cookies from the site!

════════════════════════════════════════════════════════════════
""")

# Create crawler
crawler = WebCrawler("https://ai.lilly.com", config)

# ========================================
# ADD YOUR COOKIES HERE
# ========================================
# Your cookies from ai.lilly.com:

# Replace 'PASTE_VALUE_HERE' with actual cookie values from Step 1
# Add one line for EACH cookie you see on ai.lilly.com

# EXAMPLE FORMAT:
# crawler.session.cookies.set('cookie-name', 'cookie-value', domain='ai.lilly.com')

# Common authentication cookie patterns (uncomment and add YOUR values):
#
# Microsoft/Azure AD cookies:
# crawler.session.cookies.set('ESTSAUTH', 'PASTE_VALUE_HERE', domain='ai.lilly.com')
# crawler.session.cookies.set('ESTSAUTHPERSISTENT', 'PASTE_VALUE_HERE', domain='ai.lilly.com')
# crawler.session.cookies.set('SignInStateCookie', 'PASTE_VALUE_HERE', domain='ai.lilly.com')
#
# Cloudflare cookies:
# crawler.session.cookies.set('__cf_bm', 'PASTE_VALUE_HERE', domain='ai.lilly.com')
# crawler.session.cookies.set('cf_clearance', 'PASTE_VALUE_HERE', domain='ai.lilly.com')
#
# Session cookies (look for these patterns):
# crawler.session.cookies.set('session', 'PASTE_VALUE_HERE', domain='ai.lilly.com')
# crawler.session.cookies.set('sessionid', 'PASTE_VALUE_HERE', domain='ai.lilly.com')
# crawler.session.cookies.set('session_token', 'PASTE_VALUE_HERE', domain='ai.lilly.com')
#
# Add ANY other cookies you see:
# crawler.session.cookies.set('COOKIE_NAME', 'PASTE_VALUE_HERE', domain='ai.lilly.com')
# crawler.session.cookies.set('ANOTHER_COOKIE', 'PASTE_VALUE_HERE', domain='ai.lilly.com')

# 💡 TIP: List all cookie names by running this in browser Console:
#    document.cookie.split('; ').forEach(c => console.log(c.split('=')[0]))

# ========================================
# CHECK IF COOKIES ARE ADDED
# ========================================
if len(crawler.session.cookies) == 0:
    print("❌ NO COOKIES ADDED YET")
    print("\nPlease follow the steps above to add your authentication cookies.")
    print("Edit this file and uncomment the cookie lines, then add your values.")
    exit(1)

# ========================================
# START CRAWLING
# ========================================
print("✅ Cookies added! Starting authenticated crawl...\n")
print(f"Cookies configured: {len(crawler.session.cookies)}")
print(f"Target: https://ai.lilly.com")
print(f"Max pages: {config['max_pages']}")
print(f"Output directory: {config['output_dir']}")
print("\nPress Ctrl+C to stop at any time.\n")
print("="*80)

try:
    crawler.crawl()
    print("\n✅ CRAWL COMPLETE!")
    print(f"Results saved to: {config['output_dir']}/")
except KeyboardInterrupt:
    print("\n\n⚠️  Crawl interrupted by user")
    crawler.save_results()
    print("Partial results saved.")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("If you see authentication errors, your cookies may have expired.")
    print("Try logging in again and getting fresh cookies.")
