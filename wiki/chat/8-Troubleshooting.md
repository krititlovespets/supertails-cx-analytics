# 8 · Troubleshooting

[← Home](Home.md)

## Errors

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError: …json` | `KEY_PATH` in the script points at a key that isn't there | set `KEY_PATH` (top of the script) to the real key location |
| `gspread.exceptions.SpreadsheetNotFound` or `APIError [404]` | wrong `SHEET_ID`, **or** the sheet isn't shared with the service account | share the sheet with the service account's `client_email` as **Editor**; check `SHEET_ID` |
| `APIError [403] … does not have permission` | shared as Viewer, or the Sheets API isn't enabled in the Google Cloud project | give Editor access; enable the Google Sheets API for the project |
| `APIError [429] … Write requests per minute` | Google allows ~60 writes/min | nothing — the script backs off and retries (15 s, 30 s, …). If it still fails, wait a minute and re-run with the same file |
| `WorksheetNotFound` | a tab was renamed or deleted | restore the exact names: `Chat - Daily Summary`, `Chat - Agent Summary`, `Chat - Raw Dump (Sep 1+)` |
| `ValueError: Usecols do not match columns, columns expected but not found: [...]` (the last line of a long traceback) | the file is **not** a chat ticket export (e.g. a `CALL_Details…` telephony report) or a required column is missing | send the right file; required columns are in [5-Data-and-Exports](5-Data-and-Exports.md). Nothing is written — verified by feeding it the CALL_Details file on 2026-10-26 |
| `Raw Dump tab is missing columns [...]` | the Raw Dump tab lost a column | rebuild: `--base none` with all source CSVs, oldest first |
| `ModuleNotFoundError: pandas / gspread` | libraries not installed | `pip install pandas gspread` |
| Pages of `FutureWarning` / "Python 3.9 past end of life" / `NotOpenSSLWarning` | old system Python | harmless. Add `-W ignore` to silence: `python3 -W ignore update_chat_dashboard.py …` |
| `--base none needs at least one CSV` | you passed no files with `--base none` | pass the source CSVs |

## "The numbers look wrong"

| You see | Check |
|---|---|
| The latest day has tiny counts or odd averages | the export ended mid-day — it's partial. The next export completes it |
| A day has far fewer tickets than expected, or a missing morning | run the gap checks in [1-Runbook](1-Runbook.md): first ticket of the day (normal 07:45–09:15), largest silence (> 10 h) |
| A date column is **missing** entirely | no tickets that day in the data. The script warns `missing calendar days`; ask for a re-export |
| A column shows blank cells for an agent | that agent had no tickets that day — expected |
| An agent you don't recognise appears | OBH shows everyone; the Day view shows everyone *except* the exclusion list. New agents appear automatically |
| Average is huge but median is normal | a single long ticket or a queue hold — read the median; see [7-Findings](7-Findings.md) §3 |
| OBH Actual FRT is hours | **expected** — it measures the overnight wait |
| Day Starting FRT count < Actual FRT count | negatives (reassigned tickets) were dropped from Day Starting FRT |
| Totals differ from the old HTML dashboard | the HTML was a Sep 1–23 snapshot with different windows — ignore it |
| A number differs from what you saw yesterday | the newest export refreshed overlapping tickets (a late reply or resolution arrived). Normal |
| Month column says `Aug Avg` in OBH | the tail of the Aug 31 shift; ~15 tickets |

## After a run

| You see | Meaning / fix |
|---|---|
| dry-run right after a real run shows **0 differing cells** | success |
| dry-run shows differing cells after a real run | a write was interrupted. Re-run the **same** command — it is idempotent. The Raw Dump tab is written last, so also pass the same CSV again |
| the Raw Dump tab looks short after a failed run | re-run with the same CSV(s); if it is badly damaged, `--base none` with all source CSVs |
| the summary tabs are empty | the run died between "clear" and "update"; re-run |

## If a run fails halfway

The script writes in this order: **Daily Summary → Agent Summary → Raw Dump**. The summary tabs are cleared and rewritten (so briefly empty); the Raw Dump is overwritten in place
and is never cleared. Because the *base* is the Raw Dump tab, a failure before the last step just means the base does not yet contain the new tickets — **re-run with the same CSV** and everything
lines up. You can't lose history this way.

## Things that are NOT bugs

- Time cells can't be summed or charted — they are text (see [3-Sheet-Reference](3-Sheet-Reference.md)).
- Your hand-formatting on the three tabs disappears on the next run.
- The Day view's Team Average ignores four agents on purpose.
- Agent rows reorder when volumes change (sorted by total tickets).
- The Raw Dump tab stores ticket IDs as text.

## Still stuck

Run the dry-run and read it top to bottom; the output states what it loaded, how many tickets merged, and every warning. Then ask Claude (new account included):
> Read `~/Downloads/chat-dashboard-wiki/8-Troubleshooting.md` and `9-Script-Reference.md`, then diagnose this error: *(paste it)*.
