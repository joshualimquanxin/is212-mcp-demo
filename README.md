# is212-mcp-demo

Late-fee rules for a small library. This is the throwaway repo behind
Team 7's IS212 presentation on MCP, the Model Context Protocol (20 Oct 2026).

The point of the repo is not the code. It is one live demo with two halves:

1. **Useful.** An AI agent connected to Jira, Google Drive and our own circulation
   database through MCP servers takes a user story from the backlog, implements it
   with tests, works out which members it affects and updates the ticket, with no
   integration code written by us. Two of the servers are vendors'; the third is
   72 lines of Python in this repo.
2. **Caution.** A second agent, in a sandbox, uses a notes server standing in for one
   downloaded from the internet, which we poisoned ourselves. One hidden paragraph in
   a tool description is enough to make it reach for a (fake) secret. The approval
   prompt is what catches it.

## What is here

| Path | What it is |
|---|---|
| `libfines/fines.py` | All the fee logic: `DAILY_RATE` and `late_fee()` |
| `tests/test_fines.py` | The pytest suite |
| `.github/workflows/tests.yml` | CI gate: pytest runs on every pull request |
| `circulation_server.py` | Our own MCP server: the library's circulation database (one tool, one resource, one prompt) |
| `.mcp.json` | How Claude Code starts our server (stdio). Jira and Google Drive are claude.ai connectors: one click each, no file |
| `CLAUDE.md` | How the agent is told to work in this repo |
| `.claude/settings.json` | What the agent may do without asking, must ask for, and can never do |
| `sandbox/` | The poisoned notes server, with its own MCP config and settings (see `sandbox/README.md`) |
| `demo/` | Run sheet, the demo prompt, stage settings (plugins and auto-memory off for the demo sessions), reset and dry-run helpers |
| `demo/video/` | Records a real run in a hidden terminal and builds the narrated, subtitled backup video into `demo/backup/` (gitignored) |

## Run the servers by hand

```
pip install mcp
python demo/check_server.py        # starts circulation over stdio, lists tools, calls one
python sandbox/check_poison.py     # shows the notes server's tool description, clean and poisoned
```

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
