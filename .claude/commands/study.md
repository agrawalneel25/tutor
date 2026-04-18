---
description: Dashboard view  -  what's done, what's in-progress, recommended next action.
---

Show the user what's on their plate. Run `uv run tutor status` and present the output, then suggest the single most valuable next action.

If `tutor status` isn't available or errors, do this manually:

1. For each subject under `subjects/`:
   - Count `chapters/ch*-*/teach.md` (done chapters) vs the subject's total chapter count (from the PDF TOC if readable, or just report the count).
   - Count `lectures/L*-*/teach.md` (done lectures).
   - For each `sheets/<slug>/.progress.json`: count done / skipped / pending questions.

2. Identify the **single most valuable next action** based on:
   - Nearest exam (check `course-context.md`  -  summer assessment is 2026-04-27 to 2026-05-08).
   - Biggest gap: which subject has the fewest taught chapters relative to course scope?
   - In-progress sheets: pick up where they left off.

3. Output shape (keep tight  -  no walls of text):

```
tutor status

Analysis (MATH40002)
  ✓ 2 chapters taught   · 1 lecture · 0/0 sheets
Calculus (MATH40004)
   -  empty
Linear Algebra (MATH40012)
   -  empty

Next: /teach calculus 1   (weakest subject; covers integration techniques)
```

End with the Next suggestion. Don't offer more than one  -  decision fatigue slows them down.
