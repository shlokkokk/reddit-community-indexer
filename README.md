# reddit-community-indexer

reddit-community-indexer is a community knowledge-base assistant and FAQ
indexer for technical subreddits. It uses PRAW to inspect submissions and
comments, identify recurring questions, and present links to official
documentation. It can print matches during a dry run or publish short
contextual replies and weekly digests.

## Architecture

- `main.py` provides the Rich command-line interface.
- `src/indexer/config.py` loads YAML settings and Reddit OAuth environment variables.
- `src/indexer/matcher.py` matches text against configured documentation entries.
- `src/indexer/formatter.py` creates contextual replies and digest Markdown.
- `src/indexer/bot.py` manages PRAW streams, duplicate IDs, rate limits, and backoff.

## Responsible Builder Policy

- Write events are separated by at least 60 seconds and are additionally
  guarded by a `< 10 req/min` request budget.
- Processing is in memory only. The application stores no user PII and keeps
  only a bounded cache of Reddit item IDs for duplicate prevention.
- Users can opt out at any time by including `!optout` or `!stop` in text.
  Opted-out content is skipped and is never answered or retained as an answer.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp config/settings.example.yaml config/settings.yaml
```

Create a Reddit application and add credentials to `.env`:

```dotenv
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=reddit-community-indexer/1.0
REDDIT_USERNAME=optional_account_name
REDDIT_PASSWORD=optional_account_password
```

Only set username and password if the bot must use password OAuth. Local
settings and `.env` are ignored by Git.

## Configuration

Edit `config/settings.yaml`:

- `subreddits`: names of communities to monitor.
- `cooldown.minimum_seconds`: minimum interval between writes; values below
  60 are raised to 60 seconds.
- `triggers`: terms that identify knowledge requests.
- `documentation`: keyed entries containing `title` and official `url` values.
- `opt_out`: commands that disable responses for a piece of content.
- `blacklist`: terms or patterns used to exclude unsuitable material.

## CLI examples

```bash
# Inspect matches while making no Reddit writes
python main.py --dry-run

# Continuously monitor configured subreddits
python main.py --monitor

# Print a structured weekly digest
python main.py --generate-digest
```