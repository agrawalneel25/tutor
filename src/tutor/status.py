"""`tutor status`  -  dashboard showing what's done, what's pending, what to do next."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich import box

from .config import SUBJECTS, SUBJECTS_DIR, USER
from .problems import SheetProgress


console = Console()


def _count(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))


def _sheet_stats(sheet_dir: Path) -> tuple[int, int, int]:
    """Return (total, done, pending) for a sheet."""
    problems = sheet_dir / "problems"
    total = _count(problems, "q*.md")
    prog = SheetProgress.load(sheet_dir / ".progress.json")
    done = sum(1 for s in prog.questions.values() if s.status == "done")
    pending = total - done - sum(1 for s in prog.questions.values() if s.status == "skipped")
    return total, done, max(0, pending)


def _most_recent(root: Path) -> Optional[tuple[Path, float]]:
    """Find the most recently modified teach/notes/progress file under root."""
    if not root.exists():
        return None
    best: Optional[tuple[Path, float]] = None
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.name not in {"teach.md", "notes.md", ".progress.json"}:
            continue
        mtime = p.stat().st_mtime
        if best is None or mtime > best[1]:
            best = (p, mtime)
    return best


def _suggest_next(subject_stats: dict) -> str:
    """Simple heuristic. Extend later."""
    # 1. Prioritise resuming an in-progress sheet.
    for slug, s in subject_stats.items():
        for sh in s["sheets"]:
            if sh["pending"] > 0 and sh["current"]:
                return f"/practice {slug} {sh['slug']}   (resume  -  {sh['pending']} questions left)"

    # 2. Empty subjects: start chapter 1.
    empty = [slug for slug, s in subject_stats.items() if s["chapters"] == 0 and s["lectures"] == 0]
    if empty:
        return f"/teach {empty[0]} 1   ({empty[0]} is empty  -  start with chapter 1)"

    # 3. Fewest-coverage subject: next chapter.
    weakest = min(subject_stats.items(), key=lambda kv: kv[1]["chapters"])
    slug = weakest[0]
    next_ch = weakest[1]["chapters"] + 1
    return f"/teach {slug} {next_ch}   (weakest coverage  -  continue with chapter {next_ch})"


def run() -> None:
    greeting = f"Hi, {USER.name}" if USER.name != "Student" else "Hi"
    console.rule(f"[bold]tutor | {greeting}[/]", align="left", style="cyan")

    subject_stats: dict[str, dict] = {}
    for slug, meta in SUBJECTS.items():
        root = SUBJECTS_DIR / slug
        chapters = _count(root / "chapters", "ch*-*/teach.md")
        lectures = _count(root / "lectures", "L*-*/teach.md")
        sheet_dirs = sorted([p for p in (root / "sheets").iterdir() if p.is_dir()]) if (root / "sheets").exists() else []
        sheets = []
        for sd in sheet_dirs:
            total, done, pending = _sheet_stats(sd)
            prog = SheetProgress.load(sd / ".progress.json")
            sheets.append({
                "slug": sd.name, "total": total, "done": done, "pending": pending,
                "current": prog.current,
            })
        subject_stats[slug] = {
            "meta": meta, "chapters": chapters, "lectures": lectures, "sheets": sheets,
        }

    t = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold", title_style="")
    t.add_column("Subject", style="")
    t.add_column("Chapters", justify="right", style="cyan")
    t.add_column("Lectures", justify="right", style="cyan")
    t.add_column("Sheets", justify="right", style="cyan")
    t.add_column("Recent", style="dim")

    for slug, s in subject_stats.items():
        recent = _most_recent(SUBJECTS_DIR / slug)
        if recent:
            age_s = datetime.now(timezone.utc).timestamp() - recent[1]
            age = _humanize_age(age_s)
            recent_str = f"{recent[0].parent.name} · {age}"
        else:
            recent_str = " - "
        sheets_str = (
            f"{sum(x['done'] for x in s['sheets'])}/{sum(x['total'] for x in s['sheets'])} qs across {len(s['sheets'])} sheet(s)"
            if s['sheets'] else " - "
        )
        t.add_row(
            f"{s['meta'].title}\n[dim]{s['meta'].code}[/]",
            str(s['chapters']) if s['chapters'] else " - ",
            str(s['lectures']) if s['lectures'] else " - ",
            sheets_str,
            recent_str,
        )
    console.print(t)

    suggestion = _suggest_next(subject_stats)
    console.print(f"\n[bold]Next:[/] [cyan]{suggestion}[/]")


def _humanize_age(seconds: float) -> str:
    if seconds < 90:
        return f"{int(seconds)}s ago"
    if seconds < 3600 * 2:
        return f"{int(seconds / 60)}m ago"
    if seconds < 86400 * 2:
        return f"{int(seconds / 3600)}h ago"
    return f"{int(seconds / 86400)}d ago"
