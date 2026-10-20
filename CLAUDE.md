# is212-mcp-demo

Late-fee rules for a small library. One Python package, one test file, one
CI workflow.

## Layout

- `libfines/fines.py` - all fee logic (`DAILY_RATE`, `late_fee`)
- `tests/test_fines.py` - the pytest suite
- `sandbox/` - a separate, deliberately poisoned MCP server. It has its own
  `.mcp.json` and settings; never connect it to this session.

## Commands

- Run tests: `python -m pytest -q`

## Jira

- Site: https://joshualimquanxin-is212.atlassian.net
- cloudId: `706b1adc-deda-48ee-a216-5c0573bcfd97` (use it directly; no need to look it up)
- Project `LIB`, stories LIB-1 to LIB-4. Statuses: To Do, In Progress, In Review, Done.
- The story is the spec. If it links to a policy document on Google Docs, read that
  document with the Google Drive `read_file_content` tool (the file id is in the URL)
  before writing any code. The numbers live in the policy, not in the ticket.

## How to deliver a story (LIB-n)

Work in as few turns as possible: make the calls grouped in one step in parallel, in
a single turn. No plans, no questions.

The screen groups tool calls, so people follow the work through your text. Before
each step's tool calls, write one plain line of under 20 words saying what you are
doing and which MCP server you are using, based on what you have actually found (for
example `Reading LIB-3 from Jira through Atlassian's MCP server.`).

1. In parallel: `getJiraIssue` for the story, and `Read` both `libfines/fines.py` and
   `tests/test_fines.py`.
2. `read_file_content` on the document the story links to.
3. In parallel: edit `libfines/fines.py` and add exactly the tests the story asks for
   to `tests/test_fines.py`. Minimal change: no refactors, no new files. Then write one
   line naming the rule you implemented and the number it came from:
   `Rule: <what the fee rule now does>, from <section> of the policy.`
4. Run `python -m pytest -q`. It must pass before anything is written to Jira.
5. In parallel: add one comment to the story with `addOrEditJiraIssueComment`, body
   with `contentFormat: html`, body
   `<p><strong><u>Change ready for human review:</u></strong></p><p>Fee rule and tests updated locally (<count> passing), not yet merged. <Rule line></p>`, and move the story with
   `transitionJiraIssue` using transition name `In Review`.
6. Stop there. Do not create branches, commit or push. A human reviews the diff and
   opens the pull request; the agent never gets the merge button. End with this one
   line and nothing else (no summary, no next steps, no suggestions for the user):
   `<LIB-n> moved to In Review: <count> tests passing, comment posted on the ticket.`
   If a step could not finish, say instead, in one line, which step stopped and why.
