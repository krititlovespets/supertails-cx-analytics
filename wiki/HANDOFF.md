# Supertails CX Analytics — Full Handoff / Onboarding Doc

**Purpose**: this one file is meant to be handed to a fresh Claude session (e.g. on
a new account) so it can pick up this engagement with zero re-explanation. Read
this whole file first, before doing anything else on this project.

Generated 2026-10-16. The live wiki at `wiki/` (same repo) and `wiki/log.md` have
more historical depth if a specific past decision needs tracing — this file is
the condensed, current-state version of everything in it plus the standing
behavioral rules that otherwise live in Claude's own memory system (which does
NOT transfer to a new account).

---

## 1. What this project is

A recurring CX/call-center analytics engagement for **Supertails**, a pet-care
company. Two recurring data sources get cross-referenced daily:
- A **Nugget** ticket export (Freshdesk-style support tickets)
- An **Ameyo** `CALL_Details` export (call-center dialer log)

The output lives in three places:
1. **Google Sheet "Dashboard || Extra"** — `1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw`
2. **Live dashboard artifact** — "Supertails CX Pulse",
   https://claude.ai/artifact/MGn5rtRUyLPn1v8g2P6bXo (private, Kriti's own —
   this is what she actually looks at day to day, NOT the sheet)
3. **A persistent wiki** at `~/Claude/supertails-cx-analytics/wiki/`, also
   pushed to the public GitHub repo `krititlovespets/supertails-cx-analytics`
   (process docs only — see the privacy rule in section 3)

## 2. Who Kriti is

Name: Kriti. Account email: `cx.managers26@gmail.com`. She directs detailed,
iterative data-filtering logic (channel/source exclusions, phone cross-linking,
talk-time thresholds) confidently, but writes fast and informally with typos —
read messages for intent, don't parse them literally, and confirm ambiguous
filter definitions rather than guessing silently. She will correct you
immediately and bluntly if something's wrong; take the correction, fix it, and
move on without over-explaining.

## 3. Standing behavioral rules — read before doing anything

These are hard-won, from real incidents in this engagement. Follow them exactly.

- **Never touch Gmail, Nugget, or Ameyo via browser automation without live,
  explicit permission for that specific instance.** A standing instruction from
  an earlier session, a scheduled routine, or even her own prior "go ahead" in
  the same conversation does **not** carry over to the next action — ask again
  each time before navigating into or acting on any of these three accounts.
  If she says "wait," "no," or sends anything in caps, that is an immediate hard
  stop: zero further browser tool calls (not even closing a tab) until she
  explicitly says to proceed again. (Real incident, 2026-10-10: she revoked
  live permission mid-action with "YOU WILL NOT TOUICH MY BROSER BROWSER" even
  after answering "go ahead" moments earlier.)
