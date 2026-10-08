# Data Availability and Schemas

**Current access:** private coauthor review. The included derived inputs are candidates
for a future public release, accepted for author review, not publicly accessible data at present. See the
[publication-scope plan](publication_scope.md) for the approval boundary and exclusions.

## Included

Only allowlisted IDs, categorical/numeric fields, quotation offsets and hashes are exported.
Analysis identifiers remain ordered pseudonyms (`RS1_001`, `RS2_001`, ...). The private
package now includes the linkage to official JCQHC case IDs for 150 RSv1 and 60 RSv2 records.
AB/CD/EF identify pair assignments, not publicly disclosed names. These derived units
remain subject to a disclosure review before any public release; pseudonymisation is
not a claim that re-identification is impossible.

| Input | Unit and content | Purpose |
| --- | --- | --- |
| `data/case_id_mapping.json` | 210 pseudonym-to-JCQHC case links, annual filenames/file hashes, three-field hashes and lengths | Obtain and verify exact study sources without redistributing prose |
| `data/rsv2_independent_annotations.json` | 120 responses at each of two stages; all 244 factor IDs/classifications/layers at each stage; baseline evidence offsets/fingerprints, confirmation/review flags | Rebuild factor denominators and matched classification units |
| `data/rsv2_alignment_decisions.json` | All 55 saved candidate-pair decisions; relation and separate strict-quotation flag; human-confirmed=false | Rebuild match numerators without inventing unexamined negative pairs |
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

Factor correspondence uses saved one-to-one central-proposition judgements rather than
HFACS label equality as the computational matching condition. This does not establish
that the analyst was blinded to HFACS labels. Strict sensitivity additionally requires a shared quotation;
partial sensitivity admits saved partial-overlap matches. Both-empty cases retain
undefined F1. Missing classification/resolution codes are not filled in.
The decision-file creation model and remaining prompt-provenance gaps are described in
[semantic matching provenance](semantic_matching_provenance.md).
The [factor-level schema](rsv2_factor_inputs.md) explains composite factor IDs, offset
coordinates and the distinction between semantic decisions and strict-quotation matching.
`scripts/rebuild_rsv2_inputs.py` verifies all 540 count rows and both sets of 37 matched
classification pairs. Difficulty/time covariates are retained from existing case summaries.

## Withheld

The following are excluded from this companion and its proposed first public release;
they remain in the controlled research workspace. This is a scoped sharing decision,
not a claim that JCQHC public source material is categorically prohibited from reuse.

JCQHC narrative text and metadata exports; factor prose and quotations; full individual
annotation exports; names/contact details; internal coauthor comments; session/activity
logs; full model responses; clinical few-shot examples; authentication/configuration
secrets; third-party paper PDFs; original research-repository history.

The historical hashes identify controlled source versions but do not grant redistribution
permission. External data acquisition and public sharing require the applicable JCQHC
terms and team approval to be reviewed. This private package does not assert that all
inputs to the original study are already open.

## Obtaining the Original Public Sources

The original third-party sources can be obtained from JCQHC's
[annual case-download page](https://www.med-safe.jp/contents/report/report.html).
Use the **medical accident** CSV files `MedicalReportPubA_2010.csv` through
`MedicalReportPubA_2024.csv`, not the `MedicalReportPubH` near-miss series. These are
15 source files; the historical loader retained 61,606 unique records with non-empty
case IDs and event descriptions, read as `cp932` with `errors=ignore`, stripped field
values, and rejected duplicate case IDs.

The frozen file hashes and eligible-record counts are in
[`provenance/jcqhc_source_files.json`](../provenance/jcqhc_source_files.json).
The source-manifest creation date is not an original download date; the latter was not
recovered. A new download should be compared with these hashes. If a hash differs,
record the difference and do not silently replace the historical computational inputs.

Public download access is not permission for unrestricted redistribution. On 8 October
2026, the download and search pages linked to JCQHC's
[site terms](https://jcqhc.or.jp/terms_and_conditions), which reserve rights and require
prior permission for uses beyond applicable legal allowances. This package neither
asserts a blanket prohibition on research reuse nor assigns an open licence to JCQHC
text. No separate permission to redistribute the original CSVs is recorded in this
package; any proposed redistribution needs a specific rights review.

Use `data/case_id_mapping.json` to select each original `事例ID` from its specified annual
CSV. Decode and strip as above, take the last `事例の内容` column when the CSV has duplicate
headers (the historical `csv.DictReader` behaviour), and select `事例の背景要因の概要` and
`改善策`. Check UTF-8 SHA-256 hashes of these decoded, stripped fields against
`narrative_sha256`. The extension audit verified all 210 links and three fields, plus
all 15 annual-file hashes. Baseline quotation offsets refer to these exact fields.

Downloading the public corpus does **not**, by itself, reconstruct researcher-written
factor prose, full annotation versions or all contextual evidence used for semantic
judgements. The mapping and code-only factors now identify the study records and enable
recomputation from saved decisions; factor prose and raw quotations remain withheld.

## Conditions for Non-Packaged Research Material

The following describes the current access boundary, not an unconditional promise
that all restricted material is available on request. No general-public access was granted.
The additional linkage and redacted inputs are shared only within this private repository.

| Material | How to obtain or request it | Current conditions |
| --- | --- | --- |
| JCQHC source narratives and public metadata | Obtain directly from the official annual-download/search service | Follow the applicable source terms; check historical hashes |
| Exact sampled-record linkage and historical source version | Included case-ID mapping and annual-file hashes in this private package | Public-release candidate only; team approval and linkage/disclosure review remain required |
| Pseudonymised factor text, quotations and text-based matching evidence | Request a specified verification purpose, required subset and intended handling | Team approval and review of privacy, third-party text and applicable ethics/consent requirements; no automatic release |
| Redacted factor codes, saved alignment decisions and quotation offsets | Included in this private package | Public-release candidate; not equivalent to complete individual exports or semantic validation |
| Full prompt examples or saved AI output | Request only the minimum material needed for the specified audit | Consider a reviewed subset only; full exports are not promised |
| Reviewer identities/contacts, internal comments and session/activity logs, credentials, unrelated paper PDFs and original Git history | No distribution through this package | Not part of the external verification dataset; use only a reviewed non-identifying audit summary where appropriate |

For a restricted request, specify the result to verify, minimum required fields/records,
intended use, recipients and storage/non-redistribution arrangements. The team must
decide what it can lawfully and appropriately provide. No external-request service,
response deadline, approval or delivery has been established by this repository.

## Suggested Manuscript Wording (Draft)

> Original public records can be obtained from the JCQHC case-download service.
> The computational companion contains pseudonymised numerical and categorical inputs,
> redacted individual factor annotations, saved alignment decisions, quotation offsets,
> study-to-JCQHC case linkage, code and version hashes for recomputation conditional on
> saved decisions. It remains private for coauthor review; public release is pending approval.
> Source narratives, factor text, quotations and complete annotation/model-response
> exports are not included. Access to additional de-identified verification material,
> if permissible, requires a separate research-team decision subject to source-use terms
> and applicable privacy and ethics requirements. Identifying reviewer information,
> internal communications and credentials will not be shared through this package.

The live manuscript Data Availability statement is updated separately after a fresh
native backup and revision-controlled edit. Neither this proposal nor that manuscript
edit grants general-public access; private status remains explicit.
