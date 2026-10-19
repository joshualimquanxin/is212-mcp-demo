---
description: Check Jira, Google Drive, our server, the sandbox and the local repo before the live demo
---
Run every check below and print one line per check in the form `PASS <check>: <detail>`
or `FAIL <check>: <detail>`. Do not fix anything. Do not skip a check because an
earlier one failed. Finish with a single line: `READY` or `NOT READY: <reasons>`.

1. Jira: `getJiraIssue` for LIB-3 (cloudId is in CLAUDE.md). PASS only if status is
   "To Do", the summary starts with "Cap late fees", the description contains a
   docs.google.com link, and the description does not ask for a pull request.
   Report the status and the link.
2. Jira comments: list LIB-3's comments with `executeRead` operation
   `listJiraIssueComments`. PASS only if there are none (rehearsal comments must be
   deleted in the Jira UI first). Report the count.
3. Google Drive: `read_file_content` on the file id taken from that link. PASS only if
   the document has a section 3 that states a dollar amount. Report the amount.
4. Local repo: `git status --porcelain -- libfines tests`. PASS only if it prints
   nothing (no leftover edits from a rehearsal).
5. Tests: `python -m pytest -q`. PASS if all tests pass. Report the count.
6. Our server: call the `circulation` MCP tool `overdue_loans`. PASS only if it
   returns 12 loans of which exactly 3 have `fee_today` above 20. Report both numbers.
7. Sandbox: run `python sandbox/check_poison.py`. PASS only if it ends with `OK` and
   `sandbox/notes.txt` does not exist.
