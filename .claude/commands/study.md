---
description: Dashboard - exam countdown, coverage per subject, single next action.
---

Show the user what matters right now. This is exam-prep mode: the nearest exam dominates.

## Flow

1. Run `uv run tutor exams` — countdown table per subject.
2. Run `uv run tutor status` — coverage breakdown.
3. If the course map exists (`.claude/knowledge/course-map.json`), summarise what is unindexed: how many lectures per subject/term are indexed vs how many have local `teach.md`/`notes.md` folders. That is the user's catchup gap.
4. Pick **one** next action. Decision order:
   - If any exam is ≤ 3 days: push the subject with the soonest exam and the largest untaught gap.
   - Else if an in-progress sheet has pending questions: resume that sheet.
   - Else: biggest uncovered chapter/lecture in the subject with the soonest exam.

## Output shape

```
Exams:   LinAlg 29 Apr (11d)   Analysis 5 May (17d)   Calculus 6 May (18d)

Analysis (MATH40002)   autumn: 10/21 taught · spring: 0/20 taught   sheets: 3/7 done
Calculus (MATH40004)   autumn: 0/21 taught  · spring: 0/27 taught   sheets: 0/6 done
LinAlg   (MATH40012)   autumn: 0/14 taught  · spring: 0/18 taught   sheets: 0/8 done

Next: /teach linear-algebra L1 autumn   (LinAlg exam in 11 days, zero coverage)
```

Format the numbers right, keep it tight. No commentary walls.

End with exactly one `Next:` line.
