# Canonical Metric Definitions

These are the exact rules used everywhere in the "Dashboard || Extra" workbook
(spreadsheet `1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw`). Any script that
re-implements one of these must match this exactly — drift between tabs is a bug.

## Core sets (copy verbatim into any new script)

- `DOCTORS` — 36 doctor email addresses (the full list lives in every build
  script; see any `0X_build_*.py` in a recent scratch refresh dir for the literal set).
- `LANGUAGE_KEYWORDS` = `{english, telugu, tamil, kannada, kanada, hindi}`
- `TRANSFER_TARGETS` = `DOCTORS | LANGUAGE_KEYWORDS`
- `TEAM10` — the 10 core agent emails (used for Team Talk Time / Avg Talk Time per Agent)
- `NAME_TO_EMAIL` — 12-agent roster (TEAM10 + Ganashree D + Daksha K), used for
  Agent Productivity-style breakdowns
- **Core 4 Booking Agents**: Mohammed Roohulla ("Rooh"), Alan Joel, Dhanush S,
  Abdul Rahman — the dedicated UCJ-Booking/Bangalore team.

## Phone/time helpers

- `norm_phone(p)`: strip non-digits, keep last 10.
- `hms_to_sec(s)`: `"HH:MM:SS"` string → seconds.

## Valid Lead

A nugget ticket counts as a Valid Lead iff:
- `channel_name == 'Unified Customer Journey'`
- `ticket_source == 'SOURCE_CHAT'`
- title does NOT contain "call back requested"
- title's `Verification:` field (regex `Verification:\s*([^|]*)`) is not `true`
- `categorize(row)` is `'Plain/D0'` or `'Pharmacy False'` (i.e. excludes Pharmacy
  True and Bangalore/UCJ-Booking)

## categorize(row) — the 6/7-way ticket classification

- `channel_name == 'UCJ Booking Campaigns'` → `'Bangalore'`
- `channel_name != 'Unified Customer Journey'` (and not Booking) → `None`
- `ticket_source == 'SOURCE_CALL'` → `'Source Call'`
- title contains "pharmacy" → `'Pharmacy True'` / `'Pharmacy False'` by the
  `Verification:` field
- title contains "prm call" → `'Plain/D0'`
- else → `'Other'`

**IMPORTANT**: the raw nugget export can contain a 3rd channel,
`"UCJ SC Chat Assistance"`, that is NOT part of this workbook's scope anywhere —
always filter to `channel_name in {'Unified Customer Journey', 'UCJ Booking Campaigns'}`
before treating "all tickets" as the analysis population (found & fixed 2026-10-04
while building Vet Follow-up Callback).

## classify(row) — Ticket Categories' 6-category taxonomy

Same title-parsing as `categorize()` but only for the two in-scope channels,
producing: `{PRM D0, Pharmacy False, Pharmacy True} x {Unified Journey, UCJ Booking}`.

## Connect

`User Talk Time >= 30s`, any agent, any-time phone match.
(Was `> 30s` until **2026-10-04**, when Kriti corrected it to `>= 30s` — this was
a cross-tab fix touching Main Dashboard, Ticket Categories, Valid Leads Log, and
Callback Adherence's `connected` flag. If you ever see `>30` instead of `>=30`
for this check in a script, it's stale — fix it.)

## Transfer Done

`Transfer To Agent/Phone` (lowercased) is in `TRANSFER_TARGETS`, **AND**
`Customer Talk Time - User Talk Time >= 30s`. No timing constraint relative to
the ticket (any-time phone match).

## Doctor Called

`User ID` (lowercased) is in `DOCTORS`, **AND** `User Talk Time >= 30s`, **AND**
the call happened **at or after** the ticket's own `created_at`
(timing constraint exists specifically to avoid attributing a call that predates
the ticket). Mutually exclusive with Transfer Done: a phone already in
`phone_transfer_done` never also counts as Doctor Called for the same ticket.

## Transfer Total

`Transfer Done` OR `Doctor Called`, deduplicated per ticket (i.e. Transfer Total
= count where either pathway is true, not a sum — a ticket can't be transferred twice).
Shown as **Transfer Done** and **Doctor Called** on their own separate lines too
(Main Dashboard always; Ticket Categories' TOTAL block only, added 2026-10-05) —
these two always sum exactly to Transfer Total/Transfer (abs).

Because Transfer Done is an any-time match, a date's Transfer Total **keeps
rising on every subsequent refresh** as more future days' Ameyo data gets folded
into the matching pool — this is expected ("recheck previous dates"), not a bug.
A freshly-tracked day will show an artificially LOW Transfer % for its first
1-3 refreshes for exactly this reason (confirmed via raw-event-count cross-check
on 2026-10-08 for Oct 7 — the raw doctor/transfer call volume was completely
normal, only the backward-matching hadn't had time to accumulate yet).

## AHT (Average Handling Time)

Average `User Talk Time` across phone-matched calls with `User Talk Time >= 60s`
only (sub-60s calls excluded from the average entirely, not zeroed).

## FRT (First Response Time)

Gap between a valid lead's `created_at` and the phone's first-ever Ameyo call
(`phone_first_call`), for leads created **9am-8pm** (`FRT Valid Leads (9am-8pm)`)
or **9am-8:45pm** (`FRT Valid Leads (9am-8:45pm)`, added 2026-10-04 and now the
ONLY FRT pair on Main Dashboard — the 9am-8pm version was removed the same day
at Kriti's request). Outlier gaps < -10000s (phone-reuse artifacts) are excluded.

## Vet Follow-up Callback (15-Day Repeat)

New tab added 2026-10-05, see `vet-followup.md` for the full definition and its
iterations (15-min-after-first-touch threshold, not calendar-day).

## Agent Productivity-style row conventions (where still live)

- "Avg Talk Time per Agent" = Team Talk Time (TEAM10) / Agents Available.
- "Attendance %" = adjusted days present / 25 expected working days (30 - 4
  weekly-off - 1 Ganesh Chaturthi holiday), capped at 100% display-wise for
  agents who exceed it (e.g. "room"/Mohammed Roohulla).
