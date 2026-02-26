#!/usr/bin/env python3
"""
Performance and Load Tests for Web Crawler
Tests performance, memory usage, and scalability
"""

import pytest
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import psutil
import os

# Add parent directory to path
PARENT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PARENT_DIR))

from web_crawler import WebCrawler, sanitize_html


@pytest.mark.slow
class TestPerformance:
    """Performance tests for web crawler operations"""

    def test_sanitize_html_performance(self, sample_html_with_secrets):
        """Test sanitization performance on large HTML"""
        # Replicate HTML to make it larger
        large_html = sample_html_with_secrets * 100

        start = time.time()
        result = sanitize_html(large_html)
        duration = time.time() - start

        assert duration < 1.0, f"Sanitization took {duration:.2f}s, should be < 1.0s"
        assert 'REDACTED' in result

    def test_url_normalization_performance(self, basic_crawler):
        """Test URL normalization performance with many URLs"""
        urls = [
            f"https://example.com/page{i}?param=value#section"
            for i in range(1000)
        ]

        start = time.time()
        for url in urls:
            basic_crawler.normalize_url(url)
        duration = time.time() - start

        assert duration < 0.5, f"Normalizing 1000 URLs took {duration:.2f}s"

    def test_content_extraction_performance(self, basic_crawler, sample_soup_clean):
        """Test content extraction performance"""
        start = time.time()
        for _ in range(100):
            content = basic_crawler.extract_content(sample_soup_clean, "https://example.com")
        duration = time.time() - start

        assert duration < 2.0, f"100 extractions took {duration:.2f}s"

    @patch('time.sleep')
    @patch('web_crawler.requests.Session.get')
    def test_crawl_speed_with_many_pages(self, mock_get, mock_sleep, temp_output_dir):
        """Test crawling speed with multiple pages"""
        config = {
            'max_pages': 50,
            'delay': 0,
            'output_dir': temp_output_dir,
            'save_content': False  # Disable to test crawl logic only
        }

        crawler = WebCrawler("https://example.com", config)

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = '<html><body><h1>Test</h1></body></html>'
        mock_get.return_value = mock_response

        start = time.time()
        crawler.crawl()
        duration = time.time() - start

        # Should process quickly with mocked requests
        assert duration < 5.0, f"Crawling 50 pages took {duration:.2f}s"


@pytest.mark.slow
class TestMemoryUsage:
    """Memory usage and leak tests"""

    def get_memory_usage_mb(self):
        """Get current process memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    @patch('web_crawler.requests.Session.get')
    def test_memory_does_not_grow_unbounded(self, mock_get, temp_output_dir):
        """Test that memory doesn't grow unbounded during crawling"""
        config = {
            'max_pages': 100,
            'delay': 0,
            'output_dir': temp_output_dir,
            'save_content': True
        }

        # Mock response with moderate size
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = '<html><body>' + 'x' * 10000 + '</body></html>'
        mock_get.return_value = mock_response

        initial_memory = self.get_memory_usage_mb()

        crawler = WebCrawler("https://example.com", config)
        # Manually crawl pages to measure memory
        for i in range(100):
            crawler.crawl_page(f"https://example.com/page{i}", 0)

        final_memory = self.get_memory_usage_mb()
        memory_growth = final_memory - initial_memory

        # Memory growth should be reasonable (< 100MB for 100 pages)
        assert memory_growth < 100, f"Memory grew by {memory_growth:.2f}MB"

    def test_large_sitemap_handling(self, temp_output_dir):
        """Test handling of large sitemaps"""
        config = {'output_dir': temp_output_dir}
        crawler = WebCrawler("https://example.com", config)

        # Add many entries to sitemap
        for i in range(1000):
            crawler.sitemap[f"https://example.com/page{i}"] = {
                'title': f'Page {i}',
                'text_content': 'Content here ' * 100,
                'h1': ['Heading'],
                'links': [{'text': 'Link', 'href': '/other'}] * 10
            }

        initial_memory = self.get_memory_usage_mb()

        # Save results
        crawler.save_results()

        final_memory = self.get_memory_usage_mb()
        memory_growth = final_memory - initial_memory

        # Should handle large sitemap without excessive memory
        assert memory_growth < 50, f"Memory grew by {memory_growth:.2f}MB"


@pytest.mark.slow
class TestScalability:
    """Scalability tests for large crawls"""

    @patch('web_crawler.requests.Session.get')
    def test_handles_many_duplicate_urls(self, mock_get, temp_output_dir):
        """Test handling of many duplicate URLs efficiently"""
        config = {
            'max_pages': 100,
            'delay': 0,
            'output_dir': temp_output_dir
        }

        crawler = WebCrawler("https://example.com", config)

        # Add same URL many times to queue
        crawler.to_visit = []  # Clear root URL from __init__
        for i in range(1000):
            crawler.to_visit.append(("https://example.com/page", 0))

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = '<html><body>Test</body></html>'
        mock_get.return_value = mock_response

        start = time.time()
        crawler.crawl()
        duration = time.time() - start

        # Should efficiently skip duplicates
        assert len(crawler.visited_urls) == 1
        assert duration < 2.0, "Duplicate handling should be efficient"

    @patch('web_crawler.requests.Session.get')
    def test_deep_crawl_performance(self, mock_get, temp_output_dir):
        """Test performance with deep crawl depth"""
        config = {
            'max_pages': 50,
            'max_depth': 10,
            'delay': 0,
            'output_dir': temp_output_dir
        }

        crawler = WebCrawler("https://example.com", config)

        # Mock response with links to create depth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = '''
            <html><body>
                <a href="/level1">Link</a>
                <a href="/level2">Link</a>
            </body></html>
        '''
        mock_get.return_value = mock_response

        start = time.time()
        crawler.crawl()
        duration = time.time() - start

        assert duration < 5.0, f"Deep crawl took {duration:.2f}s"


@pytest.mark.slow
class TestStressTests:
    """Stress tests for edge cases"""

    def test_sanitize_extremely_long_secrets(self):
        """Test sanitization with very long secret strings"""
        # Create HTML with extremely long secret
        long_secret = "sk_test_" + "x" * 10000
        html = f'api_key: "{long_secret}"'

        start = time.time()
        result = sanitize_html(html)
        duration = time.time() - start

        assert 'REDACTED-API-KEY' in result
        assert duration < 0.5, "Should handle long strings efficiently"

    def test_many_concurrent_patterns(self, test_secrets_data):
        """Test sanitization with many different secret patterns"""
        html = ""
        for secret_type, secrets in test_secrets_data['secrets'].items():
            for secret in secrets:
                html += f'{secret_type}="{secret}"\n'

        # Replicate to make larger
        html = html * 10

        start = time.time()
        result = sanitize_html(html)
        duration = time.time() - start

        assert 'REDACTED' in result
        assert duration < 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'slow'])
