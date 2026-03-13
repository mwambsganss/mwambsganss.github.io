#!/usr/bin/env python3
"""
Playwright-based crawler with pagination and interactive element support
Handles tabs, pagination controls, "Load More" buttons, and dynamic content
"""

try:
    from playwright.sync_api import sync_playwright
    import time
    import sys
    import re
    import json
    import os
    from urllib.parse import urlparse, urljoin
    from datetime import datetime
    from bs4 import BeautifulSoup
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def sanitize_content(text: str) -> str:
    """
    Remove secrets and sensitive data from any text before saving.

    Applies to HTML, JSON, TXT, and Markdown outputs. Removes:
    - Azure AD client secrets (Q~ pattern)
    - UUIDs in client_id / tenant_id / app_id contexts
    - Bearer / Authorization header tokens
    - JWT tokens (eyJ...)
    - OpenAI keys (sk-...), Anthropic keys (sk-ant-...)
    - Generic API keys and access/refresh tokens
    - Passwords and connection strings
    - Private key blocks
    """
    # Azure AD client secrets (Q~ pattern)
    text = re.sub(r'[A-Za-z0-9_~\-\.]{3,20}Q~[A-Za-z0-9_~\-]{10,}', 'REDACTED-SECRET', text)

    # UUIDs in credential contexts
    uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
    text = re.sub(
        r'((?:client|tenant|app|subscription|object|resource)[_\-]?id["\']?\s*[:=]\s*["\']?)(' + uuid_pattern + r')',
        r'\1REDACTED-UUID', text, flags=re.IGNORECASE)

    # Bearer / Authorization tokens
    text = re.sub(r'Bearer\s+[A-Za-z0-9_\-\.]{20,}', 'Bearer REDACTED-TOKEN', text, flags=re.IGNORECASE)
    text = re.sub(
        r'(Authorization["\']?\s*[:=]\s*["\']?[A-Za-z]+\s+)[A-Za-z0-9_\-\.]{20,}',
        r'\1REDACTED-TOKEN', text, flags=re.IGNORECASE)

    # JWT tokens (eyJ base64 header)
    text = re.sub(r'eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+', 'REDACTED-JWT', text)

    # OpenAI / Anthropic / common provider keys
    text = re.sub(r'sk-ant-[A-Za-z0-9_\-]{20,}', 'REDACTED-API-KEY', text)
    text = re.sub(r'sk-[A-Za-z0-9]{20,}', 'REDACTED-API-KEY', text)

    # Generic API keys
    text = re.sub(
        r'(api[_\-]?key["\']?\s*[:=]\s*["\']?)([A-Za-z0-9_\-]{32,})',
        r'\1REDACTED-API-KEY', text, flags=re.IGNORECASE)

    # Access / refresh tokens
    text = re.sub(
        r'((?:access|refresh|id)[_\-]?token["\']?\s*[:=]\s*["\']?)([A-Za-z0-9_\-\.]{32,})',
        r'\1REDACTED-TOKEN', text, flags=re.IGNORECASE)

    # Passwords in key=value or JSON context
    text = re.sub(
        r'((?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?)([^\s"\']{8,})',
        r'\1REDACTED-PASSWORD', text, flags=re.IGNORECASE)

    # Connection strings (e.g. Server=...;Password=...)
    text = re.sub(
        r'((?:Password|Pwd)=)([^;"\'\s]{4,})',
        r'\1REDACTED-PASSWORD', text, flags=re.IGNORECASE)

    # Private key blocks
    text = re.sub(
        r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----',
        'REDACTED-PRIVATE-KEY', text, flags=re.DOTALL)

    return text


# Keep legacy alias so existing callers still work
def sanitize_html(html: str) -> str:
    return sanitize_content(html)


def get_domain_name(url):
    """Extract clean domain name from URL"""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    clean_domain = re.sub(r'[^\w\-.]', '_', domain)
    return domain, clean_domain


