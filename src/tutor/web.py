"""Local web UI for reading notes and practising problem sheets.

FastAPI + vanilla HTML/JS frontend. Localhost only  -  no auth, no TLS.
Launch with `uv run tutor web`.
"""
from __future__ import annotations
import json
import threading
import webbrowser
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import REPO, SUBJECTS_DIR, WEBUI_DIR, SUBJECTS, USER
from .problems import SheetProgress, progress_path, sheet_dir


app = FastAPI(title="tutor")

# Sandbox for file reads: only these roots are exposed via /api/file.
_READABLE_ROOTS = (SUBJECTS_DIR, REPO / ".claude" / "knowledge")


def _is_readable(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        return False
    return any(str(resolved).startswith(str(root.resolve())) for root in _READABLE_ROOTS)


def _scan_subject(slug: str) -> dict[str, Any]:
    """Build the nav tree for one subject  -  chapters, lectures, sheets."""
    root = SUBJECTS_DIR / slug
    meta = SUBJECTS[slug]
    out: dict[str, Any] = {
        "slug": slug,
        "code": meta.code,
        "title": meta.title,
        "chapters": [],
        "lectures": [],
        "sheets": [],
    }
    if not root.exists():
        return out

    chapters_dir = root / "chapters"
    if chapters_dir.exists():
        for d in sorted(chapters_dir.iterdir()):
            if not d.is_dir():
                continue
            has_teach = (d / "teach.md").exists()
            has_notes = (d / "notes.md").exists()
            out["chapters"].append({
                "slug": d.name,
                "has_teach": has_teach,
                "has_notes": has_notes,
            })

    lectures_dir = root / "lectures"
    if lectures_dir.exists():
        for d in sorted(lectures_dir.iterdir()):
            if not d.is_dir():
                continue
            meta_path = d / "meta.json"
            meta_json: dict[str, Any] = {}
            if meta_path.exists():
                try:
                    meta_json = json.loads(meta_path.read_text())
                except json.JSONDecodeError:
                    meta_json = {}
            out["lectures"].append({
                "slug": d.name,
                "number": meta_json.get("number"),
                "title": meta_json.get("title", d.name),
                "has_teach": (d / "teach.md").exists(),
                "has_notes": (d / "notes.md").exists(),
                "has_transcript": (d / "transcript.txt").exists(),
            })

    sheets_root = root / "sheets"
    if sheets_root.exists():
        for d in sorted(sheets_root.iterdir()):
            if not d.is_dir():
                continue
            prog = SheetProgress.load(d / ".progress.json")
            total = len(list((d / "problems").glob("q*.md"))) if (d / "problems").exists() else 0
            done = sum(1 for s in prog.questions.values() if s.status == "done")
            out["sheets"].append({
                "slug": d.name,
                "total": total,
                "done": done,
                "current": prog.current,
            })

    return out


@app.get("/api/tree")
def api_tree() -> JSONResponse:
    return JSONResponse({
        "user": {"name": USER.name, "preferences": {
            "hint_style": USER.preferences.hint_style,
            "teach_mode": USER.preferences.teach_mode,
            "reveal_solution_immediately": USER.preferences.reveal_solution_immediately,
        }},
        "subjects": [_scan_subject(s) for s in SUBJECTS.keys()],
    })


@app.get("/api/file")
def api_file(path: str) -> Response:
    """Read any markdown/text file under sandboxed roots."""
    p = (REPO / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if not _is_readable(p):
        raise HTTPException(403, "path outside sandbox")
    if not p.exists() or not p.is_file():
        raise HTTPException(404, "not found")
    return Response(content=p.read_text(encoding="utf-8"), media_type="text/markdown")


@app.get("/api/sheet")
def api_sheet(subject: str, slug: str) -> JSONResponse:
    if subject not in SUBJECTS:
        raise HTTPException(404, "unknown subject")
    d = sheet_dir(subject, slug)
    if not d.exists():
        raise HTTPException(404, "sheet not found")
    prog = SheetProgress.load(progress_path(subject, slug))
    index_path = d / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else None
    questions = []
    problems_dir = d / "problems"
    if problems_dir.exists():
        for qf in sorted(problems_dir.glob("q*.md")):
            qid = qf.stem
            state = prog.questions.get(qid)
            questions.append({
                "id": qid,
                "path": str(qf.relative_to(REPO)),
                "state": (state.__dict__ if state else {"status": "pending", "hints_shown": 0}),
            })
    return JSONResponse({
        "subject": subject,
        "slug": slug,
        "index": index,
        "current": prog.current,
        "questions": questions,
    })


class ProgressUpdate(BaseModel):
    subject: str
    slug: str
    qid: str
    status: str | None = None
    hints_shown: int | None = None
    attempts: int | None = None
    correct: bool | None = None
    last_attempt: str | None = None
    set_current: bool = False


@app.post("/api/progress")
def api_progress(update: ProgressUpdate) -> JSONResponse:
    if update.subject not in SUBJECTS:
        raise HTTPException(404, "unknown subject")
    path = progress_path(update.subject, update.slug)
    prog = SheetProgress.load(path)
    kwargs = {k: v for k, v in update.model_dump().items()
              if k not in {"subject", "slug", "qid", "set_current"} and v is not None}
    prog.touch(update.qid, **kwargs)
    if update.set_current:
        prog.current = update.qid
    prog.save(path)
    return JSONResponse({"ok": True})


# Static frontend  -  mount last so API routes win.
if WEBUI_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(WEBUI_DIR)), name="assets")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(WEBUI_DIR / "index.html"))


def run(port: int | None = None, open_browser: bool = True) -> None:
    import uvicorn
    resolved_port = port or USER.preferences.web_port or 8787
    url = f"http://localhost:{resolved_port}"
    if open_browser:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    print(f"tutor web → {url}")
    uvicorn.run(app, host="127.0.0.1", port=resolved_port, log_level="warning")
