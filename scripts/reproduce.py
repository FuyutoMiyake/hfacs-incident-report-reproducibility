"""Offline recomputation from pseudonymised numeric units; no AI/API calls."""

import argparse
import csv
import importlib.util
import json
import math
import platform
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DATA = ROOT / "data"
CHECKS = []


def read(path):
    return json.loads(path.read_text())


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "analysis_npj/scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compare(actual, expected, label):
    if isinstance(expected, dict):
        for k, v in expected.items():
            compare(actual[k], v, label + "." + k)
    elif isinstance(expected, list):
        assert len(actual) == len(expected), label
        for i, (a, b) in enumerate(zip(actual, expected, strict=True)):
            compare(a, b, label + f"[{i}]")
    elif isinstance(expected, (float, int)) and not isinstance(expected, bool):
        assert actual is not None and math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), (label, actual, expected)
        CHECKS.append(label)
    else:
        assert actual == expected, (label, actual, expected)


def run_script(name):
    subprocess.run([sys.executable, str(ROOT / "analysis_npj/scripts" / name)], check=True, cwd=ROOT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-rsv1-human", action="store_true", help="Recompute all initial reliability analyses (slower)")
    parser.add_argument("--figures", action="store_true", help="Requires reportlab, pypdf and pdftoppm")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    report = {"python": platform.python_version(), "new_model_calls": False,
              "scope": "Statistics conditional on preserved categorical ratings and saved semantic correspondences"}

    if args.include_rsv1_human:
        run_script("02_reliability_analysis.py")
        expected = list(csv.DictReader((DATA / "expected_rsv1_reliability.csv").open(encoding="utf-8-sig")))
        actual = list(csv.DictReader((ROOT / "analysis_npj/results/reliability/reliability_metrics.csv").open(encoding="utf-8-sig")))
        keys = ["analysis_set", "pair", "domain", "label_version", "node_scope", "granularity", "metric"]
        index = {tuple(r[k] for k in keys): r for r in actual}
        assert len(actual) == len(expected) == len(index)
        for r in expected:
            label = ":".join(r[k] for k in keys)
            a = index[tuple(r[k] for k in keys)]
            for k in ["n_cases", "n_units", "estimate", "ci_low", "ci_high"]:
                if r[k] in ["", "nan"]:
                    assert a[k] in ["", "nan"], (label, k)
                else:
                    compare(float(a[k]), float(r[k]), "RSv1.human." + label + "." + k)
        report["rsv1_human_rows"] = len(actual)

    final = load("final_eval", "79_evaluate_frozen_final_50.py")
    final_base = ROOT / "analysis_npj/prompt_adaptation/split50x3_20260722"
    report["rsv1_final"] = {}
    for model, filename in [("gpt_5_6_sol", "final_results/final_results.json"),
                            ("kimi_k26", "final_results_kimi_k26/kimi_k26_final_results.json")]:
        rows = read(DATA / f"rsv1_final_{model}_units.json")
        expected = read(final_base / filename)
        result = {key: final.with_cluster_ci(rows, getattr(final, key)) for key in ["detailed20", "tier5", "binary"]}
        for key, value in result.items():
            compare(value, expected[key], f"RSv1.final.{model}.{key}")
        report["rsv1_final"][model] = result

    rs = load("rs2", "110_analyze_rsv2_complete.py")
    expected = read(ROOT / "analysis_npj/analysis_runs/consultation_data_audit_20261002/analysis.json")
    factors = read(DATA / "rsv2_factor_case_metrics.json")
    extraction = {}
    for mode in ["all", "hfacs_only", "hfacs_or_indeterminate"]:
        for matching in ["strict", "same_proposition", "partial_sensitivity"]:
            items = [r for r in factors if r["eligibility"] == mode and r["matching"] == matching]
            key = mode + ":" + matching
            extraction[key] = {p: rs.factor_summary([r for r in items if p == "overall" or r["pair_id"] == p])
                               for p in ["overall", "AB", "CD", "EF"]}
    compare(extraction, expected["extraction"], "RSv2.extraction")
    report["rsv2_extraction"] = extraction

    records = read(DATA / "rsv2_analyzability_case_metrics.json")
    agreement = {}
    for pair in ["AB", "CD", "EF"]:
        rows = [r for r in records if r["pair_id"] == pair]
        agreement[pair] = {}
        for stage in ["before", "after"]:
            def metric(items):
                return rs.agree([r[stage][0] for r in items], [r[stage][1] for r in items], rs.LEVELS, True)
            value = metric(rows)
            value["kappa_ci95"] = rs.bootstrap(rows, lambda items: metric(items)["kappa"])
            agreement[pair][stage] = value
    compare(agreement, expected["analyzability_agreement"], "RSv2.analysability")
    transition = Counter((b, a) for r in records for b, a in zip(r["before"], r["after"], strict=True))
    matrix = [[transition[(b, a)] for a in rs.LEVELS] for b in rs.LEVELS]
    compare(matrix, expected["transitions"], "RSv2.transitions")
    report["rsv2_analyzability"] = agreement
    report["transitions"] = matrix

    units = read(DATA / "rsv2_matched_classification_units.json")
    paired = {}
    for p in ["overall", "AB", "CD", "EF"]:
        before = {(r["source_id"], r["left_id"], r["right_id"]): r for r in units["before"] if p == "overall" or r["pair_id"] == p}
        joint = [(before[(r["source_id"], r["left_id"], r["right_id"])], r) for r in units["after"] if p == "overall" or r["pair_id"] == p]
        common = [(a, b) for a, b in joint if all(x[k] for x in [a, b] for k in ["layer_left", "layer_right"])]
        singles = [(a, b) for a, b in common if all(len(x[k]) == 1 for x in [a, b] for k in ["layer_left", "layer_right"])]
        def rate(stage, overlap):
            return sum(bool(set(x[stage]["layer_left"]) & set(x[stage]["layer_right"])) if overlap else x[stage]["layer_equal"] for x in common) / len(common) if common else None
        paired[p] = dict(n_matched=len(joint), n_both_stage_classified=len(common),
            exact_before_fixed_denominator=rate(0, False), exact_after_fixed_denominator=rate(1, False),
            overlap_before_fixed_denominator=rate(0, True), overlap_after_fixed_denominator=rate(1, True),
            n_singleton_in_both_stages=len(singles),
            singleton_before_same_units=rs.agree([a["layer_left"][0] for a, b in singles], [a["layer_right"][0] for a, b in singles], ["L1", "L2", "L3", "L4"]),
            singleton_after_same_units=rs.agree([b["layer_left"][0] for a, b in singles], [b["layer_right"][0] for a, b in singles], ["L1", "L2", "L3", "L4"]))
    compare(paired, expected["classification_paired_same_units"], "RSv2.layers")
    report["rsv2_layers"] = paired

    refs = read(DATA / "rsv2_consensus_codes.json")
    consensus = {}
    for p in ["overall", "AB", "CD", "EF"]:
        rows = [r for r in refs if p == "overall" or r["pair_id"] == p]
        fs = [f for r in rows for f in r["factors"]]
        consensus[p] = dict(cases=len(rows), factors=len(fs),
            analyzability=dict(Counter(r["analyzability"] for r in rows)),
            case_resolution_stored=dict(Counter(r["case_resolution_status"] or "missing" for r in rows)),
            factor_resolution_stored=dict(Counter(f["resolution_status"] or "missing" for f in fs)),
            multilabel_factors=sum(len(rs.codes(f)) > 1 for f in fs),
            multilayer_factors=sum(len(rs.layers(f)) > 1 for f in fs), unclassified_factors=sum(not rs.codes(f) for f in fs))
    compare(consensus, expected["consensus"], "RSv2.consensus")
    report["rsv2_consensus"] = consensus

    ai = read(DATA / "rsv2_ai_classification_units.json")
    single = [r for r in ai if r["singleton_hfacs_reference"]]
    clusters = [{"source_id": r["source_id"], "pair_id": r["pair_id"],
                 "units": [u for u in single if u["source_id"] == r["source_id"]]} for r in records]
    ai_result = {}
    for name, layer in [("singleton_hfacs_detailed", False), ("singleton_hfacs_layer", True)]:
        def metric(items):
            labels = ["L1", "L2", "L3", "L4", "nonHFACS"] if layer else sorted(rs.HFACS | {"CoP", "OTHER", "INAPPROPRIATE"})
            ref = [u["human_layers" if layer else "human_codes"][0] for u in items]
            pred = [(u["ai_layer"] or "nonHFACS") if layer else u["ai_code"] for u in items]
            return rs.agree(ref, pred, labels)
        value = metric(single)
        value["case_bootstrap_ci95"] = rs.bootstrap(clusters, lambda items: metric([u for r in items for u in r["units"]])["kappa"])
        compare(value, expected["ai_conditional_exploratory"][name], "RSv2.AI." + name)
        ai_result[name] = value
    for key, rows in [("label_any_hit", [r for r in ai if r["human_codes"]]),
                      ("hfacs_label_any_hit", [r for r in ai if r["human_layers"]])]:
        value = sum(r["hit_any_human_code"] for r in rows) / len(rows)
        compare(value, expected["ai_conditional_exploratory"][key], "RSv2.AI." + key)
        ai_result[key] = value
    report["rsv2_AI"] = ai_result

    primary = [r for r in factors if r["eligibility"] == "hfacs_or_indeterminate" and r["matching"] == "same_proposition"]
    for flag in [True, False]:
        compare(rs.factor_summary([r for r in primary if r["actor_unclear_either"] == flag]),
                expected["actor_unclear_association_exploratory"][str(flag)], "RSv2.actor_group." + str(flag))
    finite = [r for r in primary if r["f1"] is not None]
    rho = rs.spearmanr([r["f1"] for r in finite], [r["time_mean_minutes"] for r in finite])
    compare(dict(n=len(finite), rho=float(rho.statistic), p=float(rho.pvalue)),
            expected["factor_f1_time_spearman_exploratory"], "RSv2.time_correlation")
    times = read(DATA / "rsv2_recorded_times.json")
    for stage, key in [("before", "original_time_minutes"), ("after", "phase2_active_time_minutes")]:
        compare(rs.dist([r["minutes"] for r in times if r["stage"] == stage]), expected[key], "RSv2." + key)
    trace = read(DATA / "rsv2_evidence_traceability.json")
    for kind in ["independent", "consensus"]:
        rows = [r for r in trace if r["type"] == kind]
        compare(dict(factors=len(rows), all_quotes_traceable=sum(r["all_quotes_traceable"] for r in rows),
                     improvement_only=sum(r["only_improvement_evidence"] for r in rows)),
                expected["evidence_traceability"][kind], "RSv2.quotation_flags." + kind)
    graph = read(DATA / "rsv2_graph_case_metrics.json")
    for p in ["overall", "AB", "CD", "EF"]:
        rows = [r for r in graph if p == "overall" or r["pair_id"] == p]
        value = {k: sum(r[k] for r in rows) for k in ["left_edges", "right_edges", "shared_directed", "shared_adjacency"]}
        value |= dict(cases=len(rows), directed_micro_f1=rs.f1(value["left_edges"], value["right_edges"], value["shared_directed"]))
        compare(value, expected["graph_exploratory"][p], "RSv2.relations." + p)

    base = ROOT / "analysis_npj/manuscript/supplementary_results_20261005"
    for script, rel, label in [
        ("120_build_rsv1_supplementary_results.py", "tables.json", "S1-S3"),
        ("121_build_fta_supplementary_results.py", "fta_extension/tables.json", "S4-S6"),
        ("122_build_rsv2_supplementary_results.py", "rsv2_extension/tables.json", "S7-S11"),
    ]:
        run_script(script)
        actual = read(base / rel)["tables"]
        expected_tables = read(DATA / f"expected_tables_{label}.json")
        for a, b in zip(actual, expected_tables, strict=True):
            assert a["title"] == b["title"] and a["rows"] == b["rows"], label
    report["supplementary_tables"] = "11 tables: all titles and cell text identical to preserved tables"
    if args.figures:
        run_script("118_build_ijmi_figures.py")
    report["numeric_checks_passed"] = len(CHECKS)
    report["checks"] = CHECKS
    (OUT / "recomputation.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: report[k] for k in ["python", "new_model_calls", "numeric_checks_passed", "supplementary_tables"]}))


if __name__ == "__main__":
    main()
