"""
Agent Productivity "Table 6" -- single-owner ticket-level model (wiki/definitions.md).
Each October valid lead is credited to ONE roster agent:
  - Transfer Done -> the roster agent on the first qualifying transfer call;
  - Doctor Called -> the last roster agent who called that phone before the first qualifying doctor call;
  - otherwise     -> the last roster agent who called that phone (any time);
  - no roster call at all -> "(no roster agent call)".
Connected = ticket-level (any caller >=30s). AHT = all >=60s calls on the phone, credited to owner.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc

ROSTER = {  # NAME_TO_EMAIL minus Nikhil Singh (0 October activity, removed 2026-10-15)
    "raisa.qlovespets@supertails.in": "Raisa Qureshi", "hammad.shaikhlovespets@supertails.in": "Hammad Vaseem Shaikh",
    "shazali.snlovespets@supertails.in": "Shazali Sanober", "arjun.llovespets@supertails.in": "Arjun L",
    "riddi.plovespets@supertails.in": "Riddi P", "alan.jlovespets@supertails.in": "Alan Joel",
    "dhanush.slovespets@supertails.com": "Dhanush S", "abdul.rahmanlovespets@supertails.in": "Abdul Rahman",
    "mohammed.rolovespets@supertails.in": "Mohammed Roohulla", "ganashree.dlovespets@supertails.in": "Ganashree D",
    "daksha.klovespets@supertails.in": "Daksha K"}
NONE = "(no roster agent call)"
label = lambda e: f"{ROSTER[e]} ({e})"


def owner(t, f, doctors, targets):
    calls = f["calls"]; roster_calls = [c for c in calls if c["user_id"] in ROSTER]
    if f["transfer_done"]:
        q = [c for c in calls if c["transfer_to"] in targets and (c["customer_talk"] - c["user_talk"]) >= 30]
        if q[0]["user_id"] in ROSTER:
            return label(q[0]["user_id"]), "Transfer Done"
        before = [c for c in roster_calls if c["call_time"] <= q[0]["call_time"]]
        return (label(before[-1]["user_id"]) if before else (label(roster_calls[-1]["user_id"]) if roster_calls else NONE)), "Transfer Done"
    if f["doctor_called"]:
        q = [c for c in calls if c["user_id"] in doctors and c["user_talk"] >= 30 and c["call_time"] >= t["_created"]]
        before = [c for c in roster_calls if c["call_time"] <= q[0]["call_time"]]
        return (label(before[-1]["user_id"]) if before else NONE), "Doctor Called"
    return (label(roster_calls[-1]["user_id"]) if roster_calls else NONE), ""


def build(T, C, D, TG, last, first=None):
    first = first or last[:8] + "01"
    per, dump = {}, []
    for t in T:
        d = t["created_at"][:10]
        if not (t["_valid"] and first <= d <= last):
            continue
        f = oc.flags(t, C, D, TG)
        o, via = owner(t, f, D, TG)
        a = per.setdefault(o, {"n": 0, "con": 0, "tr": 0, "aht": []})
        a["n"] += 1; a["con"] += f["connected"]; a["tr"] += f["transferred"]
        a["aht"] += [c["user_talk"] for c in f["calls"] if c["user_talk"] >= 60]
        dump.append([t["ticket_id"], t["_phone"], t["created_at"], o, via,
                     "Yes" if f["connected"] else "No", "Yes" if f["transferred"] else "No"])
    return per, dump
