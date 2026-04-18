# Known IDs  -  JMC Y1, 2025/26

These are the Imperial JMC Year 1 Panopto folder GUIDs and Blackboard course /
content IDs. **Identical across all students in the cohort**  -  safe to commit.

Canonical source is `src/tutor/shared.py :: SUBJECTS`. This file is the
human-readable summary.

## Core maths subjects

| Slug | Module | Title | Panopto folder | BB course |
|------|--------|-------|----------------|-----------|
| `analysis` | MATH40002 | Analysis 1 | `d8a27c20-9898-46c7-9163-b31c01552694` | `_46862_1` |
| `calculus` | MATH40004 | Calculus and Applications | `a74c2408-69e3-4920-9139-b31b013ff055` | `_46772_1` |
| `linear-algebra` | MATH40012 | Linear Algebra and Groups | `44b6c0ec-8fa4-4fe3-81f2-b31b013fedae` | `_46759_1` |

## Analysis BB content tree

Shared across all JMC students. Discovered 2026-04-17.

| Slot | Content ID | Note |
|------|-----------|------|
| Homepage | `_3554584_1` | Root entry point |
| Lecture Notes | `_3658112_1` | Has "Gapped" (T2 fill-in) and "Complete" PDFs |
| Problem Sheets | `_3658113_1` | Per-sheet PDFs |
| Coursework 2 | `_3658114_1` | |
| Midterm Past Papers | `_3661579_1` | |
| Fall 2025 archive | `_3658111_1` | Older material |

Calculus and Linear Algebra BB subtrees aren't mapped yet. Use
`uv run tutor bb roots <courseId>` → `uv run tutor bb tree <courseId> <homepageId>`
to discover them, or `uv run tutor bb sheets <subject> --resolve` for sheets.

## CS modules (materials on Scientia/CATE, not Blackboard)

| Module | Title | Panopto folder |
|--------|-------|----------------|
| COMP40009 Haskell T1 | Computing Practical 1 | `965c415c-ad7d-4d07-bc72-b2ed0175ce96` |
| COMP40009 Kotlin T2 | Computing Practical 1 | `8f8f88dc-bcc9-48b6-a359-b36e00a6c6d7` |
| COMP40008 | Graphs and Algorithms | `2f5ccfc1-1aac-4344-90a0-b2ee00d10876` |
| COMP40018 / COMP40012 | Reasoning about Programs (Logic) | `b9547766-6916-474f-8291-b2ee008fc86d` |

CATE scraping is a future addition  -  out of scope for the current pipeline.

## Panopto gotchas

- `/api/v1/folders/search` requires non-empty `searchQuery`  -  use `*` for "all".
- `/api/v1/sessions/*` returns 401 on cookie auth  -  use
  `/Panopto/Services/Data.svc/GetSessions` (the web UI's own endpoint).
- Caption `language` is an **enum**, not a name. Imperial = `1` (English_GB).
  The client auto-detects via `DeliveryInfo.aspx`.
- Folder names like "Autumn 2025-2026" often contain **both** T1 and T2
  recordings. Sort by date, don't trust naming.

## Blackboard gotchas

- Courses are "Ultra-wrapped Learn Original": Ultra nav shell around classic
  Learn Original content. `/learn/api/*` only exposes the shell (Homepage,
  Reading List); real material is at `/webapps/blackboard/content/listContent.jsp`
  and must be scraped.
- Cookie allowlist  -  full Azure AD jar (`ESTSAUTH*`, `esctx-*`) overflows nginx
  → `400 Request Header Or Cookie Too Large`. The client keeps only:
  `BbRouter, JSESSIONID, AWSELB, AWSELBCORS, shib_idp_session, samlCookie,
  SSOCOOKIEPULLED, s_session_id`.
- Folder page: `ul#content_listContainer > li` items, `<li id="contentListItem:_XXXX_1">`
  encodes the content_id, `<img class="item_icon">` alt gives the type
  (`Content Folder`, `File`, `Web Link`, `Item`, …). For `File` items the
  `<h3> <a>` href is a direct `/bbcswebdav/...` download.
