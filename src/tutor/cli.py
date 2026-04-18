"""tutor CLI: fetch lecture material from Panopto/Blackboard, set up folders for catchup."""
from __future__ import annotations
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.table import Table
from rich.console import Console

from . import auth as auth_mod
from . import panopto as pp
from . import blackboard as bb
from . import doctor as doctor_mod
from . import init as init_mod
from . import status as status_mod
from . import course_map as cm
from .config import (
    SUBJECT_SLUGS, SUBJECTS, SUBJECTS_DIR,
    PANOPTO_STATE, BLACKBOARD_STATE,
    UserConfig, USER_CONFIG_PATH,
    TERMS, EXAMS, COURSE_MAP_JSON,
)

app = typer.Typer(help="Imperial lecture catchup helper.", no_args_is_help=True)
auth_app = typer.Typer(help="SSO login flows.")
panopto_app = typer.Typer(help="Panopto operations.")
bb_app = typer.Typer(help="Blackboard operations.")
map_app = typer.Typer(help="Course map: index of lectures, chapters, exam dates.")
app.add_typer(auth_app, name="auth")
app.add_typer(panopto_app, name="panopto")
app.add_typer(bb_app, name="bb")
app.add_typer(map_app, name="map")

console = Console()


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _subject_dir(subject: str) -> Path:
    if subject not in SUBJECT_SLUGS:
        raise typer.BadParameter(f"subject must be one of {SUBJECT_SLUGS}")
    return SUBJECTS_DIR / subject


# ---------- top-level ----------
@app.command("init")
def cmd_init() -> None:
    """Interactive first-time setup. Safe to re-run."""
    init_mod.run()


@app.command("doctor")
def cmd_doctor() -> None:
    """Verify every endpoint + dependency. Exit 1 if anything red."""
    ok = doctor_mod.run_all()
    raise typer.Exit(0 if ok else 1)


@app.command("status")
def cmd_status() -> None:
    """Dashboard: what's done, what's pending, what to do next."""
    status_mod.run()


@app.command("prepare")
def cmd_prepare(
    name: Optional[str] = typer.Option(None, "--name", help="Override auto-detected name."),
    skip_playwright: bool = typer.Option(False, "--skip-playwright", help="Skip chromium install."),
) -> None:
    """Non-interactive prep: install chromium, scaffold dirs, write default user.config.json.

    Safe to re-run. Does NOT overwrite an existing user.config.json.
    """
    # 1. Playwright chromium
    if not skip_playwright:
        print("[cyan]Installing Playwright chromium...[/]")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=False,
        )

    # 2. Subject dirs
    for slug in SUBJECTS:
        for sub in ("chapters", "lectures", "materials", "sheets"):
            (SUBJECTS_DIR / slug / sub).mkdir(parents=True, exist_ok=True)
    print(f"[green]✓[/] scaffolded {len(SUBJECTS)} subject folders under {SUBJECTS_DIR.relative_to(SUBJECTS_DIR.parent)}/")

    # 3. Default config (don't overwrite)
    if USER_CONFIG_PATH.exists():
        print(f"[dim]user.config.json exists, leaving it alone.[/]")
    else:
        resolved_name = name or _detect_git_name() or "Student"
        cfg = UserConfig()
        cfg.name = resolved_name
        cfg.save()
        print(f"[green]✓[/] wrote {USER_CONFIG_PATH.name} (name={resolved_name!r}; edit to customise)")


def _detect_git_name() -> Optional[str]:
    if not shutil.which("git"):
        return None
    try:
        out = subprocess.run(
            ["git", "config", "--get", "user.name"],
            capture_output=True, text=True, check=False, timeout=3,
        )
        val = (out.stdout or "").strip()
        return val or None
    except Exception:
        return None


@app.command("web")
def cmd_web(
    port: Optional[int] = typer.Option(None, "--port"),
    no_open: bool = typer.Option(False, "--no-open", help="Don't auto-open browser."),
) -> None:
    """Serve the local notes/problem-sheet UI at http://localhost:<port>."""
    from . import web as web_mod
    web_mod.run(port=port, open_browser=not no_open)


# ---------- auth ----------
@auth_app.command("panopto")
def cmd_auth_panopto() -> None:
    """Headful login to Panopto via Imperial SSO."""
    auth_mod.login_panopto()


