# language-patterner

Static site generator for "A Pattern Language"-style books. Python + Jinja2 + markdown.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
```

## Build & validate

```bash
patterner build --source <dir> --output _site
patterner validate --source <dir>
```

## Pattern language source structure

```
<source-dir>/
  book.yaml
  patterns/
    001-name.md
    002-name.md
```

See `example/` for a working reference.

## Snippet for other repos

Add this to another repository's `CLAUDE.md` to instruct Claude to generate a pattern language from that codebase:

---

### Pattern Language Generation

Use [language-patterner](https://github.com/mverzilli/language-patterner) to generate a pattern language book that documents the recurring design patterns in this codebase.

#### Setup

```bash
pip install git+https://github.com/mverzilli/language-patterner.git
```

#### Instructions

1. **Explore the codebase thoroughly** — understand the architecture, key abstractions, module boundaries, and recurring design decisions.

2. **Create `book.yaml`** at the project root (or a subdirectory like `patterns/`):

```yaml
title: "A Pattern Language for [Project Name]"
subtitle: "Optional subtitle"
authors:
  - Author Name

scales:
  - id: system
    name: "System Architecture"
    description: "Patterns shaping the overall system"
    range: [1, 10]
  - id: component
    name: "Components & Modules"
    description: "Patterns for organizing code into units"
    range: [11, 20]
  - id: implementation
    name: "Implementation"
    description: "Patterns at the code level"
    range: [21, 30]

confidence_labels:
  0: "Hypothesis"
  1: "Progressing"
  2: "Invariant"
```

   Adjust scales and ranges to fit the project. Leave gaps in numbering for future patterns.

3. **Create `patterns/` directory** with one `.md` file per pattern:

```markdown
---
number: 1
name: "Pattern Name"
confidence: 2
contains: [11, 12]
contained_by: []
tags: [relevant, tags]
---

First paragraph before any heading = the problem statement (auto-extracted for listings).

## Context

When and why this pattern applies.

## Therefore

The solution this pattern proposes.

## Consequences

Benefits and trade-offs of applying this pattern.
```

   Frontmatter fields:
   - `number` (required) — unique int, determines scale placement via `range` in `book.yaml`
   - `name` (required) — human-readable name
   - `confidence` — 0 (hypothesis), 1 (progressing), 2 (invariant)
   - `contains` — pattern numbers this one contains (children in the hierarchy)
   - `contained_by` — pattern numbers that contain this one (parents)
   - `tags` — keyword list

   Keep `contains`/`contained_by` consistent in both directions. Larger-scale patterns typically contain smaller-scale ones.

4. **Build and validate:**

```bash
patterner build --source . --output _site
patterner validate --source .
```

#### What to look for

- **Architectural invariants** (confidence 2) — rules the codebase always follows
- **Recurring design decisions** (confidence 1) — patterns applied in most but not all cases
- **Emerging conventions** (confidence 0) — patterns you suspect but aren't yet sure about
- **Containment relationships** — which high-level patterns depend on or decompose into lower-level ones

---
