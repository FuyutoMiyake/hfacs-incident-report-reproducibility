# Supplementary Results (Draft)

**Draft snapshot captured 8 October 2026.** See the [supplement index](README.md) for version, scope and pending-review status.

Toward systems-level analysis of medical incident reports: An expert-annotated evaluation of large language models using HFACS (provisional title)

Prepared: Oct 5, 2026

Supplementary Methods: [readable snapshot](supplementary_methods.md).

Abbreviations: AI, artificial intelligence; CI, confidence interval; FTA, fault tree analysis; HFACS, Human Factors Analysis and Classification System; L1-L4, HFACS layers; RS, reference standard; AC1, Gwet's agreement coefficient; CoP, patient condition.

## Table S1. Inter-reviewer classification agreement in RSv1

| Pair | Classification | Records / nodes | Observed agreement (95% CI) | Cohen's kappa (95% CI) | Gwet's AC1 (95% CI) |
| --- | --- | --- | --- | --- | --- |
| AB | Detailed: 22 categories | 24 / 219 | 0.689 (0.615 to 0.758) | 0.628 (0.552 to 0.695) | 0.677 (0.599 to 0.746) |
| AB | Layers: L1-L4 + non-HFACS | 24 / 219 | 0.785 (0.710 to 0.851) | 0.666 (0.583 to 0.745) | 0.745 (0.653 to 0.826) |
| AB | Binary: HFACS / non-HFACS | 24 / 219 | 0.936 (0.908 to 0.965) | 0.871 (0.814 to 0.926) | 0.873 (0.814 to 0.929) |
| CD | Detailed: 22 categories | 29 / 250 | 0.500 (0.415 to 0.584) | 0.402 (0.307 to 0.481) | 0.480 (0.388 to 0.566) |
| CD | Layers: L1-L4 + non-HFACS | 29 / 250 | 0.660 (0.589 to 0.727) | 0.486 (0.411 to 0.552) | 0.594 (0.500 to 0.686) |
| CD | Binary: HFACS / non-HFACS | 29 / 250 | 0.896 (0.855 to 0.931) | 0.792 (0.709 to 0.864) | 0.792 (0.712 to 0.869) |
| EF | Detailed: 22 categories | 28 / 262 | 0.584 (0.503 to 0.657) | 0.488 (0.407 to 0.562) | 0.567 (0.483 to 0.643) |
| EF | Layers: L1-L4 + non-HFACS | 28 / 262 | 0.679 (0.593 to 0.767) | 0.438 (0.334 to 0.535) | 0.627 (0.517 to 0.724) |
| EF | Binary: HFACS / non-HFACS | 28 / 262 | 0.844 (0.783 to 0.896) | 0.665 (0.532 to 0.783) | 0.706 (0.589 to 0.811) |

Primary human analysis: Main 11-50 for each pair, records rated analysable by both reviewers, jointly retained leaf nodes, and post-L1-reassessment labels. Detailed classification comprises 19 HFACS categories plus patient condition (CoP), OTHER, and INAPPROPRIATE. The five-category layer and binary analyses combine the three non-HFACS categories. Counts are the observations entering each classification analysis. Observed agreement is a proportion, not a percentage. Confidence intervals use 2,000 record-cluster bootstrap replicates.

## Table S2. AI classification agreement with adjudicated RSv1

| Model / role | Classification | Records / nodes | Observed agreement (95% CI) | Cohen's kappa (95% CI) | Gwet's AC1 (95% CI) |
| --- | --- | --- | --- | --- | --- |
| GPT-5.6 Sol / primary | Detailed: 20 categories | 37 / 306 | 0.670 (0.599 to 0.735) | 0.427 (0.356 to 0.497) | 0.653 (0.576 to 0.723) |
| GPT-5.6 Sol / primary | Layers: L1-L4 + non-HFACS | 37 / 306 | 0.690 (0.622 to 0.754) | 0.437 (0.362 to 0.515) | 0.641 (0.555 to 0.719) |
| GPT-5.6 Sol / primary | Binary: HFACS / non-HFACS | 37 / 306 | 0.846 (0.801 to 0.890) | 0.668 (0.571 to 0.757) | 0.715 (0.624 to 0.802) |
| Kimi K2.6 / secondary | Detailed: 20 categories | 37 / 306 | 0.693 (0.632 to 0.749) | 0.499 (0.444 to 0.550) | 0.676 (0.608 to 0.736) |
| Kimi K2.6 / secondary | Layers: L1-L4 + non-HFACS | 37 / 306 | 0.716 (0.656 to 0.770) | 0.514 (0.451 to 0.574) | 0.668 (0.592 to 0.736) |
| Kimi K2.6 / secondary | Binary: HFACS / non-HFACS | 37 / 306 | 0.873 (0.835 to 0.909) | 0.734 (0.655 to 0.809) | 0.755 (0.678 to 0.831) |

