#!/usr/bin/env python3
"""populate_repo.py
Creates a set of feature branches, makes dummy commits, and tags releases.
Usage: python populate_repo.py --path <project_path>
"""
import subprocess
import sys
from pathlib import Path

def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}\nstdout:{result.stdout}\nstderr:{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def create_branch(path, branch_name):
    run(f"git checkout -b {branch_name}", cwd=path)
    # make a dummy change
    dummy_file = path / f"{branch_name.replace('/', '_')}.txt"
    dummy_file.write_text(f"Dummy content for {branch_name}\n")
    run(f"git add {dummy_file.name}", cwd=path)
    run(f"git commit -m \"feat({branch_name.split('/')[0]}): add {dummy_file.name}\"", cwd=path)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="Project directory")
    args = parser.parse_args()
    project_path = Path(args.path).resolve()
    if not (project_path / ".git").exists():
        print("Error: Not a git repository")
        sys.exit(1)
    # Create branches
    branch_names = [
        "feature/login",
        "feature/bookmarks",
        "feature/history",
        "feature/downloads",
        "feature/settings",
        "feature/ui-improvements",
        "feature/ai-integration",
        "feature/multi-tab",
        "feature/search",
        "feature/performance",
    ]
    for bn in branch_names:
        create_branch(project_path, bn)
    # Return to main branch
    run("git checkout main", cwd=project_path)
    # Create tags
    tags = {"v0.1.0": "Initial release", "v0.2.0": "Feature expansion"}
    for tag, msg in tags.items():
        run(f"git tag -a {tag} -m \"{msg}\"", cwd=project_path)
    # Push branches and tags
    run("git push -u origin --all", cwd=project_path)
    run("git push origin --tags", cwd=project_path)
    print("Repository population complete.")

if __name__ == "__main__":
    main()
