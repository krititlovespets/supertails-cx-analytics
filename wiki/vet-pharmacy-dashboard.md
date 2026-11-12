# Chat dashboard || Vets and Pharmacy

*Last updated 2026-11-12. Sheet holds Oct 1 – Nov 12 12:13 PM.*

A separate Google Sheet that tracks the **vet chat team**: how many chats come in, how fast the doctors reply and close them,
who handles what, when chats arrive, and what the chats are about.

- **Sheet:** [Chat dashboard || Vets and Pharmacy](https://docs.google.com/spreadsheets/d/1MJG4WQmz8_fuZ8xvdnBJ59sznSyIfthvBF9pBsaRROw/edit) (`1MJG4WQmz8_fuZ8xvdnBJ59sznSyIfthvBF9pBsaRROw`)
- **Script:** `vets/update_vet_pharmacy_dashboard.py` (rebuilds every tab from one export)
- **Not part of** "Dashboard || Extra". Different sheet, different channels, different rules.

## 1. Where the data comes from

Nugget ticket exports (`db….csv`) that contain the vet channels — one file per month is fine; the script merges them and de-duplicates on `ticket_id`. Each row is one chat (ticket).

Current inputs: `dbqpeu5ng12s73egib50.csv` (Oct 1–31) + `dbqolndng12s739firl0.csv` (Nov 1 – Nov 12 12:13).

| Channel in the export | Used? | Why |
|---|---|---|
| Tele Consultation Chat Outcome (channel 38) | **Yes** — shown as "Tele Consultation Chat" | Vet consults on WhatsApp |
| Pharmacy Chat Assistance (channel 37) | **Yes** — shown as "Pharmacy Chat" | Prescription / order verification on WhatsApp |
| Paid Tele Consultation Bookings | **No, removed on purpose** | System-created booking tickets. Vets never reply in chat there (0 agent messages on every ticket; the consult happens by call), so FRT cannot exist. Decision 2026-11-12. |

Any other channel in the file is ignored.

## 2. The tabs

Every tab has the same shape: rows are metrics, columns are **`<Month> Total` · `<Month> Avg` for each month, oldest first (Oct, Nov, …) · then one column per date from the first day**. The FRT / Response tabs have only `<Month> Avg`; Dispositions adds `<Month> %`.
Row 2 of each tab is a grey note with the data cut-off time and the rules used.

| # | Tab | What it shows |
|---|---|---|
| 1 | **Vets & Pharmacy Dashboard** | Total Chats, then Tele and Pharmacy. Each block = chat count, Avg FRT, Avg Response Time |
| 2 | **Doctor Chats** | Chats per doctor. Sections All Chats → Tele → Pharmacy; section total then each doctor |
| 3 | **Doctor FRT** | Avg FRT per doctor, same sections |
| 4 | **Doctor Response Time** | Avg Response Time per doctor, same sections |
| 5 | **Hourly Flow** | Chats by the hour they came in (24 rows + Total) for All / Tele / Pharmacy, heat-map shaded |
| 6 | **Dispositions** | What the chats were about: Tele by *Tele Consultation Chat Outcome*, Pharmacy by *Pharmacy Chat Disposition*; count, % of chats, daily |

## 3. Definitions

| Metric | Rule |
|---|---|
| **Chats** | Unique tickets, counted on the date (and hour) they were **created**. All 24 hours. |
| **Month Total** | All chats in the month so far. |
| **Month Avg (counts)** | Average per day over that month's **complete days only** (a closed month = all its days). Today's half-day is left out so it doesn't pull the average down. |
| **Clock start** | The **first time the chat was assigned inside its vet channel**, read from the assignment-history columns (`last_agent_assignment` … `5th_last_agent_assignment`, matched on ChannelName). *Not* `created_at` — that would include the time the customer spent with the WhatsApp bot / UCJ SC agent before reaching a vet. |
| **FRT** (first response time) | First agent reply (`agent_frt_response_at`) − clock start. |
| **Response Time** | Chat closed (`resolved_at`) − clock start. The export has no per-message times, so time-to-close is the response measure. |
| **FRT / Response window** | Only chats **created 9:00 AM – 8:59 PM**. Night chats are excluded from both. |
| **Time averages** | Simple mean over chats, shown as `h:mm:ss`. Month column = mean over every chat in the month (not an average of daily averages). Total / All Chats rows pool both channels, so the bigger channel weighs more. |
| **Doctor** | The doctor the chat is assigned to (`agent_name`). If a chat moved between doctors, it counts once, for the last one (67 chats in Nov 1–12). Doctors add up to the section total, except chats never assigned to anyone (1 in October, ticket 435712). A doctor appears if they had any Tele/Pharmacy chat in any month shown (Oct adds Dr Nisha and Dr Vaishnavi). |
| **Disposition** | The outcome field the doctor tags when closing. Blank = "Not Tagged" (none so far). |

**Excluded from FRT (disclosed, not hidden):** chats where a UCJ SC agent replied *before* the hand-off to the vet channel —
the export only keeps the first reply overall, so the vet's own first reply is unknown (24 Tele chats in Nov 1–12).

**"—" in a cell** = no chats for that doctor / day (or, for FRT, none that qualify).

## 4. How to update

1. Export Nugget tickets for the vet channels from the 1st of the month to now (same export UI as the main dashboard, see [external-sources.md](external-sources.md)). Keep the closed months' files (October's above) — every run needs **all** months you want on the sheet.
2. Dry run, check the counts:
   ```bash
   python3 vets/update_vet_pharmacy_dashboard.py ~/Downloads/<oct>.csv ~/Downloads/<nov>.csv --dry-run
   ```
