# 6 · History and Decisions

[← Home](Home.md)

A chronological log of how the dashboard was built and *why* each choice was made. Dates are the working dates; "≈" means the day is
inferred from the sequence of files. Read this before "simplifying" anything — most oddities here have a reason.

## Phase 1 — First look (≈ Sep 24)

- **Started from one export** (3,364 UCJ chat tickets, Sep 1–24). Original ask: show `created_at, agent_name, agent_assigned_at, resolved_by,
  resolved_at, last_agent_assignment, agent_frt_response_at`, then compute FRT per agent.
- **FRT definition #1:** `agent_frt_response_at − agent_assigned_at` ("how fast does an agent reply once assigned").
  The export already contains `agent_frt_response_seconds`, but it measures from `created_at`, so it was **not** used (it includes all bot/queue wait).
- **Window:** only chats *assigned* 9:00 AM–8:45 PM (the day shift). Decision by the owner.
- **Negative FRTs discovered** (137 rows): the first reply predates the *latest* assignment. 133 were reassigned tickets. Decision: **exclude negatives** and
  say so, rather than silently clean them.
- **Per-agent, per-day, agent × day** tables built in chat. This exposed **Sep 11** (one agent, ~224 s average FRT on 63 tickets) as the cause of a team spike.
- **Resolution time** added: `resolved_at − agent_assigned_at`.
- **"Is there a bot-vs-manual transfer flag?"** Investigated. There is none (see [5-Data-and-Exports](5-Data-and-Exports.md)). Dropped.
- A **first HTML dashboard** ("Chat Ops Pulse", claude.ai artifact) was built and published. It was a Sep 1–23 snapshot and was **never updated again**.
  Hosting it locally was offered and declined.

## Phase 2 — Move to Google Sheets (≈ Sep 24–29)

- The owner shared a Google Sheet. The Drive connector could not see it, so access was set up with a **service account**
  (`kriti-project@kriti-project-505208…`), writing through `gspread`. The key already existed on the Mac from earlier work.
- Two tabs created: `Chat - Daily Summary` (metric × date) and `Chat - Agent Summary` (agent × date). The Daily Summary copies the layout of the
  existing "Main Dashboard" tab (metrics as rows, dates as columns).
- **Display format:** values > 60 s shown as minutes, then ≥ 60 min as hours (`7h 3m 27s`); "s" suffix added for seconds so units are never ambiguous.
  Consequence: time cells are **text**, not numbers (see [3-Sheet-Reference](3-Sheet-Reference.md)).
- **Month Average** column added before the first date; a duplicate trailing "Agent Avg" column was later **removed** (Oct 2).
- **Tickets Handled** blocks (per agent per day, month total, average per working day) added. "Per working day" divides by days the agent actually had
  tickets, so part-timers aren't diluted.
- **Four agents removed from the Day agent view** (Akshaya, Dhanush S, Farhan, Dr Sahithya). Decision: Team Average/Total were recomputed to cover **only the
  agents shown**, so the table is internally consistent. Daily Summary was deliberately left whole-team.
- A **Quick Comparison** summary table was added to the top of Daily Summary and then **reverted** at the owner's request.
- `Chat - Raw Dump (Sep 1+)` tab added so the ticket-level data lives in the workbook.

## Phase 3 — Off-business-hours (OBH) and the FRT redefinition (≈ Sep 26 – Oct 1)

- OBH added as a second block: first as 9 PM–9 AM, then corrected to **8:45 PM–9 AM** so it exactly complements the Day window (no 15-minute hole).
- **Shift-date rule:** an overnight chat is reported under the day the shift began.
- **FRT definition #2 (Daily Summary only):** measure from the time the chat first entered channel 7 (parsed out of the assignment-history columns). It
  cut negatives from 143 to 9 and exposed a real 3.5-hour hold on Sep 3 — but it was later **superseded**.
- **The turning point (owner asked "what about OBH… a chat at 1 am replied at 8 am?").** Measured from `created_at`, overnight chats waited 8–9 hours
  (55 tickets created 12–2 AM; 527 tickets overall with ≥ 4 h from created to first reply) — while the assignment-based FRT of the same tickets was a
  couple of minutes. Assignment-based FRT was **blind to the overnight wait**.
- **FRT definition #3 (current):** Daily Summary carries **two** FRTs — *Actual* (created → first reply) and *Day Starting* (assigned → first reply) — and **both
  blocks are bucketed by `created_at`**. Agent Summary keeps the assigned-based version and buckets by `agent_assigned_at`. (An intermediate state, where the Day and OBH
  blocks used different anchors and a ticket could appear in both, no longer exists.)

## Phase 4 — Keeping it current (Sep 25 → Oct 25)

- Each new export was merged onto the history. Export *shapes changed* (cumulative → daily → UCJ-only), so merging is always
  "de-dupe on `ticket_id`, newest wins".
- **Sep 29 was missing** until a full-September export arrived (Oct 2) and filled it.
- **Sep / Oct monthly average columns** replaced the single "Window Avg" when October data appeared.
- **Oct 14 — two problems found and fixed:** (1) local scratch files had been wiped, so the cumulative base was rebuilt from the sheet and the source CSVs; (2) the
  Raw Dump tab turned out to have been **missing `resolved_by` and `last_agent_assignment`** since the Sep 29 backfill — restored.
