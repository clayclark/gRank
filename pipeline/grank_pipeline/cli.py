from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .audio import download_catalog
from .detect import detect_all
from .feed import sync_feed
from .publish import publish
from .review import review_episode
from .transcribe import transcribe_manifest
from .verify import verify_dataset
from .youtube import match_catalog

app = typer.Typer(no_args_is_help=True, help="Build and verify the gRank dataset.")
console = Console()


@app.command("sync-feed")
def sync_feed_command() -> None:
    catalog = sync_feed()
    console.print(f"[green]Synced {len(catalog['episodes'])} episodes.[/green]")


@app.command("match-youtube")
def match_youtube_command() -> None:
    result = match_catalog()
    matched = sum(item["status"] in {"automatic", "reviewed"} for item in result["matches"])
    captions = sum(bool(item.get("captionSource")) for item in result["matches"])
    console.print(
        f"[green]Matched {matched} videos; retrieved {captions} English caption tracks.[/green]"
    )


@app.command("download")
def download_command() -> None:
    console.print(f"[green]Verified {len(download_catalog())} audio files.[/green]")


@app.command("transcribe")
def transcribe_command() -> None:
    console.print(f"[green]Created {len(transcribe_manifest())} transcripts.[/green]")


@app.command("detect")
def detect_command() -> None:
    console.print(f"[green]Created {len(detect_all())} review queues.[/green]")


@app.command("review")
def review_command(guid: str) -> None:
    review_episode(guid)


@app.command("publish")
def publish_command(draft: bool = typer.Option(False, help="Allow incomplete reviews.")) -> None:
    dataset = publish(allow_draft=draft)
    count = len(dataset["episodes"])
    console.print(f"[green]Wrote {dataset['status']} dataset with {count} episodes.[/green]")


@app.command("verify")
def verify_command(path: Path = Path("data/grank.json")) -> None:
    errors = verify_dataset(path)
    if errors:
        for error in errors:
            console.print(f"[red]• {error}[/red]")
        raise typer.Exit(1)
    console.print("[green]Dataset is valid.[/green]")


if __name__ == "__main__":
    app()
