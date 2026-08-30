# ADR-0009: Exact BindingとVerification Outcomeを分離する

Status: **Accepted**  
Related Issue: **ISSUE-000009**  
Updated: 2026-08-31

## Context

Exact Bindingが検証可能であることと、**ある時点で実際に検証を実行し、どの結果になったか**は別の問題である。

`ExactArtifactBinding`自体へmutableな`verified` flagを持たせると、同じbindingが時点や環境によって書き換わり、内容参照のidentityと検証結果が混ざる。

また、verifierやpayloadが現在利用できない場合と、digest mismatchが確認された場合も分ける必要がある。

## Decision

`ExactArtifactBinding`は、logical reference、content digest、Representation Contract等の**検証対象を特定する情報**を持つ。

検証結果はbinding自体へ埋め込まず、別のoutcomeとして扱う。

少なくとも次を区別する。

- `verified` — 指定されたRepresentation Contractで検証に成功した。
- `failed` — digest mismatchやcontract違反等により検証に失敗した。
- `not_verified` — verifier、payload、必要なcontract等が現在利用できず、検証を実行・完了できていない。

```text
ExactArtifactBinding
  != Representation Contract implementation
  != Verification Outcome
```

`not_verified`を`failed`とみなさず、`failed`を「意味上誤っている」と自動解釈しない。Verificationはcontent binding integrityについての結果であり、ArtifactのTruthや妥当性そのものではない。

長期に検証結果を残す必要がある場合は、既存の`AssuranceRecord`等へ外在化する。現時点では新しいUniversal Verification Artifactを追加しない。

## Consequences

- bindingのidentityを不変に保ったまま、複数時点・複数verifierの結果を扱える。
- historical payloadが失われた場合をmismatchと誤認しにくい。
- content integrityの検証結果とsemantic truthを分離できる。
- Projectionはbindingと最新または関連するverification outcomeを組み立てる必要がある。

## Revisit conditions

AssuranceRecordでは検証履歴の意味を十分に保持できず、複数domainで独立したVerification Artifactが必要になる場合に再検討する。

## Natural Japanese review

Phase 1 hardeningとVerification Outcome設計へ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
