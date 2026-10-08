# Publication Scope (Proposed)

**Status:** private coauthor-review repository. No general-public access, open-source
licence or archived release has been created. Changing visibility is a separate action
that requires approval; this document does not authorise it.

## What Goes Where

| Destination | Scope | Purpose |
| --- | --- | --- |
| Proposed public repository | Readable manuscript supplements and draft GRRAS checklist; statistical/figure Python code, pinned environment, tests, Markdown development notes/reproduction guide, prompt templates and frozen settings, pseudonymised numeric/category units, saved aggregates and hashes | Read the supplements, recompute supported statistics and regenerate tables/figures |
| Journal submission | Final reviewed supplement files containing essential methods, classification definitions, sensitivity analyses, results tables S1-S11 and reporting checklist | Interpret the study without reading source code; meet submission requirements |
| Controlled research workspace, not the first public package | JCQHC narrative/metadata exports, extracted factor prose, quotations and text-based correspondence evidence, complete individual annotation exports, raw model responses and clinical few-shot examples | Source-level review and original-process audit |
| Never part of the public package | Reviewer names/contact details and source-ID mappings, internal coauthor comments and activity/session logs, credentials, third-party paper PDFs and original working-repository history | Protect people, access secrets and unrelated internal material |

Original public sources will be attributed. Their redistribution rights and the
disclosure risk of linked derived data must be reviewed before release. Material
withheld here is not automatically available on request; access arrangements require
a separate team decision. No blanket restriction on reuse of JCQHC public records is
asserted.

## Reproduction Boundary

The package uses saved classifications, semantic correspondences and traceability
flags. It supports statistical recomputation conditional on those saved decisions,
not independent validation of factor meaning or a complete AI-pipeline rerun.
FTA added-value tables use preserved aggregate outputs. The clinical few-shot messages
are not included, so the prompt templates are not the complete frozen prompt bundle.
See [reproduction commands](reproduction.md) and [unresolved provenance](limitations.md).

## Before Public Release

1. Obtain coauthor agreement on this scope and check derived-data disclosure risk.
2. Confirm source attribution, redistribution terms, and separate code/data licences.
3. Rerun integrity, credential-pattern, statistical and table checks on the final package.
4. Freeze a tagged version and cite that version in the manuscript; use an archival
   identifier only after one has actually been issued.
5. Change access only after explicit approval and check anonymous reader access.

## 日本語要約

- **公開候補:** 論文サプリのMarkdown版、GRRAS対応表、コード、テンプレート、再計算手順、仮名化した数値・分類データ、集計、hash。数値・分類データも著者による確認対象とする。
- **GitHubにも収録する論文サプリ:** 方法・分類定義・感度分析・結果表S1〜S11・報告チェックリスト。共同編集用Docsは正本として保持し、投稿時は雑誌の形式に合わせる。
- **今回の公開版に含めない:** 原文・メタデータ全文、要因文・引用、個別回答全文、AI応答全文・臨床few-shot例。
- **非公開を維持:** 評価者情報・対応表、内部コメント・ログ、認証情報、元repoの履歴。
- 現在はPrivate。共同研究者の確認後に公開範囲・ライセンス・固定版を決める。
