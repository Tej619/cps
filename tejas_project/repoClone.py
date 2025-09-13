# import git
# import os

# def pull_github_repo(repo_url, local_path):
#     try:
#         if os.path.exists(local_path):
#             print(f"Repository already exists at {local_path}, pulling latest changes...")
#             repo = git.Repo(local_path)
#             origin = repo.remotes.origin
#             origin.pull()
#             return "Pulled"
#         else:
#             print(f"Cloning repository from {repo_url} to {local_path}...")
#             git.Repo.clone_from(repo_url, local_path)
#             return "Cloned"
#     except Exception as e:
#         print(f"Error with {repo_url}: {e}")
#         return f"Error: {e}"

# if __name__ == "__main__":
#     # Path to your text file
#     txt_file = "repos.txt"

#     # Read all repo URLs from file
#     with open(txt_file, "r") as f:
#         repo_urls = [line.strip() for line in f if line.strip()]

#     # Create a folder for cloned repos
#     os.makedirs("./cloned_repos", exist_ok=True)

#     for repo_url in repo_urls:
#         repo_name = repo_url.split("/")[-1].replace(".git", "")
#         local_path = os.path.join("./cloned_repos", repo_name)

#         status = pull_github_repo(repo_url, local_path)
#         print(f"{repo_url} --> {status}\n")

import os
import subprocess
import git

# --- CONFIG ---
txt_file = "repos.txt"       # file containing repo URLs
clone_dir = "cloned_repos"   # where repos will be cloned
failed_builds = []           # track repos that fail docker build

# Ensure clone directory exists
os.makedirs(clone_dir, exist_ok=True)

def clone_repo(repo_url):
    """Clone a GitHub repo into clone_dir (skip if already cloned)."""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(clone_dir, repo_name)
    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url}...")
        try:
            git.Repo.clone_from(repo_url, repo_path)
        except Exception as e:
            print(f"Failed to clone {repo_url}: {e}")
            return None
    else:
        print(f"✔ Repo already exists: {repo_path}")
    return repo_path

def build_docker_images(repo_path):
    """Find Dockerfiles in a repo and build images."""
    for root, dirs, files in os.walk(repo_path):
        if "Dockerfile" in files:
            tag = os.path.basename(root).lower().replace(" ", "_")
            print(f"Building Docker image for: {root} (tag: {tag})")
            try:
                subprocess.run(
                    ["docker", "build", "-t", tag, "."],
                    cwd=root,
                    check=True
                )
                print(f"Successfully built {tag}")
            except subprocess.CalledProcessError:
                print(f"Docker build failed in {root}")
                failed_builds.append(root)

if __name__ == "__main__":
    # Read repo URLs from file
    with open(txt_file, "r") as f:
        repo_urls = [line.strip() for line in f if line.strip()]

    # Process each repo
    for repo_url in repo_urls:
        repo_path = clone_repo(repo_url)
        if repo_path:
            build_docker_images(repo_path)

    # Print final report
    print("\nFailed Docker builds:")
    for repo in failed_builds:
        print(" -", repo)
