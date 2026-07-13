from __future__ import annotations

from typing import Any

from .models import (
    DATA_DIR,
    FEED_URL,
    WORK_DIR,
    YOUTUBE_CHANNEL_URL,
    read_json,
    utc_now,
    write_json,
)
from .verify import validate_dataset


def _by_guid(path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    value = read_json(path)
    records = value.get("matches", []) if isinstance(value, dict) else value
    return {item["guid"]: item for item in records}


def _pending_review(guid: str) -> dict[str, Any]:
    return {
        "guid": guid,
        "audioSha256": None,
        "transcriptionModel": None,
        "transcriptionConfigHash": None,
        "status": "pending",
        "completedAt": None,
        "reviewMethod": None,
        "reviewPolicyVersion": None,
        "evidenceSummary": None,
        "noMentionAuditComplete": False,
        "candidates": [],
    }


def _youtube(match: dict[str, Any] | None) -> dict[str, Any] | None:
    if not match or match.get("status") not in {"automatic", "reviewed"}:
        return None
    video_id = match.get("videoId")
    watch_url = match.get("watchUrl")
    if not video_id or not watch_url:
        return None
    return {
        "videoId": video_id,
        "watchUrl": watch_url,
        "matchStatus": match["status"],
        "captionSource": match.get("captionSource"),
    }


def _episode(
    catalog_episode: dict[str, Any],
    review: dict[str, Any],
    audio: dict[str, Any] | None = None,
    youtube: dict[str, Any] | None = None,
) -> dict[str, Any]:
    accepted = sorted(
        (item for item in review["candidates"] if item["decision"] == "accepted"),
        key=lambda item: item["startMs"],
    )
    duration = catalog_episode["durationSeconds"]
    mentions = [
        {
            "id": item["id"],
            "startMs": item["startMs"],
            "endMs": item["endMs"],
            "detectedText": item["text"],
            "publicContext": item["context"],
            "source": item["source"]
            if item["source"] in {"youtube", "metadata", "manual"}
            else "mlx",
            "sources": sorted(
                {
                    source if source in {"youtube", "metadata", "manual"} else "mlx"
                    for source in item.get("sources", [item["source"]])
                }
            ),
            "reviewConfidence": item.get("reviewConfidence", 1.0),
        }
        for item in accepted
    ]
    count = len(mentions)
    return {
        "guid": catalog_episode["guid"],
        "slug": catalog_episode["slug"],
        "title": catalog_episode["title"],
        "description": catalog_episode["description"],
        "episodeNumber": catalog_episode["episodeNumber"],
        "seasonNumber": catalog_episode["seasonNumber"],
        "publishedAt": catalog_episode["publishedAt"],
        "durationSeconds": duration,
        "episodeUrl": catalog_episode["episodeUrl"],
        "imageUrl": catalog_episode["imageUrl"],
        "youtube": _youtube(youtube),
        "audio": {
            "enclosureUrl": catalog_episode["audio"]["enclosureUrl"],
            "declaredBytes": catalog_episode["audio"]["declaredBytes"],
            "analyzedBytes": audio.get("actualBytes") if audio else None,
            "sha256": (audio or {}).get("sha256") or review.get("audioSha256"),
        },
        "review": {
            "status": review["status"],
            "completedAt": review["completedAt"],
            "method": review.get("reviewMethod"),
            "policyVersion": review.get("reviewPolicyVersion"),
            "evidenceSummary": review.get("evidenceSummary"),
            "transcriptionModel": review.get("transcriptionModel"),
            "transcriptionConfigHash": review.get("transcriptionConfigHash"),
        },
        "mentions": mentions,
        "metrics": {
            "firstMentionMs": mentions[0]["startMs"] if mentions else None,
            "mentionCount": count,
            "mentionsPerHour": round(count / (duration / 3600), 3) if duration else 0,
        },
    }


def publish(allow_draft: bool = False) -> dict[str, Any]:
    catalog = read_json(DATA_DIR / "catalog.json")
    audio = _by_guid(WORK_DIR / "audio-manifest.json")
    youtube_path = DATA_DIR / "youtube-matches.json"
    youtube = _by_guid(youtube_path if youtube_path.exists() else WORK_DIR / "youtube-matches.json")
    episodes = []
    incomplete = []
    for item in catalog["episodes"]:
        review_path = DATA_DIR / "review" / f"{item['guid']}.json"
        if not review_path.exists():
            incomplete.append(item["guid"])
            review = _pending_review(item["guid"])
        else:
            review = read_json(review_path)
        if review["status"] != "complete":
            if item["guid"] not in incomplete:
                incomplete.append(item["guid"])
        elif any(candidate.get("decision") == "pending" for candidate in review["candidates"]):
            raise ValueError(f"Completed review still has pending candidates: {item['guid']}")
        elif not any(candidate.get("decision") == "accepted" for candidate in review["candidates"]):
            if not review.get("noMentionAuditComplete"):
                raise ValueError(f"No-mention review lacks completed audit: {item['guid']}")
        audio_record = audio.get(item["guid"])
        if (
            audio_record
            and review.get("audioSha256")
            and audio_record.get("sha256") != review["audioSha256"]
        ):
            raise ValueError(f"Review audio hash does not match manifest: {item['guid']}")
        episodes.append(_episode(item, review, audio_record, youtube.get(item["guid"])))
    if incomplete and not allow_draft:
        raise ValueError(f"Cannot publish; incomplete reviews: {', '.join(incomplete)}")
    dataset = {
        "schemaVersion": 1,
        "status": "draft" if incomplete else "published",
        "generatedAt": utc_now(),
        "source": {
            "feedUrl": FEED_URL,
            "youtubeChannelUrl": YOUTUBE_CHANNEL_URL,
            "feedLastBuildDate": catalog["feed"].get("lastBuildDate"),
            "catalogEpisodeCount": len(catalog["episodes"]),
        },
        "methodology": {
            "definitionVersion": "1.0.0",
            "detectorVersion": "1.0.0",
            "reviewPolicyVersion": "1.0.0",
            "reviewMethod": "automated-transcript-consensus",
        },
        "episodes": episodes,
    }
    errors = validate_dataset(dataset)
    if errors:
        raise ValueError("Cannot publish invalid dataset: " + "; ".join(errors))
    write_json(DATA_DIR / "grank.json", dataset)
    return dataset
