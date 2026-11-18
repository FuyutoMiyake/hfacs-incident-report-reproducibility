# Supplementary Results

Toward systems-level analysis of medical incident reports: A clinician-annotated evaluation of large language models using HFACS

Abbreviations: AI, artificial intelligence; CI, confidence interval; FTA, fault tree analysis; HFACS, Human Factors Analysis and Classification System; L1-L4, HFACS layers; RS, reference standard; AC1, Gwet's agreement coefficient; CoP, patient condition.

## Table S1. Inter-reviewer classification agreement in RSv1

| Pair | Classification | Records / nodes | Observed agreement (95% CI) | Cohen's kappa (95% CI) | Gwet's AC1 (95% CI) |
| --- | --- | --- | --- | --- | --- |
| All pairs | Detailed: 22 categories | 81 / 731 | 0.587 (0.540 to 0.633) | 0.503 (0.456 to 0.548) | 0.570 (0.521 to 0.618) |
| All pairs | Layers: L1-L4 + non-HFACS | 81 / 731 | 0.705 (0.661 to 0.748) | 0.529 (0.478 to 0.576) | 0.650 (0.594 to 0.705) |
| All pairs | Binary: HFACS / non-HFACS | 81 / 731 | 0.889 (0.861 to 0.914) | 0.775 (0.716 to 0.825) | 0.782 (0.727 to 0.833) |
| AB | Detailed: 22 categories | 24 / 219 | 0.689 (0.617 to 0.758) | 0.628 (0.551 to 0.695) | 0.677 (0.599 to 0.748) |
| AB | Layers: L1-L4 + non-HFACS | 24 / 219 | 0.785 (0.715 to 0.852) | 0.666 (0.583 to 0.747) | 0.745 (0.654 to 0.826) |
| AB | Binary: HFACS / non-HFACS | 24 / 219 | 0.936 (0.908 to 0.964) | 0.871 (0.812 to 0.926) | 0.873 (0.816 to 0.929) |
| CD | Detailed: 22 categories | 29 / 250 | 0.500 (0.411 to 0.583) | 0.402 (0.307 to 0.484) | 0.480 (0.387 to 0.569) |
| CD | Layers: L1-L4 + non-HFACS | 29 / 250 | 0.660 (0.588 to 0.727) | 0.486 (0.409 to 0.551) | 0.594 (0.499 to 0.679) |
| CD | Binary: HFACS / non-HFACS | 29 / 250 | 0.896 (0.857 to 0.932) | 0.792 (0.707 to 0.862) | 0.792 (0.716 to 0.866) |
| EF | Detailed: 22 categories | 28 / 262 | 0.584 (0.505 to 0.659) | 0.488 (0.409 to 0.560) | 0.567 (0.485 to 0.645) |
| EF | Layers: L1-L4 + non-HFACS | 28 / 262 | 0.679 (0.594 to 0.760) | 0.438 (0.335 to 0.537) | 0.627 (0.517 to 0.726) |
| EF | Binary: HFACS / non-HFACS | 28 / 262 | 0.844 (0.780 to 0.899) | 0.665 (0.532 to 0.779) | 0.706 (0.583 to 0.813) |

Primary analysis: records 11-50 within each pair, rated analysable by both reviewers, using jointly retained leaves and post-L1-reassessment labels. Detailed classification includes 19 HFACS categories plus CoP, OTHER and INAPPROPRIATE; layer and binary analyses combine the three non-HFACS categories. Counts show analysed records/nodes; observed agreement is a proportion. All intervals use 10,000 record-cluster bootstrap resamples. Pooled estimates combine 81 records and 731 leaves; resampling was stratified by reviewer pair (seeds 20261014, 20261015 and 20261016 for detailed, layer and binary classifications). Pairs reviewed different records.

## Table S2. AI classification agreement with adjudicated RSv1