def handle_pagination_and_tabs(page, url, base_content):
    """
    Handle pagination, tabs, and dynamic content on a page
    Returns aggregated content from all pagination states
    """
    all_items = []
    unique_content = set()

    print(f"  🔍 Checking for tabs and pagination...")

    # Tab selectors to try (common patterns)
    tab_selectors = [
        'button[role="tab"]',
        '[role="tab"]',
        'div[role="tab"]',
        '.tab',
        '[data-tab]',
        'button:has-text("Featured")',
        'button:has-text("Shared")',
        'button:has-text("My")',
    ]

    # Try to find and click through tabs
    tabs_found = []
    for selector in tab_selectors:
        try:
            tabs = page.locator(selector).all()
            if tabs:
                tabs_found = tabs
                print(f"  📑 Found {len(tabs)} tabs")
                break
        except:
            continue

    if tabs_found:
        for idx, tab in enumerate(tabs_found):
            try:
                # Get tab name
                tab_name = tab.inner_text()
                print(f"  📑 Clicking tab: {tab_name}")

                # Click tab
                tab.click()
                time.sleep(2)  # Wait for content to load

                # Handle pagination within this tab
                pagination_content = handle_pagination_controls(page)
                for content in pagination_content:
                    content_str = str(content)
                    if content_str not in unique_content:
                        unique_content.add(content_str)
                        all_items.append({
                            'tab': tab_name,
                            'content': content
                        })

            except Exception as e:
                print(f"    ⚠️  Tab error: {e}")
                continue
    else:
        # No tabs, just handle pagination
        pagination_content = handle_pagination_controls(page)
        for content in pagination_content:
            all_items.append({
                'tab': 'default',
                'content': content
            })

    return all_items


def handle_pagination_controls(page):
    """
    Handle pagination controls (Next button, Load More, etc.)
    Returns list of content from all pages
    """
    all_content = []
    max_pages = 100  # Safety limit for pagination (increased for large agent lists)
    page_count = 0

    # Pagination button selectors (common patterns)
    next_selectors = [
        'button:has-text("Next")',
        'a:has-text("Next")',
        '[aria-label*="next" i]',
        '[aria-label*="Next page" i]',
        'button[aria-label*="next" i]',
        '.pagination button:last-child',
        'button:has-text("Load More")',
        'button:has-text("Show More")',
    ]

    while page_count < max_pages:
        # Capture current page content
        try:
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'lxml')

            # Extract card/item content (adjust selectors based on site structure)
            items = extract_list_items(soup)
            if items:
                all_content.extend(items)
                print(f"    📄 Captured {len(items)} items from page {page_count + 1}")
        except Exception as e:
            print(f"    ⚠️  Content extraction error: {e}")

        # Try to find and click next button
        next_clicked = False
        for selector in next_selectors:
            try:
                next_button = page.locator(selector).first
                if next_button.is_visible() and next_button.is_enabled():
                    print(f"    ➡️  Clicking pagination: {selector}")
                    next_button.click()
                    time.sleep(2)  # Wait for content to load
                    next_clicked = True
                    break
            except:
                continue

        if not next_clicked:
            # No more pagination found
            break

        page_count += 1

        # Safety check - if page hasn't changed, break
        if page_count > 1:
            new_html = page.content()
            if new_html == html_content:
                print(f"    ℹ️  Page content unchanged, ending pagination")
                break

    if page_count > 0:
        print(f"  ✅ Navigated through {page_count + 1} pages of content")

    return all_content


def extract_list_items(soup):
    """
    Extract items from list/grid views
    Returns list of item dictionaries with title, description, etc.
    """
    items = []

    # Common card/item selectors
    card_selectors = [
        {'selector': 'article', 'title': 'h1, h2, h3, h4', 'desc': 'p'},
        {'selector': '[class*="card"]', 'title': 'h1, h2, h3, h4', 'desc': 'p'},
        {'selector': '[class*="item"]', 'title': 'h1, h2, h3, h4', 'desc': 'p'},
        {'selector': '[role="article"]', 'title': 'h1, h2, h3, h4', 'desc': 'p'},
        {'selector': 'li', 'title': 'h1, h2, h3, h4, a', 'desc': 'p, span'},
    ]

    for pattern in card_selectors:
        cards = soup.select(pattern['selector'])
        if cards:
            for card in cards:
                item = {}

                # Extract title
                title_elem = card.select_one(pattern['title'])
                if title_elem:
                    item['title'] = title_elem.get_text(strip=True)

                # Extract description
                desc_elem = card.select_one(pattern['desc'])
                if desc_elem:
                    item['description'] = desc_elem.get_text(strip=True)

                # Extract any links
                links = card.find_all('a', href=True)
                if links:
                    item['links'] = [link.get('href') for link in links]

                # Only add if we found meaningful content
                if item.get('title') or item.get('description'):
                    items.append(item)

            if items:
                break  # Found items with this pattern, no need to try others

    return items


