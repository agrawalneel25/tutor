---
description: Skip the current problem and advance.
---

Mark the current problem as skipped and move on:

1. Locate the active sheet (same logic as `/hint` and `/check`).

2. Set `questions[current].status = "skipped"` in `.progress.json`.

3. Find the next pending question in `index.json` order. If there is one, set `current = qNN` and `status = in_progress`, then display it (same format as `/practice`).

4. If all questions are done or skipped, congratulate the user and suggest `/practice <subject> <next-sheet>`.

Save progress, output tight.
