#!/usr/bin/env python3
"""Compare FTA structural rankings with frequency and co-occurrence baselines."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "analysis_npj" / "generated" / "no_improvement_full150.jsonl"
DATA_DIR = ROOT / "analysis_npj" / "derived"
TARGET_DIR = ROOT / "analysis_npj" / "results" / "improvement_holdout"
OUT_DIR = ROOT / "analysis_npj" / "results" / "fta_added_value"
BOOTSTRAP_REPS = 2000
BOOTSTRAP_SEED = 1500716
MAX_MCS = 100000

HFACS_19 = [
    "UA_DE", "UA_SE", "UA_PE", "UA_RV", "UA_EV",
    "PC_AM", "PC_AP", "PC_PL", "PC_TE", "PC_PE", "PC_CC", "PC_PR",
    "SI_IS", "SI_IO", "SI_FK", "SI_SV",
    "OI_RM", "OI_OC", "OI_OP",
]
HFACS_SET = set(HFACS_19)
ANALYSIS_SETS = {
    "primary_main11_50": lambda main_number: main_number >= 11,
    "sensitivity_main1_50": lambda main_number: True,
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def parse_set(value: str) -> set[str]:
    return set(json.loads(value or "[]")) & HFACS_SET


def absorb(cut_sets: list[frozenset[int]]) -> list[frozenset[int]]:
    unique = sorted(set(cut_sets), key=lambda item: (len(item), tuple(sorted(item))))
    result: list[frozenset[int]] = []
    for candidate in unique:
        if not any(existing <= candidate for existing in result):
            result.append(candidate)
    if len(result) > MAX_MCS:
        raise RuntimeError(f"MCS count exceeded {MAX_MCS}")
    return result


def analyze_tree(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {int(node["node_id"]): node for node in nodes}
    children: dict[int, list[int]] = defaultdict(list)
    root_id: int | None = None
    for node_id, node in by_id.items():
        parent_id = int(node.get("parent_id") or 0)
        if bool(node.get("is_top")):
            root_id = node_id
        if parent_id in by_id:
            children[parent_id].append(node_id)
    if root_id is None:
        raise ValueError("No top node")

    for parent_id in children:
        children[parent_id].sort()

    def mcs(node_id: int) -> list[frozenset[int]]:
        child_ids = children.get(node_id, [])
        if not child_ids:
            return [frozenset({node_id})]
        child_sets = [mcs(child_id) for child_id in child_ids]
        gate = str(by_id[node_id].get("gate") or "AND").upper()
        if gate == "OR":
            return absorb([cut_set for group in child_sets for cut_set in group])
        combined = [frozenset()]
        for group in child_sets:
            combined = absorb([left | right for left, right in product(combined, group)])
        return absorb(combined)

    cut_sets = mcs(root_id)
    leaf_ids = {node_id for node_id in by_id if not children.get(node_id)}
    hfacs_by_leaf = {
        node_id: str(by_id[node_id].get("hfacs") or "")
        for node_id in leaf_ids
    }

    def evaluate(node_id: int, removed_hfacs: str) -> bool:
        child_ids = children.get(node_id, [])
        if not child_ids:
            return hfacs_by_leaf.get(node_id) != removed_hfacs
        values = [evaluate(child_id, removed_hfacs) for child_id in child_ids]
        gate = str(by_id[node_id].get("gate") or "AND").upper()
        return any(values) if gate == "OR" else all(values)

    frequency = Counter(
        code for node_id, code in hfacs_by_leaf.items() if code in HFACS_SET
    )
    mcs_hit_fraction: dict[str, float] = {}
    interrupted: dict[str, int] = {}
    for code in HFACS_19:
        hit = sum(
            any(hfacs_by_leaf.get(node_id) == code for node_id in cut_set)
            for cut_set in cut_sets
        )
        mcs_hit_fraction[code] = hit / len(cut_sets) if cut_sets else 0.0
        interrupted[code] = int(not evaluate(root_id, code))

    return {
        "frequency": frequency,
        "presence": set(frequency),
        "mcs_count": len(cut_sets),
        "mcs_hit_fraction": mcs_hit_fraction,
        "interrupted": interrupted,
        "leaf_count": len(leaf_ids),
        "hfacs_leaf_count": sum(frequency.values()),
        "top_gate": str(by_id[root_id].get("gate") or ""),
    }


def global_method_scores(case_ids: list[str], analyses: dict[str, dict[str, Any]]) -> dict[str, dict[str, float]]:
    frequency_presence = Counter()
    frequency_nodes = Counter()
    cooccurrence = Counter()
    interruption = Counter()
    mcs_fraction_sum = Counter()
    for source_id in case_ids:
        analysis = analyses[source_id]
        present = sorted(analysis["presence"])
        frequency_presence.update(present)
        frequency_nodes.update(analysis["frequency"])
        for left, right in product(present, present):
            if left < right:
                cooccurrence[left] += 1
                cooccurrence[right] += 1
        for code in HFACS_19:
            interruption[code] += analysis["interrupted"][code]
            mcs_fraction_sum[code] += analysis["mcs_hit_fraction"][code]
    return {
        "frequency": {code: float(frequency_presence[code]) for code in HFACS_19},
        "frequency_nodes": {code: float(frequency_nodes[code]) for code in HFACS_19},
        "cooccurrence": {code: float(cooccurrence[code]) for code in HFACS_19},
        "fta_interruption": {
            code: float(interruption[code]) + mcs_fraction_sum[code] / 1000.0
            for code in HFACS_19
        },
        "fta_interrupted_cases": {code: float(interruption[code]) for code in HFACS_19},
        "fta_mcs_fraction_sum": {code: float(mcs_fraction_sum[code]) for code in HFACS_19},
    }


def rank_scores(scores: dict[str, float]) -> list[str]:
    return sorted(HFACS_19, key=lambda code: (-scores.get(code, 0.0), code))


def target_counts(case_ids: list[str], targets: dict[str, set[str]]) -> Counter:
    counts = Counter()
    for source_id in case_ids:
        counts.update(targets.get(source_id, set()))
    return counts


def recall_at_k(ranking: list[str], counts: Counter, k: int) -> float:
    denominator = sum(counts.values())
    if denominator == 0:
        return math.nan
    return sum(counts[code] for code in ranking[:k]) / denominator


def ndcg_at_k(ranking: list[str], counts: Counter, k: int) -> float:
    gains = [counts[code] for code in ranking[:k]]
    dcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(gains))
    ideal = sorted(counts.values(), reverse=True)[:k]
    idcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(ideal))
    return dcg / idcg if idcg else math.nan


def percentile(values: list[float]) -> tuple[float, float]:
    finite = np.asarray([value for value in values if np.isfinite(value)], dtype=float)
    if not len(finite):
        return math.nan, math.nan
    return float(np.quantile(finite, 0.025)), float(np.quantile(finite, 0.975))


def case_ranking(
    method: str,
    analysis: dict[str, Any],
    global_scores: dict[str, dict[str, float]],
) -> list[str]:
    if method == "frequency":
        return sorted(
            HFACS_19,
            key=lambda code: (
                -analysis["frequency"].get(code, 0),
                -global_scores["frequency"][code],
                code,
            ),
        )
    if method == "cooccurrence":
        return sorted(
            HFACS_19,
            key=lambda code: (
                -int(code in analysis["presence"]),
                -global_scores["cooccurrence"][code],
                code,
            ),
        )
    return sorted(
        HFACS_19,
        key=lambda code: (
            -analysis["interrupted"][code],
            -analysis["mcs_hit_fraction"][code],
            -analysis["frequency"].get(code, 0),
            -global_scores["fta_interruption"][code],
            code,
        ),
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = read_jsonl(GENERATED)
    successful = {record["source_id"]: record for record in records if record.get("status") == "success"}
    errors = [record for record in records if record.get("status") != "success"]
    if errors:
        raise RuntimeError(f"No-improvement generation has {len(errors)} errors; retry before analysis")

    cases = pd.read_csv(DATA_DIR / "canonical_cases.csv").fillna("")
    target_frame = pd.read_csv(TARGET_DIR / "improvement_target_sets.csv").fillna("")
    targets_primary = {
        row.source_id: parse_set(row.primary_target_hfacs_json)
        for row in target_frame.itertuples(index=False)
    }
    targets_sensitivity = {
        row.source_id: parse_set(row.sensitivity_target_hfacs_json)
        for row in target_frame.itertuples(index=False)
    }
    analyses = {
        source_id: analyze_tree(record["nodes"])
        for source_id, record in successful.items()
    }

    ranking_rows: list[dict[str, Any]] = []
    global_metric_rows: list[dict[str, Any]] = []
    case_metric_rows: list[dict[str, Any]] = []
    bootstrap_rows: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []

    for analysis_set, include_main in ANALYSIS_SETS.items():
        selected = cases[
            cases["main_number"].map(include_main)
            & (cases["canonical_analyzability"] == "分析可能")
            & cases["source_id"].isin(successful)
        ]
        case_ids = list(selected["source_id"])
        targets = targets_primary if analysis_set == "primary_main11_50" else targets_sensitivity
        scores = global_method_scores(case_ids, analyses)
        counts = target_counts(case_ids, targets)

        method_score_keys = {
            "frequency": "frequency",
            "cooccurrence": "cooccurrence",
            "fta": "fta_interruption",
        }
        rankings: dict[str, list[str]] = {}
        for method, score_key in method_score_keys.items():
            ranking = rank_scores(scores[score_key])
            rankings[method] = ranking
            for rank, code in enumerate(ranking, start=1):
                ranking_rows.append(
                    {
                        "analysis_set": analysis_set,
                        "method": method,
                        "rank": rank,
                        "hfacs": code,
                        "score": scores[score_key][code],
                        "target_occurrences": counts[code],
                        "case_prevalence": scores["frequency"][code],
                        "leaf_count": scores["frequency_nodes"][code],
                        "interrupted_cases": scores["fta_interrupted_cases"][code],
                        "mcs_fraction_sum": scores["fta_mcs_fraction_sum"][code],
                    }
                )
            for k in [5, 10, 19]:
                global_metric_rows.extend(
                    [
                        {
                            "analysis_set": analysis_set,
                            "method": method,
                            "metric": f"recall@{k}",
                            "estimate": recall_at_k(ranking, counts, k),
                            "n_cases": len(case_ids),
                            "n_target_cases": sum(bool(targets.get(source_id)) for source_id in case_ids),
                            "n_target_occurrences": sum(counts.values()),
                        },
                        {
                            "analysis_set": analysis_set,
                            "method": method,
                            "metric": f"ndcg@{k}",
                            "estimate": ndcg_at_k(ranking, counts, k),
                            "n_cases": len(case_ids),
                            "n_target_cases": sum(bool(targets.get(source_id)) for source_id in case_ids),
                            "n_target_occurrences": sum(counts.values()),
                        },
                    ]
                )

        for source_id in case_ids:
            target = targets.get(source_id, set())
            if not target:
                continue
            for method in ["frequency", "cooccurrence", "fta"]:
                ranking = case_ranking(method, analyses[source_id], scores)
                for k in [5, 10]:
                    selected_codes = set(ranking[:k])
                    case_metric_rows.append(
                        {
                            "analysis_set": analysis_set,
                            "source_id": source_id,
                            "method": method,
                            "k": k,
                            "recall": len(target & selected_codes) / len(target),
                            "precision": len(target & selected_codes) / k,
                            "target_count": len(target),
                            "ranking_json": json.dumps(ranking, ensure_ascii=False),
                            "target_json": json.dumps(sorted(target), ensure_ascii=False),
                        }
                    )

        if analysis_set == "primary_main11_50":
            rng = np.random.default_rng(BOOTSTRAP_SEED)
            bootstrap_values: dict[str, list[float]] = defaultdict(list)
            selection = {method: Counter() for method in ["frequency", "cooccurrence", "fta"]}
            for replicate in range(BOOTSTRAP_REPS):
                sampled = [str(value) for value in rng.choice(case_ids, size=len(case_ids), replace=True)]
                replicate_scores = global_method_scores(sampled, analyses)
                replicate_counts = target_counts(sampled, targets)
                replicate_rankings = {
                    "frequency": rank_scores(replicate_scores["frequency"]),
                    "cooccurrence": rank_scores(replicate_scores["cooccurrence"]),
                    "fta": rank_scores(replicate_scores["fta_interruption"]),
                }
                for method, ranking in replicate_rankings.items():
                    value = recall_at_k(ranking, replicate_counts, 5)
                    bootstrap_values[method].append(value)
                    selection[method].update(ranking[:5])
                bootstrap_values["fta_minus_frequency"].append(
                    bootstrap_values["fta"][-1] - bootstrap_values["frequency"][-1]
                )
                bootstrap_values["fta_minus_cooccurrence"].append(
                    bootstrap_values["fta"][-1] - bootstrap_values["cooccurrence"][-1]
                )

            for metric, values in bootstrap_values.items():
                ci_low, ci_high = percentile(values)
                bootstrap_rows.append(
                    {
                        "analysis_set": analysis_set,
                        "metric": metric if "minus" in metric else f"{metric}_recall@5",
                        "estimate": float(np.mean(values)),
                        "ci_low": ci_low,
                        "ci_high": ci_high,
                        "bootstrap_reps": BOOTSTRAP_REPS,
                    }
                )
            for method, counter in selection.items():
                for code in HFACS_19:
                    stability_rows.append(
                        {
                            "analysis_set": analysis_set,
                            "method": method,
                            "hfacs": code,
                            "top5_selection_rate": counter[code] / BOOTSTRAP_REPS,
                        }
                    )

        for source_id in case_ids:
            analysis = analyses[source_id]
            audit_rows.append(
                {
                    "analysis_set": analysis_set,
                    "source_id": source_id,
                    "mcs_count": analysis["mcs_count"],
                    "leaf_count": analysis["leaf_count"],
                    "hfacs_leaf_count": analysis["hfacs_leaf_count"],
                    "top_gate": analysis["top_gate"],
                }
            )

    rankings_df = pd.DataFrame(ranking_rows)
    global_metrics_df = pd.DataFrame(global_metric_rows)
    case_metrics_df = pd.DataFrame(case_metric_rows)
    bootstrap_df = pd.DataFrame(bootstrap_rows)
    stability_df = pd.DataFrame(stability_rows)
    audit_df = pd.DataFrame(audit_rows)

    rankings_df.to_csv(OUT_DIR / "global_rankings.csv", index=False, encoding="utf-8-sig")
    global_metrics_df.to_csv(OUT_DIR / "global_ranking_metrics.csv", index=False, encoding="utf-8-sig")
    case_metrics_df.to_csv(OUT_DIR / "case_specific_ranking_metrics.csv", index=False, encoding="utf-8-sig")
    bootstrap_df.to_csv(OUT_DIR / "bootstrap_global_recall.csv", index=False, encoding="utf-8-sig")
    stability_df.to_csv(OUT_DIR / "bootstrap_top5_stability.csv", index=False, encoding="utf-8-sig")
    audit_df.to_csv(OUT_DIR / "fta_structure_audit.csv", index=False, encoding="utf-8-sig")

    primary_rankings = rankings_df[rankings_df["analysis_set"] == "primary_main11_50"]
    primary_metrics = global_metrics_df[
        (global_metrics_df["analysis_set"] == "primary_main11_50")
        & global_metrics_df["metric"].isin(["recall@5", "ndcg@5"])
    ]
    differences = bootstrap_df.set_index("metric")
    fta_difference = differences.loc["fta_minus_frequency"]
    fta_top5 = primary_rankings[primary_rankings["method"] == "fta"].sort_values("rank").head(5)["hfacs"]
    fta_stability = stability_df[
        (stability_df["method"] == "fta") & stability_df["hfacs"].isin(fta_top5)
    ]
    min_stability = float(fta_stability["top5_selection_rate"].min())
    leakage_flags = sum(
        flag.startswith("improvement_quote_leak")
        for record in successful.values()
        for flag in record.get("validation_flags", [])
    )
    rank_difference = list(
        primary_rankings[primary_rankings["method"] == "fta"].sort_values("rank").head(5)["hfacs"]
    ) != list(
        primary_rankings[primary_rankings["method"] == "frequency"].sort_values("rank").head(5)["hfacs"]
    )
    gate_pass = {
        "recall_difference_ci_lower_gt_zero": bool(fta_difference.ci_low > 0),
        "fta_top5_min_selection_rate_ge_0_70": bool(min_stability >= 0.70),
        "fta_top5_differs_from_frequency": bool(rank_difference),
        "no_improvement_leak_flags": leakage_flags == 0,
    }
    overall_pass = all(gate_pass.values())

    summary = [
        "# FTA付加価値ゲート解析",
        "",
        "**作成日:** 2026-07-14",
        "",
        "## 解析定義",
        "",
        "- 頻度: no-improvement FTAの葉に各HFACS因子が存在する症例数。",
        "- 共起: 症例内HFACS集合の重み付きdegree。",
        "- FTA: あるHFACSカテゴリの全葉をfalseとした時に頂上事象がAND/OR構造上遮断される症例数を主順位とし、MCS hit fractionを副順位とした。",
        "- これは事故減少確率ではなく、報告内因果経路の構造的被覆である。",
        "",
        "## 主要結果",
        "",
        "| 手法 | recall@5 | NDCG@5 | Top 5 |",
        "|---|---:|---:|---|",
    ]
    for method in ["frequency", "cooccurrence", "fta"]:
        recall = primary_metrics[(primary_metrics["method"] == method) & (primary_metrics["metric"] == "recall@5")].iloc[0]
        ndcg = primary_metrics[(primary_metrics["method"] == method) & (primary_metrics["metric"] == "ndcg@5")].iloc[0]
        top5 = primary_rankings[primary_rankings["method"] == method].sort_values("rank").head(5)["hfacs"]
        summary.append(f"| {method} | {recall.estimate:.3f} | {ndcg.estimate:.3f} | {', '.join(top5)} |")
    summary.extend(
        [
            "",
            f"FTA - frequency recall@5 bootstrap差: {fta_difference.estimate:.3f} "
            f"(95% CI {fta_difference.ci_low:.3f} to {fta_difference.ci_high:.3f})",
            "",
            "## 事前定義ゲート",
            "",
        ]
    )
    for condition, passed in gate_pass.items():
        summary.append(f"- {'PASS' if passed else 'FAIL'}: `{condition}`")
    summary.extend(
        [
            "",
            f"**総合判定: {'PASS' if overall_pass else 'FAIL'}**",
            "",
            "FAILの場合、61,506件解析へ自動的に進まず、FTA優越性を主張しない。指標定義・target独立性・構造評価を再検討する。",
            "",
            "## 出力",
            "",
            "- `global_rankings.csv`: 手法別19カテゴリ順位",
            "- `global_ranking_metrics.csv`: recall/NDCG",
            "- `bootstrap_global_recall.csv`: 症例bootstrap CIと差",
            "- `bootstrap_top5_stability.csv`: Top 5選択安定性",
            "- `case_specific_ranking_metrics.csv`: 症例別recall/precision",
            "- `fta_structure_audit.csv`: MCS・葉・gate監査",
        ]
    )
    (OUT_DIR / "fta_added_value_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    (OUT_DIR / "gate_decision.json").write_text(
        json.dumps({"conditions": gate_pass, "overall_pass": overall_pass}, indent=2),
        encoding="utf-8",
    )
    print("\n".join(summary))


if __name__ == "__main__":
    main()
