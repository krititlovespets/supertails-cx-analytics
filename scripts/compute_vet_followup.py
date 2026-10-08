"""
Computes Main Dashboard rows 20-22 (Vet Follow-up Transferred / 15-Day
Repeat / Repeat %) for every tracked date, plus the Sept / Sept16-30 / Oct
summary aggregates. See wiki/vet-followup.md for the exact rule.

Needs FULL history exports (Sept1 -> latest), not just the current month --
a ticket created in September can still "repeat" in October, and its
15-day window needs calls from both files to resolve.

Population is EVERY ticket in {Unified Customer Journey, UCJ Booking
Campaigns} (channel only -- no Valid Lead / ticket_source / title
filtering, unlike other metrics; see vet-followup.md for why).

Usage:
    python3 compute_vet_followup.py <nugget_sept_csv> <nugget_oct_csv> <ameyo_full_csv> <latest_tracked_date YYYY-MM-DD>

Writes computed_vet.json next to this script.
"""
import csv, re, json, sys, os
from datetime import datetime, timedelta
from collections import defaultdict

DOCTORS_FILE = os.path.expanduser("~/Documents/Supertails work/doctors_emails.txt")
LANGUAGE_KEYWORDS = {"english", "telugu", "tamil", "kannada", "kanada", "hindi"}
IN_SCOPE_CHANNELS = {"Unified Customer Journey", "UCJ Booking Campaigns"}
REPEAT_THRESHOLD_SEC = 15 * 60


def load_doctors():
    with open(DOCTORS_FILE) as f:
        doctors = {line.strip().lower() for line in f if line.strip()}
    if len(doctors) != 36:
        print(f"WARNING: expected 36 doctor emails, found {len(doctors)}", file=sys.stderr)
    return doctors


def norm_phone(p):
    if not p:
        return ""
    digits = re.sub(r"\D", "", p)
    return digits[-10:] if len(digits) >= 10 else digits


def hms_to_sec(s):
    if not s:
        return 0
    parts = s.split(":")
    if len(parts) != 3:
        return 0
    try:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except ValueError:
        return 0


def load_tickets(path, channel_set):
    tickets = []
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ch = row.get("channel_name", "")
            if ch not in channel_set:
                continue
            created_raw = row.get("created_at", "")
            if not created_raw:
                continue
            try:
                created_at = datetime.strptime(created_raw, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            phone = norm_phone(row.get("user_phone", "")) or norm_phone(row.get("cf_phone", ""))
            tickets.append({"ticket_id": row.get("ticket_id", ""), "created_at": created_at, "phone": phone})
    return tickets


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)
    nugget_sept, nugget_oct, ameyo_full, latest_tracked_str = sys.argv[1:5]
    latest_tracked = datetime.strptime(latest_tracked_str, "%Y-%m-%d")
    now_cutoff = latest_tracked + timedelta(days=1)  # treat the tracked day as fully elapsed for window-closure purposes

    doctors = load_doctors()
    transfer_targets = doctors | LANGUAGE_KEYWORDS

    tickets = load_tickets(nugget_sept, IN_SCOPE_CHANNELS) + load_tickets(nugget_oct, IN_SCOPE_CHANNELS)
    # de-dupe by ticket_id in case the two pulls overlap on a boundary date
    seen = set()
    deduped = []
    for t in tickets:
        if t["ticket_id"] in seen:
            continue
        seen.add(t["ticket_id"])
        deduped.append(t)
    tickets = deduped
    print(f"Loaded {len(tickets)} in-scope tickets (Sept+Oct, deduped)", file=sys.stderr)

    calls_by_phone = defaultdict(list)
    with open(ameyo_full, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ct_raw = row.get("Call Time", "")
            if not ct_raw:
                continue
            try:
                call_time = datetime.strptime(ct_raw, "%d/%m/%Y %I:%M:%S %p")
            except ValueError:
                continue
            phone = norm_phone(row.get("Phone", ""))
            if not phone:
                continue
            calls_by_phone[phone].append({
                "call_time": call_time,
                "user_id": (row.get("User ID", "") or "").strip().lower(),
                "transfer_to": (row.get("Transfer To Agent/Phone", "") or "").strip().lower(),
                "customer_talk": hms_to_sec(row.get("Customer Talk Time", "")),
                "user_talk": hms_to_sec(row.get("User Talk Time", "")),
            })
    for p in calls_by_phone:
        calls_by_phone[p].sort(key=lambda c: c["call_time"])
    print(f"Loaded Ameyo calls for {len(calls_by_phone)} phones", file=sys.stderr)

    def is_qualifying_touch(c, ticket_created_at):
        if c["transfer_to"] in transfer_targets and (c["customer_talk"] - c["user_talk"]) >= 30:
            return True
        if c["user_id"] in doctors and c["user_talk"] >= 30 and c["call_time"] >= ticket_created_at:
            return True
        return False

    per_ticket = []
    for t in tickets:
        window_start = t["created_at"]
        window_end = t["created_at"] + timedelta(days=15)
        calls = calls_by_phone.get(t["phone"], [])
        touches = sorted(
            c["call_time"] for c in calls
            if window_start <= c["call_time"] <= window_end and is_qualifying_touch(c, t["created_at"])
        )
        transferred = len(touches) >= 1
        repeat = len(touches) >= 2 and (touches[-1] - touches[0]).total_seconds() > REPEAT_THRESHOLD_SEC
        window_open = window_end > now_cutoff
        per_ticket.append({
            "date": t["created_at"].strftime("%Y-%m-%d"),
            "transferred": transferred,
            "repeat": repeat,
            "window_open": window_open,
        })

    def aggregate(rows):
        transferred = sum(1 for r in rows if r["transferred"])
        repeat = sum(1 for r in rows if r["repeat"])
        pct = round(100 * repeat / transferred, 1) if transferred else 0
        return {"transferred": transferred, "repeat": repeat, "pct": pct}

    by_date = defaultdict(list)
    for r in per_ticket:
        by_date[r["date"]].append(r)

    day = {d: aggregate(rows) for d, rows in by_date.items()}

    sept_rows = [r for r in per_ticket if r["date"] >= "2026-09-01" and r["date"] <= "2026-09-30"]
    sept1630_rows = [r for r in per_ticket if "2026-09-16" <= r["date"] <= "2026-09-30"]
    oct_rows = [r for r in per_ticket if r["date"] >= "2026-10-01"]

    out = {
        "day": day,
        "sept_agg": aggregate(sept_rows),
        "sept1630_agg": aggregate(sept1630_rows),
        "oct_agg": aggregate(oct_rows),
    }
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "computed_vet.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path}")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
