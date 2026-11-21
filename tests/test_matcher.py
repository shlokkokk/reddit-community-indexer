"""Tests for inquiry matching and markdown formatting."""

from indexer.formatter import build_digest, format_contextual_reply
from indexer.matcher import is_opted_out, match_inquiry


CONFIG = {
    "opt_out": ["!optout", "!stop"],
    "documentation": {
        "python": {
            "title": "Python documentation",
            "url": "https://docs.python.org/3/",
        },
        "docker": {
            "title": "Docker documentation",
            "url": "https://docs.docker.com/",
        },
    },
}


def test_keyword_matching():
    matches = match_inquiry("Where can I find Python documentation?", CONFIG)
    assert matches == [{
        "key": "python",
        "title": "Python documentation",
        "url": "https://docs.python.org/3/",
    }]


def test_opt_out_detection():
    assert is_opted_out("Please !stop responding")
    assert is_opted_out("!OPTOUT", CONFIG["opt_out"])
    assert not is_opted_out("How do I install Docker?")


def test_matcher_respects_opt_out():
    assert match_inquiry("Python help !stop", CONFIG) == []


def test_markdown_formatting():
    matches = match_inquiry("Docker setup", CONFIG)
    reply = format_contextual_reply(matches)
    assert "[Docker documentation](https://docs.docker.com/)" in reply
    assert "!" in reply


def test_weekly_digest_formatting():
    digest = build_digest([{
        "title": "Python documentation",
        "url": "https://docs.python.org/3/",
        "count": 4,
    }])
    assert "# Weekly Community Knowledge Digest" in digest
    assert "4 references" in digest
