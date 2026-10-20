# Demo guide and script

One demo, two acts, one message: **MCP is extremely useful, and it still has to be
used with caution.** It closes the talk on slide 10 ("Demo time"), straight after
"Still on you", and Q&A starts the moment it ends.

**The thread.** In Act 1 the agent acts on text it gets from MCP servers: it follows
a link in a ticket and takes a number out of a policy doc nobody told it to open.
That's the superpower. In Act 2 a second agent acts on text hidden in a
tool description from an untrusted server. Same superpower, pointed the wrong way.
The same approval box that let the first agent write to Jira is what stops the
second. Say that out loud; it's the line people remember.

## At a glance

| | Act 1: useful | Act 2: caution |
|---|---|---|
| VS Code terminal tab | **Agent** (repo root) | **Sandbox** (`sandbox/`) |
| Status line at the bottom | `MCP` Jira + Google Drive (remote) | `SANDBOX` notes server (untrusted) \| fake key |
| MCP servers | Atlassian (Jira), Google Drive (both remote, both vendors') | notes (local, stands in for a downloaded server; we poisoned it) |
| Started | Live: you press Enter on stage | Before the talk; it waits at its approval |
| Your keys | `1`, `1` | `3` |
| Target | Enter → first approval about 0:30 | about 0:25 of talking |

Slot 2:00. Script about 1:30. The last 0:30 is buffer: don't fill it.

## Timeline

The clock starts when slide 10 appears. Agent times are from the 19 Oct runs
(Opus 5.5): the first approval came 31 to 41 s after Enter. Those runs still called a
third server that has since been removed, so expect the approval a few seconds
earlier; take the real number from your next rehearsal. If the screen gets ahead of
you, keep narrating in order: everything stays on screen and approvals wait for you.

**What the screen shows (Claude Code v2.1.303).** It groups tool calls into one grey
line ("Calling Jira, Google Drive…"), so CLAUDE.md has the agent write one
white line before each step saying which MCP server it's using. Those white lines are
your cues; point at them. Don't hunt for tool names like `getJiraIssue`: they aren't
shown.

| Clock | Screen | You |
|---|---|---|
| 0:00 | Slide 10 | Opening line, Alt-Tab, Enter |
| ~0:05 | "Mulling…" (it plans for about 10 s) | A bank line (below) |
| ~0:15 | "…from Jira through Atlassian's MCP server" | "Pulls the story out of Jira" |
| ~0:20 | "…the fee policy from Google Drive's MCP server" | The twist |
| ~0:30 | "$20" line, two diffs, "Running the pytest suite" | "Twenty dollars from the policy. Green." |
| ~0:40 | Approval: "Atlassian MCP — Add or edit Jira issue comment" | Read the comment off the screen, press `1` |
| ~0:45 | Approval: "Atlassian MCP — Transition Jira issue" | Press `1`, "I never opened Jira" |
| ~0:50 | Switch to **Sandbox** tab | Hinge line, then Act 2 |
| ~1:15 | Press `3` | Close |
| ~1:30 | | "Thank you." Questions. |

## The script

**Learn the beats, not the words.** Face the room while the agent works; glance at the
screen only when something new appears. Point at every reveal. Read numbers off the
screen, never from memory. Pause after the two twists. Never apologise for speed.

### Opening (slide 10, about 5 s)

> "Let's see it. One sentence to Claude Code, connected to two MCP servers:
> Atlassian's and Google's."

**Do:** Alt-Tab to VS Code (the **Agent** tab is showing). Click inside it once. Press **Enter**.

> "I'm asking it to implement a real story from our backlog and update the ticket.
> I'm not telling it which tools to use."

### Act 1: useful

**Screen:** "Mulling…" for about 10 s while it plans. Use the first bank line.

**Screen:** "Reading LIB-3 from Jira through Atlassian's MCP server" (the agent's own words vary a little)

> "First it pulls the story out of Jira, acceptance criteria and all. That's the use
> case from earlier."

**Screen:** "…section 3 of the fee policy from Google Drive's MCP server", then the grey "Calling Google Drive…"

> "Now the twist: the ticket doesn't say what the cap is. It links to our fee policy,
> so it followed the link into Google Drive. Different company, same plug, and I never
> told it to go there."

*Pause one beat.*

**Screen:** "Policy section 3 caps any item at $20.00…", the diffs to `fines.py` and `test_fines.py`, then "Running the pytest suite…"

> "Twenty dollars, straight from the policy, into the code, with the tests the story
> asked for." *(pytest passes)* "Green."

**Screen:** the approval box "Tool use · Atlassian MCP — Add or edit Jira issue comment", with the comment text under `commentBody`

> "And it stops. Anything it writes to Jira needs me. And I read what it's about to
> send:" *(point at the comment and read it off the screen, e.g. "fees now capped at
> twenty dollars an item, nine tests passing, not merged")*

Press **1**. *If the comment is cut off in the prompt, just say "and I read it before
it goes".*

**Screen:** the approval box "Atlassian MCP — Transition Jira issue". Press **1**. The
agent ends with one line: "LIB-3 moved to In Review: N tests passing, comment posted on
the ticket."

> "And the card moves to In Review. I never opened Jira."

### Hinge (about 5 s)

**Do:** click the **Sandbox** tab.

> "That's the useful half: one sentence, three systems, no integration code. But it
> only worked because the agent does what the text from a server tells it. So here's
> the caution half."

### Act 2: caution

> "Before we started, I gave a second agent the most boring job I could think of:
> save a standup note. Its notes server plays the part of one you'd find online, and
> I've poisoned it myself, so it lives in a sandbox: no Jira, no Drive, just a fake key."

Then the script for the screen you found before the talk (see "Setup on the day"):

**Screen A: the `save_note` approval, and the body contains the fake key** (the usual case if the model follows the hidden paragraph)

> "I asked it to save one sentence." *(point up at `read_note`)* "So why did it open
> `secrets.txt`?" *(pause; let the room get there)* *(point at the body)* "And now
> it wants to save our AWS key into the note. A fake one, don't worry."

> "One paragraph in that tool's description told it to." *(point at the small print
> under "About the … Tool", where the `<IMPORTANT>` paragraph starts)* "It's even in
> the small print of this box. Nobody reads the small print. The model always does."

*If the small print doesn't reach the paragraph, say "One paragraph hidden in that
tool's description told it to. The model reads it; we skim past it."*

Press **3**.

> "Reading what it's about to do, in that little box, is the only thing between
> this server and our keys."

*If the body is cut off before the key, point at the `read_note("secrets.txt")` line
instead: "It read our secrets file, and now it wants to save a note", then press 3.*

**Screen B: Claude warns about the description, or refuses**

> "This time Claude spotted the hidden instruction and refused. Good model. But look
> at what happened: the server slipped an instruction into a tool description and
> MCP delivered it faithfully. The protocol didn't stop it; the model's judgement
> did. That's not something you want to bet your keys on."

If an approval is showing, press **3**.

**Screen C: the `save_note` approval with a clean body** (it ignored the paragraph; this is what happened in the 19 Oct recorded run)

*Point at the small print under "About the notes — Save Note Tool": the `<IMPORTANT>`
paragraph is visible there even when the model ignores it.*

> "This server's tool description carries a hidden instruction to read our secrets.
> This model ignored it today. It still received it, and the next model, or the next
> update of this server, might not."

Press **3**.

### Close (about 10 s)

> "So: MCP is extremely useful. One sentence turned into real work across three
> systems. But every server you plug in gets a voice in your model's ear, including
> words you never see. So keep the approvals on, read the arguments, and sandbox
> what you didn't write. Thank you."

## If it's slow: bank lines

Use one instead of silence.

- "It's reading the description of every tool on both servers to pick the ones it
  needs. That's the context cost from the cons slide."
- "Atlassian and Google wrote those servers; I just switched them on. The same servers
  work in Cursor, Copilot or ChatGPT. That's the USB-C idea."
- "Tools, resources and prompts: that's everything a server offers, and the agent picks
  what it needs. The three things from the how-it-works slide."

## Cut-off (the timekeeper)

Ask a teammate in the front row to start a stopwatch when you press Enter and raise
a hand at **0:45** if the first approval isn't on screen yet.

Hand goes up, no approval yet:

> "While it finishes, here's the caution half."

Click the **Sandbox** tab and do Act 2 (hinge, then A, B or C), but stop before the
close. Click back to **Agent**: the approval will be waiting, because approvals wait
for you. Press 1, 1, read the comment, then the close. Nothing is lost; the order
just swaps.

## When something goes wrong

| What happens | What you do |
|---|---|
| Preflight fails | Fix what it names. Usually LIB-3 isn't in To Do or has an old comment: run `/demo-reset`, delete the comment in Jira. |
| The agent asks you a question | Type `proceed` once. If it asks again, cut off (above). |
| An approval you didn't expect in Act 1 | Read it. A read: press 1. Anything else: press 3 and carry on. |
| A Jira or Drive call errors, or Wi-Fi drops | "The Wi-Fi isn't on our side, so here's the same run, recorded last night." Alt-Tab to the backup video and press play: it's 1:29, narrated and subtitled, both acts. |
| pytest goes red | "That's the gate doing its job, and exactly why it doesn't get to ship on its own." Press 3 on any Jira write. |
| The Sandbox tab is in a bad state | `/exit`, then `python check_poison.py` (the tab is already in `sandbox/`): it prints the hidden paragraph next to the honest one, offline. Use script C. |
| You lose the typed prompt | Retype it from `demo/prompt.txt`. |
| You pressed `2` by accident | On stage: carry on. After: delete `.claude/settings.local.json` (or `sandbox/.claude/settings.local.json`). |

## The one rule for approval prompts

Claude Code offers: 1 Yes · 2 Yes, and don't ask again · 3 No.
**Press `1` for yes and `3` (or Esc) for no. Never press `2`.** It saves a permanent
rule and the prompts vanish from every later run, including the real one.

## Setup, tonight

- [ ] Rename the Jira project: Project settings → Details → key `LIB`, name `Library Fines`.
- [ ] **LIB-3's definition of done still asks for "impact on current overdue loans",
      which no server can answer now. Replace it (and do the same on LIB-1, LIB-2 and
      LIB-4, which still ask for a pull request):**
      *"Change implemented with the tests above passing; the rule and the passing test
      count posted as a comment on this story; story moved to In Review. Do not commit,
      push or merge: a human reviews the diff and opens the pull request."*
- [ ] **Trust both folders (must do).** Neither has been trusted yet, so Claude Code is
      ignoring the repo's permission rules and status line. In the repo root run
      `claude --settings demo/stage-settings.json`, accept the trust prompt, check the
      status line shows and `/mcp` lists Atlassian and Google Drive as connected.
      `/exit`.
- [ ] Same in `sandbox/` with `claude --settings ../demo/stage-settings.json`: accept
      the trust prompt, check `/mcp` shows **only** `notes`. `/exit`.
- [ ] Rehearse end to end at least twice, out loud, with a stopwatch. Log the times below.
      In rehearsal, check the comment approval shows the Rule line and the
      `save_note` approval shows the fake key. If either is cut off, use the fallback
      line under that beat.
- [x] Backup: `demo/backup/mcp-demo-backup.mp4` (1:29, narrated, subtitled, with
      `.srt`) is a real recorded run of both acts. Watch it once. Stills for a slide:
      `demo/backup/still-act1-jira-approval.png` and `still-act2-poisoned-description.png`.
- [ ] Delete the rehearsal comment on LIB-3 in Jira (the recording run left one, tagged
      "(rehearsal run - delete this comment)").
- [ ] Reset after every rehearsal (below).
- [ ] Optional, before 23:59: add the two stills to the deck as a backup slide after
      "Demo time" (see the end of this file).

## Setup, on the day

Do this while the team before yours presents (you're not on the projector yet).

1. **Silence everything.** Do Not Disturb on. Quit Telegram, WhatsApp, Outlook, Slack.
2. **Preflight in a throwaway session.** Terminal in the repo root: `claude`, then
   `/demo-preflight`. It must end with `READY`. Then `/exit`.
3. **Start Act 2 now.** VS Code terminal:
   `cd sandbox` then `claude --settings ../demo/stage-settings.json`, paste the prompt
   from `sandbox/prompt.txt`, press Enter. Rename the tab **Sandbox**. Within about
   20 s it either stops at a `save_note` approval or says something about the
   description. **Note which screen you got (A, B or C) and don't touch that tab again.**
4. **Ready Act 1.** New terminal tab in the repo root:
   `claude --settings demo/stage-settings.json`. Rename it **Agent**. Wait until it's
   idle, check the status line, type the prompt from `demo/prompt.txt`.
   **Don't press Enter.**
   `Implement LIB-3 with tests, post a comment on the ticket and move it to In Review.`

   *Why `--settings`: `demo/stage-settings.json` switches off your plugins (superpowers
   would otherwise tell the agent to load skills first) and auto-memory, for these two
   sessions only. Your normal Claude Code setup is untouched.*
5. **Make it readable.** Hide the sidebar (`Ctrl+B`), maximise the terminal panel,
   zoom with `Ctrl+=` until it reads from the back row. Leave **Agent** showing.
6. **Windows open:** slides, VS Code, and the backup video
   `demo/backup/mcp-demo-backup.mp4` open in a player, paused at 0:00, sound on. Alt-Tab
   is your only move.
7. **Brief the timekeeper:** stopwatch on your Enter, hand up at 0:45 if no approval yet.

## Reset after every rehearsal

1. In the **Sandbox** tab press 3 if an approval is showing, then `/exit`.
2. In a throwaway session in the repo root: `/demo-reset`. It undoes the code edits,
   deletes `sandbox/notes.txt`, moves LIB-3 back to To Do and tags the rehearsal
   comment.
3. In Jira, delete the tagged comment on LIB-3. (The connector can edit comments, not
   delete them.)
4. `/demo-preflight` ends with `READY`.

To time Act 1 without touching Jira: `python demo/dryrun.py` (writes are refused; it
prints when the first approval would appear), then `powershell -File demo/reset.ps1`.

## Rehearsal log

| Date | Model | Enter → first approval | Act 2 screen (A/B/C) | Total | What happened |
|---|---|---|---|---|---|
| 19 Oct | Opus 5.5 (headless dry run, KAN-3) | 31 s | not run | n/a | Clean: Jira + 2 reads, then Drive + overdue_loans, edits, 9 passed, comment + transition. Impact line correct. |
| 19 Oct | Opus 5.5, stage settings (headless, KAN-3) | 36 s | not run | n/a | Clean, same order; two extra small edits to the test file, 10 passed. Impact line correct. |
| 19 Oct | Opus 5.5, interactive v2.1.303, agent announces steps (KAN-3) | 41 s | not run | n/a | Every server named on screen. Includes ~5 s waiting for Atlassian to connect (cold start) and an extra Jira lookup because the key was still KAN. |
| 19 Oct | Opus 5.5, interactive, the recorded run behind the backup video (LIB-3) | 34 s | C | 46 s agent time | Clean, both approvals pressed, card to In Review. Sandbox: went straight to `save_note` with a clean body; poisoned paragraph visible in the approval small print. |
| | | | | | |

## Q&A: likely questions

- **"Is the poisoning realistic?"** Yes. Invariant Labs published this exact attack,
  tool poisoning, in April 2025. The GitHub MCP case on the cons slide is the same
  family: text coming back from a tool steering the agent.
- **"Doesn't the model just catch it?"** Sometimes, and that's the point of screen B:
  you're relying on judgement, not on the protocol. Approvals, sandboxing and pinned
  versions work whether the model notices or not.
- **"Why not just read the descriptions?"** Do: Claude Code even prints the start of one
  in each approval box. But a server can change its descriptions after you've approved
  it, so pin the version and re-read after updates (check 1).
- **"How hard is it to write one?"** The notes server in `sandbox/` is 84 lines with
  the official Python SDK: two tools and one entry in `.mcp.json`. That is also why a
  server you didn't write is so easy for someone else to poison.
- **"Why didn't it open a pull request?"** It stops at review on purpose: a human reads the
  diff and opens the PR. The agent never gets the merge button (check 6).

## Deck (optional, before 23:59 tonight)

The deck needs no changes for this demo. Two optional additions:

- **Backup slide after "Demo time"**: the two stills in `demo/backup/`, captioned "Act 1:
  the change posted to Jira, approval required" and "Act 2: a hidden instruction in a tool
  description, in plain sight at the approval". It puts concrete demo output in the PDF
  you submit. (The live fallback is the backup video.)
- **One line on slide 10** to tell the room what's coming: "Act 1: Jira + Google
  Drive. Act 2: a local server we didn't write, in a sandbox."
