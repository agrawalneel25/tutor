---
description: Build, inspect, or refresh the course map (index of lectures + materials per term).
---

The course map is at `.claude/knowledge/course-map.json`. It's the agent's index of what exists for this academic year, per subject per term.

Parse `$ARGUMENTS`:

- `build`  -  run `uv run tutor map build`. Idempotent. Safe to rerun.
- `refresh` or `rebuild`  -  same as build, rerunning after new lectures or new materials.
- `show [<subject>] [--term autumn|spring]`  -  `uv run tutor map show $ARGS`.
- `path`  -  print the on-disk location of the JSON.
- (no args)  -  if the file is missing, run build. Otherwise run `show`.

The map is **per-user** and gitignored. It does not ship in the repo — each student builds their own after SSO.

The map is **context, not a rail**. If the user asks to explore Panopto directly, use `uv run tutor panopto list <subject>`. Agents should prefer the map by default because it's 10-100x faster than scraping on every call.

End with a one-line summary of what you did.
