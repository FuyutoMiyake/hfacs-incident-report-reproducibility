#!/usr/bin/env python3
"""Evaluate a frozen model once on the held-out final 50-case reference."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "analysis_npj/prompt_adaptation/split50x3_20260722"
FREEZE = BASE / "frozen/final_configuration.json"
FINAL_REFERENCE = BASE / "locked/final_50_reference_DO_NOT_OPEN.jsonl"
OUTPUT = BASE / "final_results"
SEAL = OUTPUT / "final_evaluation_complete.json"
BOOTSTRAP_SEED = 20260722
BOOTSTRAP_REPETITIONS = 5000
HFACS_19 = {
    "UA_DE", "UA_SE", "UA_PE", "UA_RV", "UA_EV",
    "PC_AM", "PC_AP", "PC_PL", "PC_TE", "PC_PE", "PC_CC", "PC_PR",
    "SI_IS", "SI_IO", "SI_FK", "SI_SV", "OI_RM", "OI_OC", "OI_OP",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def detailed20(label: str) -> str:
    return label if label in HFACS_19 else "NON_HFACS"


def tier5(label: str) -> str:
    label = detailed20(label)
    if label.startswith("UA_"):
        return "L1"
    if label.startswith("PC_"):
        return "L2"
    if label.startswith("SI_"):
        return "L3"
    if label.startswith("OI_"):
        return "L4"
    return "NON_HFACS"


def binary(label: str) -> str:
    return "HFACS" if detailed20(label) != "NON_HFACS" else "NON_HFACS"


def prediction_map(rows: list[dict[str, Any]]) -> dict[tuple[str, int], str]:
    return {
        (row["source_id"], int(item["node_id"])): str(item["label"])
        for row in rows if row.get("status") == "ok"
        for item in row.get("result", {}).get("classifications", [])
    }


def agreement(reference: list[str], prediction: list[str]) -> dict[str, Any]:
    if not reference or len(reference) != len(prediction):
        raise ValueError("reference/prediction length mismatch")
    n = len(reference)
    labels = sorted(set(reference) | set(prediction))
    true_counts = Counter(reference)
    pred_counts = Counter(prediction)
    correct = sum(a == b for a, b in zip(reference, prediction, strict=True))
    accuracy = correct / n
    expected = sum(true_counts[label] * pred_counts[label] for label in labels) / (n * n)
    kappa = (accuracy - expected) / (1 - expected) if expected != 1 else 1.0
    if len(labels) == 1:
        ac1_expected = 0.0
    else:
        pooled = {
            label: (true_counts[label] + pred_counts[label]) / (2 * n)
            for label in labels
        }
        ac1_expected = sum(value * (1 - value) for value in pooled.values()) / (len(labels) - 1)
    ac1 = (accuracy - ac1_expected) / (1 - ac1_expected) if ac1_expected != 1 else 1.0
    return {
        "n": n,
        "correct": correct,
        "accuracy": accuracy,
        "cohens_kappa": kappa,
        "expected_agreement": expected,
        "gwets_ac1": ac1,
        "ac1_expected_agreement": ac1_expected,
    }


def percentile(values: list[float], proportion: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * proportion
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def with_cluster_ci(
    rows: list[dict[str, str]], transform: Callable[[str], str]
) -> dict[str, Any]:
    reference = [transform(row["reference"]) for row in rows]
    prediction = [transform(row["prediction"]) for row in rows]
    point = agreement(reference, prediction)
    by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_source[row["source_id"]].append(row)
    source_ids = sorted(by_source)
    rng = random.Random(BOOTSTRAP_SEED)
    bootstrap = {"cohens_kappa": [], "gwets_ac1": [], "accuracy": []}
    for _ in range(BOOTSTRAP_REPETITIONS):
        sample = [rng.choice(source_ids) for _ in source_ids]
        sampled = [row for source_id in sample for row in by_source[source_id]]
        result = agreement(
            [transform(row["reference"]) for row in sampled],
            [transform(row["prediction"]) for row in sampled],
        )
        for key in bootstrap:
            bootstrap[key].append(float(result[key]))
    for key, values in bootstrap.items():
        point[f"{key}_ci95"] = [percentile(values, 0.025), percentile(values, 0.975)]
    return point


def gate_metrics(reference_cases: list[dict[str, Any]], predictions_path: Path) -> dict[str, Any]:
    predictions = {
        row["source_id"]: row.get("result", {}).get("analyzability")
        for row in read_jsonl(predictions_path) if row.get("status") == "ok"
    }
    expected_ids = {case["source_id"] for case in reference_cases}
    if set(predictions) != expected_ids:
        raise SystemExit("analyzability predictions do not cover exactly final 50 cases")
    reference = [
        "analyzable" if case["canonical_analyzability"] == "分析可能" else "not_analyzable"
        for case in reference_cases
    ]
    prediction = [predictions[case["source_id"]] for case in reference_cases]
    result = agreement(reference, prediction)
    true_positive = sum(a == "analyzable" and b == "analyzable" for a, b in zip(reference, prediction, strict=True))
    true_negative = sum(a == "not_analyzable" and b == "not_analyzable" for a, b in zip(reference, prediction, strict=True))
    result["sensitivity_analyzable"] = true_positive / reference.count("analyzable")
    result["specificity_not_analyzable"] = true_negative / reference.count("not_analyzable")
    result["predictions_path"] = str(predictions_path.relative_to(ROOT))
    result["predictions_sha256"] = sha256(predictions_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hfacs-predictions", type=Path, required=True)
    parser.add_argument("--analyzability-predictions", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    args.hfacs_predictions = args.hfacs_predictions.resolve()
    if args.analyzability_predictions:
        args.analyzability_predictions = args.analyzability_predictions.resolve()

    if not FREEZE.exists():
        raise SystemExit("final configuration is not frozen; refusing to open final reference")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze.get("status") != "frozen_authorized_for_single_final_evaluation":
        raise SystemExit("freeze manifest does not authorize final evaluation")
    if SEAL.exists() and not args.verify_only:
        raise SystemExit("final evaluation seal already exists; refusing a second evaluation")
    if sha256(FINAL_REFERENCE) != freeze["final_reference_expected_sha256"]:
        raise SystemExit("final reference hash differs from the predeclared split")

    prediction_rows = read_jsonl(args.hfacs_predictions)
    ok_rows = [row for row in prediction_rows if row.get("status") == "ok"]
    expected_prompt_hash = freeze["selected_prompt_sha256"]
    if any(row.get("prompt_sha256") != expected_prompt_hash for row in ok_rows):
        raise SystemExit("prediction prompt hash differs from frozen prompt")
    final_cases = read_jsonl(FINAL_REFERENCE)
    if Counter(case["canonical_analyzability"] for case in final_cases) != Counter({
        "分析可能": 37, "分析不可能": 13,
    }):
        raise SystemExit("final reference is not 37 analyzable / 13 not analyzable")

    predictions = prediction_map(prediction_rows)
    leaf_rows: list[dict[str, str]] = []
    expected_sources: set[str] = set()
    for case in final_cases:
        if case["canonical_analyzability"] != "分析可能":
            continue
        expected_sources.add(case["source_id"])
        for node in case.get("nodes", []):
            if not node.get("is_leaf") or node.get("is_top"):
                continue
            key = (case["source_id"], int(node["node_id"]))
            if key not in predictions:
                raise SystemExit(f"missing final prediction for {key}")
            leaf_rows.append({
                "source_id": case["source_id"],
                "reference": str(node["reference_hfacs"]),
                "prediction": predictions[key],
            })
    prediction_sources = {row["source_id"] for row in ok_rows}
    if prediction_sources != expected_sources:
        raise SystemExit("HFACS predictions do not cover exactly final 37 analyzable cases")

    results = {
        "evaluated_at": datetime.now().astimezone().isoformat(),
        "population": {
            "all_cases": 50,
            "analyzable_cases": 37,
            "not_analyzable_cases": 13,
            "hfacs_leaves": len(leaf_rows),
        },
        "frozen_configuration": freeze,
        "hfacs_predictions_path": str(args.hfacs_predictions.relative_to(ROOT)),
        "hfacs_predictions_sha256": sha256(args.hfacs_predictions),
        "detailed20": with_cluster_ci(leaf_rows, detailed20),
        "tier5": with_cluster_ci(leaf_rows, tier5),
        "binary": with_cluster_ci(leaf_rows, binary),
        "analyzability": (
            gate_metrics(final_cases, args.analyzability_predictions)
            if args.analyzability_predictions else None
        ),
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_repetitions": BOOTSTRAP_REPETITIONS,
        "macro_f1_used": False,
        "final_reference_sha256": sha256(FINAL_REFERENCE),
        "interpretation": (
            "Held-out final evaluation separate from the current model/R selection set; "
            "the parent 100-case cohort had prior aggregate exploratory comparisons."
        ),
    }
    if args.verify_only:
        print(json.dumps({
            "status": "verified_without_writing",
            "population": results["population"],
            "detailed20": results["detailed20"],
        }, ensure_ascii=False, indent=2))
        return

    OUTPUT.mkdir(parents=True, exist_ok=True)
    result_path = OUTPUT / "final_results.json"
    result_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# 凍結後の最終評価50症例",
        "",
        f"**作成日時:** {results['evaluated_at']}",
        "",
        "## 略語",
        "",
        "- **RS:** Reference Standard。",
        "- **HFACS:** Human Factors Analysis and Classification System。",
        "- **kappa:** Cohen's kappa。",
        "- **AC1:** Gwet's Agreement Coefficient 1。",
        "",
        "## 結果",
        "",
        f"最終評価50症例は、分析可能37症例、分析不可能13症例だった。"
        f"HFACS分類は分析可能37症例・{len(leaf_rows)}葉で評価した。",
        "",
        "| 粒度 | kappa [95% CI] | AC1 [95% CI] | Accuracy [95% CI] |",
        "|---|---:|---:|---:|",
    ]
    for name in ("detailed20", "tier5", "binary"):
        item = results[name]
        lines.append(
            f"| {name} | {item['cohens_kappa']:.3f} "
            f"[{item['cohens_kappa_ci95'][0]:.3f}, {item['cohens_kappa_ci95'][1]:.3f}] | "
            f"{item['gwets_ac1']:.3f} [{item['gwets_ac1_ci95'][0]:.3f}, "
            f"{item['gwets_ac1_ci95'][1]:.3f}] | {item['accuracy']:.3f} "
            f"[{item['accuracy_ci95'][0]:.3f}, {item['accuracy_ci95'][1]:.3f}] |"
        )
    if results["analyzability"]:
        item = results["analyzability"]
        lines.extend([
            "",
            "## 分析可能性",
            "",
            f"kappa `{item['cohens_kappa']:.3f}`、accuracy `{item['accuracy']:.3f}`、"
            f"感度 `{item['sensitivity_analyzable']:.3f}`、特異度 "
            f"`{item['specificity_not_analyzable']:.3f}`。",
        ])
    lines.extend([
        "",
        "## 位置づけ",
        "",
        "三分割再解析でmodel・R選択に用いた50症例とは別に定めた最終評価用50症例である。"
        "親100症例に過去の集計比較履歴がある点はlimitationとして明記する。",
    ])
    report_path = OUTPUT / "final_results.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    seal = {
        "status": "complete_no_second_final_evaluation",
        "evaluated_at": results["evaluated_at"],
        "result_path": str(result_path.relative_to(ROOT)),
        "result_sha256": sha256(result_path),
        "report_path": str(report_path.relative_to(ROOT)),
        "report_sha256": sha256(report_path),
    }
    SEAL.write_text(
        json.dumps(seal, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(seal, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
