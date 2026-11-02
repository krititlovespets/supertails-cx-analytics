#!/usr/bin/env python3
"""
Update the Chat dashboard Google Sheet from CX ticket exports.

    python3 update_chat_dashboard.py NEW_EXPORT.csv [MORE.csv ...] [--dry-run] [--base sheet|none]

What it does
  1. Base data = the "Chat - Raw Dump (Sep 1+)" tab (default), or nothing (--base none).
  2. Merges the CSV(s) you pass (oldest -> newest), keeps only the UCJ SC Chat Assistance
     channel, de-dupes on ticket_id (newest row wins), sorts by created_at, checks for
     missing calendar days.
  3. Recomputes every metric and rewrites three tabs:
        Chat - Daily Summary | Chat - Agent Summary | Chat - Raw Dump (Sep 1+)
     It never touches any other tab in the spreadsheet.

--dry-run computes everything and diffs it against the live sheet WITHOUT writing.
Requires: python3, pandas, gspread, and a Google service-account JSON key with Editor
access to the sheet (see README.md).
"""
import argparse
import calendar
import datetime
import math
import os
import sys
import time

import gspread
import pandas as pd
from gspread.utils import rowcol_to_a1 as A1

# ============================== CONFIG ==============================
SHEET_ID = "1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw"
KEY_PATH = "~/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"
CHANNEL = "UCJ SC Chat Assistance"
START_DATE = datetime.date(2026, 9, 1)             # first day of the series (gap check)
DAY_START = datetime.time(9, 0, 0)                 # Day window: 09:00:00 .. 20:45:00 inclusive
DAY_END = datetime.time(20, 45, 0)                 # OBH = everything else
EXCLUDE_FROM_DAY_AGENT_VIEW = {"Akshaya", "Dhanush S", "Farhan", "Dr Sahithya"}
TAB_DAILY = "Chat - Daily Summary"
TAB_AGENT = "Chat - Agent Summary"
TAB_RAW = "Chat - Raw Dump (Sep 1+)"
RAW_COLS = ["ticket_id", "created_at", "agent_name", "agent_assigned_at", "resolved_by",
            "resolved_at", "last_agent_assignment", "agent_frt_response_at"]
SHADE_DAY = {"red": 0.93, "green": 0.93, "blue": 0.88}
SHADE_OBH = {"red": 0.95, "green": 0.92, "blue": 0.85}
# ====================================================================


def with_retry(fn, *a, **k):
    """Google Sheets allows ~60 writes/min/user; back off on 429 instead of failing."""
    for attempt in range(1, 8):
        try:
            return fn(*a, **k)
        except gspread.exceptions.APIError as e:
            if "429" in str(e) and attempt < 7:
                wait = 15 * attempt
                print(f"  rate-limited by Sheets, waiting {wait}s ...", flush=True)
                time.sleep(wait)
            else:
                raise


def fmt_time(v):
    """<=60s -> '45s'; <60m -> '6m 32s'; >=60m -> '7h 3m 27s'."""
    if v is None or v == "" or (isinstance(v, float) and math.isnan(v)):
        return ""
    s = round(v)
    if s <= 60:
        return f"{s}s"
    m, sec = divmod(s, 60)
    if m < 60:
        return f"{m}m {sec}s" if sec else f"{m}m"
    h, mm = divmod(m, 60)
    out = f"{h}h"
    if mm:
        out += f" {mm}m"
    if sec:
        out += f" {sec}s"
    return out


def month_name(ym):
    return calendar.month_abbr[int(ym[5:7])]


# ============================== LOAD / MERGE ==============================
def load_csv(path):
    d = pd.read_csv(path, dtype=str, keep_default_na=False, low_memory=False,
                    usecols=RAW_COLS + ["channel_name"])
    d = d[d["channel_name"] == CHANNEL][RAW_COLS]
    print(f"  {os.path.basename(path)}: {len(d)} {CHANNEL} rows")
    return d


