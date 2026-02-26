#!/usr/bin/env python3
"""
Pytest Configuration and Fixtures
Provides shared test fixtures and configuration for all tests
"""

import pytest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

# Add parent directory to path to import web_crawler
PARENT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PARENT_DIR))

from web_crawler import WebCrawler, sanitize_html


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def test_secrets_data(fixtures_dir):
    """Load test secrets data from JSON file"""
    with open(fixtures_dir / "test_secrets.json", 'r') as f:
        return json.load(f)


@pytest.fixture
def sample_html_with_secrets(fixtures_dir):
    """Load sample HTML with secrets"""
    with open(fixtures_dir / "sample_html_with_secrets.html", 'r') as f:
        return f.read()


@pytest.fixture
def sample_html_clean(fixtures_dir):
    """Load clean sample HTML"""
    with open(fixtures_dir / "sample_html_clean.html", 'r') as f:
        return f.read()


@pytest.fixture
def sample_html_with_links(fixtures_dir):
    """Load sample HTML with various link types"""
    with open(fixtures_dir / "sample_html_with_links.html", 'r') as f:
        return f.read()


@pytest.fixture
def sample_soup_clean(sample_html_clean):
    """Return BeautifulSoup object of clean HTML"""
    return BeautifulSoup(sample_html_clean, 'html.parser')


@pytest.fixture
def sample_soup_with_links(sample_html_with_links):
    """Return BeautifulSoup object of HTML with links"""
    return BeautifulSoup(sample_html_with_links, 'html.parser')


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for tests"""
    temp_dir = tempfile.mkdtemp(prefix="crawler_test_")
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def basic_crawler(temp_output_dir):
    """Create a basic WebCrawler instance for testing"""
    config = {
        'output_dir': temp_output_dir,
        'max_pages': 10,
        'delay': 0,
        'save_content': True
    }
    return WebCrawler("https://example.com", config)


@pytest.fixture
def crawler_with_subdomains(temp_output_dir):
    """Create crawler that includes subdomains"""
    config = {
        'output_dir': temp_output_dir,
        'max_pages': 10,
        'include_subdomains': True,
        'delay': 0
    }
    return WebCrawler("https://example.com", config)


@pytest.fixture
def crawler_with_external(temp_output_dir):
    """Create crawler that includes external links"""
    config = {
        'output_dir': temp_output_dir,
        'max_pages': 10,
        'include_external': True,
        'delay': 0
    }
    return WebCrawler("https://example.com", config)


@pytest.fixture
def mock_response_html():
    """Return mock HTML response"""
    return """
    <html>
        <head>
            <title>Mock Page</title>
            <meta name="description" content="Mock description">
        </head>
        <body>
            <h1>Mock Heading</h1>
            <p>Mock content for testing.</p>
            <a href="/link1">Link 1</a>
            <a href="/link2">Link 2</a>
        </body>
    </html>
    """


@pytest.fixture
def mock_response_with_secrets():
    """Return mock HTML with secrets"""
    return """
    <html>
        <head><title>Page with Secrets</title></head>
        <body>
            <script>
                const clientId = "12345678-1234-1234-1234-123456789abc";
                const clientSecret = ".nt8Q~abcdefghijklmnopqrstuvwxyz1234567890";
                const apiKey = "sk_test_abcdefghijklmnopqrstuvwxyz123456";
            </script>
        </body>
    </html>
    """


@pytest.fixture
def expected_sanitized_patterns():
    """Return patterns that should appear after sanitization"""
    return [
        'REDACTED-SECRET',
        'REDACTED-UUID',
        'REDACTED-TOKEN',
        'REDACTED-API-KEY'
    ]


@pytest.fixture
def secret_patterns_to_remove():
    """Return patterns that should NOT appear after sanitization"""
    return [
        '.nt8Q~',
        'Q~',
        '12345678-1234-1234-1234',
        'Bearer eyJ',
        'sk_test_',
        'api_key_'
    ]


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add 'unit' marker to all tests by default
        if "integration" not in item.keywords and "slow" not in item.keywords:
            item.add_marker(pytest.mark.unit)