@auth_app.command("blackboard")
def cmd_auth_blackboard() -> None:
    """Headful login to Blackboard via Imperial SSO."""
    auth_mod.login_blackboard()


@auth_app.command("all")
def cmd_auth_all() -> None:
    """Unified Imperial SSO  -  one browser login, cookies for both hosts."""
    auth_mod.login_all()


@auth_app.command("status")
def cmd_auth_status() -> None:
    print(f"panopto cookies: {'[green]yes[/]' if PANOPTO_STATE.exists() else '[red]missing[/]'}  ({PANOPTO_STATE})")
    print(f"blackboard cookies: {'[green]yes[/]' if BLACKBOARD_STATE.exists() else '[red]missing[/]'}  ({BLACKBOARD_STATE})")


# ---------- panopto ----------
@panopto_app.command("folders")
def cmd_pp_folders(
    query: str = typer.Option("*", "--q", help="Search term (folder name substring). '*' = all."),
    parent: Optional[str] = typer.Option(None, help="Parent folder ID or URL; scopes search to its subtree."),
    limit: int = typer.Option(100, "--limit"),
) -> None:
    """Search Panopto folders by name to find a subject's folder ID."""
    pid = pp.parse_folder_id(parent) if parent else None
    folders = pp.search_folders(query=query, parent_id=pid, max_results=limit)
    t = Table("ID", "Name")
    for f in folders:
        t.add_row(f.id, f.name)
    console.print(t)


@panopto_app.command("list")
def cmd_pp_list(folder: str = typer.Argument(..., help="Folder URL, GUID, or subject slug")) -> None:
    """List sessions in a Panopto folder. Accepts a subject slug as a shortcut."""
    if folder in SUBJECT_SLUGS:
        fid = SUBJECTS[folder].panopto_folder
        if not fid:
            raise typer.BadParameter(f"No Panopto folder configured for {folder}")
    else:
        fid = pp.parse_folder_id(folder)
    sessions = pp.list_sessions(fid)
    t = Table("#", "DeliveryID", "Title", "Duration (min)", "Start")
    for i, s in enumerate(sorted(sessions, key=lambda s: s.start_time), start=1):
        t.add_row(str(i), s.delivery_id, s.name, f"{s.duration_s/60:.1f}",
                  s.start_time[:19] if s.start_time else "")
    console.print(t)


@panopto_app.command("fetch")
def cmd_pp_fetch(
    subject: str,
    delivery_id: str,
    number: int = typer.Option(..., "--n", help="Lecture number, e.g. 12"),
    title: str = typer.Option(..., "--title"),
) -> None:
    """Download transcript for one Panopto session into subjects/{subject}/lectures/L{n}/."""
    subj_dir = _subject_dir(subject)
    folder = subj_dir / "lectures" / f"L{number:02d}-{_slug(title)[:40]}"
    folder.mkdir(parents=True, exist_ok=True)

    print(f"[cyan]Fetching transcript[/] -> {folder}")
    srt_path = folder / "transcript.srt"
    pp.download_transcript(delivery_id, srt_path)
    clean = pp.srt_to_text(srt_path.read_text(encoding="utf-8"))
    (folder / "transcript.txt").write_text(clean, encoding="utf-8")

    meta = {
        "subject": subject,
        "number": number,
        "title": title,
        "delivery_id": delivery_id,
        "viewer_url": f"https://imperial.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id={delivery_id}",
    }
    (folder / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"[green]Done[/]. Lecture folder: {folder}")
    print(f"[dim]Next:[/] run the lecturer agent on this folder, then note-taker.")


# ---------- blackboard ----------
@bb_app.command("courses")
def cmd_bb_courses() -> None:
    for c in bb.list_courses():
        print(f"  {c.course_id}  {c.name}  [dim]({c.id})[/]")


@bb_app.command("roots")
def cmd_bb_roots(course_id: str) -> None:
    """Top-level items of a course (entry points for `bb tree`)."""
    for it in bb.list_roots(course_id):
        kind = "[cyan]folder[/]" if it.is_folder else "leaf"
        print(f"  {kind}  {it.content_id}  {it.title}")


@bb_app.command("tree")
def cmd_bb_tree(
    course_id: str,
    content_id: str = typer.Argument(..., help="Start node (get one via `bb roots`)"),
    depth: int = typer.Option(5, "--depth"),
) -> None:
    """Scrape the Learn Original content tree starting at content_id."""
    for trail, item in bb.scrape(course_id, content_id, max_depth=depth):
        indent = "  " * len(trail)
        marker = "[cyan]/[/]" if item.is_folder else (f"[green]({len(item.files)})[/]" if item.files else "-")
        print(f"{indent}{marker} {item.title}  [dim]{item.content_id}[/]")


