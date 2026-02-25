#!/usr/bin/env python3
"""
Playwright-based crawler that keeps browser open
Maintains full authentication session and executes JavaScript
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

def get_domain_name(url):
    """Extract clean domain name from URL"""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    clean_domain = re.sub(r'[^\w\-.]', '_', domain)
    return domain, clean_domain

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
║     Playwright Headful Crawler (Keep Browser Open)            ║
╚════════════════════════════════════════════════════════════════╝

Target: {target_url}
Output: {output_dir}/
Max Pages: {max_pages}
Max Depth: {max_depth}

Browser will stay open during entire crawl.
This allows JavaScript execution and maintains full session.

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

def is_same_site(url, base_domain):
    """Check if URL belongs to same site"""
    parsed = urlparse(url)
    return base_domain in parsed.netloc

def save_page_content(url, content, html):
    """Save page content to files"""
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')

    if not path_parts or not path_parts[0]:
        filename = 'index'
    else:
        filename = '_'.join(path_parts)

    filename = filename[:200]

    # Save JSON
    json_path = os.path.join(output_dir, f"{filename}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

    # Save HTML
    html_path = os.path.join(output_dir, f"{filename}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # Save TXT
    txt_path = os.path.join(output_dir, f"{filename}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Title: {content['title']}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Description: {content.get('description', '')}\n\n")
        f.write(content.get('text_content', ''))

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
        print("🕷️  Starting crawl with browser open...")
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
                time.sleep(1)  # Let JavaScript execute

                # Get page content
                html_content = page.content()
                title = page.title()

                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'lxml')

                # Extract metadata
                description = ''
                desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                if desc_tag:
                    description = desc_tag.get('content', '')

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

                # Save page content
                save_page_content(url, content, html_content)

                print(f"  ✅ Success: Found {len(links_found)} links")

                # Delay between requests
                time.sleep(1)

            except Exception as e:
                print(f"  ❌ Failed: {str(e)}")
                failed_urls[url] = str(e)

            # Progress update
            if len(visited_urls) % 5 == 0:
                print(f"\n📊 Progress: {len(visited_urls)} pages crawled, {len(to_visit)} in queue\n")

        print("\n" + "="*80)
        print("✅ Crawl Complete!")
        print("="*80)
        print(f"Pages: {len(visited_urls)}")
        print(f"Failed: {len(failed_urls)}")
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

        # Save URLs
        urls_data = {
            'root_url': target_url,
            'base_domain': display_domain,
            'crawled_at': datetime.now().isoformat(),
            'summary': {
                'total_urls': len(visited_urls),
                'pages': len(url_categories['pages']),
                'failed': len(failed_urls)
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
            f.write(f"Web Crawl Report\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Root URL: {target_url}\n")
            f.write(f"Base Domain: {display_domain}\n")
            f.write(f"Crawled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Summary\n")
            f.write(f"{'-'*80}\n")
            f.write(f"Total URLs: {len(visited_urls)}\n")
            f.write(f"Pages: {len(url_categories['pages'])}\n")
            f.write(f"Failed: {len(failed_urls)}\n\n")
            f.write(f"Pages\n")
            f.write(f"{'-'*80}\n")
            for url in sorted(url_categories['pages']):
                f.write(f"{url}\n")
        print(f"📄 Saved report: {output_dir}/report.txt")

        # Generate markdown summary
        summary_path = os.path.join(output_dir, 'SUMMARY.md')
        with open(summary_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# {display_domain} - Crawl Summary\n\n")
            f.write(f"**Crawled:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**Root URL:** {target_url}  \n")
            f.write(f"**Total Pages:** {len(visited_urls)}  \n\n")
            f.write("---\n\n")

            # Table of contents
            f.write("## 📑 Table of Contents\n\n")
            for idx, url in enumerate(sorted(url_categories['pages']), 1):
                page_name = url.replace(target_url, '').strip('/') or 'Homepage'
                page_name = page_name.replace('/', ' / ')
                anchor = url.replace(target_url, '').strip('/').lower()
                anchor = re.sub(r'[^\w\-/]', '-', anchor) or 'homepage'
                f.write(f"{idx}. [{page_name}](#{anchor})\n")
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

                f.write(f"**Depth:** {page_data.get('depth', 0)}  \n\n")

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

            f.write(f"*Generated by Playwright Headful Crawler on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

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
