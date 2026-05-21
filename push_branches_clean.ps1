$ErrorActionPreference = 'Stop'

# Use the PAT from an environment variable for security
if (-not $env:GITHUB_TOKEN) {
    Write-Error "Environment variable GITHUB_TOKEN is not set. Please set it before running the script."
    exit 1
}
$token = $env:GITHUB_TOKEN

# Set remote URL with token authentication (HTTPS)
git remote set-url origin "https://$token@github.com/Haseeb-code1/web-browser-.git"

# Ensure we are on main and up‑to‑date
if (git rev-parse --verify main 2>$null) {
    git checkout main
} else {
    git checkout -b main
}

git fetch origin
git reset --hard origin/main

# Optional: make an initial empty commit if repo is empty
if ((git rev-parse --is-inside-work-tree) -and ((git rev-parse HEAD) -eq $null)) {
    git commit --allow-empty -m "Initial empty commit"
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

    # Skip if the remote branch already exists
    $remoteExists = git ls-remote --heads origin $branch
    if ($remoteExists) {
        Write-Host "Remote branch $branch already exists – skipping."
        continue
    }

    # Create and switch to new branch
    git checkout -b $branch

    # Create an empty commit with the comment as the message
    git commit --allow-empty -m $comment

    # Push the branch
    git push -u origin $branch

    # Return to main for next branch
    git checkout main
}
