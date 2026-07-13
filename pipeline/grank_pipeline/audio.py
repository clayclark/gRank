from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import httpx

from .models import DATA_DIR, WORK_DIR, read_json, write_json


def download_episode(guid: str, url: str, declared_bytes: int | None = None) -> dict[str, Any]:
    audio_dir = WORK_DIR / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    partial = audio_dir / f"{guid}.part"
    digest = hashlib.sha256()
    actual_bytes = 0
    with httpx.stream(
        "GET",
        url,
        follow_redirects=True,
        timeout=120,
        headers={"User-Agent": "gRank/0.1"},
    ) as response:
        response.raise_for_status()
        with partial.open("wb") as output:
            for chunk in response.iter_bytes():
                output.write(chunk)
                digest.update(chunk)
                actual_bytes += len(chunk)
    sha256 = digest.hexdigest()
    destination = audio_dir / f"{sha256}.mp3"
    partial.replace(destination)
    duration = probe_duration(destination)
    return {
        "guid": guid,
        "sourceUrl": url,
        "path": str(destination.relative_to(WORK_DIR.parent)),
        "declaredBytes": declared_bytes,
        "actualBytes": actual_bytes,
        "sha256": sha256,
        "durationSeconds": duration,
        "etag": response.headers.get("etag"),
        "lastModified": response.headers.get("last-modified"),
    }


def probe_duration(path: Path) -> float:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return float(json.loads(result.stdout)["format"]["duration"])


def download_catalog(catalog_path: Path = DATA_DIR / "catalog.json") -> list[dict[str, Any]]:
    catalog = read_json(catalog_path)
    manifest_path = WORK_DIR / "audio-manifest.json"
    manifest = (
        {item["guid"]: item for item in read_json(manifest_path)} if manifest_path.exists() else {}
    )
    for episode in catalog["episodes"]:
        guid = episode["guid"]
        if guid in manifest:
            continue
        item = download_episode(
            guid,
            episode["audio"]["enclosureUrl"],
            episode["audio"]["declaredBytes"],
        )
        manifest[guid] = item
        write_json(manifest_path, sorted(manifest.values(), key=lambda value: value["guid"]))
    return sorted(manifest.values(), key=lambda value: value["guid"])
