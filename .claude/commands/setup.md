---
description: First-time setup. One command to install deps, log into Imperial, configure preferences, and verify health.
---

You are guiding a new user through first-time setup of the `tutor` study app. Execute in order; stop and fix before proceeding if any step fails.

1. **Check `uv`.** Run `uv --version`. If missing, tell them: `curl -LsSf https://astral.sh/uv/install.sh | sh` and stop.

2. **Sync deps.** Run `uv sync`. This should be fast (pulls from the lock file).

3. **Launch the interactive wizard.** Run `uv run tutor init`. This is blocking and interactive  -  **let it take over the terminal**. Do not pipe it. The wizard handles: Playwright chromium install, preferences prompts (name, hint style, teach depth), two Imperial SSO login flows (Panopto + Blackboard, headful browser), and a final health check.

4. **If the wizard reports green**, celebrate briefly and give the user their single best next action:

   ```
   You're set. Try:

   /study                       ← see your dashboard
   /teach analysis 1            ← learn chapter 1 of Analysis
   /practice analysis sheet-1   ← work a problem sheet

   Or open the web reader: uv run tutor web
   ```

5. **If any check is red**, name the failing row + the exact fix (e.g. `uv run tutor auth blackboard` for a 401). Don't read the output back verbatim  -  summarise.

Keep output tight. The user wants to start studying, not read a setup story.

End with: `Next: /study`.
