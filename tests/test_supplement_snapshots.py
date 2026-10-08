"""Check readable supplements against preserved tables and snapshot hashes."""

import collections
import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tables(path):
    result, rows = [], []
    for line in path.read_text().splitlines() + [""]:
        if line.startswith("| "):
            cells = [cell.strip().replace("<br>", "\n").replace("\\|", "|")
                     .replace("\\\\", "\\") for cell in re.split(r"(?<!\\)\|", line)[1:-1]]
            if not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                rows.append(cells)
        elif rows:
            result.append(rows)
            rows = []
    return result


class SupplementSnapshots(unittest.TestCase):
    def test_all_results_table_cells(self):
        expected = []
        for filename in ("expected_tables_S1-S3.json", "expected_tables_S4-S6.json",
                         "expected_tables_S7-S11.json"):
            expected.extend(json.loads((ROOT / "data" / filename).read_text()))
        actual = tables(ROOT / "supplements/supplementary_results.md")
        self.assertEqual(len(actual), 11)
        self.assertEqual(actual, [table["rows"] for table in expected])

    def test_grras_complete_and_pending(self):
        checklist = tables(ROOT / "supplements/grras_checklist.md")
        self.assertEqual(len(checklist), 1)
        rows = checklist[0][1:]
        self.assertEqual([row[0] for row in rows], [str(i) for i in range(1, 16)])
        self.assertEqual(collections.Counter(row[3].split(".", 1)[0] for row in rows),
                         {"Reported": 5, "Partial": 7, "Pending": 3})

    def test_classification_definition_table(self):
        definitions = tables(ROOT / "supplements/supplementary_methods.md")
        self.assertEqual(len(definitions), 1)
        self.assertEqual(len(definitions[0]), 23)

    def test_source_snapshot_hashes(self):
        manifest = json.loads((ROOT / "provenance/supplement_manifest.json").read_text())
        for record in manifest["files"]:
            self.assertEqual(hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest(),
                             record["sha256"], record["path"])

    def test_no_private_document_links_or_export_controls(self):
        for path in (ROOT / "supplements").glob("*.md"):
            text = path.read_text()
            for forbidden in ("docs.google.com/", "drive.google.com/", "/Users/",
                              "Document ID:", "Revision ID:", "[P000", "⟦EMPTY PARAGRAPH⟧"):
                self.assertNotIn(forbidden, text, str(path))


if __name__ == "__main__":
    unittest.main()
