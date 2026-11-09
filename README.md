# HFACS incident-report analysis: computational companion

**Status:** private author-review repository; not a public data release. Updated 9 November 2026.

**Current manuscript calculations:** [7 November revision](revisions/20261107/README.md).
The default reproduction command now uses this revision. The October snapshots are retained
for provenance and are not the current manuscript results.

Companion to the draft manuscript *Toward systems-level analysis of medical incident reports:
An expert-annotated evaluation of large language models using HFACS* (provisional title).
HFACS = Human Factors Analysis and Classification System; FTA = fault tree analysis;
RS = reference standard. [Japanese overview](README_ja.md).

## Start Here

- [Current manuscript supplements](revisions/20261107/supplements/): 7 November Methods and Results snapshots.
- [Historical supplements and reporting checklist](supplements/README.md): dated October snapshots.
- [Reproduction guide](docs/reproduction.md): executable commands and the exact scope of each command.
- [Analysis map](docs/analysis_map.md): manuscript results, inputs and scripts.
- [Data availability and schemas](docs/data_availability.md): included numeric units and withheld source material.
- [Current RSv2 inputs](revisions/20261107/README.md): 248 factors for independent extraction, a separate 244-factor reassessment baseline, and 55 saved decisions; [offset/link schema](docs/rsv2_factor_inputs.md).
- [Recovered matching provenance](docs/semantic_matching_provenance.md): recorded SOL session model, decision-file checksum and remaining prompt/context gaps.
- [Publication scope](docs/publication_scope.md): proposed public package, excluded material and release approval.
- [Prompt development](docs/prompt_development.md) and [original v6b templates](docs/original_v6b_prompts.md).
- [Limitations and unresolved provenance](docs/limitations.md).
- [Source hashes](provenance/source_manifest.json): original versus companion files and transformations.
- [Repository design references](docs/repository_examples.md).

## Recompute Saved Results

Python 3.12 or later; Python 3.14 is used for the author verification.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/reproduce.py --include-rsv1-human
```

This performs no API calls. It rebuilds RSv2 extraction counts and relation counts from
redacted individual factors, relations and saved correspondence decisions. It recomputes
RSv1 human and AI agreement, RSv2 extraction, reassessment, conditional AI classification,
the additional confidence intervals, and FTA ranking/direct-classification comparisons.
Current bootstrap calculations use 10,000 replicates. Outputs and numerical checks are
written to `outputs/current/recomputation.json`.

FTA statistics are now recomputed from code-only saved trees, factor category sets and
target categories, not copied from aggregate tables. No trees, annotations or model
predictions are regenerated. Grounding/traceability flags and semantic correspondences
are preserved inputs, not independently verified truth. Current supplement text snapshots
are included, but their Word layout is not regenerated. See the [reproduction guide](docs/reproduction.md).

## Repository Layout

```text
analysis_npj/scripts/       Original statistical/table code, with documented packaging changes
analysis_npj/derived/       Pseudonymised category-only RSv1 inputs
analysis_npj/results/       Preserved aggregate outputs
data/                      Pseudonymised numeric units and expected table cells
revisions/20261107/         Current inputs, calculation adapters, expected results and supplements
docs/                      Human-readable Markdown documentation
prompts/                   Prompt templates and frozen classification settings
provenance/                File hashes and transformation records
scripts/                   Offline reproduction and integrity checks
supplements/               Readable manuscript supplements and draft GRRAS checklist
```

Original paths are retained where needed by the historical scripts. Do not run every historical
script indiscriminately: some require restricted source files not included here.

## Access, Citation and Licensing

The repository is **private** for coauthor review; a write-access invitation has been sent
to the collaborating reviewer. This is not a public release.

| Destination | Material |
| --- | --- |
| Proposed public repository, after team and disclosure review | Manuscript supplement snapshots and GRRAS checklist, analysis/figure code, environment and tests, Markdown reproduction instructions, prompt templates/settings, pseudonymised numeric/category inputs, redacted RSv2 annotations and alignment decisions, quotation offsets/fingerprints, study-to-JCQHC case links, aggregate results and hashes |
| Journal submission | Final reviewed supplements in the required submission format: essential methods, classification definitions, sensitivity analyses, results tables S1-S11 and reporting checklist |
| Not in the proposed public package | Clinical narratives/metadata exports, factor texts/quotations, complete individual annotation exports, original model responses and clinical few-shot examples, reviewer identities/contacts and reviewer-identity mappings, internal comments/logs, credentials and original working-repository history |

Public access, dataset redistribution, code licence, complete author list and an archival DOI
require the research team's approval. No open-source licence has been assigned in this draft.
Use the repository URL and an exact Git commit when citing this computational version;
do not describe the current URL as publicly accessible or as a DOI.
Clinical narratives, quotations, factor texts, identifying reviewer information, internal
comments, credentials and working-repository Git history are excluded. Original clinical
few-shot messages are withheld; the r03 template file is not the complete frozen prompt bundle.

Current supplements are included in [the revision folder](revisions/20261107/supplements/),
alongside executable code and computational documentation. The numeric/category inputs
are intended public-release candidates, accepted for author review. The collaborative
documents remain the working sources; these Markdown copies are dated snapshots, not
automatically synchronised edits. Final journal supplements and a public release remain
subject to review and approval.

Historical Issue #1 extension (8 October): 150 RSv1 and 60 RSv2 case links were checked against the 15 frozen
annual CSVs; all three supplied fields matched for all 210 records. The private package
now includes 120 baseline and 120 reassessment responses, with all 244 factor IDs at each
stage and all 55 saved decisions. Unlisted candidate pairs are not fabricated negative
judgements. This improves input-level recomputation, not independent semantic validation
or human confirmation. Case linkage may increase re-identification risk; coauthor and
disclosure approval is still needed before any public release.
