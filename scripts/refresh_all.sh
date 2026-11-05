#!/bin/bash
# Full refresh of every call-side tab + chat tabs through LAST (a complete day).
# Usage (from a scratch dir holding nugget.csv + ameyo.csv from `merge_month_exports.py 2026-11`):
#   refresh_all.sh 2026-11-01 <latest_nugget_export.csv> "$HOME/Documents/Supertails work/sept_base"
# The base dir holds hist_nugget.csv / hist_ameyo.csv: all CLOSED months (append each month when it closes).
# VET_MONTHS: months whose vet rows still move (a closed month until its 15-day windows end).
# Stops at the first failure. Secondary writers ran as dry-runs when validated; this is the real write.
set -euo pipefail
LAST=$1; NUG=$2; SEP=$3
P="$(cd "$(dirname "$0")" && pwd)"
DAY=${LAST:8:2}
DATES=$(python3 -c "print(' '.join(f'${LAST:0:8}{d:02d}' for d in range(1,$((10#$DAY))+1)))")
q() { grep -v -i -E "warn|^talk" || true; }

python3 "$P/compute_main_dashboard.py" nugget.csv ameyo.csv $DATES > /dev/null
if [ -n "${BOOKING_JSON:-}" ]; then cp "$BOOKING_JSON" booking.json; echo "bookings from $BOOKING_JSON (Clinic Dashboard skipped)"; else   # days missing from it are left blank
python3 - "$LAST" "$P" <<'PY' 2>&1 | q
import sys, os, json, gspread
last, p = sys.argv[1:3]; sys.path.insert(0, p); import clinic
gc = gspread.service_account(filename=os.path.expanduser("~/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json"))
b = clinic.daily(clinic.open_sheet(gc), lambda x: x[:3] == ["TOTAL (UCJ only)", "UCJ", "Appts created"])
o = {d: n for d, n in b.items() if d[:7] == last[:7] and d <= last}
assert len(o) == int(last[-2:]), f"Clinic Dashboard: expected {last[-2:]} days, got {len(o)}"
json.dump(o, open("booking.json", "w")); print("bookings", sum(o.values()), "last day", o[last])
PY
fi
python3 "$P/write_main_dashboard.py" booking.json 2>&1 | q
python3 "$P/write_team_rows.py" ameyo.csv "$LAST" 2>&1 | q

{ cat "$SEP/hist_nugget.csv"; tail -n +2 nugget.csv; } > all_nugget.csv
{ cat "$SEP/hist_ameyo.csv"; tail -n +2 ameyo.csv; } > all_ameyo.csv
head -1 nugget.csv > empty.csv
python3 "$P/compute_vet_followup.py" all_nugget.csv empty.csv all_ameyo.csv "$LAST" > /dev/null
python3 "$P/write_vet_rows.py" "$LAST" ${VET_MONTHS:-${LAST:0:7}} 2>&1 | q

for s in write_valid_leads_log write_ticket_categories write_table6 write_booking_analysis; do
  python3 "$P/$s.py" nugget.csv ameyo.csv "$LAST" 2>&1 | q; sleep 5
done
python3 "$P/write_prediction_model.py" "${PRED_LAST:-$LAST}" 2>&1 | q   # PRED_LAST: last COMPLETE day, when LAST is partial
python3 "$P/write_callback_adherence.py" nugget.csv ameyo.csv 2>&1 | q
python3 "$P/write_vet_tabs.py" all_nugget.csv all_ameyo.csv "$LAST" 2>&1 | q

python3 - "$NUG" "$LAST" <<'PY'
import csv, sys, datetime
csv.field_size_limit(10**9)
nug, last = sys.argv[1:3]
cut = (datetime.date.fromisoformat(last) + datetime.timedelta(days=1)).isoformat()
r = csv.DictReader(open(nug, encoding="utf-8-sig"))
w = csv.DictWriter(open("chat_cut.csv", "w", newline=""), fieldnames=r.fieldnames); w.writeheader()
w.writerows(x for x in r if x["created_at"] < cut)
PY
cd "$P/../chat"
F="$OLDPWD/chat_cut.csv"
python3 update_chat_dashboard.py "$F" 2>&1 | grep -E "merged|done|Done|WARNING" || true
python3 update_chat_dashboard.py "$F" --dry-run 2>&1 | grep differing
echo ALL_DONE
