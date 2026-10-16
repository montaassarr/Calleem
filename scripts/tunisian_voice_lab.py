"""
Create side-by-side Tunisian Derja test assistants in Vapi, then call each one from the Vapi
dashboard and pick the best speech-to-text, LLM and voice by ear: no published benchmark covers
Tunisian phone calls yet. Each variant changes one part of the baseline (A), so you hear what it does.

    python scripts/tunisian_voice_lab.py create              # all variants
    python scripts/tunisian_voice_lab.py create --only A,C,F
    python scripts/tunisian_voice_lab.py delete              # remove every lab assistant

Put the test account's key in scripts/.env (git-ignored): VAPI_PRIVATE_KEY=<private key>. The live
Calleem account (key read from Lightsail with the AWS CLI) is only used with --production.
Cloned ElevenLabs voices: add TN_ELEVENLABS_VOICES to the same file, as for the backend
("voiceId:Name:gender,..."); each gets one variant per ElevenLabs model. Lab assistants are tagged metadata.voice_lab="tunisian";
they have no tools, no phone number and send nothing to the Calleem webhook.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
from services import voice_languages  # noqa: E402

TN = voice_languages.TUNISIAN
VAPI = os.getenv("VAPI_BASE_URL", "https://api.vapi.ai")
LAB_ENV = os.path.join(ROOT, "scripts", ".env")
LAB_TAG = "tunisian"
BUSINESS = "Clinique Yasmine"

LAB_FACTS = """TEST LINE used to compare voices. You work for a pretend dental clinic in Tunis.
- Services: consultation 40 dinars, scaling (détartrage) 60 dinars, filling 80 dinars, teeth whitening 250 dinars.
- Open Monday to Saturday from 9:00 to 18:00, closed on Sunday.
- Address: 12 rue de Marseille, Tunis, near avenue Habib Bourguiba."""

LAB_BOOKING = """=== BOOKING (test line) ===
There are no tools on this test line. To book, ask for the name, the service, the day and time, and the phone number, one question at a time. Any time within opening hours is free. Read the details back, and once the caller confirms, say the appointment is booked and say goodbye.
"""

REEM = {"provider": "azure", "voiceId": "ar-TN-ReemNeural"}
HEDI = {"provider": "azure", "voiceId": "ar-TN-HediNeural"}
GPT_4O = {"provider": "openai", "model": "gpt-4o"}
STT = voice_languages.TN_TRANSCRIBERS

TEST_SCRIPT = [
    "عسلامة، نحب ناخو رونديفو عند طبيب الأسنان.",
    "قدّاش الكونسيلتاسيون؟ و الدِتارتراج قدّاش؟",
    "نجّم نجي غدوة مع العشرة متاع الصباح؟",
    "إسمي سيرين بن عمر.",
    "النيمرو: ثمنية و تسعين، مية و ستّة و عشرين، خمسة و أربعين  (98 126 045)",
    "Same number in French: quatre-vingt-dix-huit, cent vingt-six, zéro quarante-cinq",
    "Normalement je préfère l'après-midi، ما فمّاش بلاصة نهار السبت؟",
    "وين جايّة العيادة بالضبط؟",
]


def variants():
    rows = [
        ("A", "Baseline: Azure STT, Reem, GPT-4o", STT["azure"], REEM, GPT_4O),
        ("B", "Voice: Hedi (male)", STT["azure"], HEDI, GPT_4O),
        ("C", "STT: Soniox, Arabic+French", STT["soniox"], REEM, GPT_4O),
        ("D", "STT: ElevenLabs Scribe v2", STT["11labs"], REEM, GPT_4O),
        ("E", "STT: Deepgram Nova-3 (generic ar)", STT["deepgram"], REEM, GPT_4O),
        ("F", "LLM: Gemini 3.5 Flash", STT["azure"], REEM, {"provider": "google", "model": "gemini-3.5-flash"}),
        ("G", "LLM: Claude Haiku 5.5", STT["azure"], REEM, {"provider": "anthropic", "model": "claude-haiku-5-5"}),
        ("H", "LLM: GPT-4o mini (cheaper)", STT["azure"], REEM, {"provider": "openai", "model": "gpt-4o-mini"}),
    ]
    letters = iter("IJKLMNOPQRSTUVWXYZ")
    for voice in voice_languages.tunisian_voices():
        if voice["provider"] != "11labs":
            continue
        for model in ("eleven_turbo_v2_5", "eleven_v4_turbo"):
            config = {"provider": "11labs", "voiceId": voice["id"], "model": model, "language": "ar",
                      "stability": 0.5, "similarityBoost": 0.75}
            rows.append((next(letters), f"Voice: {voice['name']} ({model})", STT["azure"], config, GPT_4O))
    return rows


def lab_prompt():
    full = voice_languages.system_prompt(TN, BUSINESS, LAB_FACTS)
    return full.split("=== BOOKING FLOW ===")[0] + LAB_BOOKING


def load_lab_env():
    """KEY=VALUE lines of scripts/.env into the environment (variables already set win)."""
    if not os.path.exists(LAB_ENV):
        return
    for line in open(LAB_ENV, encoding="utf-8-sig"):
        name, sep, value = line.strip().partition("=")
        if sep and name and not name.startswith("#"):
            os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def vapi_key(production):
    if not production:
        key = os.getenv("VAPI_PRIVATE_KEY")
        if not key:
            sys.exit(f"No Vapi key: put VAPI_PRIVATE_KEY=<private key of the test account> in {LAB_ENV}")
        return key
    out = subprocess.run(
        ["aws", "lightsail", "get-container-services", "--service-name", "calleem-backend",
         "--region", "eu-west-3", "--output", "json"],
        check=True, capture_output=True, text=True,
    ).stdout
    env = json.loads(out)["containerServices"][0]["currentDeployment"]["containers"]["backend"].get("environment", {})
    for name in ("VAPI_PRIVATE_KEY", "VAPI_PRIVATE_API_KEY", "VAPI_API_KEY"):
        if env.get(name):
            return env[name]
    sys.exit("The live deployment has no Vapi key.")


def call(key, method, path, body=None):
    request = urllib.request.Request(
        VAPI + path, method=method, data=json.dumps(body).encode() if body is not None else None,
        # Cloudflare in front of Vapi rejects urllib's default User-Agent (error code 1010)
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "calleem-voice-lab/1.0"},
    )
    # Creating an assistant can take over 30 s, and Vapi still creates it after a client timeout
    with urllib.request.urlopen(request, timeout=90) as response:
        raw = response.read()
        return json.loads(raw) if raw else None


def create(key, only):
    prompt = lab_prompt()
    made = []
    for letter, label, transcriber, voice, llm in variants():
        if only and letter not in only:
            continue
        assistant = {
            "name": f"TN Lab {letter} - {label}"[:40],
            "firstMessage": voice_languages.first_message(TN, BUSINESS),
            "model": {**llm, "temperature": 0.5, "maxTokens": 300, "messages": [{"role": "system", "content": prompt}]},
            "voice": voice,
            "transcriber": transcriber,
            "serverMessages": [],
            "maxDurationSeconds": 300,
            "metadata": {"voice_lab": LAB_TAG, "variant": letter},
        }
        try:
            result = call(key, "POST", "/assistant", assistant)
            made.append((letter, label, result["id"]))
        except urllib.error.HTTPError as e:
            print(f"  {letter} {label}: Vapi refused it ({e.code}): {e.read().decode()[:300]}")

    print("\nCall each one with 'Talk to Assistant' in the Vapi dashboard (use headphones):\n")
    for letter, label, assistant_id in made:
        print(f"  {letter}  {label:<40} https://dashboard.vapi.ai/assistants/{assistant_id}")
    print("\nSay the same lines on every call:")
    for i, line in enumerate(TEST_SCRIPT, 1):
        print(f"  {i}. {line}")
    print("\nScore each 1-5: understood me / sounded Tunisian / natural voice / fast replies,"
          "\nand note whether it got the phone number right. Remove them with: "
          "python scripts/tunisian_voice_lab.py delete")


def delete(key):
    assistants = call(key, "GET", "/assistant?limit=1000") or []
    lab = [a for a in assistants if (a.get("metadata") or {}).get("voice_lab") == LAB_TAG]
    for assistant in lab:
        call(key, "DELETE", f"/assistant/{assistant['id']}")
        print(f"  deleted {assistant.get('name')}")
    print(f"{len(lab)} lab assistant(s) removed")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("action", choices=["create", "delete"])
    parser.add_argument("--only", default="", help="comma-separated variant letters, e.g. A,C,F")
    parser.add_argument("--production", action="store_true", help="use the live Calleem Vapi account")
    args = parser.parse_args()
    load_lab_env()
    key = vapi_key(args.production)
    print(f"Vapi key ...{key[-4:]} ({'live Calleem account' if args.production else 'test account'})")
    if args.action == "create":
        create(key, {v.strip().upper() for v in args.only.split(",") if v.strip()})
    else:
        delete(key)


if __name__ == "__main__":
    main()