def load_base(sh):
    vals = with_retry(sh.worksheet(TAB_RAW).get_all_values)
    if not vals:
        return pd.DataFrame(columns=RAW_COLS)
    d = pd.DataFrame(vals[1:], columns=vals[0])
    missing = [c for c in RAW_COLS if c not in d.columns]
    if missing:
        sys.exit(f"Raw Dump tab is missing columns {missing}; rebuild it with --base none from the source CSVs.")
    d = d[d["ticket_id"].str.strip() != ""][RAW_COLS]
    print(f"  sheet base ({TAB_RAW}): {len(d)} rows")
    return d


def merge(base, new_frames):
    n_base = len(base)
    new = pd.concat(new_frames, ignore_index=True) if new_frames else pd.DataFrame(columns=RAW_COLS)
    overlap = len(set(base["ticket_id"]) & set(new["ticket_id"])) if n_base and len(new) else 0
    merged = pd.concat([base, new], ignore_index=True)
    merged["ticket_id"] = merged["ticket_id"].str.strip()
    merged = merged.drop_duplicates(subset="ticket_id", keep="last")      # newest export wins
    merged["_c"] = pd.to_datetime(merged["created_at"], errors="coerce")
    merged = merged.dropna(subset=["_c"]).sort_values("_c")
    print(f"  merged: {len(merged)} tickets, {merged['_c'].min()} -> {merged['_c'].max()}")
    seen = set(merged["_c"].dt.date)
    last = merged["_c"].max().date()
    missing = [str(START_DATE + datetime.timedelta(days=i))
               for i in range((last - START_DATE).days + 1)
               if (START_DATE + datetime.timedelta(days=i)) not in seen]
    if missing:
        print(f"  !! WARNING missing calendar days (not zero, just no data): {missing}")
    if n_base and len(new) and overlap == 0:
        print("  !! WARNING new export has NO overlap with existing data. Tickets created in the "
              "last few days before this export keep stale resolved_at/FRT values. "
              "Next time export from ~3 days earlier than the last date you have.")
    return merged.drop(columns="_c")


def prepare(merged):
    r = merged.copy()
    for c in ["created_at", "agent_assigned_at", "agent_frt_response_at", "resolved_at"]:
        r[c] = pd.to_datetime(r[c], errors="coerce")
    r["agent_name"] = r["agent_name"].replace("", pd.NA)
    r["actual_frt"] = (r["agent_frt_response_at"] - r["created_at"]).dt.total_seconds()
    r["day_starting_frt"] = (r["agent_frt_response_at"] - r["agent_assigned_at"]).dt.total_seconds()
    r["resolve_seconds"] = (r["resolved_at"] - r["agent_assigned_at"]).dt.total_seconds()
    return r


def window_masks_and_dates(r, ts_col):
    """Day/OBH masks + the 'date' each row is reported under (OBH = shift start day)."""
    ts = r[ts_col]
    t = ts.dt.time
    day = ts.notna() & (t >= DAY_START) & (t <= DAY_END)
    obh = ts.notna() & ~day
    d = ts.dt.date
    shift = d.where(t >= DAY_END, d - pd.Timedelta(days=1))   # 20:45+ keeps its date, earlier -> previous day
    return day, obh, d.astype(str), shift.astype(str)


# ============================== COMPUTE ==============================
def _stats(df, col):
    return (len(df),
            round(df[col].mean(), 1) if len(df) else None,
            round(df[col].median(), 1) if len(df) else None)


