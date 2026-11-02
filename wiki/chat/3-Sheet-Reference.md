# 3 · Sheet Reference

[← Home](Home.md)

Spreadsheet: **"Dashboard || Extra"** — <https://docs.google.com/spreadsheets/d/1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw>

## Tabs

The script owns exactly three tabs and rewrites them completely on every run. **Everything else belongs to other workflows — never touch it.**

| Tab | Owner | Size now |
|---|---|---|
| `Chat - Daily Summary` | **this dashboard** | 40 × 61 |
| `Chat - Agent Summary` | **this dashboard** | 73 × 62 |
| `Chat - Raw Dump (Sep 1+)` | **this dashboard** (and the script's base data) | 5,905 × 9 |
| Main Dashboard, Ticket Categories, Prediction Model, Valid Leads Log, Callback Adherence (+ Dump), Agent Productivity, Vet Followup Callback (+ Dump), Table6 Raw Dump (Oct), Booking Analysis | other work | not documented here |

## Cell values are text, not numbers (important if you build charts or formulas)

Times are written as display strings (`45s`, `6m 32s`, `7h 3m 27s`), so those cells **cannot be summed, averaged or charted**.
Ticket counts and "Avg / Working Day" are real numbers. The Raw Dump tab stores *everything* as text (ticket IDs and timestamps
included) so a read-back is lossless. If you need numeric seconds for charting, compute them from the Raw Dump columns with a formula, or
change `fmt_time` in the script.

## `Chat - Daily Summary` — whole team, one column per date

Frozen: top 2 rows and first 4 columns. Columns: `A` = metric name · then **one column per month** (`Sep Avg`, `Oct Avg`, … — the
OBH block also has `Aug Avg`) · then **one column per date**, oldest first. The Day and OBH blocks have different numbers of columns.

| Rows | Content |
|---|---|
| 1 | Block title: *Day Chat Messages (9 AM – 8:45 PM)* |
| 2 | Header: `Metric`, month columns, dates (`YYYY-MM-DD`) |
| 3 | Tickets (n) |
| 4 / 5 / 6 | Actual FRT Tickets (n) / Avg Actual FRT / Median Actual FRT |
| 7 / 8 / 9 | Day Starting FRT Tickets (n) / Avg / Median |
| 10 / 11 / 12 | Resolution Tickets (n) / Avg Resolution / Median Resolution |
| 13 | blank |
| 14 | Block title: *OBH Chat Messages (8:45 PM – 9 AM)* |
| 15 | Header |
| 16–25 | same ten metric rows as rows 3–12 |
| 26 | blank |
| 27–32 | notes (scope, formulas, time format, the "Aug" note) |

Shading: month columns of each block are shaded (Day: warm grey `0.93/0.93/0.88`; OBH: sand `0.95/0.92/0.85`); the header row and column `A` are bold.

## `Chat - Agent Summary` — agent × date, six blocks

Frozen: top 2 rows and first 4 columns. Each block is: **title row, header row, one row per agent, a Team row, one blank row** — so a block is
`agents + 4` rows tall. With 4 Day agents and 9 OBH agents the layout today is:

| Rows | Block |
|---|---|
| 1–7 | **Day** · Average FRT (agents rows 3–6, `Team Average` row 7) |
| 9–15 | **Day** · Average Resolution Time (agents 11–14, Team row 15) |
| 17–23 | **Day** · Tickets Handled (agents 19–22, `Team Total` row 23) |
| 25–36 | **OBH** · Average FRT (agents 27–35, Team row 36) |
| 38–49 | **OBH** · Average Resolution Time (agents 40–48, Team row 49) |
| 51–62 | **OBH** · Tickets Handled (agents 53–61, Team row 62) |
| 64–68 | notes |

Block columns: `A` agent · month columns (`Sep Avg`, `Oct Avg`; OBH also `Aug Avg`) · date columns. The **Tickets Handled** blocks use
`Sep Total`, `Oct Total`, … then an extra **`Avg / Working Day`** column, then the dates. Agents are sorted by total tickets (most first).
**These row numbers shift when the agent count changes** — find blocks by their title text, not by row number.

## `Chat - Raw Dump (Sep 1+)` — one row per ticket

Header row 1 (bold, frozen). Columns, in order:
`ticket_id · created_at · agent_name · agent_assigned_at · resolved_by · resolved_at · last_agent_assignment · agent_frt_response_at`.
Sorted by `created_at`. Only the **UCJ SC Chat Assistance** channel. Timestamps `YYYY-MM-DD HH:MM:SS`. Blank cells are real blanks.
`last_agent_assignment` is a long text like
`AgentID: … || Email: … || Name: … || ChannelID: 7 || ChannelName: UCJ SC Chat Assistance || AssignedAt: …`.

The tab is **grow-only**: the script overwrites it in place (it does not clear first), so a failed run can never leave it empty.

## Formatting the script applies

Bold titles/headers, shaded month columns and Team rows, frozen panes, and tab resizing (`rows = content + 5`). Column widths and number
formats are not set. Anything you format by hand on these three tabs is wiped on the next run.
