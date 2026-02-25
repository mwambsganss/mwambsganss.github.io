#!/bin/bash
# Quick Start Script for Web Crawler

echo "════════════════════════════════════════════════════════════════"
echo "  Universal Web Crawler - Quick Start"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if dependencies are installed
if ! python3 -c "import requests, bs4" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

echo "✅ All dependencies installed"
echo ""

# Ask for mode
echo "Choose your mode:"
echo "  1) Interactive mode (recommended)"
echo "  2) Command line mode"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "Starting interactive crawler..."
        echo ""
        python3 crawl_interactive.py
        ;;
    2)
        echo ""
        read -p "Enter URL to crawl: " url
        read -p "Max pages [1000]: " max_pages
        max_pages=${max_pages:-1000}

        read -p "Max depth [10]: " max_depth
        max_depth=${max_depth:-10}

        echo ""
        echo "Starting crawler..."
        echo ""
        python3 web_crawler.py "$url" --max-pages "$max_pages" --max-depth "$max_depth"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Crawl Complete!"
echo "════════════════════════════════════════════════════════════════"
