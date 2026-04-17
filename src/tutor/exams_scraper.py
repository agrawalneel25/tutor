"""Imperial exam papers scraper for exams.doc.ic.ac.uk.

Uses Playwright (authenticated via stored cookies) to find and download
past paper PDFs. The site structure is discovered at runtime since it's
behind Imperial SSO.
"""
from __future__ import annotations
from pathlib import Path

from playwright.sync_api import sync_playwright
from rich import print

from .config import EXAMS_STATE, EXAMS_HOST, SUBJECTS_DIR


def _papers_dir(module_code: str) -> Path:
    slug = module_code.lower().replace(" ", "-")
    d = SUBJECTS_DIR / slug / "past-papers"
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch_papers(module_code: str, out_dir: Path | None = None) -> list[Path]:
    """Download all past papers for a module code. Returns list of saved paths."""
    if not EXAMS_STATE.exists():
        raise RuntimeError("No exams.doc.ic.ac.uk session found. Run: tutor auth exams")

    import json
    state = json.loads(EXAMS_STATE.read_text())
    out = out_dir or _papers_dir(module_code)
    saved: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state=state)
        page = ctx.new_page()

        print(f"[cyan]Navigating to {EXAMS_HOST}[/]")
        page.goto(EXAMS_HOST, wait_until="networkidle")

        # Try to find a search box and search for the module code.
        search = page.query_selector("input[type='search'], input[type='text'], input[name*='search'], input[placeholder*='search' i]")
        if search:
            search.fill(module_code)
            search.press("Enter")
            page.wait_for_load_state("networkidle")
        else:
            # Navigate directly — some exam sites use URL patterns like /papers?q=COMP40006
            page.goto(f"{EXAMS_HOST}/papers?q={module_code}", wait_until="networkidle")

        # Collect all PDF links on the page.
        links = page.eval_on_selector_all(
            "a[href*='.pdf'], a[href*='/download'], a[href*='/papers']",
            "els => els.map(e => ({href: e.href, text: e.innerText.trim()}))"
        )

        module_lower = module_code.lower()
        pdf_links = [
            l for l in links
            if module_lower in l["href"].lower() or module_lower in l["text"].lower()
               or ".pdf" in l["href"].lower()
        ]

        if not pdf_links:
            print(f"[yellow]No papers found for {module_code}. The site structure may differ — try tutor auth exams to refresh cookies.[/]")
            browser.close()
            return []

        print(f"[green]Found {len(pdf_links)} paper(s) for {module_code}[/]")

        for link in pdf_links:
            href = link["href"]
            label = link["text"] or Path(href).name
            filename = f"{module_code}_{label}.pdf".replace(" ", "_").replace("/", "-")
            dest = out / filename

            if dest.exists():
                print(f"[dim]Skip (exists): {dest.name}[/]")
                saved.append(dest)
                continue

            print(f"  Downloading: {label}")
            try:
                with page.expect_download() as dl_info:
                    page.goto(href)
                download = dl_info.value
                download.save_as(str(dest))
                saved.append(dest)
                print(f"  [green]Saved -> {dest.name}[/]")
            except Exception:
                # If not a direct download, save the response bytes.
                resp = page.goto(href)
                if resp and resp.ok:
                    dest.write_bytes(resp.body())
                    saved.append(dest)
                    print(f"  [green]Saved -> {dest.name}[/]")
                else:
                    print(f"  [red]Failed: {href}[/]")

        browser.close()

    return saved
