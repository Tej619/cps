import subprocess
import os
import sys

REPO_LIST_FILE = "repos.txt"
CLONE_DIR = os.path.join(os.getcwd(), "clone_repos")
LOG_DIR = os.path.join(os.getcwd(), "logs")

os.makedirs(CLONE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def run_cmd(cmd, cwd=None, capture_output=False):
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, text=True, cwd=cwd, capture_output=capture_output)

def clone_repo(repo_url):
    repo_name = os.path.basename(repo_url).replace(".git", "")
    repo_path = os.path.join(CLONE_DIR, repo_name)
    if os.path.exists(repo_path):
        print(f"Repo {repo_name} already cloned.")
    else:
        run_cmd(["git", "clone", repo_url, repo_path])
    return repo_name, repo_path

def build_image(repo_name, repo_path):
    run_cmd(["docker", "build", "-t", repo_name, "."], cwd=repo_path)

def run_container_with_strace(repo_name):
    log_file = os.path.join(LOG_DIR, f"{repo_name}_strace.log")
    with open(log_file, "w") as f:
        proc = subprocess.Popen(
            ["strace", "-f", "-tt", "-T", "docker", "run", "--rm", "--name", f"{repo_name}_container", repo_name ],
            stdout=f,
            stderr=f
        )
    print(f"Strace log saved to {log_file}")
    proc.wait()

def main():
    if not os.path.exists(REPO_LIST_FILE):
        print(f"Repo list file {REPO_LIST_FILE} not found")
        sys.exit(1)

    with open(REPO_LIST_FILE, "r") as f:
        repos = [line.strip() for line in f if line.strip()]

    for repo_url in repos:
        try:
            print(f"\n=== Processing {repo_url} ===")
            repo_name, repo_path = clone_repo(repo_url)
            build_image(repo_name, repo_path)
            run_container_with_strace(repo_name)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {repo_url}: {e}")
            continue

if __name__ == "__main__":
    main()
