#!/usr/bin/env python3
"""
Microsoft Teams Channel Chat Scraper
Scrapes chat messages from a Teams channel meeting thread.
Target: "Design Thinking-Agentic AI workshop" - March 12, 2026
"""

try:
    from playwright.sync_api import sync_playwright
    import time
    import sys
    import re
    import json
    import os
    from datetime import datetime
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Output configuration
OUTPUT_DIR = "teams_chat_DTW_AgenticAI"
TARGET_DATE_STR = "March 12"  # Used to filter messages by date label in Teams UI
MEETING_TITLE_HINT = "Design Thinking"  # Partial match to locate the channel/post
TEAMS_URL = "https://teams.microsoft.com"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("""
╔════════════════════════════════════════════════════════════════╗
║   Microsoft Teams Chat Scraper - Design Thinking/Agentic AI  ║
╚════════════════════════════════════════════════════════════════╝

This script will:
  1. Open Microsoft Teams in a browser window (visible)
  2. Wait for you to log in with your Eli Lilly credentials
  3. Let you navigate to the correct channel/team
  4. Automatically scrape all chat messages once you're in position
  5. Save the full chat history to a file

════════════════════════════════════════════════════════════════
""")

if not PLAYWRIGHT_AVAILABLE:
    print("Playwright is not installed!")
    print("\nInstall it with:")
    print("  pip3 install playwright")
    print("  playwright install chromium")
    sys.exit(1)

print("INSTRUCTIONS:")
print("=" * 70)
print("1. Browser will open to teams.microsoft.com")
print("2. Log in with your Eli Lilly SSO credentials")
print("3. Navigate to the Teams channel that hosted the")
print("   'Design Thinking-Agentic AI workshop' on March 12")
print("4. Open the meeting post / chat thread in that channel")
print("5. Scroll to the TOP of the chat to load earlier messages")
print("6. Once you're in position, press ENTER in this terminal")
print("   to start scraping")
print("=" * 70)
print("\nStarting browser in 3 seconds...")
time.sleep(3)


def extract_messages_from_page(page):
    """Extract all currently visible chat messages from the Teams page.

    Returns a dict keyed by data-mid (unique message ID) so callers can
    accumulate results across multiple scroll positions without duplicates.
    data-mid is a Unix-ms timestamp, giving free chronological ordering.
    """
    # Teams v2 DOM (confirmed from live HTML dump):
    #   .fui-ChatMessage          — wrapper per message (author header + body)
    #   [data-tid="message-author-name"] — author; only on first msg in a consecutive run
    #   time.fui-ChatMessage__timestamp  — timestamp with datetime attribute
    #   [data-tid="chat-pane-message"]   — actual message body; carries data-mid
    js_extract = """
    () => {
        const results = {};
        let currentSender = '';
        let currentTimestamp = '';

        document.querySelectorAll('.fui-ChatMessage').forEach(block => {
            const authorEl = block.querySelector('[data-tid="message-author-name"]');
            if (authorEl) currentSender = authorEl.innerText.trim();

            const timeEl = block.querySelector(
                'time.fui-ChatMessage__timestamp, time[datetime]'
            );
            if (timeEl) {
                currentTimestamp = timeEl.getAttribute('datetime') ||
                                   timeEl.getAttribute('title') ||
                                   timeEl.innerText.trim();
            }

            const bodyEl = block.querySelector('[data-tid="chat-pane-message"]');
            if (bodyEl) {
                const text = bodyEl.innerText.trim();
                const mid  = bodyEl.getAttribute('data-mid') || '';
                if (text) {
                    // Use mid as key; fall back to text hash for msgs without mid
                    const key = mid || ('noMid_' + text.slice(0, 80));
                    results[key] = {
                        mid: mid,
                        sender: currentSender,
                        timestamp: currentTimestamp,
                        text: text
                    };
                }
            }
        });

        return results;
    }
    """
    return page.evaluate(js_extract)


