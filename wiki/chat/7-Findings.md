# 7 · Findings

[← Home](Home.md)

What the data says, with the numbers behind it. The live sheet is always newer than this page — the snapshot below is
**as of the 2026-10-25 21:52 export (5,894 tickets)**.

## Snapshot from the sheet (Chat - Daily Summary)

**Day — chats created 9:00 AM–8:45 PM**

| | Sep | Oct (to Oct 25) |
|---|---|---|
| Tickets | 3,376 | 1,401 |
| Actual FRT — avg / median | 31m 4s / 2m 5s | 23m 6s / 3m 15s |
| Day Starting FRT — avg / median | 33s / 14s | 29s / 14s |
| Resolution — avg / median | 5m 40s / 4m | 6m 31s / 4m 44s |

**OBH — chats created 8:45 PM–9:00 AM**

| | Sep | Oct (to Oct 25) |
|---|---|---|
| Tickets | 804 | 261 |
| Actual FRT — avg / median | 6h 55m 17s / **8h 58m 40s** | 6h 34m 14s / **9h 8m 11s** |
| Day Starting FRT — avg / median | 41s / **13s** | 19s / **11s** |
| Resolution — avg / median | 8m 15s / 4m 12s | 6m 35s / 4m 58s |

(`Aug` OBH = 15 tickets, the tail of the Aug 31 shift. Oct is partial — Oct 18 morning and Oct 25 evening are incomplete.)

## 1. The hand-off is the problem, not agent speed

OBH Actual FRT has a median of about **9 hours**; OBH Day Starting FRT has a median of about **11–14 seconds**. Messages sent overnight sit unassigned until the day
shift starts; once an agent is given a chat they reply almost immediately. Concrete cases: ticket `269181` was created 00:29:54 and first answered 09:01:56 (8 h 32 m), yet was
assigned only at 08:59:53 — so its assignment-based FRT was **123 seconds**. In the Sep 1–25 dataset (3,598 tickets), 55 tickets were created between 12 AM and 2 AM — nearly all waited 8–9 hours — and 527 tickets overall took
≥ 4 hours from creation to first reply.

*Why the OBH median can exceed the mean:* a message sent just after 8:45 PM waits the whole night (~12 h), one sent at 8:55 AM waits minutes. The wait depends on **when in the
night** the message arrived, so it is structurally bimodal rather than outlier-driven.

## 2. Time from created to assigned (the queue)

In the first dataset (3,352 tickets): **mean ~150 min, median ~3.2 min**, minimum 4 s, maximum ~99.9 h. **701 tickets (21%) waited more than 2 hours** to be assigned
— mostly off-hours creations. 1,070 were assigned within a minute. The median is the honest "typical"; the mean is dominated by overnight.

## 3. Known spikes (explained)

| Date | What | Why |
|---|---|---|
| **Sep 3** | 13 tickets entered the channel at ~12:00–12:05 and weren't assigned/answered until ~15:28–15:34 (~3.5 h) | a real queue hold, visible under the channel-entry measure. These tickets also show `ChannelID 36` (the bot channel) in their assignment history |
| **Sep 10** (resolution) | day average 22 min instead of the usual 4–9 | one ticket (`555280`, Shazali Sanober) assigned 09:04 Sep 10, resolved 14:59 Sep 11 — **29 h 55 m** |
| **Sep 11** (FRT) | team day average 170 s vs 17–50 s on other days | one agent (Dhanush S) handled 63 tickets at ~224 s average; he is now hidden from the Day agent view |
| **Oct 18** | very low ticket count | very likely an incomplete export — see [Home](Home.md) open item 1 |

Always read the **median** next to an average. These are all single-event distortions.

## 4. Agent speed (first dataset, assigned → first reply, day shift)

Fastest to slowest by average: Salman Pasha 11.7 s · Daksha K 15.2 s · Farhan 16.6 s · Ganashree D 34.3 s · Shazali Sanober 42.6 s · Akshaya 97.5 s · Dhanush S 184.3 s
(team 35.0 s avg, 15 s median). Resolution (assigned → resolved): Farhan 61 s · Ganashree D 163 s · Salman Pasha 292 s · Daksha K 392 s · Akshaya 462 s · Dhanush S 531 s · Shazali Sanober 768 s
(team 379 s avg, 236 s median). These are a **historical snapshot**; the current per-agent numbers are on the Agent Summary tab.

## 5. Chat arrival pace (ad-hoc analysis, not in the sheet)

Average gap between one chat being assigned and the next (agent-assigned timestamps, sorted):

| Scope | Average | Median | Tickets |
|---|---|---|---|
| Whole series to Oct 6 | 643.8 s (10.7 min) | 177 s (3.0 min) | 4,831 |
| Business hours only (9–8:45) | 762.7 s (12.7 min) | 202.5 s (3.4 min) | — |
| Business hours, **Oct 6 only** | 723.5 s (12.1 min) | 497 s (8.3 min) | 57 |

Typical pace ≈ one new chat every ~3 minutes; the mean is pulled up by overnight lulls (longest 11.95 h). Oct 6 was a quieter day (median gap 8.3 min vs 3.4).

## 6. What the data cannot tell you

- **Whether a chat was moved from the bot to a human.** There is no "transferred by bot" flag. `bot_frt_response_at` is filled on ~99.9% of tickets and is ~1 s after creation
  (the bot greets everything). `cf_transferred` and `assignment_skill_name` are empty. Your own earlier notes make the same point: `channel_id` is a *current-state* field and a channel
  "move" cannot be proven from it. Describe this as "chats show a bot-style opening and a later human agent" — **not** as a proven channel transition.
- **Chats that were never assigned.** Tickets with no agent are excluded everywhere (38 of 5,449 at Oct 15), so a chat nobody picked up is invisible in these numbers.
- **Anything about the last few hours of an export**, which is why the latest day is often partial.

## Reading rules of thumb

1. Median beside average, always.
2. Judge overnight service by **Actual FRT**, judge agents by **Day Starting FRT / Agent FRT**. Never compare the two directly.
3. A partial day (first or last) has low counts and unstable averages — wait for the next export.
4. `Oct Avg` is a running figure until the month closes.
