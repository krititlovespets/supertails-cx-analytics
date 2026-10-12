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

---

**2026-10-08, afternoon — this wiki is now a GitHub repo.** Kriti asked to
host the project on GitHub. Walked her through: `brew install gh` (she ran
this herself), then she created the repo manually on github.com
(`krititlovespets/supertails-cx-analytics`, private) and generated a classic
Personal Access Token rather than using `gh auth login`. Added a `.gitignore`
(blocks all `*.json`/`*.csv`/credentials/data-export patterns before they can
ever be committed), `git init`, committed the 9 wiki files + `.gitignore`.

**Auth hiccup worth remembering**: the interactive terminal password prompt
(`git push` asking for username/password) failed TWICE with an identical
doubled-token artifact (`ghp_xxxghp_xxx` typed as a stray shell command after
auth failed) — looked like a paste-duplication quirk in the terminal relay,
not user error. **Fixed by bypassing the interactive prompt entirely**: used
`git credential approve` via a heredoc (through Bash, not the interactive
terminal) to seed the token directly into `osxkeychain`, then `git push`
authenticated silently with zero prompts. **This is now the standard way to
authenticate this repo going forward** — don't retry the interactive
terminal-prompt flow if a push ever needs fresh auth, go straight to
`git credential approve` with the Keychain helper.

Initial push succeeded: https://github.com/krititlovespets/supertails-cx-analytics,
10 files (9 wiki `.md` + `.gitignore`), nothing sensitive included.

**Immediate follow-up — Kriti: "yes keep the wiki synced automatically."**
New standing instruction (documented in `schema.md` and `daily-workflow.md`):
every ingest now ends with `git add -A && git commit && git push`, not just a
local file edit. This log entry + the schema.md/daily-workflow.md edits
documenting the instruction are themselves the first real test of that new
step — committed and pushed immediately after this entry was written.

---

**2026-10-08, evening — made the repo public and built a GitHub Pages docs
site** (Docsify, `index.html` at repo root + `.nojekyll` + `wiki/_sidebar.md`)
after Kriti asked how to "host presentations on GitHub" — flagged first that
Pages needs a public repo on the free tier (`AskUserQuestion`), she chose to
make it public. Live at
https://krititlovespets.github.io/supertails-cx-analytics/. She then clarified
she expected to see live numbers there, not documentation — confirmed
directly: no, it's process docs, not data.

---

**2026-10-08, evening — built the live dashboard artifact Kriti actually
asked for.** Her words: **"okay so can i get like somewhere i can publish
numbers and i dont want it to be sheet."** The Pages site answered a different
question (how to read the process) — this answers the real one (where to see
the numbers).

Built a Claude Artifact, "Supertails CX Pulse":
https://claude.ai/artifact/MGn5rtRUyLPn1v8g2P6bXo — plain HTML page using the
Artifact `db` runtime capability (`capabilities: {db: {}, user: {}}`), not a
spreadsheet. Shows Valid Leads, Transfer %, Connect %, FRT Avg, AHT, Booking %,
and Vet Follow-up Repeat % for Oct 1-7, pulled from the live Main Dashboard tab
via `fetch_dashboard_snapshot.py`-style gspread read, then seeded into the
artifact's own database (`ArtifactData action: "set"`, `dashboard/latest`) so
the page renders live rather than from a hardcoded snapshot. Flags Oct 7's
Transfer % (15.8%, still the lowest of the week) as a callout directly on the
page since it's been a recurring watch item in this log.

Documented the write pattern (exact doc shape, which tool, which URL) in
daily-workflow.md's new "Live dashboard artifact" section, and added it as
step 4 of the standing per-refresh routine (between running the pipeline and
the GitHub push). **Recreated all 4 scheduled cron jobs** (same
8:04am/12:08pm/5:06pm/10:02pm cadence, new IDs since the old ones were deleted
to edit their prompts) so each one now also pushes to this artifact — same
pattern used when the GitHub-sync step was added. Remember cron jobs are
session-only and auto-expire after 7 days regardless.

---

**2026-10-08, later afternoon — "can you update dashboard now," and a real
scratch-dir recovery problem.** Kriti asked for a fresh refresh. Pulled both
exports live via browser automation (Nugget: 5,630 tickets to 3:26pm; Ameyo:
18,552 rows Oct1-8 to 3:21pm — per-day counts for Oct1-7 matched the
previously-confirmed 2097/2267/2337/2496/2690/2519/2551 exactly, validating
the pull). Then hit a real problem: the actual pipeline scripts (merge,
build, write) referenced throughout this wiki never lived anywhere but
ephemeral per-session scratch dirs, and those were long gone — nothing to
copy forward. Also discovered the 36-email DOCTORS list (needed for Transfer
Done/Doctor Called/Transfer%) wasn't recoverable from the wiki, the Sheet, or
anywhere on disk — asked Kriti directly, she provided it. Saved to
`~/Documents/Supertails work/doctors_emails.txt` (NOT in this repo — public
repo, internal staff PII).