The final evaluation set contained 50 records; 37 were analysable under the adjudicated RSv1 reference and contributed 306 leaf nodes. AI labels were compared with the adjudicated reference. Detailed classification comprises 19 HFACS categories and one combined non-HFACS category (20 categories in total), unlike the 22-category human analysis in Table S1. The selected GPT configuration was primary; Kimi received the unchanged prompt as a secondary evaluation. Confidence intervals use 5,000 record-cluster bootstrap replicates. Pair-stratified resampling was not used in this final RSv1 analysis.

## Table S3. Sensitivity analyses of RSv1 inter-reviewer classification agreement

| Analysis condition | AB: records / nodes; kappa (95% CI) | CD: records / nodes; kappa (95% CI) | EF: records / nodes; kappa (95% CI) |
| --- | --- | --- | --- |
| Main 11-50; leaf nodes; after L1 reassessment; 22 categories | 24 / 219; 0.628 (0.552 to 0.695) | 29 / 250; 0.402 (0.307 to 0.481) | 28 / 262; 0.488 (0.407 to 0.562) |
| Main 11-50; all non-top nodes; after L1 reassessment; 22 categories | 24 / 321; 0.647 (0.581 to 0.710) | 29 / 383; 0.510 (0.431 to 0.575) | 28 / 401; 0.440 (0.363 to 0.507) |
| Main 11-50; leaf nodes; before L1 reassessment; 22 categories | 24 / 219; 0.573 (0.497 to 0.643) | 29 / 250; 0.478 (0.374 to 0.573) | 28 / 262; 0.418 (0.345 to 0.489) |
| Main 11-50; all non-top nodes; before L1 reassessment; 22 categories | 24 / 321; 0.601 (0.537 to 0.668) | 29 / 383; 0.566 (0.477 to 0.641) | 28 / 401; 0.398 (0.321 to 0.464) |
| Main 1-50; leaf nodes; after L1 reassessment; 22 categories | 33 / 297; 0.609 (0.527 to 0.680) | 36 / 315; 0.431 (0.344 to 0.511) | 37 / 333; 0.539 (0.462 to 0.607) |
| Main 1-50; all non-top nodes; after L1 reassessment; 22 categories | 33 / 443; 0.606 (0.521 to 0.677) | 36 / 478; 0.494 (0.420 to 0.560) | 37 / 509; 0.522 (0.435 to 0.597) |
| Main 1-50; leaf nodes; before L1 reassessment; 22 categories | 33 / 297; 0.579 (0.498 to 0.654) | 36 / 315; 0.529 (0.431 to 0.618) | 37 / 333; 0.526 (0.432 to 0.623) |
| Main 1-50; all non-top nodes; before L1 reassessment; 22 categories | 33 / 443; 0.582 (0.502 to 0.654) | 36 / 478; 0.564 (0.485 to 0.634) | 37 / 509; 0.516 (0.414 to 0.620) |
| Main 11-50; leaf nodes; after L1 reassessment; 20 categories (non-HFACS merged) | 24 / 219; 0.618 (0.533 to 0.696) | 29 / 250; 0.431 (0.356 to 0.491) | 28 / 262; 0.417 (0.320 to 0.518) |
| Main 11-50; leaf nodes; after L1 reassessment; 7 categories (L1-L4 + three non-HFACS categories) | 24 / 219; 0.666 (0.596 to 0.733) | 29 / 250; 0.446 (0.355 to 0.522) | 28 / 262; 0.505 (0.429 to 0.578) |

