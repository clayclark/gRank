from __future__ import annotations

import calendar
import html
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import feedparser
import httpx

from .models import DATA_DIR, FEED_URL, YOUTUBE_CHANNEL_URL, slugify, utc_now, write_json

_TAG_RE = re.compile(r"<[^>]+>")
_TIMESTAMP_RE = re.compile(r"(?<!\d)(?:(\d{1,2}):)?([0-5]?\d):([0-5]\d)(?!\d)")


def parse_duration(value: str | int | None) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    parts = [int(part) for part in str(value).strip().split(":")]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 1:
        return parts[0]
    raise ValueError(f"Unsupported duration: {value}")


def plain_text(value: str | None) -> str:
    if not value:
        return ""
    text = _TAG_RE.sub(" ", value)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def timestamp_hints(value: str | None) -> list[dict[str, Any]]:
    text = plain_text(value)
    hints: list[dict[str, Any]] = []
    matches = list(_TIMESTAMP_RE.finditer(text))
    for index, match in enumerate(matches):
        hours = int(match.group(1) or 0)
        seconds = hours * 3600 + int(match.group(2)) * 60 + int(match.group(3))
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        context = text[match.start() : next_start].strip()
        hints.append({"seconds": seconds, "context": context})
    return hints


def _iso_date(entry: Any) -> str:
    parsed = entry.get("published_parsed")
    if parsed:
        return (
            datetime.fromtimestamp(calendar.timegm(parsed), tz=UTC)
            .isoformat()
            .replace("+00:00", "Z")
        )
    raw = entry.get("published")
    if raw:
        return parsedate_to_datetime(raw).astimezone(UTC).isoformat().replace("+00:00", "Z")
    raise ValueError(f"Episode {entry.get('title', '<untitled>')} has no publication date")


def normalize_feed(parsed: Any, retrieved_at: str | None = None) -> dict[str, Any]:
    episodes = []
    seen_slugs: set[str] = set()
    for entry in parsed.entries:
        guid = str(entry.get("id") or entry.get("guid") or entry.get("link"))
        title = str(entry.get("title") or "Untitled episode").strip()
        episode_number = _optional_int(entry.get("itunes_episode"))
        base_slug = slugify(f"{episode_number}-{title}" if episode_number is not None else title)
        slug = base_slug
        suffix = 2
        while slug in seen_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        seen_slugs.add(slug)
        enclosure = next(iter(entry.get("enclosures") or []), {})
        image = (entry.get("image") or {}).get("href") or (parsed.feed.get("image") or {}).get(
            "href"
        )
        description_html = str(entry.get("summary") or entry.get("description") or "")
        episodes.append(
            {
                "guid": guid,
                "slug": slug,
                "title": title,
                "description": plain_text(description_html),
                "descriptionHtml": description_html,
                "episodeNumber": episode_number,
                "seasonNumber": _optional_int(entry.get("itunes_season")),
                "publishedAt": _iso_date(entry),
                "durationSeconds": parse_duration(entry.get("itunes_duration")),
                "episodeUrl": str(entry.get("link") or ""),
                "imageUrl": image,
                "audio": {
                    "enclosureUrl": str(enclosure.get("href") or enclosure.get("url") or ""),
                    "mediaType": enclosure.get("type"),
                    "declaredBytes": _optional_int(enclosure.get("length")),
                },
                "timestampHints": timestamp_hints(description_html),
            }
        )
    episodes.sort(key=lambda item: (item["publishedAt"], item["guid"]), reverse=True)
    feed_date = parsed.feed.get("updated_parsed") or parsed.feed.get("published_parsed")
    feed_last_build = None
    if feed_date:
        feed_last_build = (
            datetime.fromtimestamp(calendar.timegm(feed_date), tz=UTC)
            .isoformat()
            .replace("+00:00", "Z")
        )
    return {
        "schemaVersion": 1,
        "retrievedAt": retrieved_at or utc_now(),
        "feed": {
            "title": str(parsed.feed.get("title") or "Nerd Snipe with Theo and Ben"),
            "url": FEED_URL,
            "youtubeChannelUrl": YOUTUBE_CHANNEL_URL,
            "lastBuildDate": feed_last_build,
        },
        "episodes": episodes,
    }


def sync_feed(output: Path = DATA_DIR / "catalog.json") -> dict[str, Any]:
    response = httpx.get(
        FEED_URL, follow_redirects=True, timeout=30, headers={"User-Agent": "gRank/0.1"}
    )
    response.raise_for_status()
    parsed = feedparser.parse(response.content)
    if parsed.bozo and not parsed.entries:
        raise ValueError(f"Unable to parse feed: {parsed.bozo_exception}")
    catalog = normalize_feed(parsed)
    write_json(output, catalog)
    return catalog


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
