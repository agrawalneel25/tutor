"""Course map: the single structured index of what's where for this academic year.

Purpose
-------
The agent needs to answer fast, deterministic questions like:

  "L3 of spring Analysis — which Panopto recording?"
  "How many days until the Calculus exam?"

Scraping Panopto for every `/teach` is wasteful. This module builds the
answers once, writes them to `.claude/knowledge/course-map.json` and a
markdown mirror, and lets everything else read from disk.

The map is **committed to the repo**. Panopto `delivery_id`s, session titles,
and dates are identical for every Imperial JMC Y1 2025-26 student, so shipping
the map means new users get it for free on `git clone` — no SSO scrape needed
until they want a refresh.

Per-user material PDFs are NOT in the map. They live under
`subjects/<slug>/materials/` and agents scan that directory at query time
(it's a handful of files — scanning is instant).

The map is NOT prescriptive. Agents can still call `tutor panopto list ...`
if the user wants a live list — the map is a shortcut, not a wall.

Shape
-----
    {
      "academic_year": "2025-26",
      "generated_at": "2026-04-18T...",
      "exams": {"linear-algebra": "2026-04-29", ...},
      "subjects": {
        "analysis": {
          "code": "MATH40002",
          "title": "Analysis 1",
          "terms": {
            "autumn": {
              "lectures": [
                {"n": 1, "title": "...", "date": "2025-10-06",
                 "delivery_id": "...", "viewer_url": "...",
                 "duration_min": 60.1},
                ...
              ]
            },
            "spring": {...}
          }
        },
        ...
      }
    }

`n` is 1-indexed per term (L1, L2, ... restarts each term). This matches how
the PDF notes are numbered and how students refer to lectures.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from .config import (
    ACADEMIC_YEAR,
    ACADEMIC_YEAR_START,
    TERM_DATES,
    TERMS,
    EXAMS,
    SUBJECTS,
    SUBJECTS_DIR,
    REPO,
    COURSE_MAP_JSON,
    COURSE_MAP_MD,
    KNOWLEDGE_DIR,
    PANOPTO_HOST,
)
from . import panopto as pp


# ---------- data model ----------

@dataclass
class Lecture:
    n: int                    # 1-indexed within term
    title: str
    date: str                 # ISO YYYY-MM-DD
    delivery_id: str
    viewer_url: str
    duration_min: float


@dataclass
class TermBucket:
    lectures: list[Lecture] = field(default_factory=list)


@dataclass
class SubjectBucket:
    code: str
    title: str
    exam_date: Optional[str] = None
    terms: dict[str, TermBucket] = field(default_factory=dict)


@dataclass
class CourseMap:
    academic_year: str
    generated_at: str
    exams: dict[str, str]
    subjects: dict[str, SubjectBucket]

    # ----- io -----

    def to_dict(self) -> dict[str, Any]:
        return {
            "academic_year": self.academic_year,
            "generated_at": self.generated_at,
            "exams": self.exams,
            "subjects": {
                slug: {
                    "code": sb.code,
                    "title": sb.title,
                    "exam_date": sb.exam_date,
                    "terms": {
                        term: {"lectures": [asdict(l) for l in tb.lectures]}
                        for term, tb in sb.terms.items()
                    },
                }
                for slug, sb in self.subjects.items()
            },
        }

    def save(self, json_path: Path = COURSE_MAP_JSON, md_path: Path = COURSE_MAP_MD) -> None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(self.to_dict(), indent=2))
        md_path.write_text(self.render_markdown())

    @classmethod
    def load(cls, path: Path = COURSE_MAP_JSON) -> "CourseMap":
        if not path.exists():
            raise FileNotFoundError(
                f"No course map at {path}. Run `uv run tutor map build` first."
            )
        raw = json.loads(path.read_text())
        subjects: dict[str, SubjectBucket] = {}
        for slug, sraw in raw.get("subjects", {}).items():
            terms = {
                term: TermBucket(
                    lectures=[Lecture(**l) for l in tb.get("lectures", [])],
                )
                for term, tb in sraw.get("terms", {}).items()
            }
            subjects[slug] = SubjectBucket(
                code=sraw["code"],
                title=sraw["title"],
                exam_date=sraw.get("exam_date"),
                terms=terms,
            )
        return cls(
            academic_year=raw.get("academic_year", ACADEMIC_YEAR),
            generated_at=raw.get("generated_at", ""),
            exams=raw.get("exams", {}),
            subjects=subjects,
        )

    # ----- lookup -----

    def lectures(self, subject: str, term: str) -> list[Lecture]:
        sb = self.subjects.get(subject)
        if not sb:
            return []
        return sb.terms.get(term, TermBucket()).lectures

    def find_lecture(self, subject: str, term: str, n: int) -> Optional[Lecture]:
        for l in self.lectures(subject, term):
            if l.n == n:
                return l
        return None

    # ----- markdown mirror -----

    def render_markdown(self) -> str:
        lines: list[str] = []
        lines.append(f"# Course map  -  {self.academic_year}")
        lines.append("")
        lines.append(f"_Generated {self.generated_at}._ This file is a human-readable "
                     f"mirror of `course-map.json`. Agents: prefer the JSON for lookups, "
                     f"this markdown for narrative browsing.")
        lines.append("")
        lines.append("## Exams")
        lines.append("")
        for slug, d in self.exams.items():
            sb = self.subjects.get(slug)
            title = sb.title if sb else slug
            lines.append(f"- **{title}** ({slug})  -  {d}")
        lines.append("")

        for slug, sb in self.subjects.items():
            lines.append(f"## {sb.title}  -  `{slug}`  ({sb.code})")
            if sb.exam_date:
                lines.append(f"Exam: **{sb.exam_date}**")
            lines.append("")
            for term in TERMS:
                tb = sb.terms.get(term)
                if not tb:
                    continue
                lines.append(f"### {term.capitalize()} term")
                lines.append("")
                if tb.lectures:
                    lines.append(f"**Lectures ({len(tb.lectures)}):**")
                    lines.append("")
                    lines.append("| # | Date | Title | Panopto |")
                    lines.append("|---|------|-------|---------|")
                    for l in tb.lectures:
                        short_title = l.title.replace("|", "\\|")[:70]
                        lines.append(
                            f"| L{l.n:02d} | {l.date} | {short_title} | "
                            f"[{l.delivery_id[:8]}…]({l.viewer_url}) |"
                        )
                    lines.append("")
            lines.append("")
        lines.append("---")
        lines.append("Material PDFs (chapter notes, reference sheets) live under "
                     "`subjects/<slug>/materials/` and are NOT in this map  -  they're "
                     "per-user. Agents scan that directory at query time.")
        return "\n".join(lines)


# ---------- building ----------

def _iso_to_date(iso: str) -> Optional[date]:
    """Parse '2025-10-06T09:00:00+00:00' → date(2025, 10, 6). Tolerant of missing TZ."""
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
    except ValueError:
        # Fallback: first 10 chars look like YYYY-MM-DD
        m = re.match(r"(\d{4}-\d{2}-\d{2})", iso)
        if m:
            try:
                return date.fromisoformat(m.group(1))
            except ValueError:
                return None
    return None


def _bucket_term(d: date) -> Optional[str]:
    """Return 'autumn' or 'spring' for a session date, or None if outside term."""
    for term, (start, end) in TERM_DATES.items():
        # Generous: include a week on either side for make-ups / intro week.
        pad = 7
        if (d - start).days >= -pad and (end - d).days >= -pad:
            return term
    # Fallback: anything before Jan 1 2026 in current academic year = autumn,
    # anything after = spring. Keeps stragglers reachable.
    if d < date(2026, 1, 1):
        return "autumn"
    return "spring"


def _collect_panopto(subject_slug: str) -> dict[str, list[Lecture]]:
    """Fetch sessions for a subject's folder, filter to this academic year,
    bucket by term, number 1..N within each term chronologically."""
    meta = SUBJECTS[subject_slug]
    if not meta.panopto_folder:
        return {}

    try:
        sessions = pp.list_sessions(meta.panopto_folder, max_results=500)
    except Exception as e:
        raise RuntimeError(f"Panopto fetch failed for {subject_slug}: {e}") from e

    buckets: dict[str, list[pp.Session]] = {"autumn": [], "spring": []}
    for s in sessions:
        d = _iso_to_date(s.start_time)
        if d is None or d < ACADEMIC_YEAR_START:
            continue
        term = _bucket_term(d)
        if term in buckets:
            buckets[term].append(s)

    out: dict[str, list[Lecture]] = {}
    for term, sess in buckets.items():
        sess.sort(key=lambda s: s.start_time)
        lectures = []
        for n, s in enumerate(sess, start=1):
            d = _iso_to_date(s.start_time)
            lectures.append(Lecture(
                n=n,
                title=s.name,
                date=d.isoformat() if d else "",
                delivery_id=s.delivery_id,
                viewer_url=s.viewer_url,
                duration_min=round(s.duration_s / 60.0, 1),
            ))
        out[term] = lectures
    return out


def scan_materials(subject_slug: str, term: Optional[str] = None) -> list[Path]:
    """Runtime inventory of per-user PDFs under subjects/<slug>/materials/.

    Optionally filters by term using filename heuristics
    ('autumn'/'spring'/'t1'/'t2' anywhere in the path).

    Kept out of the committed course map so the map stays cohort-shareable.
    """
    root = SUBJECTS_DIR / subject_slug / "materials"
    if not root.exists():
        return []

    pdfs = sorted(root.rglob("*.pdf"))
    if term is None:
        return pdfs

    hints = {
        "autumn": ("autumn", "t1", "term1", "term-1", "fall"),
        "spring": ("spring", "t2", "term2", "term-2"),
    }[term]
    term_matched = [p for p in pdfs if any(h in str(p).lower() for h in hints)]
    if term_matched:
        return term_matched
    # No filename hints: return all and let the agent pick.
    return pdfs


def build(subjects: Optional[Iterable[str]] = None) -> CourseMap:
    """Scrape Panopto for the configured subjects, return a fresh CourseMap.

    Output is cohort-shareable (no per-user paths). Writes nothing; caller
    should .save() when ready.
    """
    subject_slugs = list(subjects) if subjects else list(SUBJECTS.keys())
    subject_buckets: dict[str, SubjectBucket] = {}
    for slug in subject_slugs:
        meta = SUBJECTS[slug]
        exam_d = EXAMS.get(slug)
        subject_buckets[slug] = SubjectBucket(
            code=meta.code,
            title=meta.title,
            exam_date=exam_d.isoformat() if exam_d else None,
            terms={},
        )

    # Panopto: one network pass per subject
    for slug in subject_slugs:
        lectures_by_term = _collect_panopto(slug)
        for term in TERMS:
            subject_buckets[slug].terms[term] = TermBucket(
                lectures=lectures_by_term.get(term, []),
            )

    return CourseMap(
        academic_year=ACADEMIC_YEAR,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        exams={k: v.isoformat() for k, v in EXAMS.items()},
        subjects=subject_buckets,
    )


# ---------- resolution ----------

_LECTURE_REF = re.compile(r"^(?:l|lec|lecture)?\s*(\d{1,3})$", re.I)
_CHAPTER_REF = re.compile(r"^(?:c|ch|chapter)\s*(\d{1,3})$", re.I)


def parse_ref(ref: str) -> tuple[str, int]:
    """Parse '14', 'L14', 'ch3', 'chapter 2' into (kind, n). kind ∈ {'lecture','chapter'}."""
    r = ref.strip()
    m = _CHAPTER_REF.match(r)
    if m:
        return "chapter", int(m.group(1))
    m = _LECTURE_REF.match(r)
    if m:
        return "lecture", int(m.group(1))
    raise ValueError(
        f"Can't parse reference {ref!r}. Examples: '14', 'L14', 'ch3'."
    )


def parse_viewer_url(url_or_id: str) -> Optional[str]:
    """Extract a Panopto delivery_id from a viewer URL, or return the string
    itself if it's already a GUID."""
    s = url_or_id.strip()
    if re.fullmatch(r"[0-9a-fA-F-]{36}", s):
        return s
    m = re.search(r"id=([0-9a-fA-F-]{36})", s)
    return m.group(1) if m else None


def exam_countdown(today: Optional[date] = None) -> list[tuple[str, date, int]]:
    """Return [(subject_slug, exam_date, days_until), ...] sorted soonest first.
    Negative days_until means the exam has passed."""
    today = today or date.today()
    rows = [(slug, d, (d - today).days) for slug, d in EXAMS.items()]
    rows.sort(key=lambda r: r[1])
    return rows