All rows use records rated analysable by both reviewers and jointly retained nodes. The first row repeats the primary 22-category analysis as the comparison anchor. Main 1-50 adds the earlier records; non-top nodes include intermediate nodes as well as leaves. Before/after L1 reassessment refers to saved reviewer coding versions, not different patients. The eight 22-category rows enumerate all available combinations of record range, node scope, and coding version. The last two rows show alternative grouping of non-HFACS categories; five-category layer and binary results are in Table S1. Blank classification labels were excluded from classification estimates and preserved in the source dataset. Counts and intervals are taken from the existing analysis, with 2,000 record-cluster bootstrap replicates. These are sensitivity analyses, not additional independent validation cohorts.

## Table S4. FTA ranking comparison and scale-up decision

| Ranking method | Top five categories (rank order) | Recall@5 | NDCG@5 |
| --- | --- | --- | --- |
| Frequency | UA_SE, UA_DE, UA_PE, PC_CC, PC_TE | 0.113 | 0.125 |
| Co-occurrence | UA_SE, UA_DE, PC_CC, UA_PE, PC_TE | 0.113 | 0.128 |
| FTA structural | UA_SE, UA_DE, UA_PE, PC_CC, PC_TE | 0.113 | 0.125 |

Population: 87 adjudicated-analysable RSv1 records, Main 11-50 within each pair. Improvement-related targets occurred in 49 records, comprising 62 report-category occurrences; recall@5 was 7/62. Targets combined adjudicated HFACS leaf categories with verbatim improvement quotations and reviewer-added categories, deduplicated within each report. Frequency counts reports containing a leaf category; co-occurrence counts weighted within-report category co-occurrences. FTA ranks categories by interruption of the generated AND/OR tree when their leaves are set false, with minimal-cut-set coverage as a tie-breaker. NDCG is normalised discounted cumulative gain.

Scale-up conditions: recall-difference lower 95% confidence bound > 0, not met; minimum FTA top-five selection rate >= 0.70, met (0.861); top five different from frequency, not met; no improvement-quotation leakage flags, met. Overall decision: do not scale up.

Observed FTA-minus-frequency recall@5 difference: 0.000. The 2,000-resample percentile interval was -0.415 to 0.194, with rankings recomputed in each resample. The saved bootstrap mean (-0.084) is not the observed difference.

## Table S5. FTA versus direct classification: primary RSv1 comparison

| Endpoint | FTA | Direct classification | Difference: FTA minus direct (95% CI) |
| --- | --- | --- | --- |
| Mean precision | 0.363 | 0.277 | 0.086 (0.021 to 0.156) |
| Mean recall | 0.440 | 0.563 | -0.123 (-0.194 to -0.049) |
| All 19 HFACS categories: micro-precision | 0.359 | 0.278 | 0.081 (0.027 to 0.132) |
| All 19 HFACS categories: micro-recall | 0.456 | 0.554 | -0.098 (-0.175 to -0.029) |
| All 19 HFACS categories: micro-F1 | 0.402 | 0.370 | 0.032 (-0.024 to 0.089) |
| L3/L4 combined: micro-precision | 0.520 | 0.459 | 0.061 (-0.092 to 0.213) |
| L3/L4 combined: micro-recall | 0.236 | 0.455 | -0.218 (-0.318 to -0.110) |
| L3/L4 combined: micro-F1 | 0.325 | 0.457 | -0.132 (-0.243 to -0.023) |

Both methods used Kimi K2.5 and event description plus background, without improvement measures. The reference was the report-level set of retained adjudicated RSv1 HFACS leaf categories plus reviewer-added categories. Mean precision and recall were calculated per report and then averaged. Micro metrics pooled report-category true positives, false positives, and false negatives; repeated categories within a report counted once. Paired differences use the same records, with 95% percentile intervals from 2,000 record-cluster bootstrap resamples. L3/L4 metrics pooled the categories in those two layers.

## Table S6. Sensitivity and alternative-target analyses of FTA versus direct classification

| Analysis condition / records | Endpoint | FTA | Direct classification | Difference (95% CI) |
| --- | --- | --- | --- | --- |
| Main 1-50 / 112 | Mean precision | 0.369 | 0.279 | 0.090 (0.034 to 0.147) |
| Main 1-50 / 112 | Mean recall | 0.469 | 0.569 | -0.100 (-0.164 to -0.036) |
| Main 1-50 / 112 | All HFACS: micro-F1 | 0.411 | 0.375 | 0.036 (-0.015 to 0.083) |
| Main 1-50 / 112 | L3/L4: micro-F1 | 0.306 | 0.423 | -0.117 (-0.213 to -0.024) |
| Traceable quotations / 87 | Mean precision | 0.357 | 0.279 | 0.079 (0.009 to 0.149) |
| Traceable quotations / 87 | Mean recall | 0.429 | 0.563 | -0.134 (-0.212 to -0.054) |
| Improvement-related targets / 49 | Mean precision | 0.124 | 0.120 | 0.004 (-0.060 to 0.056) |
| Improvement-related targets / 49 | Mean recall | 0.279 | 0.367 | -0.088 (-0.204 to 0.031) |

