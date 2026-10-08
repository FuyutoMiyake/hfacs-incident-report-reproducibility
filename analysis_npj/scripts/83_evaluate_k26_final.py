#!/usr/bin/env python3
"""Evaluate frozen Kimi K2.6 predictions on the existing final 37-case RS."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "analysis_npj/prompt_adaptation/split50x3_20260722"
FREEZE = BASE / "frozen/final_configuration.json"
REFERENCE = BASE / "locked/final_50_reference_DO_NOT_OPEN.jsonl"
PREDICTIONS = BASE / "final_runs/r03/kimi_k26.jsonl"
OUTPUT = BASE / "final_results_kimi_k26"
SEAL = OUTPUT / "evaluation_complete.json"
METRICS_PATH = ROOT / "analysis_npj/scripts/79_evaluate_frozen_final_50.py"


def load_metrics():
    spec = importlib.util.spec_from_file_location("final_metrics", METRICS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    metrics = load_metrics()
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))

    prediction_rows = read_jsonl(PREDICTIONS)
    successful_by_source = {
        row["source_id"]: row for row in prediction_rows if row.get("status") == "ok"
    }
    successful = list(successful_by_source.values())
    if len(successful) != 37:
        raise SystemExit(f"Kimi predictions cover {len(successful)}/37 final cases")
    if any(row.get("prompt_sha256") != freeze["selected_prompt_sha256"] for row in successful):
        raise SystemExit("Kimi prediction prompt hash differs from frozen r03")
    if any(row.get("model_requested") != "kimi-k2.6" for row in successful):
        raise SystemExit("unexpected model in Kimi final predictions")

    prediction_map = {
        (row["source_id"], int(item["node_id"])): str(item["label"])
        for row in successful
        for item in row.get("result", {}).get("classifications", [])
    }
    reference_cases = read_jsonl(REFERENCE)
    leaf_rows: list[dict[str, str]] = []
    expected_sources: set[str] = set()
    for case in reference_cases:
        if case.get("canonical_analyzability") != "分析可能":
            continue
        source_id = case["source_id"]
        expected_sources.add(source_id)
        for node in case.get("nodes", []):
            if not node.get("is_leaf") or node.get("is_top"):
                continue
            key = (source_id, int(node["node_id"]))
            if key not in prediction_map:
                raise SystemExit(f"missing Kimi final prediction for {key}")
            leaf_rows.append({
                "source_id": source_id,
                "reference": str(node["reference_hfacs"]),
                "prediction": prediction_map[key],
            })
    if set(successful_by_source) != expected_sources:
        raise SystemExit("Kimi predictions do not cover exactly the final 37 analyzable cases")
    if len(leaf_rows) != 306:
        raise SystemExit(f"expected 306 final leaves, found {len(leaf_rows)}")

    results = {
        "evaluated_at": datetime.now().astimezone().isoformat(),
        "status": "posthoc_cost_constrained_deployment_model_evaluation",
        "model": "kimi-k2.6",
        "endpoint": "https://api.kimi.com/coding/v1/chat/completions",
        "prompt": "r03",
        "prompt_sha256": freeze["selected_prompt_sha256"],
        "thinking": "disabled",
        "temperature": 0.6,
        "fewshot_seed": 20260718,
        "population": {"all_cases": 50, "analyzable_cases": 37, "hfacs_leaves": 306},
        "detailed20": metrics.with_cluster_ci(leaf_rows, metrics.detailed20),
        "tier5": metrics.with_cluster_ci(leaf_rows, metrics.tier5),
        "binary": metrics.with_cluster_ci(leaf_rows, metrics.binary),
        "bootstrap_seed": metrics.BOOTSTRAP_SEED,
        "bootstrap_repetitions": metrics.BOOTSTRAP_REPETITIONS,
        "macro_f1_used": False,
        "predictions_path": str(PREDICTIONS.relative_to(ROOT)),
        "predictions_sha256": sha256(PREDICTIONS),
        "reference_sha256": sha256(REFERENCE),
        "interpretation": (
            "Kimi K2.6 was a pre-existing model-selection candidate and used the frozen r03 "
            "prompt without further adaptation. This cost-driven deployment-model evaluation "
            "was added after the GPT-5.6 Sol final run and is reported as secondary/post hoc."
        ),
    }
    if args.verify_only:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    if SEAL.exists():
        raise SystemExit("Kimi final evaluation seal already exists; use --verify-only")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    result_path = OUTPUT / "kimi_k26_final_results.json"
    result_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Kimi K2.6 最終評価",
        "",
        f"**作成日時:** {results['evaluated_at']}",
        "",
        "## 略語",
        "",
        "- **RS:** Reference Standard（合議リファレンス標準）。",
        "- **HFACS:** Human Factors Analysis and Classification System。",
        "- **kappa:** Cohen's kappa。",
        "- **AC1:** Gwet's Agreement Coefficient 1。",
        "",
        "## 評価設定",
        "",
        "固定済みr03、Kimi K2.6、non-thinkingを、最終評価用の分析可能37症例・306葉へ適用した。",
        "推論時にはRSを入力せず、予測保存後に採点した。",
        "",
        "## 結果",
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
    lines.extend([
        "",
        "## 位置づけ",
        "",
        "Kimi K2.6はモデル選択時から存在した候補で、最終評価後のprompt改修は行っていない。",
        "ただし費用制約を理由にGPT-5.6 Solの最終実行後に追加したため、cost-constrained deployment modelの二次的・事後評価として扱う。",
    ])
    report_path = OUTPUT / "kimi_k26_final_results.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    seal = {
        "status": "complete_no_prompt_revision_after_evaluation",
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
