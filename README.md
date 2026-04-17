# uni

Imperial lecture catchup system. Pull transcripts from Panopto + slides from Blackboard, then run two Claude subagents over them: `lecturer` (teach-mode) and `note-taker` (dense revision notes).

## Setup

```bash
uv sync
uv run playwright install chromium
uv run uni auth all          # one-time headful SSO login to Panopto + Blackboard
```

## Fetch a lecture

```bash
# find the Panopto folder GUID for your subject (shown in URL when browsing)
uv run uni panopto folders
uv run uni panopto list "https://imperial.cloud.panopto.eu/Panopto/Pages/Sessions/List.aspx?folderID=<GUID>"

# download transcript into subjects/analysis/lectures/L12-.../
uv run uni panopto fetch analysis <deliveryId> --n 12 --title "Uniform continuity"
```

## Teach + notes

Open this repo in Claude Code and ask:

> Run `lecturer` on `subjects/analysis/lectures/L12-uniform-continuity`, then `note-taker` on the same folder.

Outputs: `teach.md`, `notes.md` in the lecture folder. `last-done.md` updated automatically.

## Blackboard

```bash
uv run uni bb courses                           # list enrolled courses
uv run uni bb tree <courseId>                   # inspect content tree
uv run uni bb pull analysis <courseId> <contentId> --name week-5-slides
```

## Design

See `.claude/PRIMER.md`.
