"""
Booking Analysis (a month's section) -- Bangalore = channel "UCJ Booking Campaigns".
Per-agent funnel is SINGLE-OWNER (Kriti, 2026-11-02: agent denominators must add up to the team's):
each Bangalore ticket belongs to one row -- see owner(). Connected = any caller >=30s, credited to the
owner, so agents + "Not called by these 4" = the team total on both tickets and connects.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc

AGENTS = {"dhanush.slovespets@supertails.com": "Dhanush S", "alan.jlovespets@supertails.in": "Alan Joel",
          "abdul.rahmanlovespets@supertails.in": "Abdul Rahman", "mohammed.rolovespets@supertails.in": "Mohammed Roohulla"}


NONE = "Not called by these 4"


def owner(calls):
    """Single owner: last of the 4 with an own call >=30s, else last of the 4 who called, else NONE."""
    mine = [c for c in calls if c["user_id"] in AGENTS]   # calls are sorted by time
    conn = [c for c in mine if c["user_talk"] >= 30]
    return AGENTS[(conn or mine)[-1]["user_id"]] if mine else NONE


def build(T, C, last, first=None):
    first = first or last[:8] + "01"
    per = {n: {"called": 0, "conn": 0} for n in list(AGENTS.values()) + [NONE]}
    daily = {}
    for t in T:
        d = t["created_at"][:10]
        if t["channel_name"] != "UCJ Booking Campaigns" or not (first <= d <= last):
            continue
        calls = C.get(t["_phone"], [])
        connected = any(c["user_talk"] >= 30 for c in calls)
        dd = daily.setdefault(d, {"n": 0, "conn": 0}); dd["n"] += 1; dd["conn"] += connected
        o = per[owner(calls)]; o["called"] += 1; o["conn"] += connected
    return per, daily
