# ISSUE-000067: Realization / model version交換後もhistorical Method Applicationを再構成できるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025**  
Product Milestone: **PMS-06**  
Updated: 2026-09-02

## Goal

E3b-M1bでactual model-backed Cognitive Method実行が成立した次の段階として、同じCognitive Methodを異なるmodel artifact / Realizationで実行したときに、先に記録したMethod Applicationの来歴を後続実行で書き換えず、当時の実行条件まで必要な範囲で再構成できるかを検証する。

今回の中心は、同じ出力を再現することではない。**どのMethodを、どのRealizationとmodel実行条件で適用したかを、後から区別して読み直せること**を確認する。

```text
same Method Definition
  + Realization A / model A
  → Method Application A

same Method Definition
  + Realization B / model B
  → Method Application B

Application B added
  != Application A rewritten
  != Application A provenance rebound to B
```

## Background

ISSUE-000064では、固定revisionのKJ Atlasとdeterministic model stubを使ったE3b-M1aを実証した。

ISSUE-000066では、同じKJ Atlas revision / Method surfaceをOllama `0.32.14`上の`qwen2.5:0.5b`へ接続し、actual inferenceからKJ Atlas response受理、SOZAの既存Cognitive Method Applicationへのmappingまでを実証した。

一方、current `livemethodintegration`には次の特徴がある。

- Method ApplicationはRealizationへのLogical Referenceを保持する。
- KJ Atlas live probeではM1a / M1bとも`MR-KJ-ATLAS-4F28C13`を使っている。
- opaque provenanceにはKJ Atlas repository / commit / entry point / result digestを保持する。
- Ollama version、model artifact identity、prompt digest、actual inference countersはM1bのCI Evidenceには残るが、current Method Applicationから辿るcanonical provenanceには含まれない。

したがって、**KJ Atlas sourceが同じままmodel / runtimeだけを交換したとき、historical reconstructionに必要な差をどの層へ残すべきか**はまだ実証されていない。

この不足を、現在のfield名をそのままUniversal Provenance Contractへ追加することで先に解決しない。まず実交換を行い、既存ContractのRealization Reference、provenance refs、Exact Bindingでどこまで十分かを検証する。

## Existing Requirementsとの関係

本Issueでは新しいStable Requirement / Scenarioを追加しない。

主に次の既存Requirementを実証対象とする。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0003 — 出所・発見経路・派生の分離
- REQ-0004 — Cognitive Methodの独立性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0009 — Revision / Supersessionの完全性
- REQ-0021 — Realization / Executionを交換可能にする

実証の結果、既存Requirementでは守れない耐久的な意味差が見つかった場合にのみCandidate Requirementを検討する。

## Probe design

### 1. Method surfaceは固定する

KJ AtlasはM1bと同じsourceを使う。

- Repository: `hat47x/kj-atlas`
- Commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Method surface: `POST /ai/suggest-card-groups`

Method Definition自体を交換した実験にはしない。

### 2. model artifactを実際に交換する

同じOllama runtime上で少なくとも二つのmodel artifactを実際に推論させる。

最初の候補は次とする。

- `qwen2.5:0.5b`
- `qwen2.5:1.5b`

model tagだけを信用せず、Ollamaが観測したmodel identity / digestもEvidenceへ残す。

### 3. 二つのApplicationを別のRealizationとして記録する

同じMethod Definitionを参照したまま、model artifactが異なる実行を別のprobe-local Realizationとして扱う。

RealizationのID命名規則やmodel field setをUniversal Contractへ固定しない。重要なのは、後続Realizationを追加しても旧ApplicationのRealization Referenceが変わらないことである。

### 4. execution provenanceをApplicationから辿れる形で残す

少なくとも今回のprobeでは、次を区別して保持する。

- Cognitive Method source repository / commit / entry point
- inference runtime name / version
- model tag
- observed model artifact identity
- prompt digest
- Method result digest

これらはprobe-local opaque provenanceとして扱い、今回だけを根拠にUniversal fieldへ昇格させない。

### 5. historical reconstructionを検査する

二つ目のApplicationを追加した後に、最初のApplicationについて次を再度検査する。

- Method Referenceが変わっていない。
- Realization Referenceが変わっていない。
- provenance refが変わっていない。
- provenance payloadのruntime / model identityが二つ目の実行条件へ置換されていない。
- output digestが二つ目のoutputへ置換されていない。

Exact Bindingがないと交換bundle上でこの不変条件を十分に守れないと分かった場合は、その事実を次の設計入力とする。最初からExact Binding必須とは決めない。

## Evidenceとして確認すること

- [ ] 固定revisionのKJ Atlasを同じMethod surfaceで二回実行する。
- [ ] 二つの異なるactual model artifactでprompt評価とtoken生成が発生する。
- [ ] 両方のKJ Atlas Method responseが既存parser / filteringを通る。
- [ ] 二つの実行を別Realization / ApplicationとしてSOZAへ記録する。
- [ ] 各Applicationから、それぞれのruntime / model / prompt / result provenanceを辿れる。
- [ ] 後続Application追加後も旧ApplicationのRealization / provenance / output来歴が変化しない。
- [ ] model固有情報をMethod DefinitionやUniversal Contractの必須fieldへ持ち込まない。
- [ ] grouping結果をRecommendation / Decisionへ自動昇格させない。
- [ ] 対象CIがsuccessする。

## Explicit stop lines

```text
model version exchange PASS
  != model quality satisfied
  != KJ-method outcome quality satisfied
  != arbitrary model portability
  != runtime portability
  != Operational portability
```

また、次を同一視しない。

```text
Method Definition
  != Method Realization
  != model artifact
  != inference runtime
  != Method Application
```

model tag、Ollamaのfield名、Git repository、HTTP endpoint等を、そのままSOZAのUniversal semantic identityにはしない。

## Completion condition

二つのactual model artifactを同じ固定KJ Atlas Method surfaceで実行し、それぞれのApplication / Realization / provenanceを区別したまま記録したうえで、後続実行後にも先行Applicationのhistorical basisが変化していないことをCIで確認できた時点でResolvedとする。

一方、二つ目のmodelが取得できただけ、processが起動しただけ、またはactual inference後にKJ Atlas responseが成立しなかった場合はResolvedにしない。

## Natural Japanese review

current Product Value、REQ-0001 / 0003 / 0004 / 0005 / 0009 / 0021、Cognitive Method Contract、Semantic Reference Contract、E3b-M1a / M1b Evidence、current `livemethodintegration`の実装、上流計画のversion交換・historical reconstruction節を照合した。

現在確認できている不足を「Universal Provenance fieldが足りない」と先に断定せず、実際のmodel交換で必要な意味差を観測してからContract / Requirementへ戻す構成としている。意味、規範強度、未検証範囲を変えず、自然な日本語として読めることを最重要視して全文を再ドラフトした。
