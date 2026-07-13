from __future__ import annotations

import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .models import DATA_DIR, WORK_DIR, read_json, utc_now, write_json

console = Console()


def review_episode(guid: str) -> None:
    path = DATA_DIR / "review" / f"{guid}.json"
    review = read_json(path)
    manifest = {item["guid"]: item for item in read_json(WORK_DIR / "audio-manifest.json")}
    audio = WORK_DIR.parent / manifest[guid]["path"]
    for candidate in review["candidates"]:
        if candidate["decision"] != "pending":
            continue
        console.print(
            Panel(
                f"[bold]{candidate['reason']}[/bold] at {candidate['startMs'] / 1000:.2f}s\n"
                f"{candidate['context']}",
                title=candidate["text"],
            )
        )
        while True:
            choice = Prompt.ask(
                "[a]ccept, [r]eject, [p]lay, adjust [t]imestamp, mark duplicate [x], [d]efer",
                choices=["a", "r", "p", "t", "x", "d"],
            )
            if choice == "p":
                start = max(0, candidate["startMs"] / 1000 - 8)
                subprocess.run(
                    [
                        "ffplay",
                        "-autoexit",
                        "-nodisp",
                        "-ss",
                        str(start),
                        "-t",
                        "20",
                        str(audio),
                    ],
                    check=False,
                )
                continue
            if choice == "t":
                corrected = Prompt.ask(
                    "Correct start time in seconds",
                    default=f"{candidate['startMs'] / 1000:.3f}",
                )
                try:
                    previous_start = candidate["startMs"]
                    next_start = max(0, round(float(corrected) * 1000))
                    candidate["startMs"] = next_start
                    candidate["endMs"] = max(
                        next_start,
                        candidate["endMs"] + next_start - previous_start,
                    )
                except ValueError:
                    console.print("[red]Enter a numeric timestamp in seconds.[/red]")
                    continue
                write_json(path, review)
                continue
            if choice == "a":
                candidate["decision"] = "accepted"
            elif choice == "r":
                candidate["decision"] = "rejected"
            elif choice == "x":
                candidate["decision"] = "duplicate"
            write_json(path, review)
            if choice == "d":
                return
            break
    pending = any(item["decision"] == "pending" for item in review["candidates"])
    if not pending:
        accepted = any(item["decision"] == "accepted" for item in review["candidates"])
        if (
            accepted
            or Prompt.ask("Confirm no audible mention after the relaxed audit?", choices=["y", "n"])
            == "y"
        ):
            review["noMentionAuditComplete"] = not accepted
            review["status"] = "complete"
            review["completedAt"] = utc_now()
            write_json(path, review)
            console.print("[green]Episode review complete.[/green]")
