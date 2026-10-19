# Undo the agent's edits from a demo run and clear the sandbox's saved notes.
# Touches only libfines/, tests/ and sandbox/notes.txt. Safe to run as often as you like.
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')

git restore --staged --worktree -- libfines tests
git clean -fdq -- libfines tests
$notes = 'sandbox/notes.txt'
if (Test-Path $notes) {
    Remove-Item $notes
    Write-Host "Deleted $notes"
}
Write-Host "Local repo:"
git status -sb
