"""
Phone numbers in full international (E.164) form.

Callers often give a local number ("55 123 456", "(415) 555-0123"). Its country is taken from a
reference number: the number calling, else the business's own number.
"""

import re
from typing import Optional

import phonenumbers


def _region(number: Optional[str]) -> Optional[str]:
    try:
        region = phonenumbers.region_code_for_number(phonenumbers.parse(number or ""))
    except phonenumbers.NumberParseException:
        return None
    return region if region and region != "ZZ" else None


def to_e164(raw: Optional[str], *reference_numbers: Optional[str]) -> Optional[str]:
    """+<country><number> for raw, or None if it isn't a valid phone number."""
    raw = (raw or "").strip()
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None
    if raw.startswith("+"):
        candidates = [("+" + digits, None)]
    elif digits.startswith("00"):
        candidates = [("+" + digits[2:], None)]
    else:
        regions = [r for r in dict.fromkeys(_region(ref) for ref in reference_numbers) if r]
        # Local number in the caller's / business's country first, then the digits as a full number.
        candidates = [(digits, region) for region in regions] + [("+" + digits, None)]
    for text, region in candidates:
        try:
            number = phonenumbers.parse(text, region)
        except phonenumbers.NumberParseException:
            continue
        if phonenumbers.is_valid_number(number):
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
    return None
