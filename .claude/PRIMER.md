# tutor  -  Claude's primer

Imperial JMC Year 1 catchup system. Claude, read this first.

## What this repo does

Pulls lecture transcripts (Panopto) + course materials (Blackboard), runs two
subagents per lecture or chapter  -  `lecturer` (Opus, rigorous teach-mode) and
`note-taker` (Sonnet, dense revision notes)  -  and serves the result as a local
web UI with problem-sheet practice mode.

Goal: compress 60 min of lecture into 15 min of active reading, then reinforce
via problem sheets.

## Architecture (at a glance)

| Layer            | Where                              | Purpose                                              |
|------------------|------------------------------------|------------------------------------------------------|
| Auth             | `src/tutor/auth.py`                  | Playwright headful SSO once; `auth_state/*.json`.    |
| Panopto client   | `src/tutor/panopto.py`               | `httpx` against `Data.svc` + `GenerateSRT.ashx`.     |
| Blackboard       | `src/tutor/blackboard.py`            | `httpx` against REST + `listContent.jsp` scraping.   |
| Shared constants | `src/tutor/shared.py`                | JMC-common Panopto GUIDs + BB course IDs.            |
| Runtime config   | `src/tutor/config.py`                | Loads shared + per-user `user.config.json`.          |
| CLI              | `src/tutor/cli.py`                   | Typer entrypoint: `uv run tutor …`.                    |
| Doctor           | `src/tutor/doctor.py`                | Full endpoint + deps health check.                   |
| Init wizard      | `src/tutor/init.py`                  | `uv run tutor init`.                                   |
| Web UI           | `src/tutor/web.py` + `webui/`        | FastAPI at localhost, notes + problem-sheet viewer.  |
| Problems         | `src/tutor/problems.py`              | Problem-sheet extraction + progress tracking.        |
| Agents           | `.claude/agents/*.md`              | `lecturer`, `note-taker`, `problem-solver`.          |
| Slash commands   | `.claude/commands/*.md`            | `/setup`, `/doctor`, `/teach`, `/practice`, …        |
| Knowledge        | `.claude/knowledge/*.md`           | JMC-common IDs + course context (no personal data).  |

## Personal vs shared

**Shared (committed, same for every JMC Y1):** Panopto folder GUIDs, BB course
IDs, Learn Original content IDs under the Analysis course. All in
`src/tutor/shared.py` and `.claude/knowledge/known-ids.md`.

**Per-user (never committed):** `user.config.json` (name, preferences),
`auth_state/*.json` (SSO cookies), `subjects/*/lectures`, `subjects/*/chapters`,
`subjects/*/materials`, `subjects/*/sheets`, `.claude/knowledge/lecture-map.json`.
All gitignored.

## Typical usage

```bash
uv run tutor init                          # first time only
uv run tutor doctor                        # verify everything works
uv run tutor panopto list analysis         # list all Analysis sessions
uv run tutor panopto fetch analysis <id> --n 14 --title "MVT"
uv run tutor bb sheets analysis --resolve  # grab every problem sheet
uv run tutor web                           # open the local reader
```

In Claude Code:

```
/teach analysis 14         # fetch if missing, then lecturer + note-taker
/practice analysis sheet-3 # start problem-by-problem walkthrough
/hint                      # next hint level on current problem
/check                     # submit your attempt for feedback
```

## Conventions

- **Lecture folder:** `subjects/<subject>/lectures/L{NN}-{slug}/` with
  `transcript.srt`, `transcript.txt`, `meta.json`, optionally `slides.pdf`,
  then `teach.md` + `notes.md` after agents run.
- **Chapter folder:** `subjects/<subject>/chapters/ch{NN}-{slug}/`  -  same
  pair of outputs, sourced from PDF instead of transcript.
- **Problem sheet:** `subjects/<subject>/sheets/<sheet-slug>/` with the PDF,
  `problems/qNN.md` per question, `.progress.json` tracking state.

## Auth freshness

Imperial SSO cookies last weeks but can expire mid-session. Symptom: `tutor
doctor` shows HTTP 401. Fix: `uv run tutor auth <panopto|blackboard>`.

## When things break

Always run `uv run tutor doctor` first. Each failing check tells you the exact
next command. If the BB HTML parser returns 0 items on a known homepage,
Blackboard has likely redesigned  -  check `blackboard.py:_parse_folder_page`
against a fresh page dump.
