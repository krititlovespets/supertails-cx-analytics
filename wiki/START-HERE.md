# Dashboard || Extra — Start Here

One guide to understand the Supertails CX dashboard and keep it updated. Written for a person and for Claude.
**If you are Claude: read this whole file before touching anything, then `wiki/definitions.md`.**

*Last updated 2026-11-12. Sheet runs through Nov 11, 2026. October is closed.*

## 1. What this is

The dashboard is a Google Sheet, [Dashboard || Extra](https://docs.google.com/spreadsheets/d/1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw/edit)
(`1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw`). It tracks the UCJ call centre and chat team. It is updated from two exports, by scripts in this repo:

| Export | From | What it holds |
|---|---|---|
| Ticket export (`db….csv`) | Nugget | One row per ticket |
| `CALL_Details_….csv` | Ameyo | One row per call |
| Booking counts | [Clinic Dashboard](https://docs.google.com/spreadsheets/d/1EyTmbBSkZMvL5JolKuo8xxOkguYGUKpTJTzlN68n5hM), tab `Agent_Perf_V2` | Read live by the scripts |

Three Nugget channels matter. **Unified Customer Journey** and **UCJ Booking Campaigns** (Bangalore) feed the call tabs. **UCJ SC Chat Assistance** feeds only the chat tabs.

## 2. The tabs

| Tab | Shows | Updates |
|---|---|---|
| Main Dashboard | Every core metric by day and month | Current month |
| Ticket Categories | The same metrics split into 6 ticket categories | Current month |
| Valid Leads Log | One row per valid lead, with transfer and connect flags | Current month's block |
| Agent Productivity | Table 6 = October, Table 7 = November. Tables 1–5 = September snapshots | Current month's table only |
| Table6 / Table7 Raw Dump | Ticket-level detail behind each table | Current month |
| Booking Analysis | Bangalore funnel per agent; newest month on top | Current month's section |
| Prediction Model | What the rest of the month needs to reach 30% | Current month |
| Callback Adherence + Dump | Were customer-requested callbacks honoured | November onward |
| Vet Followup Callback + Dump | Repeat vet transfers within 15 days | Rolling 15 days; full history in the dump |
| Chat - Daily / Agent Summary, Raw Dump | Chat volume and first-reply times | All chats |

Closed months stay frozen. The one exception is vet rows, which keep updating until a month's 15-day windows end (October: until Nov 15).

## 3. The key numbers

Full formulas are in [definitions.md](definitions.md). Chat rules are in [chat/4-Metrics-and-Rules.md](chat/4-Metrics-and-Rules.md).

- **Valid Lead:** a chat-source ticket in Unified Customer Journey, title has PRM or Pharmacy with verification not true, not a callback request.
- **Connect %** (goal 60%): valid leads with any call of 30+ seconds of agent talk ÷ valid leads.
- **Transfer %** (goal 30%): valid leads with a Transfer Done or Doctor Called ÷ valid leads, counted once per ticket.
  - Transfer Done: transferred to a doctor or language queue, and the customer stayed 30+ seconds after the agent.
  - Doctor Called: a doctor's own call of 30+ seconds, after the ticket was created.
- **Booking %** (goal 6.5%): Clinic Dashboard appointments ÷ Bangalore tickets.
- **AHT:** average talk time on calls of 60+ seconds.
- **FRT:** ticket creation to first call, for leads created 9am–8:45pm.
- **Vet 15-day repeat:** of tickets with a transfer in the 15 days after creation, those with another transfer more than 15 minutes after the first.
- **Single owner:** Agent Productivity and Booking Analysis give each ticket to one agent, so agents add up to the team total.

**Recent days read low. This is normal.** Calls are matched to tickets at any time, so a day's Transfer % and Connect % rise for 1–3 refreshes as later calls arrive. Don't "fix" it.

## 4. Setup (once)

Only someone with access can do this. **Never commit the key, the doctor list or any CSV.** `.gitignore` blocks them.

1. Get the code one of two ways. **No GitHub account:** unzip `supertails-dashboard-kit.zip` so you have the folder `~/supertails-cx-analytics`. **With access to the private repo:** `git clone https://github.com/krititlovespets/supertails-cx-analytics.git`.
2. Install: `pip3 install gspread pandas`
3. Create the folder `~/Documents/Supertails work/`. Ask the owner, by a private channel, for:

| Item | Goes in | Why |
|---|---|---|
| `kriti-project-505208-8a2a4a798a5f.json` (Google service-account key) | `~/Documents/Supertails work/` | Lets the scripts read and write the sheets. Treat it like a password |
| `doctors_emails.txt` (36 doctor emails) | `~/Documents/Supertails work/` | Needed for every transfer number |
| `sept_base/hist_nugget.csv`, `sept_base/hist_ameyo.csv` | `~/Documents/Supertails work/sept_base/` | All closed months; holds customer phone numbers |

A safer alternative to sharing the key: create your own service account, share both sheets with it, and name its key the same.

## 5. The update routine

Do this **only when asked**. There is no automatic schedule.

1. **Get the two exports** into `~/Downloads`. If `~/Downloads` lacks the earlier days of the month, both exports must start from the 1st, because the scripts rebuild the whole month.
2. **Check them.** Make sure the Nugget file really covers the last day through 23:59. An October export once stopped at 11:55.
3. **Run,** from any empty working folder. `LAST` = the last complete day.

```bash
python3 ~/supertails-cx-analytics/scripts/merge_month_exports.py 2026-11
```

Read the per-day counts it prints. A normal day is about 550–600 UCJ tickets and 2,300–2,900 calls. Then:

```bash
VET_MONTHS="2026-10 2026-11" bash ~/supertails-cx-analytics/scripts/refresh_all.sh 2026-11-01 ~/Downloads/NEW_NUGGET.csv "$HOME/Documents/Supertails work/sept_base"
```

Adjust the paths if you cloned elsewhere. It takes about 5 minutes and stops at the first error. After Nov 15, drop `2026-10` from `VET_MONTHS`. If `LAST` is a partial day, add `PRED_LAST=<last complete day>` in front.

4. **Verify.** This must end with `problems: 0`, and the chat lines must show `0 differing cells`.

```bash
python3 ~/supertails-cx-analytics/scripts/verify_main_dashboard.py
```

5. **Update the wiki.** Add an entry to [log.md](log.md) with the date, files used, key numbers and anything odd. With repo access, commit and push. From the zip, there is nothing to push: send Kriti the new log entry so the main copy stays current, and ask for a fresh zip when scripts change.

A new month has a checklist: [daily-workflow.md](daily-workflow.md), "Month rollover checklist".

## 6. Rules to follow

- Refresh only when asked. Use the files given; don't re-pull over them.
- Check what a file really contains. Filenames and descriptions have been wrong before.
- `CALL_Details_…csv` is a call file, not a ticket file. The chat script needs the ticket file.
- Stop at the last complete day unless the person asks for today. Keep partial days out of the Prediction Model.
- Other tabs in the spreadsheet may be other people's work. Never clear a tab you don't own.
- Never say a ticket "moved from ch36 to ch7". The data can't prove it. Say "a bot-style opening and a later human agent".
- Report what was done, what was not, and anything that looks wrong. Don't hide a low number or a failed step.
- If a pasted deck disagrees with a source deck, keep the source deck's number and flag the difference.

## 7. Known issues

- **Oct 30–31 froze on early counts.** One more October run around Nov 5 would catch later matches.
- **Oct 26 bookings = 1** on the Clinic Dashboard looks low. Not yet confirmed with the clinic team.
- **Callback Adherence:** October onward counts any ticket that ever had a callback scheduled. July–September used an older method, so they aren't directly comparable.
- **Booking Analysis:** per-agent Booking % is approximate, because Clinic bookings aren't linked to tickets. September still uses the older method.
- **Clinic Dashboard date headers** for days 1–12 come back as numbers. `scripts/clinic.py` handles this; always read bookings through it.
- **Row label** "Avg Talk Time per Agent (10 agents)" is out of date. The roster is 9.
- **Incentives:** the combined criteria PDF overrides `HANDOFF.md` section 10. Ask Kriti for it.

## 8. The claude.ai pages (optional)

These belong to Kriti's Claude account. Updating them needs edit access, which Kriti must grant from each page's Share menu. Steps are in [daily-workflow.md](daily-workflow.md).

- [Supertails CX Pulse](https://claude.ai/artifact/6CtMvgBY69qfLofu1SQx8c)
- [November UCJ Tracker](https://claude.ai/artifact/HH5BjcV1zt5dCZNwevYTGS)
- [October UCJ Tracker](https://claude.ai/artifact/9AqvMDAuHWWfyG9UopkDJp) (final)

The separate **UCJ October Pulse** leadership report is not part of this routine.

## 9. Where to look next

| For | Read |
|---|---|
| Every formula | [definitions.md](definitions.md) |
| Row-by-row tab layout | [sheet-structure.md](sheet-structure.md) |
| Refresh detail, month rollover, page updates | [daily-workflow.md](daily-workflow.md) |
| Past bugs to avoid | [bug-patterns.md](bug-patterns.md) |
| Vet follow-up history | [vet-followup.md](vet-followup.md) |
| What happened on each date | [log.md](log.md) |
| Chat tabs | [chat/Home.md](chat/Home.md), [chat/8-Troubleshooting.md](chat/8-Troubleshooting.md) |
| Older background (dated Oct 16; this file wins) | [HANDOFF.md](HANDOFF.md) |
