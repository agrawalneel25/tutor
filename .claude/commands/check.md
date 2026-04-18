---
description: Submit an attempt at the current problem. Usage  -  /check <your attempt, free-form>
---

The user submits `$ARGUMENTS` as their attempt at the current problem.

1. Identify the active problem (see `/hint` for lookup logic).

2. Read the qNN.md `## Solution` section plus any `## Common pitfalls`.

3. **Mark the attempt.** Compare against the canonical solution rigorously:
   - Is the final answer correct?
   - Is the reasoning sound? Are the right theorems cited with hypotheses checked?
   - Are there gaps, sign errors, or missed cases?

4. **Give feedback** in this shape:

   ```
   Verdict: ✓ correct   |   ≈ mostly correct   |   ✗ not quite

   What you got right:
   - {bullet}
   - {bullet}

   What to fix:
   - {bullet, specific  -  point at the exact line / step}
   - {bullet}

   Canonical solution: (show it in full, collapsed if very long)
   ```

5. **Update progress**:
   - `questions[current].attempts += 1`
   - `questions[current].last_attempt = $ARGUMENTS`
   - `questions[current].correct = true | false`
   - If correct or "mostly" and user wants to move on, offer to set `status = done` and advance to the next pending question  -  but don't auto-advance; let the user say so or invoke `/practice` again.

6. Save progress.

Be generous with partial credit but ruthless about rigour  -  a correct answer with a hand-waved argument should get "≈ mostly correct" with a pointer to the specific rigour gap.

End with a one-line `Next:`  -  on a correct attempt, suggest advancing (`Mark done and go to q+1?` or `/skip` to advance); on a wrong attempt, suggest `/hint` or reattempt.
