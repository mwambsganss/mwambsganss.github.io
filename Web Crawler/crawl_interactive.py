#!/usr/bin/env python3
"""
Interactive Web Crawler Configuration Script
"""

import json
import os


def get_input(prompt, default=None, type_cast=str):
    """Get user input with default value"""
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    value = input(prompt).strip()

    if not value and default is not None:
        return default

    try:
        return type_cast(value) if value else default
    except ValueError:
        print(f"Invalid input. Using default: {default}")
        return default


def yes_no(prompt, default=True):
    """Get yes/no input"""
    default_str = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{default_str}]: ").strip().lower()

    if not value:
        return default

    return value in ['y', 'yes', 'true', '1']


def main():
    print("=" * 80)
    print("Web Crawler Configuration Wizard")
    print("=" * 80)
    print()

    # Get URL
    url = get_input("Enter the root URL to crawl")

    # Get configuration
    print("\nCrawl Settings:")
    max_pages = get_input("Maximum pages to crawl", 1000, int)
    max_depth = get_input("Maximum depth (levels from root)", 10, int)
    delay = get_input("Delay between requests (seconds)", 1.0, float)

    print("\nScope Settings:")
    include_subdomains = yes_no("Include subdomains?", True)
    include_external = yes_no("Include external links?", False)

    print("\nOutput Settings:")
    output_dir = get_input("Output directory", "crawl_output")
    save_content = yes_no("Save page content (HTML/JSON/TXT)?", True)

    # Build config
    config = {
        'max_pages': max_pages,
        'max_depth': max_depth,
        'delay': delay,
        'include_subdomains': include_subdomains,
        'include_external': include_external,
        'output_dir': output_dir,
        'save_content': save_content
    }

    # Summary
    print("\n" + "=" * 80)
    print("Configuration Summary:")
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Max Pages: {max_pages}")
    print(f"Max Depth: {max_depth}")
    print(f"Delay: {delay}s")
    print(f"Include Subdomains: {include_subdomains}")
    print(f"Include External: {include_external}")
    print(f"Output Dir: {output_dir}")
    print(f"Save Content: {save_content}")
    print("=" * 80)

    proceed = yes_no("\nStart crawling?", True)

    if proceed:
        print("\nStarting crawler...\n")

        # Import and run crawler
        from web_crawler import WebCrawler

        crawler = WebCrawler(url, config)

        try:
            crawler.crawl()
        except KeyboardInterrupt:
            print("\n\n⚠️  Crawl interrupted by user")
            crawler.save_results()
            print("Partial results saved.")
    else:
        print("\nCrawl cancelled.")

        # Save config
        save_config = yes_no("Save configuration to file?", False)
        if save_config:
            config_file = get_input("Config filename", "config.json")
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration saved to: {config_file}")


if __name__ == '__main__':
    main()
