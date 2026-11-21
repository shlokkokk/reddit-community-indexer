"""Match community questions to configured documentation entries."""

import re
from typing import Iterable, Mapping, Optional


def is_opted_out(text: str, opt_out: Optional[Iterable[str]] = None) -> bool:
    """Return True when text contains an opt-out command."""
    tokens = opt_out if opt_out is not None else ("!optout", "!stop")
    lowered = text.lower()
    return any(str(token).lower() in lowered for token in tokens)


def match_inquiry(text: str, config: Mapping) -> list:
    """Find documentation entries mentioned or requested by text."""
    if not text or is_opted_out(text, config.get("opt_out")):
        return []

    for blocked in config.get("blacklist", []):
        if blocked and re.search(re.escape(str(blocked)), text, re.I):
            return []

    documentation = config.get("documentation", {})
    matches = []
    lowered = text.lower()

    for key, entry in documentation.items():
        title = str(entry.get("title", key))
        url = str(entry.get("url", ""))
        patterns = [re.escape(str(key)), re.escape(title)]
        patterns.extend(
            re.escape(str(trigger))
            for trigger in entry.get("keywords", [])
        )
        if url and any(re.search(r"\b" + pattern + r"\b", lowered, re.I)
                      for pattern in patterns):
            matches.append({"key": str(key), "title": title, "url": url})
    return matches


detect_opt_out = is_opted_out
find_matches = match_inquiry
