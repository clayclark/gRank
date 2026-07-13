from grank_pipeline.auto_review import METHOD, adjudicate_review


def candidate(identifier, start, normalized, reason, sources=None):
    return {
        "id": identifier,
        "startMs": start,
        "endMs": start + 500,
        "text": normalized,
        "normalizedText": normalized,
        "reason": reason,
        "source": (sources or ["mlx-whisper"])[0],
        "sources": sources or ["mlx-whisper"],
        "context": normalized,
        "decision": "pending",
    }


def test_auto_review_accepts_explicit_and_rejects_generic_stack():
    result = adjudicate_review(
        {
            "guid": "episode",
            "status": "pending",
            "completedAt": None,
            "noMentionAuditComplete": False,
            "candidates": [
                candidate("explicit", 1_000, "g stack", "exact", ["mlx-whisper", "youtube"]),
                candidate("generic", 5_000, "stack", "stack-audit"),
            ],
        },
        completed_at="2026-01-01T00:00:00Z",
    )

    assert result["status"] == "complete"
    assert result["reviewMethod"] == METHOD
    assert result["candidates"][0]["decision"] == "accepted"
    assert result["candidates"][1]["decision"] == "rejected"
    assert result["evidenceSummary"]["acceptedCount"] == 1
    assert result["noMentionAuditComplete"] is False


def test_auto_review_marks_overlapping_fuzzy_window_as_duplicate():
    result = adjudicate_review(
        {
            "guid": "episode",
            "candidates": [
                candidate("fuzzy", 1_000, "g sack", "fuzzy", ["youtube"]),
                candidate("exact", 1_050, "g stack", "exact", ["mlx-whisper"]),
            ],
        }
    )

    assert result["candidates"][0]["decision"] == "duplicate"
    assert result["candidates"][1]["decision"] == "accepted"


def test_auto_review_completes_no_mention_audit():
    result = adjudicate_review(
        {
            "guid": "episode",
            "candidates": [candidate("generic", 1_000, "tanstack", "stack-audit")],
        }
    )

    assert result["noMentionAuditComplete"] is True
    assert result["evidenceSummary"]["acceptedCount"] == 0
