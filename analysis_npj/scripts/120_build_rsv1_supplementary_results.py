"""Build RSv1 supplementary tables from preserved analysis outputs, without rerunning AI."""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis_npj/manuscript/supplementary_results_20261005"
SOURCE_CSV = ROOT / "analysis_npj/results/reliability/reliability_metrics.csv"
SOURCE_AI = [
    ROOT / "analysis_npj/prompt_adaptation/split50x3_20260722/final_results/final_results.json",
    ROOT / "analysis_npj/prompt_adaptation/split50x3_20260722/final_results_kimi_k26/kimi_k26_final_results.json",
]


def ci(value, low, high):
    return f"{float(value):.3f} ({float(low):.3f} to {float(high):.3f})"


def verify_native(payload):
    path = OUT / "verified_native_readback/document-result.json"
    if not path.exists():
        return
    result = json.loads(path.read_text())
    doc = result["structuredContent"]
    tab = doc["tabs"][0]
    tables = [block["table"] for block in tab["body"]["content"] if "table" in block]
    assert len(tables) == len(payload["tables"])
    checked = 0
    for actual, expected in zip(tables, payload["tables"], strict=True):
        rows = actual["tableRows"]
        assert len(rows) == len(expected["rows"])
        for ri, (row, values) in enumerate(zip(rows, expected["rows"], strict=True)):
            assert len(row["tableCells"]) == len(values)
            for cell, value in zip(row["tableCells"], values, strict=True):
                runs = [element["textRun"] for block in cell["content"]
                        for element in block.get("paragraph", {}).get("elements", [])
                        if "textRun" in element]
                assert "".join(run["content"] for run in runs).strip() == value
                for run in runs:
                    style = run.get("textStyle", {})
                    assert style["fontSize"]["magnitude"] == 10
                    if run["content"].strip():
                        assert style.get("bold", False) == (ri == 0)
                checked += 1
    verification = dict(document_id=doc["documentId"], revision=doc["revisionId"],
                        tables=len(tables), cells_checked=checked,
                        cell_text_exact=True, table_text_size_pt=10,
                        header_bold=True, source_hashes=payload["sources"],
                        scope="Existing-output table assembly and native readback, not independent statistical replication")
    (OUT / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with SOURCE_CSV.open(encoding="utf-8-sig", newline="") as stream:
        source_rows = list(csv.DictReader(stream))
    selected_rows = []

    def find(pair, granularity, metric="cohens_kappa", analysis_set="primary_main11_50",
             label_version="post_l1", node_scope="leaf"):
        key = dict(pair=pair, granularity=granularity, metric=metric,
                   analysis_set=analysis_set, label_version=label_version,
                   node_scope=node_scope, domain="hfacs_classification")
        found = [r for r in source_rows if all(r[k] == v for k, v in key.items())]
        assert len(found) == 1, (key, len(found))
        selected_rows.append(found[0])
        return found[0]

    def formatted(row):
        return ci(row["estimate"], row["ci_low"], row["ci_high"])

    s1 = [["Pair", "Classification", "Records / nodes", "Observed agreement (95% CI)",
           "Cohen's kappa (95% CI)", "Gwet's AC1 (95% CI)"]]
    for pair in ["AB", "CD", "EF"]:
        for code, name in [("detailed_22", "Detailed: 22 categories"),
                           ("tier_plus_non_5", "Layers: L1-L4 + non-HFACS"),
                           ("binary_hfacs", "Binary: HFACS / non-HFACS")]:
            rows = [find(pair, code, metric) for metric in ["agreement", "cohens_kappa", "gwet_ac1"]]
            assert len({(r["n_cases"], r["n_units"]) for r in rows}) == 1
            s1.append([pair, name, f"{rows[0]['n_cases']} / {rows[0]['n_units']}",
                       *[formatted(r) for r in rows]])

    s2 = [["Model / role", "Classification", "Records / nodes", "Observed agreement (95% CI)",
           "Cohen's kappa (95% CI)", "Gwet's AC1 (95% CI)"]]
    for source, model in zip(SOURCE_AI, ["GPT-5.6 Sol / primary", "Kimi K2.6 / secondary"], strict=True):
        data = json.loads(source.read_text())
        assert data["population"]["all_cases"] == 50
        assert data["population"]["analyzable_cases"] == 37
        assert data["population"]["hfacs_leaves"] == 306
        assert data["bootstrap_repetitions"] == 5000
        for code, name in [("detailed20", "Detailed: 20 categories"),
                           ("tier5", "Layers: L1-L4 + non-HFACS"),
                           ("binary", "Binary: HFACS / non-HFACS")]:
            metric = data[code]
            assert metric["n"] == 306
            values = [ci(metric[k], *metric[f"{k}_ci95"])
                      for k in ["accuracy", "cohens_kappa", "gwets_ac1"]]
            s2.append([model, name, "37 / 306", *values])

    s3 = [["Analysis condition", "AB: records / nodes; kappa (95% CI)",
           "CD: records / nodes; kappa (95% CI)", "EF: records / nodes; kappa (95% CI)"]]
    for aset, sample in [("primary_main11_50", "Main 11-50"), ("sensitivity_main1_50", "Main 1-50")]:
        for version, label in [("post_l1", "after L1 reassessment"), ("first_round", "before L1 reassessment")]:
            for scope, nodes in [("leaf", "leaf nodes"), ("all_non_top", "all non-top nodes")]:
                condition = f"{sample}; {nodes}; {label}; 22 categories"
                values = []
                for pair in ["AB", "CD", "EF"]:
                    r = find(pair, "detailed_22", analysis_set=aset, label_version=version, node_scope=scope)
                    values.append(f"{r['n_cases']} / {r['n_units']}; {formatted(r)}")
                s3.append([condition, *values])
    for code, condition in [
        ("detailed_20_non_merged", "Main 11-50; leaf nodes; after L1 reassessment; 20 categories (non-HFACS merged)"),
        ("tier_plus_non_7", "Main 11-50; leaf nodes; after L1 reassessment; 7 categories (L1-L4 + three non-HFACS categories)"),
    ]:
        values = []
        for pair in ["AB", "CD", "EF"]:
            r = find(pair, code)
            values.append(f"{r['n_cases']} / {r['n_units']}; {formatted(r)}")
        s3.append([condition, *values])

    notes = [
        "Primary human analysis: Main 11-50 for each pair, records rated analysable by both reviewers, jointly retained leaf nodes, and post-L1-reassessment labels. Detailed classification comprises 19 HFACS categories plus patient condition (CoP), OTHER, and INAPPROPRIATE. The five-category layer and binary analyses combine the three non-HFACS categories. Counts are the observations entering each classification analysis. Observed agreement is a proportion, not a percentage. Confidence intervals use 2,000 record-cluster bootstrap replicates.",
        "The final evaluation set contained 50 records; 37 were analysable under the adjudicated RSv1 reference and contributed 306 leaf nodes. AI labels were compared with the adjudicated reference. Detailed classification comprises 19 HFACS categories and one combined non-HFACS category (20 categories in total), unlike the 22-category human analysis in Table S1. The selected GPT configuration was primary; Kimi received the unchanged prompt as a secondary evaluation. Confidence intervals use 5,000 record-cluster bootstrap replicates. Pair-stratified resampling was not used in this final RSv1 analysis.",
        "All rows use records rated analysable by both reviewers and jointly retained nodes. The first row repeats the primary 22-category analysis as the comparison anchor. Main 1-50 adds the earlier records; non-top nodes include intermediate nodes as well as leaves. Before/after L1 reassessment refers to saved reviewer coding versions, not different patients. The eight 22-category rows enumerate all available combinations of record range, node scope, and coding version. The last two rows show alternative grouping of non-HFACS categories; five-category layer and binary results are in Table S1. Blank classification labels were excluded from classification estimates and preserved in the source dataset. Counts and intervals are taken from the existing analysis, with 2,000 record-cluster bootstrap replicates. These are sensitivity analyses, not additional independent validation cohorts.",
    ]
    payload = dict(title="Supplementary Results (Draft)", prepared_date="2026-10-05",
                   manuscript="Toward systems-level analysis of medical incident reports: An expert-annotated evaluation of large language models using HFACS (provisional title)",
                   abbreviations="AI, artificial intelligence; CI, confidence interval; FTA, fault tree analysis; HFACS, Human Factors Analysis and Classification System; L1-L4, HFACS layers; RS, reference standard; AC1, Gwet's agreement coefficient; CoP, patient condition.",
                   tables=[dict(title="Table S1. Inter-reviewer classification agreement in RSv1", rows=s1, note=notes[0]),
                           dict(title="Table S2. AI classification agreement with adjudicated RSv1", rows=s2, note=notes[1]),
                           dict(title="Table S3. Sensitivity analyses of RSv1 inter-reviewer classification agreement", rows=s3, note=notes[2])])
    payload["sources"] = [dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                          for p in [SOURCE_CSV, *SOURCE_AI]]
    (OUT / "tables.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    unique_rows = {json.dumps(r, sort_keys=True): r for r in selected_rows}
    with (OUT / "selected_reliability_rows.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=source_rows[0].keys())
        writer.writeheader()
        writer.writerows(unique_rows.values())
    text = [f"# {payload['title']}", f"Prepared: {payload['prepared_date']}", payload["abbreviations"], payload["manuscript"]]
    for table in payload["tables"]:
        text.extend(["", f"## {table['title']}", "", "| " + " | ".join(table["rows"][0]) + " |",
                     "| " + " | ".join(["---"] * len(table["rows"][0])) + " |"])
        text.extend("| " + " | ".join(row) + " |" for row in table["rows"][1:])
        text.extend(["", table["note"]])
    text.extend(["", "## Internal source provenance (not for submission)",
                 "Table-building script: analysis_npj/scripts/120_build_rsv1_supplementary_results.py"])
    text.extend(f"- `{s['path']}`; SHA-256: `{s['sha256']}`" for s in payload["sources"])
    (OUT / "supplementary_results.md").write_text("\n\n".join(text) + "\n")
    verify_native(payload)
    print(json.dumps(dict(output=str(OUT), rows=[len(t["rows"])-1 for t in payload["tables"]],
                          selected_csv_rows=len(unique_rows), sources=payload["sources"]), ensure_ascii=False))


if __name__ == "__main__":
    main()