Main 1-50 includes all 112 adjudicated-analysable RSv1 records. The traceable-quotation analysis retained predictions linked to quotations locatable in event description or background; this is a traceability filter, not a full-support judgement. The alternative improvement-related target analysis used the 49 records with nonempty targets defined in Table S4. Means assigned precision 1 when both prediction and reference were empty, precision 0 when only the prediction was empty, and recall 1 when the reference was empty. Differences and 95% percentile intervals use 2,000 paired record-cluster resamples. These analyses reuse RSv1 records with alternative populations or prediction/reference conditions.

## Table S7. RSv2 factor-extraction agreement: eligibility and matching sensitivity

| Eligibility / matching | Factor counts: left / right | Matched pairs | Micro-F1 (95% CI) | Both-empty records |
| --- | --- | --- | --- | --- |
| HFACS or indeterminate: same proposition | 81 / 95 | 37 | 0.420 (0.300 to 0.524) | 14 |
| HFACS or indeterminate: same proposition + shared quotation | 81 / 95 | 13 | 0.148 (0.077 to 0.213) | 14 |
| HFACS or indeterminate: including partial overlap | 81 / 95 | 45 | 0.511 (0.400 to 0.613) | 14 |
| HFACS only: same proposition | 81 / 73 | 32 | 0.416 (0.290 to 0.526) | 16 |
| HFACS only: same proposition + shared quotation | 81 / 73 | 10 | 0.130 (0.055 to 0.203) | 16 |
| HFACS only: including partial overlap | 81 / 73 | 37 | 0.481 (0.359 to 0.591) | 16 |
| All factors: same proposition | 87 / 157 | 39 | 0.320 (0.221 to 0.412) | 13 |
| All factors: same proposition + shared quotation | 87 / 157 | 13 | 0.107 (0.052 to 0.158) | 13 |
| All factors: including partial overlap | 87 / 157 | 48 | 0.393 (0.291 to 0.488) | 13 |

All conditions used the same 60 records and AI-assisted one-to-one factor correspondences. Left and right counts pool the first and second reviewers within each pair, not two reviewers of all 60 records. Main condition: HFACS or indeterminate eligibility and same-proposition matching. Strict matching additionally required a shared quotation; partial matching admitted saved partial-overlap correspondences. Both-empty records were counted separately and not assigned F1 = 1. Intervals are saved 95% percentile intervals from 3,000 record-cluster bootstrap resamples stratified by pair.

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
| AB / 20 | 12/20 (60.0%) | 7/20 (35.0%) | 0.398 (0.057 to 0.716) | 0.113 (-0.226 to 0.412) |
| CD / 20 | 10/20 (50.0%) | 10/20 (50.0%) | 0.348 (-0.011 to 0.639) | 0.245 (0.000 to 0.541) |
| EF / 20 | 9/20 (45.0%) | 9/20 (45.0%) | 0.400 (0.137 to 0.650) | 0.388 (0.110 to 0.643) |
| All pairs / 60 | 31/60 (51.7%) | 26/60 (43.3%) | Not pooled | Not pooled |

Each pair assessed its own 20 records. Exact agreement requires identical three-state analysability ratings. Kappa uses linear weights for ordered responses. Pairwise intervals are saved 95% percentile record-cluster bootstrap intervals (3,000 resamples). All-pair exact agreement pools counts; no pooled weighted kappa is reported.

Within-reviewer transitions (120 responses): 19 to a more analysable state, 7 to a less analysable state, and 94 unchanged. From not analysable: 39 remained not analysable, 2 became uncertain, 0 became clear. From uncertain: 1 became not analysable, 16 remained uncertain, 17 became clear. From clear: 2 became not analysable, 4 became uncertain, 39 remained clear.

## Table S10. Inter-reviewer HFACS layer agreement on the same matched factors

