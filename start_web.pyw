import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


APP_URL = "http://127.0.0.1:5000"
APP_PORT = 5000
BASE_DIR = Path(__file__).resolve().parent
WEB_APP = BASE_DIR / "web_app.py"


def hidden_creation_flags():
    if sys.platform == "win32":
        return subprocess.CREATE_NO_WINDOW
    return 0


def update_from_github():
    """Git管理されている場合だけ、起動前にmainの最新版を取得する。"""
    if not (BASE_DIR / ".git").exists():
        return

    git = shutil.which("git")
    if not git:
        return

    try:
        subprocess.run(
            [git, "pull", "--ff-only"],
            cwd=str(BASE_DIR),
            creationflags=hidden_creation_flags(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


def server_is_running():
    try:
        with urllib.request.urlopen(APP_URL, timeout=0.5) as response:
            return 200 <= response.status < 500
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def listening_pids(port):
    """Windowsで指定ポートを待ち受けているPIDを取得する。"""
    if sys.platform != "win32":
        return []

    try:
        result = subprocess.run(
            ["netstat", "-ano", "-p", "tcp"],
            capture_output=True,
            text=True,
            creationflags=hidden_creation_flags(),
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    pids = set()
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[3].upper() != "LISTENING":
            continue
        local_address = parts[1]
        if not local_address.endswith(f":{port}"):
            continue
        try:
            pids.add(int(parts[-1]))
        except ValueError:
            continue
    return sorted(pids)


def stop_existing_server():
    """前回のローカルWebサーバーを停止して、最新版へ確実に切り替える。"""
    if sys.platform != "win32":
        return

    for pid in listening_pids(APP_PORT):
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                creationflags=hidden_creation_flags(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass

    deadline = time.time() + 3
    while time.time() < deadline:
        if not server_is_running():
            return
        time.sleep(0.2)


def start_server():
    env = os.environ.copy()
    # ローカル版は自動リロードを使用。公開先ではGunicornを使う。
    env["FLASK_DEBUG"] = "1"
    env["HOST"] = "127.0.0.1"
    env["PORT"] = str(APP_PORT)

    subprocess.Popen(
        [sys.executable, str(WEB_APP)],
        cwd=str(BASE_DIR),
        env=env,
        creationflags=hidden_creation_flags(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_server(timeout_seconds=10):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if server_is_running():
            return True
        time.sleep(0.25)
    return False


def main():
    update_from_github()
    stop_existing_server()
    start_server()
    wait_for_server()
    webbrowser.open(APP_URL)


if __name__ == "__main__":
    main()
