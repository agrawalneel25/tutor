---
description: Reveal the next hint for the current problem.
---

Show the next hint for the current problem:

1. Find the active sheet from the most recent `/practice` invocation (or read `.progress.json` under each subject's `sheets/` until you find one where `current` is set and the question status is `in_progress`).

2. Load `.progress.json`. Increment `questions[current].hints_shown`.

3. Read the corresponding `problems/qNN.md`. Depending on the new `hints_shown` value:
   - `1`: print the `## Hint 1` section.
   - `2`: print `## Hint 2`.
   - `3+`: print the `## Solution` section, set status to `done`, `correct: null` (user has seen solution without submitting).

4. Save progress.

Output the hint and nothing else beyond a one-line footer: `Hints shown: N/2. Next: /check <attempt> or /hint`.
