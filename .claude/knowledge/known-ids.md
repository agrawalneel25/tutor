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

**Key insight:** Imperial's JMC courses are "Ultra-wrapped Learn Original" — Ultra chrome, classic content backend. `/learn/api/*` only exposes Ultra's top-level shell (Homepage + Reading List). The real material lives at `/webapps/blackboard/content/listContent.jsp` and is scraped as HTML.

- Cookie allowlist: `BbRouter`, `JSESSIONID`, `AWSELB`, `AWSELBCORS`, `shib_idp_session`, `samlCookie`, `SSOCOOKIEPULLED`, `s_session_id`. Full Azure AD cookie set (`ESTSAUTH*`, `esctx-*`) trips nginx header size → `400 Request Header Or Cookie Too Large`.
- Student account: `aa5925`, student ID `02691878`, Blackboard user ID `_6250442_1`.
- Entry pattern: `uni bb roots <courseId>` → REST, gives `Homepage` content_id → then `uni bb tree <courseId> <homepageId>` scrapes the Learn Original subtree.
- Folder page parse: `ul#content_listContainer > li` items. Each `<li id="contentListItem:_XXXX_1">` carries the content_id. The `<img class="item_icon">` `alt` attribute gives the type (`Content Folder`, `File`, `Web Link`, `Item`, ...). For `File` items, the `<h3> <a>` href is the direct `/bbcswebdav/...` download.
- File URLs: `/bbcswebdav/pid-{n}-dt-content-rid-{n}_1/xid-{n}_1` — served 200 with cookie auth, `Content-Disposition` gives the real filename.

## Analysis 1 known content tree (2025/26)

- Homepage: `_3554584_1`
- Lecture Notes: `_3658112_1` — contains "Gapped" and "Complete" subfolders, plus full handwritten PDF
- Problem Sheets: `_3658113_1`
- Coursework 2: `_3658114_1`
- Midterm Past Papers: `_3661579_1`
- Fall 2025 Materials (archive): `_3658111_1`

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