@bb_app.command("pull")
def cmd_bb_pull(
    subject: str,
    course_id: str,
    content_id: str,
    name: str = typer.Option(..., "--name", help="Subfolder name under subjects/{subject}/materials/"),
    recursive: bool = typer.Option(True, "--recursive/--flat"),
) -> None:
    """Download every file attachment under a Blackboard content item."""
    out = _subject_dir(subject) / "materials" / _slug(name)
    written = bb.download_folder_files(course_id, content_id, out, recursive=recursive)
    print(f"[green]Done[/]  -  {len(written)} files into {out}")
    for p in written[:20]:
        print(f"  ✓ {p.relative_to(_subject_dir(subject))}")
    if len(written) > 20:
        print(f"  ... and {len(written)-20} more")


@bb_app.command("sheets")
def cmd_bb_sheets(
    subject: str,
    resolve: bool = typer.Option(False, "--resolve", help="Rescan homepage to discover the Problem Sheets folder."),
) -> None:
    """Fetch all problem sheets for a subject into subjects/{subject}/sheets/."""
    if subject not in SUBJECT_SLUGS:
        raise typer.BadParameter(f"subject must be one of {SUBJECT_SLUGS}")
    meta = SUBJECTS[subject]
    if not meta.bb_course:
        raise typer.BadParameter(f"No Blackboard course configured for {subject}")

    cid = meta.bb_problem_sheets
    if resolve or not cid:
        # Walk the homepage looking for a folder titled like "Problem Sheet*"
        if not meta.bb_homepage:
            raise typer.BadParameter(
                f"No homepage configured for {subject}. "
                f"Run `tutor bb roots {meta.bb_course}` to find one."
            )
        items = bb.list_classic(meta.bb_course, meta.bb_homepage)
        match = next((i for i in items if i.is_folder and "problem" in i.title.lower()), None)
        if not match:
            print(f"[red]Could not find a Problem Sheets folder[/] under {meta.bb_homepage}.")
            print("Folders on the homepage:")
            for it in items:
                if it.is_folder:
                    print(f"  {it.content_id}  {it.title}")
            raise typer.Exit(1)
        cid = match.content_id
        print(f"[dim]Resolved problem-sheets folder:[/] {cid}  -  {match.title}")

    out = _subject_dir(subject) / "sheets"
    written = bb.download_folder_files(meta.bb_course, cid, out, recursive=True)
    print(f"[green]Done[/]  -  {len(written)} files into {out}")
    for p in written:
        print(f"  ✓ {p.relative_to(_subject_dir(subject))}")


# ---------- map ----------
@map_app.command("build")
def cmd_map_build(
    subject: Optional[str] = typer.Option(
        None, "--subject", "-s",
        help="Build just this subject. Default: all three.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print summary, don't write."),
) -> None:
    """Scrape Panopto + inventory materials, write .claude/knowledge/course-map.{json,md}.

    This is the index agents consult on /teach. Idempotent. Safe to rerun after
    new lectures land or you pull fresh materials with `tutor bb pull`.
    """
    slugs = [subject] if subject else None
    if subject and subject not in SUBJECT_SLUGS:
        raise typer.BadParameter(f"subject must be one of {SUBJECT_SLUGS}")

    print("[cyan]Building course map...[/]")
    course_map = cm.build(subjects=slugs)

    total_l = sum(
        len(tb.lectures)
        for sb in course_map.subjects.values()
        for tb in sb.terms.values()
    )
    print(f"[green]✓[/] indexed {total_l} lectures across "
          f"{len(course_map.subjects)} subject(s).")

    if dry_run:
        print("[dim]--dry-run: no files written.[/]")
        return

    course_map.save()
    print(f"[green]✓[/] wrote {COURSE_MAP_JSON.relative_to(COURSE_MAP_JSON.parents[2])}")


