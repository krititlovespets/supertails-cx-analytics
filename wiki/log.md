# Ingest / Lint Log

Chronological, append-only. One entry per ingest or lint pass.

---

**2026-10-08 — Initial wiki bootstrap.** Created the project folder
(`/Users/kritituteja/Claude/supertails-cx-analytics/`) and this wiki, per
Kriti's request (she referenced Karpathy's "LLM Wiki" gist:
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). First
ingest distilled the accumulated auto-memory file
(`nugget_ameyo_daily_sheet_workflow.md`, ~400 lines covering 2026-09-16 through
2026-10-07) into 6 topic pages: `definitions.md`, `daily-workflow.md`,
`sheet-structure.md`, `bug-patterns.md`, `external-sources.md`,
`vet-followup.md`, plus `schema.md` and this `index.md`/`log.md` pair.

Same session: also discussed automating the Nugget ticket export via browser
tooling (Kriti walked through the manual UI steps with screenshots) — not yet
built, documented in `external-sources.md`. Kriti said this folder+wiki setup
is "the first step," with a second step still to come.

No lint pass yet — nothing to lint on day one.

---

**2026-10-08, later same day — Confirmed the Nugget export automation works end
to end.** Kriti asked for a live test. Using the Claude in Chrome extension
(already logged in as Kriti): opened `/#/admin/tickets`, confirmed the 3
required channel checkboxes were already correctly set, updated the date range
to Oct 1 → now via "Set current time," opened Export, confirmed all 55/141/18
ticket/property/user fields were selected, clicked Export → "Request submitted
successfully." The ready email landed in Gmail in ~1 minute (much faster than
the UI's "15-20 minutes" warning), clicked the "here" link, CSV downloaded to
`~/Downloads/` automatically. Verified the downloaded file directly: 5,444
rows, exactly the 3 correct channels, Oct 1-7 counts matching what's already
tracked (Oct 7 at 679 vs our 678 — nearly settled) plus a fresh partial Oct 8
(206 rows). **This closes the open TODO in `external-sources.md` — the browser
automation path is proven and can replace waiting for Kriti to manually run and
attach the CSV each day**, though nothing has been wired up yet to do this
automatically/on a schedule — that's still a manual trigger per session.

---

**2026-10-08, later same day — "second step": confirmed the Ameyo CALL Details
export also works end to end via browser automation.** Kriti gave the manual
UI walkthrough (Reports → Queue → Re-Run → edit End Date → tick CSV → Run →
wait for SUCCESS → click CSV icon) with screenshots. Ran it live: Re-Run on the
most recent "CALL Details" queue entry, edited End Date to the current time
(typing directly into the field, since the date-picker's calendar view resets
the time to 00:00), ticked CSV, clicked Run. Status went WAITING → QUEUED →
SUCCESS in ~41 seconds (required manually navigating away and back to Queue to
see the status update — no auto-poll). Clicked the CSV icon, file downloaded
to `~/Downloads/` automatically. Verified contents directly: 17,703 rows,
Oct1-7 exactly matching already-tracked counts, plus a fresh Oct8 partial (746
rows). Documented the full flow in `external-sources.md`.

**Both halves of the daily refresh input (Nugget ticket export + Ameyo
call-detail export) are now proven to work via Claude in Chrome automation.**
This was the second of the two steps Kriti said she'd give. Nothing has been
wired into a scheduled/automatic trigger yet — both are still manual-per-session,
run when explicitly asked.

---

**2026-10-08, immediately after — Kriti: "so now every day your thir step
should be to take both the downloads and updated the dashboard and sheets."**
New STANDING INSTRUCTION, documented at the top of `daily-workflow.md`: pull
both exports via browser automation as step 1-2, then run the refresh pipeline
as step 3 — every day, by default, not just when explicitly asked to pull files.
Immediately executed this as the first live run of the new routine, using the
exact files just pulled in the two prior ingests (`db3j4q5ctnfs73d4tqs0.csv` +
`CALL_Details_2026-10-08_11_46_51(...).csv`). New scratch dir `oct8b_refresh`.
Oct1-6 stable; Oct7 +1 ticket, 11 more channel drifts (expected ongoing
pattern). Ran the full 8-tab pipeline. **Final Oct1-7 figures**: Valid Leads
393/410/406/365/388/362/**349** (Oct7 ticked down 356→349 from drifts).
Transfer% 30.8%/28.3%/25.1%/28.8%/29.1%/31.5%/**15.8%**. Connect%
56.2%/57.6%/57.6%/56.2%/64.7%/66.0%/46.4%. Prediction Model: 7 banked days,
2,673 leads/726 transfers=27.2%, required rate 30.8%.

**Worth flagging on the NEXT refresh**: Oct7's Transfer% (15.8%) still hasn't
climbed the way Oct5 (→29.1%) and Oct6 (→31.5%) did after a few refresh
cycles — it's been low across 4 consecutive refreshes now (15.1% partial →
15.4% → 15.4% → 15.8%). Every other recently-tracked day self-corrected
upward within 1-3 refreshes once it had enough forward-matching data; Oct7
hasn't yet. Keep watching — if it's STILL stuck low after another refresh or
two, that would be worth investigating as a genuine anomaly rather than
assuming it'll self-correct like the others did.

Cross-tab validation passed exactly as always (Valid Leads Log Oct1-7 =
393/410/406/365/388/362/349 == Main Dashboard; log total 14,842 rows).

---

**2026-10-08, 12:40pm — first fully scheduled run, fired by the 12:08pm cron
job.** Pulled both exports myself via browser automation (no files attached by
Kriti this time — this is the standing instruction working as intended):
Nugget (5,506 tickets, "here" link clicked via Gmail) and Ameyo CALL Details
(Re-Run → edit End Date → tick CSV → Run → SUCCESS in ~69s → CSV icon). One
hiccup: a fresh browser tab opened for the Gmail navigation landed on an
unrelated "Attendance- CX" Google Sheet instead (stale tab state, not a
real redirect) — did NOT interact with it, re-navigated directly to the Gmail
URL, which then worked correctly. Oct1-7 fully stable (2 minor channel drifts
only) — confirms the `oct8b_refresh` data from ~1 hour earlier had already
settled. Oct8 still very early (268 nugget / 970 ameyo rows at 12:40pm,
excluded as before). New scratch dir `oct8c_refresh`. Ran the full 8-tab
pipeline — all values identical to the prior refresh (393/410/406/365/388/
362/349 leads, same Transfer%/Connect%), as expected given 0 real data change.

**Oct7's Transfer% is STILL 15.8%, unchanged from the last refresh** — but
this is expected and not yet concerning: Oct8's data barely grew between the
two pulls (746→970 Ameyo rows, roughly the same ~1-hour window), so there
wasn't meaningfully more forward-matching data available to move it. The
"worth investigating if still stuck" flag from the prior entry should be
re-evaluated once Oct8 itself is much further along (e.g. the 5pm or 10pm
scheduled run), not based on this one.
