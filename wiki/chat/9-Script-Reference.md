# 9 · Script Reference — `update_chat_dashboard.py`

[← Home](Home.md)

One file, 450 lines, standard libraries plus `pandas` and `gspread`. Run `python3 update_chat_dashboard.py --help` for usage.

```
python3 update_chat_dashboard.py [CSV ...] [--base sheet|none] [--dry-run]
```

| Option | Meaning |
|---|---|
| `CSV …` | export file(s), **oldest first** |
| `--base sheet` *(default)* | start from the Raw Dump tab, then merge the CSVs |
| `--base none` | ignore the sheet; build only from the CSVs you pass (rebuild / bootstrap) |
| `--dry-run` | compute, diff against the live Daily/Agent tabs, **write nothing** |

## Flow

```
load base (sheet) + load CSVs (UCJ rows only)
   → merge: de-dupe on ticket_id (newest wins), drop blank created_at, sort, gap-check, overlap-check
   → prepare: parse timestamps, compute actual_frt / day_starting_frt / resolve_seconds
   → compute: Daily (bucket by created_at) · Agent (bucket by agent_assigned_at)
   → build: sheet rows + formatting specs
   → dry-run: diff vs live      |      real run: write Daily → Agent → Raw Dump
```

## CONFIG (top of the file) — the knobs you'll actually touch

| Constant | Default | Change it when |
|---|---|---|
| `SHEET_ID` | the live spreadsheet | you copied/moved the sheet |
| `KEY_PATH` | `~/Downloads/kriti-project-505208-8a2a4a798a5f.json` | the key moves (do this — see [2-Setup-and-Migration](2-Setup-and-Migration.md)) |
| `CHANNEL` | `UCJ SC Chat Assistance` | you want a different channel (also update titles/notes text) |
| `START_DATE` | 2026-09-01 | the series start changes (only used by the missing-day check) |
| `DAY_START` / `DAY_END` | 09:00:00 / 20:45:00 | the shift boundaries change. `DAY_END` also defines when an OBH shift "starts" for the date rule |
| `EXCLUDE_FROM_DAY_AGENT_VIEW` | Akshaya, Dhanush S, Farhan, Dr Sahithya | the roster view changes |
| `TAB_DAILY` / `TAB_AGENT` / `TAB_RAW` | the three tab names | tabs are renamed |
| `RAW_COLS` | the 8 stored columns | the export gains/loses a needed column |
| `SHADE_DAY` / `SHADE_OBH` | block shading colours | cosmetic |

## Functions

| Function | Role |
|---|---|
| `with_retry` | retries a Sheets call on HTTP 429 with back-off |
| `fmt_time` | seconds → `45s` / `6m 32s` / `7h 3m 27s` |
| `month_name` | `'2026-10'` → `Oct` for month column titles |
| `load_csv` | read the 9 needed columns as text, keep UCJ rows |
| `load_base` | read the Raw Dump tab (refuses if a column is missing) |
| `merge` | combine, de-dupe, sort, print warnings |
| `prepare` | parse timestamps; add the three duration columns |
| `window_masks_and_dates` | Day/OBH masks and the date each row is reported under (shift-start rule) |
| `compute_daily_block` | per-month and per-date stats for one window (whole team) |
| `compute_agent_block` | per-agent, per-month, per-date matrices + ticket counts for one window |
| `build_daily` / `build_agent` | turn computed stats into sheet rows + formatting specs |
| `diff_with_live` / `same` | cell-by-cell comparison (numeric-tolerant) used by `--dry-run` |
| `push_tab` | clear → resize → write (RAW) → one `batch_format` → freeze |
| `push_raw` | resize → overwrite in place (no clear) → bold header → freeze |

## Recipes

**Change the Day/OBH boundary.** Edit `DAY_START`/`DAY_END`. Also edit the hard-coded *titles and notes* in `build_daily` and `build_agent` ("9 AM – 8:45 PM", "8:45 PM – 9 AM") — they are text.

**Hide or show an agent in the Day view.** Edit `EXCLUDE_FROM_DAY_AGENT_VIEW`. Team Average/Total follow automatically.

**Add a metric row to Daily Summary.** Add its fields in `compute_daily_block` → add a `row(...)` in `build_daily` → update the **hard-coded row constants** in `build_daily`'s formatting section
(`bold("A2:A12")`, `shade(f"B2:…12…")`, and `ot, oh, ol = 14, 15, 25`, which assume 12-row blocks) and the row map in [3-Sheet-Reference](3-Sheet-Reference.md).

**Get numeric times for charts.** Change `fmt_time` to return seconds (and apply a duration number format in `push_tab`). Note `diff_with_live` compares strings — update it too.

**Rebuild from scratch.** `python3 update_chat_dashboard.py --base none <every source CSV, oldest first>` into a sheet that has the three tabs.

**Add a new month.** Nothing to do; month columns are generated from the data.

## Behaviours worth knowing

- **Everything is read and written as text** (`dtype=str`, `value_input_option="RAW"`), so the Raw Dump round-trips exactly. Counts and averages-per-day are written as numbers.
- **`agent_name` blank → treated as missing** and the ticket is excluded from every metric.
- **The summary tabs are cleared then rewritten** (briefly empty); the Raw Dump is not cleared. A failed run is recovered by re-running with the same CSV.
- **`--dry-run` still reads** the sheet (needs the key and network) but writes nothing.
- **Timestamps are naive** local time (no time-zone conversion).
- The missing-day check only inspects whole calendar days; partial days are caught by the human checks in [1-Runbook](1-Runbook.md).
- Only cells the script would write are diffed; stale extra cells in the live tabs beyond the generated shape are not reported (they are removed by the clear anyway).

## How it was tested

1. `--dry-run` against the live sheet with the sheet as base → **0 differing cells** on both summary tabs (2026-10-16, re-checked after every real run through Oct 25).
2. `--dry-run --base none` rebuilding from four source files → **0 differing cells** (2026-10-16).
3. `py_compile` clean; the embedded copy in the old README is byte-identical to this file.
4. Every real run was followed by a dry run confirming 0 differences.

## Dependencies

Python 3 (tested 3.9.6), `pandas` (2.3.3), `gspread` (6.2.1), a service-account JSON key with Editor access. No Claude, no database, no other network access.

## Not covered by the script

Making or choosing the export; any other tab in the spreadsheet; charts; scheduling (see the macOS note in [2-Setup-and-Migration](2-Setup-and-Migration.md)).
