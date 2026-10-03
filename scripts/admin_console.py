"""Run the Calleem super-admin console on this PC only.

The public deployment has no admin API (ADMIN_API_ENABLED=false) and no /admin pages.
This script starts the exact production backend image with the live production settings
(read from the Lightsail deployment) plus ADMIN_API_ENABLED=true, and the Next.js admin
UI. Both listen on 127.0.0.1 only, so nothing is reachable from the internet or your LAN.

    python scripts/admin_console.py        # then log in at http://localhost:3000/admin
                                           # Ctrl+C stops everything

Requires Docker, Node.js (npm install in frontend_next) and the AWS CLI (logged in).
"""
import json
import os
import subprocess
import tempfile
import time
import urllib.request
import webbrowser

REGION = "eu-west-3"
SERVICE = "calleem-backend"
CONTAINER = "backend"
REGISTRY = "143876480018.dkr.ecr.eu-west-3.amazonaws.com"
API_NAME = "calleem-admin-api"
API_URL = "http://localhost:8000"
UI_URL = "http://localhost:3000"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def wait_for(url, seconds):
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                if r.status < 500:
                    return
        except Exception:
            pass
        time.sleep(2)
    raise SystemExit(f"{url} did not come up")


def start_api():
    out = subprocess.run(
        ["aws", "lightsail", "get-container-services", "--service-name", SERVICE, "--region", REGION, "--output", "json"],
        check=True, capture_output=True, text=True,
    ).stdout
    live = json.loads(out)["containerServices"][0]["currentDeployment"]["containers"][CONTAINER]
    env = dict(live.get("environment", {}))
    env.update({
        "ADMIN_API_ENABLED": "true",
        "WORKERS": "1",
        "CORS_ORIGINS": "http://localhost:3000,http://127.0.0.1:3000",
    })

    password = subprocess.run(["aws", "ecr", "get-login-password", "--region", REGION], check=True, capture_output=True, text=True).stdout
    subprocess.run(["docker", "login", "--username", "AWS", "--password-stdin", REGISTRY], input=password, text=True, check=True, capture_output=True)
    print(f"Pulling the production image {live['image']} ...")
    subprocess.run(["docker", "pull", "-q", live["image"]], check=True)
    subprocess.run(["docker", "rm", "-f", API_NAME], capture_output=True)

    # Production secrets go through a private temp file, never the command line.
    fd, path = tempfile.mkstemp(suffix=".env")
    try:
        with os.fdopen(fd, "w") as f:
            f.writelines(f"{k}={v}\n" for k, v in env.items())
        subprocess.run(
            ["docker", "run", "-d", "--rm", "--name", API_NAME, "-p", "127.0.0.1:8000:8000", "--env-file", path, live["image"]],
            check=True, capture_output=True,
        )
    finally:
        os.remove(path)
    wait_for(f"{API_URL}/health", 90)


def main():
    start_api()
    print("Admin API running on", API_URL, "(this PC only)")
    npx = "npx.cmd" if os.name == "nt" else "npx"
    ui = subprocess.Popen(
        [npx, "next", "dev", "-H", "127.0.0.1", "-p", "3000"],
        cwd=os.path.join(ROOT, "frontend_next"),
        env={**os.environ, "ADMIN_UI_ENABLED": "true", "NEXT_PUBLIC_API_URL": API_URL, "API_URL": API_URL},
    )
    try:
        wait_for(f"{UI_URL}/admin/login", 240)
        print(f"\nAdmin console ready: {UI_URL}/admin  (Ctrl+C to stop)\n")
        webbrowser.open(f"{UI_URL}/admin/login")
        ui.wait()
    except KeyboardInterrupt:
        pass
    finally:
        ui.terminate()
        subprocess.run(["docker", "stop", API_NAME], capture_output=True)
        print("Admin console stopped.")


if __name__ == "__main__":
    main()
