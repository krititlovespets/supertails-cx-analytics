"""
Shared per-ticket core for the secondary tabs (Valid Leads Log, Ticket Categories,
Agent Productivity Table 6, Booking Analysis, ...). Reuses the exact rules in
compute_main_dashboard.py (see wiki/definitions.md) so every tab ties out to
Main Dashboard.

load(nugget_csv, ameyo_csv) -> (tickets, calls_by_phone, doctors, transfer_targets)
flags(ticket, calls, doctors, targets) -> dict of per-ticket booleans

Inputs are the merged month-to-date CSVs described in wiki/daily-workflow.md
("Building the Oct-to-date inputs from rolling exports").
"""
import csv, os, sys
from datetime import datetime
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute_main_dashboard import (load_doctors, LANGUAGE_KEYWORDS, IN_SCOPE_CHANNELS,
                                    norm_phone, hms_to_sec, sec_to_hms, categorize, is_valid_lead)

csv.field_size_limit(10**9)


def verification(title):
    import re
    m = re.search(r"verification:\s*([^|]*)", (title or "").lower())
    return m.group(1).strip() if m else ""


def load(nugget_file, ameyo_file):
    doctors = load_doctors()
    targets = doctors | LANGUAGE_KEYWORDS
    tickets = []
    with open(nugget_file, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get("channel_name", "") not in IN_SCOPE_CHANNELS:
                continue
            try:
                created = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
            except (KeyError, ValueError):
                continue
            row["_created"] = created
            row["_phone"] = norm_phone(row.get("user_phone", "")) or norm_phone(row.get("cf_phone", ""))
            row["_cat"] = categorize(row["channel_name"], row.get("ticket_source", ""), row.get("title", ""))
            row["_valid"] = is_valid_lead(row["channel_name"], row.get("ticket_source", ""), row.get("title", ""))
            tickets.append(row)
    calls = defaultdict(list)
    with open(ameyo_file, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                t = datetime.strptime(row["Call Time"], "%d/%m/%Y %I:%M:%S %p")
            except (KeyError, ValueError):
                continue
            p = norm_phone(row.get("Phone", ""))
            if not p:
                continue
            calls[p].append({"call_time": t,
                             "user_id": (row.get("User ID", "") or "").strip().lower(),
                             "user_name": (row.get("User Name", "") or "").strip(),
                             "transfer_to": (row.get("Transfer To Agent/Phone", "") or "").strip().lower(),
                             "customer_talk": hms_to_sec(row.get("Customer Talk Time", "")),
                             "user_talk": hms_to_sec(row.get("User Talk Time", ""))})
    for p in calls:
        calls[p].sort(key=lambda c: c["call_time"])
    return tickets, calls, doctors, targets


def flags(t, calls_by_phone, doctors, targets):
    calls = calls_by_phone.get(t["_phone"], [])
    td = any(c["transfer_to"] in targets and (c["customer_talk"] - c["user_talk"]) >= 30 for c in calls)
    dc = any(c["user_id"] in doctors and c["user_talk"] >= 30 and c["call_time"] >= t["_created"] for c in calls)
    return {"calls": calls, "found": bool(calls), "transfer_done": td,
            "doctor_called": dc and not td, "transferred": td or dc,
            "connected": any(c["user_talk"] >= 30 for c in calls)}
