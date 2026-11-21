"""Command-line entry point for reddit-community-indexer."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

# Allow direct execution without requiring an editable package install.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from indexer.bot import CommunityIndexer
from indexer.config import get_reddit_credentials, load_config
from indexer.formatter import build_digest, format_contextual_reply


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Index verified documentation references from Reddit communities."
    )
    parser.add_argument("--config", default="config/settings.yaml",
                        help="Path to settings YAML")
    parser.add_argument("--dry-run", action="store_true",
                        help="Inspect matches without posting replies")
    parser.add_argument("--monitor", action="store_true",
                        help="Monitor configured subreddits")
    parser.add_argument("--generate-digest", action="store_true",
                        help="Generate a weekly markdown digest")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    console = Console()
    try:
        try:
            config = load_config(args.config)
        except FileNotFoundError:
            if args.config == "config/settings.yaml":
                config = load_config("config/settings.example.yaml")
            else:
                raise

        if args.generate_digest:
            digest = build_digest([], datetime.now().strftime("%Y-%m-%d"))
            console.print(digest)
            return 0

        if args.monitor or args.dry_run:
            console.print(
                "[bold]Dry-run mode[/bold]: no Reddit replies will be posted."
                if args.dry_run else "[bold]Live monitoring started[/bold]"
            )
            if args.dry_run:
                console.print(
                    "[yellow]No Reddit stream is started in dry-run mode.[/yellow]"
                )
                return 0
            credentials = get_reddit_credentials()
            indexer = CommunityIndexer(config, credentials, dry_run=False)
            indexer.dry_run = args.dry_run
            if args.dry_run:
                for result in indexer.inspect():
                    console.print(
                        "[cyan]{id}[/cyan] {text}".format(**result)
                    )
                    console.print(format_contextual_reply(result["matches"]))
            else:
                indexer.monitor()
            return 0

        build_parser().print_help()
        return 0
    except (OSError, EnvironmentError, ValueError) as error:
        console.print("[red]Error:[/red] {}".format(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