- API write quota (HTTP 429) hit once on Oct 8 → switched to **one batched formatting call per tab** and added automatic retry.

## Phase 5 — Consolidate and hand off (Oct 16 → Nov 2)

- **Oct 16:** everything folded into `update_chat_dashboard.py` with `--dry-run`. Design goals: (a) the **sheet itself is the base** so no local state can be lost;
  (b) a from-scratch rebuild path (`--base none`); (c) refuse to write if the base is missing a column; (d) overwrite the Raw Dump in place (never clear first).
  Both paths were tested: 0 differing cells against the live sheet.
- Oct 17 → Oct 25: routine updates with the script (each: dry-run → run → re-dry-run to confirm 0 diffs).
- **Oct 23:** a `CALL_Details…csv` telephony file was sent by mistake — caught by checking its columns; nothing written.
- **Oct 21:** the **Oct 18 gap** was detected (13.5 h silence at an export boundary) and later re-checked with a stronger test (see [Home](Home.md), open item 1).
- **Oct 26:** this wiki; the failing automation on the Mac found along the way (see [10-Related-Systems-and-Memory](10-Related-Systems-and-Memory.md)).
- **Oct 27:** Oct 26 added (cut at 23:59). **Oct 18 gap fixed** from two older exports, filtered to the 20 missing IDs. Added
  [11-Transfer-Rules](11-Transfer-Rules.md). Standing rule from now on: **every update ends with a wiki update** (both wikis if both halves changed). Main Dashboard "Agents Available" month columns switched to daily average.
- **Oct 28:** Oct 27 added (cut at 23:59): 38 Day chats, Day Starting FRT avg 37s. 6,009 tickets; re-dry-run 0 diffs.
- **Oct 29:** Oct 28 full + Oct 29 partial ("till today"): Oct 28 = 27 Day chats, Day Starting FRT avg 52s. 6,059 tickets; 0 diffs.
- **Oct 30:** Oct 29 completed (cut at 23:59): 44 Day chats, Day Starting FRT avg 41s. 6,108 tickets; 0 diffs.
- **Oct 31:** Oct 30 added (cut at 23:59). 6,166 tickets; 0 diffs. The chat update now runs as the last step of `refresh_all.sh` in the repo.
- **Nov 1:** full-October export applied. 6,202 tickets; 0 diffs. Oct 31 still partial (export ended 11:55).
- **Nov 2:** Oct 31 completed, October closed. November started: the script adds `Nov Avg` columns by itself. 6,301 tickets; 0 diffs.

## Decision register (short)

| Decision | Chosen | Alternative rejected | Why |
|---|---|---|---|
| FRT anchor | two FRTs: created-based and assigned-based | one assigned-based FRT | assigned-based hid a ~9 h overnight wait |
| Negative FRT | exclude and disclose | clip to 0 / ignore | negatives are artefacts of reassignment, not real speed |
| Day window | 09:00–20:45 inclusive | 9–9 | owner's shift definition |
| OBH window | exact complement | 9 PM–9 AM | left a 15-minute hole |
| OBH date | shift start day | calendar date | a 9 PM–9 AM shift spans midnight |
| Daily Summary bucket | `created_at` | `agent_assigned_at` | measures when the customer wrote |
| Agent Summary bucket | `agent_assigned_at` | `created_at` | measures an agent's own workload and speed |
| Team Average (Day agent view) | only agents shown | whole original team | table stays consistent with what's displayed |
| Time cells | display text | numeric seconds | readability for CX managers |
| Averages | ticket-weighted pooled | mean of daily values | avoids over-weighting quiet days |
| Missing day/blank | skip, never zero | count as 0 | zeros would drag averages down |
| Base data | the Raw Dump tab | local files | local files get wiped; the sheet is shared and durable |
| Updates | one script, dry-run first | ad-hoc code each time | removes drift and re-explanation |

- **2026-11-04** — Nov 3 added (`dbldlqb6er6c738p5m40.csv`, cut Nov 3 23:59): 6,420 tickets; Nov 3 Day 46 chats, Day Starting FRT avg 17 s / median 9 s, Actual FRT avg 8:29. Dry-run 0 differing cells. Same run as the call tabs (refresh_all.sh); a brief Clinic Dashboard outage affected only the bookings step, not chat.
- **2026-11-05** — Nov 4 added (`dbm0uf36er6c73bqdbng.csv`, cut Nov 4 23:59): 6,490 tickets; Nov 4 Day 53 chats, Day Starting FRT avg 33 s / median 20 s. Dry-run 0 differing cells.
- **2026-11-05 (midday)** — Nov 5 added as a part day (`dbm2k836er6c738ut300.csv`, to 12:19): 6,521 tickets; Nov 5 Day 26 chats so far. Dry-run 0 differing cells. Kriti's ticket exclusions do not touch chat tabs.
- **2026-11-06** — Nov 5 completed and Nov 6 added as a part day (`dbmn6fer7kms73ecmplg.csv`, to 11:54): 6,599 tickets; Nov 5 Day 70 chats, Nov 6 20 so far. Dry-run 0 differing cells. The call-tab bulk rules (Primary Disposition = Bulk; Nov 5 tickets closed by akshaya.r) do not touch chat tabs.
