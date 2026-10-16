"""
Cold-email outreach for Calleem: sends a 3-step email sequence from a Gmail account and stops
for anyone who replies, bounces, or asks to be left alone.

Setup (once):
  1. Turn on 2-Step Verification on the Google account, then create an App Password at
     https://myaccount.google.com/apppasswords (Gmail refuses scripts that use the normal password).
  2. python scripts/outreach/send_outreach.py init --email you@gmail.com
     then fill in scripts/outreach/data/config.json. The postal address is required: US law
     (CAN-SPAM) needs one in every commercial email, so `send` refuses to run without it.
  3. Put prospects in scripts/outreach/data/leads.csv. Columns used: business_name, email,
     owner_first_name, city, trade, opener (an email-ready first sentence about that business),
     voicemail_at (fill ONLY if you really called and got voicemail, e.g. "at 7:40am on Tuesday").
     Extra columns are ignored; rows without an email are skipped.

Every day (PowerShell):
  $env:GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
  python scripts/outreach/send_outreach.py preview    # what would go out today; nothing is sent
  python scripts/outreach/send_outreach.py send       # checks replies, then sends follow-ups and new emails

Other commands:
  test --to you@example.com   send the 3 emails for the first lead to yourself, to check how they look
  status                      who was contacted, replied, bounced, or is due a follow-up
  stop someone@example.com    never email this address again
  record x@example.com --subject "..." [--message-id "<id@mail.gmail.com>"]
                              log an email sent another way (e.g. from Gmail itself) so follow-ups include it

Everything under scripts/outreach/data/ stays local (it is git-ignored): config, leads, and the
send log the script uses to know who got which email.
"""

import argparse
import csv
import getpass
import imaplib
import json
import os
import random
import re
import smtplib
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

DATA_DIR = Path(__file__).resolve().parent / "data"
CONFIG_PATH = DATA_DIR / "config.json"
LEADS_PATH = DATA_DIR / "leads.csv"
LOG_PATH = DATA_DIR / "sent_log.csv"
STOP_PATH = DATA_DIR / "do_not_contact.txt"
PREVIEW_PATH = DATA_DIR / "preview.txt"

# Prospects are in Dallas-Fort Worth: send on their weekdays, 6am-6pm their time.
RECIPIENT_TZ = ZoneInfo("America/Chicago")
SEND_HOURS = (6, 18)
# Days to wait after the previous email before each follow-up (email 3 lands about a week after email 1).
FOLLOW_UP_DAYS = {2: 3, 3: 4}
LAST_STEP = 3

