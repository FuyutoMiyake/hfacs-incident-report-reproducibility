#!/usr/bin/env python3
"""Compute pair-specific, case-clustered inter-rater reliability metrics."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "analysis_npj" / "derived"
OUT_DIR = ROOT / "analysis_npj" / "results" / "reliability"
BOOTSTRAP_REPS = 2000
BOOTSTRAP_SEED = 1500714

PAIR_ANNOTATORS = {
    "AB": ("annotator_A", "annotator_B"),
    "CD": ("annotator_C", "annotator_D"),
    "EF": ("annotator_E", "annotator_F"),
}

HFACS_19 = [
    "UA_DE", "UA_SE", "UA_PE", "UA_RV", "UA_EV",
    "PC_AM", "PC_AP", "PC_PL", "PC_TE", "PC_PE", "PC_CC", "PC_PR",
    "SI_IS", "SI_IO", "SI_FK", "SI_SV",
    "OI_RM", "OI_OC", "OI_OP",
]
NON_HFACS = ["CoP", "OTHER", "INAPPROPRIATE"]
DETAILED_22 = HFACS_19 + NON_HFACS
TIER_7 = ["L1", "L2", "L3", "L4"] + NON_HFACS
DETAILED_20 = HFACS_19 + ["NON_HFACS"]
TIER_5 = ["L1", "L2", "L3", "L4", "NON_HFACS"]
BINARY_2 = ["HFACS", "NON_HFACS"]

ANALYSIS_SETS = {
    "primary_main11_50": lambda main_number: main_number >= 11,
    "sensitivity_main1_50": lambda main_number: True,
}


def tier(label: str) -> str:
    if label.startswith("UA_"):
        return "L1"
    if label.startswith("PC_"):
        return "L2"
    if label.startswith("SI_"):
        return "L3"
    if label.startswith("OI_"):
        return "L4"
    return label


def binary(label: str) -> str:
    return "HFACS" if label in HFACS_19 else "NON_HFACS"


def merge_non_hfacs(label: str) -> str:
    return label if label in HFACS_19 else "NON_HFACS"


def tier_merge_non_hfacs(label: str) -> str:
    return tier(label) if label in HFACS_19 else "NON_HFACS"


def cohen_kappa(pairs: list[tuple[str, str]], categories: list[str]) -> float:
    if not pairs:
        return math.nan
    index = {category: i for i, category in enumerate(categories)}
    matrix = np.zeros((len(categories), len(categories)), dtype=float)
    used = 0
    for left, right in pairs:
        if left in index and right in index:
            matrix[index[left], index[right]] += 1
            used += 1
    if used == 0:
        return math.nan
    observed = np.trace(matrix) / used
    row = matrix.sum(axis=1) / used
    column = matrix.sum(axis=0) / used
    expected = float(np.dot(row, column))
    if math.isclose(expected, 1.0):
        return math.nan
    return float((observed - expected) / (1.0 - expected))


def gwet_ac1(pairs: list[tuple[str, str]], categories: list[str]) -> float:
    if not pairs or len(categories) < 2:
        return math.nan
    index = {category: i for i, category in enumerate(categories)}
    matrix = np.zeros((len(categories), len(categories)), dtype=float)
    used = 0
    for left, right in pairs:
        if left in index and right in index:
            matrix[index[left], index[right]] += 1
            used += 1
    if used == 0:
        return math.nan
    observed = float(np.trace(matrix) / used)
    pooled = (matrix.sum(axis=1) + matrix.sum(axis=0)) / (2.0 * used)
    expected = float(np.sum(pooled * (1.0 - pooled)) / (len(categories) - 1))
    if math.isclose(expected, 1.0):
        return math.nan
    return float((observed - expected) / (1.0 - expected))


def percent_agreement(pairs: list[tuple[str, str]], categories: list[str] | None = None) -> float:
    if categories is not None:
        pairs = [(a, b) for a, b in pairs if a in categories and b in categories]
    if not pairs:
        return math.nan
    return float(np.mean([left == right for left, right in pairs]))


def percentile_ci(values: Iterable[float]) -> tuple[float, float, int]:
    finite = np.asarray([value for value in values if np.isfinite(value)], dtype=float)
    if len(finite) == 0:
        return math.nan, math.nan, 0
    return float(np.quantile(finite, 0.025)), float(np.quantile(finite, 0.975)), int(len(finite))


def cluster_bootstrap_pairs(
    by_case: dict[str, list[tuple[str, str]]],
    metric: Callable[[list[tuple[str, str]]], float],
    rng: np.random.Generator,
) -> tuple[float, float, int]:
    case_ids = list(by_case)
    if not case_ids:
        return math.nan, math.nan, 0
    estimates: list[float] = []
    for _ in range(BOOTSTRAP_REPS):
        sampled = rng.choice(case_ids, size=len(case_ids), replace=True)
        observations: list[tuple[str, str]] = []
        for case_id in sampled:
            observations.extend(by_case[str(case_id)])
        estimates.append(metric(observations))
    return percentile_ci(estimates)


def cluster_bootstrap_mean(values: dict[str, float], rng: np.random.Generator) -> tuple[float, float, int]:
    case_ids = list(values)
    if not case_ids:
        return math.nan, math.nan, 0
    estimates: list[float] = []
    for _ in range(BOOTSTRAP_REPS):
        sampled = rng.choice(case_ids, size=len(case_ids), replace=True)
        estimates.append(float(np.mean([values[str(case_id)] for case_id in sampled])))
    return percentile_ci(estimates)


def set_jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return 1.0 if not union else len(left & right) / len(union)


def set_dice(left: set[str], right: set[str]) -> float:
    denominator = len(left) + len(right)
    return 1.0 if denominator == 0 else 2.0 * len(left & right) / denominator


def fmt(value: float) -> str:
    return "NA" if not np.isfinite(value) else f"{value:.3f}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = pd.read_csv(DATA_DIR / "canonical_cases.csv")
    rating_cases = pd.read_csv(DATA_DIR / "latest_rating_cases.csv").fillna("")
    nodes = pd.read_csv(DATA_DIR / "latest_rating_nodes_post_l1.csv").fillna("")

    cases = cases[["source_id", "pair", "pair_label", "main_number"]]
    rating_cases = rating_cases.merge(cases, on="source_id", how="left", validate="many_to_one")
    nodes = nodes.merge(cases, on="source_id", how="left", validate="many_to_one")

    case_rating_map = {
        (row.source_id, row.annotator_id): row
        for row in rating_cases.itertuples(index=False)
    }
    node_groups = {
        (source_id, annotator_id): group.copy()
        for (source_id, annotator_id), group in nodes.groupby(["source_id", "annotator_id"])
    }

    metric_rows: list[dict[str, object]] = []
    confusion_rows: list[dict[str, object]] = []
    set_rows: list[dict[str, object]] = []
    structural_case_rows: list[dict[str, object]] = []
    missing_rows: list[dict[str, object]] = []

    def append_pair_metrics(
        *,
        analysis_set: str,
        pair: str,
        domain: str,
        granularity: str,
        by_case: dict[str, list[tuple[str, str]]],
        categories: list[str],
        label_version: str = "post_l1",
        node_scope: str = "case",
    ) -> None:
        flat = [observation for observations in by_case.values() for observation in observations]
        rng = np.random.default_rng(
            BOOTSTRAP_SEED + sum(ord(char) for char in analysis_set + pair + domain + granularity + label_version + node_scope)
        )
        specs = [
            ("cohens_kappa", lambda values: cohen_kappa(values, categories)),
            ("gwet_ac1", lambda values: gwet_ac1(values, categories)),
            ("agreement", lambda values: percent_agreement(values, categories)),
        ]
        for metric_name, function in specs:
            estimate = function(flat)
            ci_low, ci_high, valid_reps = cluster_bootstrap_pairs(by_case, function, rng)
            metric_rows.append(
                {
                    "analysis_set": analysis_set,
                    "pair": pair,
                    "domain": domain,
                    "granularity": granularity,
                    "label_version": label_version,
                    "node_scope": node_scope,
                    "metric": metric_name,
                    "n_cases": len(by_case),
                    "n_units": len(flat),
                    "estimate": estimate,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "bootstrap_valid_reps": valid_reps,
                }
            )

    for analysis_set, include_main in ANALYSIS_SETS.items():
        selected_cases = cases[cases["main_number"].map(include_main)]
        for pair, (aid_a, aid_b) in PAIR_ANNOTATORS.items():
            pair_cases = selected_cases[selected_cases["pair"] == pair].sort_values("main_number")

            analyzability_by_case: dict[str, list[tuple[str, str]]] = {}
            mutually_analyzable: list[str] = []
            for case in pair_cases.itertuples(index=False):
                left = case_rating_map[(case.source_id, aid_a)].analyzability
                right = case_rating_map[(case.source_id, aid_b)].analyzability
                analyzability_by_case[case.source_id] = [(left, right)]
                if left == "analyzable" and right == "analyzable":
                    mutually_analyzable.append(case.source_id)
            append_pair_metrics(
                analysis_set=analysis_set,
                pair=pair,
                domain="analyzability",
                granularity="binary",
                by_case=analyzability_by_case,
                categories=["analyzable", "not_analyzable"],
            )

            existence_by_case: dict[str, list[tuple[str, str]]] = {}
            gate_by_case: dict[str, list[tuple[str, str]]] = {}
            classification_maps: dict[tuple[str, str], dict[str, list[tuple[str, str]]]] = defaultdict(dict)

            for source_id in mutually_analyzable:
                left_nodes = node_groups[(source_id, aid_a)]
                right_nodes = node_groups[(source_id, aid_b)]
                left_map = {str(int(row.node_id)): row for row in left_nodes.itertuples(index=False)}
                right_map = {str(int(row.node_id)): row for row in right_nodes.itertuples(index=False)}
                original_ids = sorted(
                    {
                        node_id
                        for node_id, row in left_map.items()
                        if bool(row.is_original_node) and not bool(row.is_top)
                    }
                    | {
                        node_id
                        for node_id, row in right_map.items()
                        if bool(row.is_original_node) and not bool(row.is_top)
                    },
                    key=int,
                )

                existence_observations: list[tuple[str, str]] = []
                gate_observations: list[tuple[str, str]] = []
                for node_id in original_ids:
                    left = left_map[node_id]
                    right = right_map[node_id]
                    left_action = "keep" if left.action == "keep" else "delete"
                    right_action = "keep" if right.action == "keep" else "delete"
                    existence_observations.append((left_action, right_action))

                    if left_action != "keep" or right_action != "keep":
                        continue
                    if left.gate in {"AND", "OR"} and right.gate in {"AND", "OR"}:
                        gate_observations.append((left.gate, right.gate))

                    for label_version, column in [
                        ("post_l1", "hfacs"),
                        ("first_round", "hfacs_first_round"),
                    ]:
                        left_label = str(getattr(left, column)).strip()
                        right_label = str(getattr(right, column)).strip()
                        if not left_label or not right_label:
                            missing_rows.append(
                                {
                                    "analysis_set": analysis_set,
                                    "pair": pair,
                                    "source_id": source_id,
                                    "node_id": int(node_id),
                                    "label_version": label_version,
                                    "left_label": left_label,
                                    "right_label": right_label,
                                    "is_leaf_left": bool(left.is_leaf),
                                    "is_leaf_right": bool(right.is_leaf),
                                }
                            )
                            continue
                        for node_scope, include_node in [
                            ("leaf", bool(left.is_leaf) and bool(right.is_leaf)),
                            ("all_non_top", True),
                        ]:
                            if include_node:
                                classification_maps[(label_version, node_scope)].setdefault(source_id, []).append(
                                    (left_label, right_label)
                                )

                existence_by_case[source_id] = existence_observations
                gate_by_case[source_id] = gate_observations

                def retained_structure(frame: pd.DataFrame) -> tuple[set[str], set[tuple[str, str]], set[str]]:
                    kept = frame[frame["action"].isin(["keep", "added"])].copy()
                    kept_ids = {str(int(value)) for value in kept["node_id"]}
                    edges = {
                        (str(int(row.node_id)), str(int(row.parent_id)))
                        for row in kept.itertuples(index=False)
                        if not bool(row.is_top) and str(row.parent_id) not in {"", "0", "0.0"}
                    }
                    parent_ids = {parent for _, parent in edges}
                    leaves = {node_id for node_id in kept_ids if node_id not in parent_ids}
                    return kept_ids, edges, leaves

                _, edges_a, leaves_a = retained_structure(left_nodes)
                _, edges_b, leaves_b = retained_structure(right_nodes)
                structural_case_rows.append(
                    {
                        "analysis_set": analysis_set,
                        "pair": pair,
                        "source_id": source_id,
                        "edge_jaccard": set_jaccard(edges_a, edges_b),
                        "edge_exact": float(edges_a == edges_b),
                        "leaf_jaccard": set_jaccard(leaves_a, leaves_b),
                        "leaf_exact": float(leaves_a == leaves_b),
                    }
                )

            append_pair_metrics(
                analysis_set=analysis_set,
                pair=pair,
                domain="node_existence",
                granularity="keep_delete",
                by_case=existence_by_case,
                categories=["keep", "delete"],
                node_scope="all_non_top",
            )
            append_pair_metrics(
                analysis_set=analysis_set,
                pair=pair,
                domain="gate",
                granularity="and_or",
                by_case=gate_by_case,
                categories=["AND", "OR"],
                node_scope="all_non_top",
            )

            for (label_version, node_scope), by_case in classification_maps.items():
                transforms = [
                    ("detailed_22", DETAILED_22, lambda value: value),
                    ("detailed_20_non_merged", DETAILED_20, merge_non_hfacs),
                    ("tier_plus_non_5", TIER_5, tier_merge_non_hfacs),
                    ("tier_plus_non_7", TIER_7, tier),
                    ("binary_hfacs", BINARY_2, binary),
                ]
                for granularity, categories, transform in transforms:
                    transformed = {
                        source_id: [(transform(left), transform(right)) for left, right in observations]
                        for source_id, observations in by_case.items()
                    }
                    append_pair_metrics(
                        analysis_set=analysis_set,
                        pair=pair,
                        domain="hfacs_classification",
                        granularity=granularity,
                        by_case=transformed,
                        categories=categories,
                        label_version=label_version,
                        node_scope=node_scope,
                    )
                    if analysis_set == "primary_main11_50" and label_version == "post_l1" and node_scope == "leaf":
                        flat = [item for observations in transformed.values() for item in observations]
                        counts = Counter(flat)
                        for (left, right), count in sorted(counts.items()):
                            confusion_rows.append(
                                {
                                    "pair": pair,
                                    "granularity": granularity,
                                    "rater_a": left,
                                    "rater_b": right,
                                    "count": count,
                                }
                            )

            for label_version, column in [("post_l1", "hfacs"), ("first_round", "hfacs_first_round")]:
                for source_id in mutually_analyzable:
                    left_nodes = node_groups[(source_id, aid_a)]
                    right_nodes = node_groups[(source_id, aid_b)]

                    def label_set(frame: pd.DataFrame, allowed: set[str]) -> set[str]:
                        selected = frame[
                            (frame["action"] == "keep")
                            & frame["is_leaf"].astype(bool)
                            & frame[column].isin(allowed)
                        ]
                        return set(selected[column].astype(str))

                    for scope, allowed in [("hfacs19", set(HFACS_19)), ("all22", set(DETAILED_22))]:
                        left_set = label_set(left_nodes, allowed)
                        right_set = label_set(right_nodes, allowed)
                        set_rows.append(
                            {
                                "analysis_set": analysis_set,
                                "pair": pair,
                                "source_id": source_id,
                                "label_version": label_version,
                                "set_scope": scope,
                                "jaccard": set_jaccard(left_set, right_set),
                                "dice": set_dice(left_set, right_set),
                                "exact": float(left_set == right_set),
                                "rater_a_labels": json.dumps(sorted(left_set), ensure_ascii=False),
                                "rater_b_labels": json.dumps(sorted(right_set), ensure_ascii=False),
                            }
                        )

    metrics = pd.DataFrame(metric_rows)
    set_frame = pd.DataFrame(set_rows)
    structure_frame = pd.DataFrame(structural_case_rows)

    for keys, group in set_frame.groupby(["analysis_set", "pair", "label_version", "set_scope"]):
        analysis_set, pair, label_version, set_scope = keys
        for metric_name in ["jaccard", "dice", "exact"]:
            values = dict(zip(group["source_id"], group[metric_name]))
            estimate = float(group[metric_name].mean())
            rng = np.random.default_rng(
                BOOTSTRAP_SEED + sum(ord(char) for char in "".join(keys) + metric_name)
            )
            ci_low, ci_high, valid_reps = cluster_bootstrap_mean(values, rng)
            metric_rows.append(
                {
                    "analysis_set": analysis_set,
                    "pair": pair,
                    "domain": "case_multilabel",
                    "granularity": set_scope,
                    "label_version": label_version,
                    "node_scope": "leaf",
                    "metric": metric_name,
                    "n_cases": len(group),
                    "n_units": len(group),
                    "estimate": estimate,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "bootstrap_valid_reps": valid_reps,
                }
            )

    for keys, group in structure_frame.groupby(["analysis_set", "pair"]):
        analysis_set, pair = keys
        for metric_name in ["edge_jaccard", "edge_exact", "leaf_jaccard", "leaf_exact"]:
            values = dict(zip(group["source_id"], group[metric_name]))
            estimate = float(group[metric_name].mean())
            rng = np.random.default_rng(
                BOOTSTRAP_SEED + sum(ord(char) for char in analysis_set + pair + metric_name)
            )
            ci_low, ci_high, valid_reps = cluster_bootstrap_mean(values, rng)
            metric_rows.append(
                {
                    "analysis_set": analysis_set,
                    "pair": pair,
                    "domain": "structure",
                    "granularity": metric_name.replace("_jaccard", "").replace("_exact", ""),
                    "label_version": "post_l1",
                    "node_scope": "all_nodes",
                    "metric": "jaccard" if "jaccard" in metric_name else "exact",
                    "n_cases": len(group),
                    "n_units": len(group),
                    "estimate": estimate,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "bootstrap_valid_reps": valid_reps,
                }
            )

    metrics = pd.DataFrame(metric_rows).sort_values(
        ["analysis_set", "pair", "domain", "label_version", "node_scope", "granularity", "metric"]
    )
    metrics.to_csv(OUT_DIR / "reliability_metrics.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(confusion_rows).to_csv(
        OUT_DIR / "primary_leaf_post_l1_confusion_long.csv", index=False, encoding="utf-8-sig"
    )
    set_frame.to_csv(OUT_DIR / "case_multilabel_similarity.csv", index=False, encoding="utf-8-sig")
    structure_frame.to_csv(OUT_DIR / "case_structure_similarity.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(missing_rows).drop_duplicates().to_csv(
        OUT_DIR / "excluded_blank_labels.csv", index=False, encoding="utf-8-sig"
    )

    primary = metrics[
        (metrics["analysis_set"] == "primary_main11_50")
        & (metrics["domain"] == "hfacs_classification")
        & (metrics["label_version"] == "post_l1")
        & (metrics["node_scope"] == "leaf")
        & (metrics["metric"] == "cohens_kappa")
    ]
    summary = [
        "# 評価者間信頼性解析",
        "",
        "**作成日:** 2026-07-14",
        "",
        "## 主要結果",
        "",
        "Main 11-50、両評価者が分析可能とした症例、両者が保持した葉ノード、L1再評価反映後を主要集団とした。",
        "95%信頼区間は症例単位2,000回bootstrapで算出した。",
        "",
        "| ペア | 粒度 | N症例 | Nノード | Cohen's κ (95% CI) |",
        "|---|---|---:|---:|---:|",
    ]
    labels = {
        "detailed_22": "22カテゴリ",
        "tier_plus_non_5": "L1-L4 + 統合非HFACS",
        "binary_hfacs": "HFACS / 非HFACS",
    }
    for pair in PAIR_ANNOTATORS:
        for granularity in ["detailed_22", "tier_plus_non_5", "binary_hfacs"]:
            row = primary[(primary["pair"] == pair) & (primary["granularity"] == granularity)].iloc[0]
            summary.append(
                f"| {pair} | {labels[granularity]} | {int(row.n_cases)} | {int(row.n_units)} | "
                f"{fmt(row.estimate)} ({fmt(row.ci_low)}-{fmt(row.ci_high)}) |"
            )

    analyzability = metrics[
        (metrics["analysis_set"] == "primary_main11_50")
        & (metrics["domain"] == "analyzability")
        & (metrics["metric"].isin(["cohens_kappa", "gwet_ac1", "agreement"]))
    ]
    summary.extend(
        [
            "",
            "## 分析可能性",
            "",
            "| ペア | 指標 | N症例 | 推定値 (95% CI) |",
            "|---|---|---:|---:|",
        ]
    )
    for pair in PAIR_ANNOTATORS:
        for metric_name in ["cohens_kappa", "gwet_ac1", "agreement"]:
            row = analyzability[(analyzability["pair"] == pair) & (analyzability["metric"] == metric_name)].iloc[0]
            summary.append(
                f"| {pair} | {metric_name} | {int(row.n_cases)} | "
                f"{fmt(row.estimate)} ({fmt(row.ci_low)}-{fmt(row.ci_high)}) |"
            )

    summary.extend(
        [
            "",
            "## 解釈上の注意",
            "",
            "- κ、AC1、一致率を併記し、カテゴリ偏在によるκ paradoxを隠さない。",
            "- 22カテゴリのκが低い場合も除外せず、詳細HFACS結果の解釈を弱める。",
            "- node existenceにdeleteが存在しない場合、観測一致率は算出できてもκは定義不能となる。",
            "- AND/ORやedgeの高一致は、既存LLM構造を編集する画面によるanchoringを含む。独立な構造妥当性とはみなさない。",
            "- 全Main、全非頂上ノード、L1再評価前、症例レベルmulti-label、構造指標はCSVに併記した。",
            "",
            "## 出力",
            "",
            "- `reliability_metrics.csv`: 全指標と症例cluster bootstrap CI",
            "- `primary_leaf_post_l1_confusion_long.csv`: 主要解析の混同行列long形式",
            "- `case_multilabel_similarity.csv`: 症例単位Jaccard/Dice/完全一致",
            "- `case_structure_similarity.csv`: edge・葉集合の症例単位一致",
            "- `excluded_blank_labels.csv`: 条件付き分類から除外した欠測ラベル",
        ]
    )
    (OUT_DIR / "reliability_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    print("\n".join(summary[:45]))
    print(f"\nWrote reliability results to: {OUT_DIR}")


if __name__ == "__main__":
    main()
