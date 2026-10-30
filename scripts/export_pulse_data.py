"""
Exports the numbers the two claude.ai dashboard pages show (Supertails CX Pulse, October UCJ
Tracker) straight from the LIVE sheet, so the pages can never disagree with it:
  daily.csv  -- one row per tracked day (Sept + Oct) from Main Dashboard
  months.csv -- Sept / Oct period columns from Main Dashboard
  chat.csv   -- Day-shift chat volume + FRTs per day from "Chat - Daily Summary"
Durations are seconds; percentages are fractions (0-1).
Usage: python3 export_pulse_data.py <out_dir>
"""
import sys, os, csv, gspread

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"
ROWS = [("Valid Leads", "valid_leads", "n"), ("Transfer Total", "transfers", "n"), ("Transfer %", "transfer_pct", "p"),
        ("Transfer Done", "transfer_done", "n"), ("Doctor Called", "doctor_called", "n"), ("Connect (Numerator)", "connects", "n"),
        ("Connect %", "connect_pct", "p"), ("AHT", "aht_sec", "t"), ("Avg Talk Time per Agent", "talk_per_agent_sec", "t"),
        ("FRT Avg", "frt_sec", "t"), ("Agents Available", "agents", "f"), ("UCJ Bangalore Customer", "bangalore", "n"),
        ("Booking Done", "bookings", "n"), ("% Booking Done", "booking_pct", "p"), ("Vet Follow-up Transferred", "vet_transferred", "n"),
        ("Vet Follow-up 15-Day Repeat", "vet_repeat", "n"), ("Vet Follow-up Repeat %", "vet_repeat_pct", "p")]


def conv(x, kind):
    x = (x or "").strip()
    if not x:
        return ""
    if kind == "p":
        return round(float(x.rstrip("%")) / 100, 4)
    if kind == "t":
        h, m, s = map(int, x.split(":")); return h * 3600 + m * 60 + s
    if kind == "f":
        return float(x)
    return int(float(x))


def chat_sec(x):
    x = (x or "").strip(); tot = 0
    for part in x.split():
        n, u = int(part[:-1]), part[-1]
        tot += n * {"h": 3600, "m": 60, "s": 1}[u]
    return tot if x else ""


def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    sh = gspread.service_account(filename=KEY).open_by_key(SHEET_ID)
    v = sh.worksheet("Main Dashboard").get_all_values(); H = v[0]
    rows = {key: next(r for r in v if r[0].startswith(lab)) for lab, key, _ in ROWS}
    dates = [h for h in H if h[:4] == "2026"]
    with open(os.path.join(out, "daily.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "month"] + [k for _, k, _ in ROWS])
        for d in dates:
            i = H.index(d)
            w.writerow([d, d[:7]] + [conv(rows[k][i] if i < len(rows[k]) else "", kind) for _, k, kind in ROWS])
    with open(os.path.join(out, "months.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["period", "label"] + [k for _, k, _ in ROWS])
        last = dates[-1]
        for i, (p, lab) in enumerate([("2026-09", "September"), ("2026-09-16..30", "Sep 16-30"), ("2026-10", f"October (to {last[5:]})")], start=1):
            w.writerow([p, lab] + [conv(rows[k][i], kind) for _, k, kind in ROWS])
    c = sh.worksheet("Chat - Daily Summary").get_all_values()
    hdr = c[1]; lab = lambda s: next(r for r in c[2:12] if r[0].startswith(s))
    t, a, d = lab("Tickets (n)"), lab("Avg Actual FRT"), lab("Avg Day Starting FRT")
    ma, md = lab("Median Actual FRT"), lab("Median Day Starting FRT")
    with open(os.path.join(out, "chat.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "month", "chats", "avg_actual_frt_sec", "median_actual_frt_sec", "avg_start_frt_sec", "median_start_frt_sec"])
        for i, h in enumerate(hdr):
            if h[:4] == "2026" and i < len(t) and t[i]:
                w.writerow([h, h[:7], int(t[i]), chat_sec(a[i]), chat_sec(ma[i]), chat_sec(d[i]), chat_sec(md[i])])
    print("exported", len(dates), "days to", out)


if __name__ == "__main__":
    main()
