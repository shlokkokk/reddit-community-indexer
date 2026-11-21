"""Configuration loading for reddit-community-indexer."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
import yaml


@dataclass(frozen=True)
class RedditCredentials:
    """Reddit OAuth credentials loaded from environment variables."""

    client_id: str
    client_secret: str
    user_agent: str


def load_config(path: str = "config/settings.yaml") -> Dict[str, Any]:
    """Load a YAML settings file and return its mapping."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            "Configuration not found at {}. Copy config/settings.example.yaml "
            "to config/settings.yaml.".format(config_path)
        )

    with config_path.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}
    if not isinstance(config, dict):
        raise ValueError("The settings file must contain a YAML mapping.")
    return config


def get_reddit_credentials() -> RedditCredentials:
    """Load Reddit OAuth credentials from .env or process environment."""
    load_dotenv()
    missing = [
        name
        for name in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT")
        if not os.getenv(name)
    ]
    if missing:
        raise EnvironmentError(
            "Missing required environment variables: {}".format(", ".join(missing))
        )
    return RedditCredentials(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ["REDDIT_USER_AGENT"],
    )


load_settings = load_config
get_credentials = get_reddit_credentials