| Model / role | Classification | Records / nodes | Observed agreement (95% CI) | Cohen's kappa (95% CI) | Gwet's AC1 (95% CI) |
| --- | --- | --- | --- | --- | --- |
| GPT-5.6 Sol / primary | Detailed: 20 categories | 37 / 306 | 0.670 (0.599 to 0.733) | 0.427 (0.359 to 0.493) | 0.653 (0.576 to 0.720) |
| GPT-5.6 Sol / primary | Layers: L1-L4 + non-HFACS | 37 / 306 | 0.690 (0.620 to 0.751) | 0.437 (0.365 to 0.509) | 0.641 (0.553 to 0.717) |
| GPT-5.6 Sol / primary | Binary: HFACS / non-HFACS | 37 / 306 | 0.846 (0.803 to 0.889) | 0.668 (0.574 to 0.754) | 0.715 (0.625 to 0.799) |
| Kimi K2.6 / secondary | Detailed: 20 categories | 37 / 306 | 0.693 (0.634 to 0.749) | 0.499 (0.445 to 0.551) | 0.676 (0.610 to 0.737) |
| Kimi K2.6 / secondary | Layers: L1-L4 + non-HFACS | 37 / 306 | 0.716 (0.659 to 0.770) | 0.514 (0.453 to 0.573) | 0.668 (0.594 to 0.736) |
| Kimi K2.6 / secondary | Binary: HFACS / non-HFACS | 37 / 306 | 0.873 (0.834 to 0.911) | 0.734 (0.654 to 0.809) | 0.755 (0.677 to 0.832) |

The final evaluation set contained 50 records; 37 were analysable under the adjudicated RSv1 reference and contributed 306 leaf nodes. AI labels were compared with the adjudicated reference. Detailed classification comprises 19 HFACS categories and one combined non-HFACS category (20 categories in total), unlike the 22-category human analysis in Table S1. The selected GPT configuration was primary; Kimi received the unchanged prompt as a secondary evaluation. Confidence intervals use 10,000 record-cluster bootstrap replicates. Resampling was stratified by reviewer pair, preserving the observed pair-specific record counts (seed 20260722).

## Table S3. Sensitivity analyses of RSv1 inter-reviewer classification agreement

| Analysis condition | AB: records / nodes; kappa (95% CI) | CD: records / nodes; kappa (95% CI) | EF: records / nodes; kappa (95% CI) |
| --- | --- | --- | --- |
| Main 11-50; leaf nodes; after L1 reassessment; 22 categories | 24 / 219; 0.628 (0.551 to 0.695) | 29 / 250; 0.402 (0.307 to 0.484) | 28 / 262; 0.488 (0.409 to 0.560) |
| Main 11-50; all non-top nodes; after L1 reassessment; 22 categories | 24 / 321; 0.647 (0.581 to 0.709) | 29 / 383; 0.510 (0.431 to 0.575) | 28 / 401; 0.440 (0.361 to 0.509) |
| Main 11-50; leaf nodes; before L1 reassessment; 22 categories | 24 / 219; 0.573 (0.496 to 0.644) | 29 / 250; 0.478 (0.371 to 0.572) | 28 / 262; 0.418 (0.344 to 0.490) |
| Main 11-50; all non-top nodes; before L1 reassessment; 22 categories | 24 / 321; 0.601 (0.536 to 0.668) | 29 / 383; 0.566 (0.476 to 0.640) | 28 / 401; 0.398 (0.322 to 0.468) |
| Main 1-50; leaf nodes; after L1 reassessment; 22 categories | 33 / 297; 0.609 (0.528 to 0.681) | 36 / 315; 0.431 (0.344 to 0.508) | 37 / 333; 0.539 (0.464 to 0.608) |
| Main 1-50; all non-top nodes; after L1 reassessment; 22 categories | 33 / 443; 0.606 (0.523 to 0.677) | 36 / 478; 0.494 (0.420 to 0.560) | 37 / 509; 0.522 (0.439 to 0.596) |
| Main 1-50; leaf nodes; before L1 reassessment; 22 categories | 33 / 297; 0.579 (0.496 to 0.656) | 36 / 315; 0.529 (0.432 to 0.614) | 37 / 333; 0.526 (0.430 to 0.626) |
| Main 1-50; all non-top nodes; before L1 reassessment; 22 categories | 33 / 443; 0.582 (0.504 to 0.653) | 36 / 478; 0.564 (0.486 to 0.631) | 37 / 509; 0.516 (0.417 to 0.616) |
| Main 11-50; leaf nodes; after L1 reassessment; 20 categories (non-HFACS merged) | 24 / 219; 0.618 (0.536 to 0.695) | 29 / 250; 0.431 (0.354 to 0.494) | 28 / 262; 0.417 (0.318 to 0.518) |
| Main 11-50; leaf nodes; after L1 reassessment; 7 categories (L1-L4 + three non-HFACS categories) | 24 / 219; 0.666 (0.594 to 0.733) | 29 / 250; 0.446 (0.353 to 0.520) | 28 / 262; 0.505 (0.428 to 0.576) |

