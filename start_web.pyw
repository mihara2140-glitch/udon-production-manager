import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


APP_URL = "http://127.0.0.1:5000"
BASE_DIR = Path(__file__).resolve().parent
WEB_APP = BASE_DIR / "web_app.py"


def server_is_running():
    try:
        with urllib.request.urlopen(APP_URL, timeout=0.5) as response:
            return 200 <= response.status < 500
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def start_server():
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NO_WINDOW

    subprocess.Popen(
        [sys.executable, str(WEB_APP)],
        cwd=str(BASE_DIR),
        creationflags=creation_flags,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_server(timeout_seconds=8):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if server_is_running():
            return True
        time.sleep(0.25)
    return False


def main():
    if not server_is_running():
        start_server()
        wait_for_server()

    webbrowser.open(APP_URL)


if __name__ == "__main__":
    main()
