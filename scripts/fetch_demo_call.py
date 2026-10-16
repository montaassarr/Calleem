"""Turn a real Vapi call into the landing page's voice demo (the "Hear a real call" button).

1. Give a demo business the plumber template and the Vapi "Elliot" voice, then call it (phone or the
   dashboard's test call) and play a homeowner, roughly following the caller script below.
2. Copy the call ID from the Vapi dashboard (Call Logs) and run, with the Vapi *private* API key:
       $env:VAPI_API_KEY = "..."                                   # PowerShell
       python scripts/fetch_demo_call.py <call-id> --business "Bluebonnet Plumbing"
   The recording goes to frontend_next/public/audio/ and every line of the transcript, with the second
   it starts and the pipeline node it lights up, to frontend_next/lib/demo-call.json. Check the printed
   mapping (edit the JSON if a line landed on the wrong node), then commit both and deploy the frontend.

Caller script (say it naturally; use fake details):
  - "It's an emergency, my water heater is leaking all over the garage."
  - after the safety tip: "Okay, I turned it off."
  - "Mike Johnson, 2418 Oak Street in Dallas. I own the house."  /  number: "214-555-0147"
  - when offered a time: "Yes, that works."
  - "Perfect, thank you!"
"""
import argparse
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, "frontend_next", "public", "audio")
DATA_PATH = os.path.join(ROOT, "frontend_next", "lib", "demo-call.json")
AUDIO_NAME = "plumber-demo"
API = os.environ.get("VAPI_BASE_URL", "https://api.vapi.ai").rstrip("/")

