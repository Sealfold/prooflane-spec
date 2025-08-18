# prooflane-spec - Repository Health Check

Write-Host 'Checking prooflane-spec repository health...' -ForegroundColor Yellow

# Check git status
if (Test-Path '.git') {
    Write-Host '✅ Git repository detected' -ForegroundColor Green
} else {
    Write-Host '❌ Not a git repository' -ForegroundColor Red
}

# Check documentation
$docsPath = 'docs'
if (Test-Path $docsPath) {
    Write-Host '✅ Documentation directory exists' -ForegroundColor Green
} else {
    Write-Host '❌ Documentation directory missing' -ForegroundColor Red
}

Write-Host 'Health check complete for prooflane-spec' -ForegroundColor Cyan