LEAD_FIELDS = ["business_name", "email", "owner_first_name", "city", "trade", "opener", "voicemail_at"]
LOG_FIELDS = ["email", "business_name", "event", "step", "at", "message_id", "subject"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
BUSINESS_SUFFIX_RE = re.compile(r",?\s+(LLC|L\.L\.C\.|Inc\.?|Co\.?|Corp\.?|Company|Ltd\.?)$", re.IGNORECASE)

DEFAULT_CONFIG = {
    "sender_email": "",
    "from_name": "Montassar from Calleem",
    "signature_name": "Montassar",
    "signature_title": "Founder, Calleem",
    "website": "calleem.tech",
    "phone": "",
    "demo_number": "",
    "postal_address": "",
    "trial_days": 14,
    "daily_limit": 25,
    "delay_seconds": [45, 120],
}


# ===== DATA =====

@dataclass
class Lead:
    email: str
    business_name: str
    first_name: str = ""
    city: str = ""
    trade: str = ""
    opener: str = ""
    voicemail_at: str = ""


@dataclass
class History:
    """What has happened with one address, rebuilt from the send log."""
    sent: Dict[int, Tuple[datetime, str, str]] = field(default_factory=dict)  # step -> (at, message_id, subject)
    replied: bool = False
    bounced: bool = False

    @property
    def last_step(self) -> int:
        return max(self.sent) if self.sent else 0


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(f"No config yet. Run: python {Path(__file__).name} init --email you@gmail.com")
    config = {**DEFAULT_CONFIG, **json.loads(CONFIG_PATH.read_text(encoding="utf-8"))}
    if not EMAIL_RE.match(config["sender_email"]):
        sys.exit(f"Set sender_email in {CONFIG_PATH}")
    return config


def load_leads() -> List[Lead]:
    if not LEADS_PATH.exists():
        sys.exit(f"No leads file at {LEADS_PATH}")
    leads: Dict[str, Lead] = {}
    with LEADS_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            email = row.get("email", "").lower()
            if not EMAIL_RE.match(email) or email in leads:
                continue
            leads[email] = Lead(
                email=email,
                business_name=row.get("business_name", ""),
                first_name=row.get("owner_first_name", ""),
                city=row.get("city", ""),
                trade=row.get("trade", ""),
                opener=row.get("opener", ""),
                voicemail_at=row.get("voicemail_at", ""),
            )
    return list(leads.values())


def load_stop_list() -> set:
    if not STOP_PATH.exists():
        return set()
    return {line.strip().lower() for line in STOP_PATH.read_text(encoding="utf-8").splitlines() if line.strip()}


def load_history() -> Dict[str, History]:
    history: Dict[str, History] = {}
    if not LOG_PATH.exists():
        return history
    with LOG_PATH.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            h = history.setdefault(row["email"], History())
            if row["event"] == "sent":
                h.sent[int(row["step"])] = (datetime.fromisoformat(row["at"]), row["message_id"], row["subject"])
            elif row["event"] == "replied":
                h.replied = True
            elif row["event"] == "bounced":
                h.bounced = True
    return history


def log_event(lead: Lead, event: str, step: int = 0, message_id: str = "", subject: str = "") -> None:
    """Append one event and flush right away, so a crash mid-run never causes a double send."""
    new_file = not LOG_PATH.exists()
    with LOG_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow({
            "email": lead.email,
            "business_name": lead.business_name,
            "event": event,
            "step": step,
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "message_id": message_id,
            "subject": subject,
        })


# ===== EMAIL CONTENT =====

def short_name(business_name: str) -> str:
    return BUSINESS_SUFFIX_RE.sub("", business_name).strip() or business_name


def trade_details(trade: str) -> Tuple[str, str, str]:
    """(what they do, where they are when the phone rings, a demo scenario) for the trade column."""
    t = trade.lower()
    has_plumbing, has_hvac = "plumb" in t, ("hvac" in t or "heat" in t or "air" in t)
    if has_plumbing and not has_hvac:
        return "plumbing", "under a sink", "you have a burst pipe"
    if has_hvac and not has_plumbing:
        return "HVAC", "up in an attic", "your heater just quit"
    return "plumbing and HVAC", "on a job", "you have a burst pipe"


def trial_phrase(days: int) -> str:
    return "2 weeks" if days == 14 else f"{days} days"


def step_content(step: int, lead: Lead, config: dict) -> Tuple[str, List[str], str]:
    """Subject, paragraphs and an optional P.S. for one email: short and plain, like a note from one person."""
    biz = short_name(lead.business_name)
    hello = f"Hi {lead.first_name}," if lead.first_name else "Hi there,"
    trades, busy_spot, scenario = trade_details(lead.trade)
    subject = f"tried calling {biz}" if lead.voicemail_at else f"question about {biz}"

    if step == 1:
        if lead.voicemail_at:
            opening = [f"I called {biz} {lead.voicemail_at} and got voicemail. No worries, you were probably on a job."]
        else:
            where = f" in {lead.city}" if lead.city else ""
            opening = [lead.opener or f"Came across {biz} while looking at {trades} companies{where}.",
                       f"Curious, who picks up when you're {busy_spot} and the phone rings?"]
        pitch = ("I built an AI receptionist that answers those calls, checks if it's an emergency and books the job. "
                 f"Happy to set it up free for {biz} for {trial_phrase(config['trial_days'])}.")
        demo = config.get("demo_number")
        postscript = f"P.S. You can hear it at {demo}, just pretend {scenario}." if demo else ""
        return subject, [hello, *opening, pitch, "Worth a try?"], postscript

    if step == 2:
        return f"Re: {subject}", [
            hello,
            "One thing I should have mentioned: since October 1, Google charges Local Services Ads for "
            "business-hours calls nobody picks up. If you run those ads, a missed call now costs you twice.",
            "Want me to set it up so that doesn't happen?",
        ], ""

    return f"Re: {subject}", [
        hello,
        "I'll stop here, I know you're busy. If missed calls ever become a headache, just reply and I'll set you up.",
    ], ""


OPT_OUT = "Not interested? Just reply \"no\" and I won't email again."


def compose(step: int, lead: Lead, config: dict) -> Tuple[str, str]:
    """Subject and plain-text body. No HTML, images or tracking: it should read like a personal email, not an ad."""
    subject, paragraphs, postscript = step_content(step, lead, config)
    signature = config["signature_name"] + "\n" + " | ".join(
        x for x in [config["signature_title"], config["website"], config.get("phone", "")] if x)
    parts = [*paragraphs, signature] + ([postscript] if postscript else [])
    # CAN-SPAM needs a postal address and a way to opt out in every email: one quiet line at the bottom.
    address = config.get("postal_address", "").strip().rstrip(".")
    parts.append(f"{address}. {OPT_OUT}" if address else OPT_OUT)
    return subject, "\n\n".join(parts) + "\n"


def build_message(config: dict, to_addr: str, subject: str, text: str, reply_to_id: str = "") -> EmailMessage:
    msg = EmailMessage()
    sender = config["sender_email"]
    msg["From"] = formataddr((config["from_name"], sender))
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=sender.split("@")[1])
    # A one-click way out keeps spam complaints (and Gmail's penalties for them) down.
    msg["List-Unsubscribe"] = f"<mailto:{sender}?subject=unsubscribe>"
    if reply_to_id.startswith("<"):
        # Follow-ups thread under the first email in the prospect's inbox. (Emails sent from Gmail
        # itself are logged with their Gmail thread ID instead, which is no use as a header.)
        msg["In-Reply-To"] = reply_to_id
        msg["References"] = reply_to_id
    msg.set_content(text)
    return msg


