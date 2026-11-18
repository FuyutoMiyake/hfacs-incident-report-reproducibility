"""Check the scoped provenance recovery and public-source acquisition metadata."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProvenanceDocumentation(unittest.TestCase):
    def test_matching_recovery_is_scoped(self):
        data = json.loads((ROOT / "provenance/semantic_matching_audit.json").read_text())
        self.assertEqual(data["model_recorded_at_creation"], "gpt-6.1-sol")
        self.assertTrue(data["creation_patch_matches_current_csv"])
        self.assertEqual(sum(data["relations"].values()), data["decision_rows"])
        self.assertTrue(data["ab_cd_candidate_keys_equal_legacy"])
        self.assertFalse(data["standalone_frozen_matching_prompt_recovered"])
        self.assertFalse(data["full_conversation_exported"])
        self.assertFalse(data["human_independent_confirmation"])
        self.assertNotIn("transcript", data)

    def test_source_files_are_versioned_with_private_study_linkage(self):
        data = json.loads((ROOT / "provenance/jcqhc_source_files.json").read_text())
        self.assertEqual(data["n_files"], 15)
        self.assertEqual(sum(row["eligible_records"] for row in data["files"]), 61606)
        self.assertTrue(data["original_source_id_mapping_distributed"])
        self.assertFalse(data["general_public_release"])
        expected = {f"MedicalReportPubA_{year}.csv" for year in range(2010, 2025)}
        self.assertEqual({row["file"] for row in data["files"]}, expected)
        for row in data["files"]:
            self.assertRegex(row["sha256"], r"^[a-f0-9]{64}$")
            self.assertEqual(row["official_url"], "https://www.med-safe.jp/download/" + row["file"])

    def test_documentation_links_and_access_boundary(self):
        for name in ["semantic_matching_provenance.md", "data_availability.md"]:
            path = ROOT / "docs" / name
            text = path.read_text()
            for link in re.findall(r"\]\(([^)]+)\)", text):
                if link.startswith("https://"):
                    continue
                self.assertTrue((path.parent / link.split("#", 1)[0]).is_file(), link)
        text = (ROOT / "docs/data_availability.md").read_text()
        self.assertIn("not an unconditional promise", text)
        self.assertIn("does **not**, by itself, reconstruct", text)
        self.assertIn("Packaged files are public", text)
        self.assertIn("withheld material requires a separate access decision", text)


if __name__ == "__main__":
    unittest.main()
