"""
Computes Main Dashboard day-by-day values (Valid Leads, Transfer%, Connect%,
AHT, FRT, UCJ Bangalore Customer) for a given set of tracked October dates,
from a freshly-pulled Nugget ticket export + Ameyo CALL Details export.

Does NOT compute: Avg Talk Time per Agent / Agents Available (needs the
TEAM10 agent roster, not persisted anywhere yet) or the Vet Follow-up rows
(needs the full Sept1-> history, not just the current month's exports -- see
wiki/vet-followup.md). Booking Done / UCJ Bangalore Customer's conversion %
still needs a separate pull from the Clinic Dashboard sheet (see
wiki/external-sources.md) for Booking Done specifically.

Usage:
    python3 compute_main_dashboard.py <nugget_csv> <ameyo_csv> <date1> [<date2> ...]

Writes computed.json next to this script. See wiki/daily-workflow.md for how
this fits into the full refresh routine, and definitions.md for the exact
metric formulas this implements.

The DOCTORS list is NOT embedded here (it's internal staff email addresses
and this repo is public) -- it's read from a private file kept out of git:
~/Documents/Supertails work/doctors_emails.txt (one email per line).
"""
import csv, re, json, sys, os
from datetime import datetime
from collections import defaultdict

DOCTORS_FILE = os.path.expanduser("~/Documents/Supertails work/doctors_emails.txt")

def load_doctors():
    with open(DOCTORS_FILE) as f:
        doctors = {line.strip().lower() for line in f if line.strip()}
    if len(doctors) != 36:
        print(f"WARNING: expected 36 doctor emails, found {len(doctors)} in {DOCTORS_FILE}", file=sys.stderr)
    return doctors

LANGUAGE_KEYWORDS = {"english", "telugu", "tamil", "kannada", "kanada", "hindi"}
IN_SCOPE_CHANNELS = {"Unified Customer Journey", "UCJ Booking Campaigns"}


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


