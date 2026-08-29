import subprocess
import time
import requests
import sys


def test_running_application():
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        time.sleep(2)

        response = requests.get(
            "http://127.0.0.1:5000/health",
            timeout=5
        )

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    finally:
        process.terminate()
        process.wait()