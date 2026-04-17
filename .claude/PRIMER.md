# `uni` — Imperial Catchup System

Personal tool for catching up on missed lectures. Finals 2026-04-27 → 2026-05-08.

## What this does

For a given lecture:
1. **Fetch** transcript (Panopto) + slides (Blackboard) via saved SSO cookies.
2. **Teach** — an Opus subagent reconstructs the lecture as rigorous Imperial-grade teaching material (`teach.md`).
3. **Note** — a Sonnet subagent distills teach output into dense revision notes (`notes.md`).

Target: compress 1hr of lecture into ~15min of active reading.

## Architecture

- `src/uni/auth.py` — Playwright headful SSO once, persists `auth_state/{panopto,blackboard}.json`.
- `src/uni/panopto.py` — `httpx` against `Data.svc/GetSessions`, `GenerateSRT.ashx`. No OAuth.
- `src/uni/blackboard.py` — `httpx` against `/learn/api/public/v1/*`. No OAuth.
- `src/uni/cli.py` — Typer CLI: `uni auth`, `uni panopto`, `uni bb`.
- `.claude/agents/{lecturer,note-taker}.md` — subagent defs with the full teach/notes contracts inline.
- `subjects/{analysis,calculus,linear-algebra}/` — per-subject workspaces.

## Typical workflow

```
# 1. One-time (or when cookies expire)
uv run uni auth all

# 2. Discover a Panopto folder for the subject
uv run uni panopto folders                     # root folders
uv run uni panopto list "<folder-url-or-id>"   # sessions in it

# 3. Fetch a specific lecture
uv run uni panopto fetch analysis <deliveryId> --n 12 --title "Uniform continuity"

# 4. In Claude Code, in this repo:
#    > Run lecturer on subjects/analysis/lectures/L12-*
#    > Then note-taker on the same folder
```

## Conventions

- Lecture folder: `subjects/{subject}/lectures/L{NN}-{slug}/`
  - `transcript.srt`, `transcript.txt`, `meta.json`, `slides.pdf` (opt), `teach.md`, `notes.md`.
- `subjects/{subject}/last-done.md` — append-only log, updated by note-taker.
- Never commit `auth_state/` or lecture material (personal, gitignored).

## Auth freshness

Imperial SSO cookies typically last weeks but can expire mid-session. If an `httpx` call 302s to login, run `uv run uni auth panopto` (or `blackboard`) again.

## Known IDs

**Always read `.claude/knowledge/known-ids.md` before scraping.** It has the Panopto folder GUIDs + Blackboard course IDs for all three subjects — don't re-run `uni panopto folders` or `uni bb courses` unless IDs look stale.

## MCP

- `notion-query` (http, worker URL in `.mcp.json`) — use this to read the missed-lectures / missed-problem-sheets queue from Notion.

## Known unknowns

- Caption availability varies per lecture — older sessions may have no transcript; the client raises a clear error if the SRT body is empty.
- OAuth client registration (both platforms) is a future option if scraping breaks.
