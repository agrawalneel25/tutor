# Known IDs — lookup table

Subject slugs (`analysis`, `calculus`, `linear-algebra`) → Imperial course codes → Panopto folder GUIDs → Blackboard course IDs.

**Re-scrape only if a new term starts or this file is older than 6 months.** Commands to rebuild:
```bash
uv run uni panopto folders --q MATH4
uv run uni bb courses
```

## Core subjects (JMC Y1, 2025/26)

| Slug | Module code | Full title | Panopto folder ID | Blackboard course ID |
|------|-------------|------------|-------------------|----------------------|
| `analysis` | MATH40002 | Analysis 1 | `d8a27c20-9898-46c7-9163-b31c01552694` | `_46862_1` |
| `calculus` | MATH40004 | Calculus and Applications | `a74c2408-69e3-4920-9139-b31b013ff055` | `_46772_1` |
| `linear-algebra` | MATH40012 | Linear Algebra and Groups for JMC | `44b6c0ec-8fa4-4fe3-81f2-b31b013fedae` | `_46759_1` |

## Related (not currently in scope)

| Module | Full title | Panopto | Blackboard |
|--------|------------|---------|------------|
| MATH40001/40009 | Intro to University Mathematics | `4e572b5b-024d-4953-bd5e-b31b013ff15e` | `_46805_1` / `_46829_1` |
| CLCC40008 | Introduction to Philosophy | — | `_46142_1` |

## Panopto conventions

- Caption `language` param is an **enum, not a name**. Imperial = `1` (English_GB). Client auto-detects via `DeliveryInfo.aspx`.
- `/api/v1/folders/search` needs `searchQuery` non-empty (use `*` = all).
- `/api/v1/sessions/*` returns 401 with cookies — use `Data.svc/GetSessions` instead (web UI's own endpoint, cookie-authenticated).

## Blackboard conventions

- Only these cookies belong in requests: `BbRouter`, `JSESSIONID`, `AWSELB`, `AWSELBCORS`, `shib_idp_session`, `samlCookie`, `SSOCOOKIEPULLED`, `s_session_id`.
- Sending the full Azure AD cookie set (`ESTSAUTH*`, `esctx-*`, etc.) trips nginx's header size limit → `400 Request Header Or Cookie Too Large`. `blackboard._client()` already filters.
- Student account: `aa5925`, student ID `02691878`, Blackboard user ID `_6250442_1`.
- Content listing: `/learn/api/v1/courses/{id}/contents?parentId=...` (cookie-auth). The documented `/public/v1/.../children` 403s for student cookies.
- Ultra content schema: folder detection via `contentDetail["resource/x-bb-folder"].isFolder`, not the documented Public-v1 shape. Deep content is often embedded (iframe to old Learn Original) — REST visibility is limited past 2 levels. Falls back to Playwright scraping if we need slide PDFs that aren't surfaced.

## Notion queue

Database: `Joint Mathematics and Computer Science`
ID: `289457a5-1164-80d3-975f-df76937e5ca6`

**Schema (properties that matter):**
- `Name` (title) — e.g. "Lecture 39"
- `Module` (select) — exact options: `MATH40002: Analysis I`, `MATH40004: Calculus and Applications`, `MATH40012: Linear Algebra and Groups`, `MATH40009: Introduction to University Mathematics`, `COMP40009: Computing Practical 1`, `COMP40018 / COMP40012 : Section on logic`, `COMP40008: Graphs and Algorithms`
- `Type` (select) — `Lecture`, `Problem Sheet`, `Exam`, `Quiz`, `Revision`, `Coursework`, `PPT`, `PMT`
- `Status` (status) — `Not started`, `In progress`, `Done`
- `Date` (date), `Duration` (number), `Material` (url), `Notes` (rich_text)

**Module → subject slug mapping:**
| Notion `Module` value | Subject slug |
|-----------------------|--------------|
| `MATH40002: Analysis I` | `analysis` |
| `MATH40004: Calculus and Applications` | `calculus` |
| `MATH40012: Linear Algebra and Groups` | `linear-algebra` |

**Canonical "missed lectures" query** (via the `notion-query` MCP):
```json
{
  "database_id": "289457a5-1164-80d3-975f-df76937e5ca6",
  "filter": {"and": [
    {"property": "Type",   "select": {"equals": "Lecture"}},
    {"property": "Status", "status": {"does_not_equal": "Done"}}
  ]},
  "sorts": [{"property": "Date", "direction": "descending"}]
}
```
Narrow to one subject by `and`-ing: `{"property": "Module", "select": {"equals": "MATH40002: Analysis I"}}`.
