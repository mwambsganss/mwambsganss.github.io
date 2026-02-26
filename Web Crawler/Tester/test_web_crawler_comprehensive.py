#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Web Crawler
Tests all components with data staging and fixtures
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from bs4 import BeautifulSoup
import os
import json
import sys
from pathlib import Path

# Add parent directory to path
PARENT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PARENT_DIR))

from web_crawler import WebCrawler, sanitize_html


class TestSanitizeHTML:
    """Test the sanitize_html function for secret removal using staged test data"""

    def test_sanitize_azure_client_secret(self, test_secrets_data):
        """Test sanitization of Azure AD client secrets"""
        for secret in test_secrets_data['secrets']['azure_client_secrets']:
            html = f'client_secret="{secret}"'
            result = sanitize_html(html)
            assert 'REDACTED-SECRET' in result
            assert secret not in result
            assert 'Q~' not in result  # Pattern should be removed

    def test_sanitize_client_id_uuid(self, test_secrets_data):
        """Test sanitization of Azure client IDs (UUIDs)"""
        for client_id in test_secrets_data['secrets']['azure_client_ids']:
            html = f'clientId: "{client_id}"'
            result = sanitize_html(html)
            assert 'REDACTED-UUID' in result
            assert client_id not in result

    def test_sanitize_bearer_token(self, test_secrets_data):
        """Test sanitization of Bearer tokens"""
        for token in test_secrets_data['secrets']['bearer_tokens']:
            html = f'Authorization: {token}'
            result = sanitize_html(html)
            assert 'REDACTED-TOKEN' in result
            # Extract just the token part (after 'Bearer ')
            token_value = token.replace('Bearer ', '')
            assert token_value not in result

    def test_sanitize_api_key(self, test_secrets_data):
        """Test sanitization of API keys"""
        for api_key in test_secrets_data['secrets']['api_keys']:
            html = f'api_key: "{api_key}"'
            result = sanitize_html(html)
            assert 'REDACTED-API-KEY' in result
            assert api_key not in result

    def test_sanitize_access_token(self, test_secrets_data):
        """Test sanitization of access tokens"""
        for token in test_secrets_data['secrets']['access_tokens']:
            html = f'access_token = "{token}"'
            result = sanitize_html(html)
            assert 'REDACTED-TOKEN' in result
            assert token not in result

    def test_sanitize_full_html_with_secrets(self, sample_html_with_secrets, expected_sanitized_patterns, secret_patterns_to_remove):
        """Test sanitization of complete HTML file with multiple secrets"""
        result = sanitize_html(sample_html_with_secrets)

        # All redaction patterns should be present
        for pattern in expected_sanitized_patterns:
            assert pattern in result, f"Expected pattern '{pattern}' not found in sanitized HTML"

        # No secret patterns should remain
        for pattern in secret_patterns_to_remove:
            assert pattern not in result, f"Secret pattern '{pattern}' still present after sanitization"

    def test_preserve_normal_content(self, sample_html_clean):
        """Test that normal content is preserved during sanitization"""
        result = sanitize_html(sample_html_clean)
        assert result == sample_html_clean
        assert 'Welcome to Test Page' in result
        assert '<h1>' in result
        assert 'Documentation' in result


class TestWebCrawlerInit:
    """Test WebCrawler initialization"""

    def test_init_with_default_config(self, temp_output_dir):
        """Test initialization with default configuration"""
        crawler = WebCrawler("https://example.com")
        assert crawler.root_url == "https://example.com"
        assert crawler.base_domain == "example.com"
        assert crawler.config['max_pages'] == 1000
        assert crawler.config['delay'] == 1.0

    def test_init_with_custom_config(self, temp_output_dir):
        """Test initialization with custom configuration"""
        config = {
            'max_pages': 50,
            'delay': 2.0,
            'output_dir': temp_output_dir
        }
        crawler = WebCrawler("https://example.com", config)
        assert crawler.config['max_pages'] == 50
        assert crawler.config['delay'] == 2.0
        assert crawler.config['output_dir'] == temp_output_dir

    def test_creates_output_directory(self, temp_output_dir):
        """Test that output directory is created"""
        config = {'output_dir': temp_output_dir}
        crawler = WebCrawler("https://example.com", config)
        assert os.path.exists(temp_output_dir)

    def test_init_with_subdomain(self):
        """Test initialization with subdomain URL"""
        crawler = WebCrawler("https://blog.example.com")
        assert crawler.base_domain == "blog.example.com"

    def test_init_with_path(self):
        """Test initialization with URL containing path"""
        crawler = WebCrawler("https://example.com/subdir/page")
        assert crawler.root_url == "https://example.com/subdir/page"
        assert crawler.base_domain == "example.com"


