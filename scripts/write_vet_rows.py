"""
Writes Main Dashboard rows 20-22 (Vet Follow-up Transferred / 15-Day Repeat / Repeat %) for the
given months' day columns <= last_date and their Avg columns, from computed_vet.json.
Pass a closed month too while its 15-day windows are still open (e.g. Oct until Nov 15).
Use this instead of write_vet_followup.py, which also rewrites Sept columns.
Usage: python3 write_vet_rows.py <last_date> [YYYY-MM ...]
"""
import sys, os, json, gspread
from datetime import datetime

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"


def main():
    last = sys.argv[1]
    c = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "computed_vet.json")))
    sh = gspread.service_account(filename=KEY).open_by_key(SHEET_ID); ws = sh.worksheet("Main Dashboard")
    H = ws.row_values(1); A = ws.col_values(1)
    r = next(i for i, x in enumerate(A, 1) if x.startswith("Vet Follow-up Transferred"))
    assert A[r].startswith("Vet Follow-up 15") and A[r + 1].startswith("Vet Follow-up Repeat %")
    col = lambda i: gspread.utils.rowcol_to_a1(1, i + 1)[:-1]
    pct = lambda a, b: round(a / b, 3) if b else 0
    data = []
    for month in sys.argv[2:] or [last[:7]]:
        day = {d: x for d, x in c["day"].items() if d[:7] == month and d <= last and d in H}
        T = sum(x["transferred"] for x in day.values()); R = sum(x["repeat"] for x in day.values())
        mc = col(H.index(datetime.strptime(month, "%Y-%m").strftime("%B Avg")))
        data.append({"range": f"Main Dashboard!{mc}{r}:{mc}{r + 2}", "values": [[T], [R], [pct(R, T)]]})
        for d, x in day.items():
            c0 = col(H.index(d))
            data.append({"range": f"Main Dashboard!{c0}{r}:{c0}{r + 2}", "values": [[x["transferred"]], [x["repeat"]], [pct(x["repeat"], x["transferred"])]]})
        print(f"vet rows {month}: {T} transferred / {R} repeat ({pct(R, T):.1%})")
    sh.values_batch_update({"valueInputOption": "RAW", "data": data})
    i = H.index(last)
    sh.batch_update({"requests": [{"repeatCell": {"range": {"sheetId": ws.id, "startRowIndex": r + 1, "endRowIndex": r + 2,
                     "startColumnIndex": i, "endColumnIndex": i + 1}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}},
                     "fields": "userEnteredFormat.numberFormat"}}]})


if __name__ == "__main__":
    main()
