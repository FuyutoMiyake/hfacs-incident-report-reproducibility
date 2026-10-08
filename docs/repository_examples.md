# Companion Repository Design References

Reviewed 8 October 2026. These examples informed organisation only; their code, data,
licences and text have not been imported into this repository.

1. [CRAFT-MD repository](https://github.com/rajpurkarlab/craft-md), accompanying
   [An evaluation framework for clinical use of large language models in patient interaction tasks](https://www.nature.com/articles/s41591-024-03328-5).
   Its README links the paper, describes the task and separates source, data, results,
   environment information and reproduction entrypoints. We adopt this readable
   paper-to-code navigation pattern, not the original implementation or licence.
2. [MedHELM analysis repository](https://github.com/som-shahlab/medhelm), linked from
   the code-availability section of
   [Holistic evaluation of large language models for medical tasks with MedHELM](https://www.nature.com/articles/s41591-025-04151-2).
   It separates `data`, `plots`, `tables`, `scripts` and an execution environment,
   and provides explicit commands for regenerating figures and tables. This is the
   closest organisational model for our computational supplement. We also inspected
   the broader [MedHELM framework](https://github.com/PacificAI/medhelm), but do not
   adopt its dependencies or represent that fork as the paper's analysis repository.
3. [NHS ELM4PSIR](https://github.com/nhsx/ELM4PSIR) and its
   [NHS England project description](https://nhsengland.github.io/datascience/our_work/p33_patientsafetylms/).
   This is a domain-related repository/project report, not represented here as a
   peer-reviewed manuscript supplement. It illustrates incident-report NLP organised
   as inspectable computational material.

Our journal supplement retains essential methods/results tables. This repository holds
code, templates, computational inputs, hashes and execution instructions. A public
release or archival DOI is a separate decision; private creation does not constitute it.