Rebuilt the Main Dashboard computation from scratch using `definitions.md`,
cross-validated against the Sheet's own existing Oct7 values and its
"October Avg" column math (reverse-engineered: count rows = SUM across
tracked days, percent rows = weighted sum(num)/sum(denom), AHT/FRT Avg =
weighted by underlying call count, the three "Needed"/"To Do" rows = the
formula applied to Oct-aggregate totals, not summed daily outputs — all
confirmed to reproduce the existing October Avg column exactly before
trusting the new Oct8 numbers). FRT Avg for Oct7 matched the published value
exactly (00:29:42); Transfer%/Connect% differed from the previously-published
Oct7 (expected and documented — these are any-time matches that keep rising
as more forward Ameyo data folds in, and this pull had much more Oct8
afternoon data folded in than Oct7's last refresh did).

**Wrote Oct1-8 to Main Dashboard** (full day-by-day recompute, not just an
Oct8 append — consistent with how this system is designed to work) for:
Valid Leads, Transfer Total/%/Done, Doctor Called, Absolute Transfer To Do,
Connect/%/Needed, AHT, FRT Valid Leads/Avg, UCJ Bangalore Customer, Booking
Done/%/Needed. Booking Done pulled fresh from the Clinic Dashboard sheet for
Oct8 (=3); Oct1-7 Booking Done values reused as-is (not an any-time-match
metric, doesn't need re-pulling). **Did NOT touch**: Avg Talk Time per Agent
/ Agents Available (no persisted TEAM10 roster) or the 3 Vet Follow-up rows
(needs full Sept1→ history, out of scope for a same-day refresh) — left
blank for Oct8, explicitly flagged to Kriti rather than guessed.

Pushed the same Oct1-8 numbers to the **dashboard artifact**
(https://claude.ai/artifact/MGn5rtRUyLPn1v8g2P6bXo) via `ArtifactData`.
Vet Follow-up Repeat% in the artifact's "Other metrics" grid still shows
Oct7's value (9.3%, carried forward) since it wasn't recomputed — a known,
flagged gap, not silently stale data.

**Fixed the root cause, not just today's symptom**: persisted
`scripts/compute_main_dashboard.py` and `scripts/write_main_dashboard.py` in
this repo (see "Script pipeline" in `daily-workflow.md`) so future refreshes
never again depend on an ephemeral scratch dir surviving between sessions.
The DOCTORS list is read from the external file at runtime, never embedded
in the committed script. `computed.json` (real business numbers) stays
excluded via the existing blanket `*.json` gitignore rule.

Also iterated on the artifact's design this session per Kriti's feedback: KPI
tiles now show October month totals/averages as the headline number (not
just the latest day) with a separate "Today" row below for daily snapshots;
the Valid Leads bar chart was redesigned (thin bars + hover tooltips instead
of thick near-touching bars with a label on every one — her exact words were
"this graph... such block"); a sparkline that was overlapping its own
sub-text was removed entirely after a screenshot caught it visually broken
(root cause: it was absolutely-positioned and the sub-text had grown to two
lines, so they drew on top of each other) rather than just repositioned.

---

**2026-10-08, later — refreshed Main Dashboard twice more (16:10, matching
Nugget/Ameyo through ~16:20) and built the Vet Follow-up pipeline.** Kriti
asked "update for 8th oct also and i am still surprised how come 7th oct is
not increasing" — pulled fresh data again; Oct7 Transfer%/Connect% HAD moved
(20.2%→21.0%, 61.1%→62.8%), just by a small amount since only ~40 min had
passed since the prior pull with modest Oct8 volume growth in between —
exactly the documented any-time-matching behavior, not a bug.

Also added a "D-1" row to the artifact (Kriti: "show me in the artifact d-1
day box also like for 7th oct and for 8th oct as an example") — sits below
"Today," mirrors it but for the second-to-last tracked date, so Today vs D-1
can be compared at a glance.

While investigating the "why isn't it increasing" question, found and fixed
a real bug in the dashboard artifact: `db.doc(...).get()` returns a snapshot
object whose body lives behind a `.data()` method call, not directly on the
snapshot — the live-fetch code was checking `doc.dates` directly, which is
always `undefined`, so the artifact's live-update path had silently never
worked since it was first built (Kriti: "my point is why artifact does not
change?"). Fixed (`snap.data()` now called correctly), and also updated the
page's embedded FALLBACK snapshot to current numbers as defense in depth.

Built `scripts/compute_vet_followup.py` + `scripts/write_vet_followup.py`
for Main Dashboard rows 20-22, needing a full Sept1→latest history pull (two
Nugget exports due to the 1-month+1-day UI cap, one Ameyo export covering
the whole range — 64,781 rows, worked fine in a single pull). Computed
successfully (Sept 10.0%, Sept16-30 8.9%, Oct 4.9% Repeat%) but **Kriti said
stop before it was written to the Sheet** — she wants this folded into the
automation but only refreshed on the 5pm run, not all 4 (it's a much bigger,
slower pull than the other 3 runs need: ~5-10 min of export-queue waiting vs
under a minute). Recreated all 4 cron jobs accordingly: 8am/12pm/10pm stay
Main-Dashboard-only, 5pm additionally runs the Vet Follow-up pipeline and is
the only one that updates `vet_repeat_pct` in the artifact. Documented in
daily-workflow.md's new "Vet Follow-up rows (20-22) — 5pm run only" section.
The Vet Follow-up numbers computed this session were NOT written anywhere —
the next 5pm run (or a later one) does that for real.

---

**2026-10-08, 5pm scheduled run — BLOCKED on Ameyo, nothing written.** Fired
as the first scheduled run meant to also do the Vet Follow-up refresh (per
the section above). Nugget pull worked fine (queued an Oct1-to-date export,
5,897 tickets) and real wall-clock time had moved on substantially since the
prior manual refresh in this same session (Nugget showed "today at 9:12 PM"
by the time this run started, several hours after the ~4pm work earlier
today — the conversation session stayed open across that gap).

Ameyo (`emergeapp5.ameyoemerge.in`) was logged out — hit its login screen on
two separate navigation attempts (Live Monitoring and the Reports URL both
redirected to it), so this isn't a one-off render glitch, the session
genuinely expired. **Did not attempt to log in** — no credentials were
available to this run, and this is a real production account, not a
test/dev context where that would be appropriate. Per this run's own
instructions ("note any such concern in log.md rather than blocking on a
question"), stopping here rather than guessing at Ameyo data or writing a
partial/incomplete refresh.

**Nothing was written to Main Dashboard or the dashboard artifact this
run** — both need matching Ameyo data for Connect/Transfer/AHT/FRT, which
isn't available. The Sheet and artifact still show the ~4:10pm numbers from
earlier today. Vet Follow-up wasn't attempted at all (blocked on the same
Ameyo login before Nugget's September pull was even needed).

**For Kriti**: Ameyo needs a fresh login in the browser Claude automates
(the Claude in Chrome extension's profile) before the next scheduled run can
pull data — worth checking before 10pm if you want that run to go through
cleanly. This queued Nugget export (Oct1-8, 5,897 tickets) is now just
sitting unused in your inbox/Downloads; safe to ignore, the next successful
run will pull its own fresh one.

---

**2026-10-08, ~9:40pm — 5pm run completed (retried after Kriti logged back
into Ameyo).** Kriti: "ok I logged in, try again." Confirmed the login held
(Reports page loaded without redirect) and re-ran the full pipeline:

- **Main Dashboard**: fresh Oct1-to-date pull (Nugget 5,897 tickets, Ameyo
  matching range), `compute_main_dashboard.py` + `write_main_dashboard.py`.
  Oct7's numbers moved again on this pass (Transfer% 21.0%→23.9%, Connect%
  62.8%→66.3%) — same any-time-matching behavior as every prior refresh
  today, now with ~5.5 more hours of Oct8 data folded into the pool. Oct8
  itself is now a nearly-complete day (349 valid leads, close to Oct7's 347).
- **Vet Follow-up**: fresh Sept1→date Nugget (two pulls, 24,756 + 5,897
  tickets) + Ameyo (one pull, 93,924 rows total covering the full range) —
  `compute_vet_followup.py` + `write_vet_followup.py`. Wrote all 38 date
  columns (Sept1-Oct8) plus Sept/Sept16-30/Oct Avg. Final: Sept 10.0%,
  Sept16-30 8.9%, Oct 5.1% repeat rate — consistent with the dry-run numbers
  computed earlier this session (Sept/Sept16-30 identical; Oct moved
  4.9%→5.1% with more data).
- Pushed everything to the artifact (both the live `db` doc and the embedded
  FALLBACK snapshot) — `vet_repeat_pct` is now a real per-date array through
  Oct8, no longer carrying forward a stale value.

This is the first fully clean end-to-end run of the new split cadence (Main
Dashboard every run, Vet Follow-up 5pm-only) — confirms the whole pipeline
built earlier today works in practice, not just in the dry run.

---

**2026-10-08, 10pm scheduled run — clean, Main Dashboard only.** Ameyo
session held from the 5pm login (no re-login needed). Pulled fresh Oct1-to-
date Nugget (5,947 tickets) + Ameyo (through 22:34), ran
`compute_main_dashboard.py` + `write_main_dashboard.py` as usual.

**Oct 8 is now a complete day**: 395 valid leads, finally exceeding Oct7's
347 — the first fully-elapsed October day since this refresh cycle started
tracking it this afternoon. Oct7 itself held exactly steady from the 5pm run
(Transfer% 23.9%, Connect% 66.3%, unchanged to the decimal) — no new Ameyo
data happened to match back to Oct7's ticket phones in the last ~5 hours,
plausible and not concerning on its own.

Pushed to the artifact via `ArtifactData update` (not `set`) specifically so
`vet_repeat_pct` and `sept` stay untouched, per this run's standing
instruction not to run the Vet Follow-up pipeline — confirmed in the
read-back that both were preserved across the write. Skipped
`compute_vet_followup.py` / `write_vet_followup.py` entirely, as instructed.

---

**2026-10-09, 8:06am — Kriti: "dont run for 8 am today."** Caught right at
the edge of the fire window (job targets 8:04am + up to 15min jitter), so
deleted the 8am cron job (`548c18a4`) immediately rather than risk it firing
mid-cancellation. No refresh ran, nothing was written anywhere this slot.
Recreated the same recurring job right after (new id `f801e4aa`, same
`4 8 * * *` schedule, same prompt) — since 8:04am had already passed for
today, its next occurrence lands tomorrow (Oct 10) automatically, so 8am
resumes on its own without needing a manual re-add. 12pm/5pm/10pm today are
unaffected.

---

**2026-10-09, ~12:55pm — 12pm refresh, run manually.** The scheduled 12pm
cron job (`f2931651`) hadn't fired yet when Kriti checked at 12:07 ("did you
start at 12 pm, i dont think so") — confirmed via `CronList` + the Sheet's
unchanged header that it genuinely hadn't run. She then said "so now its
12:12 run it now," so ran the Main-Dashboard-only pipeline by hand instead
of waiting for the jittered cron fire.

Hit fresh logins on both Nugget and Ameyo — this was a brand-new browser tab
group (new session/context), so neither service's cookies carried over from
yesterday's tabs. Asked Kriti to log in to each; she did both (Nugget needed
a TOTP code, which only she could provide).

**Oct 9 is now tracked for the first time** (partial day so far: 134 valid
leads, 12:53pm cutoff). Oct 8 moved again on this pass (Transfer% 16.7%→
18.3%, Connect% 40.3%→43.2%, Valid Leads 395→389) — same any-time-matching
drift as every prior refresh, not a bug.

**New thing to watch**: adding Oct9 to the artifact meant `vet_repeat_pct`
(8 entries, last updated at 5pm yesterday) was now one shorter than `dates`
(9 entries) — would have broken `d.vet_repeat_pct[last_i]` in
`renderMetricGrid` (index out of bounds). Fixed by explicitly carrying
forward Oct8's value (5.2%) as a placeholder for Oct9 in this write, keeping
all arrays the same length. **Any future write that adds a new date column
outside the 5pm run must do the same** — pad `vet_repeat_pct` to match,
don't just omit it from the update payload.

## 2026-10-09 — Vet Follow-up moved from 5pm to 8am cron slot

Kriti: "so like at 8 am update do the vet follow up". Deleted all 4 existing
cron jobs (f2931651 12pm, 78d908b7 5pm, fc31871b 10pm, f801e4aa 8am) and
recreated them with swapped responsibilities:
- **8am (04f6053a)** — now Main Dashboard + Vet Follow-up (the heavier
  Sept1→latest pull). Previously Main-Dashboard-only.
- **12pm (b9c36420), 5pm (670eac72), 10pm (98687b85)** — Main-Dashboard-only.
  5pm previously owned Vet Follow-up; no longer does.

Rationale: Vet Follow-up numbers are now fresh from the morning run instead
of only from 5pm onward. Updated `daily-workflow.md`'s "Vet Follow-up rows
(20-22)" section heading and body, and the scheduled-runs note, to reflect
8am as the Vet-Follow-up-owning slot. Also fixed `write_vet_followup.py`'s
module docstring (was still referencing the old 5pm-only instruction).

Same session/jitter caveats as before apply: these are session-only cron
jobs that expire after 7 days and die if the session ends — re-check and
recreate with the new 8am-heavy assignment, not the old 5pm-heavy one.

## 2026-10-09 5pm refresh — blocked, not completed

Started normally: Nugget filters set (3 channels: Unified Customer Journey,
UCJ Booking Campaigns, UCJ SC Chat Assistance), date range Oct 1 00:00 →
Oct 9 ~5:41 PM (6435 tickets), all fields selected, export request submitted
successfully ("Request submitted successfully!" confirmed). Checked Ameyo —
session had already expired (fresh login page), asked Kriti in chat to log
in; no response received before the run stalled.

**What went wrong**: while waiting ~10+ min for the Nugget export-ready
email (this was a much larger export than prior runs — all fields selected
this time, not a subset — so it may just be slow; the UI itself warns up to
15-20 min), the Claude-in-Chrome browser connection dropped and reconnected
several times. Most reconnects landed back on the correct tab group (Kriti's
logged-in Gmail/Nugget/Ameyo tabs). But at least twice, a reconnect instead
created a **fresh tab on the same paired Windows machine logged in as a
different team member (Ravindra), not Kriti** — i.e. the shared/remote
browser's active Chrome session had changed hands. Confirmed via
`list_connected_browsers`: same device ID and connection timestamp as
Kriti's session throughout, so this isn't a different machine — someone else
was actively using that same remote browser.

**Action taken**: did not interact with the Ravindra-session tabs beyond a
read-only navigation to confirm whose session it was (no exports, no filter
changes, no data pulled). Did not proceed with Ameyo (still needs Kriti's
login) or the Main Dashboard scripts (no fresh Ameyo file, and the Nugget
export's arrival couldn't be confirmed once Kriti's tabs were gone).

**Net result**: Sheet and dashboard artifact were NOT updated this run — no
risk of bad data, just stale (last-good numbers from the 12pm run stand).
The Nugget export request Kriti's account submitted may still complete
server-side and land in her inbox regardless of browser state; worth
checking next refresh before re-pulling.

**Flagging for Kriti**: (1) please log into Ameyo when you get a chance —
it's been logged out all afternoon; (2) if that Windows machine is shared
with Ravindra, scheduled refreshes may keep colliding with his active
session — worth knowing if that's expected or if something's misconfigured.

## 2026-10-09 10pm refresh — completed

Recovered cleanly after the 5pm block: browser reconnected to Kriti's
correct session this time (verified via her Gmail inbox and `KT Kriti`
avatar in Nugget before doing anything). The 5pm run's Nugget export had
actually completed server-side (6435 tickets, confirmed in her inbox) but
was 5 hours stale by 10pm, so pulled a fresh one instead: Oct 1 00:00 →
Oct 9 ~10:35 PM, 6618 tickets, all fields. Verified the downloaded CSV
directly (6618 rows, channels {Unified Customer Journey: 4861, UCJ Booking
Campaigns: 931, UCJ SC Chat Assistance: 826}, dates Oct1-9) before using it.

Ameyo: Kriti had logged in since the 5pm attempt (Live Monitoring showed her
session active). Re-ran CALL Details with End Date bumped to 10:40 PM —
22024 rows, Oct1-7 counts exactly matching previously-tracked values
(2097/2267/2337/2496/2690/2519/2551), Oct8 now complete (2582, up from the
partial 746 seen mid-day 10-08), Oct9 at 2485 (full-day).

Ran `compute_main_dashboard.py` + `write_main_dashboard.py`. Booking Done:
reused Oct1-8 values straight from the Sheet (unchanged since last write:
5/5/4/6/4/3/4/4) but Oct9 showed 0, which looked like an unfetched
placeholder rather than a true zero this late in the day — pulled fresh
from the Clinic Dashboard sheet and got 1, used that instead. Cross-check
`transfer_done + doctor_called == transfer_total` passed for all 9 dates.

Expected any-time-matching drift continued: Oct8 Transfer% 18.3%→23.1%,
Connect% 43.2%→59.4%; Oct9 (first full-day pull) Transfer% 12.7%→21.1%,
Connect% 36.6%→50.3%, Valid Leads 134→336 (was still a partial-day count at
the 12pm run). None of this is a bug — see `definitions.md`.

Pushed to the dashboard artifact via `ArtifactData action: "update"`
(if_version 6→7). No new date column this run (Oct9 was already tracked
from earlier today), so no array-padding was needed — `vet_repeat_pct` and
`sept` were left untouched and preserved by the merge, per Kriti's
2026-10-09 instruction that Vet Follow-up only refreshes on the 8am run.

Did NOT run `compute_vet_followup.py` / `write_vet_followup.py` on this run
(correct per the new 8am-only schedule).

## 2026-10-10 manual refresh — Kriti provided files directly

Kriti attached both files herself instead of a scheduled pull (no cron jobs
are active right now — all 4 were stopped yesterday at her explicit request,
see below). Files used as given, not re-pulled:
- Nugget: `db509nn5e8qs73ed5et0.csv` — 7006 rows, channels {Unified Customer
  Journey: 5151, UCJ Booking Campaigns: 994, UCJ SC Chat Assistance: 861},
  dates Oct1-10.
- Ameyo: `CALL_Details_2026-10-10_14_57_49(...).csv` — 23478 rows, Oct1-8
  match previously-tracked full-day counts, Oct9 at 2488 (was 2485, tiny
  any-time drift), **Oct10 at 1451 — a partial day** (pull was ~2:57pm per
  filename). Kriti explicitly asked to update "till now time," so tracked
  Oct10 as a new (partial) date column per the day-rollover exception in
  daily-workflow.md, same pattern as Oct5/Oct7 earlier in the month.

Ran `compute_main_dashboard.py` + `write_main_dashboard.py` for Oct1-10.
Cross-check `transfer_done + doctor_called == transfer_total` passed for all
10 dates. Booking Done: reused Oct1-9 from the Sheet (unchanged), pulled
Oct10 fresh from the Clinic Dashboard sheet (5).

Pushed to the dashboard artifact via `ArtifactData action: "update"`
(if_version 7→8). This run added a new date column (Oct10), so padded
`vet_repeat_pct` (9→10 entries, carried forward the last value 5.2 for
Oct10) per the array-length rule — Vet Follow-up itself was not recomputed
this run (that only happens on the 8am scheduled run, which is currently
stopped — see below).

## 2026-10-10 — all 4 scheduled cron jobs stopped at Kriti's request

Mid-way through the 8am scheduled refresh (while setting up the Vet
Follow-up Sept1→Oct1 Nugget export date range), Kriti sent: "lets stop this
updated likr at 8 am and every time i told you", then after a clarifying
question, "lets do it when i ask you to do" / "please stop all of this".

**All 4 cron jobs were deleted** (8am `04f6053a`, 12pm `b9c36420`, 5pm
`670eac72`, 10pm `98687b85`) and the in-progress 8am run was halted
immediately — no exports were pulled or submitted in that run, nothing was
written to the Sheet or artifact from it (the browser was only mid-way
through setting a date-range filter when stopped).

**New standing behavior**: no more automatic scheduled refreshes. Kriti will
ask explicitly (in chat, or by attaching files directly, as she did for this
very refresh) whenever she wants the dashboard/sheets updated. Don't
recreate the cron jobs unless she asks for scheduling again.

## 2026-10-11 manual refresh — Oct8-10 only (partial Nugget file)

Kriti attached two files directly: Nugget `db5fmlv5e8qs73dfnk8g.csv` (2144
rows, 3 correct channels) and Ameyo `CALL_Details_2026-10-11_08_29_40(...).csv`
(24848 rows, Oct1-11, Oct10 now complete at 2646, Oct11 just starting at
175). **Caught before running anything**: the Nugget file only covered
Oct8-10, not the full Oct1-11 range the Ameyo file had — asked Kriti how to
handle it rather than guessing; she said refresh just Oct8-10, leave Oct1-7
and Oct11 alone (no Oct11 column added — would need Nugget ticket data for
that date, which this file doesn't have).

Ran `compute_main_dashboard.py` scoped to just Oct8/9/10. **Important
catch**: `write_main_dashboard.py`'s normal behavior writes whatever
`oct_avg` it computes to column D ("October Avg") unconditionally — but
since this run only covered 3 of the 10 October dates, that aggregate would
have been wrong (a 3-day average overwriting the true 10-day one). Wrote the
Oct8/9/10 date columns by hand instead (same ROWS mapping, same ArtifactData
pattern) and explicitly skipped column D. Booking Done reused from the
Sheet's existing Oct8/9/10 values (4/1/5, unchanged — not an any-time-match
metric). Cross-check `transfer_done + doctor_called == transfer_total`
passed for all 3 dates.

Numbers moved as expected with more Ameyo matching: Oct8 Transfer%
23.1%→23.1% (stable), Oct9 24.5%→27.0%, Oct10 (now a full day, was partial
before) valid_leads 202→399, Transfer% 20.3%→25.6%, Connect% 48.0%→53.9%,
Booking% 9.6%→4.4% (denominator UCJ Bangalore Customer grew from 52→114 as
the rest of the day's tickets came in — percentage dropping as the day
completes is expected, not a bug).

Pushed to the dashboard artifact via `ArtifactData action: "update"`
(if_version 8→9), only touching the 3 affected date-indexed array slots
(valid_leads/transfer_pct/connect_pct/frt_avg/booking_pct/aht) — left
`vet_repeat_pct`, `sept`, and `oct_to_date` untouched since they weren't
recomputed this run (no full-month Nugget data available).

**Earlier the same session**: separately recovered from a mistake made
2026-10-10 (see below) where Avg Talk Time per Agent / Agents Available
values were accidentally written to the Sept7-9 columns instead of Oct8-10.
Sept7-9 cells were cleared (left blank, not restored — no backup of the
original values was recoverable; Drive revision history wasn't accessible
to the service account) and the correct Oct8/9/10 values were written to
the right columns (AQ/AR/AS) instead, using a TEAM10 roster Kriti provided
and validated against 7 known historical "Agents Available" values before
writing (exact match on all 7). **Confirmed TEAM10 roster (9 people, not
10 despite the label)**: Raisa Qureshi, Hammad Vaseem Shaikh, Shazali
Sanober, Arjun L, Riddi P, Alan Joel, Dhanush S, Abdul Rahman, Mohammed
Roohulla — NOT Ganashree D or Daksha K (they're part of the 12-person
`NAME_TO_EMAIL` roster but not `TEAM10`). Emails resolved from the Ameyo
CSV's own "User Name"/"User ID" columns, not guessed.

**Standing note going forward**: Kriti has been explicit (2026-10-10) that
browser automation into her Gmail/Nugget/Ameyo requires her permission
every single time, not a standing yes — always ask first, never resume
on a prior answer. See memory for the fuller incident.

## 2026-10-11 — Oct10 Booking Done was stale, fixed

Kriti flagged Booking Done looked wrong right after the Oct8-10 refresh
above. She was right: Oct10's Booking Done (row 17) was still showing 5 —
the value pulled yesterday when Oct10 was a partial day. Re-pulled from the
Clinic Dashboard sheet: it had grown to 9 (full day now). **Lesson: Booking
Done isn't an any-time-match metric like Transfer/Connect, but it still
needs a fresh pull whenever a day moves from partial to complete** — reusing
a day's earlier Booking Done value is only safe once that day is fully
closed, not while it's still "today."

Fixed: Sheet row17/18/19 col AS (Oct10) → Booking Done 9, Booking% 7.9%
(was 4.4%), Bookings Needed -2. Dashboard artifact `booking_pct[9]` updated
to 7.9 (if_version 9→10).

## 2026-10-11 — "update all the sheets" (Ticket Categories, Valid Leads Log, Callback Adherence, Prediction Model)

Kriti asked to update all the sheets (Prediction Model, Valid Leads Log,
"and what not"). These 4 tabs (plus Main Dashboard, already current) hadn't
been touched since **2026-10-08** — a 3-day gap, confirmed stale on
inspection (Ticket Categories' own NOTE cell said "day-by-day columns run
Sept 1 - Oct 4", live data actually ran through Oct7; Callback Adherence's
October row showed 373 scheduled, clearly outdated).

**Key recovery**: the 2026-10-08 scratch build scripts (`oct8c_refresh/`)
were still present in this session's scratchpad (hadn't expired), so the
original, battle-tested classify/matching logic could be reused verbatim
instead of reconstructed from scratch. Also recovered the original frozen
source files still sitting in `~/Downloads` from when they were first
pulled: September Nugget (`dauuegbkeinc73durekg.csv`, Sept1-30, verified),
September Ameyo (`CALL_Details_2026-10-01_10_24_49(...).csv`, Sept1-Oct1,
verified), and July+August Nugget/Ameyo (`damfs9ld509s73e7soi0.csv`,
`damg09dd509s73fs4uag.csv`, `CALL_Details_2026-09-18_14_31_48(...).csv`).

**Ticket Categories**: scoped patch, not full rebuild — validated the
classify()/matching logic reproduces the known Oct1-7 TOTAL Count exactly
(589/627/602/594/581/571/557) before writing anything. Added Oct8/9/10 date
columns (615/544/324 TOTAL Count) and recomputed the "October" aggregate
column (was Oct1-7 only = stale, now Oct1-10 = 5604). Left September
aggregate and all Sept1-30/Oct1-7 day columns completely untouched.

**Valid Leads Log**: append-only by design (one row per ticket) — appended
1118 new Oct8-10 rows (389+330+399, matching Main Dashboard's Valid Leads
row digit-for-digit, the documented cross-check) without touching any
existing row. 14842 → 15960 total rows.

**Callback Adherence + Callback Adherence Dump**: full rebuild (these two
tabs are always clear+rewrite, not append/patch) using July+Aug frozen +
recovered Sept + current Oct data (merged/deduped two Oct Nugget files,
preferring the fuller Oct8-10 pull for overlapping ticket IDs; used the
fullest available Oct Ameyo file, Oct1-11). **Validation caught something
real**: raw validation against the known Oct8 July/Aug/Sept numbers
initially "failed" on the Anytime/Transferred columns — investigated rather
than overriding blindly. Two legitimate causes, not bugs: (1) "Anytime"
matching is unbounded-forward, so having Ameyo data through Oct11 now
(vs Oct4 at the last build) surfaces new matches for old scheduled
callbacks — same any-time-drift pattern documented everywhere else in this
project; (2) `doctors_emails.txt` has genuinely changed since Oct8 (diffed
against the old script's frozen inline list: 5 doctors added, 5 removed —
real roster turnover), which is the current correct roster, not a bug to
avoid. Confirmed the two inputs that SHOULD be time-invariant (Scheduled
Callbacks count, and the +/-30min-window counts, both fixed to a historical
moment) matched the known values exactly on all 5 rows before writing.
October row: 373 → 466 scheduled callbacks (now reflects Oct1-10).

**Prediction Model**: full rebuild, `banked_dates` extended from Oct1-7 to
Oct1-10 (Oct10 confirmed complete, Oct11 excluded as still in progress per
the day-rollover rule). Valid Leads/Transfer Total for the banked days
pulled directly from the live Main Dashboard sheet (just-refreshed,
authoritative) rather than re-derived from any CSV snapshot. New forecast:
banked 10 days = 3789 leads / 1037 transfers (27.4%), forecast total Oct =
11746, need 31.3% on remaining 21 days to still hit 30% cumulative.

**Cross-checks after writing**: Valid Leads Log Oct8/9/10 counts
(389/330/399) match Main Dashboard's Valid Leads row exactly, digit for
digit, as required. Ticket Categories TOTAL Count is correctly higher
(615/544/324 — includes Pharmacy True/Bangalore/Source Call tickets that
Valid Lead excludes), not a discrepancy.

**Not done this session**: Vet Follow-up Callback / Dump tabs, and Main
Dashboard rows 20-22 — Kriti said she'd send Sept data for that separately
("sept i will give you afterwards").

Scratch build scripts for this session live in
`<scratchpad>/oct11_refresh/` (build_callback_adherence.py,
build_write_prediction_model.py) plus two one-off scripts used for Ticket
Categories/Valid Leads Log — none committed to the repo (all hardcode
today's specific Downloads filenames, not reusable).

## 2026-10-11 night refresh — Oct8-11 (Oct11 now tracked)

Kriti attached two files: Nugget `db5ssin5e8qs73fh738g.csv` (2882 rows,
Oct8-11, correct 3 channels) and Ameyo `CALL_Details_2026-10-11_23_29_41(...).csv`
(27105 rows, Oct1-11, Oct11 at 2432 — near-complete, end-of-day pull).
Explicit instruction: update dashboard/sheets but skip Vet Repeat %.

Ran `compute_main_dashboard.py` scoped to Oct8-11. Cross-check
`transfer_done + doctor_called == transfer_total` passed all 4 dates.
Booking Done: reused Oct8/9/10 from the Sheet (4/1/9, unchanged), pulled
Oct11 fresh from Clinic Dashboard (1 — likely still settling, worth a
re-check next refresh).

Wrote Main Dashboard by hand again (not the generic write script) to avoid
touching column D — this run only covers 4 of 11 October dates. Oct11 added
as a new column; Oct8/9/10 refreshed in place.

Pushed to the dashboard artifact (if_version 10→11): `dates` extended to
include Oct11, valid_leads/transfer_pct/connect_pct/frt_avg/booking_pct/aht
updated for Oct8-11. **`vet_repeat_pct` explicitly NOT recomputed per
Kriti's instruction** — padded from 10 to 11 entries by carrying forward
the last value (5.2) to keep array lengths in sync with `dates`, per the
standing array-length rule. Still waiting on the September dump for an
actual Vet Follow-up refresh.

Did not touch Ticket Categories / Valid Leads Log / Callback Adherence /
Prediction Model this run — Kriti's instruction was "update the sheets and
dashboard," read as Main Dashboard + artifact (the usual meaning of "the
dashboard"), not the full "all the sheets" scope from yesterday.

## 2026-10-11 night — Ticket Categories, Valid Leads Log, Callback Adherence, Prediction Model (Oct11 + a bug fix)

Kriti confirmed she wanted the other 4 tabs updated too, same scope as the
2026-10-10 "all the sheets" session.

**Bug caught and fixed**: while extending Ticket Categories to Oct11,
validation flagged that the live sheet's Oct10 TOTAL Count (324) didn't
match a fresh recomputation (621). Root cause: the 2026-10-10 Ticket
Categories build used `db509nn5e8qs73ed5et0.csv` for Oct8-10, but that file
had only captured Oct10 as a PARTIAL day (384 raw tickets, pulled before
Oct10 closed) — unlike the Main Dashboard refresh the same day, which had
correctly switched to a fuller same-day file for exactly this reason. The
Ticket Categories script never got that same fix. Confirmed via raw ticket
counts: `db509nn5e8qs73ed5et0.csv` has 384 Oct10 rows, `db5fmlv5e8qs73dfnk8g.csv`
and today's `db5ssin5e8qs73fh738g.csv` both have the true 760. Verified
Oct8/Oct9 were unaffected (identical raw counts, 723/661, across all three
files) before concluding only Oct10 needed correcting. **Lesson for next
time: when a script reads a Nugget export file by filename, sanity-check
that file's per-date row counts for the specific dates being written, not
just trust the filename/date-range label** — a file genuinely covering the
range can still have an incomplete LATEST day inside that range.

Corrected Oct10 (324→621 TOTAL Count) and added Oct11 (624), recomputed the
October aggregate (col C) over the now-correct Oct1-11 data: 6525 (verified
as the exact sum of all 11 day columns). September untouched.

**Valid Leads Log**: Oct8-10 had already used the correct full-day file
(no bug here) — just appended 398 new Oct11 rows, matching Main Dashboard's
Oct11 Valid Leads exactly.

**Callback Adherence + Dump**: full rebuild again, Oct Nugget now merged
from 3 files (base + two overlapping refinements, latest wins) to get
genuine Oct1-11 coverage; Oct Ameyo swapped to today's fullest pull.
Validation (Scheduled Callbacks + /-30min window counts, both
time-invariant) passed exactly on all 5 known July/Aug/Sept rows. October
row: 466 → 475 scheduled callbacks.

**Prediction Model**: `banked_dates` extended to Oct1-11 (Oct11's Ameyo
pull was near-complete, 2432 rows at 23:29, close enough to end-of-day to
bank). New forecast: 11 banked days = 4187 leads / 1167 transfers (27.9%),
forecast total Oct = 11800, need 31.2% on the remaining 20 days to still
hit 30% cumulative.

**Cross-checks after writing**: Valid Leads Log Oct11 (398) matches Main
Dashboard Oct11 Valid Leads exactly. Ticket Categories TOTAL Count
correctly higher than Valid Leads for every one of Oct8-11 (621/624 >
399/398), as expected given its broader category scope.

## 2026-10-12 morning — Oct10-11 refresh (no new date; all sheets)

Kriti attached Nugget `db66dmn5e8qs73c4i040.csv` (1498 rows, Oct10-11 only,
correct 3 channels) and Ameyo `CALL_Details_2026-10-12_10_20_51(...).csv`
(5506 rows, Oct10-12, Oct12 just starting at 428 rows). No Nugget data for
Oct12, so no new date column added this run — scoped to refreshing
Oct10/Oct11 across all tabs.

**Main Dashboard + artifact**: ran scoped to Oct10-11. Cross-check passed
both dates. Oct11 valid_leads drifted 398→388 (10-ticket channel-drift,
within the normal 1-20/refresh range, not alarming). Booking Done for
Oct10/11 reconfirmed unchanged (9, 1) now that both days are fully closed.
Artifact pushed if_version 11→12, only the Oct10/11 array slots touched.

**Ticket Categories**: refreshed Oct10/Oct11 values in place (no new
column) and recomputed the October aggregate — TOTAL Count unchanged
(621/624, as expected since ticket population is now stable for closed
days), minor AHT/Talk-Time drift from continued any-time Ameyo matching.
Validated Oct1-9 still match the live sheet exactly before writing.

**Valid Leads Log**: no changes (append-only by date; no new Oct12 date to
add, and already-appended Oct10/11 rows aren't re-touched by convention).

**Callback Adherence + Dump**: full rebuild. **Caught a real gap before
running**: today's Ameyo file only covers Oct10-12, NOT Oct1-9 — naively
swapping it in as the sole Oct Ameyo source would have silently dropped
Oct1-9's forward call-matching data entirely. Fixed by splitting into two
non-overlapping date ranges: yesterday's fuller file for Oct1-9, today's
fresher pull for Oct10 onward. Validation (Scheduled Callbacks + /-30min
window) passed on all 5 known rows. October row: 475→472 scheduled (small
drop, 3 tickets — plausible from re-pulled/corrected ticket data, same
order of magnitude as routine channel drift elsewhere).

**Prediction Model**: banked_dates unchanged (Oct1-11, still no Oct12
data), refreshed with updated Oct10/11 transfer totals. New forecast: 4177
leads / 1168 transfers (28.0%), forecast total Oct = 11772, need 31.1% on
remaining 20 days.

**Process note for future refreshes**: when swapping in a fresher Ameyo
file for an "any-time" matching rebuild (Callback Adherence, Vet Follow-up,
etc.), always check the file's own date coverage against what's being
replaced — a file can look like "the latest pull" by timestamp while
actually covering a narrower date window than what it's superseding.

## 2026-10-12 — Fixed stale "October Avg" column (Main Dashboard col D)

Kriti asked me to check whether the October average was correct. It
wasn't: column D hadn't been recomputed since before Oct10 was corrected
and before Oct11 was ever tracked — every refresh since the 2026-10-09 10pm
run had explicitly skipped column D because no single run had full Oct1-11
data in hand at once. Confirmed by comparing column D's stale numbers
against a fresh sum of the actual Oct1-11 day columns (e.g. Valid Leads:
col D said 3592, actual sum is 4177).

**Fix**: merged all 4 available Oct Nugget exports (deduped by ticket_id,
latest wins) and the two most recent Oct Ameyo exports (Oct1-9 from the
2026-10-11 pull, Oct10-11 from the 2026-10-12 pull — non-overlapping date
split) into one combined Oct1-11 dataset, ran `compute_main_dashboard.py`
once across the full window to get a properly-weighted `oct_avg` (this
matters for AHT/FRT avg specifically — those are weighted averages, not
a mean of the daily values), and wrote all 16 affected column-D cells:

| Metric | Was | Now |
|---|---|---|
| Valid Leads | 3592 | 4177 |
| Transfer Total | 968 | 1173 |
| Transfer % | 26.9% | 28.1% |
| Connect | 2136 | 2521 |
| Connect % | 59.5% | 60.4% |
| Booking Done | 41 | 46 |
| Booking % | 4.1% | 3.8% |

Also caught and fixed rows 12/15 (Avg Talk Time per Agent / Agents
Available), whose October Avg was even more obviously stale (Agents
Available showed 46, impossible for a 9-person team). Recomputed properly:
all 9 TEAM10 agents were active at some point in Oct1-11, total team talk
time 217:27:05 over the period → Avg Talk Time per Agent (period) =
217:27:05 / 9 = **24:09:41**, Agents Available (period) = **9**.

**Standing lesson, now doubly confirmed**: whenever a refresh is scoped to
only some dates (no full-month data on hand), explicitly skip column D
rather than guess — but don't forget to circle back and recompute it once
full-range data becomes available. It's easy for this column to silently
go stale for days if nobody asks.

Did not touch Ticket Categories' October aggregate (col C) — that one has
been correctly recomputed every refresh this whole time and was already
accurate (6525).
