# Interpretation and Pending Provenance

- Semantic matches were AI-assisted analyst decisions, not independently human-verified
  reference correspondence. On 8 October 2026, the decision-file creation was traced to
  a conversational Codex session recorded as `gpt-6.1-sol` (`high` reasoning effort).
  The creation patch matches the preserved CSV. No standalone frozen matching prompt
  was recovered, and the earlier AB/CD candidate-table creation remains unresolved.
  See [recovered matching provenance](semantic_matching_provenance.md); this recovery
  does not establish blinded matching or validate factor meaning.
- The current independent extraction dataset contains 248 redacted factors; the
  reassessment uses its separate, actually presented 244-factor baseline. The retained
  October package used 244 factors at both stages. There are 55 saved decisions,
  source linkage and quotation offsets. Counts and matched classification
  units can now be reconstructed rather than accepted only as aggregate inputs.
  The decision table remains AI-assisted and not independently human-verified;
  omitted candidate pairs were not adjudicated negatives. Without researcher-written
  factor prose, a reader cannot independently repeat semantic alignment under new criteria.
  Providing the saved decision table does not resolve the original prompt/context gaps.
- The 210 study-to-JCQHC links permit retrieval of exact public records using the annual
  source-file and field hashes. Offsets identify quotation passages after source retrieval,
  but neither offsets nor hashes establish full support. Publicly accessible reviewer
  codes, annotations and source IDs remain linked pseudonymised data; absence of a
  reviewer-name mapping does not establish anonymity.
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
