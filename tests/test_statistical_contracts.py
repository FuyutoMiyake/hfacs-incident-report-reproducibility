"""Focused tests for preserved metric and denominator conventions."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "analysis_npj/scripts" / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


rs = module("rs", "110_analyze_rsv2_complete.py")
final = module("final", "79_evaluate_frozen_final_50.py")


class StatisticalContracts(unittest.TestCase):
    def test_empty_factor_set_is_undefined(self):
        self.assertIsNone(rs.f1(0, 0, 0))

    def test_micro_f1_denominator(self):
        self.assertAlmostEqual(rs.f1(81, 95, 37), 74 / 176)

    def test_non_hfacs_categories_are_merged_only_in_transforms(self):
        self.assertEqual(final.detailed20("CoP"), "NON_HFACS")
        self.assertEqual(final.tier5("SI_IO"), "L3")
        self.assertEqual(final.binary("UA_DE"), "HFACS")

    def test_multilabel_layers_are_not_first_entry(self):
        self.assertEqual(rs.layers({"classifications": ["UA_DE", "SI_IO"]}), {"L1", "L3"})

    def test_linear_weights_distinguish_one_and_two_step_disagreement(self):
        values = ["not_analyzable", "uncertain", "clear"]
        self.assertNotEqual(rs.agree(values, ["uncertain", "clear", "clear"], values, True)["kappa"],
                            rs.agree(values, ["clear", "clear", "clear"], values, True)["kappa"])


if __name__ == "__main__":
    unittest.main()