def scroll_to_load_all(page, pause=2.0, max_scrolls=80):
    """Scroll up in the chat panel, accumulating every message seen.

    Teams virtualises the list — older messages load at the top while newer
    ones are removed from the DOM at the bottom.  We capture each scroll
    snapshot into a single dict (keyed by data-mid) so nothing is lost.
    After reaching the top we sort by mid (chronological) and return the list.
    """
    print("\nScrolling to accumulate all messages (Teams virtual list)...")

    # Confirmed scrollable container selectors from HTML dump
    scrollable_selector = (
        '[data-tid="message-pane-list-viewport"], '
        '[data-tid="message-pane-list-runway"], '
        '[data-tid="chat-pane-list"]'
    )

    # Master accumulator keyed by data-mid
    all_messages = {}

    prev_new = -1
    stable_rounds = 0

    for i in range(max_scrolls):
        # Scroll to top of the chat container
        page.evaluate(f"""
            () => {{
                const el = document.querySelector(`{scrollable_selector}`);
                if (el) el.scrollTop = 0;
                else window.scrollTo(0, 0);
            }}
        """)
        time.sleep(pause)

        snapshot = extract_messages_from_page(page)
        new_this_round = sum(1 for k in snapshot if k not in all_messages)
        all_messages.update(snapshot)

        total = len(all_messages)
        print(f"  Scroll {i+1}: {len(snapshot)} in DOM | "
              f"+{new_this_round} new | {total} accumulated")

        if new_this_round == 0:
            stable_rounds += 1
            if stable_rounds >= 3:
                print("  No new messages for 3 rounds — reached top of chat.")
                break
        else:
            stable_rounds = 0

        prev_new = new_this_round

    # Sort by data-mid (numeric Unix-ms) for chronological order
    def sort_key(item):
        mid = item.get('mid', '')
        try:
            return int(mid)
        except (ValueError, TypeError):
            return 0

    ordered = sorted(all_messages.values(), key=sort_key)
    return ordered


