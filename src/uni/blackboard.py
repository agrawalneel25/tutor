"""Blackboard Learn Ultra scraper. Uses saved SSO cookies.

Imperial uses Blackboard's public REST API at /learn/api/public/v1/*, which
the Ultra UI itself calls. Session cookies from SSO authenticate these calls
the same way they authenticate the UI.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import httpx

from .auth import cookies_for_httpx
from .config import BLACKBOARD_HOST, BLACKBOARD_STATE


@dataclass
class Course:
    id: str
    name: str
    course_id: str  # human code like MATH40002


@dataclass
class Content:
    id: str
    title: str
    content_handler: str
    has_children: bool


# Only these cookies are meaningful to Blackboard; sending the full Azure AD
# cookie set triggers nginx "Request Header Or Cookie Too Large" (400).
_BB_COOKIE_ALLOWLIST = {
    "BbRouter", "JSESSIONID", "AWSELB", "AWSELBCORS",
    "shib_idp_session", "samlCookie", "SSOCOOKIEPULLED", "s_session_id",
}


def _client() -> httpx.Client:
    all_cookies = cookies_for_httpx(BLACKBOARD_STATE)
    cookies = {k: v for k, v in all_cookies.items() if k in _BB_COOKIE_ALLOWLIST}
    return httpx.Client(
        base_url=BLACKBOARD_HOST,
        cookies=cookies,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Referer": f"{BLACKBOARD_HOST}/ultra/course",
        },
        timeout=30,
    )


def list_courses() -> list[Course]:
    """Courses the current user is enrolled in."""
    with _client() as c:
        r = c.get("/learn/api/public/v1/users/me/courses", params={"limit": 200, "expand": "course"})
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


def list_contents(course_id: str, parent_id: str | None = None) -> list[Content]:
    """Children of a course folder. Uses /learn/api/v1 with parentId query
    because /public/v1/.../children returns 403 for student cookies.

    Schema is Ultra's internal format, not the documented Public v1 one:
      - `id`, `title`, `contentDetail` present.
      - Folder-ness signaled by `contentDetail["resource/x-bb-folder"].isFolder`.
      - `contentHandler` may be a dict or missing; we flatten to a short string.
    """
    path = f"/learn/api/v1/courses/{course_id}/contents"
    params: dict[str, str | int] = {"limit": 200}
    if parent_id:
        params["parentId"] = parent_id
    with _client() as c:
        r = c.get(path, params=params)
        r.raise_for_status()
        out: list[Content] = []
        for row in r.json().get("results", []):
            detail = row.get("contentDetail") or {}
            is_folder = False
            handler = ""
            for key, val in detail.items():
                handler = key  # e.g. "resource/x-bb-folder", "resource/x-bb-file"
                if isinstance(val, dict) and val.get("isFolder"):
                    is_folder = True
                break
            ch = row.get("contentHandler")
            if isinstance(ch, dict):
                handler = ch.get("id") or handler
            elif isinstance(ch, str):
                handler = ch or handler
            out.append(Content(
                id=row["id"],
                title=row.get("title", ""),
                content_handler=handler,
                has_children=is_folder,
            ))
        return out


def download_attachments(course_id: str, content_id: str, out_dir: Path) -> list[Path]:
    """Download all file attachments of a content item."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    with _client() as c:
        r = c.get(f"/learn/api/public/v1/courses/{course_id}/contents/{content_id}/attachments")
        r.raise_for_status()
        for att in r.json().get("results", []):
            att_id = att["id"]
            name = att.get("fileName") or f"{att_id}.bin"
            dl = c.get(
                f"/learn/api/public/v1/courses/{course_id}/contents/{content_id}/attachments/{att_id}/download",
                follow_redirects=True,
            )
            dl.raise_for_status()
            path = out_dir / name
            path.write_bytes(dl.content)
            written.append(path)
    return written


def walk_tree(course_id: str, max_depth: int = 6) -> list[tuple[list[str], Content]]:
    """DFS the content tree. Dedupes by id (Ultra can return cycles)."""
    out: list[tuple[list[str], Content]] = []
    seen: set[str] = set()

    def _walk(parent: str | None, trail: list[str]) -> None:
        if len(trail) > max_depth:
            return
        for item in list_contents(course_id, parent):
            if item.id in seen:
                continue
            seen.add(item.id)
            out.append((trail, item))
            if item.has_children:
                _walk(item.id, trail + [item.title])

    _walk(None, [])
    return out
