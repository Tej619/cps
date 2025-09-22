import subprocess
import time
import sys

IMAGE_NAME = "vsomeip"
CONTAINER_NAME = "vsome"
LOG_FILE = "strace_output.log"

def run_cmd(cmd, capture_output=False):
    print(f"⚡ Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, text=True, capture_output=capture_output)

def build_image():
    run_cmd(["docker", "build", "-t", IMAGE_NAME, "."])

def run_container():
    # Keep container alive indefinitely
    run_cmd([
        "docker", "run", "-d", "--name", CONTAINER_NAME, "--rm", IMAGE_NAME, "sleep", "infinity"
    ])

def get_container_pid():
    result = run_cmd(
        ["docker", "inspect", "--format", "{{.State.Pid}}", CONTAINER_NAME],
        capture_output=True
    )
    return result.stdout.strip()

def strace_container(pid):
    with open(LOG_FILE, "w") as f:
        proc = subprocess.Popen(
            ["sudo", "nsenter", "--target", pid, "--pid", "strace", "-f", "-tt", "-T", "-p", "1"],
            stdout=f,
            stderr=f
        )
    print(f"📄 Strace attached inside container namespace, logs -> {LOG_FILE}")
    return proc

def main():
    try:
        build_image()
        run_container()
        time.sleep(2)  # give container time to start
        pid = get_container_pid()
        print(f"🐳 Container host PID: {pid}")
        proc = strace_container(pid)
        proc.wait()
        print("✅ Strace finished, check log file.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
