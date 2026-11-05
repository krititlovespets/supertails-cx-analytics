# 11 · Transfer Rules

[← Home](Home.md)

"Transfer" means two different things in "Dashboard || Extra". This page keeps them apart. *Added 2026-10-27.*

| | Chat tabs (this wiki) | Call / lead-funnel tabs |
|---|---|---|
| Tabs | `Chat - Daily Summary`, `Chat - Agent Summary`, `Chat - Raw Dump` | Main Dashboard, Ticket Categories, Valid Leads Log, Vet Followup, Callback Adherence, Agent Productivity |
| Channel | `UCJ SC Chat Assistance` only | `Unified Customer Journey` + `UCJ Booking Campaigns` only (chat channel always filtered out) |
| Is there a transfer metric? | **No** | **Yes** — Transfer Done / Doctor Called / Transfer Total / Transfer % |
| Source of truth | this wiki | GitHub repo [krititlovespets/supertails-cx-analytics](https://github.com/krititlovespets/supertails-cx-analytics) — `wiki/definitions.md`, `wiki/HANDOFF.md` §6 |

## Chat tabs — what "transfer" means here

1. **Bot → agent transfer: not measurable, don't claim it.** The exports have no field for it (`cf_transferred`, `assignment_skill_name` are empty;
   the bot greets every ticket ~1 s after creation). Say "chats show a bot-style opening and a later human agent", never "moved from ch36 to ch7".
   See [5-Data-and-Exports](5-Data-and-Exports.md) and [7-Findings](7-Findings.md).
2. **Agent → agent reassignment: negative FRTs are excluded and disclosed.** On a reassigned ticket the first reply is the *first* agent's but
   `agent_assigned_at` is the *latest* assignment, so Day Starting FRT / Agent FRT go negative — those rows are dropped (not clipped to 0).
   Actual FRT keeps them. See [4-Metrics-and-Rules](4-Metrics-and-Rules.md).
3. **The hand-off is the bottleneck:** OBH Actual FRT median ~9 h vs Day Starting FRT ~11–14 s. See [7-Findings](7-Findings.md).

## Call / lead-funnel tabs — transfer metric (summary of the repo's rules)

Data: Nugget ticket export × Ameyo `CALL_Details` export, matched on phone (`norm_phone` = last 10 digits).

- **`TRANSFER_TARGETS`** = the 36 doctor emails ∪ language queues `{english, telugu, tamil, kannada, kanada, hindi}`.
  The doctor list is kept out of the public repo (`~/Documents/Supertails work/doctors_emails.txt` locally).
- **Transfer Done**: `Transfer To Agent/Phone` (lowercased) ∈ `TRANSFER_TARGETS` **and** `Customer Talk Time − User Talk Time ≥ 30s`.
  Any-time phone match — no timing constraint vs the ticket.
- **Doctor Called**: `User ID` ∈ doctors **and** `User Talk Time ≥ 30s` **and** call at/after the ticket's `created_at`.
  Checked after Transfer Done; never both for one ticket.
- **Transfer Total** = Transfer Done OR Doctor Called, **one per ticket** (not summed). Check: Done + Doctor Called = Total.
- **Transfer %** = Transfer Total ÷ Valid Leads. **Target 30%.** `Abs Transfer To Do = round(Valid Leads × 0.30) − Transfer Total`.
- **A fresh day reads low.** Because matching is any-time, a date's Transfer % keeps rising for 1–3 refreshes as later call data arrives.
  Expected — don't "fix" it.
- **Per-agent credit (Agent Productivity Table 6):** each ticket belongs to one agent — the transfer-credited agent if transferred,
  otherwise the last agent who called that phone.
- **Incentives** use a Transfer % ladder and a Transfer team roster — see `wiki/HANDOFF.md` §10 in the repo (amounts not copied here, same
  reason as [10-Related-Systems-and-Memory](10-Related-Systems-and-Memory.md)).

**Local copy of the repo:** `~/Claude/supertails-cx-analytics/`.

**Related call-tab rule (2026-10-27):** Main Dashboard "Agents Available" month columns = daily average of the day columns (Sept 7.6, Oct 6.7), not a sum.

**Excluded tickets (2026-11-05):** ticket IDs Kriti lists in `~/Documents/Supertails work/exclusions/*.txt` are removed from every call-tab denominator (first list: 390 tickets of Nov 4). Chat tabs are not affected. Details in the repo `wiki/definitions.md`.