def compute_daily_block(sub, date_series):
    sub = sub.copy()
    sub["date"] = date_series.loc[sub.index]
    sub = sub[sub["agent_name"].notna()]
    actual = sub[sub["actual_frt"].notna() & (sub["actual_frt"] >= 0)]
    dstart = sub[sub["day_starting_frt"].notna() & (sub["day_starting_frt"] >= 0)]
    resolve = sub[sub["resolve_seconds"].notna()]
    dates = sorted(sub["date"].unique())
    months = sorted(set(d[:7] for d in dates))

    def agg(df, col):
        return df.groupby("date")[col].agg(["count", "mean", "median"]).round(1)
    a_d, d_d, r_d = agg(actual, "actual_frt"), agg(dstart, "day_starting_frt"), agg(resolve, "resolve_seconds")
    t_d = sub.groupby("date").size()

    def cell(tbl, dt, k):
        return float(tbl.loc[dt, k]) if dt in tbl.index else None

    month_stats = {}
    for m in months:
        a = _stats(actual[actual["date"].str.startswith(m)], "actual_frt")
        d = _stats(dstart[dstart["date"].str.startswith(m)], "day_starting_frt")
        rr = _stats(resolve[resolve["date"].str.startswith(m)], "resolve_seconds")
        month_stats[m] = {"total": int(sub["date"].str.startswith(m).sum()),
                          "actual_count": a[0], "actual_avg": a[1], "actual_median": a[2],
                          "dstart_count": d[0], "dstart_avg": d[1], "dstart_median": d[2],
                          "resolve_count": rr[0], "resolve_avg": rr[1], "resolve_median": rr[2]}
    per_date = {}
    for dt in dates:
        per_date[dt] = {"total": int(t_d.get(dt, 0)),
                        "actual_count": int(a_d.loc[dt, "count"]) if dt in a_d.index else 0,
                        "actual_avg": cell(a_d, dt, "mean"), "actual_median": cell(a_d, dt, "median"),
                        "dstart_count": int(d_d.loc[dt, "count"]) if dt in d_d.index else 0,
                        "dstart_avg": cell(d_d, dt, "mean"), "dstart_median": cell(d_d, dt, "median"),
                        "resolve_count": int(r_d.loc[dt, "count"]) if dt in r_d.index else 0,
                        "resolve_avg": cell(r_d, dt, "mean"), "resolve_median": cell(r_d, dt, "median")}
    return {"dates": dates, "months": months, "month_stats": month_stats, "per_date": per_date}


def compute_agent_block(sub, date_series, exclude=None):
    sub = sub.copy()
    sub["date"] = date_series.loc[sub.index]
    sub = sub[sub["agent_name"].notna()]
    if exclude:
        sub = sub[~sub["agent_name"].isin(exclude)]
    frt = sub[sub["day_starting_frt"].notna() & (sub["day_starting_frt"] >= 0)]
    res = sub[sub["resolve_seconds"].notna()]
    dates = sorted(sub["date"].unique())
    months = sorted(set(d[:7] for d in dates))
    agents = sorted(sub["agent_name"].unique())

    def mavg(df, col, m, agent=None):
        s = df[df["date"].str.startswith(m)]
        if agent is not None:
            s = s[s["agent_name"] == agent]
        return round(s[col].mean(), 1) if len(s) else None

    per_agent_month = {a: {m: {"frt_avg": mavg(frt, "day_starting_frt", m, a),
                               "resolve_avg": mavg(res, "resolve_seconds", m, a)} for m in months} for a in agents}
    team_month = {m: {"frt_avg": mavg(frt, "day_starting_frt", m), "resolve_avg": mavg(res, "resolve_seconds", m)}
                  for m in months}

    def pivot(df, col):
        p = df.pivot_table(index="agent_name", columns="date", values=col, aggfunc="mean").round(1)
        return {a: {d: (None if pd.isna(v) else float(v)) for d, v in row.items()} for a, row in p.iterrows()}
    frt_pivot, res_pivot = pivot(frt, "day_starting_frt"), pivot(res, "resolve_seconds")

    date_frt = frt.groupby("date")["day_starting_frt"].mean().round(1)
    date_res = res.groupby("date")["resolve_seconds"].mean().round(1)
    team_date = {d: {"frt_avg": float(date_frt[d]) if d in date_frt.index else None,
                     "resolve_avg": float(date_res[d]) if d in date_res.index else None} for d in dates}

    counts = {a: sub[sub["agent_name"] == a].groupby("date").size() for a in agents}
    count_matrix = {a: {d: (int(counts[a][d]) if d in counts[a].index else None) for d in dates} for a in agents}
    totals = {}
    for a in agents:
        tot = int((sub["agent_name"] == a).sum())
        dw = sub[sub["agent_name"] == a]["date"].nunique()
        totals[a] = {"total": tot, "avg_per_day": round(tot / dw, 1) if dw else None}
    per_date_totals = {d: int((sub["date"] == d).sum()) for d in dates}
    return {"dates": dates, "months": months, "agents": agents, "per_agent_month": per_agent_month,
            "team_month": team_month, "team_date": team_date, "frt_pivot": frt_pivot, "res_pivot": res_pivot,
            "count_matrix": count_matrix, "totals": totals, "per_date_totals": per_date_totals,
            "team_total": int(len(sub)),
            "team_avg_per_day": round(len(sub) / len(dates), 1) if dates else None}


