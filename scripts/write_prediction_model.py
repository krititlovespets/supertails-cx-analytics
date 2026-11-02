"""
Refreshes "Prediction Model" (the month of <last_banked_date>, 30% cumulative transfer target) from the
LIVE Main Dashboard (so the two can't disagree). Banked days = every date
column of the month on Main Dashboard up to <last_date>; forecast basis = October actual-to-date
average leads/day; remaining days get a FLAT daily quota (design choice 2026-09-17).
Rows are located by label; one day row per day of the month, TOTAL right below.
Usage: python3 write_prediction_model.py <last_banked_date> [--dry-run]
"""
import sys, re, calendar, gspread, os
from datetime import datetime

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = os.path.expanduser("~/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json")
TARGET = 0.30


def main():
    last = sys.argv[1]; dry = "--dry-run" in sys.argv
    sh = gspread.service_account(filename=KEY).open_by_key(SHEET_ID)
    md = sh.worksheet("Main Dashboard").get_all_values()
    H = md[0]; row = {r[0].split(" (")[0]: r for r in md[1:] if r[0]}
    vl_r, tt_r = row["Valid Leads"], row["Transfer Total"]
    month = last[:7]; ndays = calendar.monthrange(int(last[:4]), int(last[5:7]))[1]
    banked = [d for d in H if d.startswith(month) and d <= last]
    vl = {d: int(vl_r[H.index(d)]) for d in banked}; tt = {d: int(tt_r[H.index(d)]) for d in banked}
    nb = len(banked); rem = ndays - nb
    VL, TT = sum(vl.values()), sum(tt.values())
    basis = VL / nb; fc_leads = round(basis * rem); fc_total = VL + fc_leads
    needed = round(TARGET * fc_total); remaining = needed - TT
    rate = round(remaining / fc_leads, 3) if fc_leads else 0
    per_day_leads = round(basis); per_day_tr = round(per_day_leads * rate)
    print(f"banked {nb} days: {VL} leads, {TT} transfers ({TT / VL:.1%}); basis {basis:.1f}/day; forecast total {fc_total}; "
          f"needed {needed}; remaining {remaining}; required rate {rate:.1%}; flat quota {per_day_tr}/day")
    if dry:
        print("dry run - nothing written"); return
    ws = sh.worksheet("Prediction Model"); v = ws.get_all_values()
    MN = datetime.strptime(last, "%Y-%m-%d").strftime("%B"); MU = MN[:3].upper(); Mo = MN[:3]; L = f"{Mo} 1-{nb}"
    find = lambda rx: next(i for i, r in enumerate(v, 1) if re.match(rx, r[0]))
    pad = lambda r: r + [""] * (5 - len(r))
    upd = {}
    upd[1] = [f"=== PREDICTION MODEL -- {MN.upper()} ==="]
    upd[find("Forecast basis")] = [f"Forecast basis (daily valid leads): {basis:.1f}/day -- {MN}'s own actual-to-date average ({L}, rolling forward daily as more real days land)."]
    t = find("Transfer target"); upd[t] = [f"Transfer target: 30% cumulative, {Mo} 1-{ndays}"]
    t = find("Transfer = Transfer Done"); upd[t] = [v[t - 1][0].replace("Connect = User Talk Time > 30s", "Connect = User Talk Time >= 30s")]
    upd[find(r"\w+ window:")] = [f"{MN} window: {Mo} 1-{ndays} ({ndays} days). {L} is actual/banked ({nb} days); the remaining {rem} days are forecasted at {basis:.1f} leads/day = {fc_leads} forecasted leads."]
    upd[find(r"Forecasted total \w+ leads:")] = [f"Forecasted total {MN} leads: {VL} (actual, {L}) + {fc_leads} (forecasted, remaining {rem} days) = {fc_total}"]
    upd[find("ACTUAL,")] = [f"ACTUAL, {MU} 1-{nb} (banked so far -- {nb} of {ndays} days)"]
    upd[find("Valid Leads$")] = ["Valid Leads", VL]
    upd[find("Transfers$")] = ["Transfers", TT]
    upd[find("Transfer %$")] = ["Transfer %", round(TT / VL, 3)]
    upd[find("=== TARGET")] = [f"=== TARGET: 30% cumulative, {Mo} 1-{ndays} ==="]
    upd[find(r"Forecasted total \w+ leads$")] = [f"Forecasted total {MN} leads", fc_total]
    upd[find("Transfers needed")] = [f"Transfers needed ({int(TARGET * 100)}% of forecasted total)", needed]
    upd[find("Already banked")] = [f"Already banked ({L})", TT]
    upd[find("Remaining needed")] = [f"Remaining needed (remaining {rem} days)", remaining]
    upd[find("Required rate")] = ["Required rate on remaining forecasted leads", rate]
    actual_pct = TT / VL
    upd[find(r"[A-Z][a-z]{2} 1-\d+ actual")] = [f"{L} actual ({actual_pct:.1%}) is {'BELOW' if actual_pct < TARGET else 'AT/ABOVE'} the 30% target -- remaining days need to run at {rate:.1%} to still hit 30% for the full month."]
    upd[find("=== DAY-BY-DAY")] = [f"=== DAY-BY-DAY: TRANSFERS NEEDED, {MU} 1-{ndays} ==="]
    hdr = find("Date$"); base = datetime(1899, 12, 30)
    for i in range(ndays):
        d = f"{month}-{i + 1:02d}"; r = hdr + 1 + i
        ser = (datetime.strptime(d, "%Y-%m-%d") - base).days
        upd[r] = [ser] + (["Actual", vl[d], tt[d], round(tt[d] / vl[d], 3)] if d in vl else ["Forecast Target", per_day_leads, per_day_tr, rate])
    tot = hdr + 1 + ndays
    upd[tot] = [f"TOTAL ({Mo} 1-{ndays})", "Actual+Forecast", fc_total, needed, TARGET]
    old_tot = find("TOTAL")
    n = find("NOTE: This table")
    note = re.sub(r"\(\d+ forecasted leads x [\d.]+% required rate = \d+ transfers/day\)",
                  f"({per_day_leads} forecasted leads x {rate:.1%} required rate = {per_day_tr} transfers/day)", v[n - 1][0])
    upd[n] = [note.replace("real October days", f"real {MN} days").replace("latest October-to-date", f"latest {MN}-to-date").replace("Oct 1 through", f"{Mo} 1 through")]
    data = [{"range": f"'Prediction Model'!A{r}", "values": [val]} for r, val in upd.items()]
    if old_tot > tot:
        sh.batch_update({"requests": [{"copyPaste": {"source": {"sheetId": ws.id, "startRowIndex": old_tot - 1, "endRowIndex": old_tot, "startColumnIndex": 0, "endColumnIndex": 5},
                         "destination": {"sheetId": ws.id, "startRowIndex": tot - 1, "endRowIndex": tot, "startColumnIndex": 0, "endColumnIndex": 5}, "pasteType": "PASTE_FORMAT"}}]})
        ws.batch_clear([f"A{tot + 1}:E{old_tot}"])
    sh.values_batch_update({"valueInputOption": "RAW", "data": data})
    print(f"written {len(data)} rows")


if __name__ == "__main__":
    main()
