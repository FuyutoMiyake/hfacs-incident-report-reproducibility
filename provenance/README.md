# Computational Snapshot Verification

Prepared 8 October 2026 in a fresh Python 3.14.6 virtual environment.

- RSv1 human reliability: 510 aggregate metric rows checked, including sensitivity conditions.
- RSv1 final model evaluations and RSv2 supported unit-level analyses: deterministic
  point estimates and confidence intervals compared with saved values.
- Total numerical comparisons: 3,925, tolerance 1e-12.
- Supplementary Results: all titles and cell text in S1-S11 identical to saved tables.
- Figures: four generated; 11 population, margin, input-integrity and PDF/font checks passed.
- Focused metric/denominator tests: five passed; Python compilation passed.
- No AI calls, new annotations, clinical-source redistribution or changes in statistical definitions.

The full calculation check record is `recomputation.json`. These are computational
checks conditional on the saved inputs, not independent adjudication of matching,
traceability or causal validity. `source_manifest.json` records original input/code
hashes and packaging transformations; `file_manifest.json` checks the curated checkout.

The first full execution reached the FTA table assembly but failed because its provenance
list required withheld files. The table builders' provenance enumeration was restricted
to available companion files; no statistic or table cell was changed. The full execution
then passed. Code licensing, public release and complete citation metadata remain pending.
