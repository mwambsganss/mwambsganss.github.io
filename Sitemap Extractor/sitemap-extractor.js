// Universal Sitemap Extractor
// Run this script in your browser console on any website

(function() {
    console.log('🔍 Starting sitemap extraction...');

    // Configuration - automatically detects current domain
    const currentDomain = window.location.hostname;
    const config = {
        baseDomain: currentDomain,
        includeExternalLinks: true, // Set to false to exclude external links
        includeSubdomains: true,     // Set to false to only include exact domain match
        maxDepth: 3
    };

    console.log(`📍 Extracting sitemap for: ${currentDomain}`);

    // Storage for all discovered URLs
    const discoveredUrls = new Set();
    const urlsByType = {
        pages: new Set(),
        subsites: new Set(),
        resources: new Set(),
        external: new Set()
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

    // Extract all links from current page
    function extractLinksFromCurrentPage() {
        const links = document.querySelectorAll('a[href]');
        const currentPageLinks = [];

        links.forEach(link => {
            try {
                const href = link.href;
                const text = link.textContent.trim();
                const url = new URL(href, window.location.href);

                // Categorize the link
                if (isSameSite(url)) {
                    discoveredUrls.add(url.href);

                    // Categorize by path
                    const path = url.pathname;
                    if (path.match(/\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|csv|txt|json|xml)$/i)) {
                        urlsByType.resources.add(url.href);
                    } else if (url.hostname !== config.baseDomain) {
                        // Different subdomain
                        urlsByType.subsites.add(url.href);
                    } else {
                        urlsByType.pages.add(url.href);
                    }

                    currentPageLinks.push({
                        url: url.href,
                        text: text,
                        path: url.pathname,
                        hostname: url.hostname
                    });
                } else if (config.includeExternalLinks) {
                    urlsByType.external.add(url.href);
                }
            } catch (e) {
                // Invalid URL, skip
                console.warn('Skipped invalid URL:', link.href);
            }
        });

        return currentPageLinks;
    }

    // Extract navigation structure
    function extractNavigation() {
        const navElements = document.querySelectorAll('nav, [role="navigation"], .navigation, .menu, .navbar');
        const navigation = [];

        navElements.forEach((nav) => {
            const navLinks = nav.querySelectorAll('a[href]');
            const navGroup = {
                type: nav.tagName,
                class: nav.className,
                links: []
            };

            navLinks.forEach(link => {
                navGroup.links.push({
                    text: link.textContent.trim(),
                    url: link.href
                });
            });

            if (navGroup.links.length > 0) {
                navigation.push(navGroup);
            }
        });

        return navigation;
    }

    // Extract page metadata
    function extractPageMetadata() {
        return {
            url: window.location.href,
            domain: window.location.hostname,
            title: document.title,
            description: document.querySelector('meta[name="description"]')?.content || '',
            keywords: document.querySelector('meta[name="keywords"]')?.content || '',
            h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent.trim()),
            h2: Array.from(document.querySelectorAll('h2')).map(h => h.textContent.trim())
        };
    }

    // Run extraction
    const results = {
        config: {
            domain: config.baseDomain,
            includeSubdomains: config.includeSubdomains,
            includeExternalLinks: config.includeExternalLinks
        },
        currentPage: extractPageMetadata(),
        navigation: extractNavigation(),
        links: extractLinksFromCurrentPage(),
        summary: {
            totalLinks: discoveredUrls.size,
            pages: urlsByType.pages.size,
            subsites: urlsByType.subsites.size,
            resources: urlsByType.resources.size,
            external: urlsByType.external.size
        },
        categorizedUrls: {
            pages: Array.from(urlsByType.pages).sort(),
            subsites: Array.from(urlsByType.subsites).sort(),
            resources: Array.from(urlsByType.resources).sort(),
            external: Array.from(urlsByType.external).sort()
        }
    };

    // Display results
    console.log('✅ Extraction complete!');
    console.log('Summary:', results.summary);
    console.log('Full results:', results);

    // Create downloadable file
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sitemap-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('📥 Sitemap downloaded as JSON file');

    // Also create a simple text version
    let textOutput = `SITEMAP FOR ${window.location.href}\n`;
    textOutput += `Domain: ${config.baseDomain}\n`;
    textOutput += `Generated: ${new Date().toISOString()}\n\n`;
    textOutput += `=== SUMMARY ===\n`;
    textOutput += `Total Links: ${results.summary.totalLinks}\n`;
    textOutput += `Pages: ${results.summary.pages}\n`;
    textOutput += `Subsites: ${results.summary.subsites}\n`;
    textOutput += `Resources: ${results.summary.resources}\n`;
    textOutput += `External: ${results.summary.external}\n\n`;

    textOutput += `=== PAGES ===\n`;
    results.categorizedUrls.pages.forEach(url => textOutput += `${url}\n`);

    textOutput += `\n=== SUBSITES ===\n`;
    results.categorizedUrls.subsites.forEach(url => textOutput += `${url}\n`);

    textOutput += `\n=== RESOURCES ===\n`;
    results.categorizedUrls.resources.forEach(url => textOutput += `${url}\n`);

    if (config.includeExternalLinks && results.summary.external > 0) {
        textOutput += `\n=== EXTERNAL LINKS ===\n`;
        results.categorizedUrls.external.forEach(url => textOutput += `${url}\n`);
    }

    console.log('\n' + textOutput);

    // Download text version
    const textBlob = new Blob([textOutput], { type: 'text/plain' });
    const textUrl = URL.createObjectURL(textBlob);
    const textLink = document.createElement('a');
    textLink.href = textUrl;
    textLink.download = `sitemap-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(textLink);
    textLink.click();
    document.body.removeChild(textLink);
    URL.revokeObjectURL(textUrl);

    console.log('📥 Sitemap downloaded as TXT file');

    return results;
})();
