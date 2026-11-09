#!/usr/bin/env python3
"""Compare no-improvement FTA factor extraction with a direct flat baseline."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
BUNDLE = Path(__file__).resolve().parents[1]
DATA_DIR = BUNDLE / "data"
FTA_FILE = BUNDLE / "data/fta_trees.json"
FLAT_FILE = BUNDLE / "data/flat_factors.json"
TARGET_FILE = BUNDLE / "data" / "improvement_target_sets.csv"
OUT_DIR = ROOT / "analysis_npj" / "results" / "flat_vs_fta"
BOOTSTRAP_REPS = 10000
BOOTSTRAP_SEED = 1500718

HFACS_19 = [
    "UA_DE", "UA_SE", "UA_PE", "UA_RV", "UA_EV",
    "PC_AM", "PC_AP", "PC_PL", "PC_TE", "PC_PE", "PC_CC", "PC_PR",
    "SI_IS", "SI_IO", "SI_FK", "SI_SV",
    "OI_RM", "OI_OC", "OI_OP",
]
HFACS_SET = set(HFACS_19)
SYSTEM_SET = {code for code in HFACS_19 if code.startswith(("SI_", "OI_"))}
ANALYSIS_SETS = {
    "primary_main11_50": lambda main_number: main_number >= 11,
    "sensitivity_main1_50": lambda main_number: True,
}


def read_jsonl(path):
    return {r["source_id"]: r for r in json.loads(path.read_text())}

def parse_set(value: str) -> set[str]:
    return set(json.loads(value or "[]")) & HFACS_SET


def normalized(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(value)))


def set_metrics(reference: set[str], prediction: set[str]) -> dict[str, float]:
    intersection = len(reference & prediction)
    union = len(reference | prediction)
    return {
        "precision": intersection / len(prediction) if prediction else (1.0 if not reference else 0.0),
        "recall": intersection / len(reference) if reference else 1.0,
        "jaccard": intersection / union if union else 1.0,
        "dice": (2 * intersection / (len(reference) + len(prediction))) if reference or prediction else 1.0,
        "exact": float(reference == prediction),
    }


def percentile(values: list[float]) -> tuple[float, float]:
    finite = np.asarray([value for value in values if np.isfinite(value)], dtype=float)
    if not len(finite):
        return math.nan, math.nan
    return float(np.quantile(finite, 0.025)), float(np.quantile(finite, 0.975))


def bootstrap_means(
    case_ids: list[str], values: dict[str, dict[str, float]], seed: int
) -> dict[str, tuple[float, float]]:
    rng = np.random.default_rng(seed)
    estimates = {method: [] for method in values}
    for _ in range(BOOTSTRAP_REPS):
        sampled = pair_sample(rng, case_ids)
        for method, method_values in values.items():
            estimates[method].append(float(np.mean([method_values[str(source_id)] for source_id in sampled])))
    return {method: percentile(samples) for method, samples in estimates.items()}


def micro_metrics(
    case_ids: list[str], references: dict[str, set[str]], predictions: dict[str, set[str]], categories: set[str]
) -> dict[str, float]:
    tp = fp = fn = 0
    for source_id in case_ids:
        reference = references[source_id] & categories
        prediction = predictions[source_id] & categories
        tp += len(reference & prediction)
        fp += len(prediction - reference)
        fn += len(reference - prediction)
    precision = tp / (tp + fp) if tp + fp else math.nan
    recall = tp / (tp + fn) if tp + fn else math.nan
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else math.nan
    return {"precision": precision, "recall": recall, "f1": f1}


def bootstrap_micro_difference(
    case_ids: list[str],
    references: dict[str, set[str]],
    fta: dict[str, set[str]],
    flat: dict[str, set[str]],
    categories: set[str],
    metric: str,
    seed: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    differences = []
    for _ in range(BOOTSTRAP_REPS):
        sampled = [str(value) for value in pair_sample(rng, case_ids)]
        fta_value = micro_metrics(sampled, references, fta, categories)[metric]
        flat_value = micro_metrics(sampled, references, flat, categories)[metric]
        differences.append(fta_value - flat_value)
    return percentile(differences)



PAIR_MAP = dict(pd.read_csv(DATA_DIR / "canonical_cases.csv")[["source_id", "pair"]].itertuples(index=False, name=None))
def pair_sample(rng, case_ids):
    groups = [[s for s in case_ids if PAIR_MAP[s] == p] for p in sorted({PAIR_MAP[s] for s in case_ids})]
    return np.concatenate([rng.choice(g, size=len(g), replace=True) for g in groups])

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = pd.read_csv(DATA_DIR / "canonical_cases.csv").fillna("")
    nodes = pd.read_csv(DATA_DIR / "canonical_nodes.csv").fillna("")
    targets_frame = pd.read_csv(TARGET_FILE).fillna("")
    fta_records = read_jsonl(FTA_FILE)
    flat_records = read_jsonl(FLAT_FILE)
    if set(fta_records) != set(flat_records):
        raise RuntimeError("FTA and flat source IDs differ")

    references: dict[str, set[str]] = {}
    for case in cases.itertuples(index=False):
        case_nodes = nodes[(nodes["source_id"] == case.source_id) & nodes["is_leaf"].astype(bool)]
        reference = set(
            case_nodes[(case_nodes["action"] == "keep") & case_nodes["hfacs"].isin(HFACS_SET)]["hfacs"]
        )
        references[case.source_id] = reference | parse_set(case.added_hfacs_json)
    improvement_targets = {
        row.source_id: parse_set(row.primary_target_hfacs_json)
        for row in targets_frame.itertuples(index=False)
    }

    predictions: dict[str, dict[str, set[str]]] = {
        "fta": {}, "flat": {}, "fta_grounded": {}, "flat_grounded": {}
    }
    for source_id, record in fta_records.items():
        leaves = [
            node for node in record["nodes"]
            if bool(node.get("is_leaf")) and str(node.get("hfacs") or "") in HFACS_SET
        ]
        predictions["fta"][source_id] = {str(node["hfacs"]) for node in leaves}
        predictions["fta_grounded"][source_id] = {
            str(node["hfacs"])
            for node in leaves
            if node["normalized_grounded"]
        }
    for source_id, record in flat_records.items():
        predictions["flat"][source_id] = set(record.get("factor_set") or []) & HFACS_SET
        predictions["flat_grounded"][source_id] = {
            str(item["hfacs"])
            for item in record.get("factors") or []
            if item.get("normalized_grounded") and str(item.get("hfacs") or "") in HFACS_SET
        }

    case_rows: list[dict[str, Any]] = []
    aggregate_rows: list[dict[str, Any]] = []
    difference_rows: list[dict[str, Any]] = []
    category_rows: list[dict[str, Any]] = []
    ranking_rows: list[dict[str, Any]] = []
    global_bootstrap_rows: list[dict[str, Any]] = []

    for analysis_set, include_main in ANALYSIS_SETS.items():
        selected = cases[
            cases["main_number"].map(include_main)
            & (cases["canonical_analyzability"] == "分析可能")
        ]
        all_case_ids = list(selected["source_id"])
        target_definitions = {
            "augmented_reference": {source_id: references[source_id] for source_id in all_case_ids},
            "improvement_holdout": {
                source_id: improvement_targets[source_id]
                for source_id in all_case_ids
                if improvement_targets.get(source_id)
            },
        }
        for target_name, target_sets in target_definitions.items():
            case_ids = list(target_sets)
            for method, method_predictions in predictions.items():
                for source_id in case_ids:
                    values = set_metrics(target_sets[source_id], method_predictions[source_id])
                    case_rows.append(
                        {
                            "analysis_set": analysis_set,
                            "target": target_name,
                            "method": method,
                            "source_id": source_id,
                            **values,
                        }
                    )
            for metric in ["precision", "recall", "jaccard", "dice", "exact"]:
                values = {
                    method: {
                        source_id: set_metrics(target_sets[source_id], method_predictions[source_id])[metric]
                        for source_id in case_ids
                    }
                    for method, method_predictions in predictions.items()
                }
                intervals = bootstrap_means(
                    case_ids, values,
                    BOOTSTRAP_SEED + sum(ord(char) for char in analysis_set + target_name + metric),
                )
                for method, method_values in values.items():
                    estimate = float(np.mean(list(method_values.values())))
                    ci_low, ci_high = intervals[method]
                    aggregate_rows.append(
                        {
                            "analysis_set": analysis_set,
                            "target": target_name,
                            "method": method,
                            "metric": metric,
                            "estimate": estimate,
                            "ci_low": ci_low,
                            "ci_high": ci_high,
                            "n_cases": len(case_ids),
                        }
                    )
                for fta_method, flat_method in [("fta", "flat"), ("fta_grounded", "flat_grounded")]:
                    differences = {
                        source_id: values[fta_method][source_id] - values[flat_method][source_id]
                        for source_id in case_ids
                    }
                    diff_intervals = bootstrap_means(
                        case_ids, {"difference": differences},
                        BOOTSTRAP_SEED + 1000 + sum(ord(char) for char in analysis_set + target_name + metric + fta_method),
                    )["difference"]
                    difference_rows.append(
                        {
                            "analysis_set": analysis_set,
                            "target": target_name,
                            "comparison": f"{fta_method}_minus_{flat_method}",
                            "metric": metric,
                            "estimate": float(np.mean(list(differences.values()))),
                            "ci_low": diff_intervals[0],
                            "ci_high": diff_intervals[1],
                            "n_cases": len(case_ids),
                        }
                    )

        selected_references = {source_id: references[source_id] for source_id in all_case_ids}
        for scope, categories in [
            ("all_hfacs", HFACS_SET), ("l3_l4", SYSTEM_SET),
            *((code, {code}) for code in HFACS_19),
        ]:
            for method, method_predictions in predictions.items():
                values = micro_metrics(all_case_ids, selected_references, method_predictions, categories)
                category_rows.append(
                    {
                        "analysis_set": analysis_set,
                        "scope": scope,
                        "method": method,
                        "n_cases": len(all_case_ids),
                        **values,
                    }
                )
            for metric in ["precision", "recall", "f1"]:
                fta_value = micro_metrics(all_case_ids, selected_references, predictions["fta"], categories)[metric]
                flat_value = micro_metrics(all_case_ids, selected_references, predictions["flat"], categories)[metric]
                ci_low, ci_high = bootstrap_micro_difference(
                    all_case_ids, selected_references, predictions["fta"], predictions["flat"],
                    categories, metric,
                    BOOTSTRAP_SEED + 2000 + sum(ord(char) for char in analysis_set + scope + metric),
                )
                difference_rows.append(
                    {
                        "analysis_set": analysis_set,
                        "target": scope,
                        "comparison": "fta_minus_flat",
                        "metric": f"micro_{metric}",
                        "estimate": fta_value - flat_value,
                        "ci_low": ci_low,
                        "ci_high": ci_high,
                        "n_cases": len(all_case_ids),
                    }
                )

        counts = Counter()
        for source_id in all_case_ids:
            counts.update(improvement_targets.get(source_id, set()))
        denominator = sum(counts.values())
        for method, method_predictions in predictions.items():
            prevalence = Counter()
            for source_id in all_case_ids:
                prevalence.update(method_predictions[source_id])
            ranking = sorted(HFACS_19, key=lambda code: (-prevalence[code], code))
            recall5 = sum(counts[code] for code in ranking[:5]) / denominator if denominator else math.nan
            for rank, code in enumerate(ranking, start=1):
                ranking_rows.append(
                    {
                        "analysis_set": analysis_set,
                        "method": method,
                        "rank": rank,
                        "hfacs": code,
                        "case_prevalence": prevalence[code],
                        "target_occurrences": counts[code],
                        "global_recall_at_5": recall5,
                    }
                )

        rng = np.random.default_rng(
            BOOTSTRAP_SEED + 3000 + sum(ord(char) for char in analysis_set)
        )
        for replicate in range(BOOTSTRAP_REPS):
            sampled = [str(value) for value in pair_sample(rng, all_case_ids)]
            sampled_target_counts = Counter()
            for source_id in sampled:
                sampled_target_counts.update(improvement_targets.get(source_id, set()))
            sampled_denominator = sum(sampled_target_counts.values())
            recalls: dict[str, float] = {}
            for method in ["fta", "flat"]:
                sampled_prevalence = Counter()
                for source_id in sampled:
                    sampled_prevalence.update(predictions[method][source_id])
                sampled_ranking = sorted(
                    HFACS_19, key=lambda code: (-sampled_prevalence[code], code)
                )
                recall5 = (
                    sum(sampled_target_counts[code] for code in sampled_ranking[:5])
                    / sampled_denominator
                    if sampled_denominator else math.nan
                )
                recalls[method] = recall5
                global_bootstrap_rows.append(
                    {
                        "analysis_set": analysis_set,
                        "replicate": replicate,
                        "method": f"{method}_leaf_prevalence",
                        "recall_at_5": recall5,
                    }
                )
            global_bootstrap_rows.append(
                {
                    "analysis_set": analysis_set,
                    "replicate": replicate,
                    "method": "fta_minus_flat",
                    "recall_at_5": recalls["fta"] - recalls["flat"],
                }
            )

    pd.DataFrame(case_rows).to_csv(OUT_DIR / "case_metrics.csv", index=False, encoding="utf-8-sig")
    aggregate = pd.DataFrame(aggregate_rows)
    differences = pd.DataFrame(difference_rows)
    categories = pd.DataFrame(category_rows)
    rankings = pd.DataFrame(ranking_rows)
    aggregate.to_csv(OUT_DIR / "aggregate_metrics.csv", index=False, encoding="utf-8-sig")
    differences.to_csv(OUT_DIR / "paired_differences.csv", index=False, encoding="utf-8-sig")
    categories.to_csv(OUT_DIR / "micro_category_metrics.csv", index=False, encoding="utf-8-sig")
    rankings.to_csv(OUT_DIR / "global_prevalence_rankings.csv", index=False, encoding="utf-8-sig")
    global_bootstrap = pd.DataFrame(global_bootstrap_rows)
    global_bootstrap.to_csv(OUT_DIR / "global_recall_bootstrap.csv", index=False, encoding="utf-8-sig")

    primary = aggregate[
        (aggregate["analysis_set"] == "primary_main11_50")
        & aggregate["method"].isin(["fta", "flat"])
        & aggregate["metric"].isin(["precision", "recall", "jaccard"])
    ]
    summary = [
        "# 改善策非入力: FTA対flat multi-label baseline",
        "",
        "**作成日:** 2026-07-14",
        "",
        "本解析はFTA付加価値ゲート確認後に追加した探索的比較である。",
        "",
        "## Main 11-50・RS分析可能症例",
        "",
        "| Target | Method | Precision | Recall | Jaccard |",
        "|---|---|---:|---:|---:|",
    ]
    for target in ["augmented_reference", "improvement_holdout"]:
        for method in ["fta", "flat"]:
            rows = primary[(primary["target"] == target) & (primary["method"] == method)].set_index("metric")
            values = []
            for metric in ["precision", "recall", "jaccard"]:
                row = rows.loc[metric]
                values.append(f"{row.estimate:.3f} ({row.ci_low:.3f}-{row.ci_high:.3f})")
            summary.append(f"| {target} | {method} | " + " | ".join(values) + " |")

    summary.extend(["", "## Paired difference: FTA minus flat", "", "| Target | Metric | Difference | 95% CI |", "|---|---|---:|---:|"])
    primary_diff = differences[
        (differences["analysis_set"] == "primary_main11_50")
        & (differences["comparison"] == "fta_minus_flat")
        & differences["metric"].isin(["precision", "recall", "jaccard", "micro_f1"])
    ]
    for row in primary_diff.itertuples(index=False):
        summary.append(f"| {row.target} | {row.metric} | {row.estimate:.3f} | {row.ci_low:.3f} to {row.ci_high:.3f} |")

    summary.extend(["", "## Micro category performance", "", "| Scope | Method | Precision | Recall | F1 |", "|---|---|---:|---:|---:|"])
    primary_category = categories[
        (categories["analysis_set"] == "primary_main11_50")
        & categories["method"].isin(["fta", "flat"])
    ]
    for row in primary_category.itertuples(index=False):
        summary.append(f"| {row.scope} | {row.method} | {row.precision:.3f} | {row.recall:.3f} | {row.f1:.3f} |")

    summary.extend(["", "## Global prevalence top 5", ""])
    primary_rankings = rankings[rankings["analysis_set"] == "primary_main11_50"]
    for method in ["fta", "flat"]:
        frame = primary_rankings[(primary_rankings["method"] == method) & (primary_rankings["rank"] <= 5)]
        codes = ", ".join(frame.sort_values("rank")["hfacs"])
        recall5 = float(frame["global_recall_at_5"].iloc[0])
        summary.append(f"- {method}: {codes}; improvement-target recall@5={recall5:.3f}")
    primary_global_diff = global_bootstrap[
        (global_bootstrap["analysis_set"] == "primary_main11_50")
        & (global_bootstrap["method"] == "fta_minus_flat")
    ]["recall_at_5"].dropna().tolist()
    diff_low, diff_high = percentile(primary_global_diff)
    observed_fta = float(
        primary_rankings[(primary_rankings["method"] == "fta")]["global_recall_at_5"].iloc[0]
    )
    observed_flat = float(
        primary_rankings[(primary_rankings["method"] == "flat")]["global_recall_at_5"].iloc[0]
    )
    summary.append(
        f"- FTA leaf prevalence minus flat prevalence: {observed_fta - observed_flat:.3f} "
        f"(bootstrap 95% CI {diff_low:.3f} to {diff_high:.3f})"
    )

    (OUT_DIR / "flat_vs_fta_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
