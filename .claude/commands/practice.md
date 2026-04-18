---
description: Start or resume working through a problem sheet. Usage  -  /practice <subject> <sheet-slug>
---

User invoked `/practice $ARGUMENTS`. Parse:
- **Subject**: one of `analysis`, `calculus`, `linear-algebra`.
- **Sheet slug**: folder name under `subjects/<subject>/sheets/`. If omitted or ambiguous, list available sheets and ask.

Flow:

1. **Locate sheet.** Check `subjects/<subject>/sheets/<sheet-slug>/`.
   - If it doesn't exist: run `uv run tutor bb sheets <subject>` to fetch, then re-check. If still missing, list what's available and stop.
   - If it exists but no `problems/` subfolder: invoke the `problem-solver` agent on the sheet directory. Wait for it to complete and write `problems/qNN.md` + `index.json`.

2. **Load progress** from `subjects/<subject>/sheets/<sheet-slug>/.progress.json` (create empty if missing).

3. **Determine current question.** Either the `current` field in progress, or the first question with `status != done && status != skipped`.

4. **Respect user preference**  -  read `user.config.json` → `preferences.hint_style`:
   - `progressive`: show the statement only, offer `/hint` or `/check` next.
   - `on_demand`: show statement + "hints available: /hint" note.
   - `none`: show statement only; no hint prompts.
   - If `preferences.reveal_solution_immediately` is true, show the full solution too.

5. **Display the current question.**
   - Read the q`NN`.md.
   - Print: the statement (formatted), plus a footer like:
     ```
     Question 3 of 8   -   technique: {technique}
     Commands: /hint  /check <attempt>  /skip  /practice <subj> <sheet> to reselect
     ```
   - Also mention: run `uv run tutor web` to see it rendered with math in the browser.

6. **Update progress**: set `current: qNN` and `questions.qNN.status = in_progress`, save.

Keep the output tight. The user will read the problem, attempt it, then come back with `/hint` or `/check`.

End with a one-line footer: `Next: /hint · /check <attempt> · /skip`.
