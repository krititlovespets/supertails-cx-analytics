# Daily Refresh Workflow

## STANDING INSTRUCTION (as of 2026-10-08): pull both exports yourself

**Kriti's explicit instruction, 2026-10-08: "so now every day your third step
should be to take both the downloads and update the dashboard and sheets."**
This supersedes waiting for her to attach CSVs. The daily routine is now:

1. Pull the **Nugget ticket export** via browser automation (see
   `external-sources.md` for the exact click-by-click flow) — set the date
   range to month-start → now, export, grab the CSV from the Gmail "Your
   Ticket Export is Ready" link.
2. Pull the **Ameyo CALL Details export** via browser automation (see
   `external-sources.md`) — Reports → Queue → Re-Run the latest "CALL Details"
   entry, edit End Date to now, tick CSV, Run, wait for SUCCESS, download.
3. Run the normal refresh pipeline (below) using those two freshly-downloaded
   files, exactly as if Kriti had attached them.
4. Push the same numbers to the **live dashboard artifact** (see
   "Live dashboard artifact" section below) — this is the thing Kriti actually
   looks at, so it must stay current every refresh, not just the Sheet.
5. Append the ingest entry to `log.md` (and update any other wiki page that
   changed), then **commit and push the wiki to GitHub** — see `schema.md` for
   the exact command and the Keychain-backed auth setup. This is now a
   standing instruction too (Kriti, 2026-10-08: "yes keep the wiki synced
   automatically") — every ingest ends with a push, not just a local edit.

Both flows are proven working (confirmed live 2026-10-08, see `log.md`).
If Kriti ever attaches files herself instead, use those — don't re-pull over
ones she just gave you.

## Live dashboard artifact (added 2026-10-08)

Kriti's explicit request, 2026-10-08: **"okay so can i get like somewhere i can
publish numbers and i dont want it to be sheet."** She wants to look at numbers
somewhere other than the Sheet. Built a Claude Artifact for this:

- **URL:** https://claude.ai/artifact/MGn5rtRUyLPn1v8g2P6bXo — "Supertails CX
  Pulse." Private artifact (owner + anyone Kriti shares it with).
- It is a plain HTML page using the Artifact `db` runtime capability — NOT a
  new spreadsheet, NOT a static snapshot. The page reads
  `db.doc("dashboard/latest")` on load and re-renders live; it also ships a
  real embedded fallback snapshot so it never opens empty.
- **Every refresh, after the Sheet is updated, write the same numbers to this
  doc** using the `ArtifactData` tool (load via `ToolSearch` first — it's
  deferred):
  ```
  ArtifactData(action: "set", url: "https://claude.ai/artifact/MGn5rtRUyLPn1v8g2P6bXo",
    collection: "dashboard", doc_id: "latest", data: { ...same shape as below... })
  ```
  Shape of the doc (all arrays are Oct-to-date, one entry per tracked day, same
  order as `dates`):
  ```json
  {
    "dates": ["2026-10-01", ...],
    "valid_leads": [393, ...],
    "transfer_pct": [30.8, ...],
    "connect_pct": [56.2, ...],
    "frt_avg": ["01:29:41", ...],
    "booking_pct": [4.7, ...],
    "aht": ["00:04:56", ...],
    "vet_repeat_pct": [2.1, ...],
    "sept": {"valid_leads": 12168, "transfer_pct": 22.6, "connect_pct": 57.1},
    "oct_to_date": {"valid_leads": 2673, "transfer_pct": 27.2, "connect_pct": 57.9},
    "updated_at": "<ISO timestamp of this refresh>"
  }
  ```
- Pull these exact numbers from the just-updated Main Dashboard tab (same
  source the Sheet itself used) — don't recompute separately, so the Sheet and
  the dashboard artifact can never disagree.
- **All arrays must stay the same length as `dates`, always** (found as a real
  bug 2026-10-09 when Oct9 was first tracked outside the Vet Follow-up run).
  The non-Vet-Follow-up runs don't recompute `vet_repeat_pct`, so when `dates`
  grows by a new day, `vet_repeat_pct` would otherwise be one entry short —
  that's an out-of-bounds read in `renderMetricGrid` (`d.vet_repeat_pct[last_i]`),
  not just a stale-looking number. **Always pad it** by carrying forward the
  previous day's value for the new date before writing, on any run that adds
  a new date column. The 8am run (which now owns Vet Follow-up — moved from
  5pm, see below, 2026-10-09) replaces the padded values with real ones the
  same day.
- Prefer `ArtifactData action: "update"` (merge) over `"set"` (replace) for
  routine refreshes — pass only the fields this run actually recomputed
  (Main Dashboard fields on 12pm/5pm/10pm runs) and the untouched ones
  (`vet_repeat_pct`, `sept`) are preserved automatically, so there's no risk
  of accidentally overwriting them with stale local data. Still needs
  `if_version` — `get` the doc first, pass its version back. `"set"` is only
  for a full rebuild (e.g. after an 8am run that touches everything).
- The page shows an alert callout when the latest day's Transfer % is still
  below 20% (the "freshly-tracked day opens low" pattern — see
  `definitions.md`); no action needed there, it's automatic from the data.
- If the artifact's `db` doc doesn't exist yet or a write fails, the page just
  keeps showing its last-known data — not a blocking failure, but still flag
  it to Kriti if a write genuinely fails repeatedly.

## Scheduled runs (set up 2026-10-08)

Kriti asked for this to run automatically at **8am, 12pm, 5pm, and 10pm every
day**. Set up as 4 recurring `CronCreate` jobs in that day's session. **Two
hard constraints to know about:**
- Cron jobs in this tool are **session-only** — they stop the moment the
  Claude session that created them ends (app closed, session killed, etc.).
  They are NOT a durable background service.
- They **auto-expire after 7 days** even if the session stays alive, and need
  to be recreated.

**Practical implication: whenever a new session picks up this project (or an
old one is still running a week later), check whether the 4 scheduled jobs are
still active and re-create them if not** — don't assume they're still running
just because they were set up once. There's no reliable way to check this
across sessions other than noticing the 8am/12pm/5pm/10pm refreshes have
stopped showing up in `log.md`, or Kriti mentioning the dashboard looks stale.

**2026-10-09: Vet Follow-up moved from the 5pm slot to the 8am slot** (Kriti:
"so like at 8 am update do the vet follow up") — see the "Vet Follow-up rows"
section below for the full rationale. When re-creating these 4 jobs after an
expiry, the 8am job is now the heavier one (Main Dashboard + Vet Follow-up)
and 12pm/5pm/10pm are Main-Dashboard-only — don't recreate them with the old
5pm-is-heavy assumption.

## What "update the dashboard" vs "update all the sheets" means

- **"update the dashboard"** (or "the dashboard and sheets") = the 3 core tabs:
  Main Dashboard, Ticket Categories, Valid Leads Log.
- **"update all the sheets"** = the above 3, plus Prediction Model, Callback
  Adherence, Callback Adherence Dump. (Vet Followup Callback + Dump are newer —
  ask whether they're included until Kriti confirms it's now the default.)
- Never assume a scope beyond what's asked; confirm/flag if ambiguous.

## Inputs each refresh

Either Kriti attaches two files, or (per the standing instruction above) pull
them yourself:
1. A **nugget export** (Freshdesk ticket CSV, `created_at`-keyed).
2. An **Ameyo export** (`CALL_Details_*.csv`, `Call Time`-keyed, `DD/MM/YYYY
   hh:mm:ss AM/PM` format).

**Before merging either file in:**
- Check each file's actual date coverage (don't trust the filename or what
  Kriti says it contains — on 2026-10-06 a file she described as "the whole
  Oct 5th data" turned out to contain zero Oct 5 rows).
- Compare ticket ID **sets** (not just counts) against the previously-used file
  for every already-tracked date, to catch channel drift
  (`Unified Customer Journey` → `UCJ Booking Campaigns` is the one recurring
  direction seen all week — usually 1-20 tickets per refresh, not alarming
  unless the count or direction changes).
- A day is "tracked" (gets its own column) once its data is substantially
  complete — rule of thumb: Ameyo row count in the same ballpark as other full
  days (~2000-2700), nugget row count ~700-830. A pull before ~6pm is usually
  still partial. **Exception**: Kriti can explicitly ask to track a partial day
  anyway (happened for Oct 5 and Oct 7) — then track it, but hold it OUT of
  Prediction Model's `banked_dates` until it's actually complete (folding a
  half-day count into the forecast average distorts it).

## Script pipeline

**As of 2026-10-08, the Main Dashboard pipeline scripts live in this repo**,
not a scratch dir: [`scripts/compute_main_dashboard.py`](../scripts/compute_main_dashboard.py)
+ [`scripts/write_main_dashboard.py`](../scripts/write_main_dashboard.py).
This replaces the old "copy the previous day's scratch dir forward" pattern
for Main Dashboard specifically — **the scratch-dir approach turned out to be
a real liability**: on 2026-10-08, asked to "update dashboard now," the
previous scripts were unrecoverable because they'd only ever lived in an
ephemeral per-session scratchpad that was already gone, forcing a full
from-scratch rebuild (see `log.md` for the full story, including the DOCTORS
list recovery). Keep using these persisted scripts going forward; extend them
rather than reverting to one-off scratch copies.

**Usage:**
```
python3 scripts/compute_main_dashboard.py <nugget_csv> <ameyo_csv> 2026-10-01 2026-10-02 ... 2026-10-08
python3 scripts/write_main_dashboard.py '{"2026-10-01": 5, ..., "2026-10-08": 3}'
```
The second arg to `write_main_dashboard.py` is that day's Booking Done counts
(from the Clinic Dashboard sheet, see `external-sources.md`) — pull it fresh
for any NEW date, but already-tracked dates' values can just be resent as-is
(Booking Done isn't an any-time-match metric, it doesn't drift like
Transfer/Connect do).

**What these two scripts do NOT yet cover** (left untouched by design —
don't guess at these, they need more than just the current month's exports):
- **Avg Talk Time per Agent / Agents Available** rows — need the TEAM10
  10-agent roster, which isn't persisted anywhere yet (only the 12-agent
  `NAME_TO_EMAIL` roster is derivable, from the "Agent Productivity" tab).