# ============================== BUILD SHEET CONTENT ==============================
def _fmts():
    out = []

    def bold(rng):
        out.append({"range": rng, "format": {"textFormat": {"bold": True}}})

    def shade(rng, c):
        out.append({"range": rng, "format": {"textFormat": {"bold": True}, "backgroundColor": c}})
    return out, bold, shade


def build_daily(day, obh):
    def block(title, B):
        dates, months, ms, pdt = B["dates"], B["months"], B["month_stats"], B["per_date"]

        def row(label, key, conv=False):
            mv = [ms[m][key] for m in months]
            dv = [pdt[d][key] for d in dates]
            f = (lambda v: fmt_time(v)) if conv else (lambda v: "" if v is None else v)
            return [label] + [f(v) for v in mv] + [f(v) for v in dv]
        return [[title],
                ["Metric"] + [f"{month_name(m)} Avg" for m in months] + dates,
                row("Tickets (n)", "total"),
                row("Actual FRT Tickets (n)", "actual_count"),
                row("Avg Actual FRT", "actual_avg", True),
                row("Median Actual FRT", "actual_median", True),
                row("Day Starting FRT Tickets (n)", "dstart_count"),
                row("Avg Day Starting FRT", "dstart_avg", True),
                row("Median Day Starting FRT", "dstart_median", True),
                row("Resolution Tickets (n)", "resolve_count"),
                row("Avg Resolution", "resolve_avg", True),
                row("Median Resolution", "resolve_median", True)]
    d_rows = block("Day Chat Messages (9 AM – 8:45 PM) — Daily Summary  [bucketed by created_at]", day)
    o_rows = block("OBH Chat Messages (8:45 PM – 9 AM) — Daily Summary  [bucketed by created_at, date = shift start day]", obh)
    notes = [[],
             ["Scope: UCJ SC Chat Assistance. Both blocks bucketed by created_at (message arrival) — Day = created 9:00 AM–8:45 PM, OBH = created 8:45 PM–9:00 AM (grouped by shift start date)."],
             ["Actual FRT = agent_frt_response_at − created_at — true end-to-end customer wait."],
             ["Day Starting FRT = agent_frt_response_at − agent_assigned_at — agent speed once actually assigned the ticket."],
             ["Resolution time = resolved_at − agent_assigned_at, unchanged."],
             ["Values ≤60s = seconds; >60s and <60m = minutes; ≥60m = hours (7h 3m 27s)."],
             ["OBH's \"Aug Avg\" is just the tail of the overnight shift that started Aug 31 — not a full day."]]
    rows = d_rows + [[]] + o_rows + notes
    fm, bold, shade = _fmts()
    ndm, nom = len(day["months"]), len(obh["months"])
    bold("A1"); bold(f"A2:{A1(2, len(day['dates']) + ndm + 1)}"); bold("A2:A12")
    shade(f"B2:{A1(12, 1 + ndm)}", SHADE_DAY)
    ot, oh, ol = 14, 15, 25
    bold(f"A{ot}"); bold(f"A{oh}:{A1(oh, len(obh['dates']) + nom + 1)}"); bold(f"A{oh}:A{ol}")
    shade(f"B{oh}:{A1(ol, 1 + nom)}", SHADE_OBH)
    ncols = max(len(day["dates"]) + ndm, len(obh["dates"]) + nom) + 2
    return rows, fm, (2, 1 + max(ndm, nom)), ncols


