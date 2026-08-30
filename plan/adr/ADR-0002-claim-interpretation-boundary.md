# ADR-0002: Universal Claim / Interpretationをv1 Coreへ追加しない

Status: **Accepted**  
Related Issue: **ISSUE-000002**  
Updated: 2026-08-31

## Context

SOZAでは、原資料の記述、観察、解釈、仮説、Method固有の統合物を区別する必要がある。

しかし、それらをすべて受けるUniversal `Claim` / `Interpretation`型を早期に導入すると、異なる認識状態を一つの抽象型へ戻し、かえって境界を弱める可能性がある。

## Decision

v1 CoreにはUniversal `Claim` / `Interpretation` Artifactを追加しない。

現時点では、次の組み合わせで必要な意味差を表す。

```text
Observation
+ Hypothesis
+ Method-specific Artifact
+ Derivation
+ EpistemicSeam
+ Provenance
+ EvidenceUse
```

### Source assertionを世界の事実へ自動昇格させない

Source Aが「Xが起きた」と述べている場合、必要に応じて、

> Source Aが「Xが起きた」と報告している。

というObservationとして保持する。これは「Xが起きた」という世界状態の確定とは別である。

### 解釈は検証可能な形で外在化する

資料から導いた説明候補が、後から支持・反証・比較され得る場合はHypothesisとして扱う。

KJ synthesisやcultural-substrate-weavingの中間生成物のようにMethod固有の意味を持つものは、Method固有Artifactとして保持し、Universal Interpretationへ変換することを要求しない。

### 複数解釈を並存できる

同じObservationから複数Hypothesisが生じても、latest-winsで一つへ潰さない。後続Evidence、Conflict、Decision、Semantic Lineageで扱いを明示する。

### Epistemic Seamを保持する

少なくとも、次の継ぎ目を一文へ潰さない。

- Sourceの記載と紹介者の推論
- ObservationとInterpretation
- 確認済み事実と推定原因
- 文化体系の原典と、対象との対応候補

EvidenceUseされたことも、そのArtifactが普遍的Truthになったことを意味しない。

## Consequences

- 認識状態の差を具体的なArtifactとrelationで保持できる。
- KJ等のMethod固有生成物を無理に共通型へ変換せずに済む。
- UIやqueryは複数種のArtifactを組み立てる必要がある。

## Revisit conditions

複数domain / Methodで、ObservationでもHypothesisでもMethod固有Artifactでもない中立的な「表明された命題」を独立identityとして頻繁に扱う必要が生じ、既存組み合わせではEvidenceUse、Assurance、Responsibility、revision等の意味が実際に失われる場合に再検討する。

その場合も`Claim = Truth`とはしない。

## Natural Japanese review

Architecture baselineへ戻して内容を照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
