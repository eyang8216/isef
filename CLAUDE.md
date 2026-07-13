# CLAUDE.md

## Agent skills

### Issue tracker

Local markdown under `.scratch/<feature>/` — solo project, no public tracker needed despite the GitHub remote. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root, created lazily by `/domain-modeling` when needed. See `docs/agents/domain.md`.
