"""
Writes Agent Productivity Table 6 (rows located by the "TABLE 6:" header, never by
fixed row number) and fully rewrites the "Table6 Raw Dump (Oct)" tab.
Usage: python3 write_table6.py <merged_nugget_csv> <merged_ameyo_csv> <last_date> [--dry-run]
"""
import sys, os, re, gspread
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oct_core as oc, table6 as t6

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"


def main():
    nug, ame, last = sys.argv[1:4]; dry = "--dry-run" in sys.argv
    T, C, D, TG = oc.load(nug, ame)
    per, dump = t6.build(T, C, D, TG, last)
    pct = lambda a, b: f"{100 * a / b:.1f}%" if b else "0.0%"
    hms = lambda xs: oc.sec_to_hms(sum(xs) / len(xs)) if xs else "00:00:00"
    agents = sorted((k for k in per if k != t6.NONE), key=lambda k: -per[k]["n"])
    rows = [[k, str(per[k]["n"]), str(per[k]["con"]), pct(per[k]["con"], per[k]["n"]), str(per[k]["tr"]),
             pct(per[k]["tr"], per[k]["n"]), hms(per[k]["aht"])] for k in agents]
    N = sum(per[k]["n"] for k in agents); CN = sum(per[k]["con"] for k in agents); TR = sum(per[k]["tr"] for k in agents)
    rows.append(["TEAM TOTAL (sum / sum -- matches Main Dashboard)", str(N), str(CN), pct(CN, N), str(TR), pct(TR, N),
                 hms([x for k in agents for x in per[k]["aht"]])])
    none = per.get(t6.NONE, {"n": 0})["n"]
    print(f"Table 6: {len(agents)} agents, team {N} tickets, {CN} connected, {TR} transferred ({pct(TR, N)}); no-roster {none}; dump {len(dump)} rows")
    if dry:
        print("dry run - nothing written"); return
    sh = gspread.service_account(filename=KEY).open_by_key(SHEET_ID)
    ws = sh.worksheet("Agent Productivity"); col = ws.col_values(1)
    h = next(i for i, x in enumerate(col, 1) if x.startswith("TABLE 6:"))
    assert col[h] == "Agent", col[h]
    note_r = next(i for i in range(h, 0, -1) if col[i - 1].startswith("NOTE (Table 6"))
    note = re.sub(r"refreshed through Oct\d+", f"refreshed through Oct{int(last[-2:])}", col[note_r - 1])
    start = h + 2; end = start + len(rows) - 1
    old_end = max(i for i, x in enumerate(col, 1) if i >= start and x) if len(col) >= start else start
    ws.update(range_name=f"A{start}:G{end}", values=rows, value_input_option="RAW")
    ws.update(range_name=f"A{note_r}", values=[[note]], value_input_option="RAW")
    if old_end > end:
        ws.batch_clear([f"A{end + 1}:G{old_end}"])
    dws = sh.worksheet("Table6 Raw Dump (Oct)")
    hdr = dws.row_values(1); old_n = len(dws.col_values(1))
    dump.sort(key=lambda r: r[2], reverse=True)
    if dws.row_count < len(dump) + 1:
        dws.resize(rows=len(dump) + 100)
    dws.update(range_name=f"A2:G{len(dump) + 1}", values=dump, value_input_option="RAW")
    if old_n > len(dump) + 1:
        dws.batch_clear([f"A{len(dump) + 2}:G{old_n}"])
    print(f"written: Table 6 rows {start}-{end}, dump header {hdr[:3]}..., {len(dump)} rows")


if __name__ == "__main__":
    main()
