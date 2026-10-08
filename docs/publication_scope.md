# Publication Scope (Proposed)

**Status:** private coauthor-review repository. No general-public access, open-source
licence or archived release has been created. Changing visibility is a separate action
that requires approval; this document does not authorise it.

**Scope refreshed:** 8 October 2026. The remote repository was confirmed private.
All three supplement snapshots were checked against fresh reads of the collaborative
documents; their active Markdown text was unchanged. The 11 results tables and 433
cells still match the preserved expected tables. Internal author-review spreadsheets
and unconfirmed reviewer-selection drafts are not part of the release candidates.

## What Goes Where

| Destination | Scope | Purpose |
| --- | --- | --- |
| Proposed public repository | Readable manuscript supplements and draft GRRAS checklist; statistical/figure Python code, pinned environment, tests, Markdown reproduction guide, prompt templates/settings, pseudonymised numeric/category units, redacted individual RSv2 annotations and alignment decisions, quotation offsets/fingerprints, study-to-JCQHC links, aggregates/hashes and matching provenance | Read the supplements, retrieve attributed source records, recompute supported statistics and regenerate tables/figures |
| Journal submission | Final reviewed supplement files containing essential methods, classification definitions, sensitivity analyses, results tables S1-S11 and reporting checklist | Interpret the study without reading source code; meet submission requirements |
| Controlled research workspace, not the first public package | JCQHC narrative/metadata exports, extracted factor prose, quotations and text-based correspondence evidence, complete individual annotation exports, raw model responses and clinical few-shot examples | Source-level review and original-process audit |
| Never part of the public package | Reviewer names/contact details and reviewer-identity mappings, internal coauthor comments and activity/session logs, credentials, third-party paper PDFs and original working-repository history | Protect people, access secrets and unrelated internal material |

Original public sources will be attributed. Their redistribution rights and the
disclosure risk of linked derived data must be reviewed before release. Material
withheld here is not automatically available on request; access arrangements require
a separate team decision. No blanket restriction on reuse of JCQHC public records is
asserted.

The [data acquisition and restricted-access conditions](data_availability.md#obtaining-the-original-public-sources)
identify the official source service, historical file hashes, included study linkage
and the separate review required for any additional verification material. There is
no unconditional "available on request" commitment.

Issue #1 changes the private sharing boundary: 244 independent factors at each time point,
55 saved decisions, quotation offsets/fingerprints and 210 case links are now included.
All original case IDs and three narrative fields matched the frozen annual source files.
No clinical prose, quotation strings, names, notes or activity/session logs were added.
These additions are **public-release candidates**, not approved public disclosures.
Coauthors must approve linked annotations/decisions and assess re-identification risk
from source IDs and A-F reviewer codes before release. The repository remains private.

## Reproduction Boundary

The package uses saved classifications, semantic correspondences and traceability
flags. It supports statistical recomputation conditional on those saved decisions,
not independent validation of factor meaning or a complete AI-pipeline rerun.
The 540 count rows and the 37 matched classification pairs at both time points are now
rebuilt from factor IDs/codes and the saved decision table, with full snapshot checks.
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

更新日：2026年10月8日。**現在の共有用GitHubはPrivateで、一般公開はしていません。**
「公開候補」は将来の公開版へ収録する案であり、公開実行の承認とは区別します。

| 内容 | 現在の共有用GitHub | 今後の公開方針 |
| --- | --- | --- |
| Python解析・図表作成コード、検証テスト、実行環境 | 収録済み | 公開候補 |
| Markdownの研究の流れ・再計算手順・解析上の制約 | 収録済み | 公開候補 |
| プロンプトテンプレート・固定設定・開発比較の説明 | 収録済み | 公開候補。ただし臨床few-shot全文は除外 |
| 仮名化した数値・分類データ、保存済み集計、hash | 収録済み | 公開候補として了承済み。公開前に内容確認 |
| 要因対応の来歴（SOLモデル確認・保存CSV照合） | 収録済み。会話全文は除外 | 公開候補。確認済みの事実と再実行上の制約を記載 |
| RSv2全244要因のID・分類（追加前後）、対応判定55件、引用位置・hash | 必要項目のみ追加収録。要因文・引用文・内部メモは除外 | 公開候補。共著者了承と特定リスク確認後に判断 |
| RSv1・RSv2計210例とJCQHC事例ID・年次CSVの対応表 | 追加収録。元CSV15件・3欄本文を照合済み | 公開候補。評価者コードとの組合せも公開前確認 |
| 原データの取得方法・提供条件、公開元CSVのhash | 収録済み。原データ全文は除外 | 公開候補。無条件の提供を約束しない |
| Supplementary Methods / Results（S1〜S11） | Markdownで収録済み。最新Docsと照合済み | 公開候補。投稿時は確定版を別途添付 |
| GRRAS対応表15項目 | 暫定版を収録済み。最新Docsと照合済み | 記載済み5・一部7・未記載3。確認・更新後に公開候補 |
| JCQHC原文・メタデータ全文、要因文・引用 | 未収録 | 今回の公開版には含めない |
| 個別回答全文・AI応答全文・臨床few-shot | 未収録 | 管理された研究用環境のみで保持 |
| 評価者名・連絡先・評価者ID対応表・内部コメント／活動ログ・著者確認用GSS | 未収録 | 公開しない |
| 認証情報・第三者論文PDF・元リポジトリの内部Git履歴 | 未収録 | 公開版には含めない |

上の一覧はこの共有用リポジトリの収録範囲です。元の研究リポジトリの
公開範囲・権限は変更しません。数値・分類データも著者による確認対象とします。
共同編集用Docsは正本として保持し、GitHubのMarkdown版とは自動同期しません。
今回の最新取得ではサプリ3点の通常表示本文に変更はなく、結果11表・433セルと
GRRASの15項目・対応状況を保持しました。GSS上の内部質問や未確定の選定理由案は
論文サプリへ転記していません。

保存済み判定に基づく統計の再計算と、同じAI判定を最初からやり直すことは
区別します。専用の固定対応プロンプト等の未確認事項は
[要因対応の来歴](semantic_matching_provenance.md)に残します。
一般公開・ライセンス・投稿引用用の固定版は、共同研究者の確認後に別途決めます。
