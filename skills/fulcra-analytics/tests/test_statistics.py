from fulcra_analytics.statistics import summarize_records


def test_summarize_records_basic_numeric_fields():
    result = summarize_records([
        {"steps": 1000, "mood": "4", "note": "walk"},
        {"steps": 2000, "mood": "5", "note": "run"},
        {"steps": None, "mood": "", "note": "rest"},
    ])
    assert result.row_count == 3
    assert result.missing["steps"] == 1
    assert result.numeric["steps"]["mean"] == 1500
    assert result.numeric["mood"]["max"] == 5
