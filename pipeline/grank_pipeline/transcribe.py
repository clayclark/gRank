from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

from .models import WORK_DIR, config_hash, read_json, utc_now, write_json

DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"
DEFAULT_CONFIG = {
    "model": DEFAULT_MODEL,
    "language": "en",
    "word_timestamps": True,
    "initial_prompt": "Nerd Snipe, Theo, Ben, Gary Tan, gstack, G Stack",
    "condition_on_previous_text": True,
}


def transcribe_audio(path: Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        import mlx_whisper
    except ImportError as error:
        raise RuntimeError(
            "Install analysis dependencies with: uv sync --extra analysis"
        ) from error
    settings = {**DEFAULT_CONFIG, **(config or {})}
    model = settings.pop("model")
    result = mlx_whisper.transcribe(str(path), path_or_hf_repo=model, **settings)
    return {
        "schemaVersion": 1,
        "createdAt": utc_now(),
        "engine": "mlx-whisper",
        "model": model,
        "config": settings,
        "configHash": config_hash({"model": model, **settings}),
        "platform": {"system": platform.system(), "machine": platform.machine()},
        "language": result.get("language", "en"),
        "segments": result.get("segments", []),
        "text": result.get("text", ""),
    }


def transcribe_manifest(manifest_path: Path = WORK_DIR / "audio-manifest.json") -> list[Path]:
    outputs = []
    for item in read_json(manifest_path):
        output = WORK_DIR / "transcripts" / f"{item['guid']}.mlx.json"
        if output.exists():
            outputs.append(output)
            continue
        source = WORK_DIR.parent / item["path"]
        write_json(
            output,
            {**transcribe_audio(source), "guid": item["guid"], "audioSha256": item["sha256"]},
        )
        outputs.append(output)
    return outputs
