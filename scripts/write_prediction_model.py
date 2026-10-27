"""
Refreshes "Prediction Model" (October, 30% cumulative transfer target) from the
LIVE Main Dashboard (so the two can't disagree). Banked days = every October date
column on Main Dashboard up to <last_date>; forecast basis = October actual-to-date
average leads/day; remaining days get a FLAT daily quota (design choice 2026-09-17).
Rows are located by label; the 31 day rows (Oct 1-31) are fixed.
Usage: python3 write_prediction_model.py <last_banked_date> [--dry-run]
"""
import sys, re, calendar, gspread

SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY = "/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"
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
    L = f"Oct 1-{nb}"
    print(f"banked {nb} days: {VL} leads, {TT} transfers ({TT / VL:.1%}); basis {basis:.1f}/day; forecast total {fc_total}; "
          f"needed {needed}; remaining {remaining}; required rate {rate:.1%}; flat quota {per_day_tr}/day")
    if dry:
        print("dry run - nothing written"); return
    ws = sh.worksheet("Prediction Model"); v = ws.get_all_values()
    find = lambda p: next(i for i, r in enumerate(v, 1) if r[0].startswith(p))
    upd = {}
    upd[find("Forecast basis")] = [f"Forecast basis (daily valid leads): {basis:.1f}/day -- October's own actual-to-date average ({L}, rolling forward daily as more real days land)."]
    t = find("Transfer = Transfer Done"); upd[t] = [v[t - 1][0].replace("Connect = User Talk Time > 30s", "Connect = User Talk Time >= 30s")]
    upd[find("October window")] = [f"October window: Oct 1-{ndays} ({ndays} days). {L} is actual/banked ({nb} days); the remaining {rem} days are forecasted at {basis:.1f} leads/day = {fc_leads} forecasted leads."]
    upd[find("Forecasted total October leads:")] = [f"Forecasted total October leads: {VL} (actual, {L}) + {fc_leads} (forecasted, remaining {rem} days) = {fc_total}"]
    upd[find("ACTUAL, OCT")] = [f"ACTUAL, OCT 1-{nb} (banked so far -- {nb} of {ndays} days)"]
    upd[find("Valid Leads")] = ["Valid Leads", VL]
    upd[find("Transfers") ] = ["Transfers", TT]
    upd[find("Transfer %")] = ["Transfer %", round(TT / VL, 3)]
    upd[find("Forecasted total October leads") + 0 if False else next(i for i, r in enumerate(v, 1) if r[0] == "Forecasted total October leads")] = ["Forecasted total October leads", fc_total]
    upd[find("Transfers needed")] = [f"Transfers needed ({int(TARGET * 100)}% of forecasted total)", needed]
    upd[find("Already banked")] = [f"Already banked ({L})", TT]
    upd[find("Remaining needed")] = [f"Remaining needed (remaining {rem} days)", remaining]
    upd[find("Required rate")] = ["Required rate on remaining forecasted leads", rate]
    actual_pct = TT / VL
    upd[find(f"Oct 1-")] = [f"{L} actual ({actual_pct:.1%}) is {'BELOW' if actual_pct < TARGET else 'AT/ABOVE'} the 30% target -- remaining days need to run at {rate:.1%} to still hit 30% for the full month."]
    hdr = find("Date")
    for i in range(ndays):
        d = f"{month}-{i + 1:02d}"; r = hdr + 1 + i
        upd[r] = (["Actual", vl[d], tt[d], round(tt[d] / vl[d], 3)] if d in vl else ["Forecast Target", per_day_leads, per_day_tr, rate], "B")
    upd[find("TOTAL (Oct")] = ([f"TOTAL (Oct 1-{ndays})", "Actual+Forecast", fc_total, needed, TARGET], "A")
    n = find("NOTE: This table")
    upd[n] = [re.sub(r"\(\d+ forecasted leads x [\d.]+% required rate = \d+ transfers/day\)",
                     f"({per_day_leads} forecasted leads x {rate:.1%} required rate = {per_day_tr} transfers/day)", v[n - 1][0])]
    data = []
    for r, val in upd.items():
        vals, c = (val if isinstance(val, tuple) else (val, "A"))
        data.append({"range": f"'Prediction Model'!{c}{r}", "values": [vals]})
    sh.values_batch_update({"valueInputOption": "RAW", "data": data})
    print(f"written {len(data)} rows")


if __name__ == "__main__":
    main()
