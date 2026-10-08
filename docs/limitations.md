# Interpretation and Pending Provenance

- Semantic matches were AI-assisted analyst decisions, not independently human-verified
  reference correspondence. The original matching model/prompt were not identified in
  the available records; no provenance is reconstructed or invented here.
- Matching sensitivity is material: under the main eligibility rule, strict quotation
  matching gives F1 about 0.148, central-proposition matching 0.420, and partial overlap
  0.511. Computational reproducibility does not make these choices equivalent or prove
  that every conclusion is unaffected by them.
- RSv1 and RSv2 use different cases and tasks. Their agreement estimates do not represent
  paired performance improvement. Different pairs also rated different case samples.
- Public-information reassessment was sequential and non-blinded. Additional factual
  fields, reporter judgements, rereading and prior consensus exposure were not separated.
- Reporter-assigned causes are judgements, not independent HFACS ground truth.
- Multiple reference labels may represent alternative interpretations or coexisting
  problems; these were not systematically distinguished. Candidate hits are permissive,
  not complete label-set accuracy.
- Missing resolution codes remain missing. Post-hoc LLM resolution/support strata are
  not human-adjudicated reasons, and saved quotation traceability is not full support.
- RSv2 AI testing supplied fixed human consensus factors for classification. End-to-end
  extraction and clinical effectiveness of layer-specific feedback were not evaluated.
- Recorded before/after times refer to different measurement procedures/tasks.

These qualifications belong in the manuscript and its essential supplement where
necessary. This code package neither fills missing observations nor changes the analysis
population in response to the desired bottom-line message.
