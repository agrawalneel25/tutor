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
