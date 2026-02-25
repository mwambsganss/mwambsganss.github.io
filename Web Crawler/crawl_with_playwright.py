#!/usr/bin/env python3
"""
AI.LILLY.COM Authenticated Crawler with Playwright (Auto-Start)
This version starts immediately without requiring Enter key press
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

AUTO-START MODE - Browser will open automatically in 3 seconds...

This script will:
  1. Open a browser window (visible)
  2. Navigate to ai.lilly.com
  3. Wait for you to login with your credentials
  4. Detect when login completes automatically
  5. Extract authentication cookies
  6. Start crawling with your session

════════════════════════════════════════════════════════════════
""")

if not PLAYWRIGHT_AVAILABLE:
    print("❌ Playwright is not installed!")
    print("\nTo use browser-based authentication, install Playwright:")
    print("  pip install playwright")
    print("  playwright install chromium")
    exit(1)

print("\n⚠️  INSTRUCTIONS:")
print("="*80)
print("1. Browser window will open automatically")
print("2. Login with your Eli Lilly credentials")
print("3. Complete any MFA/2FA if required")
print("4. Script will auto-detect when you're logged in")
print("5. Crawling will start automatically after login")
print("="*80)

print("\nStarting in 3 seconds...")
time.sleep(3)

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

        # Navigate to the site with better error handling
        try:
            page.goto("https://ai.lilly.com", wait_until="domcontentloaded", timeout=60000)
            # Wait a bit for any redirects to complete
            time.sleep(3)
            print("✅ Page loaded")
        except Exception as e:
            print(f"⚠️  Navigation warning: {e}")
            print("Continuing anyway...")

        print("\n" + "="*80)
        print("📋 PLEASE LOGIN NOW:")
        print("="*80)
        print("1. Enter your username in the browser")
        print("2. Enter your password")
        print("3. Complete MFA if prompted")
        print("4. Wait for the page to load")
        print("\nScript is watching for login completion...")
        print("="*80)

        # Wait for user to complete login
        print("\n⏳ Waiting for login...")

        # Wait up to 5 minutes for login
        timeout_seconds = 300
        start_time = time.time()
        check_interval = 3  # Check every 3 seconds instead of 2

        while True:
            try:
                # Wait for page to be stable before checking title
                page.wait_for_load_state("networkidle", timeout=5000)

                # Small delay to ensure page is fully stable
                time.sleep(1)

                current_title = page.title()
                current_url = page.url

                # Check if we're past the login page
                if "sign in" not in current_title.lower() and "login.microsoftonline.com" not in current_url:
                    print(f"\n✅ Login detected! (Page: '{current_title}')")
                    break

            except Exception as e:
                # If there's an error (navigation, timeout), just continue
                print(f"  Waiting for page stability... ({int(time.time() - start_time)}s)")
                pass

            # Check timeout
            if time.time() - start_time > timeout_seconds:
                print("\n⏱️  Timeout waiting for login (5 minutes)")
                print("Please try running the script again.")
                browser.close()
                exit(1)

            # Wait before checking again
            time.sleep(check_interval)

            # Progress indicator every 15 seconds
            elapsed = int(time.time() - start_time)
            if elapsed % 15 == 0 and elapsed > 0:
                print(f"  Still waiting for login... ({elapsed}s elapsed)")

        # Give the page a moment to fully load
        print("Waiting for page to fully load...")
        time.sleep(5)

        print("\n✅ Extracting cookies from authenticated session...")

        # Get all cookies
        cookies = context.cookies()

        if not cookies:
            print("❌ No cookies found!")
            browser.close()
            exit(1)

        print(f"✅ Found {len(cookies)} cookies!")

        # Display cookies for debugging
        print("\n📋 Cookie Summary:")
        for cookie in cookies[:10]:
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
        print("\n🚀 Starting crawl now...\n")
        print("="*80 + "\n")

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
