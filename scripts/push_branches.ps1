$ErrorActionPreference = 'Stop'

# GitHub authentication using environment variable GITHUB_TOKEN
$token = $env:GITHUB_TOKEN
# Set remote URL with token authentication
git remote set-url origin "https://$token@github.com/Haseeb-code1/web-browser-.git"

# Ensure we are on the main branch and up‑to‑date
if (git rev-parse --verify main 2>$null) {
    git checkout main
} else {
    git checkout -b main
}

git fetch origin
git reset --hard origin/main

# Initial commit if repository is empty
if ((git status --porcelain) -ne "") {
    git add .
    git commit -m "Initial commit of full project"
    git push -u origin main
}

# Define 20 branches with meaningful names and a short comment for each
$branches = @(
    @{ Name = 'feature-authentication'; Comment = 'Add user authentication flow' }
    @{ Name = 'feature-search'; Comment = 'Implement search functionality' }
    @{ Name = 'feature-bookmarks'; Comment = 'Add bookmarking ability' }
    @{ Name = 'feature-history'; Comment = 'Track browsing history' }
    @{ Name = 'feature-settings'; Comment = 'User settings UI' }
    @{ Name = 'bugfix-header-layout'; Comment = 'Fix header layout issues' }
    @{ Name = 'bugfix-tooltip'; Comment = 'Correct tooltip positioning' }
    @{ Name = 'improvement-performance'; Comment = 'Optimize page load performance' }
    @{ Name = 'improvement-accessibility'; Comment = 'Enhance accessibility compliance' }
    @{ Name = 'refactor-codebase'; Comment = 'Refactor modules for clarity' }
    @{ Name = 'docs-readme-update'; Comment = 'Update README with usage docs' }
    @{ Name = 'docs-api'; Comment = 'Add API documentation' }
    @{ Name = 'test-unit'; Comment = 'Add unit tests for core functions' }
    @{ Name = 'test-integration'; Comment = 'Add integration tests' }
    @{ Name = 'ci-cd-pipeline'; Comment = 'Setup CI/CD workflow' }
    @{ Name = 'security-sanitization'; Comment = 'Sanitize input to prevent XSS' }
    @{ Name = 'ui-theme-darkmode'; Comment = 'Introduce dark mode UI' }
    @{ Name = 'ui-animations'; Comment = 'Add smooth UI animations' }
    @{ Name = 'deployment-docker'; Comment = 'Dockerize the application' }
    @{ Name = 'deployment-k8s'; Comment = 'Add Kubernetes deployment files' }
)

foreach ($branchInfo in $branches) {
    $branch = $branchInfo.Name
    $comment = $branchInfo.Comment
    # Skip if remote branch already exists
    if (git ls-remote --heads origin $branch) {
        Write-Host "Remote branch $branch already exists, skipping."
        continue
    }
    Write-Host "Creating branch $branch"
    git checkout -b $branch
    $notePath = Join-Path -Path $PSScriptRoot -ChildPath 'branch_note.txt'
    Set-Content -Path $notePath -Value $comment -Encoding UTF8
    git add $notePath
    git commit -m $comment
    git push -u origin $branch
    Remove-Item $notePath -Force
    git checkout main
}
