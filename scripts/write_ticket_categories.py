"""
Recomputes the current month of "Ticket Categories": its period column (found by header,
e.g. "November") and every day column of that month (adding new ones at the right, formats
copied from the previous column). Earlier months' columns are frozen and never touched.

Every column of the month is recomputed from the current merged exports on every
run -- connect/transfer are any-time phone matches, so older days keep rising
(found 2026-10-27: until then each day column had been frozen at the value it
had on the day it was first added).

Rules (match row 1's NOTE and wiki/definitions.md): 6 categories = {PRM D0,
Pharmacy False, Pharmacy True} by title x {Unified Journey, UCJ Booking} by
channel, all ticket sources; per ticket, not de-duped by phone. TOTAL = all 6.
Talk Time = total User Talk Time of the 10-agent team on calls phone-matched to
the bucket's tickets / number of those agents with >=1 such call.

Usage: python3 write_ticket_categories.py <merged_nugget_csv> <merged_ameyo_csv> <last_date> [--dry-run]
"""
import sys, os, re, gspread
from datetime import datetime
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"
TAB = "Ticket Categories"
TEAM = {"mohammed.rolovespets@supertails.in", "nikhil.singhlovespets@supertails.com", "abdul.rahmanlovespets@supertails.in",
        "arjun.llovespets@supertails.in", "shazali.snlovespets@supertails.in", "riddi.plovespets@supertails.in",
        "dhanush.slovespets@supertails.com", "hammad.shaikhlovespets@supertails.in", "alan.jlovespets@supertails.in",
        "raisa.qlovespets@supertails.in"}
CH = {"Unified Customer Journey": "Unified Journey", "UCJ Booking Campaigns": "UCJ Booking"}
CATS = [f"{s} ({c})" for c in ("Unified Journey", "UCJ Booking") for s in ("PRM D0", "Pharmacy False", "Pharmacy True")]


def sub(t):
    tl = (t.get("title") or "").lower()
    if "pharmacy" in tl:
        return "Pharmacy True" if oc.verification(tl) == "true" else "Pharmacy False"
    if "prm call" in tl:
        return "PRM D0"


def agg(fl):
    n = len(fl); con = sum(f["connected"] for f in fl); tr = sum(f["transferred"] for f in fl)
    aht = [c["user_talk"] for f in fl for c in f["calls"] if c["user_talk"] >= 60]
    tt = 0; ag = set()
    for f in fl:
        for c in f["calls"]:
            if c["user_id"] in TEAM:
                tt += c["user_talk"]; ag.add(c["user_id"])
    return {"Count": n, "Connect (abs)": con, "Connect %": round(con / n, 3) if n else 0,
            "Transfer (abs)": tr, "Transfer %": round(tr / n, 3) if n else 0,
            "Transfer Done": sum(f["transfer_done"] for f in fl), "Doctor Called": sum(f["doctor_called"] for f in fl),
            "AHT": oc.sec_to_hms(sum(aht) / len(aht)) if aht else "00:00:00",
            "Talk Time": oc.sec_to_hms(tt / len(ag)) if ag else "00:00:00"}


def col_letter(i1):
    s = ""
    while i1:
        i1, r = divmod(i1 - 1, 26); s = chr(65 + r) + s
    return s


def main():
    nug, ame, last = sys.argv[1:4]; dry = "--dry-run" in sys.argv
    T, C, D, TG = oc.load(nug, ame)
    B = defaultdict(list)
    for t in T:
        s = sub(t); d = t["created_at"][:10]
        if s and d.startswith(last[:7]) and d <= last:
            B[(f"{s} ({CH[t['channel_name']]})", d)].append(oc.flags(t, C, D, TG))
    dates = sorted({d for _, d in B})
    sh = gspread.service_account(filename=KEY).open_by_key(SHEET_ID); ws = sh.worksheet(TAB)
    v = ws.get_all_values(); hdr = v[1]
    month_name = datetime.strptime(last, "%Y-%m-%d").strftime("%B")
    assert month_name in hdr, hdr[:5]
    col0 = {h: i for i, h in enumerate(hdr)}
    nxt = len(hdr); new = []
    for d in dates:
        if d not in col0:
            col0[d] = nxt; nxt += 1; new.append(d)
    cols = [(month_name, dates)] + [(d, [d]) for d in dates]
    data = []
    for r_i, row in enumerate(v[2:], start=3):
        lab = row[0]
        if " -- " not in lab:
            continue
        cat, metric = lab.split(" -- ", 1)
        cat = "TOTAL" if cat.startswith("TOTAL") else cat
        key = next(k for k in ("Count", "Connect (abs)", "Connect %", "Transfer (abs)", "Transfer %", "Transfer Done",
                               "Doctor Called", "AHT", "Talk Time") if metric.startswith(k))
        for name, ds in cols:
            fl = [f for d in ds for c in (CATS if cat == "TOTAL" else [cat]) for f in B[(c, d)]]
            data.append({"range": f"'{TAB}'!{col_letter(col0[name] + 1)}{r_i}", "values": [[agg(fl)[key]]]})
    tot = agg([f for k, fl in B.items() for f in fl])
    print(f"{month_name}: {tot['Count']} tickets, connect {tot['Connect %']:.1%}, transfer {tot['Transfer (abs)']} "
          f"({tot['Transfer %']:.1%}); {len(dates)} day columns, new: {new or 'none'}; {len(data)} cells")
    if dry:
        print("dry run - nothing written"); return
    if ws.col_count < nxt:
        ws.resize(cols=nxt)
    for d in new:
        data.append({"range": f"'{TAB}'!{col_letter(col0[d] + 1)}2", "values": [[d]]})
    note = re.sub(r"day-by-day columns run Sept 1 - [A-Za-z]+ \d+", f"day-by-day columns run Sept 1 - {month_name[:3]} {int(last[-2:])}", v[0][0])
    note = note.replace("Rebuilt from scratch 2026-10-02.", "Rebuilt from scratch 2026-10-02; current-month columns fully recomputed every refresh (any-time matching, older days keep rising).")
    data.append({"range": f"'{TAB}'!A1", "values": [[note]]})
    sh.values_batch_update({"valueInputOption": "RAW", "data": data})
    reqs = [{"copyPaste": {"source": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": len(v),
                                      "startColumnIndex": col0[d] - 1, "endColumnIndex": col0[d]},
                           "destination": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": len(v),
                                           "startColumnIndex": col0[d], "endColumnIndex": col0[d] + 1},
                           "pasteType": "PASTE_FORMAT"}} for d in new]
    if reqs:
        sh.batch_update({"requests": reqs})
    print("written")


if __name__ == "__main__":
    main()