class TestWebCrawlerURLHandling:
    """Test URL categorization and normalization"""

    def test_is_same_site_exact_match(self, basic_crawler):
        """Test same site detection with exact domain match"""
        assert basic_crawler.is_same_site("https://example.com/page")
        assert not basic_crawler.is_same_site("https://other.com")

    def test_is_same_site_subdomain(self, crawler_with_subdomains):
        """Test same site detection with subdomains"""
        assert crawler_with_subdomains.is_same_site("https://sub.example.com")
        assert crawler_with_subdomains.is_same_site("https://blog.example.com")
        assert not crawler_with_subdomains.is_same_site("https://example.org")

    def test_is_same_site_without_subdomains(self, basic_crawler):
        """Test same site detection excluding subdomains"""
        basic_crawler.config['include_subdomains'] = False
        assert not basic_crawler.is_same_site("https://sub.example.com")
        assert basic_crawler.is_same_site("https://example.com/page")

    def test_normalize_url_removes_fragment(self, basic_crawler):
        """Test URL normalization removes fragments"""
        url = "https://example.com/page#section"
        normalized = basic_crawler.normalize_url(url)
        assert normalized == "https://example.com/page"
        assert '#' not in normalized

    def test_normalize_url_removes_query_params(self, basic_crawler):
        """Test URL normalization removes query parameters"""
        url = "https://example.com/page?param=value&foo=bar"
        normalized = basic_crawler.normalize_url(url)
        assert normalized == "https://example.com/page"
        assert '?' not in normalized

    def test_normalize_url_trailing_slash(self, basic_crawler):
        """Test URL normalization handles trailing slashes"""
        url = "https://example.com/page/"
        normalized = basic_crawler.normalize_url(url)
        assert normalized == "https://example.com/page"

        # Root URL should keep trailing slash
        root_url = "https://example.com/"
        normalized_root = basic_crawler.normalize_url(root_url)
        assert normalized_root == "https://example.com/"

    def test_should_exclude_logout_urls(self, basic_crawler):
        """Test exclusion of logout and dangerous URLs"""
        assert basic_crawler.should_exclude("https://example.com/logout")
        assert basic_crawler.should_exclude("https://example.com/signout")
        assert basic_crawler.should_exclude("https://example.com/sign-out")
        assert basic_crawler.should_exclude("https://example.com/delete")
        assert basic_crawler.should_exclude("https://example.com/remove")
        assert not basic_crawler.should_exclude("https://example.com/normal-page")

    def test_categorize_url_external(self, basic_crawler):
        """Test URL categorization for external links"""
        category = basic_crawler.categorize_url("https://external.com")
        assert category == "external"

    def test_categorize_url_resources(self, basic_crawler):
        """Test URL categorization for resource files"""
        assert basic_crawler.categorize_url("https://example.com/file.pdf") == "resources"
        assert basic_crawler.categorize_url("https://example.com/doc.docx") == "resources"
        assert basic_crawler.categorize_url("https://example.com/data.csv") == "resources"
        assert basic_crawler.categorize_url("https://example.com/archive.zip") == "resources"

    def test_categorize_url_subsite(self, crawler_with_subdomains):
        """Test URL categorization for subsites"""
        category = crawler_with_subdomains.categorize_url("https://blog.example.com")
        assert category == "subsites"

    def test_categorize_url_page(self, basic_crawler):
        """Test URL categorization for regular pages"""
        category = basic_crawler.categorize_url("https://example.com/page")
        assert category == "pages"


