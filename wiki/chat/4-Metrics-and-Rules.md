# 4 · Metrics and Rules

[← Home](Home.md)

Every definition below is what the script in this folder actually does. Seconds internally; displayed as `45s` / `6m 32s` / `7h 3m 27s`.

## The raw timestamps

| Column | Means |
|---|---|
| `created_at` | when the customer's message created the ticket |
| `agent_assigned_at` | when the ticket was assigned to its **current/last** agent |
| `agent_frt_response_at` | the **first agent reply** on the ticket (by *any* agent) |
| `resolved_at` | when the ticket was resolved |
| `last_agent_assignment` (+ `2nd_last` … `5th_last` in the full export) | text of the assignment history, including `ChannelID` and `AssignedAt` |

## Metrics

| Metric | Formula | Shown in | Counted when |
|---|---|---|---|
| **Actual FRT** | `agent_frt_response_at − created_at` | Daily Summary | both present and result ≥ 0 |
| **Day Starting FRT** | `agent_frt_response_at − agent_assigned_at` | Daily Summary | both present and result ≥ 0 |
| **Agent FRT** | same formula as Day Starting FRT, split per agent | Agent Summary | both present and result ≥ 0 |
| **Resolution time** | `resolved_at − agent_assigned_at` | both tabs | both present (no ≥ 0 filter) |
| **Tickets (n)** | tickets in the bucket that have an agent | Daily Summary | `agent_name` present |
| **"… Tickets (n)"** rows | how many tickets passed each metric's validity rule | Daily Summary | as above |
| **Tickets Handled** | every ticket assigned to that agent in the bucket, regardless of FRT/resolution validity | Agent Summary | `agent_name` present |
| **Avg / Working Day** | agent's total ÷ the number of distinct days they had tickets (whole period, **not per month**) | Agent Summary | — |

**Why two FRTs.** *Actual FRT* is the customer's experience, including any time the chat sat unassigned or queued. *Day Starting FRT* is the
agent's speed once the chat was handed to them. Reading them side by side separates a **hand-off problem** from an **agent-speed problem**
(see [7-Findings](7-Findings.md)).

**Why negatives are dropped.** On a reassigned ticket, `agent_frt_response_at` is still the *first* agent's reply, but `agent_assigned_at`
is the *latest* assignment — so the subtraction goes negative. Those rows are excluded from Day Starting FRT and Agent FRT (137 of 3,251 rows in
the first dataset were negative; 133 of those were reassigned tickets). Actual FRT cannot go negative this way.

## Averages, medians, months

- **Month / "Avg" columns are ticket-weighted**: every valid ticket in that month, pooled — **not** an average of the daily columns.
  The median is the median of those pooled tickets, not a median of daily medians.
- **Blank cell = no tickets that day.** Missing days are skipped, never counted as zero.
- **Team Average (Agent Summary)** = pooled average over the *agents shown in that block* (so the Day view's Team Average covers only 4 agents).
  **Team Total** = sum of the shown agents. In Daily Summary the "team" is everyone.
- Month columns are generated from the data (`Sep Avg`, `Oct Avg`, `Nov Avg`, …). OBH also shows `Aug Avg` — see below.

## Windows (Day vs OBH)

- **Day** = timestamp from `09:00:00` through `20:45:00` **inclusive**. **OBH** = everything else — an exact complement: no gap, no overlap.
  (An earlier version used 9 PM–9 AM and left 8:45–9 PM unassigned; that was corrected.)
- **Which timestamp decides the bucket:**
  - `Chat - Daily Summary` buckets by **`created_at`** — when the customer wrote. Day and OBH are a strict split of the same tickets.
  - `Chat - Agent Summary` buckets by **`agent_assigned_at`** — when that agent got the chat.
- **OBH date = shift start day.** A chat at 02:10 on Oct 5 is reported under **Oct 4** (the evening the shift began). Times at/after
  20:45 keep their own date. So an OBH column "Oct 4" covers Oct 4 20:45 → Oct 5 09:00.
- **The `Aug Avg` column in OBH** is only the tail of the shift that started Aug 31 (chats between 00:31 and 09:00 on Sep 1, before the data
  begins). It is a handful of tickets, not a real month.

## Who is counted

- Tickets with **no `agent_name`** are excluded everywhere (38 of 5,449 on Oct 15). They never reached an agent, so they have no assignment
  or FRT. This is a real blind spot: chats that were never picked up do not appear in any number.
- **Agent Summary → Day blocks hide** Akshaya, Dhanush S, Farhan, Dr Sahithya (at the owner's request; edit
  `EXCLUDE_FROM_DAY_AGENT_VIEW`). Any *new* agent appears automatically in the Day view.
- **Agent Summary → OBH blocks include everyone** who worked a night shift — the night roster is genuinely different. Dhanush S and Farhan have
  real overnight volume; Mohammad Rizwan and Mohammed Roohulla appeared with 1 ticket each; Akshaya first appeared in OBH in the Oct 18–20
  export.
- **Daily Summary has no exclusions.**
- Only the channel **`UCJ SC Chat Assistance`** is kept (see [5-Data-and-Exports](5-Data-and-Exports.md)).

## Display format

| Seconds | Shown as |
|---|---|
| ≤ 60 | `45s` (note: 60 → `60s`) |
| 61 – 3,599 | `6m 32s`; whole minutes drop the seconds: `6m` |
| ≥ 3,600 | `7h 3m 27s`; zero parts are dropped: `1h`, `1h 5m` |

## Data-quality rules baked in

1. De-duplicate on `ticket_id` — the **newest export wins**.
2. Drop rows with an unparseable `created_at`.
3. Sort by `created_at`.
4. Check every calendar day from 2026-09-01 to the last ticket has at least one ticket; warn if not.
5. Warn when a new file has zero overlap with existing data.
