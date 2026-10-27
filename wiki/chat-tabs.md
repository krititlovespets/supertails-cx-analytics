# Chat Tabs — Rules (and why there is no chat "transfer")

The three `Chat - *` tabs in "Dashboard || Extra" (`Chat - Daily Summary`, `Chat - Agent Summary`,
`Chat - Raw Dump (Sep 1+)`) are built by a **separate script** from chat ticket CSV exports, channel
`UCJ SC Chat Assistance` only. Its full wiki lives on Kriti's Mac (`chat-dashboard-wiki/`, start at `Home.md`);
this page is the summary so the two wikis don't contradict each other. *Added 2026-10-27.*

## "Transfer" in the two halves of the workbook

| | Call / lead-funnel tabs (rest of this wiki) | Chat tabs |
|---|---|---|
| Channel | `Unified Customer Journey` + `UCJ Booking Campaigns` | `UCJ SC Chat Assistance` |
| Transfer metric | Transfer Done / Doctor Called / Transfer Total — see [definitions.md](definitions.md) | **none** |

- **Bot → agent transfer cannot be measured from the chat export.** `cf_transferred` and `assignment_skill_name` are empty, and
  `bot_frt_response_at` is ~1 s after creation on ~99.9% of tickets (the bot greets everything). `channel_id` is current-state only
  (36 = Super Companion bot, 7 = human-agent channel), so never say a ticket "moved from 36 to 7" — say "bot-style opening plus a later
  human agent".
- **Agent → agent reassignment:** on a reassigned ticket `agent_frt_response_at` is the *first* agent's reply but `agent_assigned_at`
  is the *latest* assignment, so assignment-based FRT goes negative. **Negatives are excluded and disclosed, not clipped to 0.**

## Core chat rules

- **Actual FRT** = `agent_frt_response_at − created_at` (customer's wait). **Day Starting FRT / Agent FRT** =
  `agent_frt_response_at − agent_assigned_at` (agent's speed). Both need result ≥ 0. **Resolution** = `resolved_at − agent_assigned_at`.
- **Day** = 09:00:00–20:45:00 inclusive; **OBH** = everything else, dated by the day the shift **started** (02:10 on Oct 5 → Oct 4).
- Daily Summary buckets by `created_at`; Agent Summary buckets by `agent_assigned_at`.
- Tickets with no `agent_name` are excluded everywhere.
- Month/Avg columns are **ticket-weighted** (pooled), not averages of daily columns. Blank = no tickets, never zero.
- Agent Summary Day blocks hide 4 agents by request (`EXCLUDE_FROM_DAY_AGENT_VIEW` in the script); OBH blocks and Daily Summary hide none.
- De-dupe on `ticket_id`, newest export wins. Update = dry-run → run → dry-run shows `0 differing cells`.
- **Headline finding:** OBH Actual FRT median ~9 h vs Day Starting FRT ~11–14 s — the delay is the hand-off, not agent speed.

Related: the Nugget-based **Chat Volume / Chat FRT** self-compute in [definitions.md](definitions.md) uses the same
`agent_frt_response_at − agent_assigned_at` formula and 9:00–20:45 window.
