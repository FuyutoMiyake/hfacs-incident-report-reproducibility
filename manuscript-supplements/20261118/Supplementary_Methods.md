# Supplementary Methods

Toward systems-level analysis of medical incident reports: A clinician-annotated evaluation of large language models using HFACS

This supplement provides the coding definitions, reviewer preparation, sampling and analysis procedures supporting the main manuscript. Sections S1-S3 support main Methods 2.1-2.3; S4-S5 detail RSv1 analyses, S6 details FTA analyses, S7 and S7a detail RSv2 analyses, and S8 details reassessment. Supplementary Results contains Tables S1-S11 and additional estimates.

## Abbreviations

AI, artificial intelligence; AC1, Gwet's agreement coefficient 1; CI, confidence interval; FTA, fault tree analysis; HFACS, Human Factors Analysis and Classification System; JCQHC, Japan Council for Quality Health Care; LLM, large language model; RS, reference standard.

### Table SM2. LLM roles and generation settings

| Stage, model and route | Execution date and prompt | Inputs | Generation settings and record status |
| --- | --- | --- | --- |
| Initial FTA candidates<br>Kimi K2.5<br>ID: kimi-k2.5<br>Kimi Coding API | Run date not recovered<br>v6b two-stage workflow | Event description, background, and improvement measures | Temperature 0.1; thinking disabled; maximum output 4,000 tokens per call. Settings recovered from the historical runner; returned model ID not retained. |
| Regenerated FTA<br>Kimi K2.5<br>ID: kimi-k2.5<br>Kimi Coding API | 14 July 2026<br>Three-stage workflow derived from v6b | Event description and background; improvement measures excluded | Temperature 0.6; thinking disabled; output limits 4,000 / 4,000 / 10,000 tokens for stages 1 / 2 / 3. |
| Direct multi-label baseline<br>Kimi K2.5<br>ID: kimi-k2.5<br>Kimi Coding API | 14 July 2026<br>Direct report-level classification prompt | Event description and background; improvement measures excluded | Temperature 0.6; thinking disabled; maximum output 3,000 tokens. |
| RSv1 final classification<br>GPT-5.6 Sol, primary<br>ID: openai/gpt-5.6-sol<br>OpenRouter, OpenAI provider | Run date not recovered<br>r03; configuration frozen 22 July 2026 | FTA leaf-node candidates and the three narrative fields | Temperature not explicitly specified; reasoning effort none; maximum output 8,192 tokens. Requested and returned model IDs agreed in all 37 saved responses. |
| RSv1 final classification<br>Kimi K2.6, secondary<br>ID: kimi-k2.6<br>Kimi Coding API | Run date not recovered<br>Unchanged r03 prompt | FTA leaf-node candidates and the three narrative fields | Temperature 0.6; thinking disabled; maximum output 2,048 tokens. Requested and returned model IDs agreed in all 37 saved responses. |
| RSv2 fixed-factor classification<br>GPT-5.6 Sol<br>ID: openai/gpt-5.6-sol<br>OpenRouter | 1 October 2026<br>Frozen RSv1 r03 classification configuration | Human-adjudicated factor texts and the three narrative fields; reference labels withheld | Temperature omitted from saved requests; reasoning effort none; maximum output 8,192 tokens. |
| RSv2 exploratory post-hoc judgements<br>GPT-5.6 Sol<br>ID: openai/gpt-5.6-sol<br>OpenRouter | 1 October 2026<br>Separate post-hoc resolution and support prompt | Human-adjudicated factors, quotations, and narratives; not the r03 classification task | Temperature omitted from saved requests; reasoning effort none; maximum output 8,192 tokens. |
| Preparation of semantic matching decisions<br>GPT-6.1 Sol<br>ID: gpt-6.1-sol<br>Codex conversational session | 1 October 2026<br>Conversational assistance; no standalone frozen prompt recovered | Reviewer factor propositions and candidate correspondences; see S7 for provenance limits | Reasoning effort high; Codex client 0.159.0. Temperature and output limit not recovered. No immutable model snapshot recorded. |

