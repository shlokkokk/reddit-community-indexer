"""PRAW stream listener for reddit-community-indexer."""

from collections import deque
import time
from typing import Iterable, Mapping, Optional

MAX_REQUESTS_PER_MINUTE = 9

try:
    import praw
    from praw.exceptions import RedditAPIException
except ImportError:  # PRAW is installed when running the application.
    praw = None
    RedditAPIException = Exception

from .matcher import is_opted_out, match_inquiry
from .formatter import format_contextual_reply


class RateLimiter:
    """Keep write events at or below the configured frequency."""

    def __init__(self, minimum_seconds: float = 60.0) -> None:
        self.minimum_seconds = max(float(minimum_seconds), 60.0)
        self.last_write: Optional[float] = None

    def wait(self) -> None:
        if self.last_write is None:
            return
        remaining = self.minimum_seconds - (time.monotonic() - self.last_write)
        if remaining > 0:
            time.sleep(remaining)

    def wrote(self) -> None:
        self.last_write = time.monotonic()


class CommunityIndexer:
    """Listen to Reddit streams and optionally publish reference replies."""

    def __init__(
        self,
        config: Mapping,
        credentials,
        dry_run: bool = True,
        max_processed: int = 1000,
    ) -> None:
        self.config = config
        self.credentials = credentials
        self.dry_run = dry_run
        cooldown = config.get("cooldown", {})
        minimum = cooldown.get("minimum_seconds", 60)
        self.rate_limiter = RateLimiter(minimum)
        self.processed = deque(maxlen=max_processed)
        self.processed_set = set()
        self.processed_ids = self.processed_set
        self.reddit = None

    def _remember(self, item_id: str) -> bool:
        if item_id in self.processed_set:
            return False
        if len(self.processed) == self.processed.maxlen:
            removed = self.processed.popleft()
            self.processed_set.discard(removed)
        self.processed.append(item_id)
        self.processed_set.add(item_id)
        return True

    def connect(self) -> None:
        if praw is None:
            raise RuntimeError("PRAW is required. Install dependencies with pip.")
        kwargs = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "user_agent": self.credentials.user_agent,
        }
        self.reddit = praw.Reddit(**kwargs)

    def inspect(self, subreddits: Optional[Iterable[str]] = None) -> Iterable[dict]:
        """Yield matching submissions and comments without writing."""
        names = subreddits or self.config.get("subreddits", [])
        if self.reddit is None:
            self.connect()
        for submission in self.reddit.subreddit("+".join(names)).stream.submissions(
            skip_existing=True
        ):
            if not self._remember(submission.id):
                continue
            matches = match_inquiry(submission.title + "\n" + submission.selftext,
                                    self.config)
            if matches:
                yield {"id": submission.id, "text": submission.title,
                       "matches": matches}

    def monitor(self) -> None:
        """Monitor configured subreddits until interrupted."""
        names = self.config.get("subreddits", [])
        if self.reddit is None:
            self.connect()
        subreddit = self.reddit.subreddit("+".join(names))
        backoff = 1
        while True:
            try:
                for submission in subreddit.stream.submissions(skip_existing=True):
                    if not self._remember(submission.id):
                        continue
                    text = submission.title + "\n" + submission.selftext
                    if is_opted_out(text, self.config.get("opt_out")):
                        continue
                    matches = match_inquiry(text, self.config)
                    if matches and not self.dry_run:
                        self.rate_limiter.wait()
                        submission.reply(format_contextual_reply(matches))
                        self.rate_limiter.wrote()
                backoff = 1
            except RedditAPIException:
                time.sleep(backoff)
                backoff = min(backoff * 2, 300)


RedditBot = CommunityIndexer