All rows use records rated analysable by both reviewers and jointly retained nodes. The first row repeats the primary 22-category analysis as the comparison anchor. Main 1-50 adds the earlier records; non-top nodes include intermediate nodes as well as leaves. Before/after L1 reassessment refers to saved reviewer coding versions, not different patients. The eight 22-category rows enumerate all available combinations of record range, node scope, and coding version. The last two rows show alternative grouping of non-HFACS categories; five-category layer and binary results are in Table S1. Blank classification labels were excluded from classification estimates and preserved in the source dataset. Counts and intervals are taken from the existing analysis, with 10,000 record-cluster bootstrap replicates. These are sensitivity analyses, not additional independent validation cohorts.

## Table S4. FTA ranking comparison and scale-up decision

| Ranking method | Top five categories (rank order) | Recall@5 | NDCG@5 |
| --- | --- | --- | --- |
| Frequency | UA_SE, UA_DE, UA_PE, PC_CC, PC_TE | 0.113 | 0.125 |
| Co-occurrence | UA_SE, UA_DE, PC_CC, UA_PE, PC_TE | 0.113 | 0.128 |
| FTA structural | UA_SE, UA_DE, UA_PE, PC_CC, PC_TE | 0.113 | 0.125 |

Population: 87 adjudicated-analysable RSv1 records, Main 11-50 within each pair. Improvement-related targets occurred in 49 records, comprising 62 report-category occurrences; recall@5 was 7/62. Targets combined adjudicated HFACS leaf categories with verbatim improvement quotations and reviewer-added categories, deduplicated within each report. Frequency counts reports containing a leaf category; co-occurrence counts weighted within-report category co-occurrences. FTA ranks categories by interruption of the generated AND/OR tree when their leaves are set false, with minimal-cut-set coverage as a tie-breaker. NDCG is normalised discounted cumulative gain.

Scale-up conditions: recall-difference lower 95% confidence bound &gt; 0, not met; minimum FTA top-five selection rate &gt;= 0.70, met (0.869); top five different from frequency, not met; no improvement-quotation leakage flags, met. Overall decision: do not scale up.

Observed FTA-minus-frequency recall@5 difference: 0.000. The 10,000-resample percentile interval was -0.411 to 0.128, with rankings recomputed in each reviewer-pair-stratified record resample. The bootstrap mean (-0.085) is not the observed difference.

## Table S5. FTA versus direct classification in the main RSv1 cohort

| Endpoint | FTA | Direct classification | Difference: FTA minus direct (95% CI) |
| --- | --- | --- | --- |
| Mean precision | 0.363 | 0.277 | 0.086 (0.021 to 0.152) |
| Mean recall | 0.440 | 0.563 | -0.123 (-0.195 to -0.050) |
| All 19 HFACS categories: micro-precision | 0.359 | 0.278 | 0.081 (0.031 to 0.134) |
| All 19 HFACS categories: micro-recall | 0.456 | 0.554 | -0.098 (-0.167 to -0.030) |
| All 19 HFACS categories: micro-F1 | 0.402 | 0.370 | 0.032 (-0.024 to 0.086) |
| L3/L4 combined: micro-precision | 0.520 | 0.459 | 0.061 (-0.091 to 0.217) |
| L3/L4 combined: micro-recall | 0.236 | 0.455 | -0.218 (-0.314 to -0.124) |
| L3/L4 combined: micro-F1 | 0.325 | 0.457 | -0.132 (-0.237 to -0.028) |

