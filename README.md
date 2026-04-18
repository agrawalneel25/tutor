# tutor

A Claude Code study app for Imperial JMC Year 1. Clone it, open Claude Code, run `/setup`, then catch up on lectures and problem sheets with AI-guided teaching.

## Get started

1. Install [uv](https://docs.astral.sh/uv/) and [Claude Code](https://docs.claude.com/en/docs/claude-code).
2. Clone this repo and open it in Claude Code:
   ```bash
   git clone https://github.com/advitrocks9/tutor.git
   cd tutor
   claude --dangerously-skip-permissions
   ```
3. Inside Claude Code, type:
   ```
   /setup
   ```

That is all. Claude Code runs the whole setup autonomously: dependencies, Playwright, config, Imperial SSO logins (two headful browser pops where you just log in), and a health check. Then type `/study` to see your dashboard, or `/teach analysis 1` to start learning.

## What it does

Pulls Panopto transcripts and Blackboard materials for your JMC modules, turns each lecture or chapter into a rigorous teach.md plus dense revision notes.md, and fans problem sheets into per-question walkthroughs with graduated hints. A local web viewer renders everything with proper math typesetting.

## Slash commands

| Command | Use |
| --- | --- |
| `/setup` | First-time setup wizard |
| `/doctor` | Health check for every endpoint and dependency |
| `/study` | Dashboard showing progress and the next best action |
| `/teach <subject> <chapter-or-lecture>` | Learn new material |
| `/practice <subject> <sheet>` | Work a problem sheet question by question |
| `/hint` | Next hint on the active problem |
| `/check <your attempt>` | Mark your attempt against the canonical solution |
| `/skip` | Skip the current problem and advance |

## Scope

Built for the MATH40002 (Analysis), MATH40004 (Calculus), and MATH40012 (Linear Algebra and Groups) modules in the Imperial JMC Year 1 2025/26 cohort. The Panopto folder GUIDs and Blackboard course IDs are hardcoded because they are the same for every student. CS modules (COMP40008/40009/40018) are out of scope because those materials live on CATE.

## Privacy

Your Imperial SSO cookies live in `auth_state/` and are gitignored. Your preferences in `user.config.json` are gitignored. All fetched lectures, notes, and sheets under `subjects/` are gitignored. Nothing personal ever leaves your machine.
