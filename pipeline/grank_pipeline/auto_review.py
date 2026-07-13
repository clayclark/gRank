from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .models import DATA_DIR, read_json, utc_now, write_json

METHOD = "automated-transcript-consensus"
POLICY_VERSION = "1.0.0"
EXPLICIT_FORMS = {"gstack", "g stack", "gee stack"}


def _nearby_exact(
    candidate: dict[str, Any], exact_candidates: list[dict[str, Any]], tolerance_ms: int
) -> bool:
    return any(
        item["id"] != candidate["id"]
        and abs(item["startMs"] - candidate["startMs"]) <= tolerance_ms
        for item in exact_candidates
    )


def _decision(
    candidate: dict[str, Any], exact_candidates: list[dict[str, Any]]
) -> tuple[str, str, float]:
    normalized = candidate.get("normalizedText", "")
    reason = candidate.get("reason")
    sources = set(candidate.get("sources") or [candidate.get("source", "transcript")])

    if reason == "exact" and normalized in EXPLICIT_FORMS:
        confidence = 1.0 if len(sources) > 1 else 0.97
        evidence = "corroborated-exact" if len(sources) > 1 else "single-source-exact"
        return "accepted", evidence, confidence

    if reason == "fuzzy" and _nearby_exact(candidate, exact_candidates, 1_500):
        return "duplicate", "overlaps-exact-candidate", 1.0

    if (
        reason == "stack-audit"
        and ("gstack" in normalized or "g stack" in normalized)
        and _nearby_exact(candidate, exact_candidates, 2_500)
    ):
        return "duplicate", "overlaps-exact-candidate", 1.0

    if reason == "metadata-hint":
        return "rejected", "metadata-is-not-spoken-evidence", 1.0

    return "rejected", "not-an-explicit-gstack-reference", 0.99


def adjudicate_review(
    review: dict[str, Any], completed_at: str | None = None
) -> dict[str, Any]:
    result = deepcopy(review)
    exact_candidates = [
        item
        for item in result.get("candidates", [])
        if item.get("reason") == "exact" and item.get("normalizedText") in EXPLICIT_FORMS
    ]

    for candidate in result.get("candidates", []):
        decision, decision_reason, confidence = _decision(candidate, exact_candidates)
        candidate["decision"] = decision
        candidate["decisionReason"] = decision_reason
        candidate["reviewMethod"] = METHOD
        candidate["reviewConfidence"] = confidence

    candidates = result.get("candidates", [])
    accepted = [item for item in candidates if item["decision"] == "accepted"]
    rejected = [item for item in candidates if item["decision"] == "rejected"]
    duplicates = [item for item in candidates if item["decision"] == "duplicate"]
    corroborated = [
        item for item in accepted if len(set(item.get("sources") or [item.get("source")])) > 1
    ]

    result["status"] = "complete"
    result["completedAt"] = completed_at or utc_now()
    result["noMentionAuditComplete"] = not accepted
    result["reviewMethod"] = METHOD
    result["reviewPolicyVersion"] = POLICY_VERSION
    result["evidenceSummary"] = {
        "candidateCount": len(candidates),
        "acceptedCount": len(accepted),
        "rejectedCount": len(rejected),
        "duplicateCount": len(duplicates),
        "corroboratedAcceptedCount": len(corroborated),
        "singleSourceAcceptedCount": len(accepted) - len(corroborated),
    }
    return result


def auto_review_all(review_dir: Path = DATA_DIR / "review") -> list[Path]:
    outputs = []
    completed_at = utc_now()
    for path in sorted(review_dir.glob("*.json")):
        write_json(path, adjudicate_review(read_json(path), completed_at=completed_at))
        outputs.append(path)
    return outputs
