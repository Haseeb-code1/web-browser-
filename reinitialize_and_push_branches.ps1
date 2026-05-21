$ErrorActionPreference = 'Stop'

# Ensure GITHUB_TOKEN is set in environment
if (-not $env:GITHUB_TOKEN) {
    Write-Error "Environment variable GITHUB_TOKEN is not set. Set it before running the script."
    exit 1
}
$token = "$env:GITHUB_TOKEN"

# Path to project (current directory)
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $projectPath

# Remove existing .git if present to wipe history containing secrets
if (Test-Path .git) {
    Write-Host "Removing existing .git directory to eliminate secret history..."
    Remove-Item -Recurse -Force .git
}

# Initialize new repository
git init

git add .
# Initial commit
git commit -m "Initial commit of project files"

# Set remote with token authentication (HTTPS)
git remote add origin "https://$token@github.com/Haseeb-code1/web-browser-.git"
# Push initial commit and set upstream
git push -u origin master

# Ensure we are on master (or main)
git checkout -B main

git push -u origin main --force

# Define branches and comments
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
    # Create new branch, commit empty, and force push (overwrites if exists)
    git checkout -b $name
    git commit --allow-empty -m $msg
    git push -u origin $name --force
    git checkout main
}


Write-Host "All branches created and pushed successfully."
