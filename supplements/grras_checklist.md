# GRRAS reporting checklist correspondence (draft)

**Draft snapshot captured 8 October 2026.** See the [supplement index](README.md) for version, scope and pending-review status.

Reviewed on: Oct 8, 2026

Abbreviations: GRRAS, Guidelines for Reporting Reliability and Agreement Studies; HFACS, Human Factors Analysis and Classification System; JCQHC, Japan Council for Quality Health Care; RS, reference standard; FTA, fault tree analysis; AI, artificial intelligence.

Scope: Inter-reviewer agreement in the HFACS-based contributing-factor assessment procedure. AI-reference comparisons, FTA added value and sequential reassessment are described separately.

Status: Reported = information is present; Partial = clarification or confirmation is needed; Pending = not yet provided. These are reporting checks, not validity scores. Requirements below are paraphrased from GRRAS Table 1.

Supplementary Methods: [readable snapshot](supplementary_methods.md).

Supplementary Results: [readable snapshot](supplementary_results.md).

## Table. GRRAS 15-item correspondence

| No. | Reporting requirement | Manuscript location | Coverage / action needed |
| --- | --- | --- | --- |
| 1 | Identify inter-rater or intra-rater reliability/agreement in the title or abstract. | Title; abstract not yet drafted | Pending. Add inter-reviewer agreement to the abstract. The current title need not be replaced solely for this item. |
| 2 | Name and describe the assessment procedure or measurement tool. | Methods 2.1, 2.2, 2.4; Supplementary Methods S3, Table SM1 | Reported. The HFACS-based extraction, quotation, classification and structuring procedure and category definitions are described. |
| 3 | Specify the population of subjects or objects of interest. | Methods 2.1; Supplementary Methods S1 | Reported. The sampling frame is 61,606 public JCQHC records from 2010-2024. Inputs are public fields, not complete hospital investigation reports. |
| 4 | Specify the population of raters of interest, where applicable. | Methods 2.2, 2.4; Supplementary Methods S2, S7 | Partial. Six clinicians are identified. Describe reviewer eligibility and the clinical expertise represented; do not infer actual experience from the original planned criterion. |
| 5 | Summarise prior reliability/agreement evidence and explain the rationale. | Introduction not yet drafted; Methods 2.1 | Pending. Add prior evidence and why agreement was assessed separately for AI-generated candidates and independent human extraction. |
| 6 | Explain sample size choice and planned raters, objects and replicate ratings. | Methods 2.2, 2.4, 2.5; Supplementary Methods S2, S7 | Partial. Counts are stated; explain the choice of 150 and 60 records. Earlier kappa planning used a different three-rater design and does not establish adequacy of the final two-rater cohort. |
| 7 | Describe sampling of raters and subjects or objects. | Methods 2.2, 2.4; Supplementary Methods S2, S7 | Partial. Record sampling, seeds and exclusions are described. Add the reviewer recruitment/selection method, if documented. |
| 8 | Describe the rating process, timing, information available and blinding. | Methods 2.2, 2.4, 2.5; Supplementary Methods S2c, S7, S8 | Partial. Inputs, calibration, consensus and non-blinded reassessment are described. Confirm training details and intervals between assessment stages from existing records. |
| 9 | State whether ratings or measurements were obtained independently. | Methods 2.2, 2.4, 2.5; Supplementary Methods S2c, S7, S8 | Reported. Initial reviews were independent; RSv2 partner responses were hidden. Four saved updates after consensus viewing and non-blinded reassessment are disclosed. |
| 10 | Describe the statistical methods used for reliability/agreement. | Methods 2.2, 2.4-2.7; Supplementary Methods S4, S7, S8 | Partial. Metrics, matching rules, sensitivity analyses and clustered bootstrap are described. Identify analysis software and versions; retain the disclosed gap in semantic-matching model/prompt provenance. |
| 11 | Report actual raters, subjects or objects and replicate observations. | Results 3.1, 3.3, 3.4; Figure 1; Tables S1, S7-S9 | Reported. Six reviewers, 150 RSv1 records/300 responses and 60 RSv2 records/120 responses are reported, with eligible subsets and 120 reassessments. |
| 12 | Describe sample characteristics and raters' training and experience. | Results 3.1, 3.3; Supplementary Methods S2c, S7 | Partial. Counts and analysability are reported. Add verified reviewer specialties, experience and HFACS training, plus relevant case-mix characteristics for the sampled records. |
| 13 | Report agreement/reliability estimates and statistical uncertainty. | Results 3.1, 3.3, 3.4; Tables 1-2, S1, S3, S7, S9-S10 | Reported. Main agreement estimates and bootstrap confidence intervals are provided. Factor-matching uncertainty is distinguished from conditional sampling uncertainty; some auxiliary results are point estimates. |
| 14 | Discuss the practical relevance of the findings. | Discussion not yet drafted | Pending. Explain implications for HFACS analysis and use of automated outputs, distinguishing agreement from correctness, established causation and clinical benefit. |
| 15 | Make detailed results available, including online material where feasible. | Supplementary Results S1-S11; Data and code availability; Supplementary Methods S9 | Partial. Detailed results are in separate supplementary tables. Finalise the sharing-repository URL, release identifier and data-access statement before submission. |

## Reference

Kottner J, et al. Guidelines for Reporting Reliability and Agreement Studies (GRRAS) were proposed. J Clin Epidemiol. 2011;64:96-106. https://doi.org/10.1016/j.jclinepi.2010.03.002. Checklist: Table 1, p. 98.
