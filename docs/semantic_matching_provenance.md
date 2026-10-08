# Semantic Matching: Recovered Provenance

**Checked:** 8 October 2026. This records observable creation history, not a new
matching run or an independent validation of the saved decisions.

## What Was Recovered

The decision CSV used for the 60-record RSv2 analysis was created in a conversational
Codex session at 2026-10-01 07:32:10 UTC (16:32:10 Japan time). The recorded session
model was **`gpt-6.1-sol`**, with reasoning effort `high`, provider `openai`, and client
version `0.159.0`. The agent wrote the CSV through `apply_patch`; this was not a
separate batch matching API with one frozen request per record. This session model
must not be confused with the `GPT-5.6 Sol` classification arm.

The recovered creation patch is byte-identical to the preserved decision CSV:
SHA-256 `e5a787696b7b6440903036b8a94c4ab69914d7055b653633889d1fe136172457`.
Its 55 candidate relations comprise 39 `same`, 9 `partial`, 6 `causal_related`, and
1 `actor_diff` relations. These are candidate counts before factor eligibility is
applied; they are not the 37 eligible matches used for the main F1 estimate.

The AB/CD candidate keys (35 rows) are identical to those in the earlier candidate
table; their relation judgements were written into the recovered CSV. EF has 20
candidate rows. Recovery does not establish the model or prompt that originally
created the earlier AB/CD candidate table, or that all possible candidates were
searched in the same way across pairs.

## Recorded Task and Implemented Rules

The conversational task was to integrate the saved independent RSv2 responses,
consensus reference and reassessment data, then analyse human extraction agreement
and related outcomes. The analysis specification directed correspondence by factor
meaning rather than by HFACS label equality. This task description is a summary of
the record, **not a recovered standalone matching prompt**.

| Stored judgement | Implemented use |
| --- | --- |
| `same` | Central-proposition match in the main condition |
| `partial` | Additional match only in the partial-overlap sensitivity condition |
| `causal_related` or `actor_diff` | Not counted as an extraction match |
| Strict sensitivity | A `same` judgement plus at least one identical section/quotation pair |

The code checks one-to-one correspondence among the selected `same`/`partial`
relations within each record. Factor eligibility is applied separately, and both-empty
records have undefined F1. Bootstrap and sensitivity calculations reuse these saved
judgements; they do not rerun semantic matching.

## Remaining Limits

- No standalone frozen matching prompt or complete replayable request bundle was
  identified. A newly written prompt would be a new method, not the historical prompt.
- The session model identifier is recovered, but an immutable backend snapshot and
  generation parameters beyond the recorded session metadata are not established.
- The earlier AB/CD candidate-table creation provenance remains unresolved.
- Independent blinding and human verification of the correspondence are not established.
  The intended meaning-based rule is not evidence that HFACS labels were unavailable.
- Factor texts, quotations and the private conversation are not distributed here, so
  this package supports recomputation conditional on saved matches, not semantic replay.

The selected metadata and checksum checks are in
[`provenance/semantic_matching_audit.json`](../provenance/semantic_matching_audit.json).
Private source receipts remain in the controlled workspace. No clinical prose or full
session logs were added to this repository, and no saved match or analysis result changed.

## 日本語要約

要因対応表の作成時モデルは、記録上 `gpt-6.1-sol` と確認できました。
固定プロンプトを各症例へ送るAPIではなく、Codex上の会話に基づいてCSVを作成したものです。
作成内容は保存済みCSVと一致しますが、旧AB/CD候補表の来歴・単独の固定プロンプト・
盲検性・独立した人間確認まで回復したわけではありません。
