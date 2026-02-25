#!/usr/bin/env python3
"""
Universal Web Crawler
Scrapes all content and URLs from a website and its subsites/subpages
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
import os
from datetime import datetime
from collections import defaultdict
import re
from typing import Set, Dict, List
import argparse


class WebCrawler:
    def __init__(self, root_url: str, config: Dict = None):
        """
        Initialize the web crawler

        Args:
            root_url: Starting URL to crawl
            config: Configuration dictionary
        """
        self.root_url = root_url
        self.parsed_root = urlparse(root_url)
        self.base_domain = self.parsed_root.netloc

        # Default configuration
        self.config = {
            'max_pages': 1000,
            'delay': 1.0,  # Seconds between requests
            'include_subdomains': True,
            'include_external': False,
            'max_depth': 10,
            'timeout': 30,
            'user_agent': 'Mozilla/5.0 (compatible; WebCrawler/1.0)',
            'save_content': True,
            'output_dir': 'crawl_output',
            'exclude_patterns': [
                r'/logout', r'/signout', r'/sign-out',
                r'/delete', r'/remove'
            ],
            'file_extensions': [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx',
                '.ppt', '.pptx', '.zip', '.tar', '.gz',
                '.csv', '.json', '.xml'
            ]
        }

        # Update with user config
        if config:
            self.config.update(config)

        # Tracking sets
        self.visited_urls: Set[str] = set()
        self.to_visit: List[tuple] = [(root_url, 0)]  # (url, depth)
        self.failed_urls: Dict[str, str] = {}

        # Results storage
        self.sitemap: Dict[str, Dict] = {}
        self.url_categories = {
            'pages': set(),
            'subsites': set(),
            'resources': set(),
            'external': set()
        }

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config['user_agent']
        })

        # Create output directory
        os.makedirs(self.config['output_dir'], exist_ok=True)

    def is_same_site(self, url: str) -> bool:
        """Check if URL belongs to the same site"""
        parsed = urlparse(url)

        if self.config['include_subdomains']:
            # Match base domain and all subdomains
            base_parts = self.base_domain.split('.')
            url_parts = parsed.netloc.split('.')

            # Get root domain (last 2 parts)
            base_root = '.'.join(base_parts[-2:]) if len(base_parts) >= 2 else self.base_domain
            url_root = '.'.join(url_parts[-2:]) if len(url_parts) >= 2 else parsed.netloc

            return base_root == url_root
        else:
            # Exact domain match
            return parsed.netloc == self.base_domain

    def should_exclude(self, url: str) -> bool:
        """Check if URL matches exclusion patterns"""
        for pattern in self.config['exclude_patterns']:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False

    def categorize_url(self, url: str) -> str:
        """Categorize URL type"""
        parsed = urlparse(url)

        # Check if it's external
        if not self.is_same_site(url):
            return 'external'

        # Check if it's a resource (file)
        for ext in self.config['file_extensions']:
            if parsed.path.lower().endswith(ext):
                return 'resources'

        # Check if it's a subsite (different subdomain)
        if parsed.netloc != self.base_domain:
            return 'subsites'

        # Regular page
        return 'pages'

    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and query params"""
        parsed = urlparse(url)
        # Keep scheme, netloc, and path only
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        # Remove trailing slash unless it's the root
        if normalized.endswith('/') and len(parsed.path) > 1:
            normalized = normalized[:-1]
        return normalized

    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all links from the page"""
        links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            # Make absolute URL
            absolute_url = urljoin(current_url, href)
            # Normalize
            normalized = self.normalize_url(absolute_url)

            # Skip if excluded
            if self.should_exclude(normalized):
                continue

            # Add if same site or including external
            if self.is_same_site(normalized) or self.config['include_external']:
                links.append(normalized)

        return links

    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract page content and metadata"""
        content = {
            'url': url,
            'title': '',
            'description': '',
            'keywords': '',
            'h1': [],
            'h2': [],
            'h3': [],
            'text_content': '',
            'links': [],
            'images': [],
            'meta': {}
        }

        # Title
        title_tag = soup.find('title')
        content['title'] = title_tag.get_text(strip=True) if title_tag else ''

        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content_attr = meta.get('content', '')
            if name:
                content['meta'][name] = content_attr

                # Common meta tags
                if name.lower() == 'description':
                    content['description'] = content_attr
                elif name.lower() == 'keywords':
                    content['keywords'] = content_attr

        # Headings
        content['h1'] = [h.get_text(strip=True) for h in soup.find_all('h1')]
        content['h2'] = [h.get_text(strip=True) for h in soup.find_all('h2')]
        content['h3'] = [h.get_text(strip=True) for h in soup.find_all('h3')]

        # Main text content (excluding scripts and styles)
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)
        content['text_content'] = ' '.join(text.split())  # Clean whitespace

        # Links
        content['links'] = [
            {'text': link.get_text(strip=True), 'href': link.get('href', '')}
            for link in soup.find_all('a', href=True)
        ]

        # Images
        content['images'] = [
            {'alt': img.get('alt', ''), 'src': img.get('src', '')}
            for img in soup.find_all('img')
        ]

        return content

    def save_page_content(self, url: str, content: Dict, html: str):
        """Save page content to files"""
        # Create safe filename from URL
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')

        if not path_parts or not path_parts[0]:
            filename = 'index'
        else:
            filename = '_'.join(path_parts)

        # Limit filename length
        filename = filename[:200]

        # Save JSON metadata
        json_path = os.path.join(self.config['output_dir'], f"{filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

        # Save HTML
        html_path = os.path.join(self.config['output_dir'], f"{filename}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # Save text content
        txt_path = os.path.join(self.config['output_dir'], f"{filename}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {content['title']}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Description: {content['description']}\n\n")
            f.write(content['text_content'])

    def crawl_page(self, url: str, depth: int) -> bool:
        """Crawl a single page"""
        try:
            print(f"[Depth {depth}] Crawling: {url}")

            # Make request
            response = self.session.get(
                url,
                timeout=self.config['timeout'],
                allow_redirects=True
            )
            response.raise_for_status()

            # Check if it's HTML
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                print(f"  ⚠️  Skipped (not HTML): {content_type}")
                self.url_categories[self.categorize_url(url)].add(url)
                return False

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract content
            content = self.extract_content(soup, url)
            content['depth'] = depth
            content['status_code'] = response.status_code
            content['crawled_at'] = datetime.now().isoformat()

            # Save to sitemap
            self.sitemap[url] = content

            # Categorize URL
            category = self.categorize_url(url)
            self.url_categories[category].add(url)

            # Save content to files
            if self.config['save_content']:
                self.save_page_content(url, content, response.text)

            # Extract and queue new links
            if depth < self.config['max_depth']:
                links = self.extract_links(soup, url)
                for link in links:
                    if link not in self.visited_urls and link not in [u for u, d in self.to_visit]:
                        self.to_visit.append((link, depth + 1))

            print(f"  ✅ Success: Found {len(content['links'])} links")
            return True

        except requests.RequestException as e:
            print(f"  ❌ Failed: {str(e)}")
            self.failed_urls[url] = str(e)
            return False
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.failed_urls[url] = str(e)
            return False

    def crawl(self):
        """Main crawl loop"""
        print(f"\n{'='*80}")
        print(f"🕷️  Starting Web Crawler")
        print(f"{'='*80}")
        print(f"Root URL: {self.root_url}")
        print(f"Base Domain: {self.base_domain}")
        print(f"Max Pages: {self.config['max_pages']}")
        print(f"Max Depth: {self.config['max_depth']}")
        print(f"Output Dir: {self.config['output_dir']}")
        print(f"{'='*80}\n")

        start_time = time.time()

        while self.to_visit and len(self.visited_urls) < self.config['max_pages']:
            url, depth = self.to_visit.pop(0)

            # Skip if already visited
            if url in self.visited_urls:
                continue

            # Mark as visited
            self.visited_urls.add(url)

            # Crawl the page
            self.crawl_page(url, depth)

            # Delay between requests
            time.sleep(self.config['delay'])

            # Progress update
            if len(self.visited_urls) % 10 == 0:
                print(f"\n📊 Progress: {len(self.visited_urls)} pages crawled, {len(self.to_visit)} in queue\n")

        elapsed = time.time() - start_time

        print(f"\n{'='*80}")
        print(f"✅ Crawling Complete!")
        print(f"{'='*80}")
        print(f"Pages Crawled: {len(self.visited_urls)}")
        print(f"Failed Pages: {len(self.failed_urls)}")
        print(f"Time Elapsed: {elapsed:.2f} seconds")
        print(f"{'='*80}\n")

        # Save final results
        self.save_results()

    def save_results(self):
        """Save crawl results"""
        # Check if this is an update or new crawl
        sitemap_path = os.path.join(self.config['output_dir'], 'sitemap.json')
        is_update = os.path.exists(sitemap_path)

        if is_update:
            print(f"\n🔄 Updating existing crawl data for {self.base_domain}...")
        else:
            print(f"\n✨ Creating new crawl data for {self.base_domain}...")

        # Complete sitemap (no timestamp, always overwrites)
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            json.dump(self.sitemap, f, indent=2, ensure_ascii=False)
        print(f"📄 Saved complete sitemap: {sitemap_path}")

        # URL list by category
        urls_data = {
            'root_url': self.root_url,
            'base_domain': self.base_domain,
            'crawled_at': datetime.now().isoformat(),
            'summary': {
                'total_urls': len(self.visited_urls),
                'pages': len(self.url_categories['pages']),
                'subsites': len(self.url_categories['subsites']),
                'resources': len(self.url_categories['resources']),
                'external': len(self.url_categories['external']),
                'failed': len(self.failed_urls)
            },
            'urls': {
                'pages': sorted(list(self.url_categories['pages'])),
                'subsites': sorted(list(self.url_categories['subsites'])),
                'resources': sorted(list(self.url_categories['resources'])),
                'external': sorted(list(self.url_categories['external']))
            },
            'failed': self.failed_urls
        }

        urls_path = os.path.join(self.config['output_dir'], 'urls.json')
        with open(urls_path, 'w', encoding='utf-8') as f:
            json.dump(urls_data, f, indent=2, ensure_ascii=False)
        print(f"📄 Saved URL list: {urls_path}")

        # Text report (no timestamp)
        report_path = os.path.join(self.config['output_dir'], 'report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Web Crawl Report\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Root URL: {self.root_url}\n")
            f.write(f"Base Domain: {self.base_domain}\n")
            f.write(f"Crawled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write(f"Summary\n")
            f.write(f"{'-'*80}\n")
            f.write(f"Total URLs Crawled: {len(self.visited_urls)}\n")
            f.write(f"Pages: {len(self.url_categories['pages'])}\n")
            f.write(f"Subsites: {len(self.url_categories['subsites'])}\n")
            f.write(f"Resources: {len(self.url_categories['resources'])}\n")
            f.write(f"External Links: {len(self.url_categories['external'])}\n")
            f.write(f"Failed: {len(self.failed_urls)}\n\n")

            f.write(f"Pages\n")
            f.write(f"{'-'*80}\n")
            for url in sorted(self.url_categories['pages']):
                f.write(f"{url}\n")

            f.write(f"\nSubsites\n")
            f.write(f"{'-'*80}\n")
            for url in sorted(self.url_categories['subsites']):
                f.write(f"{url}\n")

            f.write(f"\nResources\n")
            f.write(f"{'-'*80}\n")
            for url in sorted(self.url_categories['resources']):
                f.write(f"{url}\n")

            if self.config['include_external']:
                f.write(f"\nExternal Links\n")
                f.write(f"{'-'*80}\n")
                for url in sorted(self.url_categories['external']):
                    f.write(f"{url}\n")

            if self.failed_urls:
                f.write(f"\nFailed URLs\n")
                f.write(f"{'-'*80}\n")
                for url, error in self.failed_urls.items():
                    f.write(f"{url}\n  Error: {error}\n\n")

        print(f"📄 Saved text report: {report_path}")

        # Generate markdown summary
        self.save_markdown_summary()

        print(f"\n✅ All results saved to: {self.config['output_dir']}/")

    def save_markdown_summary(self):
        """Generate a markdown file with content summaries for each page"""
        summary_path = os.path.join(self.config['output_dir'], 'SUMMARY.md')

        with open(summary_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# {self.base_domain} - Crawl Summary\n\n")
            f.write(f"**Crawled:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**Root URL:** {self.root_url}  \n")
            f.write(f"**Total Pages:** {len(self.visited_urls)}  \n\n")
            f.write("---\n\n")

            # Table of contents
            f.write("## 📑 Table of Contents\n\n")
            for idx, url in enumerate(sorted(self.url_categories['pages']), 1):
                # Create clean page name from URL
                page_name = url.replace(self.root_url, '').strip('/') or 'Homepage'
                page_name = page_name.replace('/', ' / ')
                f.write(f"{idx}. [{page_name}](#{self._make_anchor(url)})\n")
            f.write("\n---\n\n")

            # Page summaries
            f.write("## 📄 Page Summaries\n\n")

            for url in sorted(self.url_categories['pages']):
                if url not in self.sitemap:
                    continue

                page_data = self.sitemap[url]
                page_name = url.replace(self.root_url, '').strip('/') or 'Homepage'

                # Page header
                f.write(f"### {page_name}\n\n")
                f.write(f"<a id=\"{self._make_anchor(url)}\"></a>\n\n")
                f.write(f"**URL:** [{url}]({url})  \n")
                f.write(f"**Title:** {page_data.get('title', 'N/A')}  \n")

                if page_data.get('description'):
                    f.write(f"**Description:** {page_data['description']}  \n")

                f.write(f"**Depth:** {page_data.get('depth', 0)}  \n\n")

                # Headings
                if page_data.get('h1'):
                    f.write(f"**Main Topics (H1):**\n")
                    for h1 in page_data['h1'][:5]:  # Limit to first 5
                        f.write(f"- {h1}\n")
                    f.write("\n")

                if page_data.get('h2'):
                    f.write(f"**Sections (H2):**\n")
                    for h2 in page_data['h2'][:10]:  # Limit to first 10
                        f.write(f"- {h2}\n")
                    f.write("\n")

                # Content preview
                if page_data.get('text_content'):
                    content = page_data['text_content']
                    # Get first 500 characters as preview
                    preview = content[:500].strip()
                    if len(content) > 500:
                        preview += "..."
                    f.write(f"**Content Preview:**\n\n")
                    f.write(f"> {preview}\n\n")

                # Links found
                if page_data.get('links_found'):
                    f.write(f"**Links Found:** {page_data['links_found']}\n\n")

                f.write("---\n\n")

            # Resources section
            if self.url_categories['resources']:
                f.write("## 📦 Resources\n\n")
                for url in sorted(self.url_categories['resources']):
                    resource_name = url.split('/')[-1]
                    f.write(f"- [{resource_name}]({url})\n")
                f.write("\n---\n\n")

            # Subsites section
            if self.url_categories['subsites']:
                f.write("## 🔗 Related Subsites\n\n")
                for url in sorted(self.url_categories['subsites']):
                    f.write(f"- [{url}]({url})\n")
                f.write("\n---\n\n")

            # Failed URLs
            if self.failed_urls:
                f.write("## ❌ Failed URLs\n\n")
                for url, error in sorted(self.failed_urls.items()):
                    f.write(f"- **{url}**\n")
                    f.write(f"  - Error: `{error}`\n\n")
                f.write("---\n\n")

            # Footer
            f.write(f"*Generated by Web Crawler on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        print(f"📄 Saved markdown summary: {summary_path}")

    def _make_anchor(self, url):
        """Create URL-safe anchor from URL"""
        anchor = url.replace(self.root_url, '').strip('/').lower()
        anchor = re.sub(r'[^\w\-/]', '-', anchor)
        anchor = re.sub(r'-+', '-', anchor)
        return anchor or 'homepage'

def main():
    parser = argparse.ArgumentParser(
        description='Universal Web Crawler - Scrape content and map all URLs'
    )
    parser.add_argument('url', help='Root URL to start crawling')
    parser.add_argument('--max-pages', type=int, default=1000, help='Maximum pages to crawl')
    parser.add_argument('--max-depth', type=int, default=4, help='Maximum crawl depth (default: 4)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--output-dir', default='crawl_output', help='Output directory')
    parser.add_argument('--no-subdomains', action='store_true', help='Exclude subdomains')
    parser.add_argument('--include-external', action='store_true', help='Include external links')
    parser.add_argument('--no-save', action='store_true', help='Do not save page content')

    args = parser.parse_args()

    config = {
        'max_pages': args.max_pages,
        'max_depth': args.max_depth,
        'delay': args.delay,
        'output_dir': args.output_dir,
        'include_subdomains': not args.no_subdomains,
        'include_external': args.include_external,
        'save_content': not args.no_save
    }

    crawler = WebCrawler(args.url, config)

    try:
        crawler.crawl()
    except KeyboardInterrupt:
        print("\n\n⚠️  Crawl interrupted by user")
        crawler.save_results()
        print("Partial results saved.")


if __name__ == '__main__':
    main()
