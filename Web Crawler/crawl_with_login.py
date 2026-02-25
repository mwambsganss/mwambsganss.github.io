#!/usr/bin/env python3
"""
AI.LILLY.COM Authenticated Crawler with Playwright
This uses browser automation to login and then crawl the site
"""

try:
    from playwright.sync_api import sync_playwright
    import time
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

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
║     AI.LILLY.COM Crawler with Playwright Authentication       ║
╚════════════════════════════════════════════════════════════════╝

This script will:
  1. Open a browser window (visible)
  2. Navigate to ai.lilly.com
  3. Let you login manually with your credentials
  4. Extract authentication cookies automatically
  5. Use those cookies for automated crawling

════════════════════════════════════════════════════════════════
""")

if not PLAYWRIGHT_AVAILABLE:
    print("❌ Playwright is not installed!")
    print("\nTo use browser-based authentication, install Playwright:")
    print("  pip install playwright")
    print("  playwright install chromium")
    print("\n" + "="*80)
    print("\n💡 EASIER ALTERNATIVE: Use the Browser Tool")
    print("="*80)
    print("\n1. Login to ai.lilly.com in your browser")
    print("2. Press F12 → Console tab")
    print("3. Run: ../Sitemap Extractor/sitemap-extractor.js")
    print("4. Get instant results with no setup!")
    exit(1)

print("\n⚠️  BROWSER AUTOMATION MODE")
print("="*80)
print("\nA browser window will open. Please:")
print("  1. Enter your Eli Lilly username (email)")
print("  2. Enter your password")
print("  3. Complete any MFA/2FA if required")
print("  4. Wait until you see the actual ai.lilly.com content")
print("  5. The script will automatically detect when you're logged in")
print("\n" + "="*80)

input("\nPress Enter to open the browser...")

with sync_playwright() as p:
    try:
        print("\n✅ Launching browser...")

        # Try to use system Chrome/Edge if available
        browser = None
        try:
            # Try Microsoft Edge first (common on corporate machines)
            browser = p.chromium.launch(
                headless=False,
                channel="msedge"  # Use system Edge
            )
            print("✅ Using Microsoft Edge")
        except:
            try:
                # Try Google Chrome
                browser = p.chromium.launch(
                    headless=False,
                    channel="chrome"  # Use system Chrome
                )
                print("✅ Using Google Chrome")
            except:
                # Fallback to downloaded Chromium
                browser = p.chromium.launch(headless=False)
                print("✅ Using Chromium")

        # Create a new context (like an incognito window)
        context = browser.new_context()

        # Create a new page
        page = context.new_page()

        print("✅ Browser opened!")
        print("Navigating to ai.lilly.com...")

        # Navigate to the site
        page.goto("https://ai.lilly.com", wait_until="networkidle")

        print("\n" + "="*80)
        print("📋 ACTION REQUIRED:")
        print("="*80)
        print("\n1. The browser window has opened")
        print("2. Login with your Eli Lilly credentials")
        print("3. Complete any MFA/2FA if prompted")
        print("4. Wait until you see the actual ai.lilly.com content")
        print("\n💡 TIP: The script will wait for you to complete login")
        print("   Don't close the browser window!")
        print("\n" + "="*80)

        # Wait for user to complete login
        print("\nWaiting for you to login...")
        print("(Looking for when the page title changes from 'Sign in'...)")

        # Wait up to 5 minutes for login
        timeout_seconds = 300
        start_time = time.time()

        while True:
            current_title = page.title()
            current_url = page.url

            # Check if we're past the login page
            if "sign in" not in current_title.lower() and "login.microsoftonline.com" not in current_url:
                print(f"\n✅ Detected successful login! (Page: '{current_title}')")
                break

            # Check timeout
            if time.time() - start_time > timeout_seconds:
                print("\n⏱️  Timeout waiting for login. Please try again.")
                browser.close()
                exit(1)

            # Wait a bit before checking again
            time.sleep(2)

        # Give the page a moment to fully load
        print("Waiting for page to fully load...")
        time.sleep(3)

        print("\n✅ Extracting cookies from authenticated session...")

        # Get all cookies
        cookies = context.cookies()

        if not cookies:
            print("❌ No cookies found! Something went wrong.")
            browser.close()
            exit(1)

        print(f"✅ Found {len(cookies)} cookies!")

        # Display cookies for debugging
        print("\n📋 Cookie Summary:")
        for cookie in cookies[:10]:  # Show first 10
            print(f"  • {cookie['name']}")
        if len(cookies) > 10:
            print(f"  ... and {len(cookies) - 10} more")

        # Close browser
        print("\n✅ Closing browser...")
        browser.close()
        print("✅ Browser closed")

        # Create crawler
        print("\n" + "="*80)
        print("🕷️  Starting authenticated crawl...")
        print("="*80)

        crawler = WebCrawler("https://ai.lilly.com", config)

        # Add all cookies to the crawler session
        for cookie in cookies:
            crawler.session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie.get('domain', 'ai.lilly.com')
            )

        print(f"\n✅ Added {len(cookies)} cookies to crawler")
        print(f"Target: https://ai.lilly.com")
        print(f"Max pages: {config['max_pages']}")
        print(f"Output: {config['output_dir']}/")
        print("\nStarting crawl... (Press Ctrl+C to stop)\n")

        # Start crawling
        crawler.crawl()

        print("\n" + "="*80)
        print("✅ CRAWL COMPLETE!")
        print("="*80)
        print(f"Results saved to: {config['output_dir']}/")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        try:
            browser.close()
        except:
            pass
        print("Browser closed.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            browser.close()
        except:
            pass
