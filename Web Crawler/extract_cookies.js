// COOKIE EXTRACTOR FOR AI.LILLY.COM
// Run this in your browser console (F12 → Console tab)
// After logging in to ai.lilly.com

(function() {
    console.log('╔════════════════════════════════════════════════════════════════╗');
    console.log('║           AI.LILLY.COM Cookie Extractor                        ║');
    console.log('╚════════════════════════════════════════════════════════════════╝');
    console.log('');

    // Get all cookies
    const cookies = document.cookie.split('; ');

    if (cookies.length === 0 || (cookies.length === 1 && cookies[0] === '')) {
        console.log('❌ No cookies found!');
        console.log('Make sure you are:');
        console.log('  1. Logged in to ai.lilly.com');
        console.log('  2. On the actual ai.lilly.com domain (not login.microsoft.com)');
        console.log('  3. Not in incognito/private mode');
        return;
    }

    console.log(`✅ Found ${cookies.length} cookies\n`);
    console.log('Copy the Python code below and paste it into:');
    console.log('  → Web Crawler/crawl_ai_lilly_authenticated.py');
    console.log('  → Section: "ADD YOUR COOKIES HERE"\n');
    console.log('════════════════════════════════════════════════════════════════\n');
    console.log('# Generated cookie configuration:');
    console.log('# Copy everything below this line:\n');

    // Generate Python code
    cookies.forEach(cookie => {
        const parts = cookie.split('=');
        const name = parts[0].trim();
        const value = parts.slice(1).join('='); // In case value contains '='

        if (name && value) {
            console.log(`crawler.session.cookies.set('${name}', '${value}', domain='ai.lilly.com')`);
        }
    });

    console.log('\n════════════════════════════════════════════════════════════════');
    console.log('✅ Done! Copy the lines above and paste into your Python script.');
    console.log('');
    console.log('📋 Cookie Names Found:');
    cookies.forEach(cookie => {
        const name = cookie.split('=')[0].trim();
        if (name) console.log(`  • ${name}`);
    });
    console.log('');
    console.log('⚠️  IMPORTANT NOTES:');
    console.log('  • Cookies expire - you may need to re-extract them later');
    console.log('  • Never share these cookie values with anyone');
    console.log('  • Delete the cookie values after testing');

})();
