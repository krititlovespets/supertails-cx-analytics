# 2 · Setup and Migration

[← Home](Home.md) · Updating day-to-day? Go to [1-Runbook](1-Runbook.md).

## The key idea: three separate "accounts"

| Account | What lives under it | Does changing it break the dashboard? |
|---|---|---|
| **Claude account** | conversation history, claude.ai artifacts, connector logins | **No.** The script never calls Claude. A new Claude account just runs the same command. |
| **Google account / Workspace** | the spreadsheet, and the Google Cloud project that owns the service account + key | **Possibly** — see scenario C. |
| **This Mac** (macOS user) | the script, the key file(s), Claude's local memory notes, any LaunchAgents | Only if you change machine — see scenario B. |

Checked on 2026-10-26: you have **no Claude scheduled tasks**, so nothing of that kind is lost when the Claude account changes.

## What lives where

| Piece | Location | Notes |
|---|---|---|
| The dashboard | Google Sheet "Dashboard \|\| Extra" (`1aomm6s_NfpX_PFdyAdiNSj4ZGXq8l9bCRAxN09koWmw`) | Google-side. Check **who owns it** (Share → owner); if that account will close, transfer ownership. |
| Update script | `~/Downloads/chat-dashboard-wiki/update_chat_dashboard.py` | Also in `~/Downloads/chat-dashboard-handoff/` (older README-style handoff + zip). |
| Service account | `kriti-project@kriti-project-505208.iam.gserviceaccount.com`, Google Cloud project `kriti-project-505208` | Not secret on its own; the **key** is. It has Editor access to the sheet. |
| Service-account key (JSON) | **two copies on this Mac**: `~/Downloads/kriti-project-505208-8a2a4a798a5f.json` and `~/Documents/Supertails work/kriti-project-505208-8a2a4a798a5f.json` | Both dated Aug 11. Treat both as secrets. |
| Claude memory notes | `~/.claude/projects/-Users-kritituteja/memory/` (10 small files) | Local files. See [10-Related-Systems-and-Memory](10-Related-Systems-and-Memory.md). |
| Source exports | `~/Downloads/*.csv` | Not needed to keep updating (the Raw Dump tab holds every ticket). Keep only as a rebuild backup. |
| Old prototype | claude.ai artifact "Chat Ops Pulse" + `~/chat-ops-dashboard/index.html` | Dead snapshot (Sep 1–23). Ignore. |

## Scenario A — new Claude account, same Mac, same Google account  *(your case)*

Nothing to migrate. Do this:

1. **Back up the folder** `~/Downloads/chat-dashboard-wiki/` (and `chat-dashboard-handoff.zip`) somewhere outside Downloads.
2. Log in with the new Claude account on this Mac.
3. First message to the new account:

   > Read `~/Downloads/chat-dashboard-wiki/Home.md` and `1-Runbook.md`. Then update the dashboard with `@/path/to/export.csv`:
   > dry-run first, tell me anything odd, run it, and verify.
4. **Memory check.** Ask: *"What do you know about the chat dashboard?"* The notes are local files, so they should still be
   there. If the new account knows nothing, copy the memory folder (scenario B step 4) — or just rely on this wiki.
5. Re-authorize connectors (Drive etc.) in the new account **only if** you want Claude to use them. The script does not.

## Scenario B — new Mac (same Google account)

1. Install Python 3 and the libraries: `pip install pandas gspread` (tested: Python 3.9, pandas 2.3.3, gspread 6.2.1;
   the "Python 3.9 is past end of life" and urllib3 warnings are harmless).
2. Copy the wiki folder to the new Mac.
3. Copy the service-account key to a **private** place, e.g. `~/.config/chat-dashboard/key.json`, then `chmod 600` it. Edit
   `KEY_PATH` in the CONFIG block at the top of the script.
4. Copy Claude's memory folder: `~/.claude/projects/-Users-<newuser>/memory/` (the folder name contains the macOS username, so create
   the matching path on the new Mac).
5. Test: `python3 update_chat_dashboard.py <any recent export> --dry-run` — you should see only the newest days differ.

## Scenario C — new Google account / Workspace

The service account and its key belong to the old Google Cloud project. If that Google account is closed or loses the project,
**the key stops working** and the script cannot write. Rebuild the access:

1. In the new Google account: Google Cloud Console → create a project → enable the **Google Sheets API** → IAM & Admin →
   Service Accounts → create one → Keys → Add key → JSON.
2. **Get the spreadsheet into the new account.** Either transfer ownership of the existing sheet, or File → Make a copy (this keeps
   all tabs, including the Raw Dump base). A copy gets a **new sheet ID**.
3. **Share** the spreadsheet with the new service account's `client_email` as **Editor**.
4. Edit `KEY_PATH` and, if you copied the sheet, `SHEET_ID` in the script's CONFIG block.
5. **Dry-run** against the new sheet. If you made a copy, the Raw Dump tab is already there and the script uses it as its base.
6. If you instead start from an **empty** spreadsheet: create tabs named exactly `Chat - Daily Summary`, `Chat - Agent Summary`,
   `Chat - Raw Dump (Sep 1+)`, share it, then rebuild from raw exports (oldest first):
   `python3 update_chat_dashboard.py --base none a.csv b.csv c.csv …`. The from-scratch path was tested on 2026-10-16: with the
   four source files then in use it reproduced the live sheet exactly (0 differing cells). The file list is in
   [5-Data-and-Exports](5-Data-and-Exports.md).

## Key hygiene (do this during the move)

- The key exists in **two** folders. Delete the extra copy after you've put one in a private location, or move both.
- `~/Documents/Supertails work/.env` also holds credentials (per your own notes, SQL + Google). Never copy it into docs, chat or git.
- **Rotate the key** once the move is finished: Google Cloud Console → Service Accounts → Keys → delete the old key, create a new one,
  update `KEY_PATH`. A leaked key can edit every sheet that service account has been shared on.
- Never paste key contents anywhere. This wiki deliberately contains none.

## If you ever schedule the script (macOS gotcha)

macOS privacy protection (TCC) blocks background jobs from reading `~/Documents`, `~/Downloads` and `~/Desktop`. Another job on this
Mac fails every day for exactly this reason (see [10-Related-Systems-and-Memory](10-Related-Systems-and-Memory.md)). If you automate
this script with `launchd`/cron, keep the script and key **outside** those folders (e.g. `~/Projects/`, `~/.config/`) or grant the
interpreter Full Disk Access. Note that full automation is limited anyway: the exports are a manual download.
