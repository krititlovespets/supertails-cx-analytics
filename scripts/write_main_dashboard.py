"""
Writes computed.json (from compute_main_dashboard.py) into the "Main
Dashboard" tab of the live sheet: October Avg column + one column per
tracked October date. Adds a new date column if it doesn't exist yet.

Does NOT touch: Avg Talk Time per Agent / Agents Available (skipped --
no persisted agent roster) or the Vet Follow-up rows (skipped -- needs
full Sept1-> history). See compute_main_dashboard.py's docstring and
wiki/daily-workflow.md.

Usage:
    python3 write_main_dashboard.py <booking_done_json>
    # booking_done_json: {"2026-10-01": 5, "2026-10-02": 5, ...} -- pull
    # these from the Clinic Dashboard sheet per wiki/external-sources.md;
    # Booking Done isn't an "any-time match" metric so already-tracked
    # days' values don't need to be re-pulled, only re-send what you have.
"""
import json, os, sys
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
SERVICE_ACCOUNT_FILE = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PINK = {"red": 0.972549, "green": 0.77254903, "blue": 0.81960785}
RED = {"red": 0.95686275, "green": 0.6, "blue": 0.6}
WHITE = {"red": 1, "green": 1, "blue": 1}

# sheet row (1-indexed, VERIFY against the live sheet if row count ever
# changes -- see wiki/sheet-structure.md's warning about not trusting
# hardcoded row numbers blindly) -> (computed.json field key, kind, color)
ROWS = [
    (2,  "valid_leads",            "count", WHITE),
    (3,  "transfer_total",         "count", WHITE),
    (4,  "transfer_pct",           "pct",   PINK),
    (5,  "transfer_done",          "count", WHITE),
    (6,  "doctor_called",          "count", WHITE),
    (7,  "abs_transfer_to_do",     "count", RED),
    (8,  "connect",                "count", WHITE),
    (9,  "connect_pct",            "pct",   PINK),
    (10, "connect_needed",         "count", WHITE),
    (11, "aht_hms",                "hms",   WHITE),
    (13, "frt_valid_leads",        "count", WHITE),
    (14, "frt_avg_hms",            "hms",   PINK),
    (16, "ucj_bangalore_customer", "count", WHITE),
    (17, "booking_done",           "count", WHITE),
    (18, "booking_pct",            "pct",   PINK),
    (19, "bookings_needed",        "count", WHITE),
]


def col_letter(idx1):
    s = ""
    while idx1 > 0:
        idx1, rem = divmod(idx1 - 1, 26)
        s = chr(65 + rem) + s
    return s


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    booking_done = json.loads(sys.argv[1]) if sys.argv[1].strip().startswith("{") else json.load(open(sys.argv[1]))

    with open(os.path.join(SCRIPT_DIR, "computed.json")) as f:
        data = json.load(f)
    day, oct_avg = data["day"], data["oct_avg"]
    dates = sorted(day.keys())

    for d in dates:
        bd = booking_done[d]
        ucj_b = day[d]["ucj_bangalore_customer"]
        day[d]["booking_done"] = bd
        day[d]["booking_pct"] = round(100 * bd / ucj_b, 1) if ucj_b else 0
        day[d]["bookings_needed"] = round(ucj_b * 0.065) - bd

    agg_booking = sum(booking_done[d] for d in dates)
    agg_ucj_b = oct_avg["ucj_bangalore_customer"]
    oct_avg["booking_done"] = agg_booking
    oct_avg["booking_pct"] = round(100 * agg_booking / agg_ucj_b, 1) if agg_ucj_b else 0
    oct_avg["bookings_needed"] = round(agg_ucj_b * 0.065) - agg_booking

    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet("Main Dashboard")
    sheet_id = ws.id

    header = ws.row_values(1)
    date_col0 = {d: i for i, d in enumerate(header)}  # 0-indexed
    new_dates = [d for d in dates if d not in date_col0]
    next_col0 = len(header)
    for d in sorted(new_dates):
        date_col0[d] = next_col0
        next_col0 += 1
    if ws.col_count < next_col0:
        ws.resize(cols=next_col0)

    value_ranges = []
    for sheet_row, key, kind, _color in ROWS:
        oavg = oct_avg[key]
        value_ranges.append({"range": f"Main Dashboard!D{sheet_row}",
                              "values": [[oavg / 100.0 if kind == "pct" else oavg]]})
        for d in dates:
            v = day[d][key]
            col1 = date_col0[d] + 1
            value_ranges.append({"range": f"Main Dashboard!{col_letter(col1)}{sheet_row}",
                                  "values": [[v / 100.0 if kind == "pct" else v]]})
    sh.values_batch_update({"valueInputOption": "RAW", "data": value_ranges})

    for d in new_dates:
        ws.update_acell(f"{col_letter(date_col0[d] + 1)}1", d)

    format_requests = []
    for d in new_dates:
        col0 = date_col0[d]
        for sheet_row, key, kind, color in ROWS:
            row0 = sheet_row - 1
            cell_format = {"backgroundColor": color}
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

    print(f"Wrote {len(dates)} date columns ({', '.join(new_dates) or 'none new'}) + October Avg.")


if __name__ == "__main__":
    main()
