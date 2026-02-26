# Web Crawler Test Suite

Comprehensive test suite for the Web Crawler tool with data staging, fixtures, and performance testing.

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Data & Fixtures](#test-data--fixtures)
- [Test Categories](#test-categories)
- [Coverage Reports](#coverage-reports)
- [Writing New Tests](#writing-new-tests)

## 🎯 Overview

This test suite provides comprehensive testing for the Web Crawler, including:

- **Unit Tests**: Fast, isolated tests for individual functions
- **Integration Tests**: Tests for complete workflows
- **Performance Tests**: Speed and scalability tests
- **Security Tests**: Secret sanitization and data protection
- **Staged Test Data**: Realistic test fixtures with dummy secrets

## 📦 Installation

### 1. Install Test Dependencies

```bash
cd "Web Crawler/Tester"
pip install -r test_requirements.txt
```

### 2. Install Main Dependencies

```bash
cd ..
pip install -r requirements.txt
```

## 🗂️ Test Structure

```
Tester/
├── README.md                              # This file
├── pytest.ini                             # Pytest configuration
├── conftest.py                            # Shared fixtures and setup
├── test_requirements.txt                  # Test dependencies
├── test_web_crawler_comprehensive.py      # Main test suite
├── test_performance.py                    # Performance & stress tests
└── fixtures/                              # Test data directory
    ├── test_secrets.json                  # Dummy secrets for testing
    ├── sample_html_with_secrets.html      # HTML with fake secrets
    ├── sample_html_clean.html             # Clean HTML sample
    └── sample_html_with_links.html        # HTML with various link types
```

## 🚀 Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"

# Security tests only
pytest -m security
```

### Run Specific Test Files

```bash
# Main test suite
pytest test_web_crawler_comprehensive.py

# Performance tests
pytest test_performance.py

# Specific test class
pytest test_web_crawler_comprehensive.py::TestSanitizeHTML

# Specific test function
pytest test_web_crawler_comprehensive.py::TestSanitizeHTML::test_sanitize_azure_client_secret
```

### Run with Verbosity

```bash
# Verbose output
pytest -v

# Extra verbose (show all tests)
pytest -vv

# Show print statements
pytest -s
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=../web_crawler.py --cov-report=html

# View coverage in browser
open coverage_report/index.html
```

### Parallel Execution

```bash
# Run tests in parallel (faster)
pytest -n auto
```

## 🎭 Test Data & Fixtures

### Test Secrets (fixtures/test_secrets.json)

Contains **FAKE** secrets for testing sanitization:
- Azure AD client secrets
- Azure client IDs (UUIDs)
- Bearer tokens
- API keys
- Access tokens

**⚠️ Important**: All secrets in test data are fake and for testing only.

### HTML Fixtures

1. **sample_html_with_secrets.html**
   - Contains fake secrets embedded in HTML
   - Tests sanitization functions
   - Includes various secret formats

2. **sample_html_clean.html**
   - Clean HTML without secrets
   - Tests content extraction
   - Contains headings, links, images

3. **sample_html_with_links.html**
   - Various link types (internal, external, relative)
   - Tests link extraction and categorization
   - Includes excluded URLs (logout, delete)

### Using Fixtures in Tests

```python
def test_example(sample_html_clean, test_secrets_data):
    # Use the fixtures directly
    assert 'Clean Test Page' in sample_html_clean
    assert 'azure_client_secrets' in test_secrets_data['secrets']
```

## 📊 Test Categories

### Unit Tests (Fast)
- ✅ Secret sanitization
- ✅ URL normalization
- ✅ URL categorization
- ✅ Content extraction
- ✅ Link extraction

### Integration Tests
- ✅ Full crawl workflow
- ✅ File saving operations
- ✅ Summary generation

### Performance Tests
- ⏱️ Sanitization speed
- ⏱️ Crawling performance
- ⏱️ Memory usage
- ⏱️ Scalability

### Security Tests
- 🔒 Azure secret removal
- 🔒 API key sanitization
- 🔒 Token redaction
- 🔒 UUID removal

## 📈 Coverage Reports

### Generate Coverage Report

```bash
pytest --cov=../web_crawler.py --cov-report=html
```

### View Coverage

```bash
# Open HTML report
open coverage_report/index.html

# Terminal report
pytest --cov=../web_crawler.py --cov-report=term-missing
```

### Coverage Targets

- **Minimum**: 80% code coverage
- **Target**: 90%+ code coverage
- **Critical paths**: 100% coverage

## ✍️ Writing New Tests

### Test Structure

```python
import pytest

class TestNewFeature:
    """Test description"""

    def test_specific_behavior(self, basic_crawler):
        """Test a specific behavior"""
        # Arrange
        test_data = "test"

        # Act
        result = basic_crawler.some_method(test_data)

        # Assert
        assert result == expected_value
```

### Using Fixtures

```python
def test_with_fixtures(self, basic_crawler, temp_output_dir, sample_html_clean):
    """Test using multiple fixtures"""
    # Fixtures are automatically provided
    crawler = basic_crawler
    output_dir = temp_output_dir
    html = sample_html_clean
```

### Adding Test Data

1. Create new fixture file in `fixtures/`
2. Add fixture function to `conftest.py`:

```python
@pytest.fixture
def my_new_fixture(fixtures_dir):
    with open(fixtures_dir / "my_data.json", 'r') as f:
        return json.load(f)
```

3. Use in tests:

```python
def test_my_feature(my_new_fixture):
    assert 'expected_key' in my_new_fixture
```

## 🎯 Test Best Practices

1. **Isolation**: Each test should be independent
2. **Fast**: Unit tests should run in milliseconds
3. **Clear**: Test names should describe what is being tested
4. **Arranged**: Use Arrange-Act-Assert pattern
5. **Mocked**: Mock external dependencies (HTTP, file I/O)
6. **Fixtures**: Use fixtures for reusable test data

## 🐛 Debugging Tests

### Run Single Test with Debugging

```bash
# Drop into debugger on failure
pytest --pdb

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

### Print Debug Information

```bash
# Show print statements
pytest -s

# Show more detailed output
pytest -vv
```

## 📝 Continuous Integration

### GitHub Actions Example

```yaml
- name: Run Tests
  run: |
    cd "Web Crawler/Tester"
    pytest --cov --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

## 🤝 Contributing

When adding new features to the crawler:

1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain >85% coverage
4. Add test data to fixtures if needed
5. Update this README if adding new test categories

## 📞 Support

For questions or issues with tests:
- Check test output and error messages
- Review fixture data in `fixtures/` directory
- Run with `-vv` for detailed output
- Use `--pdb` to debug failing tests

## 🔐 Security Note

All test data contains **FAKE** credentials for testing purposes only. Never commit real secrets or credentials to the repository.

---

**Happy Testing! 🧪**
