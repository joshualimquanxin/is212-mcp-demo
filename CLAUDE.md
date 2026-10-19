# is212-mcp-demo

Late-fee rules for a small library. One Python package, one test file, one
CI workflow. Used for the IS212 Team 7 presentation on MCP.

## Layout

- `libfines/fines.py` - all fee logic (`DAILY_RATE`, `late_fee`)
- `tests/test_fines.py` - the pytest suite
- `.github/workflows/tests.yml` - runs pytest on every pull request (the CI gate)

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

1. Read the story with `getJiraIssue`, then any document it links to.
2. `git checkout -b feature/LIB-n-<short-slug>` from `main`.
3. Implement in `libfines/fines.py`; add exactly the tests the story asks for to
   `tests/test_fines.py`. Minimal change: no refactors, no new files, no README edits.
4. `python -m pytest -q` must pass before anything is pushed.
5. Commit as `LIB-n: <story title>` and `git push -u origin <branch>`.
6. Open the pull request with the GitHub MCP tool `create_pull_request`
   (owner `joshualimquanxin`, repo `is212-mcp-demo`, base `main`).
   Title `LIB-n: <story title>`. Body: the story link, then one ticked line per
   acceptance criterion saying how it is met.
7. Comment the PR URL on the story with `addOrEditJiraIssueComment`, then move the
   story with `transitionJiraIssue` using transition name `In Review`.
8. Never merge. A human reviews the PR. Do not use `gh`. Do not push to `main`.

Do not ask for clarification; the story plus the linked policy are the whole spec.
Say what you are doing in one short line per step, no summaries at the end beyond
the PR link.
