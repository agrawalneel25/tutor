"""Blackboard client for Imperial.

Reality check (2026-04-17): Imperial's JMC courses are "Ultra-wrapped Learn
Original"  -  Ultra navigation shell around classic Learn Original content.
The `/learn/api/` REST endpoints only expose the Ultra shell (Homepage,
Reading List) and give 403 on children; the real material lives at
`/webapps/blackboard/content/listContent.jsp` and must be scraped.

This module:
- `list_courses()`           -  REST works, cookie-authenticated.
- `list_roots(course_id)`    -  REST top-level items (Homepage + Reading List).
- `scrape(course_id, content_id)`  -  recursively walks Learn Original folder pages.
- `download_folder_files()`  -  grabs every `/bbcswebdav/...` attachment in a subtree.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs

import httpx
from bs4 import BeautifulSoup

from .auth import cookies_for_httpx
from .config import BLACKBOARD_HOST, BLACKBOARD_STATE, BB_COOKIE_ALLOWLIST


@dataclass
class Course:
    id: str
    name: str
    course_id: str  # human code like "13433.202510"


@dataclass
class Item:
    """A content node on a Learn Original folder page."""
    title: str
    content_id: str
    is_folder: bool
    description: str = ""
    files: list[tuple[str, str]] = field(default_factory=list)  # (label, absolute_url)


def _client() -> httpx.Client:
    all_cookies = cookies_for_httpx(BLACKBOARD_STATE)
    cookies = {k: v for k, v in all_cookies.items() if k in BB_COOKIE_ALLOWLIST}
    return httpx.Client(
        base_url=BLACKBOARD_HOST,
        cookies=cookies,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/json",
            "Referer": f"{BLACKBOARD_HOST}/ultra/course",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        },
        timeout=45,
        follow_redirects=True,
    )


# ---------- REST (courses list) ----------

def list_courses() -> list[Course]:
    with _client() as c:
        r = c.get("/learn/api/public/v1/users/me/courses",
                  params={"limit": 200, "expand": "course"})
        r.raise_for_status()
        out: list[Course] = []
        for row in r.json().get("results", []):
            course = row.get("course") or {}
            out.append(Course(
                id=course.get("id", row.get("courseId", "")),
                name=course.get("name", ""),
                course_id=course.get("courseId", ""),
            ))
        return out


def list_roots(course_id: str) -> list[Item]:
    """Top-level items via REST (where it still works). Use the returned ids as
    entry points for `scrape()`."""
    with _client() as c:
        r = c.get(f"/learn/api/v1/courses/{course_id}/contents", params={"limit": 100})
        r.raise_for_status()
        out: list[Item] = []
        for row in r.json().get("results", []):
            detail = row.get("contentDetail") or {}
            is_folder = False
            for v in detail.values():
                if isinstance(v, dict) and v.get("isFolder"):
                    is_folder = True
                    break
            out.append(Item(
                title=row.get("title", ""),
                content_id=row["id"],
                is_folder=is_folder,
            ))
        return out


# ---------- Learn Original scraping ----------

def _parse_folder_page(html: str) -> list[Item]:
    soup = BeautifulSoup(html, "lxml")
    items: list[Item] = []
    for li in soup.select("ul#content_listContainer > li"):
        li_id = li.get("id", "")  # e.g. "contentListItem:_3658206_1"
        if ":" not in li_id:
            continue
        content_id = li_id.split(":", 1)[1]

        a = li.select_one("h3 a")
        if not a:
            continue
        title = a.get_text(strip=True)
        href = a.get("href", "")

        img = li.select_one("img.item_icon") or li.select_one("img[alt]")
        kind = (img.get("alt", "") if img else "").strip()

        desc_el = li.select_one(".details .vtbegenerated, .details")
        description = desc_el.get_text(" ", strip=True) if desc_el else ""

        is_folder = (kind == "Content Folder") or "listContent.jsp" in href
        files: list[tuple[str, str]] = []

        if not is_folder:
            # Primary link if it's a direct file/download/external
            if href and ("/bbcswebdav/" in href or "/xid-" in href):
                files.append((title, urljoin(BLACKBOARD_HOST, href)))
            # Any additional attachments inside the description
            for fa in li.select("a[href*='/bbcswebdav/'], a[href*='/xid-']"):
                fu = urljoin(BLACKBOARD_HOST, fa["href"])
                label = fa.get_text(strip=True) or title
                files.append((label, fu))
            seen: set[str] = set()
            files = [(l, u) for l, u in files if not (u in seen or seen.add(u))]

        items.append(Item(
            title=title,
            content_id=content_id,
            is_folder=is_folder,
            description=description,
            files=files,
        ))
    return items


def list_classic(course_id: str, content_id: str) -> list[Item]:
    """One folder page of Learn Original content."""
    with _client() as c:
        r = c.get("/webapps/blackboard/content/listContent.jsp",
                  params={"course_id": course_id, "content_id": content_id})
        r.raise_for_status()
        return _parse_folder_page(r.text)


def scrape(course_id: str, content_id: str, max_depth: int = 5) -> list[tuple[list[str], Item]]:
    """DFS walk a Learn Original subtree."""
    out: list[tuple[list[str], Item]] = []
    seen: set[str] = set()

    def _walk(cid: str, trail: list[str], depth: int) -> None:
        if depth > max_depth or cid in seen:
            return
        seen.add(cid)
        for item in list_classic(course_id, cid):
            out.append((trail, item))
            if item.is_folder:
                _walk(item.content_id, trail + [item.title], depth + 1)

    _walk(content_id, [], 0)
    return out


def download_folder_files(
    course_id: str,
    content_id: str,
    out_dir: Path,
    recursive: bool = True,
) -> list[Path]:
    """Download every attached file in a folder (and optionally its subtree)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    def _fetch(item: Item, trail: list[str]) -> None:
        subdir = out_dir / Path(*[_safe(p) for p in trail]) if trail else out_dir
        subdir.mkdir(parents=True, exist_ok=True)
        with _client() as c:
            for label, url in item.files:
                # Follow redirects to resolve the actual filename
                r = c.get(url)
                r.raise_for_status()
                name = _filename_from_response(r, fallback=f"{_safe(label)}.bin")
                path = subdir / name
                path.write_bytes(r.content)
                written.append(path)

    if recursive:
        for trail, item in scrape(course_id, content_id):
            if item.files:
                _fetch(item, trail + [item.title])
    else:
        for item in list_classic(course_id, content_id):
            if item.files:
                _fetch(item, [item.title])

    return written


def _safe(s: str) -> str:
    import re
    return re.sub(r"[^\w\- .]+", "_", s).strip()[:80] or "_"


def _filename_from_response(r: httpx.Response, fallback: str) -> str:
    cd = r.headers.get("content-disposition", "")
    import re
    m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', cd)
    if m:
        from urllib.parse import unquote
        return _safe(unquote(m.group(1)))
    # Fall back to URL path
    path = urlparse(str(r.url)).path
    name = path.rsplit("/", 1)[-1]
    if "." in name:
        return _safe(name)
    return fallback
