"""
Rewrites the OCTOBER section of "Booking Analysis" (everything above the September
NOTE). New days are added by INSERTING a row before the daily TOTAL row, so the
September section and the frozen Leadership snapshot below move down with their
formatting (no clear()/rewrite of the tail -- see bug-patterns.md #2).
Per-agent Booked = sum of the agent's daily "Appts created" (Clinic Dashboard,
Agent_Perf_V2) for Oct 1..last; TEAM TOTAL Booked = TOTAL (UCJ only) row.
Usage: python3 write_booking_analysis.py <merged_nugget_csv> <merged_ameyo_csv> <last_date> [--dry-run]
"""
import sys, os, gspread
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc, booking_analysis as ba

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
CLINIC_ID = "1EyTmbBSkZMvL5JolKuo8xxOkguYGUKpTJTzlN68n5hM"
KEY = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"
TAB = "Booking Analysis"
ORDER = ["Dhanush S", "Alan Joel", "Abdul Rahman", "Mohammed Roohulla"]
pct = lambda a, b: f"{100 * a / b:.1f}%" if b else "0.0%"


def clinic_booked(gc, last):
    v = gc.open_by_key(CLINIC_ID).worksheet("Agent_Perf_V2").get_all_values()
    h = v[3]; day = int(last[-2:])
    cols = [i for i, x in enumerate(h) if x.endswith("/10/2026") and int(x[:2]) <= day]
    s = lambda r: sum(int(r[i] or 0) for i in cols)
    per = {ba.AGENTS[r[0]]: s(r) for r in v if r[0] in ba.AGENTS and r[2] == "Appts created"}
    team = s(next(r for r in v if r[:3] == ["TOTAL (UCJ only)", "UCJ", "Appts created"]))
    return per, team


def main():
    nug, ame, last = sys.argv[1:4]; dry = "--dry-run" in sys.argv
    gc = gspread.service_account(filename=KEY)
    T, C, D, TG = oc.load(nug, ame)
    per, daily = ba.build(T, C, last)
    booked, team_booked = clinic_booked(gc, last)
    assert set(booked) == set(ORDER), f"Clinic Dashboard per-agent rows missing: {set(ORDER) - set(booked)}"
    L = f"Oct 1-{int(last[-2:])}"
    dates = sorted(daily)
    top = [
        [f"NOTE: Booking team analysis, {L} (full day). \"Called\" = Bangalore (UCJ Booking Campaigns) tickets the agent dialled any time; "
         "\"Connected\" = that agent's OWN call >=30s (per-agent funnel, from the Nugget+Ameyo exports). \"Booked\" per agent = that agent's "
         "Appts created in the Clinic Dashboard (Agent_Perf_V2), summed over the same days -- live again from 2026-10-27 (the per-agent rows "
         "were missing Oct25-26, when this column was frozen at Oct24 values). TEAM TOTAL Booked comes from the Clinic Dashboard's "
         "TOTAL (UCJ only) Appts Created row, so it can exceed the 4-agent sum. The daily Bangalore Connect% table uses the TEAM-WIDE "
         "definition (any caller, >=30s), same as Main Dashboard; recent days keep rising on future refreshes (any-time phone matching)."],
        [""],
        [f"=== PER-AGENT FUNNEL ({L}) ==="],
        ["Agent", "Called", "Connected (own call)", "Connect %", "Booked", "Booking % (Booked/Called)", "Booked/Connected %"]]
    for n in ORDER:
        a = per[n]; b = booked[n]
        top.append([n, str(a["called"]), str(a["conn"]), pct(a["conn"], a["called"]), str(b), pct(b, a["called"]), pct(b, a["conn"])])
    tc = sum(per[n]["called"] for n in ORDER); tn = sum(per[n]["conn"] for n in ORDER)
    top.append(["TEAM TOTAL (Called/Connected live; Booked = live Clinic Dashboard total, not agent sum)",
                str(tc), str(tn), pct(tn, tc), str(team_booked), pct(team_booked, tc), pct(team_booked, tn)])
    top += [[""], ["=== BANGALORE CONNECT % BY DATE (team-wide, any caller) ==="], ["Date", "Bangalore Tickets", "Connected", "Connect %"]]
    for d in dates:
        x = daily[d]; top.append([d, str(x["n"]), str(x["conn"]), pct(x["conn"], x["n"])])
    N = sum(x["n"] for x in daily.values()); CN = sum(x["conn"] for x in daily.values())
    top += [[f"TOTAL ({L})", str(N), str(CN), pct(CN, N)], [""], [f"=== OVERALL FUNNEL SUMMARY ({L}) ==="],
            ["Bangalore Tickets", "Connected", "Connect %", "Booked (team, live)", "Booked % of Connected", "Booked % of Total"],
            [str(N), str(CN), pct(CN, N), str(team_booked), pct(team_booked, CN), pct(team_booked, N)]]
    top = [r + [""] * (7 - len(r)) for r in top]
    print(f"{L}: agents " + ", ".join(f"{n} {per[n]['called']}/{per[n]['conn']}/{booked[n]}" for n in ORDER)
          + f"; Bangalore {N} tickets, {CN} connected ({pct(CN, N)}), booked {team_booked}; {len(dates)} daily rows")
    if dry:
        print("dry run - nothing written"); return
    sh = gc.open_by_key(SHEET_ID); ws = sh.worksheet(TAB)
    col = ws.col_values(1)
    sept = next(i for i, x in enumerate(col, 1) if x.startswith("NOTE: Same definitions as the October section"))
    tot_row = next(i for i, x in enumerate(col, 1) if x.startswith("TOTAL (Oct"))
    old_days = tot_row - (next(i for i, x in enumerate(col, 1) if x == "Date") + 1)
    add = len(dates) - old_days
    if add > 0:
        sh.batch_update({"requests": [{"insertDimension": {"range": {"sheetId": ws.id, "dimension": "ROWS",
                         "startIndex": tot_row - 1, "endIndex": tot_row - 1 + add}, "inheritFromBefore": True}}]})
    assert add >= 0, "fewer days than before -- not handled"
    gap = (sept + add) - len(top) - 1  # blank rows kept between October section and the September NOTE
    assert gap >= 1, gap
    ws.update(range_name=f"A1:G{len(top)}", values=top, value_input_option="RAW")
    print(f"written: October section rows 1-{len(top)} ({add} row(s) inserted); September NOTE now at row {sept + add}")


if __name__ == "__main__":
    main()
