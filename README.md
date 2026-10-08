# Supertails CX Analytics

Automated daily refresh pipeline + persistent knowledge base for Supertails'
call-center / lead-funnel dashboard.

**The live dashboard itself lives in Google Sheets** — this repo is the
documentation and process behind it, not the numbers themselves:
📊 [Dashboard || Extra](https://docs.google.com/spreadsheets/d/1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw/edit)

## What's automated

Four times a day (8am, 12pm, 5pm, 10pm), Claude:
1. Pulls a fresh ticket export from Nugget and a fresh call-detail export
   from Ameyo, via browser automation
2. Rebuilds all 8 tabs of the dashboard (Main Dashboard, Ticket Categories,
   Valid Leads Log, Vet Followup Callback + Dump, Prediction Model, Callback
   Adherence + Dump)
3. Cross-checks the numbers tie out
4. Logs what changed here, in [`wiki/log.md`](wiki/log.md), and pushes it

## Start here

➡️ **[wiki/index.md](wiki/index.md)** — the full wiki index: metric
definitions, the refresh workflow, tab-by-tab sheet structure, known bug
patterns, and the export-automation flow.

| Page | What's in it |
|---|---|
| [definitions.md](wiki/definitions.md) | Every canonical metric formula (Valid Lead, Connect, Transfer, AHT, FRT, Vet Follow-up) |
| [daily-workflow.md](wiki/daily-workflow.md) | The refresh process end to end, including the scheduling setup |
| [sheet-structure.md](wiki/sheet-structure.md) | Current layout of every tab in the live sheet |
| [bug-patterns.md](wiki/bug-patterns.md) | Recurring bugs and their fixes — check before trusting new scripts |
| [external-sources.md](wiki/external-sources.md) | Clinic Dashboard lookup + the Nugget/Ameyo export UI flows |
| [vet-followup.md](wiki/vet-followup.md) | The 15-Day Repeat metric's definition history |
| [log.md](wiki/log.md) | Chronological record of every refresh and change |

## Recent activity

See [wiki/log.md](wiki/log.md) for the full history — it's updated after
every refresh.

---
*This repo is kept in sync automatically — every refresh ends with a commit
and push, no manual step required.*