3. Write:
   ```bash
   python3 vets/update_vet_pharmacy_dashboard.py ~/Downloads/<oct>.csv ~/Downloads/<nov>.csv
   ```

The script rebuilds **all six tabs** in place from the files given (tab links don't change). A month left out of the command disappears from the sheet;
a file starting mid-month drops that month's earlier days. If two files hold the same ticket, the later file in the command wins. Needs `pip3 install gspread pandas` and the service-account key
at `~/Documents/Supertails work/kriti-project-505208-….json` with Editor access on the sheet (same key as Dashboard || Extra).

## 5. Numbers so far

| | Oct chats | Oct /day | Oct FRT | Oct Response | Nov 1–12 chats | Nov /day | Nov FRT | Nov Response |
|---|---|---|---|---|---|---|---|---|
| **Total** | 2,680 | 86 | 0:01:17 | 0:25:51 | 1,478 | 130 | 0:00:56 | 0:29:58 |
| Tele Consultation | 1,748 | 56 | 0:01:23 | 0:27:54 | 1,043 | 92 | 0:01:04 | 0:31:59 |
| Pharmacy | 932 | 30 | 0:01:05 | 0:21:39 | 435 | 38 | 0:00:39 | 0:25:10 |

November volume is ~50% higher per day than October; FRT got faster, time-to-close a little slower.

November detail:

- **Doctors:** Dr Shubham 807 chats (FRT 1:20), Dr Hima 544 (0:36), Dr Smera 67 (0:37), Dr Athira 60 (0:34).
- **Peak hour:** 12–1 PM (~12.6 chats/day); quiet midnight – 8 AM; still ~5–7 chats/hour until 11 PM.
- **Unresponsive customers** close 66% of Tele chats and 72% of Pharmacy chats. Of engaged Tele chats, General Consultation and Skin Issues lead.

## 6. Known gaps

- **FRT is blank for Oct 1–3 and rests on 1 chat for Oct 4.** Until Oct 4 every chat went to a UCJ SC agent first, who replied before handing it to the vets; the export keeps only the first reply on a ticket, so the vet's own first reply is unknown (Oct 1: 38 of 38 chats, Oct 2: 51/52, Oct 3: 51/51, Oct 4: 44/45). Routing changed Oct 5. The script spots any day where over half the 9–9 chats are like this and puts a hover note on its FRT cells (Dashboard + Doctor FRT) plus a line in row 2. Response Time is unaffected.
- The export's SLA-breach flags are `False` on every ticket — unusable, so there is no SLA metric yet. A target (e.g. FRT ≤ 1 min) would have to be set by us.
- Averages swing on low-volume doctors: one chat open for a day (Dr Athira, Nov 2: 26:43:36) moves the whole month.
- Response Time is time-to-close, not reply-to-reply; real per-message response time needs a message-level export.

## 7. History

- **2026-11-12** — Dashboard built tab by tab with Kriti: chat volume → FRT/response (clock moved from created to channel-assignment on her call) →
  Paid bookings removed → single dashboard tab → doctor tabs (layout tried 3 ways; final = one tab each for Chats, FRT, Response, section-first) →
  Hourly Flow → Dispositions (kept every disposition, no grouping). Script and this page added the same day; the script reproduces the live sheet exactly.
- **2026-11-12** — October added (`dbqpeu5ng12s73egib50.csv`, 3,019 tickets → 2,680 Tele + Pharmacy). Script now takes several files and writes Total/Avg columns per month; dates run from Oct 1. All November cells re-checked: 0 changed. Section headings on Hourly Flow / Dispositions no longer carry a chat count (Total rows show it per month).
