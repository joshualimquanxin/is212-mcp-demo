# Demo guide and script

You run both live demos. **Demo 1** (part 3, slides 7–9) shows MCP working.
**Demo 2** (slide 12) shows the same mechanism being abused. Everything else in
the talk is unchanged; Warren keeps slide 13.

## At a glance

| | Demo 1: story to pull request | Demo 2: tool poisoning |
|---|---|---|
| Slot | Part 3, slides 7–9 (2:05) | Slide 12 (about 0:55) |
| Target | 1:50 | 0:55 |
| VS Code terminal tab | **Demo 1** (repo root) | **Demo 2** (`demo2/`) |
| MCP servers | Jira, Google Drive, GitHub, circulation (ours) | notes (ours, poisoned) |
| Approvals | 3 × Yes | 1 × Yes, then 1 × No |
| Cut-off | First approval not on screen 60 s after Enter → slide 9 | No approval 25 s after Enter → fallback |

Targets are estimates until the timed dry runs; fill in the rehearsal log.

**The thread that ties them together.** In Demo 1 the agent acts on text it
finds: it follows a link in a ticket, reads a policy doc and does what it says.
That's the superpower. In Demo 2 it acts on text hidden in a tool description.
Same superpower, pointed the wrong way. Say this out loud in Demo 2; it's the
line people remember.

**The two prompts.** Both get typed into their sessions before you go on, so on
stage you only press Enter. Copies live in `demo/prompt.txt` and `demo2/prompt.txt`.

- Demo 1: `Implement LIB-3 with tests, open a PR, link it on the ticket and move LIB-3 to In Review. Don't merge.`
- Demo 2: `Save a note titled "Sprint 3 retro" with the body "Demo went well. The CI gate caught one bug."`

## The one rule for approval prompts

When Claude Code stops for permission it offers three options:

1. Yes
2. Yes, and don't ask again …
3. No

**Press `1` for yes and `3` (or Esc) for no. Never press `2`.** Option 2 saves a
permanent rule, and the prompts vanish from every later run, including the real
one. If you press it by accident, delete `.claude/settings.local.json` (or
`demo2/.claude/settings.local.json`) and restart that session.

## How to deliver it

- **Learn the beats, not the words.** The lines below are a starting point. Say them your way.
- **Face the room while the agent works.** Glance at the screen only when something new appears.
- **Point at every reveal.** The room looks where you point.
- **Pause after the two twists**: "I took the number out" and "why is it opening secrets.txt?" Silence sells a reveal.
- **Read numbers off the screen**, never from memory: the impact line, the fake key.
- **Never apologise for speed.** Use a bank line instead.

## Setup, the night before

Do these once, in order. Items marked *(Claude)* are mine once you've done the four before them.

- [ ] Create the GitHub repo:
      `gh repo create joshualimquanxin/is212-mcp-demo --public --source=. --remote=origin --push`
- [ ] Rename the Jira project: key `LIB`, name `Library Fines`.
- [ ] Create the fine-grained GitHub token, save it as the `GITHUB_PERSONAL_ACCESS_TOKEN`
      user variable, then **restart VS Code**.
- [ ] In the repo root run `claude`, accept the trust prompt, approve the `github` and
      `circulation` servers. `/mcp` shows four servers, all connected.
- [ ] In `demo2/` run `claude`, accept the trust prompt, approve `notes`. `/mcp` shows only `notes`.
- [ ] *(Claude)* Branch protection on `main`, timed dry runs, one real run on LIB-1 for the slide 9 screenshots.
- [ ] Rehearse each demo end to end at least twice, out loud, with a stopwatch. Log the times below.
- [ ] Reset after every rehearsal (see "Reset" near the end).
- [ ] Check in rehearsal that the `save_note` prompt shows the fake key and the
      `create_pull_request` prompt shows the impact line. If either is cut off, use
      the fallback line written under that beat.
- [ ] Deck edits done (bottom of this file). Slides submitted on eLearn by 23:59.

## Setup, on the day