- **No scheduled/automatic refreshes.** An earlier "pull it yourself every day"
  instruction (2026-10-08) was explicitly revoked on 2026-10-10 ("lets do it
  when i ask you to do" / "please stop all of this"). All cron jobs were
  deleted. Only refresh when she asks in chat or attaches files — don't
  proactively pull data or recreate scheduled jobs.
- **No unsolicited downloadable files.** Default to in-chat markdown
  tables/text for any result. Only produce an actual file (CSV, PDF, HTML) when
  she explicitly asks for one ("give me a CSV," "downloadable format," etc.).
- **No unsolicited writes to the Sheet or dashboard.** A question about the
  data ("how many X," "why does Y happen") is answered in chat. Only write a
  new metric/row/tab into the Sheet, or push new data to the dashboard
  artifact, when she explicitly says to add/update it there. The *recurring
  daily refresh itself* (when she asks for "update dashboard and sheets") is a
  standing, already-granted exception — keep doing the already-established
  tabs/rows as documented in section 7-8 without re-asking each time.
- **The dashboard stays private.** Never publish the "Supertails CX Pulse"
  artifact (or any version showing real business numbers) to the public
  GitHub repo/Pages site. That repo is public *only* for the process-docs wiki
  (definitions, workflow, bug patterns) — never for actual metric values. The
  live dashboard stays the private Claude Artifact, shareable only with people
  she explicitly chooses via its Share menu.
- **Firebase/self-hosting is paused, not rejected.** She tried self-hosting the
  dashboard (Firebase Hosting+Auth+Firestore) on 2026-10-08, hit Google Cloud
  onboarding friction (org permission 403 on her work account, then a
  billing/ToS gate on her personal account), and said "leave it let work on
  this artifact." Don't re-propose Firebase/Supabase/self-hosting unprompted —
  if she brings it up again, pick up from `console.firebase.google.com`
  directly (skips the CLI's gate) rather than restarting the evaluation. An
  orphaned half-created GCP project (`supertails-cx-pulse`) exists from the
  first attempt and can be ignored or deleted.
- **Never print/echo the service account's `private_key` field**, anywhere —
  not in chat, not into a memory/wiki file.
- **The DOCTORS list (36 internal staff emails) is never embedded in any
  committed script** — this repo is public. It's read at runtime from
  `~/Documents/Supertails work/doctors_emails.txt` (outside git entirely, one
  email per line). If that file is ever missing, ask Kriti for the list again
  rather than guessing.

## 4. Key IDs, URLs, and file locations

| What | Value |
|---|---|
| Google Sheet ("Dashboard \|\| Extra") | `1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw` |
| Service account credentials | `/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json` |
| Service account email | `kriti-project@kriti-project-505208.iam.gserviceaccount.com` |
| DOCTORS list file (36 emails, outside git) | `~/Documents/Supertails work/doctors_emails.txt` |
| Project repo (this wiki + scripts) | `~/Claude/supertails-cx-analytics/` |
| GitHub repo (public, process docs only) | `krititlovespets/supertails-cx-analytics` |
| Live dashboard artifact ("Supertails CX Pulse") | https://claude.ai/artifact/MGn5rtRUyLPn1v8g2P6bXo |
| Clinic Dashboard sheet (Booking Done source, external team) | `1EyTmbBSkZMvL5JolKuo8xxOkguYGUKpTJTzlN68n5hM`, tab `Agent_Perf_V2` |
| UCJ Incentive Eligibility Criteria — living doc | https://claude.ai/artifact/LDXMmvqtbbPDHrmq4eHqCc |
| UCJ Incentive Eligibility Criteria — standalone HTML | https://claude.ai/artifact/RSEp1sK3MJqq919ncPqwXe |

## 5. Roster

**TEAM10** (9 emails, name is historical/nominal — not a literal count of 10):
```
raisa.qlovespets@supertails.in        Raisa Qureshi
hammad.shaikhlovespets@supertails.in  Hammad Vaseem Shaikh
shazali.snlovespets@supertails.in     Shazali Sanober
arjun.llovespets@supertails.in        Arjun L
riddi.plovespets@supertails.in        Riddi P
alan.jlovespets@supertails.in         Alan Joel
dhanush.slovespets@supertails.com     Dhanush S  (.com, not .in — the one exception)
abdul.rahmanlovespets@supertails.in   Abdul Rahman
mohammed.rolovespets@supertails.in    Mohammed Roohulla
```

**12-agent roster** (`NAME_TO_EMAIL`) = TEAM10 + Ganashree D
(`ganashree.dlovespets@supertails.in`) + Daksha K
(`daksha.klovespets@supertails.in`). A 13th name, **Nikhil Singh**
(`nikhil.singhlovespets@supertails.com`), appears in some agent lists but has
confirmed **zero activity** all through October — verified genuine (zero
matching Ameyo rows), not a matching bug. Excluded from all per-agent tables by
Kriti's explicit request.

**3-team incentive split** (set up 2026-10-15/16, see section 10):
- **Transfer team**: Raisa Qureshi, Hammad Vaseem Shaikh, Shazali Sanober, Arjun L, Riddi P
- **Booking team**: Alan Joel, Dhanush S, Abdul Rahman, Mohammed Roohulla
- **Chat team**: Ganashree D, Daksha K
- Plus two oversight roles: **TL** and **SME** (flat team-level gates, not per-agent)

## 6. Canonical metric definitions

These are the *current, correct* rules — any older memory or scratch script
disagreeing with this section is stale; this section wins.

**Core sets**:
- `LANGUAGE_KEYWORDS` = `{english, telugu, tamil, kannada, kanada, hindi}`
- `DOCTORS` = the 36-email file (section 3/4) — loaded at runtime, never embedded
- `TRANSFER_TARGETS` = `DOCTORS | LANGUAGE_KEYWORDS`
- `norm_phone(p)`: strip non-digits, keep last 10
- `hms_to_sec(s)`: `"HH:MM:SS"` → seconds

**In-scope channels**: `{Unified Customer Journey, UCJ Booking Campaigns}` only.
The raw Nugget export can contain a 3rd channel, `UCJ SC Chat Assistance` — it
is **never** part of this workbook's scope anywhere; always filter it out.

**`categorize(row)`** (6/7-way classification):
- `channel_name == 'UCJ Booking Campaigns'` → `'Bangalore'`
- `channel_name != 'Unified Customer Journey'` (and not Booking) → `None`
- `ticket_source == 'SOURCE_CALL'` → `'Source Call'`
- title contains "pharmacy" → `'Pharmacy True'` / `'Pharmacy False'` by the
  `Verification:` field (regex `Verification:\s*([^|]*)`)
- title contains "prm call" → `'Plain/D0'`
- else → `'Other'`

**Valid Lead** — a Nugget ticket counts iff:
- `channel_name == 'Unified Customer Journey'`
- `ticket_source == 'SOURCE_CHAT'`
- title does NOT contain "call back requested"
- title's `Verification:` field is not `true`
- `categorize(row)` is `'Plain/D0'` or `'Pharmacy False'`

**Connect**: `User Talk Time >= 30s`, any agent, any-time phone match (was
`>30s` until 2026-10-04 — if you ever see the old `>` instead of `>=`, it's stale).

**Transfer Done**: `Transfer To Agent/Phone` (lowercased) is in
`TRANSFER_TARGETS`, **AND** `Customer Talk Time − User Talk Time >= 30s`.
Any-time phone match, no timing constraint relative to the ticket.

**Doctor Called**: `User ID` (lowercased) is in `DOCTORS`, **AND**
`User Talk Time >= 30s`, **AND** the call happened at or after the ticket's own
`created_at`. Mutually exclusive with Transfer Done (checked first).

**Transfer Total**: Transfer Done **OR** Doctor Called, **deduplicated per
ticket** (not summed — a ticket can't be transferred twice).

**Important drift pattern**: because Transfer Done/Doctor Called/Connect are
all any-time phone matches, a date's numbers **keep rising on every subsequent
refresh** as more future Ameyo data gets folded into the matching pool. A
freshly-tracked day will show an artificially LOW Transfer%/Connect% for its
first few refreshes — this is expected, not a bug. Don't "fix" a low fresh-day
number; just expect it to climb.

**AHT**: average `User Talk Time` across phone-matched calls with
`User Talk Time >= 60s` only (sub-60s calls excluded entirely, not zeroed).

**FRT**: gap between a valid lead's `created_at` and the phone's first-ever
Ameyo call, for leads created 9am–8:45pm. Outlier gaps < −10000s (phone-reuse
artifacts) excluded.

**Vet Follow-up / 15-Day Repeat** (Main Dashboard rows 20-22; currently stale,
see section 9): population = ALL tickets in the two in-scope channels (not just
Valid Leads). Window = `[created_at, created_at+15 days]`. "Transferred" = ≥1
qualifying touch in that window. "15-Day Repeat" = a touch lands **more than 15
minutes after the first touch** in the window — NOT `touch_count>=2` (inflates
wildly from same-session multi-row artifacts) and NOT "next calendar day"
(too coarse). Needs a full Sept1→latest pull to compute (see section 9).

**Agents Available** (Main Dashboard row 15) = count of distinct TEAM10 emails
with ≥1 Ameyo call that date.
**Avg Talk Time per Agent** (row 12) = sum of TEAM10 `User Talk Time` that date
÷ Agents Available for that date (not divided by 9 flat — by however many were
actually active). Both are daily-only, computable from a single day's Ameyo
file, no history needed — but **not yet wired into `compute_main_dashboard.py`**,
still computed by hand each refresh (see section 8).

**Agent Productivity "Table 6" — single-owner ticket-level model** (built
2026-10-15, the current/best version): each October valid-lead ticket is
credited to exactly ONE agent (no cross-agent double-counting): if transferred,
the agent credited by the Transfer Total rule; otherwise, the LAST agent who
called that phone. "Connected" = ticket-level fact (≥1 call from **anyone**,
any time, ≥30s — same basis as Main Dashboard's Connect, NOT limited to the
owner's own calls — an earlier version of this script had that bug, fixed
2026-10-15). Because every ticket has exactly one owner, summing
Dialled/Connected/Transferred across all agents reproduces team-level numbers
almost exactly (small gap = valid leads with zero call from a roster agent).
**A simple unweighted average of the per-agent % column will never equal the
team %** — that's real math (weighted vs. simple average), not an error; if
asked "why doesn't X match," check this before assuming a bug.

## 7. Sheet structure (tab-by-tab)

**Never hardcode a tab name without calling `sh.worksheets()` first** — Kriti
renames tabs directly in the UI. Current tabs (grows over time):

- **Main Dashboard** — Metric | Sept Avg | Avg(Sept16-30) | October Avg | blank |
  day-by-day (Sept1→latest). Row order: Valid Leads(2), Transfer Total(3),
  **Transfer%**(4, pink), Transfer Done(5), Doctor Called(6), **Abs Transfer To
  Do**(7, red), Connect(8), **Connect%**(9, pink), Connect Needed(10),
  AHT(11), Avg Talk Time per Agent(12), FRT Valid Leads(13), **FRT Avg**(14,
  pink), Agents Available(15), UCJ Bangalore Customer(16), Booking Done(17),
  **Booking%**(18, pink), Bookings Needed(19), Vet Transferred(20), Vet 15-Day
  Repeat(21), Vet Repeat%(22). Column D = October Avg (full-month aggregate —
  recompute this on every refresh, it silently goes stale if a scoped run skips it).
- **Ticket Categories** — NOTE row, header, TOTAL (All Categories) block (9
  metrics incl. Transfer Done/Doctor Called), then 6 category blocks ×
  `{PRM D0, Pharmacy False, Pharmacy True} × {Unified Journey, UCJ Booking}`.
  Full `ws.clear()` + rewrite every refresh.
- **Valid Leads Log** — one row per Valid Lead ticket (~17,500+ rows and
  growing). Columns: ticket_id, created_at, created_date, agent_name, title,
  verification_subline, user_phone, found_in_ameyo, transfer_done,
  doctor_called, connect_match, last_checked. **Append-only** — never rebuild
  from scratch (would duplicate); always check already-logged ticket_ids
  before appending new ones.
- **Prediction Model** — ASSUMPTIONS / DATA BASIS / ACTUAL-banked block /
  30%-target block / day-by-day table (`Actual` for banked days, `Forecast
  Target` flat quota for remaining days). Reads live from Main Dashboard —
  just extend `banked_dates` and rerun.
- **Callback Adherence** / **Callback Adherence Dump** — full rebuild every
  refresh from frozen July/Aug/Sept files + latest Oct merge. Has a built-in
  validation step (known July/Aug/Sept counts must match exactly before
  writing) — if it fails, investigate the specific mismatch (usually a single
  newly-surfaced ticket with a retroactive callback date) before overriding
  the check, don't just disable it.
- **Vet Followup Callback** / **Dump** — currently stale, see section 9.
- **Agent Productivity** — 6 stacked tables (historical Tables 1-5 plus the
  current Table 6, section 6). A tab with stacked tables: never search for a
  row by label alone, always scope to start after that table's own header row.
- **Table6 Raw Dump (Oct)** — per-ticket audit dump backing Table 6 (owner,
  transfer-via, connected, transferred per ticket). Not refreshed every single
  day unless asked — supplementary, not part of the core pipeline.
- **Chat - Daily Summary / Chat - Agent Summary / Chat - Raw Dump** — a
  separate chat-platform data source (not Nugget/Ameyo). "Chat - Agent
  Summary" has an "Average FRT — Agent x Date [Day 9AM–8:45PM]" table (Team
  Average row) and a "Tickets Handled — Agent x Date" table (Team Total row) —
  these feed the dashboard's Chat Volume/Chat FRT metrics. This sheet tab lags
  by a day or two sometimes; check its last date column before assuming it's current.

## 8. The actual current refresh workflow

(The wiki's `daily-workflow.md` describes an older numbered-script pipeline
`01_merge.py`→`28_...py` living in scratch dirs — that's **legacy**, superseded
by what's below. Don't follow the old numbered list.)

When Kriti attaches a fresh Nugget CSV + Ameyo CSV and asks to update:

1. **Check each file's actual date coverage** (`created_at` / `Call Time`
   columns) — don't trust the filename or what she says is in it. A file can be
   a superset of a previous pull (more complete for the same days) or cover a
   narrower/different range than expected.
2. **Merge with the previous day's merged file**: keep old rows for dates
   fully outside the new file's range, take the new file's rows entirely for
   any date it covers (the new file is always fresher/more complete for
   overlapping dates) — write a new `merged_oct1_N_nugget.csv` /
   `_ameyo.csv` in `/tmp`.
3. **Sanity-check for drift** on any already-tracked date before trusting a
   count change: if Day X's count changed from the last refresh, check whether
   it's (a) a genuine completion (day was partial before, now fuller — expected
   and fine) or (b) a real bug (wrong file, wrong filter). Both have happened;
   always check which one before writing.
4. Run `scripts/compute_main_dashboard.py <nugget> <ameyo> <date1> <date2>
   ...` (full Oct1→latest range every time, so October Avg recomputes
   correctly) then `scripts/write_main_dashboard.py '<booking_done_json>'`
   (Booking Done per day — pull fresh for new dates from the Clinic Dashboard
   sheet per section 4, already-tracked dates can resend their existing values).
5. **By hand** (not yet scripted): compute and write Avg Talk Time per Agent
   (row 12) / Agents Available (row 15) for any new or corrected date, and the
   October Avg for both — using the TEAM10 roster and the formula in section 6.
   **Always verify the column letter against the live header before writing** —
   a past column-offset mistake once overwrote real September data.
6. For Ticket Categories / Valid Leads Log / Callback Adherence / Prediction
   Model / Agent Productivity Table 6: there's no single canonical script yet
   for each — the working pattern is to take the most recent dated copy under
   `scratchpad/octNN_refresh/` (e.g. `fill_ticket_categories_octNN.py`,
   `append_valid_leads_log_octNN.py`, `build_callback_adherence.py`,
   `build_write_prediction_model.py`), copy it forward, and `sed`/edit the file
   paths and date constants for the new day. These scripts live in the
   session's ephemeral scratchpad, not in the repo's `scripts/` — if a fresh
   session has no scratchpad history, rebuild the logic from this doc's
   section 6 definitions rather than guessing at an old script's exact shape.
7. **Vet Follow-up (rows 20-22)**: needs a FULL Sept1→latest Nugget pull (two
   exports — Nugget's UI caps a single export at 1 month+1 day) plus a full
   Ameyo pull. If this fresh full-history data isn't available in a given
   refresh, **skip Vet Follow-up and say so explicitly** rather than guessing —
   this has been skipped multiple times recently (see section 9) and is
   currently stale.
8. **Push the same numbers to the dashboard artifact**: pull the final values
   straight from the just-updated Main Dashboard (never recompute separately —
   Sheet and artifact must never disagree), then:
   - `ArtifactData(action:"get", ...)` the `dashboard/latest` doc to get its
     current `version`
   - `ArtifactData(action:"update", ..., if_version:<that version>, data:{...})`
     with only the fields that actually changed (merge, not replace)
   - Edit the local HTML file's `FALLBACK` JS object to match (so the artifact
     never opens empty even before the live `db` read resolves)
   - `Artifact(action:"publish", url:<the artifact URL>, file_path:<local html>)`
   - **All arrays in the `dashboard/latest` doc must stay the same length as
     `dates`** — pad any field not recomputed this run by carrying forward its
     last value, never leave an array short (causes an out-of-bounds read in
     the page's render code).
9. Append one line to `wiki/log.md`, update any wiki topic page that changed,
   then `git add -A && git commit && git push` the wiki (standing instruction —
   do this as the last step, not a separate manual ask). Only `wiki/` and
   `.gitignore` are tracked in git — never commit credentials/CSVs/raw data.

**Google Sheets API rate limits**: writing to ~8 tabs back-to-back routinely
hits `APIError 429`. Routine, not a bug — just retry with a short backoff.

## 9. Known current gaps (as of 2026-10-16)

- **Vet Follow-up (Main Dashboard rows 20-22) is stale** — hasn't been rebuilt
  since the one-time Sept-data run earlier in this engagement, because recent
  refreshes haven't had a fresh Sept1→latest Nugget pull available. Flag this
  explicitly whenever asked to "update everything" — don't silently skip it
  without saying so.
- **Chat Volume / Chat FRT** (dashboard artifact's "Other metrics" tiles) come
  from the "Chat - Agent Summary" sheet tab, which has its own lag — check its
  last date column each time rather than assuming it's caught up to Main
  Dashboard's latest tracked date.
- **"Table6 Raw Dump (Oct)"** audit tab is not refreshed as part of the core
  pipeline — only rebuild it if specifically asked.

## 10. Incentive scheme (built 2026-10-15/16)

Two artifacts hold the current incentive policy (criteria only, no live
numbers mixed in — see URLs in section 4):
- A living Claude Doc (collaboratively editable)
- A standalone styled HTML page (downloadable/shareable, green pastel theme)

**Structure**: 3 agent teams (Transfer / Booking / Chat, roster in section 5),
each scored on **two independent criteria that add up** (not OR'd into one
shared ladder — that was tried and explicitly reversed): the common
Transfer% ladder, plus one team-specific metric (AHT for Transfer team,
Booking% for Booking team, FRT for Chat team). Max ₹6,000/agent/month
(₹3,000 + ₹3,000).

**Bands** (each tier's threshold includes a 90%-of-target leniency on
Transfer%/Booking% only — NOT on AHT/FRT):
- Transfer%: 27–35.9%→₹1,000, 36–44.9%→₹2,000, ≥45%→₹3,000
- AHT (more talk time is better): 4–4.9min→₹1,000, 5–5.9min→₹2,000, ≥6min→₹3,000
- Booking% (= Appts Created from Clinic Dashboard ÷ Bangalore leads called by
  that agent): 5.85–6.29%→₹1,000, 6.3–6.74%→₹2,000, ≥6.75%→₹3,000
- FRT (Business Hours, faster is better): 20.1–30s→₹1,000, 15.1–20s→₹2,000,
  ≤15s→₹3,000

**Eligibility gate**: 90%+ attendance required for ANY payout. Attendance% =
days worked (≥1 logged Ameyo call) ÷ expected working days (calendar days in
the month to date, minus week-offs — the exact week-off count has been
adjusted during discussion, confirm the current number with Kriti rather than
assuming).

**TL** and **SME** are separate, flat (non-tiered) team-level gates, not
per-agent: TL = Booking%(team) ≥6.5% → ₹7,000 flat. SME = Connect%(team) ≥60%
**AND** Transfer%(team) ≥30% → ₹6,000 flat (both conditions required for the
one payout). Miss the gate → ₹0, no partial credit.

**Booking% per-agent data source** (discovered 2026-10-15): the Clinic
Dashboard sheet (`1EyTmbBSkZMvL5JolKuo8xxOkguYGUKpTJTzlN68n5hM`, tab
`Agent_Perf_V2`) DOES have per-agent rows (search columns A/B/C for the
agent's email + `UCJ` + `Appts created` — row numbers shift, search don't
hardcode), not just the team TOTAL row. Row position for a given agent isn't
fixed — find it each time by scanning column A for the agent's email.

## 11. Where to look for more

- `wiki/index.md` — the original wiki's own index (topic pages:
  `definitions.md`, `daily-workflow.md`, `sheet-structure.md`,
  `bug-patterns.md`, `external-sources.md`, `vet-followup.md`, `schema.md`)
- `wiki/log.md` — full chronological ingest log, append-only, ~1250 lines —
  useful for tracing *how* a specific past decision was reached, not needed
  for day-to-day work
- `wiki/bug-patterns.md` — 11 recurring Sheets-API/script bug classes (formula
  misreads on `=`-prefixed cells, stale formatting after row shifts, percent
  auto-format, batching format calls, 24h duration wraparound, `ws.resize()`
  before writing, multi-table row search, script-vs-patch drift, orphaned
  trailing rows on grid shrink, verifying file contents not just descriptions,
  stale-snapshot carryover across merges) — check new scripts against this
  before trusting them
- `wiki/external-sources.md` — exact click-by-click manual UI flows for
  pulling Nugget and Ameyo exports via browser (only use with live permission
  per section 3)
