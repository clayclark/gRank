from grank_pipeline.youtube import _caption_transcript, match_score


def test_duration_identity_outweighs_rewritten_video_title():
    episode = {"title": "Anthropic solved compute", "durationSeconds": 5783}
    exact_duration = {"title": "Theo's Security Psychosis", "duration": 5784}
    similar_title = {"title": "Anthropic compute from Elon", "duration": 5716}

    assert match_score(episode, exact_duration) > match_score(episode, similar_title)


def test_json3_captions_become_timestamped_word_segments():
    result = _caption_transcript(
        "guid",
        "video",
        "youtube-automatic:en",
        {
            "events": [
                {
                    "tStartMs": 1000,
                    "dDurationMs": 1000,
                    "segs": [
                        {"utf8": "g", "tOffsetMs": 0},
                        {"utf8": " stack", "tOffsetMs": 400},
                    ],
                }
            ]
        },
    )

    assert result["segments"][0]["text"] == "g stack"
    assert result["segments"][0]["words"][1]["start"] == 1.4
