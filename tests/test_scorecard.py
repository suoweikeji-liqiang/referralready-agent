from pathlib import Path

from app.scorecard import evaluate_submission, render_scorecard_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_scorecard_reports_stage_one_blockers_and_multi_judge_average():
    report = evaluate_submission(PROJECT_ROOT)

    assert report["stage_1"]["ready"] is False
    assert any("Marketplace" in blocker for blocker in report["stage_1"]["blockers"])
    assert len(report["judges"]) == 3
    assert report["average_scores"]["ai_factor"] > 0
    assert report["average_scores"]["feasibility"] > 0


def test_scorecard_reports_score_spread_and_prioritized_actions():
    report = evaluate_submission(PROJECT_ROOT)

    assert report["score_spread"]["ai_factor"] >= 0
    assert report["score_spread"]["potential_impact"] >= 0
    assert report["score_spread"]["feasibility"] >= 0
    assert report["recommended_actions"]
    assert "Marketplace" in report["recommended_actions"][0]


def test_scorecard_report_renderer_includes_stage_one_and_average_scores():
    report = evaluate_submission(PROJECT_ROOT)
    rendered = render_scorecard_report(report)

    assert "Stage 1 Readiness" in rendered
    assert "Average Scores" in rendered
    assert "Judge" in rendered
