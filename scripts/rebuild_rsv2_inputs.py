"""Rebuild matching counts from redacted factors and saved decisions; no AI calls."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HFACS = set("UA_DE UA_SE UA_PE UA_RV UA_EV PC_AM PC_AP PC_PL PC_TE PC_PE PC_CC PC_PR SI_IS SI_IO SI_FK SI_SV OI_RM OI_OC OI_OP".split())
ALLOWED_CODES = HFACS | {"CoP", "OTHER", "INAPPROPRIATE", "INDETERMINATE"}
MODES = ("all", "hfacs_only", "hfacs_or_indeterminate")
MATCHING = ("strict", "same_proposition", "partial_sensitivity")
RELATIONS = {"same", "partial", "causal_related", "actor_diff"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def layers(codes):
    return sorted({{"UA": "L1", "PC": "L2", "SI": "L3", "OI": "L4"}[c.split("_")[0]]
                   for c in set(codes) & HFACS})


def eligible(factor, mode):
    return mode == "all" or bool(set(factor["classifications"]) & HFACS) or (
        mode == "hfacs_or_indeterminate" and "INDETERMINATE" in factor["classifications"])


def quote_keys(factor):
    return {(e["section"], e["normalized_quote_sha256"]) for e in factor.get("evidence", [])}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(annotations, decisions, mapping):
    require(annotations["schema_version"] == decisions["schema_version"] == mapping["schema_version"] == 1,
            "Unsupported schema")
    cases = {}
    original_ids = set()
    for c in mapping["cases"]:
        require(c["source_id"] not in cases, "Duplicate case pseudonym")
        require(c["jcqhc_case_id"] not in original_ids, "Duplicate original case ID")
        cases[c["source_id"]] = c
        original_ids.add(c["jcqhc_case_id"])
    responses, factors = {}, {}
    for r in annotations["responses"]:
        sid, reviewer, stage = r["source_id"], r["reviewer_code"], r["stage"]
        require(stage in ("before", "after"), "Invalid stage")
        require(r["pair_id"] in ("AB", "CD", "EF") and reviewer in r["pair_id"], "Reviewer/pair mismatch")
        require(sid in cases and sid.startswith("RS2_"), "Unknown RSv2 case")
        key = (sid, reviewer, stage)
        require(key not in responses, "Duplicate response")
        require(r["analyzability"] in ("clear", "uncertain", "not_analyzable"), "Invalid analysability")
        responses[key] = r
        for f in r["factors"]:
            fkey = (*key, f["factor_id"])
            require(fkey not in factors, "Duplicate factor ID within response")
            require(set(f["classifications"]) <= ALLOWED_CODES, "Unknown category")
            require(f["classifications"] == sorted(set(f["classifications"])), "Duplicate or unsorted categories")
            require(f["layers"] == layers(f["classifications"]), "Layer/category mismatch")
            for e in f.get("evidence", []):
                require(e["section"] in ("main", "background", "improvement"), "Invalid evidence section")
                require(len(e["normalized_quote_sha256"]) == 64, "Invalid quotation fingerprint")
                require(bool(e["spans"]), "Unlocated quotation")
                require(e["source_field_sha256"] == cases[sid]["narrative_sha256"][e["section"]],
                        "Evidence/source hash mismatch")
                for span in e["spans"]:
                    require(0 <= span["start"] < span["end"] <= cases[sid]["narrative_lengths"][e["section"]],
                            "Invalid evidence offset")
            factors[fkey] = f
    before = {key[:2]: r for key, r in responses.items() if key[2] == "before"}
    after = {key[:2]: r for key, r in responses.items() if key[2] == "after"}
    require(set(before) == set(after), "Missing before/after response")
    assignments = defaultdict(set)
    for key, r in before.items():
        a = after[key]
        require(r["pair_id"] == a["pair_id"], "Changed pair assignment")
        require({f["factor_id"] for f in r["factors"]} == {f["factor_id"] for f in a["factors"]},
                "Missing or extra factor after reassessment")
        assignments[r["source_id"]].add(r["reviewer_code"])
    for sid, reviewers in assignments.items():
        pair = next(r["pair_id"] for r in before.values() if r["source_id"] == sid)
        require(reviewers == set(pair), "Missing pair reviewer")
    require(set(assignments) == {sid for sid in cases if sid.startswith("RS2_")}, "Missing case response")
    seen, matched_left, matched_right = set(), set(), set()
    for d in decisions["decisions"]:
        sid, pair = d["source_id"], d["pair_id"]
        require(pair in ("AB", "CD", "EF") and d["relation"] in RELATIONS, "Invalid decision")
        left = factors.get((sid, pair[0], "before", d["left_id"]))
        right = factors.get((sid, pair[1], "before", d["right_id"]))
        require(left is not None and right is not None, "Decision references unknown factor")
        key = (sid, d["left_id"], d["right_id"])
        require(key not in seen, "Duplicate decision")
        seen.add(key)
        require(d["strict_quote_match"] == bool(quote_keys(left) & quote_keys(right)), "Strict quotation mismatch")
        require(d["human_confirmed"] is False, "Human verification status changed")
        if d["relation"] in ("same", "partial"):
            lk, rk = (sid, d["left_id"]), (sid, d["right_id"])
            require(lk not in matched_left and rk not in matched_right, "Non-one-to-one correspondence")
            matched_left.add(lk)
            matched_right.add(rk)
    require(len(cases) == 210 and len(before) == len(after) == 120, "Unexpected cohort/response count")
    require(sum(len(r["factors"]) for r in before.values()) == 244, "Unexpected baseline factor count")
    require(len(decisions["decisions"]) == 55, "Unexpected saved decision count")
    return responses, factors


def rebuild(annotations, decisions, mapping, preserved_rows):
    responses, factors = validate(annotations, decisions, mapping)
    context = {}
    for r in preserved_rows:
        sid = r["source_id"]
        values = {k: r[k] for k in ("pair_id", "actor_unclear_either", "time_mean_minutes")}
        require(sid not in context or context[sid] == values, "Inconsistent preserved case covariates")
        context[sid] = values
    require(set(context) == {sid for sid, _, stage in responses if stage == "before"}, "Missing case context")
    by_case = defaultdict(list)
    for d in decisions["decisions"]:
        by_case[d["source_id"]].append(d)
    rows, units = [], {"before": [], "after": []}
    for mode in MODES:
        for matching in MATCHING:
            for sid, covariates in context.items():
                pair = covariates["pair_id"]
                left, right = [{f["factor_id"]: f for f in responses[sid, reviewer, "before"]["factors"]
                                if eligible(f, mode)} for reviewer in pair]
                selected = [d for d in by_case[sid] if d["left_id"] in left and d["right_id"] in right
                            and (d["relation"] == "same" or (matching == "partial_sensitivity" and d["relation"] == "partial"))
                            and (matching != "strict" or d["strict_quote_match"])]
                n1, n2, count = len(left), len(right), len(selected)
                rows.append(dict(source_id=sid, **covariates, n_left=n1, n_right=n2, matches=count,
                                 f1=2 * count / (n1 + n2) if n1 + n2 else None,
                                 eligibility=mode, matching=matching))
                if (mode, matching) != ("hfacs_or_indeterminate", "same_proposition"):
                    continue
                for d in selected:
                    for stage in units:
                        x, y = [factors[sid, reviewer, stage, fid] for reviewer, fid
                                in zip(pair, (d["left_id"], d["right_id"]), strict=True)]
                        lx, ly = set(x["layers"]), set(y["layers"])
                        units[stage].append(dict(source_id=sid, pair_id=pair, left_id=d["left_id"], right_id=d["right_id"],
                            codes_left=x["classifications"], codes_right=y["classifications"],
                            layer_left=x["layers"], layer_right=y["layers"],
                            codes_equal=x["classifications"] == y["classifications"], layer_equal=lx == ly,
                            layer_jaccard=len(lx & ly) / len(lx | ly) if lx | ly else None))
    return rows, units


def assert_equivalent(actual, expected, key):
    require(len(actual) == len(expected), "Row count mismatch")
    a = {tuple(r[k] for k in key): r for r in actual}
    b = {tuple(r[k] for k in key): r for r in expected}
    require(len(a) == len(actual) and len(b) == len(expected), "Duplicate output key")
    require(a == b, "Rebuilt inputs differ from preserved snapshot")


def rebuild_from_directory(root=ROOT):
    data = root / "data"
    annotations = read(data / "rsv2_independent_annotations.json")
    decisions = read(data / "rsv2_alignment_decisions.json")
    mapping = read(data / "case_id_mapping.json")
    preserved = read(data / "rsv2_factor_case_metrics.json")
    rows, units = rebuild(annotations, decisions, mapping, preserved)
    assert_equivalent(rows, preserved, ("source_id", "eligibility", "matching"))
    expected = read(data / "rsv2_matched_classification_units.json")
    for stage in units:
        assert_equivalent(units[stage], expected[stage], ("source_id", "left_id", "right_id"))
    response_rows = read(data / "rsv2_analyzability_case_metrics.json")
    ratings = {(r["source_id"], r["reviewer_code"], r["stage"]): r["analyzability"] for r in annotations["responses"]}
    for r in response_rows:
        for stage in ("before", "after"):
            require([ratings[r["source_id"], reviewer, stage] for reviewer in r["pair_id"]] == r[stage],
                    "Analysability snapshot mismatch")
    report = dict(case_links=len(mapping["cases"]), baseline_responses=120, reassessment_responses=120,
                  baseline_factors=244, reassessment_factors=sum(len(r["factors"]) for r in annotations["responses"] if r["stage"] == "after"),
                  decisions=len(decisions["decisions"]), relations=dict(Counter(d["relation"] for d in decisions["decisions"])),
                  rebuilt_count_rows=len(rows), matched_pairs={stage: len(value) for stage, value in units.items()},
                  case_covariates="Actor-difficulty flags and mean times retained from preserved case summaries, not rederived",
                  new_model_calls=False, human_confirmation=False)
    return rows, units, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/rsv2_rebuilt")
    args = parser.parse_args()
    rows, units, report = rebuild_from_directory()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in (("factor_case_metrics.json", rows), ("matched_classification_units.json", units), ("verification.json", report)):
        (args.output_dir / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
