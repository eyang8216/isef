# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Layout: single-context

This repo is single-context — one `CONTEXT.md` + `docs/adr/` at the repo root.

```
/
├── CONTEXT.md
├── docs/adr/
└── solver/
```

Neither `CONTEXT.md` nor `docs/adr/` exists yet. That's expected — see below.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, if it exists.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in.

If these files don't exist, **proceed silently**. Don't flag their absence;
don't suggest creating them upfront. The `/domain-modeling` skill (reached
via `/grill-with-docs` and `/improve-codebase-architecture`) creates them
lazily when terms or decisions actually get resolved — e.g. once "shielding
metric," "residual," or "half-angle" need a fixed glossary definition, or
once a hard-to-reverse choice (grid indexing convention, far-boundary
default) is worth recording as an ADR instead of just living in a spec.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor
proposal, a hypothesis, a test name), use the term as defined in
`CONTEXT.md` once it exists. Don't drift to synonyms the glossary explicitly
avoids.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather
than silently overriding.
