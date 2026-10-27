"""
Booking Analysis (October section) -- Bangalore = channel "UCJ Booking Campaigns".
Per-agent: Called = Bangalore tickets in range whose phone this agent dialled (any time);
Connected = this agent's OWN call >=30s on that phone. Daily table + summary use the
team-wide any-caller >=30s Connect basis (same as Main Dashboard).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc

AGENTS = {"dhanush.slovespets@supertails.com": "Dhanush S", "alan.jlovespets@supertails.in": "Alan Joel",
          "abdul.rahmanlovespets@supertails.in": "Abdul Rahman", "mohammed.rolovespets@supertails.in": "Mohammed Roohulla"}


def build(T, C, last, first="2026-10-01"):
    per = {n: {"called": 0, "conn": 0} for n in AGENTS.values()}
    daily = {}
    for t in T:
        d = t["created_at"][:10]
        if t["channel_name"] != "UCJ Booking Campaigns" or not (first <= d <= last):
            continue
        calls = C.get(t["_phone"], [])
        dd = daily.setdefault(d, {"n": 0, "conn": 0}); dd["n"] += 1
        dd["conn"] += any(c["user_talk"] >= 30 for c in calls)
        for e, n in AGENTS.items():
            mine = [c for c in calls if c["user_id"] == e]
            if mine:
                per[n]["called"] += 1
                per[n]["conn"] += any(c["user_talk"] >= 30 for c in mine)
    return per, daily
