# External Sources

## Clinic Dashboard sheet (Booking Done source)

`1EyTmbBSkZMvL5JolKuo8xxOkguYGUKpTJTzlN68n5hM`, tab `Agent_Perf_V2`. Service
account confirmed has read access (verified 2026-10-02). Row matched by columns
A/B/C == `('TOTAL (UCJ only)', 'UCJ', 'Appts created')` — don't hardcode the row
number, it can shift if the clinic team edits their sheet. Daily columns start
after a block of month/week totals; find each target date's column by scanning
row 4 for its `DD/MM/YYYY` string, don't hardcode the column index either.
"Appts created" on this row IS what this workbook calls "Booking Done" (confirmed
exact match against a manually-pasted reference set on 2026-10-02).

## Nugget admin ticket export (manual UI flow, documented by Kriti 2026-10-08)

URL: `https://supertails.nugget.com/#/admin/tickets`

1. Click the **Filters** control.
2. In the channel filter, tick the checkboxes (not the names) for all 3:
   `UCJ SC Chat Assistance`, `Unified Customer Journey`, `UCJ Booking Campaigns`.
   Click **Apply**.
3. Go to **Sort tickets** → the "Created In" date dropdown → select
   **Custom date and time**.
4. Set the From/To range to the window being pulled (e.g. month start to the
   current pull time). Max selectable range is 1 month + 1 day. Click **Apply**.
5. Click the **Export** (share/upload icon) button.
6. In the export dialog, tick **all** ticket fields, property fields, and user
   fields (Select All on each section). Click **Export**.
7. Go to Gmail (`https://mail.google.com/mail/u/0/?ogbl&hl=en_GB#inbox`), open
   the latest "**Your Ticket Export is Ready**" email, click the **here** link —
   the CSV lands in Downloads.

Note: this export includes the `UCJ SC Chat Assistance` channel, which is NOT
part of this workbook's analysis scope anywhere (see `definitions.md`) — always
filter it back out.

**CONFIRMED WORKING end-to-end via browser automation, 2026-10-08.** Using the
Claude in Chrome extension (Kriti already logged in), ran the full 7-step flow
above live: filters were already correctly set, updated the date range via
"Set current time," triggered the export, and the ready email landed in Gmail
in ~1 minute (not the 15-20 min the UI warns about). Clicked "here," CSV landed
in `~/Downloads/` automatically. Verified the downloaded file's actual contents
matched the request exactly (5,444 rows, correct 3 channels, correct date
coverage). **This means Nugget export no longer strictly requires Kriti to run
it manually and attach the CSV — it can be pulled directly via browser tooling
when needed.** Not yet wired into a scheduled/automatic routine — still a
manual trigger per session as of this writing.

## Ameyo CALL Details export (manual UI flow, documented by Kriti 2026-10-08)

URL: `https://emergeapp5.ameyoemerge.in:8443/app/?campaign=493#!LiveMonitoring`
(campaign ID in the URL may need to change if Kriti's default campaign changes).

1. Click **Reports** in the top nav.
2. Click **Queue** (under Home/Queue/Compare).
3. Find the most recent **"CALL Details"** row in the Report Queue and click its
   **Re-Run** icon (green circular arrow) — this reuses that report's saved
   parameters (campaigns, optional fields, etc.) as a starting point rather than
   configuring from scratch.
4. On the parameter form: the Start Date carries over from the last run (keep
   it, usually `10/01/2026 00:00`-equivalent — the first of the current month).
   Update the **End Date** field to the current date/time — triple-click the
   field and type the new value directly (format `MM/DD/YYYY HH:mm`, 24-hour);
   clicking into the date-picker calendar resets the time portion to 00:00, so
   typing the full string directly is more reliable than using the picker.
5. Tick the **CSV** checkbox under "Output Formats" (top of the page).
6. Click **Run** (top right).
7. This returns to the Report Queue; the new row shows **WAITING** → (after a
   browser refresh — navigate Home then back to Queue, or reload; it does not
   auto-poll) **QUEUED** → **SUCCESS**, typically within ~30-45 seconds.
8. Click the **CSV** icon on the SUCCESS row — the file downloads automatically
   to `~/Downloads/` as `CALL_Details_<timestamp>(runnableReportId...).csv`,
   same naming/format as every manually-provided Ameyo file this whole engagement.

**CONFIRMED WORKING end-to-end via browser automation, 2026-10-08** (same
session as the Nugget confirmation above): Re-Run → edited End Date to
11:50 → ticked CSV → Run → WAITING → QUEUED → SUCCESS (~41s) → downloaded.
Verified contents: 17,703 rows, Oct1-7 counts matching exactly what's already
tracked (2097/2267/2337/2496/2690/2519/2551), plus a fresh Oct8 partial (746
rows). **Both halves of the daily data pull (Nugget ticket export AND Ameyo
call-detail export) are now proven to work via browser automation** — the full
daily refresh could in principle be run without waiting for Kriti to manually
pull and attach either file. Still manual-trigger-per-session, not scheduled.