Dates are calendar dates in UTC where recoverable from run manifests or timestamped response files. A configuration-freeze date is not an execution date. Not explicitly specified means the temperature field was omitted from the request; not recovered means the historical value or date could not be established. Model IDs are recorded identifiers, not independently verified immutable backend snapshots. Kimi Coding API denotes api.kimi.com/coding/v1/chat/completions.

## Supplementary Methods S1 Data source and version control

The sampling frame comprised 61,606 public JCQHC records released during 2010-2024. Initial reviewer and model inputs were the event description, background and improvement-measures fields. These public narratives were not complete original hospital investigation reports. We did not infer an absence of information in the original hospital record from its absence in these inputs.

Analyses used saved source copies and versioned responses rather than reading changing spreadsheets during calculation. For RSv1, the canonical dataset combined saved pair adjudications, independent responses and focused L1 reassessments. For RSv2, the saved 60-record consensus dataset was locked for analysis; the database draft status and analytical approval status were retained separately. Original responses, excluded categories, missing values and earlier versions were preserved.

## Supplementary Methods S2 RSv1 annotation and analysis population

After excluding the 100 records used for prompt development with seed 671, 150 records were sampled without replacement using seed 150. Three reviewer pairs each reviewed 50 records. The initial Kimi K2.5 workflow generated FTA nodes and suggested classifications. A node represented an event or candidate contributing factor; the top node represented the incident, and a leaf was a node with no children. Intermediate nodes linked more detailed contributors to the incident.

The generated parent-child links represented inferred relationships among events and contributing factors. AND gates required all child events, whereas OR gates required at least one child event. These links and gates were inferred from narratives and were not treated as established causation.

### S2a Exploratory generation-prompt development

We compared three two-stage prompt variants on the same 10 previously selected development records. This was an exploratory, non-random comparison, not an independent validation study. All variants first generated the FTA structure and then assigned HFACS categories. The comparison addressed inclusion of improvement measures and an explicit prohibition on inference beyond the reported facts.

We adopted v6b to retain the complete three-field narrative input while explicitly restricting unsupported inference. This was a development choice, not evidence that v6b had superior accuracy; the comparison lacked an independent reference standard. The 10 comparison records were included in the seed-671 development sample and excluded from the 150-record RSv1 cohort. For the later FTA added-value analysis, trees were separately regenerated without improvement measures (Supplementary Methods S6).

### S2b Adopted generation workflow

The adopted two-stage v6b workflow used Kimi K2.5 with temperature 0.1, a 4,000-token output limit, and thinking disabled. Available prompts, configurations and exploratory comparison materials are retained in the versioned reproducibility materials described in S9.

### S2c Reviewer preparation and independent annotation

The six reviewers were five physicians and one nurse, with a median of 8 years of clinical experience (range, 2-15 years). None had used HFACS before the study. Common written instructions were provided, and a calibration meeting on 5 May 2026 addressed analysability, non-HFACS categories and HFACS coding boundaries. The same three reviewer pairs (AB, CD and EF) worked across RSv1, RSv2 and reassessment. Each reviewer assessed the assigned records independently before pair consensus.

For inter-reviewer agreement, each reviewer's independent response was compared with the paired reviewer's response; neither response was treated as a reference standard. Pair consensus subsequently produced RSv1 or RSv2, which were used as reference standards for the corresponding AI-classification evaluations.

Reviewers independently assessed the source narratives and generated candidates before pair adjudication. A retained node was one the reviewer did not delete from the assessment; retention did not imply that the reviewer accepted its initial AI classification. Retention and classification were separate decisions, and a retained node could be classified as INAPPROPRIATE.

The primary human classification analysis included each pair's records 11-50, only records both reviewers judged analysable, and only original leaf nodes both retained. The first 10 records coincided with calibration and procedural refinement and were excluded from this primary estimate, not removed from the dataset. Primary classification labels incorporated focused L1 reassessment.

L1 reassessment revisited labels assigned to individual unsafe acts using clarified coding guidance to reconsider whether the text supported an individual, supervisory or organisational contributor. It was a revision of reference construction, not an independent proof of more accurate labels. Historical rules could favour higher HFACS layers when individual responsibility was unclear. Both original and revised classifications were therefore retained. In RSv2, unclear actor or organisational scope was not itself sufficient evidence for L3 or L4.