class TestWebCrawlerExtraction:
    """Test content extraction from HTML using staged test data"""

    def test_extract_content_title(self, basic_crawler, sample_soup_clean):
        """Test extraction of page title"""
        content = basic_crawler.extract_content(sample_soup_clean, "https://example.com")
        assert content['title'] == "Clean Test Page"

    def test_extract_content_meta_description(self, basic_crawler, sample_soup_clean):
        """Test extraction of meta description"""
        content = basic_crawler.extract_content(sample_soup_clean, "https://example.com")
        assert content['description'] == "A clean page without any secrets"

    def test_extract_content_meta_keywords(self, basic_crawler, sample_soup_clean):
        """Test extraction of meta keywords"""
        content = basic_crawler.extract_content(sample_soup_clean, "https://example.com")
        assert content['keywords'] == "test, clean, sample"

    def test_extract_content_headings(self, basic_crawler, sample_soup_clean):
        """Test extraction of heading tags"""
        content = basic_crawler.extract_content(sample_soup_clean, "https://example.com")
        assert len(content['h1']) == 1
        assert "Welcome to Test Page" in content['h1']
        assert len(content['h2']) >= 2
        assert len(content['h3']) >= 2

    def test_extract_content_text(self, basic_crawler, sample_soup_clean):
        """Test extraction of text content"""
        content = basic_crawler.extract_content(sample_soup_clean, "https://example.com")
        assert 'clean test page' in content['text_content'].lower()
        assert 'introduction' in content['text_content'].lower()

    def test_extract_content_links(self, basic_crawler, sample_soup_clean):
        """Test extraction of links from page"""
        content = basic_crawler.extract_content(sample_soup_clean, "https://example.com")
        assert len(content['links']) > 0
        # Check that links have expected structure
        for link in content['links']:
            assert 'text' in link
            assert 'href' in link

    def test_extract_content_images(self, basic_crawler, sample_soup_clean):
        """Test extraction of images from page"""
        content = basic_crawler.extract_content(sample_soup_clean, "https://example.com")
        assert len(content['images']) >= 2
        # Check that images have expected structure
        for img in content['images']:
            assert 'alt' in img
            assert 'src' in img

    def test_extract_links_internal_only(self, basic_crawler, sample_soup_with_links):
        """Test extraction of internal links only"""
        basic_crawler.config['include_external'] = False
        links = basic_crawler.extract_links(sample_soup_with_links, "https://example.com")

        # Should include internal links
        assert any('example.com' in link for link in links)
        # Should not include external links
        assert not any('google.com' in link for link in links)
        assert not any('github.com' in link for link in links)

    def test_extract_links_with_external(self, crawler_with_external, sample_soup_with_links):
        """Test extraction including external links"""
        links = crawler_with_external.extract_links(sample_soup_with_links, "https://example.com")

        # Should include external links when configured
        assert any('google.com' in link or 'github.com' in link for link in links)

    def test_extract_links_excludes_filtered(self, basic_crawler, sample_soup_with_links):
        """Test that excluded URLs are filtered out"""
        links = basic_crawler.extract_links(sample_soup_with_links, "https://example.com")

        # Should not include logout/delete links
        assert not any('/logout' in link for link in links)
        assert not any('/signout' in link for link in links)
        assert not any('/delete' in link for link in links)


