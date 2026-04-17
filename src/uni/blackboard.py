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


def _client() -> httpx.Client:
    cookies = cookies_for_httpx(BLACKBOARD_STATE)
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
    path = f"/learn/api/public/v1/courses/{course_id}/contents"
    if parent_id:
        path = f"/learn/api/public/v1/courses/{course_id}/contents/{parent_id}/children"
    with _client() as c:
        r = c.get(path, params={"limit": 200})
        r.raise_for_status()
        out: list[Content] = []
        for row in r.json().get("results", []):
            handler = (row.get("contentHandler") or {}).get("id", "")
            out.append(Content(
                id=row["id"],
                title=row.get("title", ""),
                content_handler=handler,
                has_children=row.get("hasChildren", False),
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


def walk_tree(course_id: str) -> list[tuple[list[str], Content]]:
    """DFS the content tree. Yields (path_names, content)."""
    out: list[tuple[list[str], Content]] = []

    def _walk(parent: str | None, trail: list[str]) -> None:
        for item in list_contents(course_id, parent):
            out.append((trail, item))
            if item.has_children:
                _walk(item.id, trail + [item.title])

    _walk(None, [])
    return out
