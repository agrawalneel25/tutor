---
description: Compile a Scientia export into a single revision document with exercise-to-solution pairings.
---

Use this when the user wants the document-library equivalent of `/practice`:
take a large Scientia export and turn it into one master study file.

## Flow

1. Ask for or locate the source root of the Scientia export.
2. Inventory the folder tree: PDFs, notes, exercise sets, solution notes.
3. If the sources are not yet text-readable, extract OCR/text first or mark the
   unreadable items as unresolved.
4. Invoke the `scientia-compiler` agent on the source root.
5. Write the outputs into a clean target directory, keeping `master.md`,
   `index.json`, and `unresolved.md` together.

## Output shape

Report back with:

- the source root used
- the output directory written
- the count of paired / partial / unresolved documents
- a short recommendation on whether the resulting master file is good enough
  to study from directly or should be split by topic

## Decision rules

- If the export is small, prefer a single `master.md`.
- If the export is large, keep a top-level index and split the body by topic.
- If OCR quality is poor, do not guess. Keep the unresolved section visible.
- If the notes contain the solutions already, extract those instead of
  re-deriving them.

## What makes this useful

The value is not just storage. The compiler turns a library into a revision
sequence: exercise statement, solution source, and the minimum context needed
to revise efficiently.
