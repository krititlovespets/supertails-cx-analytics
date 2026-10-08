# Supertails CX Analytics — Wiki Index

Persistent knowledge base for the Supertails call-center/lead-funnel analytics
engagement (Google Sheet "Dashboard || Extra"). See `schema.md` for how this
wiki works. Start a session by reading the pages relevant to the task, not all
of them.

## Pages

- [schema.md](schema.md) — how this wiki is structured and maintained (ingest/lint)
- [definitions.md](definitions.md) — canonical metric definitions (Valid Lead,
  Connect, Transfer Done/Doctor Called, AHT, FRT, Vet Follow-up, etc.)
- [daily-workflow.md](daily-workflow.md) — the refresh process: inputs, script
  pipeline, day-rollover checklist, verification steps, rate-limit handling
- [sheet-structure.md](sheet-structure.md) — current tab-by-tab layout of the
  live Google Sheet (row/column structure, what's pink/red, row counts)
- [bug-patterns.md](bug-patterns.md) — 11 recurring bug classes and their fixes;
  check new scripts against this before trusting them
- [external-sources.md](external-sources.md) — Clinic Dashboard sheet (Booking
  Done) + the manual Nugget ticket-export UI flow
- [vet-followup.md](vet-followup.md) — the 15-Day Repeat metric's definition
  history and current rule (15-minute threshold, not calendar-day)

## Fallback / historical detail

The full day-by-day narrative of this engagement (every message, every
back-and-forth, through 2026-10-07) lives in the Claude auto-memory file
`nugget_ameyo_daily_sheet_workflow.md`. This wiki is now the primary reference
for *current state*; that file remains useful for *how we got here* on a
specific historical question.

## Status

First ingest: 2026-10-08, bootstrapped from the existing memory file's
accumulated knowledge. See `log.md` for what's been added since.
