"""Internal competition scorecard for ReferralReady."""
from __future__ import annotations

import json
from pathlib import Path


CRITERIA = ("ai_factor", "potential_impact", "feasibility")
ARTIFACT_PATHS = {
    "readme": "README.md",
    "architecture": "docs/architecture.md",
    "demo_script": "docs/demo_script.md",
    "marketplace_setup": "docs/marketplace_setup.md",
    "safety": "docs/safety.md",
    "devpost_draft": "submission/devpost_draft.md",
    "manifest": "submission/prompt_opinion_manifest.example.json",
}


def _read_text(path: Path, max_chars: int = 4000) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")[:max_chars]


def _load_artifacts(project_root: Path) -> dict[str, str]:
    return {
        name: _read_text(project_root / relative_path)
        for name, relative_path in ARTIFACT_PATHS.items()
    }


def _has_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _count_patients(project_root: Path) -> int:
    return len(list((project_root / "data" / "synthetic_fhir").glob("*.json")))


def _count_specialties(project_root: Path) -> int:
    return len(list((project_root / "data" / "checklists").glob("*.json")))


def _evaluate_stage_one(artifacts: dict[str, str], project_root: Path) -> dict:
    manifest = artifacts["manifest"]
    readme = artifacts["readme"]
    marketplace_setup = artifacts["marketplace_setup"]
    demo_script = artifacts["demo_script"]
    safety = artifacts["safety"]
    devpost_draft = artifacts["devpost_draft"]

    checks = {
        "marketplace_published": {
            "passed": _has_any(devpost_draft + marketplace_setup, ["https://", "http://"])
            and _has_any(devpost_draft + marketplace_setup, ["marketplace"]),
            "label": "Marketplace publication evidence present",
        },
        "protocol_adherence": {
            "passed": (project_root / "app" / "mcp_server.py").exists()
            and _has_any(readme + manifest, ["mcp", "mcp_server"]),
            "label": "MCP or A2A protocol evidence present",
        },
        "platform_integration": {
            "passed": _has_any(
                demo_script + marketplace_setup,
                ["functioning within the prompt opinion platform", "tools visible and callable"],
            )
            and _has_any(devpost_draft, ["prompt opinion marketplace"]),
            "label": "Prompt Opinion integration evidence present",
        },
        "safety_compliance": {
            "passed": _has_any(readme + safety + devpost_draft, ["synthetic", "no phi", "does not diagnose"]),
            "label": "Synthetic-only safety evidence present",
        },
    }

    blockers = [item["label"].replace(" evidence present", "") for item in checks.values() if not item["passed"]]
    return {"ready": all(item["passed"] for item in checks.values()), "checks": checks, "blockers": blockers}


def _base_scores(artifacts: dict[str, str], project_root: Path, stage_one: dict) -> dict[str, float]:
    readme = artifacts["readme"]
    architecture = artifacts["architecture"]
    demo_script = artifacts["demo_script"]
    safety = artifacts["safety"]
    manifest = artifacts["manifest"]
    devpost_draft = artifacts["devpost_draft"]
    marketplace_setup = artifacts["marketplace_setup"]
    patient_count = _count_patients(project_root)
    specialty_count = _count_specialties(project_root)

    ai_factor = 4.5
    if _has_any(readme + architecture + devpost_draft, ["agent", "prompt opinion", "llm", "summarization"]):
        ai_factor += 1.5
    if _has_any(manifest, ["build_referral_packet", "generate_care_coordination_tasks"]):
        ai_factor += 1.0
    if _has_any(architecture, ["checklist + ai", "agent summarization"]):
        ai_factor += 1.0

    potential_impact = 4.5
    if _has_any(readme + demo_script + devpost_draft, ["delayed", "referral", "specialist", "handoff"]):
        potential_impact += 2.0
    potential_impact += min(float(specialty_count) * 0.5, 1.5)
    potential_impact += min(float(patient_count) * 0.15, 1.0)

    feasibility = 4.5
    if _has_any(readme + safety + devpost_draft, ["synthetic", "human review", "no phi", "no diagnosis"]):
        feasibility += 2.0
    if _has_any(marketplace_setup + demo_script, ["mcp", "tools", "demo"]):
        feasibility += 1.0
    if not stage_one["checks"]["marketplace_published"]["passed"]:
        feasibility -= 0.5
    if not stage_one["checks"]["platform_integration"]["passed"]:
        feasibility -= 1.0

    return {
        "ai_factor": max(1.0, min(10.0, round(ai_factor, 1))),
        "potential_impact": max(1.0, min(10.0, round(potential_impact, 1))),
        "feasibility": max(1.0, min(10.0, round(feasibility, 1))),
    }


