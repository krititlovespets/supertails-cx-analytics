# Vet Follow-up Callback (15-Day Repeat)

New tab, added 2026-10-05. Tracks whether a customer who got transferred to a
vet/doctor gets ANOTHER qualifying transfer within 15 days of their ticket's
own creation date.

## Current definition (as of 2026-10-05, stable since)

- **Population**: tickets in `{Unified Customer Journey, UCJ Booking Campaigns}`
  only (the raw export's 3rd channel, `UCJ SC Chat Assistance`, is excluded —
  see `definitions.md`). ALL tickets, not just the narrow "Valid Lead" subset
  (Kriti's explicit choice — vet transfers span Pharmacy True, Bangalore, etc.,
  which Valid Lead excludes).
- **Window**: `[created_at, created_at + 15 days]` per ticket.
- **"Transferred"**: phone has >=1 qualifying touch (Transfer Done OR Doctor
  Called rule, same as everywhere else) inside that window.
- **"15-Day Repeat"**: a touch lands **more than 15 minutes after the FIRST
  touch** in the window (`(touch.dt - touches[0].dt).total_seconds() > 900`).
  **This is the final, correct rule — do not revert to either earlier version:**
  - v1 (wrong): `touch_count >= 2` anywhere in the window → gave a wildly
    inflated 59.3% repeat rate. 93% of those "repeats" were same-session
    multi-row artifacts (the agent's Transfer-To-Agent handoff call immediately
    followed by the doctor's own outbound call back to the customer, logged as
    2-3 separate Ameyo rows within minutes).
  - v2 (also wrong, briefly): required the second touch on a LATER CALENDAR
    DAY than the first. Better than v1 but too coarse — missed a genuine
    same-day-but-hours-later repeat, and Kriti's own correction was more
    precise: a 15-MINUTE threshold, not a calendar-day one.

## Scope caveat (always re-state when sharing these numbers)

Every window needs 15 full days of forward Ameyo data to fully resolve. Any
ticket created within 15 days of the latest tracked date has an "Open" window —
its repeat count is a lower bound that can only go UP on future refreshes, never
down. As of 2026-10-07's data: tickets created on/before **2026-09-22** have
fully "Closed" windows; everything after is provisional. The headline "closed
window" rate (the only trustworthy point-in-time figure) was **10.3-10.5%**
across the last several refreshes — much more stable than the blended
all-windows figure (~9.0%, drags down by provisional recent data).

## Where it feeds

- **Vet Followup Callback** tab: rolling-last-15-days date-by-date view + a
  BY CATEGORY block — both scoped to the rolling window, not full history.
- **Vet Followup Callback Dump**: full Sept1→latest history, one row per
  transferred ticket, for drill-down.
- **Main Dashboard rows 20-22**: Sept/Sept16-30/Oct aggregate totals, built
  from the FULL history (not the rolling-15-day subset) via `sept_agg`/
  `sept1630_agg`/`oct_agg` in the build script's summary JSON.

## By-category pattern (fairly stable across refreshes)

Source Call customers repeat far more than other categories (~15%) — makes
sense, they're already phone-originated repeat callers by nature. Plain/D0
lowest (~1.5-2%). Bangalore/Pharmacy True/False cluster in the 3-5% range.