These analyses estimated classification agreement conditional on both reviewers retaining a candidate in a jointly analysable record. They did not measure independent factor extraction or unconditional performance across all public records.

## Supplementary Methods S3 HFACS categories and aggregation

We used the four-layer healthcare adaptation of HFACS [1,2]. The category codes and names used in the project are listed in Table SM1. L1-L4 denote levels of analysis, not increasing severity. Detailed RSv1 human agreement used 19 HFACS categories plus three separate non-HFACS categories: patient condition (CoP); OTHER, for other content outside HFACS, including appropriate medical responses; and INAPPROPRIATE, for unsuitable FTA candidates, including outcome descriptions, top events or duplicate nodes. INAPPROPRIATE was not a new HFACS factor category.

Sensitivity analyses combined the three non-HFACS categories into one, yielding 20 detailed categories. Layer analyses used L1-L4 and the specified non-HFACS grouping. Binary analyses distinguished HFACS from non-HFACS. These aggregations changed the classification task; their coefficients were not interchangeable. For frozen final AI-to-RSv1 agreement, CoP, OTHER and INAPPROPRIATE were collapsed on both prediction and reference sides at scoring, yielding 19 HFACS categories plus one non-HFACS category, unlike the 22-category primary human analysis.

Inadequate supervision (SI_IS) concerned guidance, training, oversight or leadership of staff. Patient observation alone was not sufficient evidence for that category. Planned inappropriate operations (SI_IO) concerned supported local planning or management problems. Organisation-wide resources or procedures supported OI_RM or OI_OP, respectively; a job title or department name alone did not establish the responsible layer.

## Supplementary Methods S4 RSv1 sensitivity analyses and uncertainty

We calculated percentage agreement, nominal Cohen's kappa and Gwet's AC1. Report-level bootstrap resampling preserved dependence among nodes within each record. Initial RSv1 reliability calculations used 10,000 resamples; the implementation stored metric-specific deterministic seeds derived from base seed 1500714. The final reported analyses used 10,000 resamples throughout, following Hesterberg [3] as a routine-use recommendation. Additional pooled RSv1 inter-reviewer estimates resampled records within each reviewer pair, preserving 24 AB, 29 CD and 28 EF records; each record retained all jointly classified leaves. The three granularity-specific deterministic seeds were 20261014, 20261015, and 20261016. Supplementary Results S1 retains the original pair-specific estimates.

We examined four alternatives to the primary analysis: including records 1-50; including all original non-top nodes rather than leaves alone; using labels recorded before L1 reassessment; and combining CoP, OTHER and INAPPROPRIATE into one category. Each alternative retained the requirement that both reviewers judged a record analysable and retained the candidate node. Changing one dimension did not imply removing all other eligibility restrictions. Supplementary Results Table S3 reports the estimates for these conditions.

These comparisons describe sensitivity of the estimates to analysis choices. They do not establish that reassessment caused improvement or that any one grouping is objectively correct. We did not infer significance of between-condition differences from overlapping or non-overlapping confidence intervals alone.

## Supplementary Methods S5 Frozen RSv1 AI classification

The 150-record parent cohort was later divided into development, model/prompt selection and final evaluation sets of 50. The selected r03 prompt and GPT-5.6 Sol configuration were frozen before the final run. Earlier aggregate comparisons had used the parent cohort, so the final set was not an external validation cohort. Allocation to the model/prompt selection and final evaluation sets was stratified by reviewer pair and RSv1 analysability. The final 50 records included 10 records used during initial calibration and procedural refinement (records 1-10 within each pair), eight of which were included in the 37-record classification analysis.

