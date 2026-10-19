# Close LIB-3 pull requests, delete their branches, and return the checkout to a clean main.
# Safe to run as often as you like. Needs: gh (logged in), git.
$ErrorActionPreference = 'Stop'
$repo = 'joshualimquanxin/is212-mcp-demo'
Set-Location (Join-Path $PSScriptRoot '..')

$open = gh pr list --repo $repo --state open --json number,headRefName,title | ConvertFrom-Json
foreach ($pr in $open) {
    if ($pr.headRefName -like 'feature/LIB-3*') {
        Write-Host "Closing PR #$($pr.number) ($($pr.headRefName))"
        gh pr close $pr.number --repo $repo --delete-branch
    }
}

git checkout -q main
git fetch -q --prune origin
git reset -q --hard origin/main
git branch --list 'feature/LIB-3*' | ForEach-Object {
    $b = $_.Trim().TrimStart('* ')
    if ($b) { git branch -D $b }
}
git clean -fdq
Write-Host "Local repo:"
git status -sb
$still = gh pr list --repo $repo --state open --json number | ConvertFrom-Json
Write-Host "Open PRs remaining: $($still.Count)"
