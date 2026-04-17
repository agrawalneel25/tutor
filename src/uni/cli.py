"""uni CLI — fetch lecture material from Panopto/Blackboard, set up folders for catchup."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.table import Table
from rich.console import Console

from . import auth as auth_mod
from . import panopto as pp
from . import blackboard as bb
from .config import SUBJECTS, SUBJECTS_DIR, PANOPTO_STATE, BLACKBOARD_STATE

app = typer.Typer(help="Imperial lecture catchup helper.", no_args_is_help=True)
auth_app = typer.Typer(help="SSO login flows.")
panopto_app = typer.Typer(help="Panopto operations.")
bb_app = typer.Typer(help="Blackboard operations.")
app.add_typer(auth_app, name="auth")
app.add_typer(panopto_app, name="panopto")
app.add_typer(bb_app, name="bb")

console = Console()


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _subject_dir(subject: str) -> Path:
    if subject not in SUBJECTS:
        raise typer.BadParameter(f"subject must be one of {SUBJECTS}")
    return SUBJECTS_DIR / subject


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
    auth_mod.login_panopto()
    auth_mod.login_blackboard()


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
def cmd_pp_list(folder: str = typer.Argument(..., help="Folder URL or GUID")) -> None:
    """List sessions in a Panopto folder."""
    fid = pp.parse_folder_id(folder)
    sessions = pp.list_sessions(fid)
    t = Table("DeliveryID", "Title", "Duration (min)", "Start")
    for s in sessions:
        t.add_row(s.delivery_id, s.name, f"{s.duration_s/60:.1f}", s.start_time[:19] if s.start_time else "")
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
    print(f"[green]Done[/] — {len(written)} files into {out}")
    for p in written[:20]:
        print(f"  ✓ {p.relative_to(_subject_dir(subject))}")
    if len(written) > 20:
        print(f"  ... and {len(written)-20} more")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
