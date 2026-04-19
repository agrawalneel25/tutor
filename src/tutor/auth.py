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

from .config import PANOPTO_HOST, BLACKBOARD_HOST, PANOPTO_STATE, BLACKBOARD_STATE, EXAMS_STATE, EXAMS_CREDS, EXAMS_HOST


PANOPTO_HOME = f"{PANOPTO_HOST}/Panopto/Pages/Home.aspx"
BLACKBOARD_HOME = f"{BLACKBOARD_HOST}/ultra/course"
EXAMS_HOME = f"{EXAMS_HOST}/"

PANOPTO_SUCCESS = "imperial.cloud.panopto.eu/Panopto/Pages"
BLACKBOARD_SUCCESS = "bb.imperial.ac.uk/ultra"
EXAMS_SUCCESS = "exams.doc.ic.ac.uk"


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


def login_exams(username: str = "", password: str = "") -> None:
    """Single-host: exams.doc.ic.ac.uk. Passes HTTP Basic Auth credentials."""
    import json
    http_credentials = {"username": username, "password": password} if username else None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(http_credentials=http_credentials)
        ctx.new_page()
        _wait_and_save(ctx, EXAMS_HOME, EXAMS_SUCCESS, EXAMS_STATE, "Exams site")
        browser.close()
    if username:
        EXAMS_CREDS.write_text(json.dumps({"username": username, "password": password}))


def login_all() -> None:
    """Unified SSO: one browser, one Imperial login, three cookie dumps.

    Works because Imperial uses a single Azure AD IDP — once the browser
    context has an IDP session cookie, subsequent hosts SSO silently.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        ctx.new_page()
        print("[bold]Imperial SSO[/]  -  one login covers Panopto, Blackboard, and Exams.")
        _wait_and_save(ctx, PANOPTO_HOME, PANOPTO_SUCCESS, PANOPTO_STATE, "Panopto")
        _wait_and_save(ctx, BLACKBOARD_HOME, BLACKBOARD_SUCCESS, BLACKBOARD_STATE, "Blackboard")
        _wait_and_save(ctx, EXAMS_HOME, EXAMS_SUCCESS, EXAMS_STATE, "Exams site")
        browser.close()
    print("[green]Done  -  all three hosts authenticated from one browser session.[/]")


def cookies_for_httpx(state_path: Path) -> dict[str, str]:
    """Load Playwright storage_state, return cookie dict for the target host."""
    import json
    data = json.loads(state_path.read_text())
    return {c["name"]: c["value"] for c in data.get("cookies", [])}
