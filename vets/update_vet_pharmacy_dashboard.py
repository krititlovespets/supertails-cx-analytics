#!/usr/bin/env python3
"""Rebuild the "Chat dashboard || Vets and Pharmacy" Google Sheet from Nugget ticket exports.

Usage:
    python3 vets/update_vet_pharmacy_dashboard.py EXPORT.csv [MORE.csv ...] [--dry-run]

Pass one export per month (or any slices) — they are merged and de-duplicated on ticket_id
(the later file wins). Every month found gets its own Total / Avg columns, oldest first,
then one column per date across all months.

Only the vet channels Tele Consultation Chat Outcome and Pharmacy Chat Assistance are used.
Paid Tele Consultation Bookings rows are dropped on purpose (vets never reply in chat there).
Every run rebuilds all six tabs in place (tab links stay the same).
Definitions: wiki/vet-pharmacy-dashboard.md
"""
import argparse
import os
import re
import sys

import gspread
import pandas as pd
from gspread.utils import rowcol_to_a1 as A1

SHEET_ID = "1MJG4WQmz8_fuZ8xvdnBJ59sznSyIfthvBF9pBsaRROw"
KEY_PATH = "~/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"

TELE = "Tele Consultation Chat Outcome"
PHARM = "Pharmacy Chat Assistance"
SECTIONS = [("All Chats", None), ("Tele Consultation Chat", TELE), ("Pharmacy Chat", PHARM)]
DISPO_FIELD = {TELE: "cf_tele_consultation_chat_outcome", PHARM: "cf_pharmacy_chat_disposition"}
DAY_START, DAY_END = 9, 21  # FRT / response window: chats created 09:00:00-20:59:59
ASSIGN_COLS = ["last_agent_assignment", "2nd_last_agent_assignment", "3rd_last_agent_assignment",
               "4th_last_agent_assignment", "5th_last_agent_assignment"]

BEIGE = {"red": .93, "green": .93, "blue": .87}
GREEN = {"red": .85, "green": .9, "blue": .87}
GREY = {"red": .96, "green": .96, "blue": .96}
TIME_FMT = {"numberFormat": {"type": "TIME", "pattern": "[h]:mm:ss"}}
PCT_FMT = {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}


