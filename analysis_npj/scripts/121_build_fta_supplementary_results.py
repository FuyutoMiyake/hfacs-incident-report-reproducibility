"""Assemble FTA supplementary tables from preserved outputs; do not rerun models."""

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "analysis_npj/manuscript/supplementary_results_20261005"
OUT = BASE / "fta_extension"
GATE = ROOT / "analysis_npj/results/fta_added_value"
FLAT = ROOT / "analysis_npj/results/flat_vs_fta"
PRIMARY = "primary_main11_50"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def find(rows, **key):
    matches = [row for row in rows if all(row[k] == v for k, v in key.items())]
    assert len(matches) == 1, (key, len(matches))
    return matches[0]


def number(value):
    return f"{float(value):.3f}"


def interval(row):
    return f"{number(row['estimate'])} ({number(row['ci_low'])} to {number(row['ci_high'])})"


def verify_native(payload):
    path = BASE / "fta_final_readback/document-result.json"
    if not path.exists():
        return
    before = json.loads((BASE / "fta_before_readback/document-result.json").read_text())["structuredContent"]
    after = json.loads(path.read_text())["structuredContent"]
    old_blocks = before["tabs"][0]["body"]["content"]
    new_blocks = after["tabs"][0]["body"]["content"]
    # The insertion starts after the original three tables and their notes.
    original_prefix = [block for block in old_blocks if block.get("endIndex", 0) <= 6643]
    preserved_prefix = [block for block in new_blocks if block.get("endIndex", 0) <= 6643]
    assert original_prefix == preserved_prefix, "Existing content or formatting changed"
    old_tables = [b["table"] for b in old_blocks if "table" in b]
    new_tables = [b["table"] for b in new_blocks if "table" in b]
    assert len(old_tables) == 3 and len(new_tables) == 6
    assert old_tables == new_tables[:3]
    checked = 0
    for actual, expected in zip(new_tables[3:], payload["tables"], strict=True):
        assert len(actual["tableRows"]) == len(expected["rows"])
        for ri, (row, values) in enumerate(zip(actual["tableRows"], expected["rows"], strict=True)):
            assert len(row["tableCells"]) == len(values)
            for cell, value in zip(row["tableCells"], values, strict=True):
                runs = [e["textRun"] for b in cell["content"]
                        for e in b.get("paragraph", {}).get("elements", []) if "textRun" in e]
                assert "".join(r["content"] for r in runs).strip() == value
                for run in runs:
                    assert run["textStyle"]["fontSize"]["magnitude"] == 10
                    if run["content"].strip():
                        assert run["textStyle"].get("bold", False) == (ri == 0)
                checked += 1
    result = dict(document_id=after["documentId"], revision=after["revisionId"],
                  existing_tables_preserved=True, existing_prefix_preserved=True,
                  total_tables=6, added_cells_checked=checked, cell_text_exact=True,
                  source_hashes=payload["sources"],
                  scope="Assembly from existing outputs and native readback; not independent statistical replication")
    (OUT / "verification.json").write_text(json.dumps(result, indent=2) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rankings = read_csv(GATE / "global_rankings.csv")
    metrics = read_csv(GATE / "global_ranking_metrics.csv")
    boot = read_csv(GATE / "bootstrap_global_recall.csv")
    stability = read_csv(GATE / "bootstrap_top5_stability.csv")
    means = read_csv(FLAT / "aggregate_metrics.csv")
    micro = read_csv(FLAT / "micro_category_metrics.csv")
    differences = read_csv(FLAT / "paired_differences.csv")
    selected = []

    s4 = [["Ranking method", "Top five categories (rank order)", "Recall@5", "NDCG@5"]]
    for method, label in [("frequency", "Frequency"), ("cooccurrence", "Co-occurrence"), ("fta", "FTA structural")]:
        top = sorted([r for r in rankings if r["analysis_set"] == PRIMARY and r["method"] == method],
                     key=lambda r: int(r["rank"]))[:5]
        recall = find(metrics, analysis_set=PRIMARY, method=method, metric="recall@5")
        ndcg = find(metrics, analysis_set=PRIMARY, method=method, metric="ndcg@5")
        assert (int(recall["n_cases"]), int(recall["n_target_cases"]), int(recall["n_target_occurrences"])) == (87, 49, 62)
        assert math.isclose(float(recall["estimate"]), 7 / 62)
        s4.append([label, ", ".join(r["hfacs"] for r in top), number(recall["estimate"]), number(ndcg["estimate"])])
    bootstrap = find(boot, analysis_set=PRIMARY, metric="fta_minus_frequency")
    observed = float(s4[3][2]) - float(s4[1][2])
    assert observed == 0
    top_fta = s4[3][1].split(", ")
    min_rate = min(float(find(stability, analysis_set=PRIMARY, method="fta", hfacs=code)["top5_selection_rate"])
                   for code in top_fta)
    decision = json.loads((GATE / "gate_decision.json").read_text())
    assert decision["overall_pass"] is False and math.isclose(min_rate, 0.8605)
    gate_lines = [
        "Scale-up conditions: recall-difference lower 95% confidence bound > 0, not met; minimum FTA top-five selection rate >= 0.70, met (0.861); top five different from frequency, not met; no improvement-quotation leakage flags, met. Overall decision: do not scale up.",
        "Observed FTA-minus-frequency recall@5 difference: 0.000. The 2,000-resample percentile interval was -0.415 to 0.194, with rankings recomputed in each resample. The saved bootstrap mean (-0.084) is not the observed difference.",
    ]

    def comparison(aset, target, metric, *, grounded=False, scope=None):
        names = ["fta_grounded", "flat_grounded"] if grounded else ["fta", "flat"]
        if scope is None:
            rows = [find(means, analysis_set=aset, target=target, method=name, metric=metric) for name in names]
            diff_key = dict(analysis_set=aset, target=target,
                            comparison="fta_grounded_minus_flat_grounded" if grounded else "fta_minus_flat", metric=metric)
        else:
            rows = [find(micro, analysis_set=aset, scope=scope, method=name) for name in names]
            diff_key = dict(analysis_set=aset, target=scope, comparison="fta_minus_flat", metric=f"micro_{metric}")
        delta = find(differences, **diff_key)
        estimates = [float(row["estimate"] if scope is None else row[metric]) for row in rows]
        assert math.isclose(estimates[0] - estimates[1], float(delta["estimate"]), abs_tol=1e-12)
        assert len({row["n_cases"] for row in [*rows, delta]}) == 1
        selected.append(dict(condition=aset, target=target if scope is None else scope,
                             metric=metric if scope is None else f"micro_{metric}",
                             comparison=delta["comparison"], n_cases=delta["n_cases"],
                             fta=estimates[0], direct=estimates[1], difference=float(delta["estimate"]),
                             ci_low=float(delta["ci_low"]), ci_high=float(delta["ci_high"])))
        return [number(v) for v in estimates] + [interval(delta)], delta["n_cases"]

    s5 = [["Endpoint", "FTA", "Direct classification", "Difference: FTA minus direct (95% CI)"]]
    for metric in ["precision", "recall"]:
        values, n = comparison(PRIMARY, "augmented_reference", metric)
        assert n == "87"
        s5.append([f"Mean {metric}", *values])
    for scope, label in [("all_hfacs", "All 19 HFACS categories"), ("l3_l4", "L3/L4 combined")]:
        for metric in ["precision", "recall", "f1"]:
            values, n = comparison(PRIMARY, "augmented_reference", metric, scope=scope)
            s5.append([f"{label}: micro-{metric.upper() if metric == 'f1' else metric}", *values])

    s6 = [["Analysis condition / records", "Endpoint", "FTA", "Direct classification", "Difference (95% CI)"]]
    for metric in ["precision", "recall"]:
        values, n = comparison("sensitivity_main1_50", "augmented_reference", metric)
        s6.append([f"Main 1-50 / {n}", f"Mean {metric}", *values])
    for scope, label in [("all_hfacs", "All HFACS: micro-F1"), ("l3_l4", "L3/L4: micro-F1")]:
        values, n = comparison("sensitivity_main1_50", "augmented_reference", "f1", scope=scope)
        s6.append([f"Main 1-50 / {n}", label, *values])
    for metric in ["precision", "recall"]:
        values, n = comparison(PRIMARY, "augmented_reference", metric, grounded=True)
        s6.append([f"Traceable quotations / {n}", f"Mean {metric}", *values])
    for metric in ["precision", "recall"]:
        values, n = comparison(PRIMARY, "improvement_holdout", metric)
        assert n == "49"
        s6.append([f"Improvement-related targets / {n}", f"Mean {metric}", *values])

    notes = [
        "Population: 87 adjudicated-analysable RSv1 records, Main 11-50 within each pair. Improvement-related targets occurred in 49 records, comprising 62 report-category occurrences; recall@5 was 7/62. Targets combined adjudicated HFACS leaf categories with verbatim improvement quotations and reviewer-added categories, deduplicated within each report. Frequency counts reports containing a leaf category; co-occurrence counts weighted within-report category co-occurrences. FTA ranks categories by interruption of the generated AND/OR tree when their leaves are set false, with minimal-cut-set coverage as a tie-breaker. NDCG is normalised discounted cumulative gain.",
        "Both methods used Kimi K2.5 and event description plus background, without improvement measures. The reference was the report-level set of retained adjudicated RSv1 HFACS leaf categories plus reviewer-added categories. Mean precision and recall were calculated per report and then averaged. Micro metrics pooled report-category true positives, false positives, and false negatives; repeated categories within a report counted once. Paired differences use the same records, with 95% percentile intervals from 2,000 record-cluster bootstrap resamples. L3/L4 metrics pooled the categories in those two layers.",
        "Main 1-50 includes all 112 adjudicated-analysable RSv1 records. The traceable-quotation analysis retained predictions linked to quotations locatable in event description or background; this is a traceability filter, not a full-support judgement. The alternative improvement-related target analysis used the 49 records with nonempty targets defined in Table S4. Means assigned precision 1 when both prediction and reference were empty, precision 0 when only the prediction was empty, and recall 1 when the reference was empty. Differences and 95% percentile intervals use 2,000 paired record-cluster resamples. These analyses reuse RSv1 records with alternative populations or prediction/reference conditions.",
    ]
    tables = [dict(title="Table S4. FTA ranking comparison and scale-up decision", rows=s4,
                   note=notes[0], paragraphs=gate_lines, column_widths=[130,360,110,158]),
              dict(title="Table S5. FTA versus direct classification: primary RSv1 comparison", rows=s5,
                   note=notes[1], paragraphs=[], column_widths=[265,85,120,288]),
              dict(title="Table S6. Sensitivity and alternative-target analyses of FTA versus direct classification", rows=s6,
                   note=notes[2], paragraphs=[], column_widths=[190,135,65,100,268])]
    sources = [GATE / name for name in ["global_rankings.csv", "global_ranking_metrics.csv", "bootstrap_global_recall.csv",
                                      "bootstrap_top5_stability.csv", "gate_decision.json"]]
    sources += [FLAT / name for name in ["aggregate_metrics.csv", "micro_category_metrics.csv", "paired_differences.csv"]]
    sources += [ROOT / "analysis_npj/results/improvement_holdout/improvement_target_sets.csv"]
    sources += [ROOT / "analysis_npj/scripts" / name for name in ["04_generate_no_improvement.py", "05_build_improvement_holdout.py",
                 "06_fta_added_value.py", "08_generate_flat_baseline.py", "09_compare_flat_vs_fta.py"]]
    payload = dict(tables=tables, sources=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                        for p in sources if p.exists()],
                   gate_observed_difference=observed, gate_bootstrap_mean=float(bootstrap["estimate"]),
                   assembly_script="analysis_npj/scripts/121_build_fta_supplementary_results.py")
    (OUT / "tables.json").write_text(json.dumps(payload, indent=2) + "\n")
    with (OUT / "selected_comparisons.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=selected[0].keys())
        writer.writeheader()
        writer.writerows(selected)
    text = ["# FTA supplementary results (draft)", "Prepared: 2026-10-05", "FTA: fault tree analysis; HFACS: Human Factors Analysis and Classification System; RS: reference standard; CI: confidence interval; NDCG: normalised discounted cumulative gain."]
    for table in tables:
        text += ["", f"## {table['title']}", "| " + " | ".join(table["rows"][0]) + " |",
                 "| " + " | ".join(["---"] * len(table["rows"][0])) + " |"]
        text += ["| " + " | ".join(row) + " |" for row in table["rows"][1:]]
        text += ["", table["note"], *table["paragraphs"]]
    (OUT / "fta_supplementary_results.md").write_text("\n\n".join(text) + "\n")
    verify_native(payload)
    print(json.dumps(dict(output=str(OUT), tables=3, data_rows=[len(t["rows"])-1 for t in tables],
                          comparisons_checked=len(selected), gate_observed_difference=observed,
                          gate_bootstrap_mean=float(bootstrap["estimate"]))))


if __name__ == "__main__":
    main()