def build_agent(day, obh):
    def avg_matrix(title, D, ao, pivot, key):
        months, dates = D["months"], D["dates"]
        rows = [[title], ["Agent"] + [f"{month_name(m)} Avg" for m in months] + dates]
        for a in ao:
            rows.append([a] + [fmt_time(D["per_agent_month"][a][m][key]) for m in months]
                        + [fmt_time(D[pivot].get(a, {}).get(d)) for d in dates])
        rows.append(["Team Average"] + [fmt_time(D["team_month"][m][key]) for m in months]
                    + [fmt_time(D["team_date"][d][key]) for d in dates])
        return rows

    def ticket_matrix(title, D, ao):
        months, dates = D["months"], D["dates"]
        rows = [[title], ["Agent"] + [f"{month_name(m)} Total" for m in months] + ["Avg / Working Day"] + dates]
        for a in ao:
            cm = D["count_matrix"][a]
            rows.append([a] + [sum(cm.get(d) or 0 for d in dates if d.startswith(m)) for m in months]
                        + [D["totals"][a]["avg_per_day"]] + [("" if cm.get(d) is None else cm[d]) for d in dates])
        rows.append(["Team Total"] + [sum(D["per_date_totals"][d] for d in dates if d.startswith(m)) for m in months]
                    + [D["team_avg_per_day"]] + [D["per_date_totals"][d] for d in dates])
        return rows

    def section(label, D):
        ao = sorted(D["agents"], key=lambda a: -D["totals"][a]["total"])
        return [avg_matrix(f"Average FRT — Agent x Date  [{label}]", D, ao, "frt_pivot", "frt_avg"),
                avg_matrix(f"Average Resolution Time — Agent x Date  [{label}]", D, ao, "res_pivot", "resolve_avg"),
                ticket_matrix(f"Tickets Handled — Agent x Date  [{label}]", D, ao)], len(ao)

    day_blocks, day_n = section("Day 9AM–8:45PM", day)
    obh_blocks, obh_n = section("OBH 8:45PM–9AM, date=shift start", obh)
    notes = [["Scope: UCJ SC Chat Assistance. Day = tickets assigned to an agent 9:00 AM–8:45 PM. OBH = 8:45 PM–9:00 AM, grouped by shift start date."],
             ["Day blocks: Daksha K, Ganashree D, Salman Pasha, Shazali Sanober only; Team Average/Total reflect only these 4."],
             ["OBH blocks include every agent who worked a night shift, no exclusions."],
             ["FRT = agent_frt_response_at − agent_assigned_at. Resolution = resolved_at − agent_assigned_at."],
             ["Values ≤60s = seconds; >60s and <60m = minutes; ≥60m = hours."]]
    rows = []
    for b in day_blocks + obh_blocks:
        rows += b + [[]]
    rows += notes
    fm, bold, shade = _fmts()
    row = 1
    for D, n, sc in [(day, day_n, SHADE_DAY), (obh, obh_n, SHADE_OBH)]:
        nm, nd = len(D["months"]), len(D["dates"])
        for i in range(3):
            extra = 1 if i == 2 else 0
            width = nd + nm + 1 + extra
            hdr = row + 1
            bold(f"A{row}"); bold(f"A{hdr}:{A1(hdr, width)}")
            shade(f"B{hdr}:{A1(hdr + n + 1, 1 + nm + extra)}", sc)
            team_r = hdr + n + 1
            shade(f"A{team_r}:{A1(team_r, width)}", sc)
            row = team_r + 2
    ncols = max(len(day["dates"]) + len(day["months"]), len(obh["dates"]) + len(obh["months"])) + 3
    return rows, fm, (2, 1 + max(len(day["months"]), len(obh["months"]))), ncols


# ============================== PUSH / DIFF ==============================
def same(a, b):
    a, b = str(a).strip(), str(b).strip()
    if a == b:
        return True
    try:
        return abs(float(a) - float(b)) < 1e-9
    except ValueError:
        return False


