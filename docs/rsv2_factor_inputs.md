# RSv2 Factor-Level Reconstruction (Issue #1)

**Date:** 8 October 2026. **Access:** private author review, not public release.
RS = reference standard; HFACS = Human Factors Analysis and Classification System;
JCQHC = Japan Council for Quality Health Care; F1 = twice the matches divided by the
sum of the two factor counts, undefined when both counts are zero.

## Included Inputs

| File | Records | Fields and role |
| --- | --- | --- |
| `data/case_id_mapping.json` | 150 RSv1 + 60 RSv2 cases | Study pseudonym, official case ID, annual filename/file hash, narrative field hashes/lengths |
| `data/rsv2_independent_annotations.json` | 120 before + 120 after responses; 244 factors at each stage | Case, pair, reviewer A-F, stage, analysability, factor ID, all classification/layer codes; before confirmation and evidence positions; after review flag |
| `data/rsv2_alignment_decisions.json` | 55 saved decisions | Case/pair, left/right factor IDs, saved relation, strict-quotation flag and human-confirmed=false |
| `provenance/rsv2_input_extension_audit.json` | One export audit | Source hashes, verified counts, exclusions and reconstruction scope |

Factor identity is **case + reviewer + stage + factor ID**. IDs such as `f01` alone are
not globally unique. Classification sets retain every code, including non-HFACS and
indeterminate codes; no first-label reduction or missing-value imputation is performed.
After responses refer to the same fixed factor IDs. Exceptional factor-change notes
are not exported as new factors. Reviewer codes do not disclose names, but combined
case linkage and code patterns can increase identification risk; review is still required.
`confirmed` and `reviewed` retain the UI confirmation/review flags; they do not mean
that semantic matching was independently human-verified.

## Decision Semantics

The 55 relations are `same` (39), `partial` (9), `causal_related` (6), and `actor_diff` (1).
They are the saved decisions, not a complete cross-product of candidate pairs. An unlisted
pair is **not** an explicit negative judgement. `same` and `partial` relations satisfy
one-to-one constraints within each case.

- `same_proposition`: include eligible saved `same` decisions.
- `strict`: include eligible `same` decisions with a shared section and normalized-quotation fingerprint.
- `partial_sensitivity`: include eligible `same` or `partial` decisions.

`strict` is a matching condition, **not another mutually exclusive saved relation**.
Eligibility uses the baseline codes: all factors; HFACS-only; or HFACS/indeterminate.
HFACS eligibility means at least one HFACS category. No code equality is used to decide
semantic matching. This computational rule does not prove the original analyst was blind
to classifications or that the decisions are semantically correct.

## Quotation Coordinates

Only baseline quotation **positions**, section codes and fingerprints are distributed,
not the quotation strings. There are 246 saved evidence items for 244 baseline factors.
Positions refer to the exact decoded, stripped source field supplied to the reviewers:

- Sections: `main`, `background`, `improvement`.
- Unit: Python Unicode code points, zero-based `start`, exclusive `end`; not UTF-8 byte offsets or UTF-16 indexes.
- Source field: retrieve via official case linkage and check `source_field_sha256`.
- Normalize for matching: Unicode NFKC, then remove whitespace with Python `re.sub(r'\s+', '', text)`.
- `normalized_quote_sha256`: SHA-256 of the normalized quotation encoded as UTF-8.
- `spans`: all matching locations, including repeated occurrences; punctuation/spacing in
  the source span need not be byte-identical to the saved quote, but normalized hashes match.

The controlled export verified each evidence item's offsets against the original field.
Fingerprints reproduce the original strict comparison without redistributing quotes.
Hashes and offsets are traceability information, not an assertion of evidentiary support.
Once official prose is retrieved, offsets reveal the corresponding source passage; review
these linked disclosures before public release.

## Rebuild and Verify

```sh
.venv/bin/python scripts/rebuild_rsv2_inputs.py
.venv/bin/python scripts/reproduce.py --include-rsv1-human
.venv/bin/python -m unittest discover -s tests -v
```

The rebuilder validates duplicate/missing responses and factors, codes/layers, source hashes,
decision references, strict flags and one-to-one matching. It recalculates `n_left`, `n_right`,
`matches`, and `f1` for all **540 rows**, plus codes/layers for the **37 primary pairs** at
both time points, and compares full row content with immutable snapshots. Analysability
ratings also match the preserved before/after case table. Outputs go under `outputs/`;
existing snapshots are not overwritten. Actor-difficulty flags and mean time covariates
are reused from the existing case summaries, not newly computed from private logs.

| Eligibility | Left / right factors | Strict matches | Same-proposition matches | Including partial matches |
| --- | --- | --- | --- | --- |
| All | 87 / 157 | 13 | 39 | 48 |
| HFACS-only | 81 / 73 | 10 | 32 | 37 |
| HFACS or indeterminate | 81 / 95 | 13 | 37 | 45 |

No model calls or human verification are added by this extension. Recalculation validates
the arithmetic and stored classification inputs, not the semantic decisions. A new semantic
review under different criteria still requires factor prose in addition to the official source
and saved decisions; that prose is not in this package. Matching prompt/context gaps remain
in [limitations](limitations.md) and [matching provenance](semantic_matching_provenance.md).
