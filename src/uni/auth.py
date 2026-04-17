"""One-time headful SSO login. Persists storage_state.json for reuse."""
from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright
from rich import print

from .config import PANOPTO_HOST, BLACKBOARD_HOST, PANOPTO_STATE, BLACKBOARD_STATE


def _login(target_url: str, state_path: Path, label: str, success_substr: str) -> None:
    print(f"[bold cyan]Opening {label}[/]. Complete Imperial SSO login in the browser.")
    print(f"[dim]Waiting until URL contains:[/] {success_substr}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(target_url)
        # Wait indefinitely for successful landing back on target host
        page.wait_for_url(lambda u: success_substr in u, timeout=0)
        # give a beat for cookies to settle
        page.wait_for_timeout(2000)
        ctx.storage_state(path=str(state_path))
        browser.close()
    print(f"[green]Saved {label} session -> {state_path}[/]")


def login_panopto() -> None:
    _login(
        f"{PANOPTO_HOST}/Panopto/Pages/Home.aspx",
        PANOPTO_STATE,
        "Panopto",
        "imperial.cloud.panopto.eu/Panopto/Pages",
    )


def login_blackboard() -> None:
    _login(
        f"{BLACKBOARD_HOST}/ultra/course",
        BLACKBOARD_STATE,
        "Blackboard",
        "bb.imperial.ac.uk/ultra",
    )


def cookies_for_httpx(state_path: Path) -> dict[str, str]:
    """Load Playwright storage_state, return cookie dict for the target host."""
    import json
    data = json.loads(state_path.read_text())
    return {c["name"]: c["value"] for c in data.get("cookies", [])}