Both methods used Kimi K2.5 and event description plus background, without improvement measures. The reference was the report-level set of retained adjudicated RSv1 HFACS leaf categories plus reviewer-added categories. Mean precision and recall were calculated per report and then averaged. Micro metrics pooled report-category true positives, false positives, and false negatives; repeated categories within a report counted once. Paired differences use the same records, with 95% percentile intervals from 10,000 record-cluster bootstrap resamples stratified by reviewer pair. L3/L4 metrics pooled the categories in those two layers.

## Table S6. Sensitivity and alternative-target analyses of FTA versus direct classification

| Analysis condition / records | Endpoint | FTA | Direct classification | Difference (95% CI) |
| --- | --- | --- | --- | --- |
| Main 1-50 / 112 | Mean precision | 0.369 | 0.279 | 0.090 (0.034 to 0.145) |
| Main 1-50 / 112 | Mean recall | 0.469 | 0.569 | -0.100 (-0.161 to -0.038) |
| Main 1-50 / 112 | All HFACS: micro-F1 | 0.411 | 0.375 | 0.036 (-0.011 to 0.082) |
| Main 1-50 / 112 | L3/L4: micro-F1 | 0.306 | 0.423 | -0.117 (-0.207 to -0.026) |
| Traceable quotations / 87 | Mean precision | 0.357 | 0.279 | 0.079 (0.013 to 0.144) |
| Traceable quotations / 87 | Mean recall | 0.429 | 0.563 | -0.134 (-0.208 to -0.062) |
| Improvement-related targets / 49 | Mean precision | 0.124 | 0.120 | 0.004 (-0.057 to 0.057) |
| Improvement-related targets / 49 | Mean recall | 0.279 | 0.367 | -0.088 (-0.204 to 0.020) |

Main 1-50 includes all 112 adjudicated-analysable RSv1 records. The traceable-quotation analysis retained predictions linked to quotations locatable in event description or background; this is a traceability filter, not a full-support judgement. The alternative improvement-related target analysis used the 49 records with nonempty targets defined in Table S4. Means assigned precision 1 when both prediction and reference were empty, precision 0 when only the prediction was empty, and recall 1 when the reference was empty. Differences and 95% percentile intervals use 10,000 paired record-cluster resamples stratified by reviewer pair. These analyses reuse RSv1 records with alternative populations or prediction/reference conditions.

## Table S7. RSv2 factor-extraction agreement: eligibility and matching sensitivity

| Eligibility / matching | Factor counts: left / right | Matched pairs | Micro-F1 (95% CI) | Both-empty records |
| --- | --- | --- | --- | --- |
| HFACS or indeterminate: same proposition | 81 / 95 | 37 | 0.420 (0.303 to 0.527) | 14 |
| HFACS or indeterminate: same proposition + shared quotation | 81 / 95 | 13 | 0.148 (0.080 to 0.214) | 14 |
| HFACS or indeterminate: including partial overlap | 81 / 95 | 45 | 0.511 (0.400 to 0.610) | 14 |
| HFACS only: same proposition | 81 / 73 | 32 | 0.416 (0.291 to 0.526) | 16 |
| HFACS only: same proposition + shared quotation | 81 / 73 | 10 | 0.130 (0.056 to 0.204) | 16 |
| HFACS only: including partial overlap | 81 / 73 | 37 | 0.481 (0.357 to 0.589) | 16 |
| All factors: same proposition | 91 / 157 | 39 | 0.315 (0.220 to 0.410) | 13 |
| All factors: same proposition + shared quotation | 91 / 157 | 13 | 0.105 (0.054 to 0.157) | 13 |
| All factors: including partial overlap | 91 / 157 | 48 | 0.387 (0.290 to 0.480) | 13 |

