# ADR-0009: Exact BindingとVerification Outcomeを分離する

Status: **Accepted**  
Related Issues: **ISSUE-000009, ISSUE-000034**  
Updated: 2026-08-31

## Context

Exact Bindingを再検証できることと、**ある時点で実際に検証を行い、どの結果になったか**は別の問題である。

`ExactArtifactBinding`自体へmutableな`verified` flagを持たせると、同じbindingが時点や環境に応じて書き換わり、内容参照のidentityと検証結果が混ざってしまう。

また、verifierやpayloadを現在利用できない場合と、実際に検証してdigest mismatch等が確認された場合も区別する必要がある。

## Decision

`ExactArtifactBinding`は、logical reference、content digest、Representation Profile等の**検証対象を特定する情報**を持つ。

検証結果はbinding自体へ埋め込まず、別のVerification Outcomeとして扱う。

少なくとも、次の三状態を区別する。

- `verified` — 指定されたRepresentation Profileで検証に成功した。
- `failed` — digest mismatchやProfileに基づく検証失敗を確認した。
- `not_verified` — verifier、payload、必要なProfile等を利用できず、検証を完了できていない。

```text
ExactArtifactBinding
  != Representation Profile implementation
  != Verification Outcome
```

`not_verified`を`failed`とみなさず、`failed`を「意味上誤っている」と自動解釈しない。Verificationはcontent binding integrityについての結果であり、ArtifactのTruthや妥当性そのものではない。

## Current realization

current `soza.semantic-reference/v1alpha1`では、Verification OutcomeをExact Bindingとは別のrecordとして表現できる。

これにより、bindingのidentityを変えずに、検証結果を外在化できる。

Verification Outcomeは、AssuranceやTruth判定、Decisionそのものではない。将来、複数verifierの履歴や署名付きAssurance等をより豊かに扱う必要が生じた場合は、既存のAssurance境界との関係を別途設計する。

current fixtureでは、少なくとも次をExecutable Evidenceとして確認している。

```text
known Profile + digest match    → verified
known Profile + digest mismatch → failed
unknown Profile                 → not_verified
```

historical M47 digestについてはRepresentation Profileを確認できていないため、推測で`verified`や`failed`へ分類しない。ISSUE-000034で独立して扱う。

## Consequences

- bindingのidentityを不変に保ったまま、検証結果を別の記録として扱える。
- historical payloadやverifierが失われた場合をmismatchと誤認しにくい。
- content integrityの検証結果とsemantic truthを分離できる。
- Projectionでは、bindingと関連するVerification Outcomeを必要に応じて組み合わせて表示する必要がある。

## Revisit conditions

current Verification Outcomeでは複数verifier・時点・Assuranceの履歴を十分に表現できず、独立したより豊かなVerification / Assurance modelが複数domainで必要になった場合に再検討する。

## Natural Japanese review

current Semantic Reference Contract、Representation Profile conformance fixture、first semantic runtimeへ戻ってDecisionを照合した。その後、Exact BindingとVerification Outcomeの分離、`not_verified != failed`、content integrityとTruthの分離を変えず、旧Phase 1時点の説明をcurrent realizationへ更新した。最後に自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済みである。
