# Reproduction Guide

## Current Manuscript Revision

The default runner uses `revisions/20261107/`, not the historical October aggregates.
Use Python 3.14 with `requirements.txt` (author verification: Python 3.14.6, NumPy 2.4.4,
pandas 3.0.1, SciPy 1.17.1).

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/verify_integrity.py
.venv/bin/python scripts/reproduce.py --include-rsv1-human
```

No API calls or model inference are performed. Calculations compare against frozen expected
values at absolute/relative tolerance 1e-12. Default outputs go to `outputs/current/`.
Without `--include-rsv1-human`, the full initial pair-specific RSv1 reliability CSV is
skipped; pooled RSv1 human agreement and all other current analyses still run.
`--skip-fta` is a debugging option and is not a complete reproduction run.

## Calculation Scope

- RSv1 pooled human agreement: 81 records/731 leaves; pair-stratified record bootstrap,
  10,000 draws, seeds 20261014-20261016 for detailed/layer/binary categories.
- RSv1 pair-specific human estimates: original record-cluster procedures, 10,000 draws,
  condition-specific seeds derived from 1500714; optional slower full CSV verification.
- RSv1 final AI classification: 37 records/306 leaves per model; pair-stratified record
  bootstrap, 10,000 draws, seed 20260722. Ordered pseudonyms preserve cluster order.
- FTA ranking and direct classification: original statistical procedures with pair-stratified
  record bootstrap, 10,000 draws; ranking seed 1500716 and original comparison-specific
  seeds derived from 1500718. Code-only trees and category sets are included.
- RSv2 independent extraction: 120 pre-consensus-viewing responses/248 factors; 55 saved
  correspondence decisions reconstruct 540 count rows and 37 matched classification pairs.
  Extraction/AI/reassessment pair-specific CIs use 10,000 draws and seed 20261001.
- Reassessment: the actually presented 244-factor baseline remains separate. Pooled linear
  weighted kappa uses pair-stratified record bootstrap with seeds 20261024/20261025.
  Within-reviewer classification changes use these same 244 existing factors.
- Additional matched-factor and fixed-26 layer kappa intervals and relation F1 interval:
  10,000 draws, seed 20261107, retaining all 60 record clusters, including empty clusters.

The independent-version selection restores four CoP-only factors excluded from primary
extraction. Primary micro-F1 is unchanged, but the all-factor denominator changes from 244
to 248 (0.320 to 0.315). Relation counts and elapsed-time summaries also use the pre-viewing
independent responses.

The latest packaged manuscript reading copies are listed in the
[18 November supplement index](../manuscript-supplements/20261118/README.md).
`revisions/20261107/supplements/` retains the calculation-era snapshots.
The runner verifies statistical outputs, not Word formatting or later editorial changes.
Expected files are comparison targets, never substitutes for calculation.

## Interpretation and Access Limits

Passing checks establish numerical reproduction conditional on saved human decisions,
model category predictions and correspondence decisions. They do not independently
validate those decisions or reproduce human annotation/model generation. Quotation
fingerprints and grounding flags are preserved checks: without obtaining the original
sources, a reader cannot independently verify narrative evidence. Clinical narrative,
factor prose, quotations, reviewer identities and internal review logs are not distributed.

The packaged files are public as of 18 November 2026. Withheld source material is not
automatically available on request. No open-source/data licence has been assigned;
any additional redistribution remains a separate decision.

## Historical October Version

`data/`, `analysis_npj/` and `supplements/` retain historical snapshots. To reproduce
the earlier computational version explicitly:

```sh
.venv/bin/python scripts/reproduce.py --historical --include-rsv1-human
```

That historical command uses the old 244-factor independent dataset and old bootstrap
counts (2,000/5,000/3,000); it must not be reported as reproduction of the current manuscript.
The old `--historical --figures` option similarly renders historical figures, not current ones.
Do not execute historical main routines indiscriminately: some require restricted inputs.

## Integrity and Provenance

`provenance/file_manifest.json` covers the packaged files. The revision's `provenance.json`
records hashes of approved local sources and the allowlisted transformations.
Original study files are not overwritten. Generated outputs are ignored by Git.
Frozen comparison values and the verification receipt identify the current computations.