The saved configuration requested openai/gpt-5.6-sol through OpenRouter with the OpenAI provider, strict JSON-schema output, a maximum of 8,192 output tokens and reasoning effort set to none. No temperature value was specified in this configuration. Prompt selection used detailed 20-category kappa, with accuracy as the tie-breaker. The unchanged prompt was later applied to Kimi K2.6 as a secondary evaluation; this did not replace the selected primary model. Final classification confidence intervals used 10,000 record-cluster bootstrap resamples within reviewer pair (AB 13, CD 12, EF 12 records), using seed 20260722 and retaining all leaves within each sampled record.

Models served different roles as new versions became available during the study: Kimi K2.5 generated initial and regenerated FTA candidates and direct multi-label predictions; GPT-5.6 Sol was the selected RSv1 classifier and the exploratory RSv2 classifier; and Kimi K2.6 was evaluated with the unchanged RSv1 prompt as a secondary model. Separately, a Codex session configured with GPT-6.1 Sol assisted preparation of semantic factor-matching decisions. Table SM2 records the settings and available execution provenance for each role.

## Supplementary Methods S6 FTA representation analyses

Improvement text was withheld from predictions when comparing them with improvement-related reference targets. Structural ranking assessed coverage of reported pathways using the generated tree, not expected reduction in clinical harm. Scale-up required a positive lower confidence bound for the difference in recall at five versus factor-frequency ranking, selection stability of at least 70 percent for every top-five category, a top five different from frequency ranking, and no detected improvement-input leakage. Both rankings used the same regenerated FTA outputs without improvement inputs. For each HFACS category, all leaves in that category were set to false and other leaves to true; AND/OR gates were then evaluated to determine whether the top event became false. The category score was the number of interrupted records plus the sum, across records, of the fraction of minimal cut sets containing that category divided by 1,000. Because the latter term was below one, it served as a tie-breaker; remaining ties were resolved by category code. Frequency rankings counted records containing the category, not individual leaf occurrences.

The structural and frequency rankings selected the same five categories and the scale-up gate failed. A subsequent direct multi-label comparison used Kimi K2.5 and event/background inputs without improvement text. This comparison was exploratory. Targets derived from the earlier assisted reference workflow were not fully independent of AI candidates. Relations and AND/OR gates were not validated causal effects or evidence of actual barrier failure. Record-level precision was intersection size divided by prediction-set size; with no predictions, it was zero for a non-empty reference and one when both sets were empty. Recall was intersection size divided by reference-set size and was one for an empty reference. These saved conventions were retained when averaging across records. Micro-F1 aggregated report-category counts rather than averaging record-level F1. Rankings were recomputed in each of 10,000 reviewer-pair-stratified record resamples (seed 1500716). Direct-classification comparisons used the same resampled records for both methods, with pair counts fixed within each analysis population. Metric-specific deterministic seeds based on 1500718 were retained in the executable analysis script.

## Supplementary Methods S7 RSv2 factor matching and consensus

Five new pilot records informed task and interface refinement and were excluded from formal estimates. Sixty new records were selected by deterministic seeded SHA-256 ranking with seed 20260812 after excluding previously used records and all pilot candidates, including reserve records, without manual difficulty screening; 20 different records were then allocated to each pair. Two reviewers independently extracted factors and quotations without an AI tree or their partner's responses. For independent analyses, preserved responses preceding documented RSv2 viewing were used where later updates were identified; the other saved responses were retained. Four responses from reviewer C (CD records 8, 12, 13 and 20) used their 16 August 2026 versions, preceding the recorded RSv2 case openings on 27 August. The versions saved after those openings each omitted one CoP-only factor and also changed recorded relationships and elapsed time. The reason for these edits was not established. All versions were preserved. The existing correspondence table was held fixed; restored CoP factors were not rematched. This selection yielded 248 independent factors, including 176 eligible factors and 37 matches under the main rule. Reassessment comparisons retained the 27 August versions actually presented to reviewers, with 244 existing factor-reviewer units; the four restored CoP factors had no reassessment and were not counted as transitions to empty labels. This audit identified these four updates, not the independence of every saved response.

Factors were matched one-to-one by their central proposition rather than identical wording. With M matched pairs and N1 and N2 eligible factors across records, micro-F1 was 2M/(N1 + N2). The main eligibility rule included factors with at least one HFACS or indeterminate label (classification could not be determined from the report) and excluded factors labelled only CoP, OTHER or INAPPROPRIATE. Sensitivity variants used all factors, HFACS-only factors, strict quotation matching and partial overlap. Both-empty records were reported separately; they were not assigned F1 of one.