# Get target URL
target_url = sys.argv[1] if len(sys.argv) > 1 else input("Enter URL to crawl: ").strip()
if not target_url.startswith(('http://', 'https://')):
    target_url = 'https://' + target_url

max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 100
max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 4  # Default max depth 4

display_domain, folder_domain = get_domain_name(target_url)
output_dir = f'{folder_domain}_crawl'
os.makedirs(output_dir, exist_ok=True)

print(f"""
╔════════════════════════════════════════════════════════════════╗
║  Playwright Crawler with Pagination Support (Keep Browser)    ║
╚════════════════════════════════════════════════════════════════╝

Target: {target_url}
Output: {output_dir}/
Max Pages: {max_pages}
Max Depth: {max_depth}

Browser will stay open during entire crawl.
Handles tabs, pagination, and dynamic content.

════════════════════════════════════════════════════════════════
""")

if not PLAYWRIGHT_AVAILABLE:
    print("❌ Playwright not installed!")
    print("pip install playwright && playwright install chromium")
    sys.exit(1)

print("Starting in 3 seconds...")
time.sleep(3)

# Tracking
visited_urls = set()
to_visit = [(target_url, 0)]
sitemap = {}
url_categories = {'pages': set(), 'subsites': set(), 'resources': set(), 'external': set()}
failed_urls = {}
pagination_data = {}  # Store paginated content

def is_same_site(url, base_domain):
    """Check if URL belongs to same site"""
    parsed = urlparse(url)
    return base_domain in parsed.netloc