# ===== PLANNING =====

def recipient_today() -> date:
    return datetime.now(RECIPIENT_TZ).date()


def days_since(at: datetime) -> int:
    return (recipient_today() - at.astimezone(RECIPIENT_TZ).date()).days


def sent_today(history: Dict[str, History]) -> int:
    today = recipient_today()
    return sum(
        1 for h in history.values() for at, _, _ in h.sent.values() if at.astimezone(RECIPIENT_TZ).date() == today
    )


def plan(leads: List[Lead], history: Dict[str, History], stopped: set) -> List[Tuple[Lead, int]]:
    """Emails due today: follow-ups first (they convert best), then first emails to new leads."""
    follow_ups, first_emails = [], []
    for lead in leads:
        h = history.get(lead.email)
        if lead.email in stopped or (h and (h.replied or h.bounced)):
            continue
        if not h or not h.sent:
            first_emails.append((lead, 1))
            continue
        step = h.last_step + 1
        if step <= LAST_STEP and days_since(h.sent[h.last_step][0]) >= FOLLOW_UP_DAYS[step]:
            follow_ups.append((lead, step))
    return follow_ups + first_emails


def in_send_window() -> bool:
    now = datetime.now(RECIPIENT_TZ)
    return now.weekday() < 5 and SEND_HOURS[0] <= now.hour < SEND_HOURS[1]


# ===== GMAIL =====

def app_password() -> str:
    password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    if not password and sys.stdin.isatty():
        password = getpass.getpass("Gmail App Password: ").replace(" ", "")
    if not password:
        sys.exit("Set GMAIL_APP_PASSWORD (a Google App Password, not your normal password).")
    return password


class Mailer:
    """One SMTP connection for the run, reopened if Gmail drops it between delayed sends."""

    def __init__(self, sender: str, password: str):
        self.sender, self.password, self.smtp = sender, password, None

    def _connect(self):
        self.smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60)
        self.smtp.login(self.sender, self.password)

    def send(self, msg: EmailMessage) -> None:
        if self.smtp is None:
            self._connect()
        try:
            self.smtp.send_message(msg)
        except smtplib.SMTPServerDisconnected:
            self._connect()
            self.smtp.send_message(msg)

    def close(self):
        if self.smtp is not None:
            try:
                self.smtp.quit()
            except smtplib.SMTPException:
                pass


def all_mail_folder(imap: imaplib.IMAP4_SSL) -> str:
    """Gmail's "All Mail" folder (its name is translated in non-English accounts), so archived replies count."""
    _, folders = imap.list()
    for raw in folders or []:
        line = raw.decode(errors="replace")
        if "\\All" in line:
            match = re.search(r'"([^"]+)"\s*$', line)
            if match:
                return f'"{match.group(1)}"'
    return "INBOX"


