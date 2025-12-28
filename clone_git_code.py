import subprocess
import os

REPO_FILE = "docker_repos.txt"
CLONE_DIR = "cloned_repos"

def clone_repositories():
    if not os.path.exists(CLONE_DIR):
        os.makedirs(CLONE_DIR)

    with open(REPO_FILE, "r") as file:
        repos = file.readlines()

    for repo in repos:
        repo = repo.strip()

        # Skip empty lines or comments
        if not repo or repo.startswith("#"):
            continue

        print(f"Cloning: {repo}")
        try:
            subprocess.run(
                ["git", "clone", repo],
                cwd=CLONE_DIR,
                check=True
            )
        except subprocess.CalledProcessError:
            print(f"❌ Failed to clone: {repo}")

if __name__ == "__main__":
    clone_repositories()
