#!/bin/bash
# Test Runner Script for Web Crawler Test Suite

set -e  # Exit on error

echo "=================================="
echo "Web Crawler Test Suite Runner"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Please install test requirements:"
    echo "  pip install -r test_requirements.txt"
    exit 1
fi

# Parse command line arguments
TEST_TYPE=${1:-all}

echo "Test Type: $TEST_TYPE"
echo ""

case $TEST_TYPE in
    "all")
        echo "Running all tests..."
        pytest -v --cov=../web_crawler.py --cov-report=html --cov-report=term
        ;;

    "unit")
        echo "Running unit tests only..."
        pytest -v -m unit
        ;;

    "integration")
        echo "Running integration tests..."
        pytest -v -m integration
        ;;

    "performance")
        echo "Running performance tests..."
        pytest -v -m slow test_performance.py
        ;;

    "security")
        echo "Running security tests..."
        pytest -v -m security -k "sanitize"
        ;;

    "fast")
        echo "Running fast tests only (excluding slow tests)..."
        pytest -v -m "not slow"
        ;;

    "coverage")
        echo "Running tests with detailed coverage..."
        pytest -v --cov=../web_crawler.py --cov-report=html --cov-report=term-missing --cov-report=json
        echo ""
        echo -e "${GREEN}Coverage report generated in coverage_report/index.html${NC}"
        ;;

    "quick")
        echo "Running quick smoke tests..."
        pytest -v -m unit --maxfail=1 -x
        ;;

    *)
        echo -e "${YELLOW}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [test_type]"
        echo ""
        echo "Available test types:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests"
        echo "  performance  - Run performance tests"
        echo "  security     - Run security tests"
        echo "  fast         - Run fast tests (exclude slow)"
        echo "  coverage     - Run with detailed coverage report"
        echo "  quick        - Quick smoke test (fail fast)"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Tests completed!${NC}"
