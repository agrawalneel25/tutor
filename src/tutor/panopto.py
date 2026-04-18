"""Panopto client. Uses saved SSO cookies against the /api/v1/* REST endpoints.

These endpoints are the same ones the web UI hits. Session cookie auth works  - 
no OAuth client registration needed.

Docs (schemas): https://imperial.cloud.panopto.eu/Panopto/api/docs/index.html
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import httpx

from .auth import cookies_for_httpx
from .config import PANOPTO_HOST, PANOPTO_STATE


@dataclass
class Session:
    delivery_id: str
    name: str
    duration_s: float
    start_time: str
    folder_id: str

    @property
    def viewer_url(self) -> str:
        return f"{PANOPTO_HOST}/Panopto/Pages/Viewer.aspx?id={self.delivery_id}"


@dataclass
class Folder:
    id: str
    name: str


def _client() -> httpx.Client:
    cookies = cookies_for_httpx(PANOPTO_STATE)
    return httpx.Client(
        base_url=PANOPTO_HOST,
        cookies=cookies,
        headers={
            "Accept": "application/json",
            "Referer": f"{PANOPTO_HOST}/Panopto/Pages/Sessions/List.aspx",
        },
        timeout=30,
        follow_redirects=False,
    )


def _check_auth(r: httpx.Response) -> None:
    if r.status_code in (301, 302, 303) and "SignIn" in r.headers.get("location", ""):
        raise RuntimeError("Panopto session expired. Run `uv run tutor auth panopto`.")
    if r.status_code == 401:
        raise RuntimeError("Panopto 401  -  re-auth with `uv run tutor auth panopto`.")


def parse_folder_id(folder_url_or_id: str) -> str:
    s = folder_url_or_id.strip()
    if re.fullmatch(r"[0-9a-fA-F-]{36}", s):
        return s
    parsed = urlparse(s)
    for src in (parsed.query, parsed.fragment):
        q = parse_qs(src)
        for key in ("folderID", "folderId", "id"):
            if key in q:
                return q[key][0]
    raise ValueError(f"Could not parse folder ID from: {folder_url_or_id}")


def search_folders(query: str = "*", parent_id: str | None = None, max_results: int = 100) -> list[Folder]:
    """Search folders by name. The API requires a non-empty searchQuery; `*` = all."""
    params: dict[str, str | int] = {
        "searchQuery": query or "*",
        "sortField": "Name",
        "sortOrder": "Asc",
        "pageNumber": 0,
        "maxNumberResults": max_results,
    }
    if parent_id:
        params["parentFolderId"] = parent_id
    with _client() as c:
        r = c.get("/Panopto/api/v1/folders/search", params=params)
        _check_auth(r)
        r.raise_for_status()
        return [Folder(id=f["Id"], name=f.get("Name", "")) for f in r.json().get("Results", [])]


def list_subfolders(parent_folder_id: str | None = None) -> list[Folder]:
    """Alias  -  historical name."""
    return search_folders(parent_id=parent_folder_id)


def list_sessions(folder_id: str, max_results: int = 250) -> list[Session]:
    """List sessions in a folder via Data.svc (the web UI's own endpoint).

    The /api/v1/sessions/* REST endpoints require OAuth bearer, but Data.svc
    accepts the normal session cookie.
    """
    out: list[Session] = []
    page = 0
    cookies = cookies_for_httpx(PANOPTO_STATE)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": PANOPTO_HOST,
        "Referer": f"{PANOPTO_HOST}/Panopto/Pages/Sessions/List.aspx?folderID={folder_id}",
    }
    with httpx.Client(base_url=PANOPTO_HOST, cookies=cookies, headers=headers, timeout=30) as c:
        while True:
            body = {"queryParameters": {
                "query": None,
                "sortColumn": 1,
                "sortAscending": False,
                "maxResults": 50,
                "page": page,
                "startDate": None,
                "endDate": None,
                "folderID": folder_id,
                "bookmarked": False,
                "getFolderData": False,
                "isSharedWithMe": False,
                "includePlaylists": False,
            }}
            r = c.post("/Panopto/Services/Data.svc/GetSessions", json=body)
            _check_auth(r)
            r.raise_for_status()
            results = (r.json().get("d") or {}).get("Results") or []
            if not results:
                break
            for s in results:
                out.append(Session(
                    delivery_id=s["DeliveryID"],
                    name=s.get("SessionName") or s.get("DeliveryName") or "",
                    duration_s=float(s.get("Duration") or 0),
                    start_time=_ms_date_to_iso(s.get("StartTime") or ""),
                    folder_id=folder_id,
                ))
                if len(out) >= max_results:
                    return out
            page += 1
    return out


def _available_language(client: httpx.Client, delivery_id: str) -> str:
    """Read DeliveryInfo to find which caption language enum this session has."""
    r = client.get(
        "/Panopto/Pages/Viewer/DeliveryInfo.aspx",
        params={"deliveryId": delivery_id, "responseType": "json"},
    )
    _check_auth(r)
    r.raise_for_status()
    delivery = r.json().get("Delivery") or {}
    langs = delivery.get("AvailableLanguages") or []
    if langs:
        return str(langs[0])
    caps = delivery.get("AvailableCaptions") or []
    if caps:
        return str(caps[0].get("Language", 1))
    return "1"  # default: English_GB


def download_transcript(delivery_id: str, out_path: Path, language: str | None = None) -> Path:
    with _client() as c:
        lang = language or _available_language(c, delivery_id)
        r = c.get(
            "/Panopto/Pages/Transcription/GenerateSRT.ashx",
            params={"id": delivery_id, "language": lang},
        )
        _check_auth(r)
        r.raise_for_status()
        if not r.text.strip():
            raise RuntimeError(
                f"Transcript empty for {delivery_id} (language={lang}). "
                f"The session may have no captions  -  check in the Panopto viewer."
            )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(r.text, encoding="utf-8")
    return out_path


_MS_DATE = re.compile(r"/Date\((\d+)")


def _ms_date_to_iso(s: str) -> str:
    m = _MS_DATE.search(s or "")
    if not m:
        return s or ""
    import datetime as _dt
    return _dt.datetime.fromtimestamp(int(m.group(1)) / 1000, tz=_dt.timezone.utc).isoformat()


_SRT_TS = re.compile(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}")


def srt_to_text(srt: str) -> str:
    """Strip SRT indices/timestamps into clean prose."""
    lines: list[str] = []
    for block in srt.strip().split("\n\n"):
        parts = block.split("\n")
        content = [p for p in parts if p.strip() and not p.strip().isdigit() and not _SRT_TS.search(p)]
        if content:
            lines.append(" ".join(content).strip())
    return "\n".join(lines)