@map_app.command("show")
def cmd_map_show(
    subject: Optional[str] = typer.Argument(None, help="Subject slug (omit = all)."),
    term: Optional[str] = typer.Option(None, "--term", "-t", help="autumn | spring"),
) -> None:
    """Print a condensed view of the course map."""
    course_map = cm.CourseMap.load()
    subs = [subject] if subject else list(course_map.subjects.keys())
    terms = [term] if term else list(TERMS)

    for slug in subs:
        sb = course_map.subjects.get(slug)
        if not sb:
            print(f"[yellow]No entry for {slug}[/]")
            continue
        print(f"\n[bold cyan]{sb.title}[/]  [dim]({sb.code})[/]  -  exam {sb.exam_date or '?'}")
        for t in terms:
            tb = sb.terms.get(t)
            if not tb or not tb.lectures:
                print(f"  [dim]{t}: (no lectures)[/]")
                continue
            print(f"  [bold]{t}[/] ({len(tb.lectures)} lectures)")
            for l in tb.lectures:
                print(f"    L{l.n:02d}  {l.date}  {l.title[:60]}")


@map_app.command("path")
def cmd_map_path() -> None:
    """Print where the course map lives on disk."""
    print(str(COURSE_MAP_JSON))


@app.command("resolve")
def cmd_resolve(
    subject: str = typer.Argument(..., help="analysis | calculus | linear-algebra"),
    ref: str = typer.Argument(..., help="Lecture or chapter ref: L14, 14, ch3, or a Panopto viewer URL."),
    term: Optional[str] = typer.Argument(None, help="autumn | spring (required for L/ch refs)."),
) -> None:
    """Look up a lecture or chapter in the course map. Prints delivery_id + viewer URL.

    Pass a Panopto viewer URL as `ref` to short-circuit the lookup.
    """
    delivery = cm.parse_viewer_url(ref)
    if delivery:
        print(f"[green]delivery_id[/]  {delivery}")
        print(f"[green]viewer_url[/]   https://imperial.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id={delivery}")
        return

    if subject not in SUBJECT_SLUGS:
        raise typer.BadParameter(f"subject must be one of {SUBJECT_SLUGS}")
    if term is None or term not in TERMS:
        raise typer.BadParameter(
            f"term is required (autumn | spring). Each term restarts lecture numbering at 1."
        )

    try:
        kind, n = cm.parse_ref(ref)
    except ValueError as e:
        raise typer.BadParameter(str(e))

    try:
        course_map = cm.CourseMap.load()
    except FileNotFoundError as e:
        raise typer.BadParameter(str(e))

    if kind == "lecture":
        lec = course_map.find_lecture(subject, term, n)
        if not lec:
            available = course_map.lectures(subject, term)
            print(f"[red]No L{n} in {subject}/{term}[/]  -  map has L1..L{len(available)}")
            raise typer.Exit(1)
        print(f"[green]delivery_id[/]  {lec.delivery_id}")
        print(f"[green]viewer_url[/]   {lec.viewer_url}")
        print(f"[green]title[/]        {lec.title}")
        print(f"[green]date[/]         {lec.date}  -  {lec.duration_min:.0f} min")
    else:
        # Chapters are PDF sections. Scan subjects/<slug>/materials/ at query
        # time — map is per-cohort (Panopto only) and doesn't track per-user PDFs.
        pdfs = cm.scan_materials(subject, term=term)
        if not pdfs:
            print(f"[yellow]No PDFs in subjects/{subject}/materials/ for {term}.[/]  "
                  f"Run `uv run tutor bb pull` to fetch them first.")
            raise typer.Exit(1)
        for p in pdfs:
            rel = p.relative_to(Path.cwd()) if p.is_absolute() else p
            print(f"  {rel}")
        print(f"[dim]Chapter boundaries live inside the PDFs.[/] "
              f"Open the PDF, find chapter {n} via bookmarks/TOC, feed pages to lecturer.")


@app.command("exams")
def cmd_exams() -> None:
    """Days-until countdown for each subject's final exam."""
    t = Table("Subject", "Date", "Days until", title="Exams")
    for slug, d, days in cm.exam_countdown():
        meta = SUBJECTS[slug]
        if days < 0:
            cell = f"[dim]{abs(days)}d ago[/]"
        elif days == 0:
            cell = "[bold red]TODAY[/]"
        elif days <= 7:
            cell = f"[bold red]{days}d[/]"
        elif days <= 14:
            cell = f"[yellow]{days}d[/]"
        else:
            cell = f"[green]{days}d[/]"
        t.add_row(f"{meta.title}\n[dim]{meta.code}[/]", d.isoformat(), cell)
    console.print(t)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