def save_page_content(url, content, html, pagination_items=None):
    """Save page content to files"""
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')

    if not path_parts or not path_parts[0]:
        filename = 'index'
    else:
        filename = '_'.join(path_parts)

    filename = filename[:200]

    # Add pagination data to content
    if pagination_items:
        content['pagination_items'] = pagination_items
        content['pagination_count'] = len(pagination_items)

    # Sanitize JSON before saving
    json_path = os.path.join(output_dir, f"{filename}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(sanitize_content(json.dumps(content, indent=2, ensure_ascii=False)))

    # Sanitize HTML before saving
    sanitized_html = sanitize_content(html)

    # Save HTML
    html_path = os.path.join(output_dir, f"{filename}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(sanitized_html)

    # Build TXT content then sanitize before saving
    txt_lines = []
    txt_lines.append(f"Title: {content['title']}")
    txt_lines.append(f"URL: {url}")
    txt_lines.append(f"Description: {content.get('description', '')}")
    txt_lines.append("")
    txt_lines.append(content.get('text_content', ''))

    if pagination_items:
        txt_lines.append(f"\n\n{'='*80}")
        txt_lines.append(f"PAGINATED ITEMS ({len(pagination_items)} total)")
        txt_lines.append(f"{'='*80}\n")
        for idx, item in enumerate(pagination_items, 1):
            txt_lines.append(f"\n--- Item {idx} ---")
            txt_lines.append(f"Tab: {item.get('tab', 'N/A')}")
            content_data = item.get('content', {})
            txt_lines.append(f"Title: {content_data.get('title', 'N/A')}")
            txt_lines.append(f"Description: {content_data.get('description', 'N/A')}")
            if content_data.get('links'):
                txt_lines.append(f"Links: {', '.join(content_data['links'])}")

    txt_path = os.path.join(output_dir, f"{filename}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(sanitize_content('\n'.join(txt_lines)))

with sync_playwright() as p:
    try:
        print("\n✅ Launching browser...")

        # Launch browser
        browser = None
        try:
            browser = p.chromium.launch(headless=False, channel="msedge")
            print("✅ Using Microsoft Edge")
        except:
            try:
                browser = p.chromium.launch(headless=False, channel="chrome")
                print("✅ Using Google Chrome")
            except:
                browser = p.chromium.launch(headless=False)
                print("✅ Using Chromium")

        context = browser.new_context()
        page = context.new_page()

        print("✅ Browser opened!")
        print(f"Navigating to {target_url}...")

        # Navigate to site
        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)
            print("✅ Page loaded")
        except Exception as e:
            print(f"⚠️  Navigation warning: {e}")

        print("\n" + "="*80)
        print("📋 PLEASE LOGIN NOW:")
        print("="*80)
        print("1. Login with your credentials")
        print("2. Complete any MFA if required")
        print("3. Navigate to the homepage if needed")
        print("\nScript is watching for login completion...")
        print("="*80)

        # Wait for login
        print("\n⏳ Waiting for login...")
        timeout_seconds = 300
        start_time = time.time()
        check_interval = 3

        while True:
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
                time.sleep(1)

                current_title = page.title()
                current_url = page.url

                login_indicators = ["sign in", "log in", "login", "authenticate", "authorization"]
                has_login = any(ind in current_title.lower() for ind in login_indicators)
                has_login_url = any(ind in current_url.lower() for ind in ["login", "signin", "auth", "sso"])

                if not has_login and not has_login_url:
                    print(f"\n✅ Login detected! (Page: '{current_title}')")
                    break
            except:
                pass

            if time.time() - start_time > timeout_seconds:
                print("\n⏱️  Timeout waiting for login")
                browser.close()
                sys.exit(1)

            time.sleep(check_interval)

            elapsed = int(time.time() - start_time)
            if elapsed % 15 == 0 and elapsed > 0:
                print(f"  Still waiting... ({elapsed}s)")

        print("Waiting for page to stabilize...")
        time.sleep(3)

        print("\n" + "="*80)
        print("🕷️  Starting crawl with pagination support...")
        print("="*80)
        print(f"Max pages: {max_pages}")
        print(f"Max depth: {max_depth}")
        print("="*80 + "\n")

        # Main crawl loop
        while to_visit and len(visited_urls) < max_pages:
            url, depth = to_visit.pop(0)

            if url in visited_urls or depth > max_depth:
                continue

            visited_urls.add(url)

            print(f"[Depth {depth}] Crawling: {url}")

            try:
                # Navigate to page
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(2)  # Let JavaScript execute

                # Wait for loading indicators to disappear (async content)
                loading_selectors = [
                    'text="Loading agents..."',
                    'text="Loading..."',
                    '[data-loading="true"]',
                    '.loading',
                    '.spinner'
                ]
                for selector in loading_selectors:
                    try:
                        page.wait_for_selector(selector, state="hidden", timeout=10000)
                        print(f"  ⏳ Waited for dynamic content to load")
                        break
                    except:
                        pass

                # Additional wait for async content
                time.sleep(3)

                # Get initial page content
                html_content = page.content()
                title = page.title()

                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'lxml')

                # Extract metadata
                description = ''
                desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                if desc_tag:
                    description = desc_tag.get('content', '')

                # Handle pagination and tabs
                pagination_items = handle_pagination_and_tabs(page, url, html_content)

                # Get final page state after pagination
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'lxml')

                # Extract links
                links_found = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)

                    # Only add same-site links
                    if is_same_site(full_url, display_domain):
                        # Remove fragments
                        full_url = full_url.split('#')[0]
                        if full_url and full_url not in visited_urls:
                            links_found.append(full_url)
                            if (full_url, depth + 1) not in to_visit:
                                to_visit.append((full_url, depth + 1))

                # Extract text content
                for script in soup(['script', 'style']):
                    script.decompose()
                text_content = soup.get_text(separator='\n', strip=True)

                # Extract headings
                h1_tags = [h.get_text(strip=True) for h in soup.find_all('h1')]
                h2_tags = [h.get_text(strip=True) for h in soup.find_all('h2')]
                h3_tags = [h.get_text(strip=True) for h in soup.find_all('h3')]

                # Store in sitemap
                content = {
                    'url': url,
                    'title': title,
                    'description': description,
                    'h1': h1_tags,
                    'h2': h2_tags,
                    'h3': h3_tags,
                    'text_content': text_content,
                    'links_found': len(links_found),
                    'depth': depth,
                    'crawled_at': datetime.now().isoformat()
                }

                sitemap[url] = content
                url_categories['pages'].add(url)

                if pagination_items:
                    pagination_data[url] = pagination_items

                # Save page content
                save_page_content(url, content, html_content, pagination_items)

                success_msg = f"  ✅ Success: Found {len(links_found)} links"
                if pagination_items:
                    success_msg += f", {len(pagination_items)} paginated items"
                print(success_msg)

                # Delay between requests
                time.sleep(1)

            except Exception as e:
                print(f"  ❌ Failed: {str(e)}")
                failed_urls[url] = str(e)
                import traceback
                traceback.print_exc()

            # Progress update
            if len(visited_urls) % 5 == 0:
                print(f"\n📊 Progress: {len(visited_urls)} pages crawled, {len(to_visit)} in queue\n")

        print("\n" + "="*80)
        print("✅ Crawl Complete!")
        print("="*80)
        print(f"Pages: {len(visited_urls)}")
        print(f"Failed: {len(failed_urls)}")
        if pagination_data:
            total_items = sum(len(items) for items in pagination_data.values())
            print(f"Paginated Items: {total_items}")
        print("="*80 + "\n")

        # Save results
        is_update = os.path.exists(os.path.join(output_dir, 'sitemap.json'))

        if is_update:
            print(f"🔄 Updating existing crawl data for {display_domain}...")
        else:
            print(f"✨ Creating new crawl data for {display_domain}...")

        # Save sitemap
        with open(os.path.join(output_dir, 'sitemap.json'), 'w', encoding='utf-8') as f:
            json.dump(sitemap, f, indent=2, ensure_ascii=False)
        print(f"📄 Saved sitemap: {output_dir}/sitemap.json")

        # Save pagination data
        if pagination_data:
            with open(os.path.join(output_dir, 'pagination_data.json'), 'w', encoding='utf-8') as f:
                json.dump(pagination_data, f, indent=2, ensure_ascii=False)
            print(f"📄 Saved pagination data: {output_dir}/pagination_data.json")

        # Save URLs
        urls_data = {
            'root_url': target_url,
            'base_domain': display_domain,
            'crawled_at': datetime.now().isoformat(),
            'summary': {
                'total_urls': len(visited_urls),
                'pages': len(url_categories['pages']),
                'failed': len(failed_urls),
                'paginated_items': sum(len(items) for items in pagination_data.values()) if pagination_data else 0
            },
            'urls': {
                'pages': sorted(list(url_categories['pages']))
            },
            'failed': failed_urls
        }

        with open(os.path.join(output_dir, 'urls.json'), 'w', encoding='utf-8') as f:
            json.dump(urls_data, f, indent=2, ensure_ascii=False)
        print(f"📄 Saved URLs: {output_dir}/urls.json")

        # Save report
        with open(os.path.join(output_dir, 'report.txt'), 'w', encoding='utf-8') as f:
            f.write(f"Web Crawl Report (with Pagination)\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Root URL: {target_url}\n")
            f.write(f"Base Domain: {display_domain}\n")
            f.write(f"Crawled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Summary\n")
            f.write(f"{'-'*80}\n")
            f.write(f"Total URLs: {len(visited_urls)}\n")
            f.write(f"Pages: {len(url_categories['pages'])}\n")
            f.write(f"Failed: {len(failed_urls)}\n")
            if pagination_data:
                f.write(f"Paginated Items: {sum(len(items) for items in pagination_data.values())}\n")
            f.write(f"\nPages\n")
            f.write(f"{'-'*80}\n")
            for url in sorted(url_categories['pages']):
                f.write(f"{url}\n")
                if url in pagination_data:
                    f.write(f"  └─ {len(pagination_data[url])} paginated items\n")
        print(f"📄 Saved report: {output_dir}/report.txt")

        # Generate markdown summary (with pagination info)
        summary_path = os.path.join(output_dir, 'SUMMARY.md')
        with open(summary_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# {display_domain} - Crawl Summary\n\n")
            f.write(f"**Crawled:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**Root URL:** {target_url}  \n")
            f.write(f"**Total Pages:** {len(visited_urls)}  \n")
            if pagination_data:
                total_items = sum(len(items) for items in pagination_data.values())
                f.write(f"**Paginated Items Captured:** {total_items}  \n")
            f.write("\n---\n\n")

            # Table of contents
            f.write("## 📑 Table of Contents\n\n")
            for idx, url in enumerate(sorted(url_categories['pages']), 1):
                page_name = url.replace(target_url, '').strip('/') or 'Homepage'
                page_name = page_name.replace('/', ' / ')
                anchor = url.replace(target_url, '').strip('/').lower()
                anchor = re.sub(r'[^\w\-/]', '-', anchor) or 'homepage'
                paginated = f" ({len(pagination_data[url])} items)" if url in pagination_data else ""
                f.write(f"{idx}. [{page_name}](#{anchor}){paginated}\n")
            f.write("\n---\n\n")

            # Page summaries
            f.write("## 📄 Page Summaries\n\n")
            for url in sorted(url_categories['pages']):
                if url not in sitemap:
                    continue
                page_data = sitemap[url]
                page_name = url.replace(target_url, '').strip('/') or 'Homepage'
                anchor = url.replace(target_url, '').strip('/').lower()
                anchor = re.sub(r'[^\w\-/]', '-', anchor) or 'homepage'

                f.write(f"### {page_name}\n\n")
                f.write(f"<a id=\"{anchor}\"></a>\n\n")
                f.write(f"**URL:** [{url}]({url})  \n")
                f.write(f"**Title:** {page_data.get('title', 'N/A')}  \n")

                if page_data.get('description'):
                    f.write(f"**Description:** {page_data['description']}  \n")

                f.write(f"**Depth:** {page_data.get('depth', 0)}  \n")

                # Show pagination info
                if url in pagination_data:
                    f.write(f"**Paginated Items:** {len(pagination_data[url])}  \n")

                f.write("\n")

                if page_data.get('h1'):
                    f.write(f"**Main Topics (H1):**\n")
                    for h1 in page_data['h1'][:5]:
                        f.write(f"- {h1}\n")
                    f.write("\n")

                if page_data.get('h2'):
                    f.write(f"**Sections (H2):**\n")
                    for h2 in page_data['h2'][:10]:
                        f.write(f"- {h2}\n")
                    f.write("\n")

                # Show paginated items
                if url in pagination_data:
                    f.write(f"**Captured Items:**\n\n")

                    # Group by tab
                    tabs = {}
                    for item in pagination_data[url]:
                        tab = item.get('tab', 'default')
                        if tab not in tabs:
                            tabs[tab] = []
                        tabs[tab].append(item['content'])

                    for tab, items in tabs.items():
                        if tab != 'default':
                            f.write(f"*{tab} Tab:*\n\n")

                        for idx, item in enumerate(items[:20], 1):  # Limit to first 20
                            title = item.get('title', 'Untitled')
                            desc = item.get('description', '')
                            f.write(f"{idx}. **{title}**")
                            if desc:
                                desc_preview = desc[:100] + "..." if len(desc) > 100 else desc
                                f.write(f" - {desc_preview}")
                            f.write("\n")

                        if len(items) > 20:
                            f.write(f"\n*...and {len(items) - 20} more items*\n")
                        f.write("\n")

                if page_data.get('text_content'):
                    content = page_data['text_content']
                    preview = content[:500].strip()
                    if len(content) > 500:
                        preview += "..."
                    f.write(f"**Content Preview:**\n\n")
                    f.write(f"> {preview}\n\n")

                if page_data.get('links_found'):
                    f.write(f"**Links Found:** {page_data['links_found']}\n\n")

                f.write("---\n\n")

            if failed_urls:
                f.write("## ❌ Failed URLs\n\n")
                for url, error in sorted(failed_urls.items()):
                    f.write(f"- **{url}**\n")
                    f.write(f"  - Error: `{error}`\n\n")

            f.write(f"*Generated by Playwright Crawler with Pagination Support on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        print(f"📄 Saved markdown summary: {summary_path}")

        print(f"\n✅ All results saved to: {output_dir}/")

        print("\n🌐 Closing browser in 5 seconds...")
        time.sleep(5)
        browser.close()
        print("✅ Browser closed")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        try:
            browser.close()
        except:
            pass
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            browser.close()
        except:
            pass
