"""`tutor init`  -  interactive setup wizard.

Usage: `uv run tutor init`. Guides the user through:
  1. Verifying prerequisites (uv, playwright chromium)
  2. Collecting preferences into user.config.json
  3. Running Panopto + Blackboard SSO auth flows
  4. Running `tutor doctor` to confirm green
"""
from __future__ import annotations
import subprocess
import sys

from rich import print as rprint
from rich.prompt import Confirm, Prompt

from . import auth as auth_mod
from . import doctor
from .config import UserConfig, USER_CONFIG_PATH, SUBJECTS, SUBJECTS_DIR


def _header(text: str) -> None:
    rprint(f"\n[bold cyan]━━ {text} ━━[/]")


def _ensure_playwright_chromium() -> None:
    rprint("Installing Playwright chromium (required for SSO)…")
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=False,
    )


def _scaffold_subject_dirs() -> None:
    """Create empty subject folders so the web UI has structure to nav."""
    for slug in SUBJECTS:
        for sub in ("chapters", "lectures", "materials", "sheets"):
            (SUBJECTS_DIR / slug / sub).mkdir(parents=True, exist_ok=True)


def _collect_config() -> UserConfig:
    existing = UserConfig.load() if USER_CONFIG_PATH.exists() else UserConfig()
    name = Prompt.ask("Your name", default=existing.name or "Student")
    email = Prompt.ask("Imperial email (optional)", default=existing.email or "")
    hint_style = Prompt.ask(
        "Hint style when working problem sheets",
        choices=["progressive", "on_demand", "none"],
        default=existing.preferences.hint_style,
    )
    teach_mode = Prompt.ask(
        "Default teach-mode depth",
        choices=["full", "brief"],
        default=existing.preferences.teach_mode,
    )

    cfg = UserConfig()
    cfg.name = name
    cfg.email = email
    cfg.preferences.hint_style = hint_style
    cfg.preferences.teach_mode = teach_mode
    cfg.save()
    rprint(f"[green]✓ saved[/] {USER_CONFIG_PATH}")
    return cfg


def run() -> None:
    rprint("[bold]tutor setup wizard[/]. Let's get you studying.\n")

    _header("Prerequisites")
    _ensure_playwright_chromium()
    _scaffold_subject_dirs()

    _header("Preferences")
    _collect_config()

    _header("Authentication")
    rprint("Two headful browser windows will open. Log in with your Imperial account.")
    if Confirm.ask("Log in to Panopto now?", default=True):
        auth_mod.login_panopto()
    if Confirm.ask("Log in to Blackboard now?", default=True):
        auth_mod.login_blackboard()

    _header("Health check")
    ok = doctor.run_all()

    _header("You're set up")
    if ok:
        rprint(
            "[green]All green.[/] In Claude Code, try:\n"
            "  [cyan]/study[/]                     -  see the dashboard.\n"
            "  [cyan]/teach analysis 1[/]          -  learn your first chapter.\n"
            "  [cyan]/practice analysis sheet-1[/]  -  work a problem sheet.\n\n"
            "Or from the shell: [cyan]uv run tutor web[/] opens the reader at "
            f"http://localhost:{UserConfig.load().preferences.web_port}."
        )
    else:
        rprint(
            "[yellow]Setup finished with failing checks.[/] "
            "The table above tells you the exact fix for each red row. "
            "Then run [cyan]uv run tutor doctor[/] again."
        )