def diff_with_live(ws, rows):
    live = with_retry(ws.get_all_values)
    bad = []
    for i, r in enumerate(rows):
        lr = live[i] if i < len(live) else []
        for j, v in enumerate(r):
            lv = lr[j] if j < len(lr) else ""
            if not same(v, lv):
                bad.append((A1(i + 1, j + 1), v, lv))
    return bad


def push_tab(ws, rows, fmts, freeze, ncols):
    with_retry(ws.clear)
    with_retry(ws.resize, rows=max(40, len(rows) + 5), cols=ncols)
    with_retry(ws.update, rows, "A1", value_input_option="RAW")
    with_retry(ws.batch_format, fmts)
    with_retry(ws.freeze, rows=freeze[0], cols=freeze[1])


def push_raw(ws, merged):
    rows = [RAW_COLS] + merged[RAW_COLS].values.tolist()
    # grow-only tab: overwrite in place (no clear) so a failed run can never leave it empty
    with_retry(ws.resize, rows=len(rows) + 10, cols=len(RAW_COLS) + 1)
    with_retry(ws.update, rows, "A1", value_input_option="RAW")
    with_retry(ws.batch_format, [{"range": "A1:H1", "format": {"textFormat": {"bold": True}}}])
    with_retry(ws.freeze, rows=1)
    return len(rows) - 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="*", help="new export CSV(s), oldest first")
    ap.add_argument("--base", choices=["sheet", "none"], default="sheet")
    ap.add_argument("--dry-run", action="store_true", help="compute + diff against live sheet, write nothing")
    args = ap.parse_args()
    if args.base == "none" and not args.csv:
        sys.exit("--base none needs at least one CSV")

    gc = gspread.service_account(filename=os.path.expanduser(KEY_PATH))
    sh = gc.open_by_key(SHEET_ID)

    print("Loading ...")
    base = load_base(sh) if args.base == "sheet" else pd.DataFrame(columns=RAW_COLS)
    merged = merge(base, [load_csv(p) for p in args.csv])
    r = prepare(merged)

    print("Computing ...")
    # Daily Summary: bucket by created_at (message arrival), whole team
    dm, om, d_date, o_date = window_masks_and_dates(r, "created_at")
    daily_day = compute_daily_block(r[dm], d_date)
    daily_obh = compute_daily_block(r[om], o_date)
    # Agent Summary: bucket by agent_assigned_at
    dm, om, d_date, o_date = window_masks_and_dates(r, "agent_assigned_at")
    ag_day = compute_agent_block(r[dm], d_date, exclude=EXCLUDE_FROM_DAY_AGENT_VIEW)
    ag_obh = compute_agent_block(r[om], o_date, exclude=None)

    daily_rows, daily_fm, daily_fz, daily_nc = build_daily(daily_day, daily_obh)
    agent_rows, agent_fm, agent_fz, agent_nc = build_agent(ag_day, ag_obh)

    print(f"  tickets {len(merged)} | Daily: {len(daily_day['dates'])} day-dates / {len(daily_obh['dates'])} OBH-dates"
          f" | Agent: Day {len(ag_day['agents'])} agents, OBH {len(ag_obh['agents'])} agents")

    if args.dry_run:
        for name, rows in [(TAB_DAILY, daily_rows), (TAB_AGENT, agent_rows)]:
            bad = diff_with_live(sh.worksheet(name), rows)
            print(f"  DRY-RUN diff vs live '{name}': {len(bad)} differing cells")
            for c, gen, live in bad[:5]:
                print(f"     {c}: would write {gen!r}, live has {live!r}")
        print("Dry run only - nothing written.")
        return

    print("Writing ...")
    push_tab(sh.worksheet(TAB_DAILY), daily_rows, daily_fm, daily_fz, daily_nc);   print(f"  {TAB_DAILY} done")
    push_tab(sh.worksheet(TAB_AGENT), agent_rows, agent_fm, agent_fz, agent_nc);   print(f"  {TAB_AGENT} done")
    n = push_raw(sh.worksheet(TAB_RAW), merged);                                    print(f"  {TAB_RAW} done ({n} rows)")
    print(f"Done. https://docs.google.com/spreadsheets/d/{SHEET_ID}")


if __name__ == "__main__":
    main()
