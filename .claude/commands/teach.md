---
description: Teach a lecture or chapter. Term-aware. Usage - /teach <subject> <L14|ch3> <autumn|spring>.
---

The user ran `/teach $ARGUMENTS`. **This is exam-prep mode.** Every module's lectures and chapters restart numbering each term, so `L3 autumn` and `L3 spring` are different recordings. Never assume a term.

## Parse

- **Subject**: `analysis`, `calculus`, or `linear-algebra`.
- **Reference**: `L{n}` or plain `{n}` (lecture), or `ch{n}` (chapter). Also accepted: a full Panopto viewer URL — use it directly, skip resolution.
- **Term**: `autumn` or `spring` (required unless the ref is a Panopto URL).

If the user did not give a term, **ask once**: *"Autumn or spring term?"* Then proceed. Don't guess.

If the user gave a Panopto link instead of a lecture number, extract the `id=<guid>` and use it as `delivery_id` — skip the map lookup entirely.

## Resolve

1. Ensure the course map exists: `ls .claude/knowledge/course-map.json`. If missing, run `uv run tutor map build` first (one-off, ~10s per subject).
2. Call `uv run tutor resolve <subject> <ref> <term>`. It prints `delivery_id`, `viewer_url`, `title`, and `date` for lectures; the matching PDF path(s) for chapters.
3. If the map has no L{n} for that subject/term, **tell the user the range you do have** (e.g. "map has L1..L14 in autumn") and ask whether they want to rebuild (`/map refresh`) or provide a Panopto link directly.

## Teach

**For a lecture:**
- Check `subjects/<subject>/lectures/L{n:02d}-*/` — if the folder exists with `transcript.txt`, skip fetching.
- Else run `uv run tutor panopto fetch <subject> <delivery_id> --n <n> --title "<title>"`. This creates the folder and writes `transcript.srt`, `transcript.txt`, `meta.json`.
- Launch the `lecturer` agent (Task tool, subagent_type: lecturer) pointed at the lecture folder. It produces `teach.md`.
- Launch the `note-taker` agent on the same folder. It produces `notes.md`.

**For a chapter:**
- Look under `subjects/<subject>/materials/` for a PDF matching the term (filenames often contain `autumn`/`spring`/`t1`/`t2`).
- The map entry lists candidates. If more than one matches, **ask the user which PDF**.
- Create `subjects/<subject>/chapters/ch{n:02d}-<slug>/`.
- Read the PDF, segment to chapter {n} (use TOC bookmarks if present; else visually scan).
- Run the `lecturer` agent on the chapter folder (it should read from the PDF page range). Then `note-taker`.

Respect `user.config.json` → `preferences.teach_mode` (`full` vs `brief`). Brief = theorem statements + one worked example + pitfalls; skip the motivation prose.

## Report

End with a tight summary:
- `Wrote: subjects/<subject>/<kind>/<folder>/{teach,notes}.md`
- `Open in the web UI:` (only mention this if `tutor web` isn't already running)
- `Next: /practice <subject> <matching-sheet-slug>` if a sheet exists, else `Next: /teach <subject> <next-ref> <term>`.

## Rules

- **Term is always required.** Ask if absent.
- **Never silently pick between two candidate PDFs.** Ask.
- **Exam urgency:** if the user's nearest exam is ≤ 7 days away and they asked for the other subject, mention it once: *"Your Linear Algebra exam is in 4 days. Want to switch?"* — then still do what they asked.
- Keep output ≤ 6 lines after the agents return.
