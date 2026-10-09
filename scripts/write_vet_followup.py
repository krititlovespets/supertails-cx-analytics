"""
Writes computed_vet.json (from compute_vet_followup.py) into Main
Dashboard rows 20-22 (Vet Follow-up Transferred / 15-Day Repeat / Repeat %):
October Avg column + Sept Avg / Sept16-30 Avg columns + one column per
tracked date (Sept1 through the latest tracked October day).

Adds new October date columns if they don't exist yet (matching
write_main_dashboard.py's behavior), but does NOT add new September date
columns -- September is frozen/already fully populated from past refreshes.

This is the heavier of the two Main Dashboard scripts (needs the full
Sept1-> history pull) -- per Kriti's instruction 2026-10-08 (moved from the
5pm slot to 8am on 2026-10-09), only run this one as part of the 8am
scheduled refresh, not all 4. The other 3 runs (12pm/5pm/10pm) should only
call compute_main_dashboard.py / write_main_dashboard.py.

Usage:
    python3 write_vet_followup.py
"""
import json, os
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
SERVICE_ACCOUNT_FILE = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

WHITE = {"red": 1, "green": 1, "blue": 1}

# sheet row (1-indexed) -> (computed_vet.json metric key, kind)
ROWS = [
    (20, "transferred", "count"),
    (21, "repeat", "count"),
    (22, "pct", "pct"),
]


def col_letter(idx1):
    s = ""
    while idx1 > 0:
        idx1, rem = divmod(idx1 - 1, 26)
        s = chr(65 + rem) + s
    return s


def main():
    with open(os.path.join(SCRIPT_DIR, "computed_vet.json")) as f:
        data = json.load(f)
    day, sept_agg, sept1630_agg, oct_agg = data["day"], data["sept_agg"], data["sept1630_agg"], data["oct_agg"]

    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet("Main Dashboard")
    sheet_id = ws.id

    header = ws.row_values(1)
    date_col0 = {d: i for i, d in enumerate(header)}  # 0-indexed

    oct_dates = sorted(d for d in day if d >= "2026-10-01")
    new_dates = [d for d in oct_dates if d not in date_col0]
    next_col0 = len(header)
    for d in sorted(new_dates):
        date_col0[d] = next_col0
        next_col0 += 1
    if ws.col_count < next_col0:
        ws.resize(cols=next_col0)

    value_ranges = []
    for sheet_row, key, kind in ROWS:
        def v(agg):
            val = agg[key]
            return val / 100.0 if kind == "pct" else val

        value_ranges.append({"range": f"Main Dashboard!B{sheet_row}", "values": [[v(sept_agg)]]})
        value_ranges.append({"range": f"Main Dashboard!C{sheet_row}", "values": [[v(sept1630_agg)]]})
        value_ranges.append({"range": f"Main Dashboard!D{sheet_row}", "values": [[v(oct_agg)]]})

        for d, col0 in date_col0.items():
            if d not in day:
                continue
            col1 = col0 + 1
            value_ranges.append({"range": f"Main Dashboard!{col_letter(col1)}{sheet_row}",
                                  "values": [[v(day[d])]]})

    sh.values_batch_update({"valueInputOption": "RAW", "data": value_ranges})

    for d in new_dates:
        ws.update_acell(f"{col_letter(date_col0[d] + 1)}1", d)

    format_requests = []
    for d in new_dates:
        col0 = date_col0[d]
        for sheet_row, key, kind in ROWS:
            row0 = sheet_row - 1
            cell_format = {"backgroundColor": WHITE}
            fields = "userEnteredFormat.backgroundColor"
            if kind == "pct":
                cell_format["numberFormat"] = {"type": "PERCENT", "pattern": "0.0%"}
                fields = "userEnteredFormat(backgroundColor,numberFormat)"
            format_requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet_id, "startRowIndex": row0, "endRowIndex": row0 + 1,
                              "startColumnIndex": col0, "endColumnIndex": col0 + 1},
                    "cell": {"userEnteredFormat": cell_format},
                    "fields": fields,
                }
            })
    if format_requests:
        sh.batch_update({"requests": format_requests})

    print(f"Wrote Vet Follow-up rows 20-22: {len(day)} date columns + Sept/Sept16-30/Oct Avg "
          f"({len(new_dates)} new date columns: {', '.join(new_dates) or 'none'}).")


if __name__ == "__main__":
    main()
