"""Health check for every moving part. Run after setup; run when things break.

Each check returns (name, ok, detail). Prints a summary table.
"""
from __future__ import annotations
import shutil
from dataclasses import dataclass
from typing import Callable

import httpx
from rich import print as rprint
from rich.table import Table
from rich.console import Console

from . import panopto as pp
from . import blackboard as bb
from .config import (
    AUTH_DIR, PANOPTO_STATE, BLACKBOARD_STATE,
    PANOPTO_HOST, BLACKBOARD_HOST,
    SUBJECTS,
)
from .auth import cookies_for_httpx

console = Console()


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def check_uv() -> Check:
    exe = shutil.which("uv")
    if not exe:
        return Check("uv installed", False, "uv not on PATH  -  install: https://docs.astral.sh/uv")
    return Check("uv installed", True, exe)


def check_playwright_browser() -> Check:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:  # pragma: no cover
        return Check("playwright import", False, str(e))
    try:
        with sync_playwright() as p:
            path = p.chromium.executable_path
            if path and shutil.which(path) is None:
                # executable_path may be a bundled path; just check it exists
                import os
                if not os.path.exists(path):
                    return Check("playwright chromium", False, f"missing: {path}")
        return Check("playwright chromium", True, "installed")
    except Exception as e:
        return Check("playwright chromium", False, f"{type(e).__name__}: {e}")


def check_auth_state() -> list[Check]:
    return [
        Check("panopto cookies", PANOPTO_STATE.exists(),
              str(PANOPTO_STATE) if PANOPTO_STATE.exists() else "run: uv run tutor auth panopto"),
        Check("blackboard cookies", BLACKBOARD_STATE.exists(),
              str(BLACKBOARD_STATE) if BLACKBOARD_STATE.exists() else "run: uv run tutor auth blackboard"),
    ]


def check_panopto_api() -> Check:
    if not PANOPTO_STATE.exists():
        return Check("panopto api", False, "no cookies")
    try:
        folders = pp.search_folders(query="*", max_results=1)
        return Check("panopto api", True, f"{len(folders)} folder(s) visible")
    except Exception as e:
        return Check("panopto api", False, f"{type(e).__name__}: {e}")


def check_panopto_folder() -> Check:
    """Verify at least one known JMC folder returns sessions."""
    if not PANOPTO_STATE.exists():
        return Check("panopto folder sessions", False, "no cookies")
    meta = SUBJECTS["analysis"]
    if not meta.panopto_folder:
        return Check("panopto folder sessions", False, "no Analysis folder configured")
    try:
        sessions = pp.list_sessions(meta.panopto_folder, max_results=1)
        return Check("panopto folder sessions", bool(sessions),
                     f"analysis folder returned {len(sessions)} session(s)")
    except Exception as e:
        return Check("panopto folder sessions", False, f"{type(e).__name__}: {e}")


def check_bb_api() -> Check:
    if not BLACKBOARD_STATE.exists():
        return Check("blackboard api", False, "no cookies")
    try:
        courses = bb.list_courses()
        return Check("blackboard api", True, f"{len(courses)} course(s) visible")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return Check("blackboard api", False,
                         "HTTP 401  -  cookies expired. Run: uv run tutor auth blackboard")
        if e.response.status_code == 400 and "Cookie Too Large" in e.response.text:
            return Check("blackboard api", False,
                         "cookies too large  -  re-auth (BB cookie allowlist should handle this)")
        return Check("blackboard api", False, f"HTTP {e.response.status_code}")
    except Exception as e:
        return Check("blackboard api", False, f"{type(e).__name__}: {e}")


def check_bb_scraper() -> Check:
    """Verify the Learn Original HTML parser still works on a known folder."""
    if not BLACKBOARD_STATE.exists():
        return Check("blackboard scraper", False, "no cookies")
    meta = SUBJECTS["analysis"]
    if not (meta.bb_course and meta.bb_homepage):
        return Check("blackboard scraper", False, "no Analysis homepage configured")
    try:
        items = bb.list_classic(meta.bb_course, meta.bb_homepage)
        if not items:
            return Check("blackboard scraper", False,
                         "homepage returned 0 items  -  BB UI may have changed; re-check parser")
        return Check("blackboard scraper", True, f"{len(items)} items on Analysis homepage")
    except Exception as e:
        return Check("blackboard scraper", False, f"{type(e).__name__}: {e}")


ALL_CHECKS: list[Callable] = [
    check_uv,
    check_playwright_browser,
    check_panopto_api,
    check_panopto_folder,
    check_bb_api,
    check_bb_scraper,
]


def run_all() -> bool:
    results: list[Check] = [*check_auth_state()]
    for fn in ALL_CHECKS:
        try:
            results.append(fn())
        except Exception as e:  # pragma: no cover  -  defensive
            results.append(Check(fn.__name__, False, f"{type(e).__name__}: {e}"))

    t = Table(title="tutor doctor", show_lines=False)
    t.add_column("Check")
    t.add_column("Status")
    t.add_column("Detail", overflow="fold")
    for c in results:
        t.add_row(c.name, "[green]✓[/]" if c.ok else "[red]✗[/]", c.detail)
    console.print(t)
    ok = all(c.ok for c in results)
    rprint("[bold green]All green.[/]" if ok else "[bold red]Some checks failed.[/]")
    return ok
