---
description: First-time setup. Fully autonomous - deps, Playwright, config, Imperial SSO, health check.
---

You are running the `tutor` first-time setup **autonomously**. Do not ask the user for permission before each step. Do not offer to run commands yourself and wait. Just run them. The user launched Claude Code with `--dangerously-skip-permissions` specifically so you can drive the whole flow.

Pause only when the user must physically act (SSO login in a browser). Keep output tight: a one-line progress note per step is enough.

## Steps

1. **Check uv.** Run `uv --version`. If missing, tell the user to run `curl -LsSf https://astral.sh/uv/install.sh | sh` then re-run `/setup`, and stop.

2. **Sync deps.** Run `uv sync`.

3. **Prepare.** Run `uv run tutor prepare`. This installs Playwright chromium, scaffolds subject folders, and writes `user.config.json` (auto-detecting name from git config, defaulting to "Student"). Allow up to 3 minutes (chromium download).

4. **Panopto SSO.** If `auth_state/panopto.json` is missing, tell the user: *"A browser window will open. Log in with your Imperial account  -  I'll wait."* Then run `uv run tutor auth panopto` with a long timeout (pass `timeout: 600000` to Bash — 10 min). The command exits once the user lands back on the Panopto home page. If the file already exists, skip this step.

5. **Blackboard SSO.** Same pattern with `uv run tutor auth blackboard` if `auth_state/blackboard.json` is missing.

6. **Health check.** Run `uv run tutor doctor`.

7. **Outcome:**

   - **All green:** reply with exactly:

     ```
     Setup complete. Try:

     /study                       dashboard
     /teach analysis 1            first chapter
     /practice analysis sheet-1   first problem sheet

     Or open the local reader: uv run tutor web
     ```

   - **Red rows:** summarise which checks failed and the exact fix the doctor output suggests. If a 401 appears on Panopto/Blackboard, re-run the matching `uv run tutor auth ...` once.

## Rules

- Do not narrate what you are about to do. Just do it and report one line.
- Do not ask "should I run X?" — run X.
- Do not pipe interactive commands. `tutor auth panopto` and `tutor auth blackboard` are blocking and need the terminal.
- Do not re-prompt the user for their name, hint style, or teach depth. `prepare` writes sensible defaults. The user can edit `user.config.json` later.

End with: `Next: /study`.
