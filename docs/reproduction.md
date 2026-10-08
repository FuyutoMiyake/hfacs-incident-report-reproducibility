# Reproduction Guide

## Offline Statistics

Create a fresh environment and install `requirements.txt`, then run:

```sh
.venv/bin/python scripts/reproduce.py --include-rsv1-human
```

Without `--include-rsv1-human`, the slower initial RSv1 human reliability analyses are
skipped; all other implemented unit-level statistics and table checks still run.
The runner imports the original statistical functions rather than introducing a new
kappa or bootstrap implementation. It compares numerical outputs at absolute/relative
tolerance 1e-12 with preserved outputs. All table cell text must match exactly.

- RSv1 initial reliability: 2,000 record-cluster bootstrap replicates; original script's
  deterministic condition-specific seeds, derived from seed 1500714.
- RSv1 final classification: 5,000 replicates, seed 20260722. Original source-ID ordering
  is preserved by ranked pseudonyms so cluster draws remain comparable.
- RSv2: 3,000 record-cluster bootstrap replicates, seed 20261001, stratified by pair.
  Empty case clusters are retained for conditional AI confidence intervals.

Outputs: `outputs/recomputation.json` and regenerated tables under
`analysis_npj/manuscript/supplementary_results_20261005/`. Inputs are not overwritten,
except the historical human reliability script regenerates the aggregate output CSV;
its values are checked against the separate immutable expected CSV in `data/`.

## Figures

Install `requirements-figures.txt` and Poppler (`pdftoppm` must be on PATH), then run:

```sh
.venv/bin/python scripts/reproduce.py --figures
```

Four SVG/PDF/PNG figures and a combined PDF are generated. Fonts use macOS Arial when
available, with a bundled ReportLab Vera fallback elsewhere. This is a rendering fallback,
not a change in statistical definitions. Figure manifests check populations, 120 responses,
transition margins, input integrity, PDF pages and font embedding.

## What a Passing Check Does Not Establish

This checks computation **conditional on saved ratings, matching decisions, classifications
and traceability flags**. It does not regenerate human annotations, establish the correctness
of semantic matching or assess full evidentiary support. No model is invoked.

Full FTA added-value recalculation, prompt selection and model inference need additional
controlled inputs. Historical scripts `06`, `09`, `79`, `83` and `110` are preserved for
inspection, but their standalone main routines may require source files not distributed
here. The supported entrypoint is `scripts/reproduce.py`. Future model reruns may differ
from preserved predictions and must not replace this computational snapshot silently.

## Integrity

```sh
.venv/bin/python scripts/verify_integrity.py
```

`provenance/source_manifest.json` documents the original source hashes and all package
transformations. `provenance/file_manifest.json` records the packaged snapshot. Rerunning
historical scripts may change output formatting or headers; run integrity checking on a
fresh checkout before regeneration. Generated output folders are ignored by Git.
