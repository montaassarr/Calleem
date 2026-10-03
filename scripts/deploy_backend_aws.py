"""Build the backend image, push it to ECR and roll it out on the Lightsail container service.

The new deployment reuses the environment variables, ports and health check of the deployment
that is currently live; only the image changes. Requires Docker and the AWS CLI (logged in).

    python scripts/deploy_backend_aws.py
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

REGION = "eu-west-3"
SERVICE = "calleem-backend"
CONTAINER = "backend"
REGISTRY = "143876480018.dkr.ecr.eu-west-3.amazonaws.com"
REPO = f"{REGISTRY}/calleem-backend"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(*cmd, **kw):
    print("$", " ".join(cmd))
    return subprocess.run(cmd, check=True, **kw)


def aws_json(*args):
    out = subprocess.run(["aws", *args, "--region", REGION, "--output", "json"], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def main():
    sha = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "backend"], capture_output=True, text=True).stdout.strip()
    tag = f"{sha}-{int(time.time())}" if dirty else sha
    image = f"{REPO}:{tag}"

    run("docker", "build", "--platform", "linux/amd64", "-t", image, os.path.join(ROOT, "backend"))
    password = subprocess.run(["aws", "ecr", "get-login-password", "--region", REGION], check=True, capture_output=True, text=True).stdout
    run("docker", "login", "--username", "AWS", "--password-stdin", REGISTRY, input=password, text=True, capture_output=True)
    run("docker", "push", image)

    service = aws_json("lightsail", "get-container-services", "--service-name", SERVICE)["containerServices"][0]
    current = service["currentDeployment"]
    containers = current["containers"]
    containers[CONTAINER]["image"] = image
    request = {"serviceName": SERVICE, "containers": containers, "publicEndpoint": current["publicEndpoint"]}

    # The request holds the production environment variables: keep it in a private temp file only.
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(request, f)
        version = aws_json("lightsail", "create-container-service-deployment", "--cli-input-json", "file://" + path.replace("\\", "/"))["containerService"]["nextDeployment"]["version"]
    finally:
        os.remove(path)
    print(f"deployment {version} started with {image}")

    for _ in range(60):
        svc = aws_json("lightsail", "get-container-services", "--service-name", SERVICE)["containerServices"][0]
        cur, nxt = svc.get("currentDeployment", {}), svc.get("nextDeployment") or {}
        if nxt.get("state") == "FAILED":
            sys.exit(f"deployment {version} FAILED; the previous version is still serving traffic")
        if cur.get("version") == version and cur.get("state") == "ACTIVE":
            break
        time.sleep(15)
    else:
        sys.exit("timed out waiting for the deployment")

    url = svc["url"].rstrip("/") + "/health"
    with urllib.request.urlopen(url, timeout=20) as r:
        print(f"deployment {version} ACTIVE - {url} -> {r.status} {r.read().decode()}")


if __name__ == "__main__":
    main()
