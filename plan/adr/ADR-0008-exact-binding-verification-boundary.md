# ADR-0008: Exact Bindingの検証方式をRepresentation Profileへ分離する

Status: **Accepted**  
Related Issues: **ISSUE-000009, ISSUE-000034**  
Updated: 2026-08-31

## Context

`ExactArtifactBinding`は、Method ApplicationやDecisionが「その時点で実際にどの内容を参照したか」を後から特定するための境界である。

しかし、`content_digest`という文字列があるだけでは、その値を元のpayloadから再計算できるとは限らない。逆に、JSON canonicalizationやhash algorithmをUniversal Coreへ固定すると、特定のrepresentation方式の都合が意味論へ逆流する。

## Decision

SOZA Coreが所有するのは、**Exact Bindingを再検証できるための意味上の条件**までとする。

canonicalization、digest algorithm、対象bytesまたはsemantic representationの定義は、明示された`Representation Profile`が所有する。

```text
LogicalArtifactRef
      ↓
ExactArtifactBinding
  content_digest
  representation_profile
      ↓
Representation Profile
  canonicalization / digest verification
```

したがって、次をUniversal Core規則にはしない。

- SHA-256を唯一のhash algorithmにすること
- JSONやJCSを唯一のrepresentationにすること
- Git object IDをsemantic identityにすること
- digest差だけからsemantic revisionを推定すること

unknownなRepresentation Profileは検証済みとして扱わない。また、representationだけが変わったことをSemantic Lineageへ自動変換しない。

## Current Profile baseline

current / future Exact Binding向けのProfile基線はADR-0023で定めている。

```text
sei.jcs+sha256/v1alpha1
sei.raw-bytes+sha256/v1alpha1
```

JSONではRFC 8785 JCSをcanonicalizationの外部仕様として用い、non-JSONや明示されたbinary contentではraw bytesを対象とするProfileを分けている。

これらはcurrent Profileの選択であり、CoreがJSON、JCS、SHA-256を唯一の方式として所有することを意味しない。

historical M47 digestの生成規則は現在も確認できていないため、current Profileへ推測で対応付けない。回収作業はISSUE-000034で独立して扱う。

## Consequences

- historical bindingがcurrentとは異なるdigest方式を持っていても、Profileを特定できれば適切なverifierを介して接続できる。
- portable exportでは、利用したRepresentation Profileを明示することでcontent integrityを再検証できる。
- Profileやverifierを特定できないhistorical bindingは参照できても、「再検証済み」とは主張しない。
- storage identityとcontent integrityを分離できる。

## Revisit conditions

複数の実際のinteroperability Scenarioで、Representation Profileを分離すること自体が意味の再構成を妨げると確認された場合に再検討する。

## Evidence state

current JCS + SHA-256 / raw-bytes + SHA-256 Profileについては、actual GitHub Actionsでfixture-scoped Executable Evidenceが成立している。

ただし、これはProduction Runtimeへの完全統合、Release Evidence、Operational Evidenceを意味しない。

historical M47 digest mappingはISSUE-000034でBlockedのままである。

## Natural Japanese review

current Semantic Reference Contract、ADR-0023、Representation Profile conformance Evidenceへ戻ってDecisionを照合した。その後、Exact Bindingの意味契約とcanonicalization / digest方式の分離を変えず、旧candidate段階の表現をcurrent基線へ更新し、自然な日本語となることを最重要視して全文を再ドラフトした。最後にEvidence強度を含めて意味監査を実施済みである。
