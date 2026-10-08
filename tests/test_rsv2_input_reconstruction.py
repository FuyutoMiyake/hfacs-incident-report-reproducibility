"""Factor-level reconstruction and failure checks, independent of model inference."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rebuild", ROOT / "scripts/rebuild_rsv2_inputs.py")
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


class InputReconstruction(unittest.TestCase):
    def setUp(self):
        self.annotations = R.read(ROOT / "data/rsv2_independent_annotations.json")
        self.decisions = R.read(ROOT / "data/rsv2_alignment_decisions.json")
        self.mapping = R.read(ROOT / "data/case_id_mapping.json")
        self.rows = R.read(ROOT / "data/rsv2_factor_case_metrics.json")

    def test_all_preserved_counts_and_units(self):
        rows, units, report = R.rebuild_from_directory(ROOT)
        self.assertEqual(len(rows), 540)
        self.assertEqual(len(units["before"]), 37)
        self.assertEqual(len(units["after"]), 37)
        self.assertEqual(report["baseline_factors"], 244)
        self.assertEqual(report["reassessment_factors"], 244)

    def test_nine_eligibility_matching_conditions(self):
        rows, _, _ = R.rebuild_from_directory(ROOT)
        expected = {"all": (87, 157, [13, 39, 48]), "hfacs_only": (81, 73, [10, 32, 37]),
                    "hfacs_or_indeterminate": (81, 95, [13, 37, 45])}
        for mode, (n1, n2, matches) in expected.items():
            for matching, count in zip(R.MATCHING, matches, strict=True):
                subset = [r for r in rows if (r["eligibility"], r["matching"]) == (mode, matching)]
                self.assertEqual(len(subset), 60)
                self.assertEqual(tuple(sum(r[k] for r in subset) for k in ("n_left", "n_right", "matches")),
                                 (n1, n2, count))
        self.assertTrue(any(r["f1"] is None and r["n_left"] == r["n_right"] == 0 for r in rows))

    def test_duplicate_factor_fails(self):
        response = next(r for r in self.annotations["responses"] if r["factors"])
        response["factors"].append(copy.deepcopy(response["factors"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate factor"):
            R.validate(self.annotations, self.decisions, self.mapping)

    def test_missing_after_factor_fails(self):
        response = next(r for r in self.annotations["responses"] if r["stage"] == "after" and r["factors"])
        response["factors"].pop()
        with self.assertRaisesRegex(ValueError, "Missing or extra factor"):
            R.validate(self.annotations, self.decisions, self.mapping)

    def test_dangling_decision_fails(self):
        self.decisions["decisions"][0]["left_id"] = "absent_factor"
        with self.assertRaisesRegex(ValueError, "unknown factor"):
            R.validate(self.annotations, self.decisions, self.mapping)

    def test_duplicate_decision_fails(self):
        self.decisions["decisions"].append(copy.deepcopy(self.decisions["decisions"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate decision"):
            R.validate(self.annotations, self.decisions, self.mapping)

    def test_strict_flag_is_verified_from_fingerprints(self):
        d = self.decisions["decisions"][0]
        d["strict_quote_match"] = not d["strict_quote_match"]
        with self.assertRaisesRegex(ValueError, "Strict quotation mismatch"):
            R.validate(self.annotations, self.decisions, self.mapping)

    def test_category_tampering_fails_snapshot_check(self):
        response = next(r for r in self.annotations["responses"] if r["stage"] == "before" and
                        any(f["classifications"] == ["CoP"] for f in r["factors"]))
        f = next(f for f in response["factors"] if f["classifications"] == ["CoP"])
        f.update(classifications=["UA_DE"], layers=["L1"])
        rows, _ = R.rebuild(self.annotations, self.decisions, self.mapping, self.rows)
        with self.assertRaisesRegex(ValueError, "differ from preserved"):
            R.assert_equivalent(rows, self.rows, ("source_id", "eligibility", "matching"))

    def test_multilabel_not_collapsed(self):
        _, units, _ = R.rebuild_from_directory(ROOT)
        self.assertTrue(any(len(r["codes_left"]) > 1 or len(r["codes_right"]) > 1 for r in units["after"]))
        unit = units["before"][0]
        response = next(r for r in self.annotations["responses"] if r["source_id"] == unit["source_id"]
                        and r["reviewer_code"] == unit["pair_id"][0] and r["stage"] == "before")
        factor = next(f for f in response["factors"] if f["factor_id"] == unit["left_id"])
        factor.update(classifications=["SI_IO", "UA_DE"], layers=["L1", "L3"])
        _, synthetic = R.rebuild(self.annotations, self.decisions, self.mapping, self.rows)
        changed = next(r for r in synthetic["before"] if (r["source_id"], r["left_id"], r["right_id"]) ==
                       (unit["source_id"], unit["left_id"], unit["right_id"]))
        self.assertEqual(changed["codes_left"], ["SI_IO", "UA_DE"])
        self.assertEqual(changed["layer_left"], ["L1", "L3"])

    def test_redacted_field_allowlists(self):
        for r in self.annotations["responses"]:
            self.assertEqual(set(r), {"source_id", "pair_id", "reviewer_code", "stage", "analyzability", "factors"})
            for f in r["factors"]:
                self.assertEqual(set(f), {"factor_id", "classifications", "layers", "confirmed", "evidence"}
                                 if r["stage"] == "before" else {"factor_id", "classifications", "layers", "reviewed"})
                for e in f.get("evidence", []):
                    self.assertEqual(set(e), {"section", "spans", "normalized_quote_sha256", "source_field_sha256"})
        for d in self.decisions["decisions"]:
            self.assertEqual(set(d), {"source_id", "pair_id", "left_id", "right_id", "relation", "strict_quote_match", "human_confirmed"})
        encoded = json.dumps([self.annotations, self.decisions])
        for excluded in ("annotator_name", "factor_text", "evidence_quote", "rationale", "submitted_at", "active_seconds", "notes"):
            self.assertNotIn('"' + excluded + '"', encoded)

    def test_source_link_duplicates_fail(self):
        self.mapping["cases"][1]["jcqhc_case_id"] = self.mapping["cases"][0]["jcqhc_case_id"]
        with self.assertRaisesRegex(ValueError, "Duplicate original"):
            R.validate(self.annotations, self.decisions, self.mapping)


if __name__ == "__main__":
    unittest.main()
