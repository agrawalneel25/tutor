# Course context  -  JMC Year 1, Imperial College London, 2025/26

Imperial Joint Maths & Computing (JMC). Y1 runs three maths modules through the
Maths Department (Blackboard + Panopto) and three CS modules through DoC
(Scientia/CATE + Panopto  -  **not** Blackboard).

## Term dates (Panopto session data, verified 2026-04-17)

- **Autumn (T1):** Mon 2025-10-27 → Thu 2025-12-11
- **Spring (T2):** Mon 2026-01-12 → Thu 2026-03-19
- **Summer assessment:** 2026-04-27 → 2026-05-08

## Maths modules (in scope for this pipeline)

### MATH40002  -  Analysis 1  (≈41 lectures)
Rigorous real analysis.
- **T1 (L01-L21):** real numbers, sequences, series, limits, continuity, IVT, EVT.
- **T2 (L22-L41):** differentiability, MVT, Taylor, power series, Riemann
  integration, FTC, intro uniform convergence.
- Rooms: HXLY-02-213 most weeks, HXLY-03-308 Mondays in T2.

### MATH40004  -  Calculus and Applications  (≈48 recordings; dedupe to ~30 unique)
- **T1:** integration techniques, 1st/2nd-order linear ODEs, complex + Euler,
  series solutions.
- **T2:** multivariable calc (partials, chain rule, gradient), vector calc
  (div/grad/curl, line/surface integrals, Green/Stokes/Divergence), intro PDEs
  (heat, wave, Laplace).
- Lectures are often recorded twice (main theatre + overflow). Dedupe by date.

### MATH40012  -  Linear Algebra and Groups for JMC  (32 lectures)
- **T1 (L01-L14):** vector spaces, bases, linear maps, matrices, rank-nullity,
  determinants, eigenvalues, diagonalisation.
- **T2 (L15-L32):** group theory  -  groups, subgroups, homomorphisms, Lagrange,
  normal subgroups, quotients, group actions.

## Numbering conventions

Two frames coexist for each module  -  be careful not to confuse them:

- **Aggregate**  -  chronological across T1+T2. "Analysis L40" = the 40th
  lecture of the year. Use this for Notion queue lookups and for the
  Panopto session index.
- **Term-local**  -  what lecture-note PDFs use ("Lecture 19 Gapped" in the T2
  Gapped folder). Convert with `aggregate = T1_count + term_local`. T1 counts:
  Analysis 21, Calc ~21 (post-dedup), LinAlg 14.

`.claude/knowledge/lecture-map.json` (generated per-user) maps Notion index →
Panopto delivery_id per subject.

## CS modules (out of scope  -  future work)

| Module | Title | Panopto | Materials |
|--------|-------|---------|-----------|
| COMP40009 | Computing Practical 1 (Haskell T1 → Kotlin T2) | ✓ | CATE |
| COMP40008 | Graphs and Algorithms | ✓ | CATE |
| COMP40018/40012 | Reasoning about Programs (Logic) | ✓ | CATE |

CATE scraping isn't implemented. For now, CS materials must be handled manually.

## Teaching style

- **Imperial rigour**, not US undergrad. Quantifiers matter. LaTeX everywhere.
- Definitions verbatim-precise. Intuition comes *after* the statement.
- Worked examples non-negotiable  -  every theorem gets at least one.
- Target compression: 60 min lecture → 15 min active reading via
  `lecturer` → `note-taker` agents.

## Assessment

- Continuous coursework 10-20% (already locked in).
- Midterm where applicable (small %).
- **Summer exam 70-80%**, 2-3 hr written (maths) or on-screen (CP1 Kotlin),
  closed-book.
