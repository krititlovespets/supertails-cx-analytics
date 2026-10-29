"""
Vet Followup Callback (summary) + Vet Followup Callback Dump. Rule: wiki/vet-followup.md.

Dump = one row per TRANSFERRED ticket, Sept 1 -> last date.
  - Every ticket present in the nugget CSV is fully recomputed (pass a Sept+Oct merged
    nugget and a Sept->now Ameyo file to rebuild the whole history). Old dump rows for
    September tickets NOT in the CSV are kept, with their October touches recomputed.
  - October tickets: fully recomputed from the merged October exports.
Summary = the last 15 created dates up to <last_date> (rolling) + TOTAL + BY CATEGORY.
Usage: python3 write_vet_tabs.py <merged_nugget_csv> <merged_ameyo_csv> <last_date> [--dry-run]
"""
import sys, os, gspread
from datetime import datetime, timedelta
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"
BASE = datetime(1899, 12, 30)
ser = lambda dt: round((dt - BASE).total_seconds() / 86400, 10)
unser = lambda x: BASE + timedelta(days=float(x))
CATORDER = ["Plain/D0", "Pharmacy False", "Pharmacy True", "Bangalore", "Source Call", "Other"]


def touches(calls, created, doctors, targets):
    out = []
    end = created + timedelta(days=15)
    for c in calls:
        if not (created <= c["call_time"] <= end):
            continue
        if c["transfer_to"] in targets and c["customer_talk"] - c["user_talk"] >= 30:
            out.append((c["call_time"], "Transfer Done"))
        elif c["user_id"] in doctors and c["user_talk"] >= 30:
            out.append((c["call_time"], "Doctor Called"))
    return out


def row_for(tid, created, agent, ch, cat, phone, tl, now_cutoff):
    tl = sorted(set(tl))
    end = created + timedelta(days=15)
    rep = len(tl) >= 2 and (tl[-1][0] - tl[0][0]).total_seconds() > 900
    return [int(tid) if str(tid).isdigit() else tid, ser(created), ser(datetime(created.year, created.month, created.day)), agent, ch, cat,
            int(phone) if str(phone).isdigit() else phone, "Yes", ser(end), "Open" if end > now_cutoff else "Closed", len(tl),
            "; ".join(f"{t:%Y-%m-%d %H:%M} ({k})" for t, k in tl), "Yes" if rep else "No"]


