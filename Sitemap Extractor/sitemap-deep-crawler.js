// Universal Deep Crawler
// This script will discover all internal links from the current page
// Run this in your browser console on any website

(async function() {
    console.log('🕷️ Starting deep crawl...');

    // Configuration - automatically detects current domain
    const currentDomain = window.location.hostname;
    const config = {
        baseDomain: currentDomain,
        includeSubdomains: true, // Set to false to only include exact domain match
        maxPages: 50, // Limit to avoid overwhelming the system
        delayBetweenPages: 1000, // 1 second delay
        excludePatterns: [
            /logout/i,
            /signout/i,
            /sign-out/i,
            /delete/i,
            /remove/i,
            /download/i
        ]
    };

    console.log(`📍 Crawling: ${currentDomain}`);

    const visited = new Set();
    const toVisit = [window.location.href];
    const sitemap = {
        pages: [],
        structure: {},
        allUrls: new Set()
    };

    // Check if URL belongs to the same site
    function isSameSite(url) {
        if (config.includeSubdomains) {
            // Match base domain and all subdomains
            const baseDomainParts = config.baseDomain.split('.');
            const urlDomainParts = url.hostname.split('.');

            // Get the root domain (last 2 parts, e.g., "example.com")
            const baseRoot = baseDomainParts.slice(-2).join('.');
            const urlRoot = urlDomainParts.slice(-2).join('.');

            return baseRoot === urlRoot;
        } else {
            // Exact domain match only
            return url.hostname === config.baseDomain;
        }
    }

    // Extract all internal links from a page
    function extractInternalLinks(baseUrl) {
        const links = document.querySelectorAll('a[href]');
        const internalLinks = [];

        links.forEach(link => {
            try {
                const url = new URL(link.href, baseUrl);

                // Check if it's an internal link
                if (isSameSite(url)) {
                    const fullUrl = url.origin + url.pathname;

                    // Check exclusion patterns
                    const shouldExclude = config.excludePatterns.some(pattern =>
                        pattern.test(fullUrl)
                    );

                    if (!shouldExclude && !visited.has(fullUrl)) {
                        internalLinks.push({
                            url: fullUrl,
                            text: link.textContent.trim(),
                            fromPage: baseUrl
                        });
                    }
                }
            } catch (e) {
                // Invalid URL, skip
            }
        });

        return internalLinks;
    }

    // Get page info
    function getPageInfo() {
        return {
            url: window.location.href,
            domain: window.location.hostname,
            title: document.title,
            h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent.trim()),
            h2: Array.from(document.querySelectorAll('h2')).map(h => h.textContent.trim()),
            linkCount: document.querySelectorAll('a[href]').length,
            timestamp: new Date().toISOString()
        };
    }

    // Show progress
    function updateProgress() {
        console.clear();
        console.log('🕷️ DEEP CRAWL IN PROGRESS');
        console.log('=========================');
        console.log(`Visited: ${visited.size} pages`);
        console.log(`Queue: ${toVisit.length} pages`);
        console.log(`Total discovered: ${sitemap.allUrls.size} URLs`);
        console.log(`\nCurrent page: ${window.location.href}`);
    }

    // Main crawl loop
    console.log('⚠️ IMPORTANT: This script will navigate through pages automatically.');
    console.log('⚠️ It will take several minutes. Stay on this browser tab.');
    console.log('⚠️ Press ESC or close the console to stop the crawl.\n');

    await new Promise(resolve => setTimeout(resolve, 3000)); // Give user time to read

    // Crawl current page first
    visited.add(window.location.href);
    const pageInfo = getPageInfo();
    sitemap.pages.push(pageInfo);

    const links = extractInternalLinks(window.location.href);
    links.forEach(link => {
        sitemap.allUrls.add(link.url);
        if (!visited.has(link.url)) {
            toVisit.push(link.url);
        }
    });

    updateProgress();

    console.log('\n📊 Crawl complete for initial page!');
    console.log('\n⚠️ MANUAL CRAWL INSTRUCTIONS:');
    console.log('1. Visit each URL below');
    console.log('2. Run the sitemap-extractor.js script on each page');
    console.log('3. Collect all the results\n');

    console.log('URLs to visit:');
    Array.from(sitemap.allUrls).sort().forEach((url, i) => {
        console.log(`${i + 1}. ${url}`);
    });

    // Export results
    const results = {
        config: {
            domain: config.baseDomain,
            includeSubdomains: config.includeSubdomains
        },
        summary: {
            totalUrls: sitemap.allUrls.size,
            pagesVisited: visited.size
        },
        urls: Array.from(sitemap.allUrls).sort(),
        pages: sitemap.pages,
        generatedAt: new Date().toISOString()
    };

    // Download results
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `deep-crawl-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('\n✅ Results downloaded!');

    return results;
})();
