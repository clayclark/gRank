from grank_pipeline.feed import parse_duration, plain_text, timestamp_hints


def test_parse_duration_variants():
    assert parse_duration("1:02:03") == 3723
    assert parse_duration("42:05") == 2525
    assert parse_duration(30) == 30


def test_plain_text_and_timestamp_hints():
    value = "<p>Intro &amp; news</p><p>40:49 — GStack is actually good</p>"
    assert plain_text(value) == "Intro & news 40:49 — GStack is actually good"
    assert timestamp_hints(value)[0]["seconds"] == 2449
