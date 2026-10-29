"""
Builds month-to-date inputs from the rolling daily exports in ~/Downloads:
  oct_nugget.csv  -- every Nugget export, created_at >= MONTH_START, newest file (mtime) wins per ticket_id
  oct_ameyo.csv   -- every Ameyo CALL_Details export, Call Time >= MONTH_START, de-duped on Call ID
Writes both into the CURRENT directory (run it from a scratch dir -- never commit the CSVs) and prints
per-day counts so a missing day is obvious before anything is computed.
Usage: python3 merge_month_exports.py
"""
import csv, glob, os, sys
from datetime import datetime
from collections import Counter
csv.field_size_limit(10**9)
files = sorted(glob.glob(os.path.expanduser("~/Downloads/*.csv")), key=os.path.getmtime)
NCOLS = ["ticket_id","created_at","title","channel_name","ticket_source","user_phone","cf_phone","agent_name","agent_assigned_at","agent_frt_response_at"]
ACOLS = ["Call ID","Call Time","Phone","User ID","User Name","Transfer To Agent/Phone","Customer Talk Time","User Talk Time"]
tick, calls = {}, {}
nsrc = Counter(); asrc = Counter()
for f in files:
    with open(f, encoding="utf-8-sig") as fh:
        r = csv.DictReader(fh); h = r.fieldnames or []
        if "ticket_id" in h and "channel_name" in h:
            for row in r:
                if row.get("created_at","") >= "2026-10-01":
                    tick[row["ticket_id"]] = {c: row.get(c,"") for c in NCOLS}; nsrc[os.path.basename(f)] += 1
        elif "Call Time" in h and "Call ID" in h:
            for row in r:
                try: t = datetime.strptime(row["Call Time"], "%d/%m/%Y %I:%M:%S %p")
                except: continue
                if t >= datetime(2026,10,1):
                    calls[row["Call ID"]] = {c: row.get(c,"") for c in ACOLS}; asrc[os.path.basename(f)] += 1
for name, d, cols in [("oct_nugget.csv", tick, NCOLS), ("oct_ameyo.csv", calls, ACOLS)]:
    with open(name, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(d.values())
print("nugget files used", len(nsrc), "tickets", len(tick)); print("ameyo files used", len(asrc), "calls", len(calls))
nd = Counter((v["created_at"][:10], v["channel_name"]) for v in tick.values())
ad = Counter(datetime.strptime(v["Call Time"], "%d/%m/%Y %I:%M:%S %p").strftime("%Y-%m-%d") for v in calls.values())
for i in range(1, 32):
    d = f"2026-10-{i:02d}"
    print(d, "UCJ", nd[(d,"Unified Customer Journey")], "Blr", nd[(d,"UCJ Booking Campaigns")], "Chat", nd[(d,"UCJ SC Chat Assistance")], "| ameyo", ad[d])
