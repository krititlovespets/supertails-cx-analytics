#!/bin/bash
# Full refresh of every call-side tab + chat tabs through LAST (a complete day).
# Usage (from a scratch dir holding oct_nugget.csv + oct_ameyo.csv from merge_month_exports.py):
#   refresh_all.sh 2026-10-30 <latest_nugget_export.csv> <dir_with_sep_nugget.csv_and_sepoct_ameyo.csv>
# Stops at the first failure. Secondary writers ran as dry-runs when validated; this is the real write.
set -euo pipefail
LAST=$1; NUG=$2; SEP=$3
P="$(cd "$(dirname "$0")" && pwd)"
DAY=${LAST:8:2}
DATES=$(python3 -c "print(' '.join(f'${LAST:0:8}{d:02d}' for d in range(1,$((10#$DAY))+1)))")
q() { grep -v -i -E "warn|^talk" || true; }

python3 "$P/compute_main_dashboard.py" oct_nugget.csv oct_ameyo.csv $DATES > /dev/null
python3 - "$LAST" "$P" <<'PY' 2>&1 | q
import sys, json, gspread
last, p = sys.argv[1:3]; sys.path.insert(0, p); import clinic
gc = gspread.service_account(filename="/Users/kritituteja/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json")
b = clinic.daily(clinic.open_sheet(gc), lambda x: x[:3] == ["TOTAL (UCJ only)", "UCJ", "Appts created"])
o = {d: n for d, n in b.items() if d[:7] == last[:7] and d <= last}
assert len(o) == int(last[-2:]), f"Clinic Dashboard: expected {last[-2:]} days, got {len(o)}"
json.dump(o, open("booking.json", "w")); print("bookings", sum(o.values()), "last day", o[last])
PY
python3 "$P/write_main_dashboard.py" booking.json 2>&1 | q
python3 "$P/write_team_rows.py" oct_ameyo.csv "$LAST" 2>&1 | q

{ cat "$SEP/sep_nugget.csv"; tail -n +2 oct_nugget.csv; } > sepoct_nugget.csv
python3 - "$SEP/sepoct_ameyo.csv" <<'PY'
import csv, sys
from datetime import datetime
w = None
with open("sepoct_ameyo.csv", "w", newline="") as out:
    for f, keep in [(sys.argv[1], lambda t: t < datetime(2026, 10, 1)), ("oct_ameyo.csv", lambda t: True)]:
        r = csv.DictReader(open(f))
        if w is None:
            w = csv.DictWriter(out, fieldnames=r.fieldnames); w.writeheader()
        for row in r:
            if keep(datetime.strptime(row["Call Time"], "%d/%m/%Y %I:%M:%S %p")):
                w.writerow(row)
PY
head -1 oct_nugget.csv > empty.csv
python3 "$P/compute_vet_followup.py" sepoct_nugget.csv empty.csv sepoct_ameyo.csv "$LAST" > /dev/null 2>&1
python3 "$P/write_vet_rows.py" "$LAST" 2>&1 | q

for s in write_valid_leads_log write_ticket_categories write_table6 write_booking_analysis; do
  python3 "$P/$s.py" oct_nugget.csv oct_ameyo.csv "$LAST" 2>&1 | q; sleep 5
done
python3 "$P/write_prediction_model.py" "${PRED_LAST:-$LAST}" 2>&1 | q   # PRED_LAST: last COMPLETE day, when LAST is partial
python3 "$P/write_callback_adherence.py" oct_nugget.csv oct_ameyo.csv 2>&1 | q
python3 "$P/write_vet_tabs.py" sepoct_nugget.csv sepoct_ameyo.csv "$LAST" 2>&1 | q

python3 - "$NUG" "$LAST" <<'PY'
import csv, sys, datetime
csv.field_size_limit(10**9)
nug, last = sys.argv[1:3]
cut = (datetime.date.fromisoformat(last) + datetime.timedelta(days=1)).isoformat()
r = csv.DictReader(open(nug, encoding="utf-8-sig"))
w = csv.DictWriter(open("chat_cut.csv", "w", newline=""), fieldnames=r.fieldnames); w.writeheader()
w.writerows(x for x in r if x["created_at"] < cut)
PY
cd ~/Downloads/chat-dashboard-wiki
F="$OLDPWD/chat_cut.csv"
python3 update_chat_dashboard.py "$F" 2>&1 | grep -E "merged|done|Done|WARNING" || true
python3 update_chat_dashboard.py "$F" --dry-run 2>&1 | grep differing
echo ALL_DONE
