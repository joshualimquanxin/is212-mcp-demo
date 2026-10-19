# is212-mcp-demo

Late-fee rules for a small library. This is the throwaway repo behind
Team 7's IS212 presentation *MCP: the missing plug* (20 Oct 2026).

The point of the repo is not the code. It is that an AI agent, connected
to Jira, Google Drive and GitHub through MCP servers, can take a user
story from the backlog to an open pull request with zero integration code
written by us.

## What is here

| Path | What it is |
|---|---|
| `libfines/fines.py` | All the fee logic: `DAILY_RATE` and `late_fee()` |
| `tests/test_fines.py` | The pytest suite |
| `.github/workflows/tests.yml` | CI gate: pytest runs on every pull request |
| `CLAUDE.md` | How the agent is told to work in this repo |
| `.claude/settings.json` | What the agent may do without asking, must ask for, and can never do |
| `demo/` | Run sheet, the demo prompt, reset and preflight helpers |

## Run the tests

```
pip install pytest
python -m pytest -q
```

## The backlog

Jira project `LIB` on
[joshualimquanxin-is212.atlassian.net](https://joshualimquanxin-is212.atlassian.net/jira/software/projects/LIB/boards/1).

| Story | Summary |
|---|---|
| LIB-1 | Add a 2-day grace period for books |
| LIB-2 | Support a new item type: laptop at $5.00 per day |
| LIB-3 | Cap late fees per the Library Fee Policy |
| LIB-4 | Itemised receipt for a member's late items |

LIB-3 is the live demo. Its cap amount is not in the ticket; it is in a
Google Doc the ticket links to, so the agent has to follow the link.
