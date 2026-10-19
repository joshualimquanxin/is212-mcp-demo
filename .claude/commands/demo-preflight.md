---
description: Check Jira, Google Drive, GitHub and the local repo before the live demo
---
Run every check below and print one line per check in the form `PASS <check>: <detail>`
or `FAIL <check>: <detail>`. Do not fix anything. Do not skip a check because an
earlier one failed. Finish with a single line: `READY` or `NOT READY: <reasons>`.

1. Jira: `getJiraIssue` for LIB-3 (cloudId is in CLAUDE.md). PASS only if status is
   "To Do", the summary starts with "Cap late fees", and the description contains a
   docs.google.com link. Report the status and the link.
2. Google Drive: `read_file_content` on the file id taken from that link. PASS only if
   the document has a section 3 that states a dollar amount. Report the amount.
3. GitHub MCP: `get_me`. PASS if it returns a login. Then `list_pull_requests` for
   owner `joshualimquanxin`, repo `is212-mcp-demo`, state open. PASS only if no open
   PR has "LIB-3" in its title or branch name.
4. Local repo: run `git fetch origin`, `git status --porcelain`, `git branch --show-current`
   and `git status -sb`. PASS only if the tree is clean, the branch is `main`, main is
   not behind or ahead of origin/main, and `git branch --list "feature/LIB-3*"` is empty.
5. CI: `gh run list --branch main --limit 1`. PASS if the latest run on main succeeded.
6. Tests: `python -m pytest -q`. PASS if all tests pass. Report the count.