class TestWebCrawlerCrawlPage:
    """Test the main crawl_page method with mocking"""

    @patch('web_crawler.requests.Session.get')
    def test_crawl_page_success(self, mock_get, basic_crawler, mock_response_html):
        """Test successful page crawl"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html; charset=utf-8'}
        mock_response.text = mock_response_html
        mock_get.return_value = mock_response

        result = basic_crawler.crawl_page("https://example.com", 0)

        assert result is True
        assert "https://example.com" in basic_crawler.sitemap
        assert basic_crawler.sitemap["https://example.com"]['title'] == "Mock Page"
        mock_get.assert_called_once()

    @patch('web_crawler.requests.Session.get')
    def test_crawl_page_non_html(self, mock_get, basic_crawler):
        """Test crawling non-HTML content"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_get.return_value = mock_response

        result = basic_crawler.crawl_page("https://example.com/file.pdf", 0)

        assert result is False

    @patch('web_crawler.requests.Session.get')
    def test_crawl_page_request_exception(self, mock_get, basic_crawler):
        """Test handling of request exceptions"""
        mock_get.side_effect = requests.RequestException("Connection error")

        result = basic_crawler.crawl_page("https://example.com", 0)

        assert result is False
        assert "https://example.com" in basic_crawler.failed_urls
        assert "Connection error" in basic_crawler.failed_urls["https://example.com"]

    @patch('web_crawler.requests.Session.get')
    def test_crawl_page_timeout(self, mock_get, basic_crawler):
        """Test handling of timeout errors"""
        mock_get.side_effect = requests.Timeout("Request timeout")

        result = basic_crawler.crawl_page("https://example.com", 0)

        assert result is False
        assert "https://example.com" in basic_crawler.failed_urls

    @patch('web_crawler.requests.Session.get')
    def test_crawl_page_respects_max_depth(self, mock_get, basic_crawler, mock_response_html):
        """Test that crawling respects max depth setting"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = mock_response_html
        mock_get.return_value = mock_response

        # Set max depth and crawl at that depth
        basic_crawler.config['max_depth'] = 2
        # Clear the initial to_visit queue (which contains root URL from __init__)
        basic_crawler.to_visit = []
        basic_crawler.crawl_page("https://example.com", 2)

        # Should not add new URLs to queue at max depth
        assert len(basic_crawler.to_visit) == 0

    @patch('web_crawler.requests.Session.get')
    def test_crawl_page_adds_links_to_queue(self, mock_get, basic_crawler, mock_response_html):
        """Test that discovered links are added to crawl queue"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = mock_response_html
        mock_get.return_value = mock_response

        initial_queue_size = len(basic_crawler.to_visit)
        basic_crawler.crawl_page("https://example.com", 0)

        # Should have added links to queue
        assert len(basic_crawler.to_visit) > initial_queue_size


class TestWebCrawlerFileOperations:
    """Test file saving operations with actual file I/O"""

    def test_save_page_content_creates_files(self, basic_crawler):
        """Test that save_page_content creates all expected files"""
        content = {
            'title': 'Test Page',
            'description': 'Test description',
            'text_content': 'Test content here'
        }
        html = "<html><body>Test</body></html>"

        basic_crawler.save_page_content("https://example.com/test-page", content, html)

        # Check files were created
        files = os.listdir(basic_crawler.config['output_dir'])
        assert 'test-page.json' in files
        assert 'test-page.html' in files
        assert 'test-page.txt' in files

    def test_save_page_content_sanitizes_html(self, basic_crawler, sample_html_with_secrets):
        """Test that HTML is sanitized before saving"""
        content = {'title': 'Test', 'text_content': 'Content', 'description': ''}

        basic_crawler.save_page_content("https://example.com", content, sample_html_with_secrets)

        # Read saved HTML and verify sanitization
        html_path = os.path.join(basic_crawler.config['output_dir'], 'index.html')
        with open(html_path, 'r') as f:
            saved_html = f.read()

        # Should contain redacted patterns
        assert 'REDACTED-SECRET' in saved_html or 'REDACTED-UUID' in saved_html
        # Should not contain actual secrets
        assert '.nt8Q~' not in saved_html

    def test_save_page_content_json_structure(self, basic_crawler):
        """Test that saved JSON has correct structure"""
        content = {
            'title': 'Test Page',
            'description': 'Description',
            'text_content': 'Content',
            'h1': ['Heading'],
            'h2': ['Subheading']
        }
        html = "<html><body>Test</body></html>"

        basic_crawler.save_page_content("https://example.com/page", content, html)

        # Read and verify JSON structure
        json_path = os.path.join(basic_crawler.config['output_dir'], 'page.json')
        with open(json_path, 'r') as f:
            saved_data = json.load(f)

        assert saved_data['title'] == 'Test Page'
        assert saved_data['description'] == 'Description'
        assert 'h1' in saved_data
        assert 'h2' in saved_data

    def test_save_results_creates_summary_files(self, basic_crawler):
        """Test that save_results creates all summary files"""
        # Add some data to sitemap
        basic_crawler.sitemap['https://example.com'] = {
            'title': 'Test',
            'text_content': 'Content',
            'description': 'Desc'
        }
        basic_crawler.url_categories['pages'].add('https://example.com')
        basic_crawler.visited_urls.add('https://example.com')

        basic_crawler.save_results()

        # Check summary files were created
        files = os.listdir(basic_crawler.config['output_dir'])
        assert 'sitemap.json' in files
        assert 'urls.json' in files
        assert 'report.txt' in files
        assert 'SUMMARY.md' in files

    def test_save_results_urls_json_structure(self, basic_crawler):
        """Test structure of urls.json output"""
        basic_crawler.sitemap['https://example.com'] = {'title': 'Test'}
        basic_crawler.url_categories['pages'].add('https://example.com')
        basic_crawler.visited_urls.add('https://example.com')

        basic_crawler.save_results()

        urls_path = os.path.join(basic_crawler.config['output_dir'], 'urls.json')
        with open(urls_path, 'r') as f:
            urls_data = json.load(f)

        assert 'root_url' in urls_data
        assert 'base_domain' in urls_data
        assert 'summary' in urls_data
        assert 'urls' in urls_data
        assert urls_data['summary']['total_urls'] == 1


class TestWebCrawlerEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_url_normalization(self, basic_crawler):
        """Test normalization of root URL"""
        normalized = basic_crawler.normalize_url("https://example.com/")
        assert normalized == "https://example.com/"

    def test_special_characters_in_url(self, basic_crawler):
        """Test handling of special characters in URLs"""
        url = "https://example.com/page?query=test&foo=bar#section"
        normalized = basic_crawler.normalize_url(url)
        assert normalized == "https://example.com/page"
        assert '?' not in normalized
        assert '#' not in normalized

    def test_relative_url_resolution(self, basic_crawler):
        """Test resolution of relative URLs"""
        html = '<a href="../other">Link</a><a href="./sibling">Link2</a>'
        soup = BeautifulSoup(html, 'html.parser')
        links = basic_crawler.extract_links(soup, "https://example.com/subdir/page")

        assert "https://example.com/other" in links
        assert "https://example.com/subdir/sibling" in links

    def test_duplicate_url_handling(self, basic_crawler):
        """Test that duplicate URLs are not crawled twice"""
        basic_crawler.visited_urls.add("https://example.com/page")
        basic_crawler.to_visit = [("https://example.com/page", 0)]

        with patch.object(basic_crawler, 'crawl_page') as mock_crawl:
            basic_crawler.crawl()
            # Should not call crawl_page since URL already visited
            mock_crawl.assert_not_called()

    def test_handle_malformed_html(self, basic_crawler):
        """Test handling of malformed HTML"""
        malformed_html = "<html><body><h1>Test<p>No closing tags"
        soup = BeautifulSoup(malformed_html, 'html.parser')
        content = basic_crawler.extract_content(soup, "https://example.com")

        # Should still extract some content despite malformed HTML
        assert 'h1' in content
        assert len(content['h1']) > 0

    def test_unicode_content_handling(self, basic_crawler):
        """Test handling of Unicode content"""
        unicode_html = """
        <html>
            <head><title>Test 中文 العربية</title></head>
            <body><p>Content with émojis 🎉 and symbols</p></body>
        </html>
        """
        soup = BeautifulSoup(unicode_html, 'html.parser')
        content = basic_crawler.extract_content(soup, "https://example.com")

        assert '中文' in content['title']
        assert 'émojis' in content['text_content']


@pytest.mark.integration
class TestWebCrawlerIntegration:
    """Integration tests with mocked requests (marked as integration)"""

    @patch('time.sleep')
    @patch('web_crawler.requests.Session.get')
    def test_full_crawl_workflow(self, mock_get, mock_sleep, temp_output_dir):
        """Test complete crawl workflow"""
        config = {
            'max_pages': 3,
            'max_depth': 2,
            'delay': 0,
            'output_dir': temp_output_dir,
            'save_content': True
        }

        crawler = WebCrawler("https://example.com", config)

        # Mock responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = '''
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1>Test</h1>
                    <a href="/page2">Page 2</a>
                    <a href="/page3">Page 3</a>
                </body>
            </html>
        '''
        mock_get.return_value = mock_response

        crawler.crawl()

        # Verify crawl completed
        assert len(crawler.visited_urls) > 0
        assert os.path.exists(os.path.join(temp_output_dir, 'sitemap.json'))
        assert os.path.exists(os.path.join(temp_output_dir, 'SUMMARY.md'))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
