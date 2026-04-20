# Scientia workflow

Scientia is the document-library version of tutor: instead of lectures and
problem sheets, it ingests a large export of exercises, notes, worked
solutions, and past papers, then compiles them into one coherent revision
document.

## What it is for

- Turn a scattered library export into a single study corpus.
- Pair each exercise with its solution source, if one exists.
- Preserve the original notation and wording where it matters.
- Produce a document that is easier to revise from than a folder tree.

## What counts as input

- PDFs
- Markdown notes
- plain text exports
- OCR text, if the PDFs are scanned
- any folder tree exported from a document library

## What comes out

- `master.md` - one consolidated revision document
- `index.json` - machine-readable inventory of sources and pairings
- optional `appendix/` files if the corpus is too large to keep in one file

## Design constraints

- Never invent missing exercise text.
- Never invent a solution that is not actually present.
- If a solution is ambiguous, mark it `TODO` and keep the unresolved source.
- If OCR is poor, keep the visible fragment and flag the confidence level.
- Prefer exact titles, numbering, and section headings when pairing exercise to solution.

## Recommended pipeline

1. Inventory the library export.
2. Group documents by subject, topic, or paper.
3. Detect exercise sets and solution notes.
4. Match exercises to solutions using title, numbering, and nearby headings.
5. Extract the statements verbatim.
6. Compile the matched solutions into a single markdown master file.
7. Add an index table and an unresolved-items section.
8. Sanity check that every source document is accounted for.

## Best use case

This is most useful when the library already contains the answer key somewhere in
the notes, but it is buried across many files. The agent can do the tedious
mapping once, then leave you with a single document you can revise from.
