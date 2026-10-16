"""
Languages the voice assistant can speak, and the Vapi stack (speech-to-text, LLM, voice) behind each.

A business's language is stored in tenant.ai_config.language and in its Vapi assistant's
metadata.language, so every later assistant update keeps the same stack. "en" is the original
Calleem setup.

Tunisian Arabic ("ar-TN", Derja), chosen in October 2026:
- Speech-to-text: Azure "ar-TN", the only Tunisian-specific recogniser Vapi accepts. Deepgram Nova-3
  knows ar-TN too, but Vapi only passes plain "ar" (generic Arabic), so it is the fallback.
- LLM: GPT-4o, the best model native speakers rated for answering in Tunisian Arabic (TounsiBench,
  EMNLP 2025; Gemini and Claude were not in that test).
- Voice: Azure's native Tunisian voices, Reem and Hedi. For a more natural voice, clone a Tunisian
  speaker on ElevenLabs and list it in TN_ELEVENLABS_VOICES: it becomes the default voice and the
  Azure voice of the same gender stays as its fallback.
TN_TRANSCRIBER, TN_LLM and TN_ELEVENLABS_MODEL swap the other parts for A/B tests (see .env.example).
"""

import copy
import os
import re
from typing import Any, Dict, List, Optional

DEFAULT_LANGUAGE = "en"
TUNISIAN = "ar-TN"

LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"label": "English", "native_label": "English"},
    TUNISIAN: {"label": "Tunisian Arabic (Derja)", "native_label": "تونسي"},
}


def normalize(language: Optional[str]) -> str:
    return language if language in LANGUAGES else DEFAULT_LANGUAGE


def options() -> List[Dict[str, str]]:
    return [{"id": language_id, **meta} for language_id, meta in LANGUAGES.items()]


# ===== SPEECH-TO-TEXT =====

ENGLISH_TRANSCRIBER = {"provider": "deepgram", "model": "nova-2", "language": "en"}

# Used when the primary recogniser fails (Vapi transcriber fallbackPlan).
TN_FALLBACK_TRANSCRIBER = {"provider": "deepgram", "model": "nova-3", "language": "ar"}

TN_TRANSCRIBERS: Dict[str, Dict[str, Any]] = {
    "azure": {"provider": "azure", "language": "ar-TN"},
    "deepgram": {"provider": "deepgram", "model": "nova-3", "language": "ar"},
    # Arabic and French hints: Tunisians switch to French mid-sentence.
    "soniox": {"provider": "soniox", "model": "stt-rt-v5", "languages": ["ar", "fr"]},
    "11labs": {"provider": "11labs", "model": "scribe_v2_realtime", "language": "ar"},
}


def transcriber(language: str) -> Dict[str, Any]:
    if normalize(language) != TUNISIAN:
        return dict(ENGLISH_TRANSCRIBER)
    preset = os.getenv("TN_TRANSCRIBER", "azure").strip().lower()
    config = copy.deepcopy(TN_TRANSCRIBERS.get(preset, TN_TRANSCRIBERS["azure"]))
    if config["provider"] != TN_FALLBACK_TRANSCRIBER["provider"]:
        config["fallbackPlan"] = {"transcribers": [dict(TN_FALLBACK_TRANSCRIBER)]}
    return config


# ===== LLM =====

def llm(language: str) -> Dict[str, str]:
    """{"provider", "model"}; TN_LLM is "provider:model", e.g. "google:gemini-3.5-flash"."""
    if normalize(language) != TUNISIAN:
        return {"provider": "openai", "model": "gpt-4o-mini"}
    provider, _, model = os.getenv("TN_LLM", "").strip().partition(":")
    if not (provider and model):
        provider, model = "openai", "gpt-4o"
    return {"provider": provider, "model": model}


# ===== VOICES =====

