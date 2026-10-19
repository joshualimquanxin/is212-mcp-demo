---
description: Put LIB-3, GitHub and the local repo back to the pre-demo state
---
Reset the demo. Do all of it without asking questions and print one line per step.

1. GitHub and local repo: run `powershell -ExecutionPolicy Bypass -File demo/reset.ps1`
   and show its output. It closes any open PR whose branch starts with
   `feature/LIB-3`, deletes those branches, and returns the checkout to a clean `main`.
2. Jira: `getJiraIssue` LIB-3. If the status is not "To Do", move it there with
   `transitionJiraIssue` (transition name `To Do`).
3. Jira comments: list the comments on LIB-3 with `executeRead` operation
   `listJiraIssueComments`. For every comment whose body contains `pull/`, edit it with
   `addOrEditJiraIssueComment` so the body reads exactly
   `(rehearsal run - PR closed, delete this comment)`. The connector cannot delete
   comments, so end with a reminder to delete them in the Jira UI if any were found.
4. Verify and report: LIB-3 status, number of open PRs, `git status -sb`.
