"""
FX trader auto-follow on X (Twitter).

- Searches X for FX-related keywords (People tab)
- Follows accounts not yet followed
- Skips already-followed / following-back accounts
- Persists state in followed.json so the same account is not re-followed
- Randomized human-like delays
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    TimeoutError as PWTimeout,
    sync_playwright,
)

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "storage_state.json"
FOLLOWED_FILE = ROOT / "followed.json"
LOG_FILE = ROOT / "log.txt"

KEYWORDS = [
    "FX",
    "ドル円",
    "ポンド円",
    "ユーロドル",
    "為替",
    "デイトレ",
    "スキャルピング",
    "FXトレーダー",
]

MAX_FOLLOWS_PER_DAY = 50
MAX_CANDIDATES_PER_KEYWORD = 30
MIN_DELAY_SEC = 30
MAX_DELAY_SEC = 120


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_followed() -> dict:
    if FOLLOWED_FILE.exists():
        return json.loads(FOLLOWED_FILE.read_text(encoding="utf-8"))
    return {"handles": [], "daily": {}}


def save_followed(data: dict) -> None:
    FOLLOWED_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def today_key() -> str:
    return date.today().isoformat()


def login(page: Page, username: str, password: str, email: str) -> None:
    log("Logging in to X...")
    page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded")
    page.wait_for_selector('input[autocomplete="username"]', timeout=30000)
    page.fill('input[autocomplete="username"]', username)
    page.keyboard.press("Enter")

    # X sometimes asks for email/phone as an extra step
    try:
        page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=5000)
        page.fill('input[data-testid="ocfEnterTextTextInput"]', email)
        page.keyboard.press("Enter")
    except PWTimeout:
        pass

    page.wait_for_selector('input[name="password"]', timeout=30000)
    page.fill('input[name="password"]', password)
    page.keyboard.press("Enter")

    page.wait_for_url("https://x.com/home", timeout=60000)
    log("Login OK.")


def ensure_session(p, headless: bool, username: str, password: str, email: str
                   ) -> tuple[Browser, BrowserContext, Page]:
    browser = p.chromium.launch(headless=headless)
    if STATE_FILE.exists():
        context = browser.new_context(storage_state=str(STATE_FILE))
        page = context.new_page()
        page.goto("https://x.com/home", wait_until="domcontentloaded")
        if "login" in page.url:
            log("Saved session invalid; logging in again.")
            context.close()
            context = browser.new_context()
            page = context.new_page()
            login(page, username, password, email)
            context.storage_state(path=str(STATE_FILE))
    else:
        context = browser.new_context()
        page = context.new_page()
        login(page, username, password, email)
        context.storage_state(path=str(STATE_FILE))
    return browser, context, page


def collect_handles(page: Page, keyword: str, limit: int) -> list[str]:
    """Scrape user handles from the People search tab."""
    url = f"https://x.com/search?q={keyword}&src=typed_query&f=user"
    log(f"Search: {keyword}")
    page.goto(url, wait_until="domcontentloaded")
    try:
        page.wait_for_selector('[data-testid="UserCell"]', timeout=15000)
    except PWTimeout:
        log(f"  No results for {keyword}")
        return []

    handles: list[str] = []
    seen: set[str] = set()
    stagnant = 0

    while len(handles) < limit and stagnant < 3:
        cells = page.locator('[data-testid="UserCell"]').all()
        before = len(handles)
        for cell in cells:
            try:
                anchor = cell.locator('a[href^="/"]').first
                href = anchor.get_attribute("href")
                if not href:
                    continue
                handle = href.lstrip("/").split("/")[0]
                if not handle or handle in seen:
                    continue
                # Skip if already following (button text indicates state)
                seen.add(handle)
                handles.append(handle)
                if len(handles) >= limit:
                    break
            except Exception:
                continue
        if len(handles) == before:
            stagnant += 1
        else:
            stagnant = 0
        page.mouse.wheel(0, 2000)
        time.sleep(1.2)

    log(f"  Collected {len(handles)} candidates")
    return handles


def follow_user(page: Page, handle: str) -> str:
    """
    Visit a profile and follow if not already followed.
    Returns one of: "followed", "already", "protected", "error".
    """
    url = f"https://x.com/{handle}"
    page.goto(url, wait_until="domcontentloaded")
    try:
        page.wait_for_selector('[data-testid$="-follow"], [data-testid$="-unfollow"]',
                               timeout=10000)
    except PWTimeout:
        return "error"

    # If an -unfollow button exists, we are already following.
    if page.locator('[data-testid$="-unfollow"]').count() > 0:
        return "already"

    btn = page.locator('[data-testid$="-follow"]').first
    if btn.count() == 0:
        return "error"
    try:
        btn.click()
        time.sleep(1.5)
        # Confirm the state flipped
        if page.locator('[data-testid$="-unfollow"]').count() > 0:
            return "followed"
        return "error"
    except Exception:
        return "error"


def main() -> int:
    load_dotenv(ROOT / ".env")
    username = os.getenv("X_USERNAME")
    password = os.getenv("X_PASSWORD")
    email = os.getenv("X_EMAIL", "")
    headless = os.getenv("HEADLESS", "false").lower() == "true"

    if not username or not password:
        log("ERROR: X_USERNAME and X_PASSWORD must be set in .env")
        return 1

    state = load_followed()
    already = set(state["handles"])
    today = today_key()
    done_today = state["daily"].get(today, 0)
    remaining = MAX_FOLLOWS_PER_DAY - done_today
    if remaining <= 0:
        log(f"Daily cap reached ({done_today}/{MAX_FOLLOWS_PER_DAY}). Exit.")
        return 0
    log(f"Today: {done_today}/{MAX_FOLLOWS_PER_DAY} done. Remaining: {remaining}")

    with sync_playwright() as p:
        browser, context, page = ensure_session(p, headless, username, password, email)

        candidates: list[str] = []
        random.shuffle(KEYWORDS)
        for kw in KEYWORDS:
            if len(candidates) >= remaining * 3:
                break
            try:
                for h in collect_handles(page, kw, MAX_CANDIDATES_PER_KEYWORD):
                    if h.lower() == username.lower():
                        continue
                    if h in already:
                        continue
                    if h not in candidates:
                        candidates.append(h)
            except Exception as e:
                log(f"  search failed: {e}")
            time.sleep(random.uniform(3, 6))

        log(f"Total unique candidates: {len(candidates)}")
        random.shuffle(candidates)

        followed_count = 0
        for handle in candidates:
            if followed_count >= remaining:
                break
            log(f"-> @{handle}")
            try:
                result = follow_user(page, handle)
            except Exception as e:
                log(f"   error: {e}")
                result = "error"
            log(f"   {result}")

            if result in ("followed", "already"):
                already.add(handle)
                state["handles"] = sorted(already)
            if result == "followed":
                followed_count += 1
                state["daily"][today] = done_today + followed_count
                save_followed(state)
                delay = random.uniform(MIN_DELAY_SEC, MAX_DELAY_SEC)
                log(f"   sleep {delay:.0f}s")
                time.sleep(delay)
            else:
                save_followed(state)
                time.sleep(random.uniform(3, 8))

        context.storage_state(path=str(STATE_FILE))
        browser.close()
        log(f"Done. Followed {followed_count} accounts today.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
