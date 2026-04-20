"""Scientia/CATE document-library search and indexing."""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

from .config import KNOWLEDGE_DIR, USER

SCIENTIA_INDEX_JSON = KNOWLEDGE_DIR / "scientia-index.json"
SUPPORTED_EXTS = {".pdf", ".md", ".txt", ".rst", ".markdown"}
DISCOVERY_HINTS = ("scientia", "cate", "library", "export", "notes", "materials", "course")


@dataclass
class ScientiaDocument:
    path: str
    relpath: str
    ext: str
    title: str
    kind: str
    size: int
    mtime: str
    text: str
    truncated: bool = False


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def default_root() -> Optional[Path]:
    raw = USER.scientia_root.strip()
    if not raw:
        return None
    return Path(raw).expanduser()


def _candidate_roots() -> list[Path]:
    home = Path.home()
    candidates = [
        home,
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
        home / "OneDrive",
        home / "OneDrive - Imperial College London",
        home / "OneDrive - Imperial College London" / "Documents",
    ]
    out: list[Path] = []
    seen: set[str] = set()
    for p in candidates:
        if not p.exists():
            continue
        key = str(p.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def discover_roots(limit: int = 20) -> list[Path]:
    """Find likely Scientia/CATE export roots without manual browsing."""
    hits: list[Path] = []
    seen: set[str] = set()
    for base in _candidate_roots():
        try:
            for root, dirs, _files in os.walk(base):
                rel = Path(root).relative_to(base)
                if len(rel.parts) > 4:
                    dirs[:] = []
                    continue
                name = Path(root).name.lower()
                if any(h in name for h in DISCOVERY_HINTS):
                    resolved = str(Path(root).resolve()).lower()
                    if resolved not in seen:
                        seen.add(resolved)
                        hits.append(Path(root))
                        if len(hits) >= limit:
                            return hits
        except OSError:
            continue
    return hits


def _iter_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTS and not path.name.startswith("~$"):
            yield path


def _title_from_path(path: Path) -> str:
    stem = path.stem
    title = re.sub(r"[_\-\s]+", " ", stem).strip()
    return title or path.name


def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _extract_pdf_text(path: Path) -> str:
    from pypdf import PdfReader

    try:
        reader = PdfReader(str(path))
    except Exception:
        return ""
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)


def _extract_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return _extract_pdf_text(path)
    if path.suffix.lower() in {".md", ".txt", ".rst", ".markdown"}:
        return _read_text_file(path)
    return ""


def build_index(root: Path, *, max_text_chars: int = 250_000) -> dict:
    root = root.resolve()
    docs: list[ScientiaDocument] = []
    for path in _iter_files(root):
        stat = path.stat()
        text = _extract_text(path)
        truncated = False
        if len(text) > max_text_chars:
            text = text[:max_text_chars]
            truncated = True
        docs.append(ScientiaDocument(
            path=str(path.resolve()),
            relpath=str(path.relative_to(root)),
            ext=path.suffix.lower(),
            title=_title_from_path(path),
            kind="pdf" if path.suffix.lower() == ".pdf" else "text",
            size=stat.st_size,
            mtime=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(timespec="seconds"),
            text=text,
            truncated=truncated,
        ))
    return {
        "root": str(root),
        "generated_at": _now(),
        "doc_count": len(docs),
        "documents": [asdict(d) for d in docs],
    }


def save_index(index: dict) -> None:
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    SCIENTIA_INDEX_JSON.write_text(json.dumps(index, indent=2), encoding="utf-8")


def load_index() -> dict | None:
    if not SCIENTIA_INDEX_JSON.exists():
        return None
    try:
        return json.loads(SCIENTIA_INDEX_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def _snippet(text: str, query: str, width: int = 180) -> str:
    if not text:
        return ""
    low = text.lower()
    q = query.lower()
    idx = low.find(q)
    if idx < 0:
        for tok in [t for t in re.split(r"\W+", q) if t]:
            idx = low.find(tok)
            if idx >= 0:
                q = tok
                break
    if idx < 0:
        return re.sub(r"\s+", " ", text[:width]).strip()
    start = max(0, idx - width // 3)
    end = min(len(text), idx + len(q) + (2 * width // 3))
    return re.sub(r"\s+", " ", text[start:end]).strip()


def _score_doc(doc: dict, query: str) -> tuple[int, str]:
    q = _normalize(query)
    tokens = [t for t in re.split(r"\W+", q) if t]
    title = _normalize(doc.get("title", ""))
    relpath = _normalize(doc.get("relpath", ""))
    text = _normalize(doc.get("text", ""))
    hay = " ".join([title, relpath, text])

    score = 0
    if q and q in hay:
        score += 12
    for tok in tokens:
        if tok in title:
            score += 4
        if tok in relpath:
            score += 4
        if tok in text:
            score += 1
    snippet = _snippet(doc.get("text", ""), query)
    if not snippet:
        snippet = doc.get("relpath", "")
    return score, snippet


def search(query: str, root: Path | None = None, limit: int = 20) -> list[dict]:
    query = query.strip()
    if not query:
        return []

    index = load_index()
    if index is not None and root is not None:
        if Path(index.get("root", "")).resolve() != root.resolve():
            index = None

    if index is None:
        resolved = root or default_root()
        if resolved is None:
            return []
        index = build_index(resolved)
        save_index(index)

    scored: list[dict] = []
    for doc in index.get("documents", []):
        score, snippet = _score_doc(doc, query)
        if score <= 0:
            continue
        item = dict(doc)
        item["score"] = score
        item["snippet"] = snippet
        scored.append(item)

    scored.sort(key=lambda d: (-d["score"], d["relpath"]))
    return scored[:limit]
