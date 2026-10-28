"""
Main Dashboard rows "Avg Talk Time per Agent" and "Agents Available" (TEAM10 roster,
wiki/definitions.md), every October day up to <last_date>, plus their month columns:
  - Avg Talk Time per Agent, D = sum(talk) / sum(daily active agents)  (weighted)
  - Agents Available, B/C/D = daily average of the day columns (Kriti, 2026-10-27), 0.0 format
Usage: python3 write_team_rows.py <merged_ameyo_csv> <last_date> [--dry-run]
"""
import sys, csv, gspread
from datetime import datetime
from collections import defaultdict

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"
TEAM = {"raisa.qlovespets@supertails.in", "hammad.shaikhlovespets@supertails.in", "shazali.snlovespets@supertails.in",
        "arjun.llovespets@supertails.in", "riddi.plovespets@supertails.in", "alan.jlovespets@supertails.in",
        "dhanush.slovespets@supertails.com", "abdul.rahmanlovespets@supertails.in", "mohammed.rolovespets@supertails.in"}


def hms(x):
    x = int(round(x)); return f"{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}"


def sec(s):
    try:
        h, m, z = map(int, s.split(":")); return h * 3600 + m * 60 + z
    except ValueError:
        return 0


def main():
    ame, last = sys.argv[1:3]; dry = "--dry-run" in sys.argv
    talk = defaultdict(int); ag = defaultdict(set)
    for r in csv.DictReader(open(ame, encoding="utf-8-sig")):
        u = r["User ID"].strip().lower()
        if u in TEAM:
            d = datetime.strptime(r["Call Time"], "%d/%m/%Y %I:%M:%S %p").strftime("%Y-%m-%d")
            if d <= last:
                talk[d] += sec(r["User Talk Time"]); ag[d].add(u)
    days = sorted(talk)
    sh = gspread.service_account(filename=KEY).open_by_key(SHEET_ID); ws = sh.worksheet("Main Dashboard")
    v = ws.get_all_values(); H = v[0]; A = [r[0] for r in v]
    r12 = next(i for i, x in enumerate(A, 1) if x.startswith("Avg Talk Time per Agent"))
    r15 = next(i for i, x in enumerate(A, 1) if x.startswith("Agents Available"))
    col = lambda i: gspread.utils.rowcol_to_a1(1, i + 1)[:-1]
    data = []
    for d in days:
        c = col(H.index(d))
        data += [{"range": f"Main Dashboard!{c}{r12}", "values": [[hms(talk[d] / len(ag[d]))]]},
                 {"range": f"Main Dashboard!{c}{r15}", "values": [[len(ag[d])]]}]
    d12 = hms(sum(talk.values()) / sum(len(ag[d]) for d in days))
    row15 = v[r15 - 1]
    def avg(lo, hi):
        x = [int(float(row15[i])) for i, h in enumerate(H) if lo <= h <= hi and i < len(row15) and row15[i].strip()]
        x = [n for n in x]; return x
    sep = avg("2026-09-01", "2026-09-30"); s1630 = avg("2026-09-16", "2026-09-30")
    octd = [len(ag[d]) for d in days]
    B, C, D = [round(sum(x) / len(x), 1) for x in (sep, s1630, octd)]
    data += [{"range": f"Main Dashboard!D{r12}", "values": [[d12]]},
             {"range": f"Main Dashboard!B{r15}:D{r15}", "values": [[B, C, D]]}]
    print(f"{last}: talk/agent {hms(talk[last] / len(ag[last]))}, agents {len(ag[last])}; Oct D12 {d12}; Agents Avail B/C/D {B}/{C}/{D}")
    if dry:
        print("dry run - nothing written"); return
    sh.values_batch_update({"valueInputOption": "RAW", "data": data})
    ws.format(f"B{r15}:D{r15}", {"numberFormat": {"type": "NUMBER", "pattern": "0.0"}})
    print("written")


if __name__ == "__main__":
    main()
