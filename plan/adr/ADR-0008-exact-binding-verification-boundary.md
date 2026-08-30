# ADR-0008: Exact Bindingの検証方式をRepresentation Contractへ分離する

Status: **Accepted**  
Related Issue: **ISSUE-000009**  
Updated: 2026-08-31

## Context

`ExactArtifactBinding`は、Method ApplicationやDecisionが「その時点で実際にどの内容を参照したか」を後から特定するための境界である。

しかし、`content_digest`という文字列があるだけでは、その値を元のpayloadから再計算できるとは限らない。逆に、JSON canonicalizationやhash algorithmをUniversal Coreへ固定すると、特定表現方式の都合が意味論へ逆流する。

## Decision

SOZA Coreが所有するのは、**Exact Bindingは独立に検証可能でなければならない**という意味契約までとする。

canonicalization、digest algorithm、対象bytesまたはsemantic representationの定義は、明示された`Representation Contract`が所有する。

```text
LogicalArtifactRef
      ↓
ExactArtifactBinding
  content_digest
  representation_contract
      ↓
Representation Contract
  canonicalization / digest verification
```

したがって、次をUniversal Core規則にはしない。

- SHA-256を唯一のhash algorithmにすること
- JSONやJCSを唯一のrepresentationにすること
- Git object IDをsemantic identityにすること
- digest差だけからsemantic revisionを推定すること

unknownなRepresentation Contractは検証済みとして扱わない。また、representationだけが変わったことをSemantic Lineageへ自動変換しない。

## Portable profile

JSON向けのstable候補としてRFC 8785 JCSを第一候補とする。custom `soza.canonical-json+sha256/v1alpha1`はcross-language pressure testの実験Profileとして保持する。

non-JSON / large binary向けにはraw bytesを対象とするProfileを別に持てる。これらはCoreの意味規則ではない。

## Consequences

- M47等が別digest方式を持っていてもadapterで接続できる。
- portable exportは表現契約を明示してintegrityを検証できる。
- Representation Contractが利用不能なhistorical bindingは参照できても、「再検証済み」とは主張できない。
- storage identityとcontent integrityを分離できる。

## Revisit conditions

複数のactual interoperability Scenarioで、Representation Contract分離そのものが意味の再構成を妨げることが示された場合に再検討する。

## Natural Japanese review

Exact Binding / canonicalization architecture baselineへ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