Semantic correspondences were AI-assisted matching decisions and were not independently confirmed by human reviewers. Their bootstrap intervals described record-sampling variability conditional on the matching, not uncertainty from possible matching errors. Matching criteria were varied in sensitivity analyses.

The saved matching-decision CSV was prepared with conversational Codex assistance on 1 October 2026. The session recorded gpt-6.1-sol, reasoning effort high, and Codex client 0.159.0 (Table SM2). Decisions used the central meaning of factor propositions, rather than agreement in HFACS labels. The creation provenance of earlier AB/CD candidate tables and a standalone frozen matching prompt were not recovered; the session record does not establish that all candidate correspondences were generated with the same model and settings.

For matched factors, exact-set agreement required identical classification-label sets (including indeterminate) or HFACS layer sets. A shared-candidate measure required at least one common category and was more permissive. Nominal kappa used units with single labels on both sides. Multiple labels were not reduced to the first entry. The dataset did not systematically distinguish genuinely coexisting categories from alternative interpretations. Directed-relation micro-F1 compared the reviewers' directed links after factor matching and was exploratory. Additional 95% percentile intervals for detailed and layer kappa on matched factors and directed-relation micro-F1 used 10,000 record-cluster resamples stratified by pair (seed 20261107). All 60 records, including records contributing no eligible matched factors or relationships, remained in the resampling frame; eligibility and the saved correspondence table were held fixed.

Pairs adopted, merged or revised candidates to create 110 consensus factors. Separate actor-scope coding and adjudication of all relationships were not mandatory. Human-assigned resolution status was source-confirmed (determined from report text), rule-adjudicated (determined using an adjudication rule), or unresolved. Missing resolution codes remained missing and were reported separately. Quotation traceability meant that the quoted text could be located in the supplied narrative; this did not by itself establish complete semantic support.

## S7a Exploratory AI classification of RSv2 factors

Exploratory AI classification received all 110 consensus factor texts and the original three narrative fields, with reference labels, actor fields and resolution status withheld. It used GPT-5.6 Sol and the frozen RSv1 classification prompt. A candidate hit required the predicted category to match at least one reference label; hit rates were calculated for factors with any reference label and for those with at least one HFACS label. Detailed-category and layer-level kappa were restricted to the 75 factors with a single HFACS reference label. Non-HFACS predictions were retained as disagreements. RSv2 bootstrap intervals used 10,000 record resamples stratified within pair, with seed 20261001. Denominators and missing resolution status are reported separately in Supplementary Results Table S11.

## Supplementary Methods S8 Reassessment with additional public information

All six reviewers independently reassessed their 20 records using their saved responses and additional public information, including involved professions, location, circumstances and reporter-assigned contributing factors. Reporter-assigned factors were presented as judgements, not HFACS ground truth. Factor sets were held fixed, with exceptional proposed changes recorded as notes. No second consensus round was requested.

We assessed within-reviewer analysability transitions and pairwise classification agreement. The reassessment was not blinded, and effects of additional information, rereading, previous consensus exposure and reporter judgements could not be separated. A change in classification was not automatically an improvement in accuracy. Saved activity time excluded inactive intervals and was not total task time. For each of the 244 existing factor-reviewer units, we compared recorded label sets before and after reassessment; empty follow-up sets counted as changes. No baseline factor IDs were missing at follow-up. Changes among the 176 baseline HFACS-or-indeterminate factors were also summarised. Pooled analysability kappa used linear weights; single-layer kappa used the same 26 matched pairs classified to one layer by both reviewers at both stages, without ordinal weights. The 244-unit baseline was the version actually presented during reassessment, distinct from the 248-factor independent-analysis version described in S7. Additional intervals for nominal kappa on the fixed 26 single-layer pairs used identical before-and-after draws from the 60-record, pair-stratified frame (10,000 resamples; seed 20261107).