- **Vet Follow-up rows (20-22)** — the 15-day-repeat computation needs the
  FULL Sept1→latest ticket history (not just the current month's exports),
  per `vet-followup.md`. A day tracked via these two scripts will show blank
  Oct cells for these 3 rows until a fuller rebuild restores this.
- **Ticket Categories, Valid Leads Log, Prediction Model, Callback
  Adherence** tabs — entirely separate, not rebuilt by these scripts at all.

**The DOCTORS list** (36 internal staff emails, needed for Transfer
Done/Doctor Called/Transfer%) is **not embedded in this repo** (public repo,
internal PII) — it's read from `~/Documents/Supertails work/doctors_emails.txt`
(one email per line, outside git entirely). If that file is ever missing,
ask Kriti for the list again rather than guessing — getting this wrong
silently corrupts a real business metric.

## Vet Follow-up rows (20-22) — 8am run only (added 2026-10-08, moved to 8am 2026-10-09)

[`scripts/compute_vet_followup.py`](../scripts/compute_vet_followup.py) +
[`scripts/write_vet_followup.py`](../scripts/write_vet_followup.py) now cover
Main Dashboard rows 20-22 (Vet Follow-up Transferred / 15-Day Repeat /
Repeat %), day-by-day plus the Sept Avg / Sept16-30 Avg / Oct Avg columns —
see `vet-followup.md` for the exact rule these implement.

**Kriti's explicit instruction, 2026-10-08: only run this as part of one
scheduled refresh, not all 4** — originally the 5pm run, **moved to the 8am
run on 2026-10-09** ("so like at 8 am update do the vet follow up") so the
Vet Follow-up numbers are fresh earlier in the day instead of only from 5pm
onward. It needs a full Sept1→latest pull (both Nugget — two exports, since
Nugget's UI caps a single export at 1 month + 1 day — and Ameyo, one pull
covering the whole range worked fine), which is meaningfully slower (~5-10
min of export-queue waiting vs under a minute for the Oct-only pulls the
other 3 runs use) and a much bigger computation. The 12pm/5pm/10pm runs stay
Main-Dashboard-only, exactly as documented above. (Note: `write_vet_followup.py`'s
own module docstring still says "5pm" as of this edit — the code itself
doesn't care which cron slot calls it, so this is a documentation-only
mismatch, not a functional one; update the docstring next time that file is
touched for another reason.)

**Usage** (8am run adds this after the normal Main Dashboard steps):
```
# Nugget: two exports (Sept1 00:00 -> Oct1 00:00, then Oct1 00:00 -> now;
# the UI's "max 1 month and 1 day" range cap forces the split)
# Ameyo: one export, Sept1 00:00 -> now, worked in a single pull
python3 scripts/compute_vet_followup.py <nugget_sept_csv> <nugget_oct_csv> <ameyo_full_csv> 2026-10-08
python3 scripts/write_vet_followup.py
```
The last arg to `compute_vet_followup.py` is the latest tracked date — it's
used to decide whether a ticket's 15-day window is "Closed" (fully resolved)
or "Open" (still accumulating); see `vet-followup.md`'s scope caveat.

Push the resulting `repeat` percentage for the latest date into the
dashboard artifact's `vet_repeat_pct` array same as the other metrics — it
was being carried forward unrefreshed before this existed (see `log.md`,
2026-10-08).

1. `01_merge.py` — loads Sept (frozen) + latest nugget/Ameyo files, filters to
   tracked dates, pickles `merged.pkl`. **Always source every previously-tracked
   date fresh from the latest file** — never carry forward an old date's cached
   rows across merge generations (this caused a real Oct 1 valid-leads inflation
   bug, 407 vs correct 393, undetected for ~1 day in early October).
2. `00_fetch_booking_done.py` — pulls fresh "Booking Done" daily counts from the
   external Clinic Dashboard sheet (`1EyTmbBSkZMvL5JolKuo8xxOkguYGUKpTJTzlN68n5hM`,
   tab `Agent_Perf_V2`, row matched by columns A/B/C ==
   `('TOTAL (UCJ only)', 'UCJ', 'Appts created')`, date columns found by scanning
   row 4's `DD/MM/YYYY` headers — never hardcode row/column positions).
3. `02_build_main_dashboard.py` → `03_assemble_main_dashboard.py` →
   `04_write_main_dashboard.py` — per-date aggregates → grid → sheet write.
   `04_write...` does an in-place `ws.update()` (not `ws.clear()`), specifically
   to preserve the pink/red background highlighting — only safe when the row
   STRUCTURE hasn't changed; any row insert/remove needs an explicit
   color-reconciliation pass after (see `bug-patterns.md`).
4. `24_build_vet_followup.py` → `25_write_vet_followup.py` +
   `26_write_vet_followup_dump.py` → `28_add_vet_rows_main_dashboard.py` — Vet
   Followup Callback pipeline. `28_...` must run on EVERY Main Dashboard refresh
   (it lives outside the `02/03/04` pipeline and updates rows 20-22 in place,
   idempotently, by label lookup — not by hardcoded row number).
5. `05_build_ticket_categories.py` → `06_write_ticket_categories.py` — full
   `ws.clear()` + rewrite each time (no format-preservation concern).
6. `07_build_valid_leads_log.py` → `08_write_valid_leads_log.py` — full rebuild
   each time. Bump the `last_checked` literal date in the build script.
7. (if "all the sheets") `11b_build_prediction_model.py` →
   `11_write_prediction_model.py` — `banked_dates` is the one list to extend
   manually (not auto-generated); day-by-day table auto-adapts to `n_banked`.
8. (if "all the sheets") `09_build_callback_adherence.py` →
   `10_write_callback_adherence.py` — reads `merged.pkl` dynamically, no
   hardcoded date list, just works once `01_merge.py` is updated.

## Day-rollover checklist (when a NEW day gets tracked for the first time)

Every one of these needs the new date added — easy to miss since some of them
are NOT derived from an auto-generated list:
- `01_merge.py` — both date filters (nugget AND Ameyo)
- `00_fetch_booking_done.py`, `02_build_main_dashboard.py`,
  `03_assemble_main_dashboard.py`, `05_build_ticket_categories.py`,
  `28_add_vet_rows_main_dashboard.py` — their `dates = [...]` list
- `03_assemble_main_dashboard.py` — the `'oct': window('2026-10-01', ...)`
  upper bound specifically (NOT part of the auto-generated `dates` list)
- `24_build_vet_followup.py` — FOUR constants: `LATEST_TRACKED`,
  `WINDOW_END_SCOPE` (both = new latest date, 23:59:59), `ROLLING_15D_START`
  (shifts forward by the same number of days), `oct_agg = agg_window(...)`
  upper bound
- `11b_build_prediction_model.py` — `banked_dates` (only once the new day is
  actually complete, see above)

## Verification, every refresh

- Cross-check Valid Leads Log's per-date `created_date` counts against Main
  Dashboard's Valid Leads row, digit for digit.
- Cross-check Ticket Categories' `TOTAL (All Categories) -- Count` row.
- Spot-check that `transfer_done + doctor_called == transfer_total` for a date
  or two.
- After any Main Dashboard row insert/remove, re-verify background colors via
  the Sheets API (`userEnteredFormat.backgroundColor`), not just values.

## Google Sheets API rate limits

Writing to ~8 tabs back-to-back routinely trips `APIError 429` (write-quota per
minute). This is now routine, not a bug signal — wrap each write step in a
simple retry loop (`until ... grep -q DONE; do grep -q 429 ... && sleep 20-25
|| break; done`) rather than treating it as something to fix in the code.

## Service account

Credentials file: `/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json`.
**Never print/echo the `private_key` field.**
