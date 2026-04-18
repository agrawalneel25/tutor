"""Problem-sheet progress tracking and PDF text extraction.

Heavy lifting (segmenting the PDF into questions, generating hints + solutions)
is delegated to the `problem-solver` agent. This module just provides the
filesystem layout helpers and lightweight progress state.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import SUBJECTS_DIR, SUBJECT_SLUGS


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class QuestionState:
    status: str = "pending"  # pending | in_progress | done | skipped
    hints_shown: int = 0
    attempts: int = 0
    correct: Optional[bool] = None
    last_attempt: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class SheetProgress:
    current: Optional[str] = None
    questions: dict[str, QuestionState] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "SheetProgress":
        if not path.exists():
            return cls()
        raw = json.loads(path.read_text())
        qs = {k: QuestionState(**v) for k, v in (raw.get("questions") or {}).items()}
        return cls(current=raw.get("current"), questions=qs)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = {
            "current": self.current,
            "questions": {k: asdict(v) for k, v in self.questions.items()},
        }
        path.write_text(json.dumps(raw, indent=2))

    def get(self, qid: str) -> QuestionState:
        if qid not in self.questions:
            self.questions[qid] = QuestionState()
        return self.questions[qid]

    def touch(self, qid: str, **kwargs) -> QuestionState:
        s = self.get(qid)
        for k, v in kwargs.items():
            setattr(s, k, v)
        s.updated_at = _now()
        return s


def sheet_dir(subject: str, sheet_slug: str) -> Path:
    if subject not in SUBJECT_SLUGS:
        raise ValueError(f"unknown subject {subject!r}")
    return SUBJECTS_DIR / subject / "sheets" / sheet_slug


def list_sheets(subject: str) -> list[Path]:
    root = SUBJECTS_DIR / subject / "sheets"
    if not root.exists():
        return []
    return sorted([p for p in root.iterdir() if p.is_dir()])


def progress_path(subject: str, sheet_slug: str) -> Path:
    return sheet_dir(subject, sheet_slug) / ".progress.json"


def pdf_to_text(pdf_path: Path) -> str:
    """Extract raw text from a PDF. Good enough for problem sheet segmentation
    by an LLM; imperfect for maths formulas  -  fall back to visual reading of
    the PDF for the actual problem statements."""
    from pypdf import PdfReader
    reader = PdfReader(str(pdf_path))
    chunks: list[str] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        chunks.append(f"\n\n--- page {i} ---\n\n{text}")
    return "\n".join(chunks)
