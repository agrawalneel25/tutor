"""Headful Imperial SSO login. Persists Playwright storage_state per host.

Unified flow (`login_all`): opens one browser, navigates to Panopto (user
completes Imperial Azure AD SSO once), saves Panopto cookies, then navigates
to Blackboard in the SAME context — Azure SSO redirects silently — and saves
Blackboard cookies. One human interaction, two cookie files.

Sequential flows (`login_panopto`, `login_blackboard`) are kept for repair
when one host's cookies expire but the other is still valid.
"""
from __future__ import annotations
from pathlib import Path

from playwright.sync_api import sync_playwright, BrowserContext
from rich import print

from .config import PANOPTO_HOST, BLACKBOARD_HOST, PANOPTO_STATE, BLACKBOARD_STATE


PANOPTO_HOME = f"{PANOPTO_HOST}/Panopto/Pages/Home.aspx"
BLACKBOARD_HOME = f"{BLACKBOARD_HOST}/ultra/course"

PANOPTO_SUCCESS = "imperial.cloud.panopto.eu/Panopto/Pages"
BLACKBOARD_SUCCESS = "bb.imperial.ac.uk/ultra"


def _wait_and_save(ctx: BrowserContext, url: str, success_substr: str, state_path: Path, label: str) -> None:
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    print(f"[bold cyan]Opening {label}[/]  -  waiting for login to complete.")
    print(f"[dim]Success when URL contains:[/] {success_substr}")
    page.goto(url)
    page.wait_for_url(lambda u: success_substr in u, timeout=0)
    page.wait_for_timeout(2000)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    ctx.storage_state(path=str(state_path))
    print(f"[green]Saved {label} session -> {state_path}[/]")


def login_panopto() -> None:
    """Single-host: Panopto only. Use for cookie repair."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        ctx.new_page()
        _wait_and_save(ctx, PANOPTO_HOME, PANOPTO_SUCCESS, PANOPTO_STATE, "Panopto")
        browser.close()


def login_blackboard() -> None:
    """Single-host: Blackboard only. Use for cookie repair."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        ctx.new_page()
        _wait_and_save(ctx, BLACKBOARD_HOME, BLACKBOARD_SUCCESS, BLACKBOARD_STATE, "Blackboard")
        browser.close()


def login_all() -> None:
    """Unified SSO: one browser, one Imperial login, two cookie dumps.

    Works because Imperial uses a single Azure AD IDP for both Panopto and
    Blackboard — once the browser context has an IDP session cookie, the
    second host SSO redirects through without user interaction.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        ctx.new_page()
        print("[bold]Imperial SSO[/]  -  one login covers both Panopto and Blackboard.")
        _wait_and_save(ctx, PANOPTO_HOME, PANOPTO_SUCCESS, PANOPTO_STATE, "Panopto")
        # Reuse the same context: the IDP session is already established.
        _wait_and_save(ctx, BLACKBOARD_HOME, BLACKBOARD_SUCCESS, BLACKBOARD_STATE, "Blackboard")
        browser.close()
    print("[green]Done  -  both hosts authenticated from one browser session.[/]")


def cookies_for_httpx(state_path: Path) -> dict[str, str]:
    """Load Playwright storage_state, return cookie dict for the target host."""
    import json
    data = json.loads(state_path.read_text())
    return {c["name"]: c["value"] for c in data.get("cookies", [])}
