---
description: First-time setup. Fully autonomous - deps, Playwright, unified SSO, health check, course map build.
---

You are running the `tutor` first-time setup **autonomously**. The user launched Claude Code with `--dangerously-skip-permissions` for this. Drive every step; do not ask before running commands.

Pause only when the user must physically act (the single Imperial SSO browser login). Keep output tight: one line of progress per step.

## Steps

1. **Check uv.** Run `uv --version`. If missing, tell the user to run `curl -LsSf https://astral.sh/uv/install.sh | sh`, then re-run `/setup`. Stop.

2. **Sync deps.** Run `uv sync`.

3. **Prepare.** Run `uv run tutor prepare`. Installs Playwright chromium, scaffolds subject folders, writes `user.config.json` (name auto-detected from `git config user.name`; default `Student`). Allow up to 3 minutes on first run for the chromium download.

4. **Unified Imperial SSO.** If either cookie file is missing (`auth_state/panopto.json` or `auth_state/blackboard.json`), tell the user: *"One browser window will open. Log in with your Imperial account once — I'll capture both Panopto and Blackboard from the same session."* Then run `uv run tutor auth all` with Bash `timeout: 900000` (15 min). The command exits once both cookie files are written.

5. **Health check.** Run `uv run tutor doctor`. If anything red:
   - 401 on Panopto or Blackboard → re-run `uv run tutor auth all` once.
   - Missing chromium → re-run `uv run tutor prepare`.
   - Still red → summarise the failing check and the fix it suggests; stop there.

6. **Pull Blackboard materials.** For each subject, run `uv run tutor bb sheets <subject> --resolve` (problem sheets). Then, if `SUBJECTS[<subject>].bb_lecture_notes` is configured (currently only `analysis`), run `uv run tutor bb pull <subject> <course_id> <content_id> --name lecture-notes` — consult `.claude/knowledge/known-ids.md` for content IDs. For `calculus` and `linear-algebra` where only the course is configured, run `uv run tutor bb roots <course_id>`, find a folder titled like "Lecture Notes", "Notes", or "Syllabus", then pull it. If nothing obvious, skip quietly — the user can pull later.

7. **Build the course map.** Run `uv run tutor map build`. Indexes every lecture (academic-year filtered, term-bucketed) plus inventoried materials. Writes `.claude/knowledge/course-map.{json,md}`.

8. **Success.** Print exactly:

   ```
   Setup complete.

   /study                               dashboard + exam countdown
   /teach analysis L1 autumn            teach a lecture
   /practice analysis sheet-1           work a problem sheet
   /map show                            see the full index

   Web reader: uv run tutor web
   ```

## Rules

- Do not narrate planned actions. Run them and report one line each.
- Never re-prompt for preferences. `prepare` writes defaults; user can edit `user.config.json` later.
- If `auth_state/*.json` already exist, skip step 4 silently.
- If the course map exists, skip step 7 unless the user explicitly asked to refresh.
- After setup, if the nearest exam is within 14 days, append one line: *"Your <subject> exam is in <n> days."*

End with: `Next: /study`.
