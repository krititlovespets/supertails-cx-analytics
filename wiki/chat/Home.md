# Chat Dashboard Wiki

Everything about the **UCJ SC Chat Assistance** chat dashboard (Supertails CX): what it is, how to update it,
how every number is defined, why it looks the way it does, and how to move it to a new account.

*Written 2026-10-26, last updated 2026-11-02. Data in the sheet runs 2026-09-01 → 2026-11-01 23:58 (6,301 tickets).*

## 60-second summary

- **The dashboard is a Google Sheet** — spreadsheet "Dashboard || Extra", three tabs: `Chat - Daily Summary`,
  `Chat - Agent Summary`, `Chat - Raw Dump (Sep 1+)`.
  <https://docs.google.com/spreadsheets/d/1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw>
- **It is updated by one Python script**, `update_chat_dashboard.py` (in this folder), fed with a CSV export from the CX
  ticketing tool. It does not use Claude, so a Claude-account change breaks nothing.
- **Two FRTs on purpose.** *Actual FRT* = first reply − message created (what the customer felt). *Day Starting FRT* =
  first reply − assigned to an agent (how fast the agent was once the chat was theirs).
- **Day vs OBH.** Day = chats created 9:00 AM–8:45 PM. OBH (off-business-hours) = 8:45 PM–9:00 AM, reported under the
  day the shift *started*.
- **The headline finding:** overnight chats wait ~9 hours (median) for a reply, but agents reply in ~11–14 s once a chat is
  assigned. The delay is in the hand-off, not in agent speed. See [7-Findings](7-Findings.md).

## Pages

| Page | Read it when you want to… |
|---|---|
| [1-Runbook](1-Runbook.md) | **update the sheet** (the 2-minute routine, preflight checks, what warnings mean) |
| [2-Setup-and-Migration](2-Setup-and-Migration.md) | move to a new Claude account, Mac, or Google account; set up from zero |
| [3-Sheet-Reference](3-Sheet-Reference.md) | find any cell/row/tab; know exactly what the script writes |
| [4-Metrics-and-Rules](4-Metrics-and-Rules.md) | check a formula, window, exclusion or display rule |
| [5-Data-and-Exports](5-Data-and-Exports.md) | understand the exports, which files were used, and what has gone wrong with them |
| [6-History-and-Decisions](6-History-and-Decisions.md) | learn why something was built that way (chronological log) |
| [7-Findings](7-Findings.md) | interpret the numbers and read the analyses done so far |
| [8-Troubleshooting](8-Troubleshooting.md) | fix an error or a number that looks wrong |
| [9-Script-Reference](9-Script-Reference.md) | change the script safely |
| [10-Related-Systems-and-Memory](10-Related-Systems-and-Memory.md) | see what else lives on this Mac (other automations, keys, Claude memory notes) |
| [11-Transfer-Rules](11-Transfer-Rules.md) | know what "transfer" means — chat tabs (no transfer metric) vs call tabs (Transfer Done / Doctor Called, 30% target) |

## Current state (as of 2026-11-02)

| | |
|---|---|
| Tickets in sheet | **6,301** (Sep 1 00:31 → Nov 1 23:58) |
| Day dates / OBH dates | 60 / 60 |
| Agents shown | Day view: 4 · OBH view: 9 |
| Last export applied | `dbjusnpm8a4s738u7530.csv`, cut at Nov 1 23:59 (Oct 29 00:10 → Nov 2 07:25 in the file) |
| Update script | tested: `--dry-run` against the live sheet gives **0 differing cells** from both the sheet base and a from-scratch rebuild |

## Open items (these live nowhere else — conversation history does not migrate)

1. ~~Oct 18 morning missing~~ — **fixed 2026-10-27.** Two older Nugget exports already in Downloads (`dbapfn8v3u3c73fudbsg.csv`,
   `dbapmigv3u3c73fudee0.csv`) held the 20 missing tickets (06:00 → 12:21; 16 Akshaya, 4 Shazali Sanober). Only those 20 ticket IDs were
   fed to the script, so no newer row was overwritten by an older one. Oct 18 Day tickets: 23 → 40.
2. **Latest OBH shift is partial** — each update is cut at 23:59 of the last full day, so that night's shift (to 09:00) is finished by the next update. October is complete, including Oct 31.
3. **A different automation on this Mac has been failing every day** (the 09:00 "FRT DATA UCJ" refresh — not part of this
   dashboard). Details in [10-Related-Systems-and-Memory](10-Related-Systems-and-Memory.md).
4. **Key hygiene:** the Google service-account key exists in **two** places on this Mac and should be moved/rotated after the
   account change — see [2-Setup-and-Migration](2-Setup-and-Migration.md).
5. The Day-view exclusion list (4 agents) and the Team Average behaviour are a *decision*, not a rule of nature —
   see [4-Metrics-and-Rules](4-Metrics-and-Rules.md).