Linear weighted kappa was used only for ordered analysability responses. The pooled reassessment estimates used 10,000 pair-stratified record-cluster resamples with seeds 20261024 before and 20261025 after reassessment. These estimates pooled distinct pair-specific samples, not six responses to each common record.

### Table SM1 Project classification codes and labels

| Layer | Code | Label |
| --- | --- | --- |
| L1 | UA_DE | Decision error |
| L1 | UA_SE | Skill-based error |
| L1 | UA_PE | Perceptual error |
| L1 | UA_RV | Routine violation |
| L1 | UA_EV | Exceptional violation |
| L2 | PC_AM | Adverse mental state |
| L2 | PC_AP | Adverse physiological state |
| L2 | PC_PL | Physical or mental limitation |
| L2 | PC_TE | Technological environment |
| L2 | PC_PE | Physical environment |
| L2 | PC_CC | Communication and coordination |
| L2 | PC_PR | Personal readiness |
| L3 | SI_IS | Inadequate supervision |
| L3 | SI_IO | Planned inappropriate operations |
| L3 | SI_FK | Failure to correct a known problem |
| L3 | SI_SV | Supervisory violation |
| L4 | OI_RM | Resource management |
| L4 | OI_OC | Organisational climate |
| L4 | OI_OP | Organisational process |
| Outside | CoP | Condition of patient |
| Outside | OTHER | Other |
| Outside | INAPPROPRIATE | Inappropriate node |

Category definitions are operational labels within the HFACS healthcare adaptation, not ordinal severity levels. CoP, OTHER and INAPPROPRIATE are outside HFACS. Indeterminate status in RSv2 represents an unresolved classification rather than an additional HFACS layer.

## Supplementary Methods S9 Reproducibility and availability

Versioned analysis scripts, available prompts, configuration files, input and output hashes, and reproduction instructions are retained in the reproducibility repository cited in the main manuscript. The fixed revision corresponding to the reported recalculation is a1e27b59adcd02741c4efd026f48bf2c0be42d9a (https://github.com/FuyutoMiyake/hfacs-incident-report-reproducibility/tree/a1e27b59adcd02741c4efd026f48bf2c0be42d9a). The revision distinguishes the independent-response dataset from the baseline responses actually presented during reassessment.

AI-assisted semantic correspondences were not independently validated by human reviewers. The Codex session used to prepare the saved semantic matching decisions was identified (Table SM2 and S7), but a standalone frozen prompt and the creation provenance of earlier AB/CD candidate tables were not recovered. The original protocol, locked source responses and previous analysis results were preserved.

The additional pooled estimates and classification-change counts were computed using the bundled Python 3.12.14 and NumPy 2.3.5 runtime. Input snapshots, seeds, source hashes, record-level units, executable code and outputs are saved in the revision audit run. Earlier computations and original results were retained. The new calculations did not rerun AI inference or change semantic correspondences. The present review recalculation used Python 3.14.6, NumPy 2.4.4, pandas 3.0.1 and SciPy 1.17.1. RSv1 pooled human, final AI and FTA intervals were recalculated with reviewer-pair-stratified record resampling to preserve the observed composition of the fixed reviewer-pair samples. Independent RSv2 outputs used the response versions specified in S7; reassessment baselines, AI predictions and semantic correspondences were not changed. Previous outputs remain archived alongside the new inputs, hashes, seeds and executable scripts in analysis_npj/analysis_runs/review_revision_20261107.

## References

1. Wiegmann DA, Shappell SA. A Human Error Approach to Aviation Accident Analysis The Human Factors Analysis and Classification System. Routledge; 2017. https://doi.org/10.4324/9781315263878.

2. Diller T, Helmrich G, Dunning S, Cox S, Buchanan A, Shappell S. The Human Factors Analysis Classification System (HFACS) applied to health care. American Journal of Medical Quality. 2014;29:181-190. https://doi.org/10.1177/1062860613491623.

3. Hesterberg TC. What teachers should know about the bootstrap: resampling in the undergraduate statistics curriculum. Am Stat. 2015;69:371-386. https://doi.org/10.1080/00031305.2015.1089789.
