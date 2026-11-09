# Recalculated Manuscript Version

Approved calculation date: 7 November 2026. Packaged for private coauthor review on
9 November 2026. The preceding fixed repository version was `14cbe429` (8 October).

## Contents

- `data/`: ordered pseudonymised input units, categorical factors and relations, 55 saved
  correspondence decisions, evidence fingerprints, saved elapsed times, code-only FTA
  trees and direct-classification factor sets. No clinical prose or reviewer identities.
- `code/`: the approved pooled statistic functions and FTA/RSv2 calculation functions;
  FTA input adapters read category-only inputs instead of original narrative responses.
- `expected/`: approved local recalculation outputs used only for comparison checks.
- `supplements/`: active text and tables from the approved 7 November supplementary Word
  files, without deleted text or comments. These are snapshots, not live Word files.
- `provenance.json`: source hashes and documented packaging transformations.
- `verification.json`: successful reproduction receipt generated after comparison.

## Distinguish the Two RSv2 Populations

`rsv2_independent_annotations.json` contains the selected pre-viewing independent
responses (248 factors) and the subsequent reassessment labels. Four CoP-only factors
were not part of the reassessment baseline and have no corresponding after-assessment.
The 37 primary matched pairs retain valid labels at both stages.

`rsv2_reassessment_annotations.json` retains the actual baseline shown during reassessment
(244 factors), and the 244 reassessed factors. Classification changes and analysability
transitions use this baseline, not a retrospective substitution.

## Changes From the October Package

| Item | Historical | Current |
| --- | --- | --- |
| All-factor extraction micro-F1 | 78/244 = 0.320 | 78/248 = 0.315 |
| Primary eligible-factor micro-F1 | 74/176 = 0.420 | 74/176 = 0.420 |
| Directed relation micro-F1 | 0.301 | 0.291 |
| Independent recorded-time median | Older saved response versions | 4.84 minutes |
| Pooled human detailed kappa | Same point estimate | 0.503 (0.456 to 0.548) |
| Selected AI detailed kappa | 0.427 (0.356 to 0.497) | 0.427 (0.359 to 0.493) |
| Secondary AI detailed kappa | 0.499 (0.443 to 0.550) | 0.499 (0.445 to 0.551) |
| FTA minus direct-classification micro-F1 | Same point estimate | 0.032 (-0.024 to 0.086) |

Primary point estimates and conclusions are unchanged. Confidence intervals use the
approved 10,000-resample procedures. Current FTA statistics are recomputed from saved
category-only trees/sets, including bootstrap and ranking, without new model calls.

The observed FTA-minus-frequency recall@5 difference is zero. The historical script's
bootstrap `estimate` field is the mean bootstrap difference (about -0.085), **not** that
observed difference. Keep these distinct when interpreting the retained CSV field names.

## Execute

From the repository root, with `requirements.txt` installed:

```sh
python scripts/reproduce.py --include-rsv1-human
```

See [the reproduction guide](../../docs/reproduction.md) for all seeds, verification
scope and limitations. A passing test is computational reproduction conditional on saved
annotations/matches, not independent validation of semantic matching or model generation.
