# ADR-0002: Universal Claim / Interpretationをv1 Coreへ追加しない

Status: **Accepted**  
Related Issue: **ISSUE-000002**  
Updated: 2026-08-31

## Context

SEIでは、原資料に書かれていること、観察されたこと、そこから導いた解釈や仮説、Method固有の統合物を区別して扱う必要がある。

しかし、それらをすべて包摂するUniversal `Claim` / `Interpretation`型を早い段階で導入すると、本来異なる認識状態を一つの抽象型へ戻し、かえって意味境界を弱めるおそれがある。

## Decision

v1 Coreには、Universal `Claim` / `Interpretation` Artifactを追加しない。

現時点では、次の組み合わせによって必要な意味差を表現する。

```text
Observation
+ Hypothesis
+ Method-specific Artifact
+ Derivation
+ EpistemicSeam
+ Provenance
+ EvidenceUse
```

### Sourceの記述を世界の事実へ自動昇格させない

Source Aが「Xが起きた」と述べている場合は、必要に応じて、

> Source Aが「Xが起きた」と報告している。

というObservationとして保持する。これは、「Xが起きた」という世界状態そのものを確定することとは別である。

### 解釈は後から検討できる形で外在化する

資料から導いた説明候補が、後から支持・反証・比較され得る場合はHypothesisとして扱う。

KJ synthesisやcultural-substrate-weavingの中間生成物のように、Method固有の意味を持つものはMethod固有Artifactとして保持し、Universal Interpretationへ変換することを要求しない。

### 複数の解釈を並存できるようにする

同じObservationから複数のHypothesisが生じても、latest-winsで一つへ潰さない。後続のEvidence、Conflict、Decision、Semantic Lineageによって、それぞれの扱いを明示する。

### Epistemic Seamを保持する

少なくとも、次の継ぎ目を一つの文やArtifactへ潰さない。

- Sourceの記載と紹介者の推論
- ObservationとInterpretation
- 確認済みの事実と推定された原因
- 文化体系の原典と、対象への対応候補

また、あるArtifactがEvidenceUseされたことも、そのArtifactが普遍的なTruthになったことを意味しない。

## Consequences

- 認識状態の違いを、具体的なArtifactとrelationとして保持できる。
- KJ等のMethod固有生成物を、無理に一つの共通型へ変換せずに済む。
- UIやqueryでは、複数種類のArtifactを組み合わせて扱う必要がある。

## Revisit conditions

複数のdomain / Methodで、ObservationでもHypothesisでもMethod固有Artifactでもない中立的な「表明された命題」を独立identityとして頻繁に扱う必要が生じ、既存の組み合わせではEvidenceUse、Assurance、Responsibility、revision等の意味が実際に失われる場合に再検討する。

その場合も、`Claim = Truth`とはしない。

## Natural Japanese review

current epistemic boundary、Architecture、Contractへ戻ってDecisionを照合した。その後、Universal Claimを追加しない判断、Source assertionとworld stateの差、複数Hypothesisの並存条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