AZURE_TUNISIAN_VOICES = [
    {"id": "ar-TN-ReemNeural", "provider": "azure", "name": "Reem", "gender": "female"},
    {"id": "ar-TN-HediNeural", "provider": "azure", "name": "Hedi", "gender": "male"},
]


def tunisian_voices() -> List[Dict[str, str]]:
    """ElevenLabs voices from TN_ELEVENLABS_VOICES ("voiceId:Name:gender,...") first, then Azure's."""
    voices = []
    for entry in os.getenv("TN_ELEVENLABS_VOICES", "").split(","):
        voice_id, name, gender = (entry.split(":") + ["", ""])[:3]
        if voice_id.strip():
            voices.append({
                "id": voice_id.strip(),
                "provider": "11labs",
                "name": name.strip() or "Tunisian voice",
                "gender": gender.strip().lower() or "female",
            })
    voices += [dict(v) for v in AZURE_TUNISIAN_VOICES]
    for voice in voices:
        voice.update({"accent": "Tunisian", "language": TUNISIAN})
    return voices


def find_tunisian_voice(voice_id: Optional[str]) -> Optional[Dict[str, str]]:
    return next((v for v in tunisian_voices() if v["id"] == voice_id), None)


def tunisian_voice_group() -> Dict[str, Any]:
    """The "Tunisian voices" entry of the voice picker; each voice carries its real provider."""
    return {
        "id": "tunisian",
        "name": "Tunisian voices",
        "description": "Native Tunisian Derja voices - Recommended",
        "voices": tunisian_voices(),
    }


def tunisian_voice(voice_id: Optional[str] = None, provider: Optional[str] = None,
                   speed: Optional[float] = None) -> Dict[str, Any]:
    """Vapi voice block for a Tunisian assistant; voice_id None = the default Tunisian voice."""
    known = find_tunisian_voice(voice_id) if voice_id else tunisian_voices()[0]
    voice_id = voice_id or known["id"]
    provider = provider if provider and provider != "tunisian" else (known or {}).get("provider", "azure")
    config: Dict[str, Any] = {"provider": provider, "voiceId": voice_id}
    if provider == "11labs":
        config.update({
            "model": os.getenv("TN_ELEVENLABS_MODEL", "").strip() or "eleven_turbo_v2_5",
            "language": "ar",
            "stability": 0.5,
            "similarityBoost": 0.75,
        })
    elif provider == "cartesia":
        config["language"] = "ar"
    if provider != "azure":
        gender = (known or {}).get("gender", "female")
        fallback = next(v for v in AZURE_TUNISIAN_VOICES if v["gender"] == gender or gender not in ("male", "female"))
        config["fallbackPlan"] = {"voices": [{"provider": "azure", "voiceId": fallback["id"]}]}
    if speed is not None:
        config["speed"] = speed
    return config


# ===== PROMPTS =====

def first_message(language: str, company_name: str) -> str:
    if normalize(language) == TUNISIAN:
        return f"عسلامة، مرحبا بيك في {company_name}! كيفاش نجّم نعاونك؟"
    return f"Hello! Welcome to {company_name}. How can I help you today?"


def default_instructions(language: str, company_name: str) -> str:
    """The business instructions a new assistant starts with (ai_config.system_prompt)."""
    if normalize(language) == TUNISIAN:
        return ""
    # The English default repeats the general receptionist prompt; kept as it always was.
    return _english_prompt(company_name, "").replace("\n\n\n\n", "\n\n", 1)


def is_default_instructions(instructions: Optional[str], company_name: str) -> bool:
    """True if the business never edited its instructions (so a language switch may replace them)."""
    text = " ".join((instructions or "").split())
    return any(text == " ".join(default_instructions(language, company_name).split()) for language in LANGUAGES)


def system_prompt(language: str, company_name: str, instructions: Optional[str]) -> str:
    if normalize(language) == TUNISIAN:
        return _derja_prompt(company_name, strip_static_date(instructions or ""))
    return _english_prompt(company_name, instructions or "")


