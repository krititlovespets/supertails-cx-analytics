"""
Writes the month's single-owner table on Agent Productivity (Table 6 = October, Table 7 = November;
rows located by the "TABLE n:" header, never by fixed row number; created below the last table on
the first run) and fully rewrites that month's raw dump tab. Earlier months' tables are frozen.
Usage: python3 write_table6.py <merged_nugget_csv> <merged_ameyo_csv> <last_date> [--dry-run]
"""
import sys, os, re, gspread
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc, table6 as t6

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"


def main():
    nug, ame, last = sys.argv[1:4]; dry = "--dry-run" in sys.argv
    mdt = datetime.strptime(last, "%Y-%m-%d"); MN, Mon = mdt.strftime("%B"), mdt.strftime("%b")
    TN = {"2026-10": 6, "2026-11": 7}.get(last[:7], mdt.month - 4)
    dump_tab = f"Table{TN} Raw Dump ({Mon})"
    T, C, D, TG = oc.load(nug, ame)
    per, dump = t6.build(T, C, D, TG, last)
    pct = lambda a, b: f"{100 * a / b:.1f}%" if b else "0.0%"
    # agent's OWN October talk time (all their calls, not just valid leads), through last
    talk = {k: 0 for k in t6.ROSTER}; days = {k: set() for k in t6.ROSTER}
    for calls in C.values():
        for c in calls:
            d = c["call_time"].strftime("%Y-%m-%d")
            if c["user_id"] in t6.ROSTER and last[:8] + "01" <= d <= last:
                talk[c["user_id"]] += c["user_talk"]; days[c["user_id"]].add(d)
    email = lambda label: label.rsplit("(", 1)[1].rstrip(")")
    longhms = lambda x: f"{int(x) // 3600:02d}:{int(x) % 3600 // 60:02d}:{int(x) % 60:02d}"
    hms = lambda xs: oc.sec_to_hms(sum(xs) / len(xs)) if xs else "00:00:00"
    agents = sorted((k for k in per if k != t6.NONE), key=lambda k: -per[k]["n"])
    rows = [[k, str(per[k]["n"]), str(per[k]["con"]), pct(per[k]["con"], per[k]["n"]), str(per[k]["tr"]),
             pct(per[k]["tr"], per[k]["n"]), hms(per[k]["aht"]),
             longhms(talk[email(k)]), str(len(days[email(k)])),
             longhms(talk[email(k)] / len(days[email(k)])) if days[email(k)] else "00:00:00"] for k in agents]
    TT = sum(talk[email(k)] for k in agents); TD = sum(len(days[email(k)]) for k in agents)
    N = sum(per[k]["n"] for k in agents); CN = sum(per[k]["con"] for k in agents); TR = sum(per[k]["tr"] for k in agents)
    rows.append(["TEAM TOTAL (sum / sum -- matches Main Dashboard)", str(N), str(CN), pct(CN, N), str(TR), pct(TR, N),
                 hms([x for k in agents for x in per[k]["aht"]]), longhms(TT), str(TD), longhms(TT / TD) if TD else "00:00:00"])
    none = per.get(t6.NONE, {"n": 0})["n"]
    print("talk:", "; ".join(f"{r[0].split(' (')[0]} {r[7]} / {r[8]}d / {r[9]}" for r in rows))
    print(f"Table {TN}: {len(agents)} agents, team {N} tickets, {CN} connected, {TR} transferred ({pct(TR, N)}); no-roster {none}; dump {len(dump)} rows")
    if dry:
        print("dry run - nothing written"); return
    sh = gspread.service_account(filename=KEY).open_by_key(SHEET_ID)
    ws = sh.worksheet("Agent Productivity"); col = ws.col_values(1)
    h = next((i for i, x in enumerate(col, 1) if x.startswith(f"TABLE {TN}:")), None)
    if h is None:   # first run of the month: build the block under the last table
        prev = next(i for i in range(len(col), 0, -1) if col[i - 1].startswith("NOTE (Table "))
        base = next(x for x in col if x.startswith("NOTE (Table 6"))
        note0 = base.replace("NOTE (Table 6", f"NOTE (Table {TN}").replace("October", MN).replace("Oct1", f"{Mon}1")
        note0 = re.sub(r"refreshed through \w+", f"refreshed through {Mon}{int(last[-2:])}", note0)
        note0 = note0.replace("(added 2026-10-28) ", "")
        n = len(col) + 2
        need = n + 5 + len(rows) + 2
        if ws.row_count < need:
            ws.resize(rows=need + 10)
        ws.update(range_name=f"A{n}", values=[[note0]], value_input_option="RAW")
        ws.update(range_name=f"A{n + 2}:A{n + 3}", values=[[f"TABLE {TN}: {MN} Valid Leads, Ticket-Level (single owner per ticket, reconciles with team Transfer % and Connect %)"], ["Agent"]], value_input_option="RAW")
        sh.batch_update({"requests": [{"copyPaste": {"source": {"sheetId": ws.id, "startRowIndex": prev - 1, "endRowIndex": prev, "startColumnIndex": 0, "endColumnIndex": 1},
                                        "destination": {"sheetId": ws.id, "startRowIndex": n - 1, "endRowIndex": n, "startColumnIndex": 0, "endColumnIndex": 1}, "pasteType": "PASTE_FORMAT"}}]})
        col = ws.col_values(1); h = n + 2
    assert col[h] == "Agent", col[h]
    ws.update(range_name=f"A{h + 1}:J{h + 1}", values=[["Agent", "Tickets Dialled", "Connected", "Connect %", "Transferred",
              "Transfer %", "AHT", f"Total Talk Time (own calls, {Mon})", "Days Worked (>=1 call)", "Avg Talk Time / Working Day"]],
              value_input_option="RAW")
    note_r = next(i for i in range(h, 0, -1) if col[i - 1].startswith(f"NOTE (Table {TN}"))
    note = re.sub(r"refreshed through \w+", f"refreshed through {Mon}{int(last[-2:])}", col[note_r - 1])
    start = h + 2; end = start + len(rows) - 1
    old_end = max(i for i, x in enumerate(col, 1) if i >= start and x) if len(col) >= start else start
    ws.update(range_name=f"A{start}:J{end}", values=rows, value_input_option="RAW")
    ws.update(range_name=f"A{note_r}", values=[[note]], value_input_option="RAW")
    if old_end > end:
        ws.batch_clear([f"A{end + 1}:J{old_end}"])
    try:
        dws = sh.worksheet(dump_tab)
    except gspread.WorksheetNotFound:
        dws = sh.add_worksheet(dump_tab, rows=len(dump) + 200, cols=7)
        dws.update(range_name="A1:G1", values=[["Ticket ID", "Phone", "Created At", "Owner Agent", "Transfer Via", "Connected (ticket-level, any caller >=30s)", "Transferred"]], value_input_option="RAW")
    hdr = dws.row_values(1); old_n = len(dws.col_values(1))
    dump.sort(key=lambda r: r[2], reverse=True)
    if dws.row_count < len(dump) + 1:
        dws.resize(rows=len(dump) + 100)
    dws.update(range_name=f"A2:G{len(dump) + 1}", values=dump, value_input_option="RAW")
    if old_n > len(dump) + 1:
        dws.batch_clear([f"A{len(dump) + 2}:G{old_n}"])
    print(f"written: Table {TN} rows {start}-{end}, dump header {hdr[:3]}..., {len(dump)} rows")


if __name__ == "__main__":
    main()
