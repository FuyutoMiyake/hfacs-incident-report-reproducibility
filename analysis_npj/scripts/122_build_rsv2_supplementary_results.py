"""Assemble RSv2 Results supplements from locked outputs, without model reruns."""

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "analysis_npj/manuscript/supplementary_results_20261005"
RUN = ROOT / "analysis_npj/analysis_runs/consultation_data_audit_20261002"
OUT = BASE / "rsv2_extension"
PAIRS = ["overall", "AB", "CD", "EF"]


def num(value):
    return f"{value:.3f}"


def rate(count, total):
    return f"{count}/{total} ({100 * count / total:.1f}%)"


def count_from_rate(value, total):
    count = round(value * total)
    assert math.isclose(value, count / total, abs_tol=1e-12)
    return count


def ci(value, bounds):
    return f"{num(value)} ({num(bounds['low'])} to {num(bounds['high'])})"


def verify_native(payload):
    final = BASE / "rsv2_final_readback/document-result.json"
    if not final.exists():
        return
    before = json.loads((BASE / "rsv2_before_readback/document-result.json").read_text())["structuredContent"]
    after = json.loads(final.read_text())["structuredContent"]
    old = before["tabs"][0]["body"]["content"]
    new = after["tabs"][0]["body"]["content"]
    old_tables = [b["table"] for b in old if "table" in b]
    new_tables = [b["table"] for b in new if "table" in b]
    assert len(old_tables) == 6 and len(new_tables) == 11
    assert old_tables == new_tables[:6], "Existing tables changed"
    old_prefix = [b for b in old if b.get("endIndex", 0) <= 10964]
    new_prefix = [b for b in new if b.get("endIndex", 0) <= 10964]
    assert old_prefix == new_prefix, "Existing manuscript-facing content changed"
    checked = 0
    for actual, expected in zip(new_tables[6:], payload["tables"], strict=True):
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
    paragraphs = ["".join(e.get("textRun", {}).get("content", "")
                          for e in b.get("paragraph", {}).get("elements", [])) for b in new]
    text = "".join(paragraphs)
    for section in payload["text_sections"]:
        assert section["title"] in text
        assert all(p in text for p in section["paragraphs"])
    result = dict(document_id=after["documentId"], revision=after["revisionId"],
                  existing_tables_preserved=True, existing_prefix_preserved=True,
                  total_tables=11, added_cells_checked=checked,
                  cell_text_exact=True, source_hashes=payload["sources"],
                  scope="Saved-output assembly and native readback, not independent statistical replication")
    (OUT / "verification.json").write_text(json.dumps(result, indent=2) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = json.loads((RUN / "analysis.json").read_text())
    main_rule = d["extraction"]["hfacs_or_indeterminate:same_proposition"]["overall"]
    assert (main_rule["cases"], main_rule["left_factors"], main_rule["right_factors"], main_rule["matched"], main_rule["both_empty"]) == (60, 81, 95, 37, 14)
    s7 = [["Eligibility / matching", "Factor counts: left / right", "Matched pairs", "Micro-F1 (95% CI)", "Both-empty records"]]
    eligibility = [("hfacs_or_indeterminate", "HFACS or indeterminate"), ("hfacs_only", "HFACS only"), ("all", "All factors")]
    matching = [("same_proposition", "same proposition"), ("strict", "same proposition + shared quotation"), ("partial_sensitivity", "including partial overlap")]
    for ek, en in eligibility:
        for mk, mn in matching:
            v = d["extraction"][f"{ek}:{mk}"]["overall"]
            assert v["cases"] == 60
            assert math.isclose(v["micro_f1"], 2 * v["matched"] / (v["left_factors"] + v["right_factors"]))
            s7.append([f"{en}: {mn}", f"{v['left_factors']} / {v['right_factors']}", str(v["matched"]),
                       ci(v["micro_f1"], v["micro_f1_ci95"]), str(v["both_empty"])])

    refs = d["consensus"]
    assert sum(refs[p]["factors"] for p in PAIRS[1:]) == refs["overall"]["factors"] == 110
    s8 = [["Measure / counting unit", "All pairs", "AB", "CD", "EF"]]
    measures = [("Records", "cases", None), ("Consensus factors", "factors", None),
                ("Records: analysable without uncertainty", "analyzability", "clear"),
                ("Records: analysable with uncertainty", "analyzability", "uncertain"),
                ("Records: not analysable", "analyzability", "not_analyzable"),
                ("Factors: multiple labels", "multilabel_factors", None),
                ("Factors: multiple HFACS layers", "multilayer_factors", None),
                ("Factors: no classification", "unclassified_factors", None),
                ("Human factor code: source-confirmed", "factor_resolution_stored", "source_confirmed"),
                ("Human factor code: rule-adjudicated", "factor_resolution_stored", "rule_adjudicated"),
                ("Human factor code: unresolved", "factor_resolution_stored", "unresolved"),
                ("Human factor code: missing", "factor_resolution_stored", "missing")]
    for label, key, subkey in measures:
        values = [refs[p][key] if subkey is None else refs[p][key].get(subkey, 0) for p in PAIRS]
        assert values[0] == sum(values[1:])
        s8.append([label, *map(str, values)])
    assert sum(refs["overall"]["factor_resolution_stored"].values()) == 110

    transitions = d["transitions"]
    assert sum(map(sum, transitions)) == 120
    improved = sum(transitions[i][j] for i in range(3) for j in range(3) if j > i)
    worsened = sum(transitions[i][j] for i in range(3) for j in range(3) if j < i)
    unchanged = sum(transitions[i][i] for i in range(3))
    assert (improved, worsened, unchanged) == (19, 7, 94)
    s9 = [["Reviewer pair / records", "Exact agreement: before", "Exact agreement: after", "Weighted kappa: before (95% CI)", "Weighted kappa: after (95% CI)"]]
    exact_totals = [0, 0]
    for p in PAIRS[1:]:
        b, a = [d["analyzability_agreement"][p][t] for t in ["before", "after"]]
        assert b["n"] == a["n"] == 20
        counts = [count_from_rate(v["raw"], v["n"]) for v in [b, a]]
        exact_totals = [total + n for total, n in zip(exact_totals, counts)]
        s9.append([f"{p} / 20", rate(counts[0], 20), rate(counts[1], 20),
                   ci(b["kappa"], b["kappa_ci95"]), ci(a["kappa"], a["kappa_ci95"])])
    assert exact_totals == [31, 26]
    s9.append(["All pairs / 60", rate(31, 60), rate(26, 60), "Not pooled", "Not pooled"])

    s10 = [["Reviewer pair", "Matched factors with layers at both stages", "Exact layer-set agreement: before -> after", "At least one shared layer: before -> after", "Single-layer factors at both stages", "Nominal kappa: before -> after"]]
    for p in PAIRS:
        v = d["classification_paired_same_units"][p]
        n = v["n_both_stage_classified"]
        before_exact, after_exact, before_overlap, after_overlap = [count_from_rate(v[k], n) for k in ["exact_before_fixed_denominator", "exact_after_fixed_denominator", "overlap_before_fixed_denominator", "overlap_after_fixed_denominator"]]
        ns = v["n_singleton_in_both_stages"]
        kb, ka = [v[t]["kappa"] for t in ["singleton_before_same_units", "singleton_after_same_units"]]
        s10.append(["All pairs" if p == "overall" else p, str(n),
                    f"{rate(before_exact, n)} -> {rate(after_exact, n)}",
                    f"{rate(before_overlap, n)} -> {rate(after_overlap, n)}", str(ns), f"{num(kb)} -> {num(ka)}"])
    assert d["classification_paired_same_units"]["overall"]["n_both_stage_classified"] == 32

    ai = d["ai_conditional_exploratory"]
    assert (ai["units"], ai["labeled_units"], ai["hfacs_labeled_units"], ai["unclassified_not_scored"]) == (110, 105, 90, 5)
    s11 = [["Evaluation population / endpoint", "Factors evaluated", "Agreement or candidate hits", "Nominal kappa (95% CI)"]]
    for name, nkey, hkey in [("Any reference label: candidate hit", "labeled_units", "label_any_hit"), ("At least one HFACS reference label: candidate hit", "hfacs_labeled_units", "hfacs_label_any_hit")]:
        n = ai[nkey]
        s11.append([name, str(n), rate(count_from_rate(ai[hkey], n), n), "Not calculated"])
    for key, name in [("singleton_hfacs_detailed", "Single HFACS reference label: detailed category"), ("singleton_hfacs_layer", "Single HFACS reference label: HFACS layer")]:
        v = ai[key]
        assert v["n"] == 75
        s11.append([name, str(v["n"]), rate(count_from_rate(v["raw"], v["n"]), v["n"]), ci(v["kappa"], v["case_bootstrap_ci95"])])

    tables = [
        dict(title="Table S7. RSv2 factor-extraction agreement: eligibility and matching sensitivity", rows=s7, column_widths=[260,115,75,220,88],
             note="All conditions used the same 60 records and AI-assisted one-to-one factor correspondences. Left and right counts pool the first and second reviewers within each pair, not two reviewers of all 60 records. Main condition: HFACS or indeterminate eligibility and same-proposition matching. Strict matching additionally required a shared quotation; partial matching admitted saved partial-overlap correspondences. Both-empty records were counted separately and not assigned F1 = 1. Intervals are saved 95% percentile intervals from 3,000 record-cluster bootstrap resamples stratified by pair."),
        dict(title="Table S8. RSv2 consensus dataset and stored human resolution codes", rows=s8, column_widths=[360,110,96,96,96],
             note="Counts are records or factors as specified. Multiple-layer factors are a subset of multiple-label factors. Human resolution-code counts are saved factor-level codes, not post-hoc large language model (LLM) judgements. Missing codes: 59/110 (53.6%); no resolution state was imputed. Stored codes do not establish independently verified complete evidentiary support."),
        dict(title="Table S9. Analysability agreement before and after public-information reassessment", rows=s9, column_widths=[120,130,130,189,189],
             note="Each pair assessed its own 20 records. Exact agreement requires identical three-state analysability ratings. Kappa uses linear weights for ordered responses. Pairwise intervals are saved 95% percentile record-cluster bootstrap intervals (3,000 resamples). All-pair exact agreement pools counts; no pooled weighted kappa is reported.",
             paragraphs=["Within-reviewer transitions (120 responses): 19 to a more analysable state, 7 to a less analysable state, and 94 unchanged. From not analysable: 39 remained not analysable, 2 became uncertain, 0 became clear. From uncertain: 1 became not analysable, 16 remained uncertain, 17 became clear. From clear: 2 became not analysable, 4 became uncertain, 39 remained clear."]),
        dict(title="Table S10. Inter-reviewer HFACS layer agreement on the same matched factors", rows=s10, column_widths=[78,95,180,180,100,125],
             note="The same 32 factor pairs had HFACS layer classifications from both reviewers at both stages. Exact agreement requires identical layer sets; shared-layer agreement requires at least one common layer. The singleton subset requires a single layer from both reviewers at both stages (26 factor pairs). The all-pair singleton kappa pools three different pair-specific samples; the six reviewers did not rate a common set of records. Nominal kappa uses no ordering of HFACS layers."),
        dict(title="Table S11. Exploratory AI classification of RSv2 consensus factors", rows=s11, column_widths=[340,100,150,168],
             note="The frozen RSv1 classification configuration received the 110 consensus factor texts and original three narrative fields. Five unclassified factors were not scored against a reference label. Candidate hits require one AI category to match any reference category; exact full-set agreement is not required. Kappa is restricted to 75 factors with one HFACS reference label. Predictions could include non-HFACS categories. Intervals are saved 95% percentile record-cluster bootstrap intervals (3,000 resamples)."),
    ]
    for t in tables:
        t.setdefault("paragraphs", [])
        assert sum(t["column_widths"]) == 758
    g = d["graph_exploratory"]["overall"]
    assert math.isclose(g["directed_micro_f1"], 2 * g["shared_directed"] / (g["left_edges"] + g["right_edges"]))
    group = d["actor_unclear_association_exploratory"]
    timing = d["factor_f1_time_spearman_exploratory"]
    evidence = d["evidence_traceability"]
    assert evidence["independent"]["factors"] == evidence["independent"]["all_quotes_traceable"] == 244
    assert evidence["consensus"]["factors"] == evidence["consensus"]["all_quotes_traceable"] == 110
    text_sections = [dict(title="Supplementary Results. Evidence, relations, difficulty and recorded time", paragraphs=[
        "All saved quotations were locatable in the supplied narratives for 244 independent and 110 consensus factors. Quotations came exclusively from improvement text for 70/244 independent factors (28.7%) and 35/110 consensus factors (31.8%). This check assessed quotation traceability.",
        f"Exploratory directed-relation micro-F1 was {num(g['directed_micro_f1'])}, with {g['shared_directed']} matched relations among {g['left_edges']} left-reviewer and {g['right_edges']} right-reviewer relations across 60 records. Pair-specific micro-F1 values were AB 0.133 (3 matches; 23/22 relations), CD 0.348 (12 matches; 37/32 relations), and EF 0.385 (10 matches; 22/30 relations). Relation correspondence used the AI-assisted factor matches.",
        f"For the main extraction rule, micro-F1 was {ci(group['True']['micro_f1'], group['True']['micro_f1_ci95'])} in {group['True']['cases']} records where either reviewer reported unclear actor, role or scope, and {ci(group['False']['micro_f1'], group['False']['micro_f1_ci95'])} in {group['False']['cases']} other records. Group factor counts (left/right) were 42/64 and 39/31, with 24 and 13 matched factors, respectively. These are descriptive subgroup estimates, not an adjusted comparison.",
        f"Across {timing['n']} records with defined factor F1 and recorded time, Spearman's rho between record-level factor F1 and mean reviewer evaluation time was {num(timing['rho'])} (p = {num(timing['p'])}). The 14 both-empty records had undefined F1 and were not included in this correlation. This analysis did not estimate the association between actor uncertainty and time directly.",
        "Median saved independent-evaluation time was 4.94 minutes (interquartile range [IQR], 2.24 to 11.80; 120 responses). Median reassessment activity time was 1.13 minutes (IQR, 0.46 to 2.97; 120 responses). Reassessment activity time excluded inactive intervals. The two timing measures describe different tasks and collection procedures.",
    ])]
    paths = [RUN / "analysis.json", RUN / "alignment_decisions.csv", RUN / "alignment_review.json", RUN / "canonical_independent.json", RUN / "canonical_consensus.json", RUN / "canonical_phase2.json", RUN / "code/110_analyze_rsv2_complete.py", ROOT / "analysis_npj/scripts/116_audit_consultation_data_results.py", Path(__file__)]
    payload = dict(tables=tables, text_sections=text_sections,
                   sources=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths if p.exists()],
                   scope="Results 3.3-3.5; preserved outputs, no AI calls or altered analysis conditions")
    (OUT / "tables.json").write_text(json.dumps(payload, indent=2) + "\n")
    lines = ["# RSv2 Supplementary Results (draft)", ""]
    for t in tables:
        lines += ["## " + t["title"], "", "| " + " | ".join(t["rows"][0]) + " |", "| " + " | ".join(["---"] * len(t["rows"][0])) + " |"]
        lines += ["| " + " | ".join(row) + " |" for row in t["rows"][1:]]
        lines += ["", t["note"], "", *t["paragraphs"], ""]
    for section in text_sections:
        lines += ["## " + section["title"], "", "\n\n".join(section["paragraphs"]), ""]
    (OUT / "rsv2_supplementary_results.md").write_text("\n".join(lines))
    verify_native(payload)
    print(json.dumps(dict(tables=len(tables), cells=sum(len(row) for t in tables for row in t["rows"]), sources=len(paths), output=str(OUT))))


if __name__ == "__main__":
    main()
