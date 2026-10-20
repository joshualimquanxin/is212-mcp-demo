---
description: Put LIB-3 and the local repo back to the pre-demo state
disable-model-invocation: true
---
Reset the demo. Do all of it without asking questions and print one line per step.

1. Local repo and sandbox: run `powershell -ExecutionPolicy Bypass -File demo/reset.ps1`
   and show its output. It undoes the agent's edits to `libfines/` and `tests/` and
   deletes `sandbox/notes.txt`.
2. Jira: `getJiraIssue` LIB-3. If the status is not "To Do", move it there with
   `transitionJiraIssue` (transition name `To Do`).
3. Jira comments: list the comments on LIB-3 with `executeRead` operation
   `listJiraIssueComments`. For every comment whose body contains `Change ready for
   human review`, edit it
   with `addOrEditJiraIssueComment` so the body reads exactly
   `(rehearsal run - delete this comment)`. The connector cannot delete comments, so
   end with a reminder to delete them in the Jira UI if any were found.
4. Verify and report: LIB-3 status, number of comments on LIB-3, `git status -sb`.
