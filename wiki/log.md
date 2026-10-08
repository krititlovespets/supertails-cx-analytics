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