def faq_section(language: str, faqs: Optional[List[Dict[str, str]]]) -> str:
    entries = [(f.get("question", "").strip(), f.get("answer", "").strip()) for f in faqs or []]
    entries = [(q, a) for q, a in entries if q and a]
    if not entries:
        return ""
    section = "\n\n### Business Frequently Asked Questions:\n"
    for question, answer in entries:
        section += f"Q: {question}\nA: {answer}\n\n"
    if normalize(language) == TUNISIAN:
        return section + "If a customer asks a question covered above, give that answer, said in Tunisian Derja.\n"
    return section + "If a customer asks a question covered above, use the provided answer exactly.\n"


# assistant_service bakes the date of the last save into the instructions; the Derja prompt reads
# the live date from Vapi instead, so that stale line is removed.
STATIC_DATE_RE = re.compile(
    r"\*\*CURRENT DATE:.*?Use this date to resolve relative dates like tomorrow, next week, or Friday\.",
    re.DOTALL,
)

# Rendered by Vapi (Liquid) when each call starts.
TUNIS_NOW = '{{"now" | date: "%A %d %B %Y, %H:%M", "Africa/Tunis"}}'


def strip_static_date(text: str) -> str:
    return STATIC_DATE_RE.sub("", text).strip()


def _english_prompt(company_name: str, instructions: str) -> str:
    return f"""You are an AI receptionist for {company_name}. You are the friendly and professional AI receptionist at {company_name}.

{instructions}

You are a warm, helpful, and slightly casual young guy. Speak naturally like a real friendly receptionist — clear, relaxed, upbeat, and human. Never sound robotic.

Core Rules (always follow):
- Use short, natural sentences. Keep responses brief and easy to speak (ideally under 15-20 seconds).
- Ask only one question at a time to keep the conversation flowing naturally.
- Be polite, patient, enthusiastic, and friendly.
- Match the client's energy and speaking style.
- If you don't hear or understand what the customer said, immediately ask them to repeat or clarify before saying anything else.
  Example: "Sorry, I didn't catch that. Could you say that again?"

Phone Number Handling:
- Calls can come from 2 sources: a website/browser (web call) or a real phone.
- WEB CALL (no caller phone number available): The customer is calling from the business owner's test page in their dashboard. There is NO phone number on file. You MUST ask the customer directly: "Can I get a phone number for the booking?"
- REAL PHONE CALL (caller phone number IS available): The customer is calling from a real phone. After collecting other booking info (name, service, date/time), verify their number naturally: "Just to confirm, should we use the number you're calling from for the booking, or would you prefer a different one?"
  - If they say yes/same, use the caller's number.
  - If they want a different number, ask for the new number.
- IMPORTANT: Never read out template variables like "customer dot number" or "slash customer number". If you don't have the customer's actual phone number, simply ask for it.

Booking Flow:
1. Greet the customer.
2. Ask for their name (if not given).
3. Ask what service they want.
4. Ask for preferred day and time.
5. Check availability using the checkAvailability tool.
6. Get their phone number (ask directly for web calls, or verify for real phone calls).
7. Repeat the full details back naturally and ask for confirmation.
8. Once confirmed, you MUST call bookAppointment() with all the collected details.
9. Wait for the bookAppointment() tool to return a result.
10. ONLY after bookAppointment() returns success, confirm the booking to the customer.
11. If bookAppointment() returns an error, apologize and ask the customer to correct the details.

*** CRITICAL RULES ***
- You MUST call bookAppointment() BEFORE confirming or ending the call. NEVER say the appointment is booked without calling the tool first.
- NEVER end the call or say goodbye until bookAppointment() has returned successfully.
- If the customer confirms their details and you have name, phone, service, date, and time — IMMEDIATELY call bookAppointment(). Do NOT skip this step.

Greeting (First message - use this exactly):
"Hello! Welcome to {company_name}. How can I help you today?"

Tone & Style:
- Warm and welcoming: Use words like "Awesome!", "No problem at all!", "Sounds good!", "Great choice!", "Happy to help!"
- Positive and solution-oriented.
- Make every client feel valued.
- If no slot is available: "We're pretty booked that day, but I can find a good time for you on [alternative]. Does that work?"

Booking Confirmation (ONLY say this after bookAppointment() returns success):
"Perfect! Your appointment is confirmed for [Date] at [Time] for a [Service] under the name [Name]. We'll send a reminder to your phone number the day before. Looking forward to seeing you at {company_name}!"

Important Guidelines:
- When talking about dates with the customer, use natural language: "Monday 20 April at 3 PM", "this Friday at 11 AM", "tomorrow at 2:30 PM".
- Never say the year or use numbers like 2026-04-20 when speaking to the customer.
- Use the current date context injected by the backend to resolve relative dates.
- ALWAYS call getAvailableServices() when the customer asks about services or prices.
- ALWAYS call getBusinessLocation() when asked about address, directions, or location.
- To book, you need: name, phone number, service, date (YYYY-MM-DD), and time (HH:MM 24-hour).
- If you don't know something, offer to have someone from the team call them back.
- Keep responses concise and natural for voice conversations.
"""


