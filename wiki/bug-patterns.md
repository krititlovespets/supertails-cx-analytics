# Recurring Bug Classes & Fixes

Check new scripts against this list before trusting them.

## 1. `"="` prefix misread as a formula
Any cell value starting with `=` (e.g. `"=== TITLE ==="`) gets interpreted as a
Sheets formula on `USER_ENTERED` write. Fix: detect and rewrite those specific
cells with `value_input_option='RAW'` after the main write.

## 2. Stale number format after a row shift
`ws.clear()` does NOT clear per-cell formatting (background color, number
format) — it stays pinned to the old ROW INDEX. Any row insert/remove/reorder
via list-splice + rewrite needs an explicit post-edit pass that re-checks and
re-applies the correct background color / number format by CONTENT's new
position, not by assuming format traveled with the content. Always verify via
the Sheets API (`userEnteredFormat.backgroundColor`) after, don't just trust the write.

## 3. Percent-row auto-detection
Don't detect "is this a percent row" by checking if the LABEL contains `%`
(`"Absolute Transfer To Do (30% of...)"` has `%` in the label but is a plain
integer). Correct fix: check the row's own VALUE — `row[1].strip().endswith('%')`.
Also: Sheets' default percent auto-format is 2-decimal ("25.80%") — always
explicitly force `{'type':'PERCENT','pattern':'0.0%'}` on any percent cell, don't
rely on Sheets' auto-detected format.

## 4. Batching format calls by column span
When fixing many cells with the same format (e.g. all percent cells in a
column), do NOT batch by `min(row)..max(row)` per column — that span can include
unrelated plain-number rows sitting between two percent rows, corrupting them
(a real incident: `12260` got displayed as `"1226000.0%"`). Group into
CONTIGUOUS row runs only.

## 5. 24h-duration wraparound
Duration-formatted cells (HH:MM:SS, can exceed 24h for big totals) need
`numberFormat: {type:'TEXT'}` + a RAW rewrite proactively, or Sheets silently
wraps a >24h duration.

## 6. `ws.resize()` before writing beyond provisioned width/height
`APIError: ...exceeds grid limits` → always `ws.resize(rows=..., cols=...)` first.

## 7. Multi-table tabs: never search for a row by name alone
A tab with stacked tables (e.g. old Agent Productivity's Table 1/2/3) can repeat
the same label (agent name) in multiple tables. Always scope the search to
start after that specific table's own header row index.

## 8. Reusable-script-vs-one-off-patch drift (3 confirmed incidents)
A row/column added via a one-off manual edit (not folded into the actual
reusable build/assemble/write script) silently disappears — or worse, gets
duplicated — the next time that script is copied forward and rerun.
Confirmed incidents: "Connect Needed" row (twice), the Vet Follow-up rows on
Main Dashboard. **Any one-off addition must either get folded into the
pipeline's own script, or become a permanently-tracked EXTRA step that's
documented and re-run every refresh** — see `daily-workflow.md`'s pipeline list.

## 9. Grid shrink leaving orphaned trailing rows
`ws.update()` only touches the range it's given. If a grid SHRINKS (fewer rows
than the previous write), the old trailing rows are left untouched with stale
content (not cleared). After any shrink, `ws.batch_clear()` the orphaned range
(old row count down to new row count + 1) before trusting the sheet matches the
new grid.

## 10. Verify file contents, not just what the user says is in them
On 2026-10-06, a file Kriti described as containing "the whole Oct 5th data"
actually had zero Oct 5 rows (confirmed by checking `created_at` max and the
file's own `updated_at` freshness). Always check a newly-attached file's actual
date coverage before merging — a confident description can still be wrong about
what actually got exported.

## 11. Stale-snapshot carryover across merge-script generations
Never carry forward a PREVIOUS session's cached rows for an already-tracked
date "because it's already tracked" — always re-source every tracked date fresh
from the LATEST available file in each merge. A real retroactive channel
reclassification (13 tickets, Sept→Oct) went undetected for ~1 day this way,
inflating Oct 1 Valid Leads (407 vs correct 393).
