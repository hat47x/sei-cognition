# PMS-06 — Current State Snapshot

更新日: 2026-09-05  
対象: PMS-06 Realization / Provider Exchange

## この文書の役割

この文書は、`SOZA_PRODUCT_MILESTONES.md`、`SOZA_REALIZATION_PROVIDER_EXCHANGE.md`、`SOZA_VALUE_TRACEABILITY.md`等のProduct基線が2026-09-03時点の状態を主に反映している一方、その後にISSUE-000072が追加されたため、**PMS-06の現在地だけを短く補完するsnapshot**です。

Product Value、Milestone Outcome、Requirement、Acceptance Scenario、Universal Contractを新しく定義しません。意味上の正本は既存Product / Requirement / Issue本文であり、このsnapshotは現在のEvidence位置を読み違えないための補助資料です。

## 現在のEvidence ladder

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b live external process / service integration
  → E4 Operational portability
```

現在までに、少なくとも次のScoped Executable Evidenceがあります。

- E2 out-of-process reference exchange
- E3a version-pinned external artifact integration
- E3b-P1 public live Provider integration
- E3b-P2 revision A fixed-artifact actual TEI CLI execution
- E3b-M1a fixed KJ Atlas + deterministic model stub
- E3b-M1b fixed KJ Atlas + actual inference model
- Method Realization historical revision / portable reconstruction
- actual model artifact交換後のhistorical Application保持

これらはv0.2.0 supported release scopeを遡及的に広げません。v0.2.0のsupported scopeはE3aまでです。

## Current Open explorations

2026-09-05時点で、PMS-06に直接関係する主要Open Issueは次の2本です。

### ISSUE-000070 — Ollama runtime version exchange

交換軸:

```text
same KJ Atlas source
same Method input
same model artifact
same prompt

Ollama 0.32.13
  ↕ runtime version only
Ollama 0.32.14
```

repository側では次まで整っています。

- fixed runtime archive metadata / digest
- fixed model artifact identity
- KJ Atlas fixed source identity
- prepositioned artifact preparation / verification
- side-effect-free preflight
- strict actual runner
- run-isolated Evidence preservation
- canonical Evidence + Provenance verifier
- partial / complete run progress observer
- repository-local focused regression surface

未検証:

```text
actual Ollama 0.32.13 / 0.32.14 archive bytes
actual binary versions
actual A/B /api/tags model identity
actual A/B inference
actual same-prompt runtime version exchange
```

したがってISSUE-000070はOpenです。

### ISSUE-000072 — TEI executable version exchange

revision Aについては、ISSUE-000065でfixed-artifact actual TEI CLI executionのScoped Executable Evidenceがあります。

revision Bは次へ固定しています。

`1a7028d444fcae60a1c4f2f2d247456f4c7c35be`

version交換の比較軸は、reference input driftを避けるため次へ固定しています。

```text
build / executable source
  = exact revision B

fixed reference input
  = exact revision A
```

repository側では次まで整っています。

- revision A historical Evidence再検証
- acquisition-independent TEI Evidence bundle verifier
- revision B execution-source Git identity verifier
- revision A fixed reference input identity verifier
- A/B Provider Plan source surface static comparison
- exact-B + exact-A fixed-input prepositioned E2 runner
- verified bundle → current SOZA Adapter E3 runner
- E2 / E3 separate Go toolchains
- canonical toolchain-split combined runner: `runtime/integration/run_tei_version_exchange_evidence.py`
- E2 / E3 stage-aware failure Evidence
- Requirement / Scenario pre-audit

単一PATHの`go`をE2からE3へ使い回す重複actual entrypointは削除し、combined executionは上記toolchain-split runnerへ一本化しています。

execution environment準備ではroot権限やsystem packageを必須にせず、Go公式Linux / amd64 archiveをuser-localへ配置する手順があります。

- E2 historical TEI build candidate: Go `1.23.2`
- E3 current SOZA live-test candidate: Go `1.25.0`

Go `1.25.0`はcurrent `runtime/go/go.mod`のGo 1.25条件を満たす再現可能なexecution candidateであり、Stable RequirementやUniversal Contractへ固定するものではありません。actual runでは使用した`go version`をEvidenceへ記録します。

```text
user-local toolchain archive verified
  != revision B build PASS
  != Provider Plan observed
  != Adapter live compatibility PASS
```

未検証:

```text
revision B actual CLI build / execution
revision B actual deployment-provider-plan
revision B current SOZA Adapter live compatibility
```

したがってISSUE-000072もOpenです。

## ISSUE-000071との関係

ISSUE-000071はResolvedですが、完了したのはCognitive Method成果品質の**評価境界の確立**です。

```text
evaluation boundary established
  != human review completed
  != KJ-method outcome quality satisfied
  != Product Value / Adoption outcome satisfied
```

human outcome reviewは後続Evidenceであり、PMS-06のruntime / Provider version exchange PASSから自動的に導出しません。

## Product-level interpretation

ISSUE-000070とISSUE-000072は、どちらも「versionを交換できたか」というだけの試験ではありません。

共通して確認するのは、実現層のversionやartifact取得方法が変わっても、次を混同しないことです。

```text
artifact acquisition path
  != artifact identity
  != logical Realization / Capability identity
  != historical Exact Binding / Provenance
  != canonical Decision / Observation meaning
```

一方、両Issueは同じ交換軸ではありません。

```text
ISSUE-000070
  = Cognitive Method側のinference runtime version exchange

ISSUE-000072
  = Capability Provider側のTEI executable / Provider Plan version exchange
```

片方のPASSをもう片方のEvidenceへ流用しません。

## Requirement boundary

現時点では新しいStable Requirement / Acceptance Scenario / Universal Contract fieldを追加しません。

ISSUE-000070ではactual A/B実行後にREQ-0001、REQ-0004、REQ-0021、SCN-0005、SCN-0015等へ戻ります。

ISSUE-000072ではactual B実行後にREQ-0001、REQ-0007、REQ-0021、SCN-0014、SCN-0018へ戻ります。Provider-neutral Observationの隣接境界としてREQ-0022も確認対象になり得ます。

```text
version exchange implementation exists
  != independent Product failure observed
  != new Stable Requirement needed
```

## Current execution constraint

2026-09-05 09時台JSTの最新確認では、actual large artifact取得・Linux execution候補として確認済みのRemote Desktop端末`HAT47X`はofflineです。

このため、ISSUE-000070 / 000072のactual executionはどちらも進めていません。

```text
execution environment unavailable
  != Ollama incompatibility
  != TEI incompatibility
  != SOZA Adapter failure
```

repository-side preparationが進んだこともactual PASSへ読み替えません。

## 次にEvidence強度が上がる条件

### ISSUE-000070

固定artifactを取得可能なLinux / amd64環境で標準handoffをactualに通し、canonical Evidence + Provenance verifierへ戻します。

### ISSUE-000072

exact revision B checkout、exact revision A fixed input checkout、TEI historical build用Go、current SOZA live-test用Goを用意し、canonical `run_tei_version_exchange_evidence.py`からE2 → E3をactualに通します。

どちらも途中停止した場合は、保存されたmachine-readable stage / milestoneまでをEvidenceとし、自然言語logから内部原因を推測してEvidence強度を上げません。

## Stop line

```text
PMS-06 repository-side execution path ready
  != ISSUE-000070 actual runtime exchange PASS
  != ISSUE-000072 actual TEI version exchange PASS
  != E4 Operational portability
  != v0.2.0 supported scope expanded
  != human outcome quality satisfied
  != Adoption / Outcome Evidence
```