| Reviewer pair | Matched factors with layers at both stages | Exact layer-set agreement: before -> after | At least one shared layer: before -> after | Single-layer factors at both stages | Nominal kappa: before -> after |
| --- | --- | --- | --- | --- | --- |
| All pairs | 32 | 25/32 (78.1%) -> 21/32 (65.6%) | 25/32 (78.1%) -> 27/32 (84.4%) | 26 | 0.668 -> 0.668 |
| AB | 7 | 4/7 (57.1%) -> 1/7 (14.3%) | 4/7 (57.1%) -> 6/7 (85.7%) | 2 | 0.333 -> 0.333 |
| CD | 14 | 12/14 (85.7%) -> 11/14 (78.6%) | 12/14 (85.7%) -> 12/14 (85.7%) | 13 | 0.755 -> 0.755 |
| EF | 11 | 9/11 (81.8%) -> 9/11 (81.8%) | 9/11 (81.8%) -> 9/11 (81.8%) | 11 | 0.450 -> 0.450 |

The same 32 factor pairs had HFACS layer classifications from both reviewers at both stages. Exact agreement requires identical layer sets; shared-layer agreement requires at least one common layer. The singleton subset requires a single layer from both reviewers at both stages (26 factor pairs). The all-pair singleton kappa pools three different pair-specific samples; the six reviewers did not rate a common set of records. Nominal kappa uses no ordering of HFACS layers.

## Table S11. Exploratory AI classification of RSv2 consensus factors

| Evaluation population / endpoint | Factors evaluated | Agreement or candidate hits | Nominal kappa (95% CI) |
| --- | --- | --- | --- |
| Any reference label: candidate hit | 105 | 46/105 (43.8%) | Not calculated |
| At least one HFACS reference label: candidate hit | 90 | 32/90 (35.6%) | Not calculated |
| Single HFACS reference label: detailed category | 75 | 25/75 (33.3%) | 0.240 (0.102 to 0.391) |
| Single HFACS reference label: HFACS layer | 75 | 40/75 (53.3%) | 0.373 (0.208 to 0.552) |

The frozen RSv1 classification configuration received the 110 consensus factor texts and original three narrative fields. Five unclassified factors were not scored against a reference label. Candidate hits require one AI category to match any reference category; exact full-set agreement is not required. Kappa is restricted to 75 factors with one HFACS reference label. Predictions could include non-HFACS categories. Intervals are saved 95% percentile record-cluster bootstrap intervals (3,000 resamples).

## Supplementary Results. Evidence, relations, difficulty and recorded time

All saved quotations were locatable in the supplied narratives for 244 independent and 110 consensus factors. Quotations came exclusively from improvement text for 70/244 independent factors (28.7%) and 35/110 consensus factors (31.8%). This check assessed quotation traceability.

Exploratory directed-relation micro-F1 was 0.301, with 25 matched relations among 82 left-reviewer and 84 right-reviewer relations across 60 records. Pair-specific micro-F1 values were AB 0.133 (3 matches; 23/22 relations), CD 0.348 (12 matches; 37/32 relations), and EF 0.385 (10 matches; 22/30 relations). Relation correspondence used the AI-assisted factor matches.

For the main extraction rule, micro-F1 was 0.453 (0.292 to 0.600) in 34 records where either reviewer reported unclear actor, role or scope, and 0.371 (0.241 to 0.507) in 26 other records. Group factor counts (left/right) were 42/64 and 39/31, with 24 and 13 matched factors, respectively. These are descriptive subgroup estimates, not an adjusted comparison.

Across 46 records with defined factor F1 and recorded time, Spearman's rho between record-level factor F1 and mean reviewer evaluation time was -0.003 (p = 0.984). The 14 both-empty records had undefined F1 and were not included in this correlation. This analysis did not estimate the association between actor uncertainty and time directly.

Median saved independent-evaluation time was 4.94 minutes (interquartile range [IQR], 2.24 to 11.80; 120 responses). Median reassessment activity time was 1.13 minutes (IQR, 0.46 to 2.97; 120 responses). Reassessment activity time excluded inactive intervals. The two timing measures describe different tasks and collection procedures.

## Computational provenance

These tables were assembled from saved analysis outputs; no annotations or model evaluations were rerun for this revision. Detailed script and source-hash inventories are retained separately with the repository-preparation materials (public URL pending).
