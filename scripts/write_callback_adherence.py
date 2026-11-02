"""
Callback Adherence + Callback Adherence Dump.

July-October rows are FROZEN (closed months) and kept exactly as they are. Rows scheduled from
November onward are rebuilt every run:
  population = in-scope tickets that EVER carried a cf_callback_ucj value in any export
  in ~/Downloads (latest non-empty value wins). Nugget CLEARS cf_callback_ucj once the
  callback is handled, so "newest row only" silently drops completed callbacks (found
  2026-10-27).
  attempted = any call to the phone within +/-30 min of the scheduled time
  connected = a call in that window with User Talk Time >= 30s
  transferred = a call in that window that is a Transfer Done (target + cust-user >= 30s)
  attempted_after = any call at/after the scheduled time (unbounded)
  done_within_30min_after = a call in [scheduled, scheduled + 30 min]
Usage: python3 write_callback_adherence.py <merged_nugget_csv> <merged_ameyo_csv> [--dry-run]
"""
import sys, os, csv, glob, gspread
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = os.path.expanduser("~/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json")
FROZEN = {"July", "August", "September", "October"}
REBUILD_FROM = datetime(2026, 11, 1)
BASE = datetime(1899, 12, 30); W = timedelta(minutes=30)
serial = lambda dt: round((dt - BASE).total_seconds() / 86400, 10)
MONTHS = {11: "November", 12: "December"}


def callback_tickets():
    tick = {}
    for f in sorted(glob.glob(os.path.expanduser("~/Downloads/*.csv")), key=os.path.getmtime):
        with open(f, encoding="utf-8-sig") as fh:
            r = csv.DictReader(fh)
            if "cf_callback_ucj" not in (r.fieldnames or []):
                continue
            for row in r:
                if row.get("cf_callback_ucj") and row.get("channel_name") in oc.IN_SCOPE_CHANNELS:
                    tick[row["ticket_id"]] = row
    return tick


def main():
    nug, ame = sys.argv[1:3]; dry = "--dry-run" in sys.argv
    _, C, D, TG = oc.load(nug, ame)
    sh = gspread.service_account(filename=KEY).open_by_key(SHEET_ID)
    dws = sh.worksheet("Callback Adherence Dump")
    old = dws.get_all_values(value_render_option="UNFORMATTED_VALUE")
    hdr, frozen = old[0], [r for r in old[1:] if r and r[5] in FROZEN]
    yn = lambda b: "Yes" if b else "No"
    new = []
    for k, t in callback_tickets().items():
        try:
            s = datetime.strptime(t["cf_callback_ucj"].strip()[:16], "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if s < REBUILD_FROM:
            continue
        ph = oc.norm_phone(t.get("user_phone", "")) or oc.norm_phone(t.get("cf_phone", ""))
        calls = C.get(ph, [])
        win = [c for c in calls if abs(c["call_time"] - s) <= W]
        closest = min(win, key=lambda c: abs(c["call_time"] - s))["call_time"] if win else None
        new.append([int(k) if k.isdigit() else k, t.get("agent_name", ""), int(ph) if ph.isdigit() else ph, serial(s),
                    serial(closest) if closest else "", MONTHS.get(s.month, s.strftime("%B")),
                    yn(win), yn(any(c["user_talk"] >= 30 for c in win)),
                    yn(any(c["transfer_to"] in TG and c["customer_talk"] - c["user_talk"] >= 30 for c in win)),
                    yn(any(c["call_time"] >= s for c in calls)), yn(any(s <= c["call_time"] <= s + W for c in calls))])
    new.sort(key=lambda r: r[3])
    rows = frozen + new
    def summ(sel):
        n = len(sel); a = sum(r[9] == "Yes" for r in sel); w = sum(r[6] == "Yes" for r in sel); tr = sum(r[8] == "Yes" for r in sel)
        f = lambda x: round(x / n, 3) if n else 0
        return [n, a, f(a), w, f(w), tr, f(tr)]
    by = lambda m: [r for r in rows if r[5] == m]
    gaps = [(r[4] - r[3]) * 86400 for r in rows if r[4] != ""]
    out = {"November": summ(by("November")),
           "December (future-scheduled)": summ(by("December")), "TOTAL": summ(rows)}
    print(f"frozen Jul-Oct rows {len(frozen)}; rebuilt Nov+ rows {len(new)}; " +
          "; ".join(f"{k}: {v[0]} sched, anytime {v[2]:.1%}, +/-30 {v[4]:.1%}, transferred {v[5]}" for k, v in out.items()) +
          f"; avg gap {sum(gaps) / len(gaps):.1f}s")
    if dry:
        print("dry run - nothing written"); return
    end = len(rows) + 1
    if dws.row_count < end:
        dws.resize(rows=end + 100)
    dws.update(range_name=f"A2:K{end}", values=rows, value_input_option="RAW")
    if len(old) > end:
        dws.batch_clear([f"A{end + 1}:K{len(old)}"])
    sid = dws.id
    sh.batch_update({"requests": [
        {"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 1, "endRowIndex": end, "startColumnIndex": 3, "endColumnIndex": 4},
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE_TIME", "pattern": "yyyy-mm-dd hh:mm"}}},
                        "fields": "userEnteredFormat.numberFormat"}},
        {"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 1, "endRowIndex": end, "startColumnIndex": 4, "endColumnIndex": 5},
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE_TIME", "pattern": "yyyy-mm-dd hh:mm:ss"}}},
                        "fields": "userEnteredFormat.numberFormat"}}]})
    ws = sh.worksheet("Callback Adherence"); col = ws.col_values(1)
    if "November" not in col:   # first November run: November is a live month now, and goes above December
        a, b = col.index("December (future-scheduled)") + 1, col.index("November (future-scheduled)") + 1
        ws.batch_update([{"range": f"A{a}", "values": [["November"]]}, {"range": f"A{b}", "values": [["December (future-scheduled)"]]}], value_input_option="RAW")
        col = ws.col_values(1)
    data = []
    for label, vals in out.items():
        r = next((i for i, x in enumerate(col, 1) if x == label), None)
        if r is None:
            continue  # month row not present (e.g. no future-scheduled callbacks) -- leave layout alone
        data.append({"range": f"'Callback Adherence'!B{r}:H{r}", "values": [vals]})
    g = next(i for i, x in enumerate(col, 1) if x.startswith("Avg gap"))
    avg = sum(gaps) / len(gaps)
    data.append({"range": f"'Callback Adherence'!B{g}", "values": [[f"{avg:.1f} seconds (landed slightly {'EARLY' if avg < 0 else 'LATE'} on average, within the window)"]]})
    sh.values_batch_update({"valueInputOption": "RAW", "data": data})
    print(f"written: dump {len(rows)} rows; summary rows {list(out)}")


if __name__ == "__main__":
    main()
