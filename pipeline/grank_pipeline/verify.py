from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from .models import DATA_DIR, ROOT, read_json


def validate_dataset(dataset: dict) -> list[str]:
    schema = read_json(ROOT / "schema" / "grank.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        error.message
        for error in sorted(validator.iter_errors(dataset), key=lambda item: list(item.path))
    ]
    guids = set()
    slugs = set()
    published = dataset.get("status") == "published"
    for episode in dataset.get("episodes", []):
        guid = episode.get("guid", "<unknown>")
        slug = episode.get("slug")
        if guid in guids:
            errors.append(f"Duplicate GUID: {guid}")
        if slug in slugs:
            errors.append(f"Duplicate slug: {slug}")
        guids.add(guid)
        slugs.add(slug)
        mentions = episode.get("mentions", [])
        metrics = episode.get("metrics", {})
        review = episode.get("review", {})
        audio = episode.get("audio", {})
        duration_ms = episode.get("durationSeconds", 0) * 1000

        starts = [item.get("startMs", -1) for item in mentions]
        if starts != sorted(starts):
            errors.append(f"{guid}: mentions are not sorted")
        mention_ids = [item.get("id") for item in mentions]
        if len(mention_ids) != len(set(mention_ids)):
            errors.append(f"{guid}: duplicate mention IDs")
        if metrics.get("mentionCount") != len(mentions):
            errors.append(f"{guid}: mentionCount does not match mentions")
        expected = mentions[0].get("startMs") if mentions else None
        if metrics.get("firstMentionMs") != expected:
            errors.append(f"{guid}: firstMentionMs does not match mentions")
        expected_rate = round(len(mentions) / (duration_ms / 3_600_000), 3) if duration_ms else 0
        if metrics.get("mentionsPerHour") != expected_rate:
            errors.append(f"{guid}: mentionsPerHour does not match mentions and duration")
        if any(
            item.get("startMs", -1) < 0
            or item.get("endMs", -1) < item.get("startMs", 0)
            or item.get("endMs", 0) > duration_ms
            for item in mentions
        ):
            errors.append(f"{guid}: mention lies outside episode duration")

        if review.get("status") == "complete":
            if not review.get("completedAt"):
                errors.append(f"{guid}: completed review has no completion timestamp")
            if not audio.get("sha256") or audio.get("analyzedBytes") is None:
                errors.append(f"{guid}: completed review has incomplete audio provenance")
        elif review.get("completedAt") is not None:
            errors.append(f"{guid}: pending review has a completion timestamp")
        if published and review.get("status") != "complete":
            errors.append(f"{guid}: published dataset contains an incomplete review")

    source = dataset.get("source", {})
    if published and len(guids) != source.get("catalogEpisodeCount"):
        errors.append("Published dataset does not contain the full catalog")
    return errors


def verify_dataset(dataset_path: Path = DATA_DIR / "grank.json") -> list[str]:
    return validate_dataset(read_json(dataset_path))
