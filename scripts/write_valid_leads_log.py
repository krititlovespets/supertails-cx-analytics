"""
Rebuilds the block of <last_date>'s month in the "Valid Leads Log" tab (one row per Valid Lead).
Earlier months' blocks are frozen and never touched. Every row of the month is re-checked on every run
(transfer/connect flags only ever flip No->Yes as more Ameyo data lands), so
last_checked = today for all of them.

Usage: python3 write_valid_leads_log.py <merged_nugget_csv> <merged_ameyo_csv> <last_date YYYY-MM-DD> [--dry-run]
"""
import sys, os, datetime, gspread
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = os.path.expanduser("~/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json")

def main():
    nug, ame, last = sys.argv[1:4]; dry = "--dry-run" in sys.argv
    MONTH = last[:7]
    T, C, D, TG = oc.load(nug, ame)
    yn = lambda b: "Yes" if b else "No"
    today = datetime.date.today().isoformat()
    rows = []
    for t in T:
        d = t["created_at"][:10]
        if not (t["_valid"] and d.startswith(MONTH) and d <= last):
            continue
        f = oc.flags(t, C, D, TG)
        title = t.get("title", "")
        rows.append([t["ticket_id"], t["created_at"], d, t.get("agent_name", ""),
                     ("'" + title) if title[:1] in "=+-@" else title,
                     oc.verification(title), t["_phone"], yn(f["found"]), yn(f["transfer_done"]),
                     yn(f["doctor_called"]), yn(f["connected"]), today])
    rows.sort(key=lambda r: r[1], reverse=True)
    ws = gspread.service_account(filename=KEY).open_by_key(SHEET_ID).worksheet("Valid Leads Log")
    dates = ws.col_values(3)
    first_oct = next((i for i, x in enumerate(dates, 1) if x.startswith(MONTH)), len(dates) + 1)
    assert all(x[:7] < MONTH for x in dates[1:first_oct - 1]), "unexpected rows above this month's block"
    old_end = max(len(dates), first_oct - 1)
    new_end = first_oct + len(rows) - 1
    print(f"{MONTH} block: rows {first_oct}..{new_end} ({len(rows)} leads, was {max(old_end - first_oct + 1, 0)}); "
          f"transferred={sum(r[8]=='Yes' or r[9]=='Yes' for r in rows)} connected={sum(r[10]=='Yes' for r in rows)}")
    if dry:
        print("dry run - nothing written"); return
    if ws.row_count < new_end:
        ws.resize(rows=new_end + 100)
    ws.update(range_name=f"A{first_oct}:L{new_end}", values=rows, value_input_option="USER_ENTERED")
    if old_end > new_end:
        ws.batch_clear([f"A{new_end + 1}:L{old_end}"])
    print("written")

if __name__ == "__main__":
    main()
