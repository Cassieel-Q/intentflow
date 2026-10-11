from pathlib import Path

import pytest

from scripts.intentflow_runtime.analytics import MissingDataContract, read_csv_rows, summarize_funnel


def test_funnel_deduplicates_people_and_reports_stage_denominators(tmp_path: Path):
    source = tmp_path / "events.csv"
    source.write_text(
        "person_id,stage\nU1,进入\nU1,完成\nU2,进入\nU3,进入\nU3,完成\n",
        encoding="utf-8",
    )
    report = summarize_funnel(read_csv_rows(source), "person_id", "stage", ["进入", "完成"], "2026-10-01/2026-10-07")
    assert report["counts"] == {"进入": 3, "完成": 2}
    assert report["conversion"]["完成"] == {"numerator": 2, "denominator": 3, "rate": 2 / 3}
    assert "分子" in report["markdown"]


def test_funnel_refuses_missing_identity_for_person_metric(tmp_path: Path):
    source = tmp_path / "events.csv"
    source.write_text("stage\n进入\n完成\n", encoding="utf-8")
    with pytest.raises(MissingDataContract):
        summarize_funnel(read_csv_rows(source), "person_id", "stage", ["进入", "完成"], "7 days")


def test_funnel_refuses_empty_denominator_and_unknown_stage(tmp_path: Path):
    source = tmp_path / "events.csv"
    source.write_text("person_id,stage\nU1,完成\n", encoding="utf-8")
    with pytest.raises(MissingDataContract):
        summarize_funnel(read_csv_rows(source), "person_id", "stage", ["进入", "完成"], "7 days")
