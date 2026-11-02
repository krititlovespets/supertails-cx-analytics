# 1 · Runbook — updating the dashboard

[← Home](Home.md)

**Time:** about 2 minutes. **Frequency:** whenever a new export arrives (it has been daily to every few days).

## The routine

1. **Get the export** from the CX ticketing tool. See [5-Data-and-Exports](5-Data-and-Exports.md) for what it must contain.
2. **Dry run** (reads the sheet, computes everything, diffs against the live tabs, writes **nothing**):

   ```bash
   cd ~/Downloads/chat-dashboard-wiki
   python3 update_chat_dashboard.py ~/Downloads/NEW_EXPORT.csv --dry-run
   ```
3. **Read the output** (table below). If it looks right, run it for real — same command without `--dry-run`.
4. **Verify:** run the dry run once more. It should say **`0 differing cells`** for both tabs. That proves the sheet now
   equals what the script computes.
5. **Report** the new "through" date, ticket total, and anything the warnings flagged.
6. **Update the wiki — every time** (standing instruction, 2026-10-27): `Home.md` current state + open items, the export list in
   [5-Data-and-Exports](5-Data-and-Exports.md), a line in [6-History-and-Decisions](6-History-and-Decisions.md). If the call tabs were
   updated too, also log it in the GitHub repo wiki (`~/Claude/supertails-cx-analytics/wiki/log.md`) and push.

Several files at once are fine, **oldest first**: `python3 update_chat_dashboard.py a.csv b.csv`.
Re-running the same file is harmless (idempotent).

**Two cautions learned 2026-10-27:**
- **Order = age.** The script treats the *last* file as newest and lets it overwrite. Never pass an **older** export after the sheet
  base just to fill a gap — filter it to ticket IDs the Raw Dump doesn't have yet, then pass that.
- **Cut to the requested day.** A Nugget export usually runs into "today"; if asked to update through day X, write a copy with
  `created_at < X+1` and feed that, so the chat tabs stop at the same date as the Main Dashboard.

## Reading the dry-run output

```
Loading ...
  sheet base (Chat - Raw Dump (Sep 1+)): 5853 rows        <- tickets already in the sheet
  dbfdvl0a400s73fcqk7g.csv: 255 UCJ SC Chat Assistance rows <- UCJ rows found in the new file
  merged: 5894 tickets, 2026-09-01 00:31:17 -> 2026-10-25 21:52:31
Computing ...
  tickets 5894 | Daily: 55 day-dates / 56 OBH-dates | Agent: Day 4 agents, OBH 9 agents
  DRY-RUN diff vs live 'Chat - Daily Summary': 35 differing cells
  DRY-RUN diff vs live 'Chat - Agent Summary': 44 differing cells
```

| You see | Meaning | Do |
|---|---|---|
| `merged:` is `base + new − overlap` | normal | check it grew by about the number of new tickets |
| Diff cells > 0 on a dry run | new date columns + refreshed overlap + shifted agent rows | expected before a real run |
| `!! WARNING missing calendar days [...]` | a whole day has no tickets in the data (**not zero** — missing) | ask for a re-export covering that day |
| `!! WARNING … NO overlap with existing data` | the new file starts after the last ticket you have | usually fine; tickets from the last few days keep stale `resolved_at`. Real impact so far: ~1 ticket. Ask for ~3 days of overlap next time |
| Diff stays > 0 right *after* a real run | something wrote partially | see [8-Troubleshooting](8-Troubleshooting.md) |
| Crashes with `Usecols do not match columns` | the file is not a chat ticket export | see "Wrong file" below |

## Preflight checks worth doing every time (30 seconds)

**1. Is it the right kind of file?** A chat export must have these columns: `ticket_id, created_at, agent_name,
agent_assigned_at, resolved_by, resolved_at, last_agent_assignment, agent_frt_response_at, channel_name`.
A file named `CALL_Details_…csv` is a **telephony call report** (Ameyo) and will fail — it has no `ticket_id`. The script fails
*before writing anything*, so a wrong file cannot damage the sheet.

**2. What dates does it cover?**

```python
import pandas as pd
n = pd.read_csv("NEW_EXPORT.csv", dtype=str, keep_default_na=False,
                usecols=["created_at", "channel_name"])
n = n[n["channel_name"] == "UCJ SC Chat Assistance"]
print(n["created_at"].min(), "->", n["created_at"].max(), len(n))
print(n.groupby(n["created_at"].str[:10]).size().to_string())
```

Look for: a first ticket in the **middle of a day** (the export started mid-day, so the morning is missing), and a last ticket
**well before the export time** (the tail of the last day is missing and will arrive next time).

**3. Is there a hole at the join?** After merging, the biggest gap between consecutive `created_at` values is a good detector.
The longest legitimate overnight silences so far are 8–9.3 hours. Anything above ~10 hours deserves a question:

```python
import gspread, pandas as pd
gc = gspread.service_account(filename="/path/to/key.json")
v = gc.open_by_key("1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw").worksheet("Chat - Raw Dump (Sep 1+)").get_all_values()
d = pd.DataFrame(v[1:], columns=v[0]); d["c"] = pd.to_datetime(d["created_at"]); d = d.sort_values("c")
d["gap_h"] = d["c"].diff().dt.total_seconds() / 3600
print(d.nlargest(6, "gap_h")[["c", "gap_h"]])
```

This is how the Oct 18 problem was found (13.46 h gap vs a previous maximum of 9.26 h).

**4. Does each day start at a normal time?** The first ticket of a normal day arrives between **07:45 and 09:15**, and no daytime silence
(both tickets between 09:00 and 20:45) has exceeded **2.9 h**. A first ticket at 12:53 (Oct 18) means the morning is missing. Don't rely on the
daily *count* — volume has been trending down, so a low count alone proves nothing.

## Asking Claude to do it

> Read `~/Downloads/chat-dashboard-wiki/Home.md` and `1-Runbook.md`, then update the dashboard with this file: `@/path/to/export.csv`.
> Dry-run first, tell me anything odd, then run it and verify.

## Never do these

- **Don't clear or resize the whole spreadsheet.** It contains other people's tabs (see [3-Sheet-Reference](3-Sheet-Reference.md)).
  The script only ever touches its three tabs.
- **Don't delete the `Chat - Raw Dump (Sep 1+)` tab.** It is the script's base data — the memory of every ticket.
- **Don't paste the service-account key anywhere** (chat, docs, git). It can edit every sheet it's shared on.
- **Don't edit the three tabs by hand.** The next run rewrites them completely.

## Writes are rate-limited

Google Sheets allows about 60 writes per minute. The script batches its formatting into single calls and retries with back-off
on a `429`; if you ever see "rate-limited, waiting…", just let it finish.
