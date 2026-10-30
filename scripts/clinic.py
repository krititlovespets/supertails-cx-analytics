"""
Clinic Dashboard (1EyTmbBSkZMvL5JolKuo8xxOkguYGUKpTJTzlN68n5hM, tab Agent_Perf_V2) helpers.
Row 4 holds the daily date headers. Normally "DD/MM/YYYY" text, BUT from ~2026-10-30 days 1-12 of
each month show up as Sheets date serials (e.g. 46296) because "01/10/2026" got auto-parsed US-style
(month=01, day=10). Such a serial is converted back with day/month SWAPPED. Always validate the
result against already-known Booking Done values before writing.
"""
from datetime import datetime, timedelta

CLINIC_ID = "1EyTmbBSkZMvL5JolKuo8xxOkguYGUKpTJTzlN68n5hM"


def header_dates(h):
    out = {}
    for i, x in enumerate(h):
        x = str(x).strip()
        if x.count("/") == 2:
            d, m, y = x.split("/")
            out[i] = f"{y}-{int(m):02d}-{int(d):02d}"
        elif x.isdigit() and 40000 < int(x) < 60000 and i > 20:   # skip the month/week number columns
            dt = datetime(1899, 12, 30) + timedelta(days=int(x))
            if dt.day <= 12:                                        # parsed US-style: swap back
                out[i] = f"{dt.year}-{dt.day:02d}-{dt.month:02d}"
    return out


def daily(v, row_match):
    """v = get_all_values() of Agent_Perf_V2; row_match = predicate on a row. Returns {YYYY-MM-DD: int}."""
    hd = header_dates(v[3])
    r = next(x for x in v if row_match(x))
    return {d: int(r[i] or 0) for i, d in hd.items() if i < len(r)}


def open_sheet(gc):
    return gc.open_by_key(CLINIC_ID).worksheet("Agent_Perf_V2").get_all_values()
