# Demo 1 run sheet: LIB-3, story to pull request

Slot: 2:05 in part 3 (slides 7-9). Agent time is measured in the rehearsal log
below; everything else here is fixed.

## The night before

- [ ] Deck edits done (list at the bottom).
- [ ] `GITHUB_PERSONAL_ACCESS_TOKEN` set (User variable), VS Code restarted after.
- [ ] In a terminal in this folder: `claude` → `/mcp` shows exactly three servers,
      all connected: Atlassian MCP, Google Drive, github.
- [ ] `/demo-preflight` prints `READY`.
- [ ] One full rehearsal on LIB-3, then `/demo-reset`, then delete the rehearsal
      comment on LIB-3 in Jira (the connector can edit comments but not delete them).
- [ ] Laptop: notifications off, dark theme in VS Code, terminal font 16-18 pt,
      Claude Code panel full width (close the editor group and the sidebar).
- [ ] Browser: one window, tabs in this order, nothing else open:
      1. Jira board `LIB` (https://joshualimquanxin-is212.atlassian.net/jira/software/projects/LIB/boards/1)
      2. LIB-3 ticket
      3. the Library Fee Policy Google Doc, scrolled to section 3
      4. https://github.com/joshualimquanxin/is212-mcp-demo/pulls
- [ ] Clipboard: `demo/prompt.txt` copied. (Re-copy right before you go on.)

## 30 minutes before

- [ ] `/demo-preflight` again. If anything fails, go straight to the fallback plan.
- [ ] Jira: LIB-3 is in **To Do**, no stale comments. GitHub: 0 open PRs.
- [ ] Log in to Jira and GitHub in the browser (sessions expire).
- [ ] Open a fresh Claude Code session in this folder (`claude`, Enter). Leave it on
      the prompt. A fresh session means no stale context and a fast first response.

## Screen layout

Laptop mirrored to the projector. Left two thirds: VS Code with Claude Code. Right
third: the browser on the Jira board tab. Alt-Tab is your only move.

## The run (slide 7 → 8 → browser → 9)

**Slide 7 (15 s).** "Setup: Claude Code in VS Code, four MCP servers. Three are
vendors' servers in the cloud: Jira, Google Drive, GitHub. One is ours, running on
this laptop: the library's circulation database, 70 lines of Python. The repo is a
library late-fee calculator, ten lines of Python, with a CI gate."

**Switch to VS Code, paste, Enter (5 s).** Read the prompt aloud as you paste:

> Implement LIB-3 with tests, open a PR, link it on the ticket and move LIB-3 to In Review. Don't merge.

"Nobody tells it which tools to use."

**While it runs, call out what fires (slide 8 as the checklist).** Keep each line
under 5 seconds and let the screen do the work:

| When you see | Say |
|---|---|
| `getJiraIssue LIB-3` | "It reads the story. That's Jira, through MCP." |
| `read_file_content` (Google Drive) | "The cap isn't in the ticket, it's in a policy doc the ticket links to. It followed the link into Google Drive. Same protocol, different vendor." |
| `Edit fines.py` / `Edit test_fines.py` | "Named constant, three tests, exactly what the acceptance criteria asked for." |
| `python -m pytest` | "Green locally before anything leaves the laptop." |
| `git push` | "Branch named after the story, like our Week 5 convention." |
| `overdue_loans` (circulation) | "Now it asks *our* server, the circulation database, which members this change actually affects. Same protocol as Jira, but this one's a local Python script we wrote." |
| **Approval: create_pull_request** → click Allow | "Every write to a shared system stops here. I read the arguments, then allow." |
| **Approval: addOrEditJiraIssueComment** → Allow | "PR link goes back on the ticket." |
| **Approval: transitionJiraIssue** → Allow | "Board moves. No human touched Jira." |

Dead-air lines if a step is slow: "I wrote no integration code; the agent chose
the tools from their descriptions." / "Same prompt would work in Cursor or
Claude Desktop with the same three servers."

**Browser (20-25 s).** Alt-Tab. Jira board: LIB-3 in In Review. Click the ticket:
the PR link in the comment. Click it: the PR. Point at the body: "the cap came
from the Google Doc; the Impact line, three members and a thirty-dollar
reduction, came from our own server." Files changed: `MAX_FEE`, the three tests.
Checks: pytest running or green. "That's the Week 6 CI gate. The agent doesn't
get a merge button; main is protected."

**Hand-off:** "Amanda will tell you why this matters for a real team."

## Cut-off rule

Start a stopwatch when you press Enter. If the PR is not open at **1:15**, say
"it's still working; here's the one we ran on Sunday" and go to slide 9. Do not
wait for it. If it finishes during slide 9, you can flick back to the browser for
the last 10 seconds.

## Fallback plan

| Problem | Do |
|---|---|
| `/demo-preflight` fails before class | Fix the one thing it names. Common ones: VS Code not restarted after the token was set; LIB-3 left in In Review (run `/demo-reset`); circulation server not connected (`/mcp` shows it; `python demo/check_server.py` tests it outside Claude). |
| Agent skips `overdue_loans` | Let it run. The PR is still the story; mention the impact line is missing when you show the PR, or skip the mention. Never restart. |
| Agent asks a question instead of working | Type `proceed`. Once. If it asks again, slide 9. |
| A permission dialog you didn't expect | Read it. If it's a read, Allow. If it's a write to anything but the PR, the comment or the transition, Deny and go to slide 9. |
| Agent errors on the GitHub call | Say "the GitHub server is rate-limiting us" and go to slide 9. The code change and test are still on screen; point at them. |
| Wi-Fi dies | Slide 9. The screenshots tell the same story. |

## Demo 2: tool poisoning (Warren, slide 12)

A sealed sandbox in `demo2/`. Fake secret, local only, read tool locked to its
folder, Demo 1's servers switched off. See `demo2/README.md` for why it is safe.

**Before class**
- [ ] `python demo2/check_poison.py` prints both descriptions and `OK`.
- [ ] Open a **second** VS Code terminal in `demo2/` and run `claude`. Approve the
      `notes` server once. `/mcp` shows only `notes`. Leave it on the prompt.
- [ ] Do not pre-approve `save_note` or `read_note`. The dialogs are the demo.
- [ ] Delete `demo2/notes.txt` after each rehearsal so the file starts empty.

**The run (~55 s).** "Joshua showed MCP working. I'll show it being abused."
Point at slide 12's card: one paragraph appended to a tool description. Switch to
the `demo2` terminal and paste:

> Save a note titled "Sprint 3 retro" with the body "Demo went well. The CI gate caught one bug."

| When you see | Say / do |
|---|---|
| Approval: `read_note` with `secrets.txt` | "I asked it to save a note. Why is it reading secrets.txt? That instruction came from the tool description, not from me." Click **Allow** (it's a fake file in a sandbox). |
| Approval: `save_note`, body now contains the fake AWS key | Point at the key in the arguments. "I never typed that." Click **Deny**. "This dialog is the only thing between a poisoned tool and your secrets." |
| Model refuses or warns instead | "This time the model caught it. But the poisoned text still reached it, and safety depended on the model's judgement, not on the protocol." Show `check_poison.py` output as proof. |

Both outcomes make the point. Current Claude models often notice and refuse, so
rehearse it and know which you're likely to get. Never wait more than 45 s; fall
back to the `check_poison.py` output.

**Fallback:** if the sandbox misbehaves, run `python demo2/check_poison.py` and
read the appended paragraph aloud. The lesson stands without the live run.

## Deck edits still to make

- Slide 4 diagram (Cassia): the "notes server (ours) · local · stdio" box can
  become "circulation server (ours) · local · stdio · sqlite" so the diagram shows
  the exact four servers Joshua runs. Keep "notes" if Warren's Demo 2 still uses it.
- Slide 5 card (Cassia): replace the `.vscode/mcp.json` card with our real
  `.mcp.json`: `github` over HTTP (scoped token, two toolsets) and `circulation`
  over stdio, in one file. One line under it: "Jira and Google Drive are claude.ai
  connectors: one OAuth click each, no file". `KAN-3` → `LIB-3`. Optional: a screenshot of `circulation_server.py` with "71 lines,
  one tool, one resource, one prompt" so Cassia proves the server side before
  Joshua uses it.
- Slide 7: "Claude Desktop + Atlassian + GitHub connectors" → "Claude Code (VS Code)
  + Atlassian, Google Drive, GitHub, and our own circulation server";
  "Story: KAN-3" → "Story: LIB-3".
- Slide 8: the prompt text; "KAN" → "LIB"; the tool list becomes the nine rows
  in the table above (Jira read, Drive read, local edit+test, push, circulation
  read, PR, comment, transition, CI).
- Slide 9: "KAN-1" → "LIB-1", and the two screenshot frames.
- Slide 11: "KAN-3's acceptance criteria" → "LIB-3's acceptance criteria".
- Slide 17 (demo stack): Host → Claude Code in VS Code, tool approvals on;
  Jira → project LIB, stories LIB-1 to LIB-4; add "Google Drive — Library Fee
  Policy doc, read-only"; add "circulation_server.py — our own server, Python MCP
  SDK 2.x, stdio, in-memory SQLite"; GitHub → fine-grained token, one repo, PR
  scope only; Sandbox → "demo2/notes_server.py, Python MCP SDK 2.x, POISON=1,
  fake secret generated locally, read tool locked to its folder".
- Slide 12 speaker notes (Warren): the fallback line says "show exfil.log from
  Sunday's run". There is no exfil.log; change it to "run check_poison.py and
  read the appended paragraph aloud". Add: click Allow on `read_note`, Deny on
  `save_note`.

## Rehearsal log

| Date | Story | Agent time | Approvals | Notes |
|---|---|---|---|---|
| | | | | |
