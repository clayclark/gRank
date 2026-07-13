import json
from pathlib import Path

import pytest
from grank_pipeline import publish as publish_module


def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def test_publish_rejects_incomplete_reviews(tmp_path, monkeypatch):
    monkeypatch.setattr(publish_module, "DATA_DIR", tmp_path)
    write(
        tmp_path / "catalog.json",
        {
            "feed": {"lastBuildDate": None},
            "episodes": [
                {
                    "guid": "one",
                    "slug": "one",
                    "title": "One",
                    "description": "",
                    "episodeNumber": 1,
                    "seasonNumber": 1,
                    "publishedAt": "2026-01-01T00:00:00Z",
                    "durationSeconds": 3600,
                    "episodeUrl": "https://example.com/one",
                    "imageUrl": None,
                    "audio": {"enclosureUrl": "https://example.com/one.mp3", "declaredBytes": 10},
                }
            ],
        },
    )
    with pytest.raises(ValueError, match="incomplete reviews"):
        publish_module.publish()


def test_draft_keeps_unreviewed_catalog_episodes_visible(tmp_path, monkeypatch):
    monkeypatch.setattr(publish_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(publish_module, "WORK_DIR", tmp_path / "work")
    write(
        tmp_path / "catalog.json",
        {
            "feed": {"lastBuildDate": None},
            "episodes": [catalog_episode()],
        },
    )

    dataset = publish_module.publish(allow_draft=True)

    assert dataset["status"] == "draft"
    assert len(dataset["episodes"]) == 1
    assert dataset["episodes"][0]["review"]["status"] == "pending"


def test_publish_derives_metrics_and_audio_provenance(tmp_path, monkeypatch):
    monkeypatch.setattr(publish_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(publish_module, "WORK_DIR", tmp_path / "work")
    write(
        tmp_path / "catalog.json",
        {
            "feed": {"lastBuildDate": None},
            "episodes": [catalog_episode()],
        },
    )
    write(
        tmp_path / "work" / "audio-manifest.json",
        [
            {
                "guid": "one",
                "actualBytes": 10,
                "sha256": "a" * 64,
            }
        ],
    )
    write(
        tmp_path / "review" / "one.json",
        {
            "guid": "one",
            "status": "complete",
            "completedAt": "2026-01-02T00:00:00Z",
            "audioSha256": "a" * 64,
            "transcriptionModel": "test-model",
            "transcriptionConfigHash": "b" * 64,
            "noMentionAuditComplete": False,
            "candidates": [
                {
                    "id": "mention-one",
                    "startMs": 5_000,
                    "endMs": 5_500,
                    "text": "g stack",
                    "context": "we use g stack here",
                    "source": "mlx-whisper",
                    "decision": "accepted",
                }
            ],
        },
    )

    dataset = publish_module.publish()
    episode = dataset["episodes"][0]

    assert dataset["status"] == "published"
    assert episode["metrics"] == {
        "firstMentionMs": 5_000,
        "mentionCount": 1,
        "mentionsPerHour": 1.0,
    }
    assert episode["audio"]["analyzedBytes"] == 10
    assert episode["audio"]["sha256"] == "a" * 64


def catalog_episode():
    return {
        "guid": "one",
        "slug": "one",
        "title": "One",
        "description": "",
        "episodeNumber": 1,
        "seasonNumber": 1,
        "publishedAt": "2026-01-01T00:00:00Z",
        "durationSeconds": 3600,
        "episodeUrl": "https://example.com/one",
        "imageUrl": None,
        "audio": {
            "enclosureUrl": "https://example.com/one.mp3",
            "declaredBytes": 10,
        },
    }
