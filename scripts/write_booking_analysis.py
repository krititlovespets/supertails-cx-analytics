"""
Rewrites the current month's section at the top of "Booking Analysis" (newest month first; everything
above the previous month's NOTE). On a month's first run the section is INSERTED at the top. New days
are added by inserting a row before the daily TOTAL row, so older sections below move down with their
formatting (no clear()/rewrite of the tail -- see bug-patterns.md #2).
Per-agent Booked = sum of the agent's daily "Appts created" (Clinic Dashboard,
Agent_Perf_V2) for Oct 1..last; TEAM TOTAL Booked = TOTAL (UCJ only) row.
Usage: python3 write_booking_analysis.py <merged_nugget_csv> <merged_ameyo_csv> <last_date> [--dry-run]
"""
import sys, os, gspread
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc, booking_analysis as ba

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
CLINIC_ID = "1EyTmbBSkZMvL5JolKuo8xxOkguYGUKpTJTzlN68n5hM"
KEY = os.path.expanduser("~/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json")
TAB = "Booking Analysis"
ORDER = ["Dhanush S", "Alan Joel", "Abdul Rahman", "Mohammed Roohulla"]
pct = lambda a, b: f"{100 * a / b:.1f}%" if b else "0.0%"


def clinic_booked(gc, last):
    import clinic  # handles the day/month-swapped date headers (2026-10-30)
    v = clinic.open_sheet(gc); month = last[:7]
    s = lambda rows: sum(n for d, n in rows.items() if d.startswith(month) and d <= last)
    per = {ba.AGENTS[r[0]]: s(clinic.daily(v, lambda x, e=r[0]: x[0] == e and x[2] == "Appts created"))
           for r in v if r[0] in ba.AGENTS and r[2] == "Appts created"}
    team = s(clinic.daily(v, lambda x: x[:3] == ["TOTAL (UCJ only)", "UCJ", "Appts created"]))
    return per, team


def previous_booked(gc, last):
    """Booked column (E) of this month's section as last written, keyed by agent; team from the TEAM TOTAL row."""
    Mon = datetime.strptime(last, "%Y-%m-%d").strftime("%b")
    v = gc.open_by_key(SHEET_ID).worksheet(TAB).get_values("A1:E60")
    start = next(i for i, r in enumerate(v) if r and r[0].startswith(f"NOTE: Booking team analysis, {Mon} "))
    end = next(i for i in range(start, len(v)) if v[i] and v[i][0].startswith("TEAM TOTAL"))   # older months sit below
    rows = {r[0]: int(r[4]) for r in v[start:end] if len(r) > 4 and r[4].isdigit()}
    team = int(v[end][4])
    return {n: rows[n] for n in ORDER if n in rows}, team