def main():
    nug, ame, last = sys.argv[1:4]; dry = "--dry-run" in sys.argv
    now_cutoff = datetime.strptime(last, "%Y-%m-%d") + timedelta(days=1)
    T, C, D, TG = oc.load(nug, ame)
    sh = gspread.service_account(filename=KEY).open_by_key(SHEET_ID)
    dws = sh.worksheet("Vet Followup Callback Dump")
    old = dws.get_all_values(value_render_option="UNFORMATTED_VALUE")
    have = {t["ticket_id"] for t in T}
    rows = []
    for r in old[1:]:
        created = unser(r[1])
        if created >= datetime(2026, 10, 1) or str(r[0]) in have:
            continue  # recomputed below from the exports
        prev = []
        for part in str(r[11]).split("; "):
            if part:
                ts, kind = part.split(" (", 1)
                t = datetime.strptime(ts, "%Y-%m-%d %H:%M")
                if t < datetime(2026, 10, 1):
                    prev.append((t, kind.rstrip(")")))
        new = [(t, k) for t, k in touches(C.get(oc.norm_phone(str(r[6])), []), created, D, TG)]
        rows.append(row_for(r[0], created, r[3], r[4], r[5], r[6], prev + new, now_cutoff))
    per = defaultdict(list)  # date -> (category, transferred, repeat)
    for t in T:
        d = t["created_at"][:10]
        if not ("2026-09-01" <= d <= last):
            continue
        tl = [(x, k) for x, k in touches(C.get(t["_phone"], []), t["_created"], D, TG)]
        cat = oc.categorize(t["channel_name"], t.get("ticket_source", ""), t.get("title", ""))
        if tl:
            r = row_for(t["ticket_id"], t["_created"], t.get("agent_name", ""), t["channel_name"], cat, t["_phone"], tl, now_cutoff)
            rows.append(r); per[d].append((cat, True, r[12] == "Yes"))
        else:
            per[d].append((cat, False, False))
    rows.sort(key=lambda r: r[1], reverse=True)
    dates = sorted(per)[-15:]
    f = lambda a, b: round(a / b, 3) if b else 0
    summ = []
    for d in dates:
        x = per[d]; n = len(x); tr = sum(1 for _, a, _ in x if a); rp = sum(1 for _, _, b in x if b)
        summ.append([ser(datetime.strptime(d, "%Y-%m-%d")), n, tr, f(tr, n), rp, f(rp, tr)])
    allx = [y for d in dates for y in per[d]]
    N = len(allx); TR = sum(1 for _, a, _ in allx if a); RP = sum(1 for _, _, b in allx if b)
    total = ["TOTAL", N, TR, f(TR, N), RP, f(RP, TR)]
    cats = []
    for c in CATORDER:
        x = [y for y in allx if y[0] == c]; n = len(x); tr = sum(1 for _, a, _ in x if a); rp = sum(1 for _, _, b in x if b)
        cats.append([c, n, tr, f(tr, n), rp, f(rp, tr)])
    resolved = (datetime.strptime(last, "%Y-%m-%d") - timedelta(days=15)).strftime("%Y-%m-%d")
    print(f"dump {len(rows)} rows (Sept {sum(1 for r in rows if unser(r[1]) < datetime(2026,10,1))}); rolling {dates[0]}..{dates[-1]}: "
          f"{N} candidates, {TR} transferred ({f(TR, N):.1%}), {RP} repeat ({f(RP, TR):.1%})")
    if dry:
        print("dry run - nothing written"); return
    end = len(rows) + 1
    if dws.row_count < end:
        dws.resize(rows=end + 100)
    dws.update(range_name=f"A2:M{end}", values=rows, value_input_option="RAW")
    if len(old) > end:
        dws.batch_clear([f"A{end + 1}:M{len(old)}"])
    fmt = lambda c, p: {"repeatCell": {"range": {"sheetId": dws.id, "startRowIndex": 1, "endRowIndex": end, "startColumnIndex": c, "endColumnIndex": c + 1},
                                       "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE_TIME", "pattern": p}}}, "fields": "userEnteredFormat.numberFormat"}}
    sh.batch_update({"requests": [fmt(1, "yyyy-mm-dd hh:mm:ss"), fmt(2, "yyyy-mm-dd"), fmt(8, "yyyy-mm-dd hh:mm:ss")]})
    ws = sh.worksheet("Vet Followup Callback"); v = ws.get_all_values()
    A = [r[0] for r in v]
    note = v[0][0]
    import re
    note = re.sub(r"rolling last-15-days view \([\d-]+ to [\d-]+, since the latest tracked (?:Ameyo )?date is [\d-]+\)",
                  f"rolling last-15-days view ({dates[0]} to {dates[-1]}, since the latest tracked date is {last})", note)
    note = re.sub(r"Tickets created on/before [\d-]+ are fully resolved; everything from [\d-]+ onward \(all 15 dates in the table below\)",
                  f"Tickets created on/before {resolved} are fully resolved; everything from "
                  f"{(datetime.strptime(resolved, '%Y-%m-%d') + timedelta(days=1)):%Y-%m-%d} onward (all 15 dates in the table below)", note)
    note = re.sub(r"the full Sept1-Oct\d+ history", f"the full Sept1-Oct{int(last[-2:])} history", note)
    t0 = A.index("TOTAL"); first = t0 - 15; assert A[first - 1] == "Created Date"
    c0 = A.index("=== BY CATEGORY ===")
    data = [{"range": "'Vet Followup Callback'!A1", "values": [[note]]},
            {"range": f"'Vet Followup Callback'!A{first + 1}:F{t0 + 1}", "values": summ + [total]},
            {"range": f"'Vet Followup Callback'!A{c0 + 2}:F{c0 + 1 + len(cats)}", "values": cats}]
    sh.values_batch_update({"valueInputOption": "RAW", "data": data})
    print("written")


if __name__ == "__main__":
    main()
