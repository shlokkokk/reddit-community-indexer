"""Markdown formatting for replies and weekly digests."""

from typing import Iterable, Mapping


def format_contextual_reply(matches: Iterable[Mapping]) -> str:
    """Build a concise markdown reference reply."""
    entries = list(matches)
    if not entries:
        return ""

    lines = [
        "Here are the official references that may help:",
        "",
    ]
    for entry in entries:
        lines.append("- [{title}]({url})".format(
            title=entry["title"], url=entry["url"]
        ))
    lines.append("")
    lines.append(
        "This link was selected from the community knowledge index. "
        "Reply `!optout` or `!stop` to opt out."
    )
    return "\n".join(lines)


def build_digest(entries: Iterable[Mapping], week_label: str = "Weekly") -> str:
    """Build a structured markdown community digest."""
    entries = list(entries)
    lines = ["# {} Community Knowledge Digest".format(week_label), ""]
    if not entries:
        lines.extend(["No matching community questions were found.", ""])
        return "\n".join(lines)

    lines.append("## Frequently Referenced Documentation")
    lines.append("")
    for entry in entries:
        count = entry.get("count")
        suffix = " — {} references".format(count) if count is not None else ""
        lines.append("- [{title}]({url}){suffix}".format(
            title=entry["title"], url=entry["url"], suffix=suffix
        ))
    lines.append("")
    return "\n".join(lines)


format_reply = format_contextual_reply
generate_digest = build_digest
