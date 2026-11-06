"""
Builds month-to-date inputs from the rolling daily exports in ~/Downloads:
  nugget.csv  -- every Nugget export, created_at >= MONTH start, newest file (mtime) wins per ticket_id
  ameyo.csv   -- every Ameyo CALL_Details export, Call Time >= MONTH start, de-duped on Call ID
Writes both into the CURRENT directory (run it from a scratch dir -- never commit the CSVs) and prints
per-day counts so a missing day is obvious before anything is computed.
Usage: python3 merge_month_exports.py 2026-11
"""
import csv, glob, os, sys
from datetime import datetime
from collections import Counter
csv.field_size_limit(10**9)
MONTH = sys.argv[1]; START = MONTH + "-01"; START_DT = datetime.strptime(START, "%Y-%m-%d")
files = sorted(glob.glob(os.path.expanduser("~/Downloads/*.csv")), key=os.path.getmtime)
NCOLS = ["ticket_id","created_at","title","channel_name","ticket_source","user_phone","cf_phone","agent_name","agent_assigned_at","agent_frt_response_at"]
ACOLS = ["Call ID","Call Time","Phone","User ID","User Name","Transfer To Agent/Phone","Customer Talk Time","User Talk Time"]
tick, calls, closer = {}, {}, {}
# Bulk closes kept out of every count (Kriti, 2026-11-06): any ticket with Primary Disposition = Bulk, and
# Nov 5 and Nov 6 tickets closed by akshaya.r (bulk closes). akshaya.r closes of other days' tickets stay in.
EXCLUDED_CLOSERS = {"bulk", ("akshaya.rlovespets@supertails.com", "2026-11-05"), ("akshaya.rlovespets@supertails.com", "2026-11-06")}
nsrc = Counter(); asrc = Counter()
for f in files:
    with open(f, encoding="utf-8-sig") as fh:
        r = csv.DictReader(fh); h = r.fieldnames or []
        if "ticket_id" in h and "channel_name" in h:
            for row in r:
                if row.get("created_at","") >= START:
                    tick[row["ticket_id"]] = {c: row.get(c,"") for c in NCOLS}; nsrc[os.path.basename(f)] += 1
                    # newest file wins: (closed by, created on), or "bulk" for UCJ IB_OB Primary Disposition = Bulk
                    closer[row["ticket_id"]] = ("bulk" if (row.get("cf_primary_disposition") or "").strip().lower() == "bulk"
                                                else ((row.get("resolved_by") or "").strip().lower(), row["created_at"][:10]))
        elif "Call Time" in h and "Call ID" in h:
            for row in r:
                try: t = datetime.strptime(row["Call Time"], "%d/%m/%Y %I:%M:%S %p")
                except: continue
                if t >= START_DT:
                    calls[row["Call ID"]] = {c: row.get(c,"") for c in ACOLS}; asrc[os.path.basename(f)] += 1
# Tickets Kriti asked to keep out of every denominator: one file per date of ticket IDs (whitespace-separated)
# in ~/Documents/Supertails work/exclusions/. Dropped here so every call-side tab leaves them out the same way.
excl = set()
for f in glob.glob(os.path.expanduser("~/Documents/Supertails work/exclusions/*.txt")):
    excl |= set(open(f).read().split())
dropped = Counter(tick.pop(i)["created_at"][:10] for i in list(tick) if i in excl)
print("excluded tickets", dict(sorted(dropped.items())) or "none")
dropped = Counter(tick.pop(i)["created_at"][:10] for i in list(tick) if closer.get(i) in EXCLUDED_CLOSERS)
print("excluded bulk (Primary Disposition Bulk, or Nov 5/6 ticket closed by akshaya.r)", dict(sorted(dropped.items())) or "none")
for name, d, cols in [("nugget.csv", tick, NCOLS), ("ameyo.csv", calls, ACOLS)]:
    with open(name, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(d.values())
print("nugget files used", len(nsrc), "tickets", len(tick)); print("ameyo files used", len(asrc), "calls", len(calls))
nd = Counter((v["created_at"][:10], v["channel_name"]) for v in tick.values())
ad = Counter(datetime.strptime(v["Call Time"], "%d/%m/%Y %I:%M:%S %p").strftime("%Y-%m-%d") for v in calls.values())
for i in range(1, 32):
    d = f"{MONTH}-{i:02d}"
    print(d, "UCJ", nd[(d,"Unified Customer Journey")], "Blr", nd[(d,"UCJ Booking Campaigns")], "Chat", nd[(d,"UCJ SC Chat Assistance")], "| ameyo", ad[d])
