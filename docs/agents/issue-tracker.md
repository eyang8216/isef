# Issue Tracker

**Choice:** Local markdown

Issues and specs for this repo live as markdown files in `.scratch/`, per
`.agents/skills/setup-matt-pocock-skills/issue-tracker-local.md`. Chosen over
GitHub Issues because this is a solo ISEF project — no need for a public
tracker even though `origin` points at GitHub.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at
  `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each file
- Comments/history append under a `## Comments` heading at the bottom

## Triage labels

Default vocabulary, unchanged — see
`.agents/skills/setup-matt-pocock-skills/triage-labels.md`:

`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`

## Domain docs

Not yet set up — no `CONTEXT.md` or `docs/adr/` exist. Run
`/domain-modeling` or the domain-docs section of
`/setup-matt-pocock-skills` before this becomes load-bearing (e.g. once
terms like "shielding metric" or "residual" need a fixed glossary
definition).
