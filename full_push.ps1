$ErrorActionPreference = 'Stop'

if (-not $env:GITHUB_TOKEN) { Write-Error "GITHUB_TOKEN env var not set"; exit 1 }
$token = $env:GITHUB_TOKEN

# Ensure we are in the project directory
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $projectPath

# Remove any existing Git history to avoid leaking the token
if (Test-Path .git) {
    Write-Host "Removing existing .git directory to start clean..."
    Remove-Item -Recurse -Force .git
}

# Initialise a fresh repository
git init

git add .
# Initial commit (empty if repo already has content)
if ((git status --porcelain) -ne "") {
    git commit -m "Initial commit of full project"
}

# Add remote with token authentication
git remote add origin "https://github.com/Haseeb-code1/web-browser-.git"

# Push the initial commit to a new "main" branch
git checkout -B main
git push https://$token@github.com/Haseeb-code1/web-browser-.git main --force

# Define 20 branches with meaningful names and short comments
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

foreach ($b in $branches) {
    $name = $b.Name
    $msg = $b.Comment
    git checkout -b $name
    git commit --allow-empty -m $msg
    git push https://$token@github.com/Haseeb-code1/web-browser-.git $name --force
    git checkout main
}

Write-Host "All branches have been created and pushed successfully."