def check_replies(config: dict, password: str, leads: List[Lead], history: Dict[str, History]) -> None:
    """Log replies and bounces for everyone mid-sequence, so nobody gets a follow-up after answering."""
    active = [l for l in leads if (h := history.get(l.email)) and h.sent and not h.replied and not h.bounced]
    if not active:
        return
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        imap.login(config["sender_email"], password)
        imap.select(all_mail_folder(imap), readonly=True)
        for lead in active:
            h = history[lead.email]
            since = (min(at for at, _, _ in h.sent.values()) - timedelta(days=1)).strftime("%Y/%m/%d")
            for event, query in (("replied", f"from:{lead.email} after:{since}"),
                                 ("bounced", f"from:mailer-daemon {lead.email} after:{since}")):
                _, data = imap.search(None, "X-GM-RAW", f'"{query}"')
                if data and data[0].split():
                    log_event(lead, event)
                    setattr(h, event, True)
                    print(f"  {event.upper():8} {lead.business_name} <{lead.email}>")
                    break
    finally:
        try:
            imap.logout()
        except imaplib.IMAP4.error:
            pass


# ===== COMMANDS =====

def cmd_init(args) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        print(f"Config already exists: {CONFIG_PATH}")
    else:
        CONFIG_PATH.write_text(json.dumps({**DEFAULT_CONFIG, "sender_email": args.email or ""}, indent=2) + "\n",
                               encoding="utf-8")
        print(f"Created {CONFIG_PATH}. Fill in postal_address (required), phone and demo_number.")
    if not LEADS_PATH.exists():
        with LEADS_PATH.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(LEAD_FIELDS)
        print(f"Created {LEADS_PATH}")
    STOP_PATH.touch(exist_ok=True)


def cmd_preview(args) -> None:
    config, leads, history = load_config(), load_leads(), load_history()
    due = plan(leads, history, load_stop_list())
    room = max(config["daily_limit"] - sent_today(history), 0)
    print(f"{len(leads)} leads with an email | {len(due)} emails due | {room} left in today's limit of "
          f"{config['daily_limit']}")
    if not config.get("postal_address"):
        print("! postal_address is empty in config.json: `send` will refuse to run until it is filled in.")
    rendered = []
    for lead, step in due[:room]:
        subject, text = compose(step, lead, config)
        rendered.append(f"=== Email {step} to {lead.business_name} <{lead.email}>\nSubject: {subject}\n\n{text}")
    PREVIEW_PATH.write_text("\n".join(rendered), encoding="utf-8")
    for text in rendered[:args.show]:
        print("\n" + text)
    if rendered:
        print(f"All {len(rendered)} emails written to {PREVIEW_PATH}")


def cmd_test(args) -> None:
    config, leads = load_config(), load_leads()
    lead = next((l for l in leads if l.email == (args.lead or "").lower()), None) if args.lead else None
    lead = lead or (leads[0] if leads else Lead(email=args.to, business_name="Example Plumbing LLC",
                                                first_name="Mike", city="Dallas", trade="plumbing"))
    mailer = Mailer(config["sender_email"], app_password())
    try:
        first_id = ""
        for step in range(1, LAST_STEP + 1):
            subject, text = compose(step, lead, config)
            msg = build_message(config, args.to, f"[TEST] {subject}", text, first_id)
            mailer.send(msg)
            first_id = first_id or msg["Message-ID"]
            print(f"Sent test email {step} ({lead.business_name}) to {args.to}")
    finally:
        mailer.close()


