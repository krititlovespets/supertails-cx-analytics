# Wiki Schema

This wiki follows the "LLM Wiki" pattern (Karpathy): raw sources get **ingested**
into persistent markdown pages here, which get queried instead of re-derived each
session, and periodically **linted** for staleness/contradictions.

## Structure

- `index.md` — catalog of all pages, organized by topic. Start here.
- `log.md` — chronological, append-only record of every ingest/lint/major session.
- `schema.md` — this file.
- Topic pages (flat, in this directory) — one per coherent subject area. See index.md.

## Conventions

- **Ingest** = after a productive session (a refresh, a new feature, a bug fix),
  update the relevant topic page(s) with what changed, and append one line to
  `log.md`. Don't wait to batch multiple sessions into one ingest.
- **Lint** = periodically (user-triggered, or when a page feels stale) re-read a
  topic page against current reality (the live Google Sheet, the current scripts)
  and fix contradictions, remove resolved TODOs, flag orphaned claims.
- Pages are living documents — rewrite/reorganize freely, don't just append forever.
  A page that only grows by appending becomes unreadable; prune superseded content.
- Cross-reference with `[[page-name]]` (no `.md`, matches the existing memory
  system's link convention).
- **Source of truth for raw history**: this wiki is the primary reference going
  forward. The older auto-memory file (`nugget_ameyo_daily_sheet_workflow.md` in
  the Claude memory directory) has the full day-by-day narrative through
  2026-10-07 and is kept as a historical fallback — don't duplicate its blow-by-blow
  detail here, just the distilled, current-state facts.
- **Scratch working directories** (`oct*_refresh/` under the session scratchpad)
  remain ephemeral/per-session — they are NOT part of this wiki and get cleaned up
  by the harness. Canonical, reusable scripts (e.g. the Vet Followup build script,
  the Prediction Model day-by-day builder) should eventually live in
  `supertails-cx-analytics/scripts/` so they survive across scratch-dir churn —
  not yet migrated, flagged as a TODO in `daily-workflow.md`.

## Open TODOs for this wiki itself

- Migrate the reusable per-tab build/write scripts out of scratch dirs into
  `supertails-cx-analytics/scripts/`, parameterized by date instead of hardcoded
  per-day copies, so "copy the whole dir forward and sed the dates" stops being
  the refresh pattern.
- Decide whether Nugget ticket exports should be pulled via browser automation
  (Kriti documented the manual UI steps on 2026-10-08) instead of waiting for
  CSV attachments every day.
