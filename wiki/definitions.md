# Canonical Metric Definitions

These are the exact rules used everywhere in the "Dashboard || Extra" workbook
(spreadsheet `1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw`). Any script that
re-implements one of these must match this exactly — drift between tabs is a bug.

## Core sets (copy verbatim into any new script)

- `DOCTORS` — 36 doctor email addresses (the full list lives in every build
  script; see any `0X_build_*.py` in a recent scratch refresh dir for the literal set).
- `LANGUAGE_KEYWORDS` = `{english, telugu, tamil, kannada, kanada, hindi}`
- `TRANSFER_TARGETS` = `DOCTORS | LANGUAGE_KEYWORDS`
- `TEAM10` — confirmed 2026-10-11 to be exactly these 9 emails (the "10" in
  the name is historical/nominal, not a current literal count — validated by
  exact match against 7 known historical "Agents Available" values before
  being written anywhere):
  ```
  raisa.qlovespets@supertails.in        (Raisa Qureshi)
  hammad.shaikhlovespets@supertails.in  (Hammad Vaseem Shaikh)
  shazali.snlovespets@supertails.in     (Shazali Sanober)
  arjun.llovespets@supertails.in        (Arjun L)
  riddi.plovespets@supertails.in        (Riddi P)
  alan.jlovespets@supertails.in         (Alan Joel)
  dhanush.slovespets@supertails.com     (Dhanush S -- note .com not .in)
  abdul.rahmanlovespets@supertails.in   (Abdul Rahman)
  mohammed.rolovespets@supertails.in    (Mohammed Roohulla)
  ```
  Source: emails resolved from the Ameyo CALL Details CSV's own "User
  Name"/"User ID" columns (never guessed) after Kriti supplied the 11-name
  list (TEAM10 + Ganashree D + Daksha K) in chat, 2026-10-10/11.
- `NAME_TO_EMAIL` — 12-agent roster (TEAM10 + Ganashree D + Daksha K =
  `ganashree.dlovespets@supertails.in` + `daksha.klovespets@supertails.in`),
  used for Agent Productivity-style breakdowns
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

- **"Agents Available"** (Main Dashboard row 15) = count of distinct
  `TEAM10` emails with >=1 Ameyo call row on that date. Validated 2026-10-11
  by exact match against 7 known historical values.
- **"Avg Talk Time per Agent"** (Main Dashboard row 12) = sum of `User Talk
  Time` across all `TEAM10` agents' Ameyo calls that date, divided by
  "Agents Available" for that date (NOT divided by 10 or by headcount —
  divided by however many of the 9 actually had activity). Validated
  2026-10-11 the same way, exact match on all 7 known dates. Both are daily
  metrics computed straight from a single day's Ameyo file — no September
  history needed, unlike Vet Follow-up.
- "Attendance %" = adjusted days present / 25 expected working days (30 - 4
  weekly-off - 1 Ganesh Chaturthi holiday), capped at 100% display-wise for
  agents who exceed it (e.g. "room"/Mohammed Roohulla).
- **"Avg Talk Time per Agent" October Avg (col D) — corrected 2026-10-22/23**:
  the October-aggregate column is `sum(team talk time across ALL tracked
  days) / sum(daily active-agent counts across ALL tracked days)` — i.e.
  total team output ÷ total agent-days worked, NOT divided by a flat 9. The
  flat-9 version grows unbounded as more days accumulate (hit 47:44:17 by
  Oct22, an obvious sum masquerading as an average) — if you ever see that
  bug again, it's stale logic, fix it to the weighted version.
- **Table 6 AHT column** (added 2026-10-25): every call >=60s talk time on
  a ticket's phone (any caller, same ticket-level single-owner model as
  Connected/Transferred) attributed to the ticket's owner and averaged.
  Team total reconciles exactly with Main Dashboard row 11.

## Chat Volume / Chat FRT — self-computed from the Nugget export (2026-10-23/25)

The regular Nugget export (pulled every refresh anyway) includes a 3rd
channel, `UCJ SC Chat Assistance`, that's normally filtered out everywhere
else in this workbook — but it has everything needed to compute the
dashboard artifact's Chat Volume/Chat FRT tiles directly, without waiting
on the separately-maintained "Chat - Agent Summary" sheet tab (which lags
1-3 days on most refreshes). **This is now the default method** — only
fall back to reading the Chat sheet if the Nugget export is ever missing
these rows.

- Filter: `channel_name == 'UCJ SC Chat Assistance'` AND `agent_name` in
  the 4 day-shift chat agents — `Daksha K`, `Ganashree D`, `Salman Pasha`,
  `Shazali Sanober` (a different, smaller roster than Agent
  Productivity's 12-agent `NAME_TO_EMAIL` — don't conflate the two) — AND
  `agent_assigned_at`'s time-of-day within 9:00-20:45 (the "Day" shift,
  matching the sheet's own scope; excludes OBH 8:45pm-9am).
- **Chat Volume** = count of such tickets per day.
- **Chat FRT** = average of `agent_frt_response_at - agent_assigned_at` in
  seconds, for tickets with a valid FRT timestamp. **Not** the raw
  `agent_frt_response_seconds` field — that's computed from a different
  anchor and does not match the sheet's own numbers.
- Validated against 5 known-correct Chat-sheet days (Oct18-22): exact on 3,
  off by 1 ticket on Oct18, off by 3 on Oct21 — acceptable noise.
