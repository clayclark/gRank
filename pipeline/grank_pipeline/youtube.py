from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import httpx
from rapidfuzz.fuzz import ratio

from .models import DATA_DIR, WORK_DIR, YOUTUBE_CHANNEL_URL, read_json, utc_now, write_json


def _title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def match_score(episode: dict[str, Any], video: dict[str, Any]) -> float:
    title_score = ratio(_title(episode["title"]), _title(video.get("title", "")))
    duration_score = 0.0
    if episode.get("durationSeconds") and video.get("duration"):
        delta = abs(float(episode["durationSeconds"]) - float(video["duration"]))
        duration_score = max(0.0, 100.0 - delta / 2.0)
    return title_score * 0.35 + duration_score * 0.65


def enumerate_channel() -> list[dict[str, Any]]:
    try:
        import yt_dlp
    except ImportError as error:
        raise RuntimeError(
            "Install analysis dependencies with: uv sync --extra analysis"
        ) from error
    options = {"extract_flat": True, "quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(options) as client:
        result = client.extract_info(f"{YOUTUBE_CHANNEL_URL}/videos", download=False)
    return list(result.get("entries") or [])


def _english_json3(info: dict[str, Any]) -> tuple[str, str] | None:
    for source_name, tracks in (
        ("manual", info.get("subtitles") or {}),
        ("automatic", info.get("automatic_captions") or {}),
    ):
        language = next(
            (key for key in ("en-orig", "en", "en-US", "en-GB") if key in tracks),
            None,
        )
        if language is None:
            language = next((key for key in tracks if key.startswith("en")), None)
        if language is None:
            continue
        formats = tracks[language]
        track = next((item for item in formats if item.get("ext") == "json3"), None)
        if track and track.get("url"):
            return f"youtube-{source_name}:{language}", track["url"]
    return None


def _caption_transcript(
    guid: str,
    video_id: str,
    source: str,
    caption: dict[str, Any],
) -> dict[str, Any]:
    segments = []
    text_parts = []
    for event in caption.get("events", []):
        pieces = [item for item in event.get("segs", []) if item.get("utf8", "").strip()]
        if not pieces:
            continue
        start_ms = int(event.get("tStartMs", 0))
        duration_ms = int(event.get("dDurationMs", 0))
        event_end_ms = start_ms + duration_ms
        words = []
        for index, piece in enumerate(pieces):
            word_start_ms = start_ms + int(piece.get("tOffsetMs", 0))
            if index + 1 < len(pieces):
                word_end_ms = start_ms + int(pieces[index + 1].get("tOffsetMs", duration_ms))
            else:
                word_end_ms = event_end_ms
            words.append(
                {
                    "word": piece["utf8"].strip(),
                    "start": word_start_ms / 1000,
                    "end": max(word_start_ms, word_end_ms) / 1000,
                }
            )
        event_text = " ".join(item["word"] for item in words)
        text_parts.append(event_text)
        segments.append(
            {
                "start": start_ms / 1000,
                "end": event_end_ms / 1000,
                "text": event_text,
                "words": words,
            }
        )
    return {
        "schemaVersion": 1,
        "createdAt": utc_now(),
        "engine": "youtube",
        "model": source,
        "configHash": None,
        "guid": guid,
        "videoId": video_id,
        "language": "en",
        "segments": segments,
        "text": " ".join(text_parts),
    }


def probe_caption(guid: str, video_id: str) -> str | None:
    transcript_path = WORK_DIR / "transcripts" / f"{guid}.youtube.json"
    if transcript_path.exists():
        return read_json(transcript_path).get("model")
    try:
        import yt_dlp
    except ImportError as error:
        raise RuntimeError(
            "Install analysis dependencies with: uv sync --extra analysis"
        ) from error
    options = {"quiet": True, "skip_download": True, "writesubtitles": True}
    with yt_dlp.YoutubeDL(options) as client:
        info = client.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    selected = _english_json3(info)
    if selected is None:
        return None
    source, url = selected
    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=60,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    caption = response.json()
    write_json(WORK_DIR / "captions" / f"{guid}.{video_id}.json3", caption)
    write_json(transcript_path, _caption_transcript(guid, video_id, source, caption))
    return source


def match_catalog(catalog_path: Path = DATA_DIR / "catalog.json") -> dict[str, Any]:
    catalog = read_json(catalog_path)
    videos = enumerate_channel()
    matches = []
    for episode in catalog["episodes"]:
        candidates = sorted(
            ({"score": match_score(episode, video), "video": video} for video in videos),
            key=lambda item: item["score"],
            reverse=True,
        )
        best = candidates[0] if candidates else None
        duration_delta = (
            abs(float(episode["durationSeconds"]) - float(best["video"].get("duration")))
            if best and best["video"].get("duration")
            else None
        )
        status = (
            "automatic"
            if best and best["score"] >= 72 and duration_delta is not None and duration_delta <= 3
            else "candidate"
            if best and best["score"] >= 72
            else "unmatched"
        )
        caption_source = None
        caption_error = None
        if status == "automatic":
            try:
                caption_source = probe_caption(episode["guid"], best["video"]["id"])
            except Exception as error:  # caption access must not block the RSS fallback
                caption_error = str(error)
        matches.append(
            {
                "guid": episode["guid"],
                "episodeTitle": episode["title"],
                "status": status,
                "score": round(best["score"], 2) if best else None,
                "durationDeltaSeconds": round(duration_delta, 3)
                if duration_delta is not None
                else None,
                "videoId": best["video"].get("id") if best else None,
                "videoTitle": best["video"].get("title") if best else None,
                "watchUrl": f"https://www.youtube.com/watch?v={best['video'].get('id')}"
                if best
                else None,
                "captionSource": caption_source,
                "captionError": caption_error,
            }
        )
    output = {"channelUrl": YOUTUBE_CHANNEL_URL, "matches": matches}
    write_json(DATA_DIR / "youtube-matches.json", output)
    return output
