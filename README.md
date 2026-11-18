# HFACS Incident-Report Analysis

Computational companion for a clinician-annotated evaluation of large language models
using the Human Factors Analysis and Classification System (HFACS).

**Public since 18 November 2026.** This package reproduces statistics from saved
classifications and matching decisions, not AI generation or independent validation
of those decisions. [日本語の案内](README_ja.md)

## Start Here

| Purpose | Resource |
| --- | --- |
| Read the latest packaged supplements and GRRAS checklist | [18 November reading copies](manuscript-supplements/20261118/README.md) |
| Recompute the manuscript statistics | [Reproduction guide](docs/reproduction.md) |
| Locate inputs and code for a result | [Analysis map](docs/analysis_map.md) |
| Understand included and withheld information | [Data availability](docs/data_availability.md) and [publication scope](docs/publication_scope.md) |
| Understand what reproduction does not establish | [Interpretation limits](docs/limitations.md) |

## Reproduce the Statistics

Python 3.14 is recommended; verified dependency versions are in the reproduction guide.

```sh
git clone https://github.com/FuyutoMiyake/hfacs-incident-report-reproducibility.git
cd hfacs-incident-report-reproducibility
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/verify_integrity.py
.venv/bin/python scripts/reproduce.py --include-rsv1-human
```

No API keys or model calls are required. Current calculations use 10,000 bootstrap
replicates; numerical comparisons are written to `outputs/current/recomputation.json`.
The runner recomputes human and AI agreement, factor extraction, reassessment,
conditional AI classification, and FTA ranking/direct-classification comparisons.
FTA means fault tree analysis; RS means reference standard.

## Versions and Contents

- **Current calculations:** [7 November revision](revisions/20261107/README.md),
  fixed in commit [a1e27b59](https://github.com/FuyutoMiyake/hfacs-incident-report-reproducibility/tree/a1e27b59adcd02741c4efd026f48bf2c0be42d9a).
  Calculation inputs, statistical code and expected outputs have not changed in this documentation update.
- **Current reading copies:** [18 November supplement index](manuscript-supplements/20261118/README.md).
  These are dated exports of the latest local clean supplements, not live Google Docs.
- **Historical materials:** `data/`, `analysis_npj/` and `supplements/` retain
  October snapshots. Do not combine their older results with the current revision.

The current independent RSv2 extraction population contains **248 factors**
(primary micro-F1 0.420; all-factor micro-F1 0.315). The **244-factor reassessment
baseline** is a separate, intentionally retained population.

```text
revisions/20261107/          Current calculation inputs, code adapters and expected results
manuscript-supplements/     Dated current manuscript reading copies
docs/                      Methods, schemas, provenance and limitations
scripts/                   Offline reproduction and integrity checks
prompts/                   Templates and saved classification settings
provenance/                File hashes and verification records
analysis_npj/, data/        Retained historical code and data
supplements/               Retained October manuscript snapshots
tests/                     Focused integrity, provenance and metric tests
```

See also [prompt development](docs/prompt_development.md),
[original templates](docs/original_v6b_prompts.md), and
[semantic-matching provenance](docs/semantic_matching_provenance.md).

## Access, Citation and Licensing

The public package includes 210 study-to-JCQHC case links, quotation offsets/hashes
and persistent reviewer codes, but no reviewer-name mapping. These are pseudonymised
linked individual data, **not anonymous aggregate data**.

Source narratives, factor prose, quotations, full annotation/model-response exports,
clinical few-shot examples, reviewer identities/contacts, internal comments,
credentials and original working-repository history are not included.
Original sources must be obtained separately under applicable terms.
The templates are not the complete frozen prompt bundle.

Use the repository URL and exact calculation commit when citing this computational
version; [CITATION.cff](CITATION.cff) supplies repository metadata.
No archival DOI or open-source/data licence has been assigned. Public accessibility
does not grant an additional licence for third-party material or promise access to
withheld files. See [publication scope](docs/publication_scope.md).

## Funding

The API usage fees were supported by a Grant-in-Aid for Scientific Research (C) from
the Japan Society for the Promotion of Science (JSPS), grant number 25K13585.
