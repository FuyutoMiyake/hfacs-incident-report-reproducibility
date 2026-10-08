# Data Availability and Schemas

## Included

Only enumerated categorical/numeric fields are exported. Original case identifiers are
replaced by ordered pseudonyms (`RS1_001`, `RS2_001`, ...); no mapping is distributed.
AB/CD/EF identify pair assignments, not publicly disclosed names. These derived units
remain subject to a disclosure review before any public release; pseudonymisation is
not a claim that re-identification is impossible.

| Input | Unit and content | Purpose |
| --- | --- | --- |
| `analysis_npj/derived/*.csv` | RSv1 case/pair codes, reviewer codes, node IDs, keep/delete decisions, HFACS labels, topology flags | Human reliability and sensitivity |
| `data/rsv1_final_*_units.json` | 306 leaves/model; case pseudonym, node ID, reference/predicted category | Frozen final classification agreement |
| `data/rsv2_factor_case_metrics.json` | 540 rows: 60 cases x 3 eligibility x 3 matching rules; counts, F1, difficulty flag, mean time | Conditional matching sensitivity |
| `data/rsv2_analyzability_case_metrics.json` | 60 cases; before/after ratings for both reviewers | Transitions and weighted kappa |
| `data/rsv2_matched_classification_units.json` | Saved factor IDs and label/layer sets before/after | Matched-unit layer agreement |
| `data/rsv2_consensus_codes.json` | 60 cases/110 factors; classifications and stored resolution codes | Consensus counts and missingness |
| `data/rsv2_ai_classification_units.json` | 110 factor IDs, human/AI labels, candidate-hit flags and saved resolution strata | Conditional AI agreement |
| `data/rsv2_graph_case_metrics.json` | Per-case edge counts and saved match counts | Exploratory relation F1 |
| `data/rsv2_evidence_traceability.json` | Section/traceability flags, no quotations | Counts conditional on saved flags |
| `data/rsv2_recorded_times.json` | Before elapsed minutes / after activity minutes | Recorded-time summaries |
| `analysis_npj/results/` and saved `analysis.json` | Aggregate statistics | Table and figure regeneration |

Factor correspondence is one-to-one and based on a saved central-proposition judgement,
not HFACS agreement. Strict sensitivity additionally requires a shared quotation;
partial sensitivity admits saved partial-overlap matches. Both-empty cases retain
undefined F1. Missing classification/resolution codes are not filled in.

## Withheld

JCQHC narrative text and metadata exports; factor prose and quotations; full individual
annotation exports; names/contact details; internal coauthor comments; session/activity
logs; full model responses; clinical few-shot examples; authentication/configuration
secrets; third-party paper PDFs; original research-repository history.

The historical hashes identify controlled source versions but do not grant redistribution
permission. External data acquisition and public sharing require the applicable JCQHC
terms and team approval to be reviewed. This private package does not assert that all
inputs to the original study are already open.
