"""
Reads the LIVE Main Dashboard and checks every formula row, date continuity and month-column sums.
Prints only problems plus a summary. Usage: python3 verify_main_dashboard.py
"""
import datetime as dt, gspread, os
SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = os.path.expanduser("~/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json")
v = gspread.service_account(filename=KEY).open_by_key(SHEET_ID).worksheet("Main Dashboard").get_all_values(); H = v[0]
R = {r[0].split(" (")[0].strip(): r for r in v[1:] if r and r[0]}
k = lambda s: R[next(n for n in R if n.startswith(s))]
def num(x):
    x = x.strip().replace("%", "").replace(",", "")
    try: return float(x)
    except ValueError: return None
VL, TT, TP, TD, DC, AB, CN, CP, CD, UB, BD, BP, BN, VT, VR, VP = [k(s) for s in ["Valid Leads", "Transfer Total", "Transfer %", "Transfer Done", "Doctor Called",
    "Absolute Transfer", "Connect", "Connect %", "Connect Needed", "UCJ Bangalore", "Booking Done", "% Booking", "Bookings Needed", "Vet Follow-up Transferred", "Vet Follow-up 15", "Vet Follow-up Repeat %"]]
dates = [(i, h) for i, h in enumerate(H) if h[:4] == "2026"]
ds = [dt.date.fromisoformat(h) for _, h in dates]
print("dates", dates[0][1], "->", dates[-1][1], len(ds), "missing:", sorted({ds[0] + dt.timedelta(n) for n in range((ds[-1] - ds[0]).days + 1)} - set(ds)))
bad = 0
for i, h in [(1, "Sept"), (2, "Sep16-30"), (3, "Oct"), (4, "Nov")] + dates:
    g = lambda r: num(r[i]) if i < len(r) else None
    vl, tt, td, dc = g(VL), g(TT), g(TD), g(DC)
    if None in (vl, tt, td, dc): print(h, "blank"); bad += 1; continue
    checks = [(td + dc, tt, "Done+Doctor"), (g(TP), round(100 * tt / vl, 1), "Transfer%"), (g(AB), round(vl * .3) - tt, "ToDo"), (g(CP), round(100 * g(CN) / vl, 1), "Connect%"),
              (g(CD), round(vl * .6) - g(CN), "ConnectNeeded"), (g(BN), round(g(UB) * .065) - g(BD), "BookingsNeeded")]
    if g(UB): checks.append((g(BP), round(100 * g(BD) / g(UB), 1), "Booking%"))
    if g(VT): checks.append((g(VP), round(100 * g(VR) / g(VT), 1), "Vet%"))
    for a, b, n in checks:
        if a is None or abs(a - b) > 0.051: print(h, n, a, b); bad += 1
for m, col in [("2026-09", 1), ("2026-10", 3), ("2026-11", 4)]:
    for name, r in [("VL", VL), ("TT", TT), ("CN", CN), ("UB", UB), ("BD", BD), ("VT", VT), ("VR", VR)]:
        s = sum(num(r[i]) or 0 for i, h in dates if h.startswith(m) and i < len(r))
        if s != num(r[col]): print("month sum", m, name, r[col], s); bad += 1
print("problems:", bad)
