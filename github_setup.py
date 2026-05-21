#!/usr/bin/env python3
"""github_setup.py
Automates creation of a GitHub repository, initializes a local git repo, makes an initial commit,
creates an optional tag, and pushes to GitHub.

Usage:
    python github_setup.py --username <GitHubUsername> --repo <RepoName> --path <ProjectPath>

Requirements:
    - Git installed and in PATH
    - GitHub CLI (gh) installed and authenticated (`gh auth login`)
    - Python 3.8+
"""

import argparse
import subprocess
import sys
from pathlib import Path

def run(cmd, cwd=None):
    """Run a shell command, raise on error, return stdout stripped."""
    result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}\nstdout: {result.stdout}\nstderr: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def create_github_repo(username, repo, description, topics, visibility="public"):
    """Create a GitHub repository via gh CLI.
    Returns the HTTPS URL of the repo.
    """
    # Build the gh command
    topic_str = " ".join([f"--topic {t}" for t in topics])
    cmd = (
        f"gh repo create {username}/{repo} --{visibility} "
        f"--description \"{description}\" {topic_str} --source . --remote=origin"
    )
    run(cmd)
    # Get the repo URL
    url = run(f"gh repo view {username}/{repo} --json url -q .url")
    return url

def init_local_repo(path: Path):
    if not (path / ".git").exists():
        print("Initializing local git repository...")
        run("git init", cwd=path)
        run("git add .", cwd=path)
        run('git commit -m "chore: initial commit"', cwd=path)
    else:
        print("Git repository already initialized.")

def add_remote_and_push(path: Path, remote_url: str, default_branch="main"):
    # Set remote origin
    run(f"git remote add origin {remote_url}", cwd=path)
    # Rename current branch to default_branch if needed
    current_branch = run("git rev-parse --abbrev-ref HEAD", cwd=path)
    if current_branch != default_branch:
        run(f"git branch -M {default_branch}", cwd=path)
    # Push all branches and tags
    run("git push -u origin --all", cwd=path)
    run("git push origin --tags", cwd=path)

def create_tag(path: Path, tag_name="v0.1.0", message="Initial release"):
    run(f"git tag -a {tag_name} -m \"{message}\"", cwd=path)

def main():
    parser = argparse.ArgumentParser(description="Setup GitHub repo and push local project.")
    parser.add_argument("--username", required=True, help="GitHub username or organization")
    parser.add_argument("--repo", required=True, help="Repository name to create")
    parser.add_argument("--path", required=True, help="Path to the local project directory")
    parser.add_argument("--description", default="Automated repository", help="Repository description")
    parser.add_argument("--topics", nargs="*", default=["python", "pyqt6", "browser", "ai"], help="Space separated list of topics")
    parser.add_argument("--visibility", choices=["public", "private"], default="public", help="Repository visibility")
    parser.add_argument("--tag", default=None, help="Optional tag name to create (e.g., v0.1.0)")
    args = parser.parse_args()

    project_path = Path(args.path).resolve()
    if not project_path.is_dir():
        print(f"Error: Path {project_path} does not exist or is not a directory.")
        sys.exit(1)

    # Step 1: Create GitHub repository (if not exists)
    try:
        repo_url = create_github_repo(
            username=args.username,
            repo=args.repo,
            description=args.description,
            topics=args.topics,
            visibility=args.visibility,
        )
        print(f"Created GitHub repository: {repo_url}")
    except SystemExit:
        # Assume repository already exists; fetch URL
        repo_url = run(f"gh repo view {args.username}/{args.repo} --json url -q .url")
        print(f"Using existing repository: {repo_url}")

    # Step 2: Init local repo and commit
    init_local_repo(project_path)

    # Step 3: Optional tag
    if args.tag:
        create_tag(project_path, tag_name=args.tag)

    # Step 4: Add remote and push
    add_remote_and_push(project_path, repo_url)

    print("Repository setup and push completed successfully.")

if __name__ == "__main__":
    main()