def save_results(messages, page_title, page_url):
    """Save scraped messages to JSON, TXT, and Markdown files."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- JSON ---
    json_path = os.path.join(OUTPUT_DIR, f"chat_{ts}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'scraped_at': datetime.now().isoformat(),
            'page_title': page_title,
            'page_url': page_url,
            'message_count': len(messages),
            'messages': messages
        }, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON: {json_path}")

    # --- Plain Text ---
    txt_path = os.path.join(OUTPUT_DIR, f"chat_{ts}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Teams Chat Export\n")
        f.write(f"{'=' * 70}\n")
        f.write(f"Source : {page_title}\n")
        f.write(f"URL    : {page_url}\n")
        f.write(f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Messages: {len(messages)}\n")
        f.write(f"{'=' * 70}\n\n")
        for m in messages:
            sender = m.get('sender', 'Unknown')
            ts_label = m.get('timestamp', '')
            text = m.get('text', '')
            if sender or ts_label:
                f.write(f"[{ts_label}] {sender}\n")
            f.write(f"{text}\n")
            f.write("-" * 40 + "\n")
    print(f"Saved TXT : {txt_path}")

    # --- Markdown ---
    md_path = os.path.join(OUTPUT_DIR, f"chat_{ts}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Teams Chat: {page_title}\n\n")
        f.write(f"**Scraped:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Messages:** {len(messages)}  \n\n")
        f.write("---\n\n")
        for m in messages:
            sender = m.get('sender', '')
            ts_label = m.get('timestamp', '')
            text = m.get('text', '').replace('\n', '  \n')
            if sender:
                f.write(f"**{sender}**")
                if ts_label:
                    f.write(f" · *{ts_label}*")
                f.write("  \n")
            f.write(f"{text}\n\n")
            f.write("---\n\n")
    print(f"Saved MD  : {md_path}")

    return txt_path, json_path, md_path


# ── Main ────────────────────────────────────────────────────────────────────

with sync_playwright() as p:
    try:
        print("\nLaunching browser...")
        browser = None

        for channel, kwargs in [
            ("msedge",  {"headless": False, "channel": "msedge"}),
            ("chrome",  {"headless": False, "channel": "chrome"}),
            ("chromium",{"headless": False}),
        ]:
            try:
                browser = p.chromium.launch(**kwargs)
                print(f"Using {channel}")
                break
            except Exception:
                continue

        if not browser:
            print("Could not launch any browser. Install chromium:")
            print("  playwright install chromium")
            sys.exit(1)

        context = browser.new_context()
        page = context.new_page()
        print("Browser opened!")

        # Navigate to Teams — user drives everything from here
        print(f"Navigating to {TEAMS_URL}...")
        try:
            page.goto(TEAMS_URL, wait_until="domcontentloaded", timeout=60000)
            time.sleep(2)
        except Exception as e:
            print(f"Navigation note: {e}")

        print("\n" + "=" * 70)
        print("YOUR TURN — do all of this in the browser window:")
        print("=" * 70)
        print("  1. Log in with your Eli Lilly SSO / MFA credentials")
        print("  2. Navigate to the Team + channel for the workshop")
        print("  3. Open the 'Design Thinking-Agentic AI workshop' meeting")
        print("     chat / reply thread (March 12)")
        print("  4. Scroll to the VERY TOP of the thread so older messages load")
        print("=" * 70)
        sentinel = os.path.join(OUTPUT_DIR, "go.txt")
        # Remove any leftover sentinel from a previous run
        if os.path.exists(sentinel):
            os.remove(sentinel)

        print(f"\nWhen you are in position, create this file to start scraping:")
        print(f"  touch \"{sentinel}\"")
        print(f"\nWaiting for {sentinel} ...")
        while not os.path.exists(sentinel):
            time.sleep(2)
        os.remove(sentinel)
        print("Sentinel detected — starting scrape!")
        print()

        print("\nCapturing current page state...")
        page_title = page.title()
        page_url = page.url
        print(f"  Title : {page_title}")
        print(f"  URL   : {page_url}")

        # ── Dump raw HTML for selector diagnostics ───────────────────────────
        html_dump_path = os.path.join(OUTPUT_DIR, "debug_page.html")
        with open(html_dump_path, 'w', encoding='utf-8') as f:
            f.write(page.content())
        print(f"  HTML dump saved: {html_dump_path}")

        # ── Scroll & Scrape ─────────────────────────────────────────────────
        messages = scroll_to_load_all(page, pause=2.0, max_scrolls=80)

        if not messages:
            print("\nNo messages found with automatic selectors.")
            print("Trying a broader text extraction from the visible page...")

            # Last-resort: grab all visible text blocks
            raw_text = page.evaluate("""
                () => {
                    const blocks = [];
                    document.querySelectorAll('p, span, div').forEach(el => {
                        const t = el.innerText.trim();
                        if (t.length > 20 && el.children.length === 0) {
                            blocks.push(t);
                        }
                    });
                    return [...new Set(blocks)];
                }
            """)
            messages = [{'sender': '', 'timestamp': '', 'text': t} for t in raw_text if t]
            print(f"  Extracted {len(messages)} text blocks via fallback.")

        print(f"\nTotal messages captured: {len(messages)}")

        # ── Save ─────────────────────────────────────────────────────────────
        txt_path, json_path, md_path = save_results(messages, page_title, page_url)

        print("\n" + "=" * 70)
        print("SCRAPE COMPLETE!")
        print("=" * 70)
        print(f"Messages : {len(messages)}")
        print(f"Output   : {OUTPUT_DIR}/")
        print(f"  TXT    : {txt_path}")
        print(f"  JSON   : {json_path}")
        print(f"  MD     : {md_path}")
        print("=" * 70)

        print("\nClosing browser in 5 seconds...")
        time.sleep(5)
        browser.close()
        print("Done.")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        try:
            browser.close()
        except Exception:
            pass

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        try:
            browser.close()
        except Exception:
            pass
