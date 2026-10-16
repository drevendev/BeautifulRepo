"""Minimal checkout-only Python API for the library README starter."""
import re


def slugline(text: str) -> str:
    """Return an ASCII slug from an ASCII phrase, or raise ValueError.

    Non-ASCII input is rejected rather than silently stripped, to avoid
    presenting a lossy transliteration as an accurate conversion.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not text or any(ord(char) > 127 for char in text):
        raise ValueError("text must be nonempty ASCII")
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if not slug:
        raise ValueError("text needs at least one ASCII letter or digit")
    return slug