def cmd_send(args) -> None:
    config = load_config()
    if not config.get("postal_address"):
        sys.exit(f"Fill in postal_address in {CONFIG_PATH} first: US law requires it in every cold email.")
    if not in_send_window() and not args.anytime:
        now = datetime.now(RECIPIENT_TZ).strftime("%a %H:%M")
        sys.exit(f"It's {now} in Dallas. Emails go out on weekdays {SEND_HOURS[0]}:00-{SEND_HOURS[1]}:00 "
                 f"Dallas time (best: 7-9am, which is early afternoon in Tunisia). Use --anytime to override.")
    leads, history = load_leads(), load_history()
    password = app_password()

    print("Checking Gmail for replies and bounces...")
    check_replies(config, password, leads, history)

    limit = config["daily_limit"] if args.limit is None else min(args.limit, config["daily_limit"])
    room = max(limit - sent_today(history), 0)
    due = plan(leads, history, load_stop_list())[:room]
    if not due:
        print("Nothing to send right now.")
        return
    print(f"Sending {len(due)} emails, {config['delay_seconds'][0]}-{config['delay_seconds'][1]}s apart. "
          "Ctrl+C stops safely.")
    mailer = Mailer(config["sender_email"], password)
    try:
        for i, (lead, step) in enumerate(due):
            if i:
                time.sleep(random.uniform(*config["delay_seconds"]))
            subject, text = compose(step, lead, config)
            h = history.get(lead.email)
            first_id = h.sent[1][1] if h and 1 in h.sent else ""
            msg = build_message(config, lead.email, subject, text, first_id)
            mailer.send(msg)
            log_event(lead, "sent", step, msg["Message-ID"], subject)
            print(f"  [{i + 1}/{len(due)}] email {step} -> {lead.business_name} <{lead.email}>")
    except KeyboardInterrupt:
        print("Stopped. Everything sent so far is logged.")
    finally:
        mailer.close()


def cmd_status(args) -> None:
    leads, history, stopped = load_leads(), load_history(), load_stop_list()
    by_email = {l.email: l for l in leads}
    replied = [e for e, h in history.items() if h.replied]
    bounced = [e for e, h in history.items() if h.bounced]
    contacted = [e for e, h in history.items() if h.sent]
    print(f"Leads with email: {len(leads)} | contacted: {len(contacted)} | replied: {len(replied)} | "
          f"bounced: {len(bounced)} | stopped: {len(stopped)} | sent today: {sent_today(history)}")
    for title, emails in (("Replied (answer these yourself)", replied), ("Bounced", bounced)):
        if emails:
            print(f"\n{title}:")
            for e in emails:
                print(f"  {by_email[e].business_name if e in by_email else ''} <{e}>")
    due = plan(leads, history, stopped)
    print(f"\nDue now: {sum(1 for _, s in due if s > 1)} follow-ups, {sum(1 for _, s in due if s == 1)} first emails")


def cmd_record(args) -> None:
    """Log an email that went out another way (e.g. from Gmail itself), so follow-ups and reply checks include it."""
    lead = next((l for l in load_leads() if l.email == args.email.strip().lower()), None)
    if lead is None:
        sys.exit(f"{args.email} is not in {LEADS_PATH}")
    log_event(lead, "sent", args.step, args.message_id, args.subject)
    print(f"Recorded email {args.step} to {lead.business_name} <{lead.email}>")


def cmd_stop(args) -> None:
    email = args.email.strip().lower()
    if email in load_stop_list():
        print(f"{email} is already on the do-not-contact list")
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with STOP_PATH.open("a", encoding="utf-8") as f:
        f.write(email + "\n")
    print(f"{email} will never be emailed again")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Calleem cold-email outreach")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init", help="create data/config.json, data/leads.csv and the do-not-contact list")
    p.add_argument("--email", help="the Gmail address you send from")
    p.set_defaults(func=cmd_init)
    p = sub.add_parser("preview", help="show today's emails without sending anything")
    p.add_argument("--show", type=int, default=3, help="how many to print in full (all go to data/preview.txt)")
    p.set_defaults(func=cmd_preview)
    p = sub.add_parser("test", help="send the 3-email sequence for one lead to yourself")
    p.add_argument("--to", required=True)
    p.add_argument("--lead", help="email of the lead to render (default: the first one)")
    p.set_defaults(func=cmd_test)
    p = sub.add_parser("send", help="check replies, then send due follow-ups and new emails")
    p.add_argument("--limit", type=int, help="send at most this many today (the config daily_limit still applies)")
    p.add_argument("--anytime", action="store_true", help="ignore the Dallas business-hours window")
    p.set_defaults(func=cmd_send)
    sub.add_parser("status", help="contacted / replied / bounced / due").set_defaults(func=cmd_status)
    p = sub.add_parser("record", help="log an email sent outside this script, so its follow-ups still happen")
    p.add_argument("email")
    p.add_argument("--subject", required=True)
    p.add_argument("--step", type=int, default=1)
    p.add_argument("--message-id", default="", help="the email's Message-ID header, so follow-ups thread under it")
    p.set_defaults(func=cmd_record)
    p = sub.add_parser("stop", help="never email this address again")
    p.add_argument("email")
    p.set_defaults(func=cmd_stop)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
