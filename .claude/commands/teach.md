---
description: Teach a lecture or chapter. Usage  -  /teach <subject> <lecture-or-chapter>. Fetches material if needed, runs lecturer agent, produces teach.md + notes.md.
---

The user ran `/teach $ARGUMENTS`. Parse the arguments to determine:
- **Subject slug**  -  one of `analysis`, `calculus`, `linear-algebra`.
- **Target**  -  either a lecture number (`L14`, `14`) or chapter identifier (`ch12`, `12`, or a chapter name).

Flow:

1. **Find the material.**
   - If target is a lecture number `N`: look in `subjects/<subject>/lectures/` for a folder matching `L{N:02d}-*`. If missing, find the delivery ID via `.claude/knowledge/lecture-map.json` (regenerate with the snippet in `lecture-map.md` if absent) and run `uv run tutor panopto fetch <subject> <deliveryId> --n N --title "<title>"`.
   - If target is a chapter: look in `subjects/<subject>/chapters/`. If missing, read the relevant PDF from `subjects/<subject>/materials/` and synthesise from there.

2. **Run the lecturer agent** on the target folder. It produces `teach.md`.

3. **Run the note-taker agent** on the same folder. It produces `notes.md` and appends to `last-done.md`.

4. **Summarise** what was produced: paths written, 1-sentence gist, and tell the user they can open the web UI (`uv run tutor web`) to read in a nicer format.

Respect `user.config.json` → `preferences.teach_mode` (`full` vs `brief`). For `brief`, tell the lecturer agent to emit a condensed teach.md (theorem statements + 1 worked example + key pitfalls, skip the full motivation prose).

End with a one-line `Next:` suggestion  -  typically `/practice <subject> <matching-sheet-slug>` if a sheet exists, or the next chapter to teach.