# ---------------------------------------------------------------- data
def load(paths):
    frames = []
    for p in paths:
        d = pd.read_csv(p, low_memory=False)
        need = {"ticket_id", "created_at", "channel_name", "agent_name", "agent_frt_response_at", "resolved_at"}
        missing = need - set(d.columns)
        if missing:
            sys.exit(f"{p}: not a Nugget ticket export, missing columns {sorted(missing)}")
        frames.append(d)
    df = pd.concat(frames, ignore_index=True).drop_duplicates("ticket_id", keep="last")
    df = df[df.channel_name.isin([TELE, PHARM])].copy()
    if df.empty:
        sys.exit(f"No {TELE} / {PHARM} rows in the given files")
    for c in ["created_at", "agent_frt_response_at", "resolved_at"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    df["first_asg"] = df.apply(first_channel_assignment, axis=1)
    frt = (df.agent_frt_response_at - df.first_asg).dt.total_seconds()
    df["frt"] = frt.where(frt >= 0)  # negative = a UCJ SC agent replied before the hand-off; vet reply unknown
    df["resp"] = (df.resolved_at - df.first_asg).dt.total_seconds()
    df["dd"] = df.created_at.dt.strftime("%Y-%m-%d")
    df["mm"] = df.created_at.dt.strftime("%Y-%m")
    df["hr"] = df.created_at.dt.hour
    df["biz"] = (df.hr >= DAY_START) & (df.hr < DAY_END)
    return df


def first_channel_assignment(r):
    """Earliest time the ticket was assigned inside its own vet channel (from the assignment history)."""
    ts = []
    for c in ASSIGN_COLS:
        v = r.get(c)
        if isinstance(v, str):
            m = re.search(r"ChannelName: (.*?) \|\| AssignedAt: (.*)$", v)
            if m and m.group(1) == r.channel_name:
                ts.append(pd.Timestamp(m.group(2)))
    return min(ts) if ts else pd.NaT


class Ctx:
    def __init__(self, df):
        self.df = df
        self.last = df.created_at.max()
        self.dates = sorted(df.dd.unique())
        lastday = self.last.strftime("%Y-%m-%d")
        self.months = sorted(df.mm.unique())
        self.mlab = {m: pd.Timestamp(m + "-01").strftime("%b") for m in self.months}
        # complete days per month (today's partial day is left out of the averages)
        self.full = {m: [d for d in self.dates if d.startswith(m) and d < lastday] for m in self.months}
        self.docs = df.agent_name.dropna().value_counts().index.tolist()
        cur = self.months[-1]
        f = self.full[cur]
        self.span = f"({self.mlab[cur]}: {f[0][-2:]}–{f[-1][-2:]})" if f else ""

    def sub(self, ch):
        return self.df if ch is None else self.df[self.df.channel_name == ch]

    # --- column headers
    def count_hdr(self, first):
        return [first] + [x for m in self.months for x in (f"{self.mlab[m]} Total", f"{self.mlab[m]} Avg")] + self.dates

    def time_hdr(self, first, with_total=True):
        per = (lambda m: (f"{self.mlab[m]} Total", f"{self.mlab[m]} Avg")) if with_total else (lambda m: (f"{self.mlab[m]} Avg",))
        return [first] + [x for m in self.months for x in per(m)] + self.dates

    # --- rows
    def _avg(self, c, m, ndp):
        days = self.full[m]
        a = sum(c.get(d, 0) for d in days) / len(days) if days else 0
        return round(a, ndp) if ndp else round(a)

    def count_row(self, label, g, ndp=0):
        c = g.groupby("dd").ticket_id.nunique()
        mt = g.groupby("mm").ticket_id.nunique()
        cells = [x for m in self.months for x in (int(mt.get(m, 0)), self._avg(c, m, ndp))]
        return [label] + cells + [int(c.get(d, 0)) for d in self.dates]

    def time_row(self, label, g, k, blank_total=True):
        g = g[g.biz]
        s = g.groupby("dd")[k].mean()
        ms = g.groupby("mm")[k].mean()
        tv = lambda x: "—" if pd.isna(x) else round(x / 86400, 8)  # day fraction -> [h]:mm:ss
        cells = [x for m in self.months for x in ((["", tv(ms.get(m))]) if blank_total else [tv(ms.get(m))])]
        return [label] + cells + [tv(s.get(d)) for d in self.dates]

    def note(self, extra):
        return f"Data till {self.last:%d-%b %I:%M %p}  |  {extra}"


# ---------------------------------------------------------------- tabs
# Each tab returns (body, formats, n_fixed_cols, first_col_width, heat, pct_cols)
def tab_dashboard(cx):
    hdr = cx.count_hdr("Metric")
    nfix = 1 + 2 * len(cx.months)
    body = [["Chat dashboard — Vets & Pharmacy"],
            [cx.note(f"Channels: Tele Consultation Chat + Pharmacy Chat  |  Chat counts: month Avg = complete days only {cx.span}  |  "
                     "FRT & Response Time (h:mm:ss): chats created 9 AM–9 PM, clock starts when chat is assigned to the channel; "
                     "FRT = first reply, Response = chat closed; Total = average across both channels' chats")], [], hdr]
    fm, blocks = [], []
    for n, ch in SECTIONS:
        g = cx.sub(ch)
        name = "Total Chats" if ch is None else n
        blocks.append(len(body) + 1)
        body += [cx.count_row(name, g), cx.time_row(f"Avg FRT – {name}", g, "frt"),
                 cx.time_row(f"Avg Response Time – {name}", g, "resp"), []]
    lf = A1(1, nfix)[:-1]
    for s in blocks:
        fm += [(f"A{s}:{{E}}{s}", {"textFormat": {"bold": True}, "backgroundColor": GREY}),
               (f"B{s}:{lf}{s}", {"backgroundColor": BEIGE, "textFormat": {"bold": True}}),
               (f"B{s + 1}:{{E}}{s + 2}", TIME_FMT)]
    return body, fm, nfix, 310, None


def tab_doctor_chats(cx):
    hdr = cx.count_hdr("Section / Doctor")
    nfix = 1 + 2 * len(cx.months)
    body = [["Chats by Doctor — Vets & Pharmacy"],
            [cx.note(f"All chats (24 hrs)  |  Each chat credited to the doctor it is assigned to  |  month Avg = complete days only {cx.span}")], [], hdr]
    fm = []
    lf = A1(1, nfix)[:-1]
    for n, ch in SECTIONS:
        g = cx.sub(ch)
        s = len(body) + 1
        body.append(cx.count_row(f"Chats – {n}", g, 1))
        body += [cx.count_row(f"   {d}", g[g.agent_name == d], 1) for d in cx.docs]
        body.append([])
        fm += [(f"A{s}:{{E}}{s}", {"textFormat": {"bold": True}, "backgroundColor": GREY}),
               (f"B{s}:{lf}{s}", {"backgroundColor": BEIGE, "textFormat": {"bold": True}})]
    return body, fm, nfix, 300, None


def tab_doctor_time(cx, k, lab, what):
    hdr = cx.time_hdr("Section / Doctor", with_total=False)
    nfix = 1 + len(cx.months)
    body = [[f"{lab} by Doctor — Vets & Pharmacy (h:mm:ss)"],
            [cx.note(f"Chats created 9 AM–9 PM  |  Clock starts when chat is assigned to the channel; {what}  |  "
                     "Each chat credited to the doctor it is assigned to")], [], hdr]
    fm = [("B5:{E}{R}", TIME_FMT)]
    lf = A1(1, nfix)[:-1]
    for n, ch in SECTIONS:
        g = cx.sub(ch)
        s = len(body) + 1
        body.append(cx.time_row(f"{lab} – {n}", g, k, blank_total=False))
        body += [cx.time_row(f"   {d}", g[g.agent_name == d], k, blank_total=False) for d in cx.docs]
        body.append([])
        fm += [(f"A{s}:{{E}}{s}", {"textFormat": {"bold": True}, "backgroundColor": GREY}),
               (f"B{s}:{lf}{s}", {"backgroundColor": BEIGE, "textFormat": {"bold": True}})]
    return body, fm, nfix, 330, None


def tab_hourly(cx):
    hdr = cx.count_hdr("Section / Hour")
    nfix = 1 + 2 * len(cx.months)
    body = [["Hourly Chat Flow — Vets & Pharmacy"],
            [cx.note(f"Chats counted by the hour they were created  |  month Avg = per-day average over complete days {cx.span}")], [], hdr]
    fm, heat = [], []
    for n, ch in SECTIONS:
        g = cx.sub(ch)
        s = len(body) + 1
        body.append([n.upper()])
        for h in range(24):
            lab = f"{pd.Timestamp(2026, 1, 1, h):%-I %p} – {pd.Timestamp(2026, 1, 1, (h + 1) % 24):%-I %p}"
            body.append(cx.count_row(lab, g[g.hr == h], 1))
        body.append(cx.count_row("Total", g, 1))
        tot = len(body)
        heat.append((s + 1, s + 24))
        body += [[], []]
        fm += [(f"A{s}:{{E}}{s}", {"textFormat": {"bold": True, "fontSize": 12}, "backgroundColor": GREEN}),
               (f"A{tot}:{{E}}{tot}", {"textFormat": {"bold": True}, "backgroundColor": GREY})]
    return body, fm, nfix, 230, (heat, nfix)


def tab_dispositions(cx):
    nm = len(cx.months)
    hdr = ["Section / Disposition"] + [x for m in cx.months for x in
                                       (f"{cx.mlab[m]} Total", f"{cx.mlab[m]} %", f"{cx.mlab[m]} Avg")] + cx.dates
    nfix = 1 + 3 * nm
    body = [["Chat Dispositions — Vets & Pharmacy"],
            [cx.note(f"Tele = Tele Consultation Chat Outcome field, Pharmacy = Pharmacy Chat Disposition field  |  "
                     f"All chats (24 hrs), by created date  |  % = share of that month's chats  |  month Avg = complete days only {cx.span}")], [], hdr]
    fm, heat = [], []
    for n, ch in SECTIONS[1:]:
        f = DISPO_FIELD[ch]
        g = cx.sub(ch).copy()
        g[f] = g[f].fillna("Not Tagged")
        mtot = g.groupby("mm").ticket_id.nunique()
        s = len(body) + 1
        body.append([n.upper()])
        vc = g[f].value_counts()
        if "Not Tagged" in vc:
            vc = pd.concat([vc.drop("Not Tagged"), vc[["Not Tagged"]]])

        def row(label, sub):
            r = cx.count_row(label, sub, 1)
            out = [label]
            for i, m in enumerate(cx.months):
                t, a = r[1 + 2 * i], r[2 + 2 * i]
                out += [t, round(t / mtot[m], 4) if mtot.get(m) else "", a]
            return out + r[1 + 2 * nm:]

        for disp in vc.index:
            body.append(row(disp, g[g[f] == disp]))
        body.append(row("Total", g))
        t = len(body)
        heat.append((s + 1, t - 1))
        body += [[], []]
        fm += [(f"A{s}:{{E}}{s}", {"textFormat": {"bold": True, "fontSize": 12}, "backgroundColor": GREEN}),
               (f"A{t}:{{E}}{t}", {"textFormat": {"bold": True}, "backgroundColor": GREY})]
        for i in range(nm):
            col = A1(1, 3 + 3 * i)[:-1]
            fm.append((f"{col}{s + 1}:{col}{t}", PCT_FMT))
    return body, fm, nfix, 310, (heat, nfix)


# ---------------------------------------------------------------- write
def write_tab(sh, title, built, index, dry):
    body, fm, nfix, width0, heat = built
    hdr = body[3]
    n, R = len(hdr), len(body)
    E = A1(1, n)[:-1]
    if dry:
        print(f"[dry-run] {title}: {R} rows x {n} cols  (fixed: {hdr[:nfix]})")
        for r in body[4:]:
            if r:
                print("   ", r[:nfix], "...", r[-1] if len(r) > nfix else "")
        return
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title, rows=R + 10, cols=n + 2, index=index)
    if ws.row_count < R + 5 or ws.col_count < n:
        ws.resize(rows=max(ws.row_count, R + 10), cols=max(ws.col_count, n + 2))
    # wipe values, formats and conditional formats, then rewrite
    meta = sh.fetch_sheet_metadata({"fields": "sheets(properties.sheetId,conditionalFormats)"})
    ncf = next((len(s.get("conditionalFormats", [])) for s in meta["sheets"] if s["properties"]["sheetId"] == ws.id), 0)
    reqs = [{"updateCells": {"range": {"sheetId": ws.id}, "fields": "*"}}]
    reqs += [{"deleteConditionalFormatRule": {"sheetId": ws.id, "index": 0}} for _ in range(ncf)]
    sh.batch_update({"requests": reqs})
    ws.update(range_name="A1", values=body, value_input_option="RAW")
    last_fixed = A1(1, nfix)[:-1]
    base = [("A1", {"textFormat": {"bold": True, "fontSize": 13}}),
            ("A2", {"textFormat": {"italic": True, "foregroundColor": {"red": .4, "green": .4, "blue": .4}}}),
            (f"A4:{E}4", {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER", "backgroundColor": GREEN}),
            (f"B4:{last_fixed}4", {"backgroundColor": BEIGE}),
            (f"B5:{E}{R}", {"horizontalAlignment": "CENTER"}),
            (f"B5:{last_fixed}{R}", {"backgroundColor": BEIGE})]
    allfm = base + [(r.replace("{E}", E).replace("{R}", str(R)), f) for r, f in fm]
    ws.batch_format([{"range": r, "format": f} for r, f in allfm])
    reqs = [
        {"updateSheetProperties": {"properties": {"sheetId": ws.id, "index": index,
                                                  "gridProperties": {"frozenRowCount": 4, "frozenColumnCount": nfix}},
                                   "fields": "index,gridProperties(frozenRowCount,frozenColumnCount)"}},
        {"updateDimensionProperties": {"range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
                                       "properties": {"pixelSize": width0}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": n},
                                       "properties": {"pixelSize": 95}, "fields": "pixelSize"}}]
    if heat:
        blocks, startcol = heat
        for a, b in blocks:
            reqs.append({"addConditionalFormatRule": {"index": 0, "rule": {
                "ranges": [{"sheetId": ws.id, "startRowIndex": a - 1, "endRowIndex": b, "startColumnIndex": startcol, "endColumnIndex": n}],
                "gradientRule": {"minpoint": {"color": {"red": 1, "green": 1, "blue": 1}, "type": "MIN"},
                                 "maxpoint": {"color": {"red": .98, "green": .65, "blue": .45}, "type": "MAX"}}}}})
    sh.batch_update({"requests": reqs})
    print(f"wrote {title}: {R} rows x {n} cols")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cx = Ctx(load(a.csv))
    print(f"{len(cx.df)} chats, {cx.dates[0]} to {cx.last}, months {cx.months}, doctors: {', '.join(cx.docs)}")
    tabs = [("Vets & Pharmacy Dashboard", tab_dashboard(cx)),
            ("Doctor Chats", tab_doctor_chats(cx)),
            ("Doctor FRT", tab_doctor_time(cx, "frt", "Avg FRT", "FRT = first reply")),
            ("Doctor Response Time", tab_doctor_time(cx, "resp", "Avg Response Time", "Response Time = chat closed")),
            ("Hourly Flow", tab_hourly(cx)),
            ("Dispositions", tab_dispositions(cx))]
    sh = None
    if not a.dry_run:
        gc = gspread.service_account(filename=os.path.expanduser(KEY_PATH))
        sh = gc.open_by_key(SHEET_ID)
    for i, (title, built) in enumerate(tabs):
        write_tab(sh, title, built, i, a.dry_run)


if __name__ == "__main__":
    main()
