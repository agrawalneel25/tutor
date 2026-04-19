"""Imperial exam papers scraper for exams.doc.ic.ac.uk.

Past papers live at /pastpapers/papers.YY-YY/<MODULE>.pdf.
The site uses HTTP Basic Auth (Imperial shortcode + password).
"""
from __future__ import annotations
from pathlib import Path

from playwright.sync_api import sync_playwright
from rich import print

from .config import EXAMS_STATE, EXAMS_CREDS, EXAMS_HOST, SUBJECTS_DIR

def _papers_dir(module_code: str) -> Path:
    slug = module_code.lower().replace(" ", "-")
    d = SUBJECTS_DIR / slug / "past-papers"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_http_credentials() -> dict | None:
    import json
    if EXAMS_CREDS.exists():
        c = json.loads(EXAMS_CREDS.read_text())
        return {"username": c["username"], "password": c["password"]}
    return None


def _discover_year_urls(page) -> list[str]:
    """Scrape homepage + archive to get all /pastpapers/papers.YY-YY/ URLs."""
    import re
    page.goto(EXAMS_HOST, wait_until="networkidle")
    links = page.eval_on_selector_all(
        "a[href*='pastpapers/papers.']",
        "els => els.map(e => e.href)"
    )
    page.goto(f"{EXAMS_HOST}/archive.html", wait_until="networkidle")
    links += page.eval_on_selector_all(
        "a[href*='pastpapers/papers.']",
        "els => els.map(e => e.href)"
    )
    seen: set[str] = set()
    result: list[str] = []
    for url in links:
        url = url.rstrip("/") + "/"
        if url not in seen:
            seen.add(url)
            result.append(url)
    return result


def fetch_papers(module_code: str, out_dir: Path | None = None) -> list[Path]:
    """Download all past papers for a module code. Returns list of saved paths."""
    if not EXAMS_STATE.exists() and not EXAMS_CREDS.exists():
        raise RuntimeError("No exams.doc.ic.ac.uk session found. Run: tutor auth exams")

    http_credentials = _load_http_credentials()
    if not http_credentials:
        raise RuntimeError("No exams credentials found. Run: tutor auth exams")

    out = out_dir or _papers_dir(module_code)
    saved: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(http_credentials=http_credentials)
        page = ctx.new_page()

        year_urls = _discover_year_urls(page)
        print(f"[dim]Searching {len(year_urls)} year directories...[/]")

        for url in year_urls:
            yr = url.rstrip("/").split("papers.")[-1]
            page.goto(url, wait_until="networkidle")
            links = page.eval_on_selector_all(
                f"a[href*='{module_code}']",
                "els => els.map(e => ({href: e.href, text: e.innerText.trim()}))"
            )
            seen: set[str] = set()
            for link in links:
                href = link["href"]
                if href in seen:
                    continue
                seen.add(href)
                filename = f"{module_code}_{yr}.pdf"
                dest = out / filename
                if dest.exists():
                    print(f"[dim]Skip (exists): {dest.name}[/]")
                    saved.append(dest)
                    continue
                print(f"  Downloading {yr}: {link['text'] or href}")
                try:
                    with page.expect_download() as dl_info:
                        page.evaluate(f"window.location.href = '{href}'")
                    dl = dl_info.value
                    dl.save_as(str(dest))
                    saved.append(dest)
                    print(f"  [green]Saved -> {dest.name}[/]")
                except Exception as e:
                    print(f"  [red]Failed: {e}[/]")
                page.goto(url, wait_until="networkidle")

        browser.close()

    if saved:
        print(f"[green]{len(saved)} paper(s) saved to {out}[/]")
    else:
        print(f"[yellow]No papers found for {module_code} across {PAPER_YEARS}.[/]")

    return saved
