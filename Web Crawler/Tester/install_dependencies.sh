#!/bin/bash
# Installation Script for Test Suite Dependencies
# Use this script if you get "pip: command not found" error

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Web Crawler Test Suite - Dependency Installer         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for Python 3
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python is not installed!${NC}"
    echo ""
    echo "Please install Python 3 from:"
    echo "  https://www.python.org/downloads/"
    echo ""
    echo "Or use Homebrew (if installed):"
    echo "  brew install python3"
    exit 1
fi

# Check for pip
echo ""
echo -e "${YELLOW}Checking pip installation...${NC}"
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
    echo -e "${GREEN}✅ Found: pip3${NC}"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
    echo -e "${GREEN}✅ Found: pip${NC}"
else
    echo -e "${YELLOW}⚠️  pip not found, using python -m pip${NC}"
    PIP_CMD="$PYTHON_CMD -m pip"
fi

# Show pip version
PIP_VERSION=$($PIP_CMD --version 2>&1 | head -1)
echo -e "${GREEN}   $PIP_VERSION${NC}"

# Upgrade pip (optional but recommended)
echo ""
echo -e "${YELLOW}Upgrading pip (recommended)...${NC}"
$PIP_CMD install --upgrade pip --quiet
echo -e "${GREEN}✅ pip upgraded${NC}"

# Install test requirements
echo ""
echo -e "${YELLOW}Installing test dependencies...${NC}"
echo -e "${BLUE}This may take a minute...${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REQUIREMENTS_FILE="$SCRIPT_DIR/test_requirements.txt"

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${RED}❌ Error: test_requirements.txt not found at:${NC}"
    echo "   $REQUIREMENTS_FILE"
    exit 1
fi

# Install dependencies
if $PIP_CMD install -r "$REQUIREMENTS_FILE"; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ All dependencies installed successfully!              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Installed packages:${NC}"
    echo "  ✓ pytest (testing framework)"
    echo "  ✓ pytest-cov (coverage reporting)"
    echo "  ✓ pytest-mock (mocking utilities)"
    echo "  ✓ responses (HTTP mocking)"
    echo "  ✓ psutil (memory profiling)"
    echo "  ✓ beautifulsoup4 (HTML parsing)"
    echo "  ✓ requests (HTTP library)"
    echo "  ✓ and more..."
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Run quick validation:  ${GREEN}python3 quick_start.py${NC}"
    echo "  2. Run all tests:         ${GREEN}pytest -v${NC}"
    echo "  3. Run with coverage:     ${GREEN}./run_tests.sh coverage${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ Installation failed!                                  ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  1. Try running with sudo (if needed):"
    echo "     ${BLUE}sudo $PIP_CMD install -r test_requirements.txt${NC}"
    echo ""
    echo "  2. Use a virtual environment (recommended):"
    echo "     ${BLUE}python3 -m venv venv${NC}"
    echo "     ${BLUE}source venv/bin/activate${NC}"
    echo "     ${BLUE}pip install -r test_requirements.txt${NC}"
    echo ""
    echo "  3. Install user-local (no admin needed):"
    echo "     ${BLUE}$PIP_CMD install --user -r test_requirements.txt${NC}"
    echo ""
    exit 1
fi

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
if $PYTHON_CMD -c "import pytest; import pytest_cov; import bs4; import requests" 2>/dev/null; then
    echo -e "${GREEN}✅ All key packages verified!${NC}"
else
    echo -e "${RED}⚠️  Some packages may not have installed correctly${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete! You're ready to run tests.${NC}"
echo ""