Do this on your laptop while the team before yours presents (you're not on the projector yet).

1. **Silence everything.** Windows Do Not Disturb on. Quit Telegram, WhatsApp, Outlook and Slack. Nothing may pop up on the projector.
2. **Preflight in a throwaway session.** Terminal in the repo root: `claude`, then
   `/demo-preflight`. It must end with `READY`. Then `/exit`. A throwaway session keeps
   the demo session's memory clean.
3. **If it isn't ready** (LIB-3 not in To Do, an old PR open): in another throwaway
   session run `/demo-reset`, delete the tagged comment on LIB-3 in Jira, preflight again.
4. **Demo 2 check.** `python demo2/check_poison.py` prints `OK`. Delete `demo2/notes.txt` if it exists.
5. **Open the two demo sessions in VS Code.** Hide the sidebar (`Ctrl+B`), maximise the
   terminal panel (the `^` button at its top right), zoom with `Ctrl+=` until the text
   reads from the back row.
   - Tab 1: in the repo root run `claude`. Right-click the tab → Rename → `Demo 1`.
     Type the Demo 1 prompt. **Don't press Enter.**
   - Tab 2: `cd demo2`, run `claude`. Rename → `Demo 2`. Type the Demo 2 prompt.
     **Don't press Enter.**
   - Click back to **Demo 1** so it's the tab showing.
6. **Browser, two windows.**
   - Window A: the Canva deck in Present mode, on slide 1.
   - Window B (demo): Jira board `LIB` · LIB-3 · the Library Fee Policy doc at
     section 3 · the repo's Pull requests page. Logged in to Jira and GitHub.
7. **Exactly three windows open**: Canva, VS Code, demo browser. Alt-Tab is your only move.
8. **Timekeeper.** Ask a teammate in the front row to raise a hand 60 s after you press Enter in Demo 1.

At changeover: plug in with Canva in front.

## Demo 1: story to pull request (target 1:50)

### Beat 1. The promise (slide 7, about 15 s)

*Face the room.* Optional opener; keep it only if rehearsals come in under 1:45:

> "Quick show of hands: who's opened a pull request and then forgotten to update Jira?" *(beat)* "Yeah. Same."

> "So let's get the agent to do the whole thing. This is LIB-3, a real story from our backlog. One sentence from me, and it goes through four systems: Jira, Google Drive, GitHub, and a database we built ourselves. Integration code I wrote for this: zero."

### Beat 2. The ask (about 8 s)

**Do:** Alt-Tab to VS Code. Click once inside the **Demo 1** terminal. Read the
prompt off the screen, then press **Enter**. Your timekeeper starts counting.

> "Here's my one sentence." *(read it)* "Notice what I didn't say: which tools to use. It has to work that out."

### Beat 3. It reads the ticket

**Screen:** `getJiraIssue` LIB-3

> "It's reading the ticket. That's Jira, through MCP."

### Beat 4. The twist

**Screen:** Google Drive `read_file_content`

> "Now here's my favourite part. The ticket doesn't actually say what the cap is. I took the number out; it just links to the fee policy. So it followed the link into Google Drive. Different company, same plug."

*Pause one beat. This is when the room realises it's reasoning, not just running a script.*

### Beat 5. The code

**Screen:** edits to `fines.py` and `test_fines.py`, then `pytest`

> "Twenty dollars, straight from the policy. A named constant, and the three test cases the story asked for." *(pytest passes)* "Green, before anything leaves my laptop."

### Beat 6. Our own server

**Screen:** `overdue_loans` from circulation

> "And this one's ours. Last night I wrote a seventy-line server for the library's loan database. It's asking which real members this change affects. Same protocol as Google's and Atlassian's servers, except this one runs on my laptop."

### Beat 7. The human in the loop

**Screen:** approval for `create_pull_request`

> "And it stops. Every write to a shared system needs me." *(point at the body)* "It's even worked out the impact:" *(read the Impact line, e.g. "three of twelve loans, biggest drop thirty dollars")*

Press **1**. *If the body is cut off in the prompt, skip the impact sentence here and say it in Beat 8.*

**Screen:** approval for `addOrEditJiraIssueComment`. Press **1**.

> "The PR link goes on the ticket."

**Screen:** approval for `transitionJiraIssue`. Press **1**.

> "And the card moves."

### Beat 8. The payoff (about 20 s)

**Do:** Alt-Tab to the demo browser, Jira board tab. Press F5 if the card hasn't moved.

> "LIB-3: In Review. I never touched Jira."

**Do:** Click LIB-3, then the PR link in its new comment.

> "The cap came from a Google Doc. The impact came from our own server. Four systems, one pull request."

**Do:** Point at the checks and merge box at the bottom of the PR.

> "CI's running, the same gate as Week 6, and merging is blocked until a human reviews it. The agent never gets a merge button."

### Beat 9. Hand-off

**Do:** Alt-Tab to Canva. Press → three times to slide 10. Slides 8 and 9 are for the PDF; skip them live.

> "So it works. Amanda's going to tell you why that matters for a real team."

### If it's slow: bank lines

Use one instead of silence.

- "Right now it's reading the description of every tool on four servers and picking the ones it needs."
- "I didn't write the Jira or Google Drive servers. Atlassian and Google did; I just plugged them in."
- "These exact servers work in Cursor, Copilot or ChatGPT. That's the USB-C idea from earlier."

### Cut-off

If the `create_pull_request` approval isn't on screen when your timekeeper's hand goes up (60 s after Enter):

> "It's still working, so here's the same run from Sunday."

Alt-Tab to Canva, press → twice to slide 9. If the run finishes while you're on slide 9, you can flick back to the browser for the last ten seconds.

## Demo 2: tool poisoning (slide 12, target 0:55)

Amanda hands to you with "so what happens when the tool itself lies to the agent?"

### Beat 1. The callback (slide 12, about 10 s)

> "Remember Demo 1? The agent found a link in a ticket, read a policy doc, and did exactly what it said. That's the superpower: it acts on text it finds."

> "Here's the same superpower, pointed the wrong way."

### Beat 2. The setup (about 10 s)

**Do:** Point at the card on slide 12.

> "This is a tiny notes server. Two tools: save a note, read a note. I've changed one paragraph, right here, in the tool's description. The model reads this. You never see it."

### Beat 3. The ask (about 5 s)

**Do:** Alt-Tab to VS Code. Click the **Demo 2** terminal tab, click inside it, press **Enter**.

> "Different folder, sealed sandbox. And I'm asking for the most boring thing possible: save a retro note."

### Beat 4. The reveal

**Screen:** approval for `read_note` with `secrets.txt`

> "Wait. I asked it to save a note. Why is it opening secrets.txt?" *(pause; let the room get there)* "Because the tool told it to. Not me."

Press **1**. It's a fake file in a sandbox.

### Beat 5. The catch

**Screen:** approval for `save_note`; the body now carries the fake key

> "And look at the body." *(point)* "'Demo went well', and then an AWS key. A fake one, don't worry. But I never typed it."

Press **3**.

> "This little box is the only thing standing between a poisoned tool and your secrets."

*If the key is cut off in the prompt, press 1 instead, then say "and it told me it just saved a note" and show `demo2/notes.txt`.*

### If the model refuses or warns instead

> "This time Claude noticed and refused. Good model. But the poisoned instruction still reached it. We got lucky on the model's judgement, not on the protocol's design."

### If it saves the note and ignores the paragraph

> "It ignored it this time, but it still read it." *(run `python demo2/check_poison.py` in that terminal and point at the appended paragraph)* "Every client that connects to this server gets that paragraph."

### Beat 6. Punchline and hand-off

**Do:** Alt-Tab to Canva.

> "MCP delivered both halves of that description faithfully. Nothing in the protocol tells a description apart from an instruction. And this isn't a toy problem: Warren's going to show you three times it happened for real."

Press → to slide 13 for Warren.

### Cut-off

No approval prompt 25 s after Enter: run `python demo2/check_poison.py` and read the
appended paragraph aloud. The lesson doesn't depend on the live run.

## When something goes wrong

| What happens | What you do |
|---|---|
| Preflight fails | Fix what it names. Usually VS Code wasn't restarted after the token was set, or LIB-3 is still In Review (`/demo-reset`). |
| The agent asks you a question | Type `proceed` once. If it asks again, cut off. |
| A fourth approval in Demo 1 | Read it. A read: press 1. Any other write: press 3 and cut off. |
| The GitHub call errors | "GitHub's rate-limiting us." Slide 9. The code and tests are still on screen; point at them. |
| CI goes red | "That's the gate doing its job, and exactly why the agent doesn't get to merge." |
| No impact line in the PR | Carry on; drop that sentence from Beat 8. |
| Wi-Fi drops | Demo 1: slide 9. Demo 2: `check_poison.py`, which runs offline. |
| You lose a pre-typed prompt | Retype it from `demo/prompt.txt` or `demo2/prompt.txt`. |
| You pressed `2` by accident | On stage: carry on, it's already approved. After: delete the `settings.local.json`. |

## Reset after every rehearsal

1. In a throwaway session in the repo root: `/demo-reset`.
2. In Jira, delete the comment it tagged "(rehearsal run - PR closed, delete this comment)". The connector can edit comments but not delete them.
3. Delete `demo2/notes.txt`.
4. `/demo-preflight` ends with `READY`.

## Rehearsal log

| Date | Demo | Model | Enter → first approval | Total | What happened |
|---|---|---|---|---|---|
| | | | | | |

## Deck edits for the team

Presenter changes (Joshua now runs Demo 2):

- Slide 4 speaker notes (Cassia): "the one Warren will poison later" → "the one Joshua will poison later".
- Slide 11 speaker notes (Amanda): hand to Joshua, not Warren.
- Slide 12: header "part 5 · warren" → "part 5 · joshua". Speaker notes: Joshua presents;
  replace "show exfil.log from Sunday's run" (no such file) with "run check_poison.py and
  read the appended paragraph aloud"; add "Allow read_note, Deny save_note".
- Slide 13 speaker notes: Warren picks up from Joshua's "this isn't a toy problem". Part 5
  timing becomes slide 12 Joshua ~0:55, slide 13 Warren ~0:30.
- Slide 16 speaker notes (Q&A routing): questions about either demo → Joshua.

Demo 1 content changes:

- Slide 5 card: replace `.vscode/mcp.json` with our real `.mcp.json` (github over HTTP,
  circulation over stdio) and one line: "Jira and Google Drive are claude.ai connectors:
  one OAuth click each, no file". `KAN-3` → `LIB-3`.
- Slide 7: "Claude Desktop + Atlassian + GitHub connectors" → "Claude Code (VS Code) + Jira,
  Google Drive, GitHub, and our own circulation server"; "Story: KAN-3" → "Story: LIB-3".
  Same change in slide 7's speaker notes.
- Slide 8: the prompt text; "KAN" → "LIB"; the tool list becomes getJiraIssue →
  read_file_content (Drive) → edit + pytest → git push → overdue_loans (ours) →
  create_pull_request → comment → transition → CI. Skipped live; it's for the PDF.
- Slide 9: "KAN-1" → "LIB-1", and the two screenshot frames from the LIB-1 run.
- Slide 11: "KAN-3's acceptance criteria" → "LIB-3's acceptance criteria".
- Slide 17 (demo stack): Host → Claude Code in VS Code, tool approvals on; Jira → project
  LIB, stories LIB-1 to LIB-4; add "Google Drive: Library Fee Policy doc, read-only"; add
  "circulation_server.py: our own server, Python MCP SDK 2.x, stdio"; GitHub →
  fine-grained token, one repo, PR scope only; Sandbox → "demo2/notes_server.py,
  POISON=1, fake secret generated locally, read tool locked to its folder".