def _judge_profiles(stage_one: dict) -> list[dict]:
    stage_one_penalty = -0.5 if not stage_one["ready"] else 0.0
    return [
        {
            "name": "Innovation Judge",
            "adjustments": {"ai_factor": 0.7, "potential_impact": 0.1, "feasibility": stage_one_penalty},
            "focus": "Rewards clear generative-AI value over static workflow logic.",
        },
        {
            "name": "Workflow Judge",
            "adjustments": {"ai_factor": -0.2, "potential_impact": 0.6, "feasibility": 0.2},
            "focus": "Rewards operational pain-point clarity and workflow usefulness.",
        },
        {
            "name": "Platform Judge",
            "adjustments": {"ai_factor": 0.1, "potential_impact": 0.0, "feasibility": -0.8 if not stage_one["ready"] else 0.4},
            "focus": "Rewards realistic deployment and penalizes missing Stage 1 proof.",
        },
    ]


def _apply_adjustments(base_scores: dict[str, float], adjustments: dict[str, float]) -> dict[str, float]:
    scores = {}
    for criterion in CRITERIA:
        scores[criterion] = max(1.0, min(10.0, round(base_scores[criterion] + adjustments.get(criterion, 0.0), 1)))
    return scores


def _average_scores(judges: list[dict]) -> dict[str, float]:
    return {
        criterion: round(sum(judge["scores"][criterion] for judge in judges) / len(judges), 2)
        for criterion in CRITERIA
    }


def _score_spread(judges: list[dict]) -> dict[str, float]:
    return {
        criterion: round(
            max(judge["scores"][criterion] for judge in judges)
            - min(judge["scores"][criterion] for judge in judges),
            2,
        )
        for criterion in CRITERIA
    }


def _recommended_actions(stage_one: dict, average_scores: dict[str, float]) -> list[str]:
    actions = []
    if not stage_one["checks"]["marketplace_published"]["passed"]:
        actions.append("Publish the project to the Prompt Opinion Marketplace and add the live Marketplace URL.")
    if not stage_one["checks"]["platform_integration"]["passed"]:
        actions.append("Capture direct Prompt Opinion discovery and invocation evidence in the demo and submission.")
    if average_scores["ai_factor"] < 7.5:
        actions.append("Strengthen the AI Factor story by clarifying what generative AI adds beyond static checklist logic.")
    if average_scores["feasibility"] < 7.5:
        actions.append("Add stronger evidence that the architecture works end-to-end inside the platform, not only locally.")
    if average_scores["potential_impact"] < 7.5:
        actions.append("Make outcome hypotheses more explicit: time saved, fewer missing packets, and fewer handoff delays.")
    return actions


def evaluate_submission(project_root: Path | str) -> dict:
    root = Path(project_root)
    artifacts = _load_artifacts(root)
    stage_one = _evaluate_stage_one(artifacts, root)
    base_scores = _base_scores(artifacts, root, stage_one)

    judges = []
    for profile in _judge_profiles(stage_one):
        scores = _apply_adjustments(base_scores, profile["adjustments"])
        judges.append(
            {
                "name": profile["name"],
                "focus": profile["focus"],
                "scores": scores,
                "overall": round(sum(scores.values()) / len(CRITERIA), 2),
            }
        )

    average_scores = _average_scores(judges)
    return {
        "stage_1": stage_one,
        "artifact_summary": {
            "patient_count": _count_patients(root),
            "specialty_count": _count_specialties(root),
            "artifact_paths": ARTIFACT_PATHS,
        },
        "judges": judges,
        "average_scores": average_scores,
        "score_spread": _score_spread(judges),
        "recommended_actions": _recommended_actions(stage_one, average_scores),
    }


def render_scorecard_report(report: dict) -> str:
    lines = ["# ReferralReady Competition Scorecard", "", "## Stage 1 Readiness"]
    lines.append(f"- Ready: {'yes' if report['stage_1']['ready'] else 'no'}")
    for check_name, check in report["stage_1"]["checks"].items():
        status = "PASS" if check["passed"] else "BLOCK"
        lines.append(f"- {status}: {check['label']} ({check_name})")
    if report["stage_1"]["blockers"]:
        lines.append("- Blockers:")
        for blocker in report["stage_1"]["blockers"]:
            lines.append(f"  - {blocker}")

    lines.extend(["", "## Average Scores"])
    for criterion, value in report["average_scores"].items():
        lines.append(f"- {criterion}: {value:.2f}/10")

    lines.extend(["", "## Score Spread"])
    for criterion, value in report["score_spread"].items():
        lines.append(f"- {criterion}: {value:.2f}")

    lines.extend(["", "## Judges"])
    for judge in report["judges"]:
        lines.append(f"- {judge['name']} ({judge['overall']:.2f}/10): {judge['focus']}")
        for criterion, value in judge["scores"].items():
            lines.append(f"  - {criterion}: {value:.1f}/10")

    lines.extend(["", "## Recommended Actions"])
    for action in report["recommended_actions"]:
        lines.append(f"- {action}")
    return "\n".join(lines) + "\n"


def evaluate_submission_as_json(project_root: Path | str) -> str:
    return json.dumps(evaluate_submission(project_root), indent=2)
