from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path
from typing import Any

from rapidfuzz.fuzz import ratio

from .models import DATA_DIR, WORK_DIR, read_json, write_json

EXACT_FORMS = {"gstack", "g stack", "gee stack", "g-stack"}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("’", "'").replace("‘", "'")
    value = re.sub(r"[‐‑‒–—-]", " ", value)
    value = re.sub(r"[^a-z0-9']+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def candidate_id(guid: str, audio_sha256: str | None, start_ms: int, text: str) -> str:
    bucket = start_ms // 500
    raw = f"{guid}:{audio_sha256 or 'unknown'}:{bucket}:{normalize(text)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def _word_stream(transcript: dict[str, Any]) -> list[dict[str, Any]]:
    words = []
    for segment in transcript.get("segments", []):
        segment_words = segment.get("words") or []
        if segment_words:
            for word in segment_words:
                words.append(
                    {
                        "text": str(word.get("word") or "").strip(),
                        "start": float(word.get("start", segment.get("start", 0))),
                        "end": float(word.get("end", segment.get("end", 0))),
                        "probability": word.get("probability"),
                    }
                )
        else:
            words.append(
                {
                    "text": str(segment.get("text") or "").strip(),
                    "start": float(segment.get("start", 0)),
                    "end": float(segment.get("end", 0)),
                    "probability": None,
                }
            )
    return words


def detect_transcript(guid: str, transcript: dict[str, Any]) -> list[dict[str, Any]]:
    words = _word_stream(transcript)
    candidates: list[dict[str, Any]] = []
    audio_sha = transcript.get("audioSha256")
    for index in range(len(words)):
        for size in (1, 2, 3):
            window = words[index : index + size]
            if len(window) != size:
                continue
            text = " ".join(word["text"] for word in window)
            normalized = normalize(text)
            score = max(ratio(normalized, form) for form in EXACT_FORMS)
            contains_stack = "stack" in normalized
            if normalized in EXACT_FORMS or score >= 82 or contains_stack:
                start_ms = round(window[0]["start"] * 1000)
                end_ms = round(window[-1]["end"] * 1000)
                reason = (
                    "exact"
                    if normalized in EXACT_FORMS
                    else "stack-audit"
                    if contains_stack
                    else "fuzzy"
                )
                candidates.append(
                    {
                        "id": candidate_id(guid, audio_sha, start_ms, normalized),
                        "startMs": start_ms,
                        "endMs": end_ms,
                        "text": text,
                        "normalizedText": normalized,
                        "score": round(score, 2),
                        "reason": reason,
                        "source": transcript.get("engine", "transcript"),
                        "sources": [transcript.get("engine", "transcript")],
                        "tokenStartIndex": index,
                        "tokenEndIndex": index + size - 1,
                        "context": " ".join(
                            word["text"] for word in words[max(0, index - 8) : index + size + 8]
                        ),
                        "decision": "pending",
                    }
                )
    return deduplicate(candidates)


def deduplicate(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(candidates, key=lambda item: (item["startMs"], -item["score"], item["id"]))
    kept = []
    for candidate in ordered:
        duplicate = next(
            (
                existing
                for existing in kept
                if abs(existing["startMs"] - candidate["startMs"]) <= 1200
                and _same_occurrence(existing, candidate)
            ),
            None,
        )
        if duplicate is None:
            kept.append(candidate)
        else:
            sources = sorted(
                set(duplicate.get("sources", [duplicate["source"]]))
                | set(candidate.get("sources", [candidate["source"]]))
            )
            if candidate["score"] > duplicate["score"]:
                kept[kept.index(duplicate)] = {**candidate, "sources": sources}
            else:
                duplicate["sources"] = sources
    return kept


def _same_occurrence(existing: dict[str, Any], candidate: dict[str, Any]) -> bool:
    same_source = existing.get("source") == candidate.get("source")
    has_token_identity = all(
        key in item
        for item in (existing, candidate)
        for key in ("tokenStartIndex", "tokenEndIndex")
    )
    if same_source and has_token_identity:
        token_overlap = (
            existing["tokenStartIndex"] <= candidate["tokenEndIndex"]
            and candidate["tokenStartIndex"] <= existing["tokenEndIndex"]
        )
        return token_overlap or abs(existing["startMs"] - candidate["startMs"]) <= 300
    text_overlap = (
        existing["normalizedText"] in candidate["normalizedText"]
        or candidate["normalizedText"] in existing["normalizedText"]
    )
    time_overlap = (
        "stack" in existing["normalizedText"]
        and "stack" in candidate["normalizedText"]
        and existing["startMs"] <= candidate["endMs"]
        and candidate["startMs"] <= existing["endMs"]
    )
    return text_overlap or time_overlap


def detect_all(catalog_path: Path = DATA_DIR / "catalog.json") -> list[Path]:
    catalog = read_json(catalog_path)
    outputs = []
    for episode in catalog["episodes"]:
        transcript_paths = sorted((WORK_DIR / "transcripts").glob(f"{episode['guid']}.*.json"))
        if not transcript_paths:
            continue
        transcripts = [read_json(path) for path in transcript_paths]
        primary = next(
            (item for item in transcripts if item.get("engine") == "mlx-whisper"),
            transcripts[0],
        )
        candidates = []
        for transcript in transcripts:
            source = "youtube" if transcript.get("engine") == "youtube" else None
            detected = detect_transcript(episode["guid"], transcript)
            if source:
                for candidate in detected:
                    candidate["source"] = source
            candidates.extend(detected)
        for hint in episode.get("timestampHints", []):
            if "gstack" in normalize(hint["context"]) or "g stack" in normalize(hint["context"]):
                start_ms = hint["seconds"] * 1000
                candidates.append(
                    {
                        "id": candidate_id(
                            episode["guid"],
                            primary.get("audioSha256"),
                            start_ms,
                            "metadata hint",
                        ),
                        "startMs": start_ms,
                        "endMs": start_ms + 20_000,
                        "text": "metadata timestamp hint",
                        "normalizedText": "metadata hint",
                        "score": 100,
                        "reason": "metadata-hint",
                        "source": "metadata",
                        "sources": ["metadata"],
                        "context": hint["context"],
                        "decision": "pending",
                    }
                )
        output = DATA_DIR / "review" / f"{episode['guid']}.json"
        existing = read_json(output) if output.exists() else None
        previous = {
            item["id"]: item
            for item in (existing or {}).get("candidates", [])
            if item.get("decision") != "pending"
        }
        merged = []
        for candidate in deduplicate(candidates):
            if candidate["id"] in previous:
                candidate = {**candidate, **previous[candidate["id"]]}
            merged.append(candidate)
        has_pending = any(item["decision"] == "pending" for item in merged)
        review_status = "pending" if has_pending else (existing or {}).get("status", "pending")
        write_json(
            output,
            {
                "schemaVersion": 1,
                "guid": episode["guid"],
                "audioSha256": primary.get("audioSha256"),
                "transcriptionModel": primary.get("model"),
                "transcriptionConfigHash": primary.get("configHash"),
                "status": review_status,
                "completedAt": None if has_pending else (existing or {}).get("completedAt"),
                "noMentionAuditComplete": False
                if has_pending
                else (existing or {}).get("noMentionAuditComplete", False),
                "candidates": merged,
            },
        )
        outputs.append(output)
    return outputs