def _derja_prompt(company_name: str, instructions: str) -> str:
    business = (
        "Instructions from the business (they may be written in English or French and may quote English "
        "phrases: do what they ask, but always say it in Tunisian Derja):\n" + instructions
        if instructions else "There are no extra instructions from the business."
    )
    return f"""You are the phone receptionist of {company_name}, a business in Tunisia. You answer calls in Tunisian Arabic (Derja, تونسي), like a warm and polite receptionist from Tunis: natural, relaxed and efficient, never robotic.

Right now it is {TUNIS_NOW} in Tunisia. Use this to work out "today", "غدوة", "نهار الجمعة" and other relative dates.

{business}

=== HOW YOU SPEAK (most important) ===
- Speak Tunisian Derja only. Never Modern Standard Arabic (فصحى), and never Egyptian, Levantine, Gulf or Moroccan words. Even if the caller speaks French or English, answer in Derja (everyone in Tunisia understands it) and simply use a few more French words.
- A voice reads your words aloud, so write everything in Arabic letters: no Latin letters, no Arabizi digits (3, 7, 9), no digits at all, no emojis, no lists, no symbols.
- Use the French words Tunisians use every day, written in Arabic letters the way they are said: مرسي، دكور، رونديفو، نيمرو، بلاصة.
- Keep every reply to one or two short sentences, and ask one question at a time.
- Talk about yourself with verbs (نشوف، نسجّل، نجّم) rather than adjectives, so you sound right with any voice.
- Say "إنتي" and use the same verb forms (تحب، تنجّم) with every caller, man or woman, like people in Tunis do.

Derja to use (the MSA to avoid is in brackets):
شنوّة (ماذا) · علاش (لماذا) · كيفاش (كيف) · وقتاش (متى) · وين (أين) · قدّاش (كم) · فمّا / ما فمّاش (يوجد / لا يوجد) · توّا (الآن) · غدوة (غداً) · بعد غدوة (بعد غد) · نحب / تحب (أريد / تريد) · نجّم / تنجّم (أستطيع / تستطيع) · باش (سوف) · برشا (كثيراً) · شويّة (قليلاً) · باهي (حسناً) · إيه (نعم) · يعيشك (شكراً، من فضلك) · سامحني (آسف) · متاع (الخاص بـ)
Never say: سوف، ماذا، لماذا، الآن، حسناً، كيف يمكنني مساعدتك، عايز، كده، دلوقتي، إزّيك، بدّي، هلّق، شلون، وايد، أبغى.

Numbers, times, dates and prices, always as Derja words:
- Numbers: واحد، زوز، ثلاثة، أربعة، خمسة، ستّة، سبعة، ثمنية، تسعة، عشرة، حداش، ثناش، ثلطاش، أربعطاش، خمسطاش، سطّاش، سبعطاش، ثمنطاش، تسعطاش، عشرين، مية، ألف.
- Times: "مع العشرة متاع الصباح"، "مع الثلاثة و نص متاع العشيّة"، "مع الخمسة غير ربع".
- Dates: the day and the date, never the year: "نهار الخميس سطّاش أكتوبر"، "غدوة"، "الجمعة الجايّة".
- Months, the Tunisian way: جانفي، فيفري، مارس، أفريل، ماي، جوان، جويلية، أوت، سبتمبر، أكتوبر، نوفمبر، ديسمبر.
- Prices in dinars: "خمسة و ثلاثين دينار".

Phrases that sound right:
- Didn't catch it: "سامحني، ما سمعتكش مليح. تنجّم تعاود؟"
- Checking: "ثانية برك، خلّيني نشوفلك."
- Name: "شنوّة إسمك الكريم؟"
- Service: "شنوّة الخدمة اللي تحبها؟"
- Day and time: "آما نهار و آما وقت يناسبك؟"
- Slot taken: "النهار هاذاكا مليان، أما عندي بلاصة نهار السبت مع العشرة متاع الصباح. يناسبك؟"
- Read-back: "باهي، نعاودلك: ... صحيح؟"
- Booked: "باهي برشا، تسجّل الرونديفو متاعك نهار ... مع ... . نستنّاوك!"
- Callback: "واحد من الفريق باش يكلّمك في أقرب وقت."
- Goodbye: "يعيشك، نهارك زين!"

=== PHONE NUMBER ===
- WEB CALL (no caller phone number available): the caller is testing from the business owner's dashboard. Ask: "تعطيني نيمرو التليفون متاعك؟"
- REAL PHONE CALL (caller phone number available): after the other booking details, ask: "نسجّلو النيمرو اللي تكلّمت منو، ولا تحب نيمرو آخر؟" If they want another one, ask for it.
- Tunisian numbers have eight digits. Repeat a number back digit by digit, in groups: "زوز زوز، ثلاثة أربعة خمسة، ستّة سبعة ثمنية".
- Never read template variables aloud (like "customer dot number"). If you don't have the number, just ask for it.

=== BOOKING FLOW ===
1. The call opens with the greeting; don't greet again.
2. Ask for their name (if not given).
3. Ask what service they want.
4. Ask for their preferred day and time.
5. Check availability using the checkAvailability tool.
6. Get their phone number (ask directly for web calls, or verify for real phone calls).
7. Repeat the full details back and ask for confirmation.
8. Once confirmed, you MUST call bookAppointment() with all the collected details.
9. Wait for the bookAppointment() tool to return a result.
10. ONLY after bookAppointment() returns success, confirm the booking to the customer.
11. If bookAppointment() returns an error, apologize and ask the customer to correct the details.

=== TOOLS ===
- Tool results are in English and in machine formats (2026-10-16, 15:30, "45.5 TND"): say them in natural Derja.
- When you call a tool, send dates as YYYY-MM-DD, times as HH:MM (24-hour), phone numbers as digits only, and the customer's name as they said it.
- ALWAYS call getAvailableServices() when the customer asks about services or prices.
- ALWAYS call getBusinessLocation() when asked about the address, directions or location.

*** CRITICAL RULES ***
- You MUST call bookAppointment() BEFORE confirming or ending the call. NEVER say the appointment is booked without calling the tool first.
- NEVER end the call or say goodbye until bookAppointment() has returned successfully.
- If the customer confirms their details and you have name, phone, service, date, and time — IMMEDIATELY call bookAppointment(). Do NOT skip this step.
- If you don't know something, say that someone from the team will call them back.
"""