All conditions used the same 60 records and AI-assisted one-to-one factor correspondences. Left and right counts pool the first and second reviewers within each pair, not two reviewers of all 60 records. Main condition: HFACS or indeterminate eligibility and same-proposition matching. Strict matching additionally required a shared quotation; partial matching admitted saved partial-overlap correspondences. Both-empty records were counted separately and not assigned F1 = 1. Intervals are saved 95% percentile intervals from 10,000 record-cluster bootstrap resamples stratified by pair. These analyses use the preserved independent-response versions specified in Supplementary Methods S7. Using the later four response versions instead reduced the total factor count from 248 to 244; main-eligibility micro-F1 remained 0.420, whereas all-factor micro-F1 was 0.320 (0.224 to 0.417), compared with 0.315 (0.220 to 0.410) in the selected independent versions. In CD, all-factor micro-F1 was 0.366 (0.209 to 0.523) with the later versions versus 0.349 (0.198 to 0.505) with the selected versions. The correspondence table was unchanged and restored CoP factors were not rematched. On the 37 main-eligibility matched factor pairs, detailed-classification nominal kappa was 0.446 (0.242 to 0.632); on the 32 pairs with one HFACS layer per reviewer, nominal kappa was 0.639 (0.402 to 0.856). These 95% intervals used 10,000 pair-stratified resamples of all 60 records (seed 20261107); all replicates were valid. The matched-factor units and point estimates were identical under both response versions.

## Table S8. RSv2 consensus dataset and stored human resolution codes

| Measure / counting unit | All pairs | AB | CD | EF |
| --- | --- | --- | --- | --- |
| Records | 60 | 20 | 20 | 20 |
| Consensus factors | 110 | 30 | 41 | 39 |
| Records: analysable without uncertainty | 15 | 2 | 4 | 9 |
| Records: analysable with uncertainty | 23 | 12 | 8 | 3 |
| Records: not analysable | 22 | 6 | 8 | 8 |
| Factors: multiple labels | 15 | 7 | 2 | 6 |
| Factors: multiple HFACS layers | 10 | 7 | 2 | 1 |
| Factors: no classification | 5 | 1 | 0 | 4 |
| Human factor code: source-confirmed | 48 | 0 | 12 | 36 |
| Human factor code: rule-adjudicated | 1 | 0 | 0 | 1 |
| Human factor code: unresolved | 2 | 0 | 0 | 2 |
| Human factor code: missing | 59 | 30 | 29 | 0 |

Counts are records or factors as specified. Multiple-layer factors are a subset of multiple-label factors. Human resolution-code counts are saved factor-level codes, not post-hoc large language model (LLM) judgements. Missing codes: 59/110 (53.6%); no resolution state was imputed. Stored codes do not establish independently verified complete evidentiary support.

## Table S9. Analysability agreement before and after public-information reassessment

| Reviewer pair / records | Exact agreement: before | Exact agreement: after | Weighted kappa: before (95% CI) | Weighted kappa: after (95% CI) |
| --- | --- | --- | --- | --- |
| AB / 20 | 12/20 (60.0%) | 7/20 (35.0%) | 0.398 (0.051 to 0.713) | 0.113 (-0.232 to 0.417) |
| CD / 20 | 10/20 (50.0%) | 10/20 (50.0%) | 0.348 (-0.007 to 0.639) | 0.245 (0.000 to 0.541) |
| EF / 20 | 9/20 (45.0%) | 9/20 (45.0%) | 0.400 (0.137 to 0.648) | 0.388 (0.091 to 0.645) |
| All pairs / 60 | 31/60 (51.7%) | 26/60 (43.3%) | 0.386 (0.189 to 0.564) | 0.203 (-0.011 to 0.395) |

