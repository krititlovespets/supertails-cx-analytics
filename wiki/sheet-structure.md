# Sheet Structure (as of 2026-10-08)

Spreadsheet: "Dashboard || Extra", `1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw`.
**Never hardcode a tab name without first calling `sh.worksheets()`** — Kriti
renames tabs directly in the UI.

Real tabs (9) + 3 always-excluded "Chat - *" tabs:

## Main Dashboard (22 rows, ~42 cols and growing by 1/day)

Columns: Metric | September Avg | Avg(Sept16-30) | October Avg | blank | day-by-day
(Sept 1 → latest tracked date).

Row order (rows 2-19, core metrics — see `definitions.md` for each):
Valid Leads, Transfer Total, **Transfer %** (pink), Transfer Done, Doctor Called,
**Absolute Transfer To Do** (red, `=round(VL*0.30)-TransferTotal`), Connect,
**Connect %** (pink), Connect Needed (`=round(VL*0.60)-Connect`),
AHT (Valid Lead), Avg Talk Time per Agent, FRT Valid Leads (9am-8:45pm),
**FRT Avg** (pink), Agents Available, UCJ Bangalore Customer, Booking Done,
**% Booking Done to UCJ Bangalore Customer** (pink), Bookings Needed.

Rows 20-22 (appended, NOT part of the core 02/03/04 pipeline — see
`daily-workflow.md`): Vet Follow-up Transferred, Vet Follow-up 15-Day Repeat,
Vet Follow-up Repeat %.

Pink rows: 4, 9, 13, 17. Red row: 7. (Verify via Sheets API after any row
insert/remove — don't trust these numbers blindly once the structure changes again.)

**Removed from an original 34-row structure** across many 2026-09/10 sessions:
FRT Matched/Median, 9-agent Team Talk block, Daily Transfers + Useful/Extra,
both old AHT blocks, the original 9am-8pm FRT pair (replaced by 9am-8:45pm).

## Ticket Categories (~60 rows, ~41 cols)

NOTE row, header, **TOTAL (All Categories)** block (9 metrics: Count, Connect
abs/%, Transfer abs/%, **Transfer Done, Doctor Called** [TOTAL block only, added
2026-10-05], AHT, Talk Time avg-per-team-agent), then 6 category blocks (7
metrics each, no Transfer Done/Doctor Called breakdown) for
`{PRM D0, Pharmacy False, Pharmacy True} x {Unified Journey, UCJ Booking}`.
Full `ws.clear()` + rewrite every refresh.

## Valid Leads Log (~14,850 rows, 12 cols)

One row per Valid Lead ticket. Columns: ticket_id, created_at, created_date,
agent_name, title, verification_subline, user_phone, found_in_ameyo,
transfer_done, doctor_called, connect_match_talktime30s, last_checked.
Full rebuild every refresh.

## Prediction Model (61 rows, 5 cols)

Restructured 2026-10-05 to add a day-by-day table. Sections: title,
ASSUMPTIONS, DATA BASIS, `ACTUAL, OCT [banked range]`, `TARGET: 30% cumulative`
summary block, then `=== DAY-BY-DAY: TRANSFERS NEEDED, OCT 1-31 ===` —
`Date | Type | Valid Leads | Transfers | Transfer %`, one row per Oct day:
`Actual` for banked days (real figures from Main Dashboard), `Forecast Target`
for remaining days (a FLAT daily quota = forecast_basis x required_rate, same
number every remaining day — deliberate design choice from 2026-09-17, not a
ramp). Forecast basis = October's own actual-to-date average, rolling forward.
30% target only (26% scenario and all September references removed 2026-10-02).

## Callback Adherence / Callback Adherence Dump

Unchanged structure since 2026-09-18. Summary has July/August/September(+
7-30/16-30 subsets)/October/November(future-scheduled)/TOTAL rows x
{Scheduled, Anytime, +/-30min, Transferred} count+% pairs. Dump is one row per
scheduled callback (`cf_callback_ucj`), ~4,800 rows.

## Vet Followup Callback / Vet Followup Callback Dump (new 2026-10-05)

See `vet-followup.md` for the metric definition. Summary tab: NOTE row, header,
15 date rows (rolling last-15-days view, NOT the full history), TOTAL row,
`=== BY CATEGORY ===` block (6 rows). Dump tab: one row per transferred ticket
across the FULL Sept1-latest history (not just the rolling 15 days) — ~4,700 rows.
