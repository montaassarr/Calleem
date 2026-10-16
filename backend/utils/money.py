"""Prices as the assistants say them, in the business's currency (business_config.currency)."""


def format_price(amount: float, currency: str = "USD") -> str:
    """"$45.00" for dollars; otherwise the amount and currency code, e.g. "45.5 TND" (dinars have 3 decimals)."""
    currency = (currency or "USD").upper()
    if currency == "USD":
        return f"${amount:.2f}"
    return f"{amount:.3f}".rstrip("0").rstrip(".") + f" {currency}"