# Which pipeline node a Calleem line lights up: first match wins.
CALLEEM_RULES = [
    ("kb", "Safety first", "Walks the caller through a quick fix",
     r"\b(valve|shut (it |the water )?off|turn (it |the water )?off|main water|breaker|bucket|towels?)\b"),
    ("book", "Books the job", "Visit saved to the schedule",
     r"(you're (all )?(set|booked)|i've (booked|scheduled)|booked you|scheduled you|is booked|is confirmed)"),
    ("cal", "Finds a slot", "Checks the schedule in real time",
     r"\b(available|availability|opening|earliest|slot|\d{1,2}(:\d{2})?\s?(a\.?m\.?|p\.?m\.?))\b"),
    ("confirm", "Sends confirmation", "Text confirmation to the caller", r"\b(text|sms|confirmation)\b"),
    ("calleem", "Takes the details", "Name, number and service address",
     r"\b(your name|address|phone number|best number|zip|own or rent)\b"),
]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Vapi answers recording requests with a redirect to a signed URL, which must be fetched without our key."""

    def redirect_request(self, *args, **kwargs):
        return None


def api_json(path: str, key: str) -> dict:
    request = urllib.request.Request(f"{API}{path}", headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        sys.exit(f"Vapi API {path} failed: {e.code} {e.read().decode(errors='replace')[:300]}")


def download_recording(call_id: str, key: str, call: dict):
    """(bytes, content type, url) of the mono recording: the private-bucket endpoint, else the legacy URL."""
    url = None
    request = urllib.request.Request(f"{API}/call/{call_id}/mono-recording", headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.build_opener(_NoRedirect).open(request, timeout=120) as response:
            return response.read(), response.headers.get("Content-Type", ""), response.geturl()
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            url = e.headers.get("Location")
        elif e.code != 404:
            sys.exit(f"Vapi recording download failed: {e.code} {e.read().decode(errors='replace')[:300]}")
    if not url:
        artifact = call.get("artifact") or {}
        url = artifact.get("recordingUrl") or call.get("recordingUrl")
    if not url:
        sys.exit("This call has no recording. Is recording on for the assistant (artifactPlan.recordingEnabled)?")
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read(), response.headers.get("Content-Type", ""), url


def audio_extension(content_type: str, url: str) -> str:
    content_type = content_type.lower()
    if "mpeg" in content_type or "mp3" in content_type:
        return ".mp3"
    if "wav" in content_type or "wave" in content_type:
        return ".wav"
    match = re.search(r"\.(mp3|wav|ogg|m4a)(\?|$)", url.lower())
    return f".{match.group(1)}" if match else ".wav"


def transcript_lines(call: dict) -> list:
    """Spoken lines in order: [{at, who, text}], consecutive lines by the same speaker merged."""
    messages = (call.get("artifact") or {}).get("messages") or call.get("messages") or []
    first_time = next((m["time"] for m in messages if isinstance(m.get("time"), (int, float))), None)
    lines = []
    for m in messages:
        role = (m.get("role") or "").lower()
        who = "calleem" if role in ("bot", "assistant") else "caller" if role in ("user", "customer") else None
        text = (m.get("message") or m.get("content") or "").strip()
        if not who or not text:
            continue
        at = m.get("secondsFromStart")
        if at is None and first_time is not None and isinstance(m.get("time"), (int, float)):
            at = (m["time"] - first_time) / 1000
        at = round(float(at or 0), 2)
        if lines and lines[-1]["who"] == who:
            lines[-1]["text"] += " " + text
        else:
            lines.append({"at": at, "who": who, "text": text})
    return lines


def assign_nodes(lines: list) -> list:
    """Add node, label and stepLabel to each line (see CALLEEM_RULES); the greeting and the last line are fixed."""
    first_caller = next((i for i, l in enumerate(lines) if l["who"] == "caller"), None)
    for i, line in enumerate(lines):
        if i == len(lines) - 1:
            node, label, step_label = "end", "Call ends", "Emergency handled in one call"
        elif i == 0 and line["who"] == "calleem":
            node, label, step_label = "calleem", "Calleem answers", "Picks up on the first ring, 24/7"
        elif line["who"] == "caller":
            node = "phone"
            label, step_label = ("Caller explains", "A homeowner with an emergency") if i == first_caller \
                else ("Caller answers", "Shares the details")
        else:
            node, label, step_label = next(
                ((n, lb, sl) for n, lb, sl, pattern in CALLEEM_RULES if re.search(pattern, line["text"], re.I)),
                ("calleem", "Calleem replies", "Asks the right questions"),
            )
        line.update(node=node, label=label, stepLabel=step_label)
    return lines


def call_duration(call: dict, lines: list) -> float:
    try:
        started = datetime.fromisoformat(call["startedAt"].replace("Z", "+00:00"))
        ended = datetime.fromisoformat(call["endedAt"].replace("Z", "+00:00"))
        return round((ended - started).total_seconds(), 1)
    except (KeyError, TypeError, ValueError):
        return round(lines[-1]["at"] + 5, 1) if lines else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("call_id", help="the Vapi call ID (Vapi dashboard > Call Logs)")
    parser.add_argument("--business", default="Bluebonnet Plumbing", help="the demo business name used in the call")
    parser.add_argument("--voice", default="Elliot", help="voice name shown on the button")
    args = parser.parse_args()

    key = os.environ.get("VAPI_API_KEY") or os.environ.get("VAPI_PRIVATE_API_KEY")
    if not key:
        sys.exit("Set VAPI_API_KEY to the Vapi private API key (Vapi dashboard > API Keys).")

    call = api_json(f"/call/{args.call_id}", key)
    lines = assign_nodes(transcript_lines(call))
    if len(lines) < 2:
        sys.exit("The call has no usable transcript yet. Wait for it to finish processing and try again.")

    audio, content_type, url = download_recording(args.call_id, key, call)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    for old in glob.glob(os.path.join(AUDIO_DIR, f"{AUDIO_NAME}.*")):
        os.remove(old)
    filename = AUDIO_NAME + audio_extension(content_type, url)
    with open(os.path.join(AUDIO_DIR, filename), "wb") as f:
        f.write(audio)

    data = {
        "audio": f"/audio/{filename}",
        "voice": args.voice,
        "business": args.business,
        "durationSeconds": call_duration(call, lines),
        "lines": lines,
    }
    with open(DATA_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Saved {filename} ({len(audio) / 1024:.0f} KB) and {len(lines)} lines to {DATA_PATH}:\n")
    for line in lines:
        print(f"  {line['at']:6.1f}s  {line['node']:8} {line['who']:8} {line['text'][:70]}")


if __name__ == "__main__":
    main()
