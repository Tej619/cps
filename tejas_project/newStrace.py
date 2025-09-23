# import subprocess
# import os
# import sys

# REPO_LIST_FILE = "repos.txt"
# CLONE_DIR = os.path.join(os.getcwd(), "clone_repos")
# LOG_DIR = os.path.join(os.getcwd(), "logs")

# os.makedirs(CLONE_DIR, exist_ok=True)
# os.makedirs(LOG_DIR, exist_ok=True)

# def run_cmd(cmd, cwd=None, capture_output=False):
#     print(f"Running: {' '.join(cmd)}")
#     return subprocess.run(cmd, check=True, text=True, cwd=cwd, capture_output=capture_output)

# def clone_repo(repo_url):
#     repo_name = os.path.basename(repo_url).replace(".git", "")
#     repo_path = os.path.join(CLONE_DIR, repo_name)
#     if os.path.exists(repo_path):
#         print(f"Repo {repo_name} already cloned.")
#     else:
#         run_cmd(["git", "clone", repo_url, repo_path])
#     return repo_name, repo_path

# def build_image(repo_name, repo_path):
#     run_cmd(["docker", "build", "-t", repo_name, "."], cwd=repo_path)

# def run_container_with_strace(repo_name):
#     log_file = os.path.join(LOG_DIR, f"{repo_name}_strace.log")
#     with open(log_file, "w") as f:
#         proc = subprocess.Popen(
#             ["strace", "-f", "-tt", "-T", "docker", "run", "--rm", "--name", f"{repo_name}_container", repo_name ],
#             stdout=f,
#             stderr=f
#         )
#     print(f"Strace log saved to {log_file}")
#     proc.wait()

# def main():
#     if not os.path.exists(REPO_LIST_FILE):
#         print(f"Repo list file {REPO_LIST_FILE} not found")
#         sys.exit(1)

#     with open(REPO_LIST_FILE, "r") as f:
#         repos = [line.strip() for line in f if line.strip()]

#     for repo_url in repos:
#         try:
#             print(f"\n=== Processing {repo_url} ===")
#             repo_name, repo_path = clone_repo(repo_url)
#             build_image(repo_name, repo_path)
#             run_container_with_strace(repo_name)
#         except subprocess.CalledProcessError as e:
#             print(f"Error processing {repo_url}: {e}")
#             continue

# if __name__ == "__main__":
#     main()


import subprocess
import os
import sys
import re

REPO_LIST_FILE = "repos.txt"
CLONE_DIR = os.path.join(os.getcwd(), "clone_repos")
LOG_DIR = os.path.join(os.getcwd(), "logs")

os.makedirs(CLONE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def run_cmd(cmd, cwd=None, capture_output=False):
    print(f"⚡ Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, text=True, cwd=cwd, capture_output=capture_output)

def clone_repo(repo_url):
    repo_name = os.path.basename(repo_url).replace(".git", "")
    repo_path = os.path.join(CLONE_DIR, repo_name)
    if os.path.exists(repo_path):
        print(f"📂 Repo {repo_name} already cloned.")
    else:
        run_cmd(["git", "clone", repo_url, repo_path])
    return repo_name, repo_path

def find_all_dockerfiles(repo_path):
    """
    Return list of folders containing Dockerfile
    """
    dockerfile_dirs = []
    for root, dirs, files in os.walk(repo_path):
        if "Dockerfile" in files:
            dockerfile_dirs.append(root)
            
    print(f"🔎 Found Dockerfiles in repo {repo_path}:")
    for d in dockerfile_dirs:
        print(f"   - {d}")
        
    return dockerfile_dirs

# def sanitize_name(repo_name, folder_path, base_repo_path):
#     """
#     Make unique image/log name by combining repo name and relative folder path
#     Replaces slashes and spaces with underscores
#     """
#     rel_path = os.path.relpath(folder_path, base_repo_path)
#     sanitized = rel_path.replace(os.sep, "_").replace(" ", "_")
#     return f"{repo_name}_{sanitized}".lower()

def sanitize_name(repo_name, folder_path, base_repo_path):
    """
    Make unique Docker image/log name by combining repo name and relative folder path
    Replaces invalid characters with underscores and removes trailing dots
    """
    rel_path = os.path.relpath(folder_path, base_repo_path)
    # Replace slashes and spaces with underscores
    sanitized = rel_path.replace(os.sep, "_").replace(" ", "_")
    # Remove invalid characters (keep letters, digits, _, -, .)
    sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "_", sanitized)
    # Remove leading/trailing dots or dashes
    sanitized = sanitized.strip(".-")
    if not sanitized:
        sanitized = "root"
    return f"{repo_name}_{sanitized}".lower()


def build_image(image_name, dockerfile_dir):
    run_cmd(["docker", "build", "-t", image_name, "."], cwd=dockerfile_dir)

def run_container_with_strace(image_name, log_file):
    with open(log_file, "w") as f:
        proc = subprocess.Popen(
            ["strace", "-f", "-tt", "-T", "docker", "run", "--rm", "--name", f"{image_name}_container", image_name],
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
            dockerfile_dirs = find_all_dockerfiles(repo_path)
            if not dockerfile_dirs:
                print(f"Skipping {repo_name}, no Dockerfile found")
                continue

            for dockerfile_dir in dockerfile_dirs:
                image_name = sanitize_name(repo_name, dockerfile_dir, repo_path)
                log_file = os.path.join(LOG_DIR, f"{image_name}_strace.log")
                build_image(image_name, dockerfile_dir)
                run_container_with_strace(image_name, log_file)

        except subprocess.CalledProcessError as e:
            print(f"Error processing {repo_url}: {e}")
            continue

if __name__ == "__main__":
    main()