def sec_to_hms(sec):
    sec = int(round(sec))
    neg = sec < 0
    sec = abs(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return ("-" if neg else "") + f"{h:02d}:{m:02d}:{s:02d}"


def categorize(channel_name, ticket_source, title):
    if channel_name == "UCJ Booking Campaigns":
        return "Bangalore"
    if channel_name != "Unified Customer Journey":
        return None
    if ticket_source == "SOURCE_CALL":
        return "Source Call"
    t = (title or "").lower()
    if "pharmacy" in t:
        m = re.search(r"verification:\s*([^|]*)", t)
        ver = (m.group(1).strip() if m else "")
        return "Pharmacy True" if ver == "true" else "Pharmacy False"
    if "prm call" in t:
        return "Plain/D0"
    return "Other"


def is_valid_lead(channel_name, ticket_source, title):
    if channel_name != "Unified Customer Journey":
        return False
    if ticket_source != "SOURCE_CHAT":
        return False
    t = (title or "").lower()
    if "call back requested" in t:
        return False
    m = re.search(r"verification:\s*([^|]*)", t)
    ver = (m.group(1).strip() if m else "")
    if ver == "true":
        return False
    return categorize(channel_name, ticket_source, title) in ("Plain/D0", "Pharmacy False")


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    nugget_file, ameyo_file = sys.argv[1], sys.argv[2]
    dates = sys.argv[3:]

    doctors = load_doctors()
    transfer_targets = doctors | LANGUAGE_KEYWORDS

    tickets = []
    with open(nugget_file, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ch = row.get("channel_name", "")
            if ch not in IN_SCOPE_CHANNELS:
                continue
            created_raw = row.get("created_at", "")
            if not created_raw:
                continue
            try:
                created_at = datetime.strptime(created_raw, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            phone = norm_phone(row.get("user_phone", "")) or norm_phone(row.get("cf_phone", ""))
            tickets.append({"created_at": created_at, "title": row.get("title", ""),
                             "channel_name": ch, "ticket_source": row.get("ticket_source", ""), "phone": phone})

    calls_by_phone = defaultdict(list)
    with open(ameyo_file, encoding="utf-8-sig") as f:
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

    valid_leads_by_date = defaultdict(list)
    bangalore_by_date = defaultdict(int)
    for t in tickets:
        d = t["created_at"].strftime("%Y-%m-%d")
        if d not in dates:
            continue
        if categorize(t["channel_name"], t["ticket_source"], t["title"]) == "Bangalore":
            bangalore_by_date[d] += 1
        if is_valid_lead(t["channel_name"], t["ticket_source"], t["title"]):
            valid_leads_by_date[d].append(t)

    day = {}
    agg_aht_sec_total = agg_aht_count = 0
    agg_frt_sec_total = agg_frt_count = 0
    agg_vl = agg_transfer_total = agg_connect = 0

    for d in dates:
        leads = valid_leads_by_date[d]
        vl = len(leads)
        connect = transfer_done = doctor_called = transfer_total = 0
        aht_calls = []
        frt_gaps = []

        for t in leads:
            calls = calls_by_phone.get(t["phone"], [])
            if any(c["user_talk"] >= 30 for c in calls):
                connect += 1
            is_td = any(c["transfer_to"] in transfer_targets and (c["customer_talk"] - c["user_talk"]) >= 30 for c in calls)
            is_dc = any(c["user_id"] in doctors and c["user_talk"] >= 30 and c["call_time"] >= t["created_at"] for c in calls)
            if is_td:
                transfer_done += 1
            if is_dc and not is_td:
                doctor_called += 1
            if is_td or is_dc:
                transfer_total += 1
            for c in calls:
                if c["user_talk"] >= 60:
                    aht_calls.append(c["user_talk"])
            hm = t["created_at"].hour * 60 + t["created_at"].minute
            if 9 * 60 <= hm <= 20 * 60 + 45 and calls:
                gap = (calls[0]["call_time"] - t["created_at"]).total_seconds()
                if gap >= -10000:
                    frt_gaps.append(gap)

        aht_avg = sum(aht_calls) / len(aht_calls) if aht_calls else 0
        frt_avg = sum(frt_gaps) / len(frt_gaps) if frt_gaps else 0

        day[d] = {
            "valid_leads": vl, "transfer_total": transfer_total,
            "transfer_pct": round(100 * transfer_total / vl, 1) if vl else 0,
            "transfer_done": transfer_done, "doctor_called": doctor_called,
            "abs_transfer_to_do": round(vl * 0.30) - transfer_total,
            "connect": connect, "connect_pct": round(100 * connect / vl, 1) if vl else 0,
            "connect_needed": round(vl * 0.60) - connect,
            "aht_hms": sec_to_hms(aht_avg),
            "frt_valid_leads": len(frt_gaps), "frt_avg_hms": sec_to_hms(frt_avg),
            "ucj_bangalore_customer": bangalore_by_date[d],
        }
        agg_aht_sec_total += sum(aht_calls); agg_aht_count += len(aht_calls)
        agg_frt_sec_total += sum(frt_gaps); agg_frt_count += len(frt_gaps)
        agg_vl += vl; agg_transfer_total += transfer_total; agg_connect += connect

    oct_avg = {
        "valid_leads": agg_vl, "transfer_total": agg_transfer_total,
        "transfer_pct": round(100 * agg_transfer_total / agg_vl, 1) if agg_vl else 0,
        "transfer_done": sum(day[d]["transfer_done"] for d in dates),
        "doctor_called": sum(day[d]["doctor_called"] for d in dates),
        "abs_transfer_to_do": round(agg_vl * 0.30) - agg_transfer_total,
        "connect": agg_connect,
        "connect_pct": round(100 * agg_connect / agg_vl, 1) if agg_vl else 0,
        "connect_needed": round(agg_vl * 0.60) - agg_connect,
        "aht_hms": sec_to_hms(agg_aht_sec_total / agg_aht_count) if agg_aht_count else "",
        "frt_valid_leads": agg_frt_count,
        "frt_avg_hms": sec_to_hms(agg_frt_sec_total / agg_frt_count) if agg_frt_count else "",
        "ucj_bangalore_customer": sum(day[d]["ucj_bangalore_customer"] for d in dates),
    }

    out = {"day": day, "oct_avg": oct_avg}
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "computed.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path}")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