def main():
    nug, ame, last = sys.argv[1:4]; dry = "--dry-run" in sys.argv
    gc = gspread.service_account(filename=KEY)
    T, C, D, TG = oc.load(nug, ame)
    per, daily = ba.build(T, C, last)
    stale = bool(os.environ.get("BOOKING_JSON"))   # refresh_all.sh run with Clinic Dashboard skipped
    booked, team_booked = previous_booked(gc, last) if stale else clinic_booked(gc, last)
    assert set(booked) == set(ORDER), f"Clinic Dashboard per-agent rows missing: {set(ORDER) - set(booked)}"
    Mon = datetime.strptime(last, "%Y-%m-%d").strftime("%b")
    L = f"{Mon} 1-{int(last[-2:])}"
    dates = sorted(daily)
    top = [
        [f"NOTE: Booking team analysis, {L} (full day). Every Bangalore (UCJ Booking Campaigns) ticket has ONE owner, so the agent rows add up exactly "
         "to the team total: the last of the 4 agents with their own call >=30s; if none connected, the last of the 4 who called; if none of the 4 called, "
         "the 'Not called by these 4' row (no call yet, or called only by others). Connected = any caller >=30s (same as Main Dashboard), credited to the owner. "
         "Booked per agent = that agent's Appts created in the Clinic Dashboard (Agent_Perf_V2), which is not tied to a ticket, so Booking % per agent is an approximation; "
         "the 'Not called' row's Booked is UCJ bookings by anyone outside the 4. The daily table uses the same team-wide Connect basis; recent days keep rising on "
         "future refreshes (any-time phone matching)."
         + (" Booked NOT refreshed this run (Clinic Dashboard was empty): Booked figures are from the previous run." if stale else "")],
        [""],
        [f"=== PER-AGENT FUNNEL ({L}) ==="],
        ["Agent", "Tickets Owned", "Connected", "Connect %", "Booked", "Booking % (Booked/Tickets)", "Booked/Connected %"]]
    for n in ORDER:
        a = per[n]; b = booked[n]
        top.append([n, str(a["called"]), str(a["conn"]), pct(a["conn"], a["called"]), str(b), pct(b, a["called"]), pct(b, a["conn"])])
    x = per[ba.NONE]; ob = team_booked - sum(booked[n] for n in ORDER)
    top.append([ba.NONE, str(x["called"]), str(x["conn"]), pct(x["conn"], x["called"]), str(ob), pct(ob, x["called"]), pct(ob, x["conn"])])
    tc = sum(a["called"] for a in per.values()); tn = sum(a["conn"] for a in per.values())
    top.append(["TEAM TOTAL (matches the Bangalore total below)", str(tc), str(tn), pct(tn, tc), str(team_booked), pct(team_booked, tc), pct(team_booked, tn)])
    top += [[""], ["=== BANGALORE CONNECT % BY DATE (team-wide, any caller) ==="], ["Date", "Bangalore Tickets", "Connected", "Connect %"]]
    for d in dates:
        x = daily[d]; top.append([d, str(x["n"]), str(x["conn"]), pct(x["conn"], x["n"])])
    N = sum(x["n"] for x in daily.values()); CN = sum(x["conn"] for x in daily.values())
    top += [[f"TOTAL ({L})", str(N), str(CN), pct(CN, N)], [""], [f"=== OVERALL FUNNEL SUMMARY ({L}) ==="],
            ["Bangalore Tickets", "Connected", "Connect %", "Booked (team, live)", "Booked % of Connected", "Booked % of Total"],
            [str(N), str(CN), pct(CN, N), str(team_booked), pct(team_booked, CN), pct(team_booked, N)]]
    top = [r + [""] * (7 - len(r)) for r in top]
    assert tc == sum(x["n"] for x in daily.values()) and tn == sum(x["conn"] for x in daily.values()), "agents do not add up to the team"
    print(f"{L}: agents " + ", ".join(f"{n} {per[n]['called']}/{per[n]['conn']}/{booked[n]}" for n in ORDER)
          + f"; not called {per[ba.NONE]['called']}/{per[ba.NONE]['conn']}/{team_booked - sum(booked.values())}; Bangalore {N} tickets, {CN} connected ({pct(CN, N)}), booked {team_booked}; {len(dates)} daily rows")
    if dry:
        print("dry run - nothing written"); return
    sh = gc.open_by_key(SHEET_ID); ws = sh.worksheet(TAB)
    col = ws.col_values(1)
    this_note = next((i for i, x in enumerate(col, 1) if x.startswith(f"NOTE: Booking team analysis, {Mon} ")), None)
    if this_note is None:   # first run of the month: open space at the very top
        sh.batch_update({"requests": [{"insertDimension": {"range": {"sheetId": ws.id, "dimension": "ROWS",
                         "startIndex": 0, "endIndex": len(top) + 3}, "inheritFromBefore": False}}]})
        start = 1; add = 0
    else:
        start = this_note
        insert = lambda at, n: sh.batch_update({"requests": [{"insertDimension": {"range": {"sheetId": ws.id, "dimension": "ROWS",
                                                "startIndex": at - 1, "endIndex": at - 1 + n}, "inheritFromBefore": True}}]})
        find = lambda pred: next(i for i, x in enumerate(col, 1) if i >= start and pred(x))
        tot_row = find(lambda x: x.startswith(f"TOTAL ({Mon}"))
        old_days = tot_row - (find(lambda x: x == "Date") + 1)
        add = len(dates) - old_days
        assert add >= 0, "fewer days than before -- not handled"
        if add > 0:
            insert(tot_row, add)
        team_row = find(lambda x: x.startswith("TEAM TOTAL"))
        if col[team_row - 2] != ba.NONE:   # sections written before the single-owner change lack this row
            insert(team_row, 1); add += 1
    ws.update(range_name=f"A{start}:G{start + len(top) - 1}", values=top, value_input_option="RAW")
    sh.batch_update({"requests": [{"repeatCell": {"range": {"sheetId": ws.id, "startRowIndex": start - 1, "endRowIndex": start, "startColumnIndex": 0, "endColumnIndex": 1},
                     "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP"}}, "fields": "userEnteredFormat.wrapStrategy"}}]})
    print(f"written: {Mon} section rows {start}-{start + len(top) - 1} ({add} row(s) inserted)")


if __name__ == "__main__":
    main()
