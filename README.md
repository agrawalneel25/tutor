# tutor

A Claude Code study app for Imperial JMC Year 1. One command, one Imperial login, then you're in exam prep mode: transcripts, rigorous teach notes, dense revision summaries, and a problem-sheet walkthrough.

> Based on [advitrocks9/tutor](https://github.com/advitrocks9/tutor) by [@advitrocks9](https://github.com/advitrocks9).

## One-line install

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/advitrocks9/tutor/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/advitrocks9/tutor/main/install.ps1 | iex
```

The installer sets up uv, Node, git, and Claude Code if missing, clones the repo, then launches Claude Code straight into `/setup`. After that you log into Imperial once in a browser and Claude drives the rest.

## Manual install (if you already have `uv` + `claude`)

```bash
git clone https://github.com/advitrocks9/tutor.git
cd tutor
claude --dangerously-skip-permissions
```
Then type `/setup` inside Claude Code.

## What you get

- **Course map** (committed) — every Panopto lecture, per subject per term, with delivery IDs and dates. No scraping needed on first run.
- **Term-aware `/teach`** — lectures restart at 1 each term, so `/teach analysis L3 autumn` and `/teach analysis L3 spring` are different recordings. Agent clarifies term if you don't say.
- **Exam countdown** — `/study` shows days-until for Linear Algebra (29 Apr), Analysis (5 May), Calculus (6 May) and picks the most valuable next action.
- **Problem sheet walkthrough** — `/practice analysis sheet-3`, hint ladder, check your attempts.
- **Local web reader** — `uv run tutor web` renders everything with KaTeX math and a progress tracker.
- **Scientia/CATE search** — `uv run tutor scientia discover`, `set-root`, `index`, `search` for local document-library exports.
- **Cache-first archive pulls** — `tutor bb pull` writes a local manifest beside the download so reruns skip files already fetched.

## Slash commands

| Command    | Use                                                        |
|------------|------------------------------------------------------------|
| `/setup`   | First-time setup  -  fully autonomous                       |
| `/doctor`  | Health check every endpoint + dependency                    |
| `/study`   | Dashboard, exam countdown, one next action                 |
| `/teach`   | `/teach <subject> <L{n}|ch{n}> <autumn|spring>`             |
| `/practice`| `/practice <subject> <sheet-slug>`                         |
| `/hint`    | Next hint on the active problem                            |
| `/check`   | `/check <attempt>` — mark against the canonical solution    |
| `/skip`    | Skip current problem, advance                              |
| `/map`     | `/map <build|show|refresh|path>`                            |

## Scope

Built for MATH40002 (Analysis), MATH40004 (Calculus), MATH40012 (Linear Algebra & Groups) in the Imperial JMC Year 1 2025/26 cohort. Panopto GUIDs and Blackboard course IDs are the same for every student — they're checked into `src/tutor/shared.py`. CS modules (COMP400xx) are out of scope because those materials live on CATE, not Blackboard.

## Privacy

Your Imperial SSO cookies live in `auth_state/` (gitignored). Your preferences in `user.config.json` are gitignored. All fetched lectures, notes, and sheets under `subjects/` are gitignored. Nothing personal leaves your machine.

## Fast workflow

- Keep startup cheap: load local notes, the course map, and cached indexes only.
- Use `tutor auth blackboard` or `tutor auth exams` only when cookies expire or you need a fresh pull.
- Use `tutor bb pull` and `tutor papers fetch` as explicit refresh commands, not as part of startup.
- If a Blackboard pull is interrupted, rerun it; the local manifest skips files that are already on disk.
