# PMS-06 — Current State Snapshot

更新日: 2026-09-05  
対象: PMS-06 Realization / Provider Exchange

## この文書の役割

この文書は、PMS-06の現在地を短く確認するためのsnapshotです。`SOZA_PRODUCT_MILESTONES.md`、`SOZA_REALIZATION_PROVIDER_EXCHANGE.md`、`SOZA_VALUE_TRACEABILITY.md`等のProduct基線を置き換えず、2026-09-05に進展したversion-exchange EvidenceとIssue状態を補完します。

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
- fixed model artifact下のOllama `0.32.13` / `0.32.14` runtime version交換後のhistorical Application保持

これらはv0.2.0 supported release scopeを遡及的に広げません。v0.2.0のsupported scopeはE3aまでです。

## Current exploration status

2026-09-05時点で、PMS-06のruntime / Provider version-exchange探索は次の状態です。

```text
ISSUE-000070
  = Resolved
  = fixed-scope Ollama runtime version exchangeのScoped Executable Evidence available

ISSUE-000072
  = Open
  = TEI executable / Provider Plan revision B actual execution pending
```

片方のEvidenceをもう片方へ流用しません。

## ISSUE-000070 — Ollama runtime version exchange

交換軸は次へ固定しました。

```text
same KJ Atlas source
same Method input
same model artifact
same prompt

Ollama 0.32.13
  ↕ runtime version only
Ollama 0.32.14
```

execution `local-20260904T193531Z-7855` のactual Evidenceを2026-09-05にcurrent developへ回収し、ISSUE-000070のResolution Criteriaへ再照合しました。

確認済み:

- fixed KJ Atlas runtime surface identity
- Ollama `0.32.13` / `0.32.14` actual archive bytes / SHA-256
- A / B actual binary version
- fixed `qwen2.5:0.5b` model full digest
- A / B actual `/api/tags` model identity
- same fixed Method input / same prompt digest
- A / B actual inference
- same logical Realization / different Exact Binding
- historical Application AのExact Reference / Provenance / output不変性
- portable historical reconstruction
- unknown revision / identity変更のnegative control
- Recommendation / Decisionへの自動昇格なし
- canonical Evidence + Provenance verification: `ready-to-review`
- verifier checks: `107 ok / 0 blocked`
- Requirement / Contract再照合: No Change

actual run commitとcurrent developのGit object identityも再監査し、ISSUE-000070 Resolution Criteria、core Evidence verifier、Provenance verifier、fixed artifact manifest、Product Requirements、Acceptance Scenarios、関連Semantic Contract baselineが同一objectであることを確認しました。

したがってISSUE-000070は**Resolved**です。

```text
ISSUE-000070 Resolved
  = fixed KJ Atlas + fixed model artifact下のOllama 0.32.13 / 0.32.14 version exchangeについてScoped Executable Evidence available
  != arbitrary runtime version portability
  != other runtime implementation portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```

成果品質は引き続き`qualityJudgement=not_evaluated`です。

## ISSUE-000072 — TEI executable version exchange

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
- canonical combined runner: `runtime/integration/run_tei_version_exchange_evidence.py`
- E2 / E3 stage-aware failure Evidence
- E3 Go requirement判定のstandalone runner側への集約
- combined runnerのGo path setup failureに対するmachine-readable toolchain stage
- Requirement / Scenario pre-audit

E2 historical TEI buildとE3 current SOZA live testは別toolchainを使います。Go versionや配置方法はexecution EvidenceでありStable Requirement / Universal Contractではありません。

未検証:

```text
revision B actual CLI build / execution
revision B actual deployment-provider-plan
revision B current SOZA Adapter live compatibility
```

したがってISSUE-000072は**Open**です。

## ISSUE-000071との関係

ISSUE-000071はResolvedですが、完了したのはCognitive Method成果品質の**評価境界の確立**です。

```text
evaluation boundary established
  != human review completed
  != KJ-method outcome quality satisfied
  != Product Value / Adoption outcome satisfied
```

ISSUE-000070のactual runtime exchange PASSも成果品質を満たしたことを意味しません。human outcome reviewは後続Evidenceです。

## Product-level interpretation

version exchangeでは、実現層のversionやartifact取得方法が変わっても、次を混同しないことを確認します。

```text
artifact acquisition path
  != artifact identity
  != logical Realization / Capability identity
  != historical Exact Binding / Provenance
  != canonical Decision / Observation meaning
```

ISSUE-000070とISSUE-000072は交換軸が異なります。

```text
ISSUE-000070
  = Cognitive Method側のinference runtime version exchange
  = fixed scopeでResolved

ISSUE-000072
  = Capability Provider側のTEI executable / Provider Plan version exchange
  = actual revision BがOpen
```

## Requirement boundary

ISSUE-000070ではREQ-0001、REQ-0004、REQ-0021、SCN-0005、SCN-0015へ再照合し、既存Requirement / Contractで表現可能と判断しました。新しいStable Requirement / Acceptance Scenario / Universal Contract fieldは追加していません。

ISSUE-000072ではactual B実行後にREQ-0001、REQ-0007、REQ-0021、SCN-0014、SCN-0018へ戻ります。Provider-neutral Observationの隣接境界としてREQ-0022も確認対象になり得ます。

```text
version exchange implementation exists
  != independent Product failure observed
  != new Stable Requirement needed
```

## Current execution constraint

2026-09-05の最新確認では、TEI revision B actual execution候補として確認済みのRemote Desktop端末`HAT47X`はofflineです。

このためISSUE-000072のactual E2 → E3はまだ進めていません。

```text
execution environment unavailable
  != TEI incompatibility
  != SOZA Adapter failure
```

ISSUE-000070は保存済みactual Evidenceとcurrent-contract object-equivalence監査により既にResolvedしており、HAT47Xの再接続をResolution条件にはしません。

## 次にEvidence強度が上がる条件

現在のPMS-06で次にEvidence強度が上がる主対象はISSUE-000072です。

exact revision B checkout、exact revision A fixed input checkout、TEI historical build用Go、current SOZA live-test用Goを用意し、canonical `run_tei_version_exchange_evidence.py`からE2 → E3をactualに通します。

途中停止した場合は、保存されたmachine-readable stageまでをEvidenceとし、自然言語logから内部原因を推測してEvidence強度を上げません。

ISSUE-000070について再実行が必要になるのは、Reopen conditionに該当するEvidenceやContract driftが観測された場合です。Resolvedであることを理由に任意runtime portabilityや成果品質へ主張を広げません。

## Stop line

```text
ISSUE-000070 fixed-scope runtime exchange Resolved
  != arbitrary runtime portability
  != outcome quality satisfied

ISSUE-000072 repository-side execution path ready
  != revision B actual TEI version exchange PASS
  != E4 Operational portability
  != v0.2.0 supported scope expanded
  != Adoption / Outcome Evidence
```
