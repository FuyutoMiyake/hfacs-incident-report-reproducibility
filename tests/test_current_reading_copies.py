"""Verify the dated reading copies without changing calculation snapshots."""

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIES = ROOT / 'manuscript-supplements/20261118'


class CurrentReadingCopies(unittest.TestCase):
    def test_exports_match_manifest(self):
        manifest = json.loads((COPIES / 'manifest.json').read_text())
        self.assertEqual(manifest['export_date'], '2026-11-18')
        self.assertEqual(len(manifest['files']), 3)
        self.assertEqual([r['tables'] for r in manifest['files']], [2, 11, 1])
        for item in manifest['files']:
            data = (COPIES / item['export']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), item['export_sha256'])
            self.assertEqual(item['comments_and_revisions'], 0)
            self.assertNotIn('/Users/', data.decode())
            self.assertNotIn('docs.google.com', data.decode())

    def test_navigation_and_population_distinction(self):
        readme = (ROOT / 'README.md').read_text()
        self.assertIn('manuscript-supplements/20261118/README.md', readme)
        self.assertIn('248 factors', readme)
        self.assertIn('244-factor reassessment', readme)
        historical = (ROOT / 'docs/rsv2_factor_inputs.md').read_text()
        self.assertIn('scripts/reproduce.py --historical --include-rsv1-human', historical)


if __name__ == '__main__':
    unittest.main()
