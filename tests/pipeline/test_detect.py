from grank_pipeline.detect import candidate_id, deduplicate, detect_transcript, normalize


def transcript(words):
    return {
        "engine": "mlx-whisper",
        "audioSha256": "a" * 64,
        "segments": [{"start": 0, "end": 10, "words": words}],
    }


def test_normalize_variants():
    assert normalize("G-Stack’s") == "g stack's"
    assert normalize("Gee   stack") == "gee stack"


def test_detects_exact_and_phonetic_forms():
    result = detect_transcript(
        "episode",
        transcript(
            [
                {"word": "We", "start": 1, "end": 1.2},
                {"word": "use", "start": 1.2, "end": 1.5},
                {"word": "gee", "start": 1.5, "end": 1.8},
                {"word": "stack", "start": 1.8, "end": 2.1},
            ]
        ),
    )
    assert any(
        item["normalizedText"] == "gee stack" and item["reason"] == "exact" for item in result
    )


def test_deduplicates_overlapping_windows():
    base = {
        "startMs": 1000,
        "endMs": 2000,
        "normalizedText": "g stack",
        "text": "g stack",
        "reason": "exact",
        "source": "mlx",
        "context": "g stack",
        "decision": "pending",
    }
    result = deduplicate(
        [{**base, "id": "a", "score": 100}, {**base, "id": "b", "score": 90, "startMs": 1100}]
    )
    assert len(result) == 1
    assert result[0]["id"] == "a"


def test_candidate_ids_are_stable():
    assert candidate_id("g", "a" * 64, 1050, "G Stack") == candidate_id(
        "g", "a" * 64, 1090, "g-stack"
    )


def test_repeated_mentions_less_than_a_second_apart_remain_distinct():
    result = detect_transcript(
        "episode",
        transcript(
            [
                {"word": "GStack", "start": 1.0, "end": 1.2},
                {"word": "GStack", "start": 1.5, "end": 1.7},
            ]
        ),
    )

    exact = [item for item in result if item["reason"] == "exact"]
    assert len(exact) == 2