Each pair assessed its own 20 records. Exact agreement requires identical three-state analysability responses. Kappa uses linear weights for ordered responses. Pairwise intervals are saved 95% percentile record-cluster bootstrap intervals (10,000 resamples). All-pair exact agreement pools counts; pooled linear weighted kappa and its 95% CI use 10,000 record-cluster resamples stratified by pair, with seeds 20261024 before and 20261025 after reassessment.

Within-reviewer transitions (120 responses): 19 to a more analysable state, 7 to a less analysable state, and 94 unchanged. From not analysable: 39 remained not analysable, 2 became analysable with uncertainty, and 0 became analysable without uncertainty. From analysable with uncertainty: 1 became not analysable, 16 remained analysable with uncertainty, and 17 became analysable without uncertainty. From analysable without uncertainty: 2 became not analysable, 4 became analysable with uncertainty, and 39 remained analysable without uncertainty.

Within-reviewer classification changes: 26/244 fixed factor-reviewer units (10.7%) had different recorded label sets; six became unclassified. All 244 baseline factors had a corresponding follow-up factor ID; none had an empty baseline label set. Empty follow-up sets were counted as changes, not excluded. Of 176 baseline HFACS-or-indeterminate factors, 20 changed (11.4%). Counts by pair were AB 24/86, CD 2/82, and EF 0/76. These are descriptive counts, not isolated reviewer effects.

## Table S10. Inter-reviewer HFACS layer agreement on the same matched factors

| Reviewer pair | Matched factors with layers at both stages | Exact layer-set agreement: before -&gt; after | At least one shared layer: before -&gt; after | Single-layer factors at both stages | Nominal kappa: before -&gt; after |
| --- | --- | --- | --- | --- | --- |
| All pairs | 32 | 25/32 (78.1%) -&gt; 21/32 (65.6%) | 25/32 (78.1%) -&gt; 27/32 (84.4%) | 26 | 0.668 -&gt; 0.668 |
| AB | 7 | 4/7 (57.1%) -&gt; 1/7 (14.3%) | 4/7 (57.1%) -&gt; 6/7 (85.7%) | 2 | 0.333 -&gt; 0.333 |
| CD | 14 | 12/14 (85.7%) -&gt; 11/14 (78.6%) | 12/14 (85.7%) -&gt; 12/14 (85.7%) | 13 | 0.755 -&gt; 0.755 |
| EF | 11 | 9/11 (81.8%) -&gt; 9/11 (81.8%) | 9/11 (81.8%) -&gt; 9/11 (81.8%) | 11 | 0.450 -&gt; 0.450 |

The same 32 factor pairs had HFACS layer classifications from both reviewers at both stages. Exact agreement requires identical layer sets; shared-layer agreement requires at least one common layer. The singleton subset requires a single layer from both reviewers at both stages (26 factor pairs). The all-pair singleton kappa pools three different pair-specific samples; the six reviewers did not rate a common set of records. Nominal kappa uses no ordering of HFACS layers. Pooled nominal kappa on the fixed 26 single-layer pairs was 0.668 (0.378 to 0.892) before and 0.668 (0.378 to 0.892) after reassessment (95% CIs). Both stages used identical draws from 60 record clusters stratified by pair (10,000 resamples; seed 20261107); all replicates were valid. The layer labels on these 26 pairs were unchanged.

## Table S11. Exploratory AI classification of RSv2 consensus factors

| Evaluation population / endpoint | Factors evaluated | Agreement or candidate hits | Nominal kappa (95% CI) |
| --- | --- | --- | --- |
| Any reference label: candidate hit | 105 | 46/105 (43.8%) | Not calculated |
| At least one HFACS reference label: candidate hit | 90 | 32/90 (35.6%) | Not calculated |
| Single HFACS reference label: detailed category | 75 | 25/75 (33.3%) | 0.240 (0.101 to 0.390) |
| Single HFACS reference label: HFACS layer | 75 | 40/75 (53.3%) | 0.373 (0.208 to 0.555) |

