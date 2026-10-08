# Manuscript-to-Code Map

The manuscript remains a draft; section numbers and table numbering can change.

| Result | Code | Included reproduction |
| --- | --- | --- |
| RSv1 independent human agreement, sensitivity (S1/S3) | `02_reliability_analysis.py` | Category-only case/node inputs; full point estimates and bootstrap CIs |
| RSv1 frozen primary/secondary AI classification (S2) | Functions in `79_evaluate_frozen_final_50.py`; original secondary evaluator `83` | 306 saved label pairs per model, point estimates and bootstrap CIs |
| FTA structural rankings and scale-up gate (S4/S5) | Historical `06_fta_added_value.py`; table builder `121` | Table cells from saved aggregates; full tree recalculation needs controlled inputs |
| FTA versus direct report-level classification (S6) | Historical `09_compare_flat_vs_fta.py`; table builder `121` | Table cells from saved aggregates; no new model generation |
| RSv2 extraction sensitivity (S7) | `scripts/rebuild_rsv2_inputs.py`, original functions in `110`, companion `scripts/reproduce.py` | All 244 factor IDs/codes and 55 decisions rebuild 540 count rows; 9 conditions x 4 groups, point estimates and bootstrap CIs |
| RSv2 consensus (S8) | `110` definitions | 60 cases/110 categorical factors; missingness preserved |
| RSv2 additional-information reassessment (S9/S10) | Factor-level rebuilder, `110` functions and companion entrypoint | Before/after factor codes rebuild the 37 matched pairs; transitions, pair-specific weighted kappa and layer agreement |
| RSv2 conditional AI classification (S11) | `110` functions and companion entrypoint | Candidate hits, singleton kappa and case-cluster CIs |
| Supplementary exploratory quantities | `110` definitions | Graph counts/F1, saved quotation flags, difficulty subgroups and recorded-time summaries |
| Table presentation | `120`, `121`, `122` | All 11 table titles/cells compared with saved expected tables |
| Figures | `118_build_ijmi_figures.py` | Four figure files and population/margin checks |

Packaging changes only: `121` and `122` hash files available in this package instead of requiring
all controlled exports; `118` adds a cross-platform font fallback. Statistical algorithms
in `02`, `79` and `110` are byte-identical to the source versions listed in the provenance
manifest. The companion runner is new orchestration code, not a new analysis definition.

The r03 classification templates are distinct from the v6b original FTA-generation
workflow. `prompts/r03_templates.json` intentionally omits 24 clinical few-shot messages
and therefore is not the complete original bundle.
