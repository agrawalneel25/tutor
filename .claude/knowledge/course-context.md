# Course context  -  JMC Year 1, Imperial College London, 2025/26

This is exam-prep mode. Teaching is over for the academic year; what remains is catchup + practice. Everything below is static until the next cohort.

## Exam dates (final, verified with the user)

| Subject                          | Code      | Exam date    |
|----------------------------------|-----------|--------------|
| Linear Algebra & Groups for JMC  | MATH40012 | **2026-04-29** |
| Analysis 1                       | MATH40002 | **2026-05-05** |
| Calculus and Applications        | MATH40004 | **2026-05-06** |

Both autumn and spring term content is examined in all three.

## Term structure

Each module is split into **autumn** (fall, T1) and **spring** (T2). Lecture numbering **restarts at 1 each term** in the official course materials. The course map encodes this: `analysis.autumn.lectures[0]` is "L1 autumn", `analysis.spring.lectures[0]` is "L1 spring" — two different recordings.

Imperial 2025-26 teaching weeks (what's used to bucket Panopto sessions):

- **Autumn:** 2025-10-06 → 2025-12-12
- **Spring:** 2026-01-12 → 2026-03-20

Panopto recordings outside those windows are dropped at map-build time. Recordings from earlier academic years are filtered by `ACADEMIC_YEAR_START = 2025-09-01`.

## The course map

`.claude/knowledge/course-map.json` (per-user, gitignored) is the agent's primary index. Built by `uv run tutor map build`, refreshed on demand.

Shape:

```
subjects.<slug>.terms.<autumn|spring>.lectures[i]  -> {n, title, date, delivery_id, viewer_url, duration_min}
subjects.<slug>.terms.<autumn|spring>.materials[i] -> {title, local_path, pages, url}
```

A markdown mirror lives at `.claude/knowledge/course-map.md` for human browsing. Agents should prefer the JSON for lookups (faster) and the markdown only when narrating.

The map is **context, not a fence**. If the user says "explore Panopto directly for me", call `tutor panopto list <subject>` — don't refuse because the map already has an answer.

## Materials structure

Chapter PDFs are not individual files. Each subject has a **single massive lecture-notes PDF** per term. Chapters live as bookmarked sections inside those PDFs. Some may have been split into smaller PDFs on Blackboard — the map inventories whatever files exist under `subjects/<slug>/materials/`.

When `/teach <subject> ch{n} <term>` runs:

1. Look up the term's PDFs in the course map.
2. If more than one PDF matches the term, **ask the user which one**.
3. Open the PDF, find chapter {n} via the bookmarks / TOC.
4. Extract the page range.
5. Feed to the `lecturer` agent.

## Lecture ↔ Panopto matching

The map pre-resolves this: call `uv run tutor resolve <subject> L{n} <term>` and get back `delivery_id` + `viewer_url`. That's the only lookup `/teach` needs.

If the user is unsure which Panopto recording they want (e.g. duplicate recordings from overflow theatre), **ask**. They can paste a Panopto viewer URL directly as the `ref` arg — `parse_viewer_url` extracts the GUID.

## Term clarification protocol

If the user says "teach me chapter 3" without a term, the agent **always asks** — once — before doing anything. The wrong term is a wasted 2-3 minutes and a misleading note file. `"Autumn or spring?"` is a 5-second clarification.

This applies to all subject commands: `/teach`, `/practice` (if sheets are term-tagged), `/check`.

## Modules (in scope)

### MATH40002  -  Analysis 1
Rigorous real analysis.

- **Autumn:** real numbers, sequences, series, limits, continuity, IVT, EVT.
- **Spring:** differentiability, MVT, Taylor, power series, Riemann integration, FTC, intro uniform convergence.

### MATH40004  -  Calculus and Applications
Often recorded twice (main + overflow); Panopto lists both, map numbers chronologically so there may be duplicates. Watch for it.

- **Autumn:** integration techniques, 1st/2nd-order linear ODEs, complex + Euler, series solutions.
- **Spring:** multivariable calc (partials, chain rule, gradient), vector calc (div/grad/curl, line/surface integrals, Green/Stokes/Divergence), intro PDEs (heat, wave, Laplace).

### MATH40012  -  Linear Algebra and Groups for JMC
- **Autumn:** vector spaces, bases, linear maps, matrices, rank-nullity, determinants, eigenvalues, diagonalisation.
- **Spring:** group theory — groups, subgroups, homomorphisms, Lagrange, normal subgroups, quotients, group actions.

Exact lecture counts per term are whatever the map reports after build. Don't hard-code.

## CS modules and Scientia exports

COMP40008 / COMP40009 / COMP40018 materials are not in Blackboard. Use Scientia/CATE exports instead. The repo now supports local Scientia root discovery, indexing, and full-text search. Live Scientia scraping is still out of scope. If the user asks for a CS module, tell them to use a Scientia export or local folder and search it there.

## Teaching style

- **Imperial rigour**, not US undergrad. Quantifiers matter. LaTeX in `$...$` and `$$...$$`.
- Definitions verbatim-precise; intuition comes *after* the statement.
- Worked examples non-negotiable — every theorem gets at least one.
- Target: 60 min lecture → 15 min active reading. `lecturer` does the teach pass, `note-taker` compresses to revision density.

## Assessment

Summer exam 70-80% of the module mark. Closed-book, written. Coursework/midterm weights are already locked in.