The frozen RSv1 classification configuration received the 110 consensus factor texts and original three narrative fields. Five unclassified factors were not scored against a reference label. Candidate hits require one AI category to match any reference category; exact full-set agreement is not required. Kappa is restricted to 75 factors with one HFACS reference label. Predictions could include non-HFACS categories. Intervals are saved 95% percentile record-cluster bootstrap intervals (10,000 resamples). The 110 factors comprised five without a classification label, 15 labelled only CoP, 15 with multiple HFACS labels, and 75 with one HFACS label: 110 minus 5 = 105 labelled factors; 105 minus 15 = 90 with HFACS labels; 90 minus 15 = 75 single-HFACS-label factors. Human resolution status is separate from classification: among the 75 single-HFACS-label factors, 29 were source-confirmed, one was rule-adjudicated and 45 had missing resolution status. Missing status did not imply a missing classification label. Of the 50 detailed-classification disagreements, 15 were non-HFACS predictions (11 INAPPROPRIATE and four CoP) and 35 were other HFACS categories. Non-HFACS predictions were retained as disagreements.

## Supplementary Results. Evidence, relations, difficulty and recorded time

All saved quotations were locatable in the supplied narratives for 248 independent and 110 consensus factors. Quotations came exclusively from improvement text for 70/248 independent factors (28.2%) and 35/110 consensus factors (31.8%). This check assessed quotation traceability.

Exploratory directed-relation micro-F1 was 0.291 (0.188 to 0.386) (95% CI), with 23 matched relations among 74 left-reviewer and 84 right-reviewer relations across 60 records. Pair-specific micro-F1 values were AB 0.133 (3 matches; 23/22 relations), CD 0.328 (10 matches; 29/32 relations), and EF 0.385 (10 matches; 22/30 relations). The overall interval used 10,000 pair-stratified record-cluster resamples (seed 20261107; all replicates valid). Relation correspondence used the saved AI-assisted factor matches. Using the later four response versions instead gave micro-F1 0.301 (25 matches; 82/84 relations); the selected versions gave 0.291. The intervals quantify sampling variability conditional on matching, not matching accuracy.

For the main extraction rule, micro-F1 was 0.453 (0.282 to 0.598) in 34 records where either reviewer reported unclear actor, role or scope, and 0.371 (0.242 to 0.508) in 26 other records. Group factor counts (left/right) were 42/64 and 39/31, with 24 and 13 matched factors, respectively. These are descriptive subgroup estimates, not an adjusted comparison.

Across 46 records with defined factor F1 and recorded time, Spearman's rho between record-level factor F1 and mean reviewer evaluation time was -0.001 (p = 0.994). The 14 both-empty records had undefined F1 and were not included in this correlation. This analysis did not estimate the association between actor uncertainty and time directly.

Median saved independent-evaluation time was 4.84 minutes (interquartile range [IQR], 2.24 to 11.80; 120 responses). Median reassessment activity time was 1.13 minutes (IQR, 0.46 to 2.97; 120 responses). Reassessment activity time excluded inactive intervals. The two timing measures describe different tasks and collection procedures. Using the later four responses instead gave a median of 4.94 minutes and a time-F1 correlation of -0.003 (p = 0.984), versus 4.84 minutes and -0.001 (p = 0.994) for the selected independent versions. Both versions had 70 factors with quotations exclusively from improvement text: 70/244 (28.7%) versus 70/248 (28.2%). Reassessment results used the actually presented 244-factor baseline throughout.

## Computational provenance

The review revision recalculated RSv1 pooled human, final AI and FTA confidence intervals with 10,000 reviewer-pair-stratified record resamples; selected preserved response versions for independent RSv2 analyses; and added the specified RSv2 agreement intervals. No annotations, model predictions or semantic correspondences were regenerated. Original and revised outputs, executable scripts, seeds and input hashes are retained in analysis_npj/analysis_runs/review_revision_20261107.
