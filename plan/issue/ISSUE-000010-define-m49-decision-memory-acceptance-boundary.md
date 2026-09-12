# ISSUE-000010: historical M49 Decision Memoryの受入境界を定義する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0010**  
Updated: 2026-08-31

## Goal

historical M49で検討したDecision Memoryについて、Recommendation、Decision、Authority、Executionを混同しない受入境界を固定し、current Product / Contractへ継承すべき意味を明確にする。

M49は設計史上のMilestone labelであり、current実装フェーズの名称ではない。

## Resolution

次を受入境界として確定した。

```text
Recommendation != Decision != Authority != Action Intent != Execution
```

Decisionはcontext / basisを参照でき、Decision時点に残っていたUnknown / Conflict / Question等を未解決のまま保持できる。外在化されたrationaleを許す一方、private chain-of-thoughtの保存を要求しない。Decisionを担った主体等のResponsibilityはDecision自体のAuthorityと同一視せず、後続DecisionはSemantic Lineageで追跡できる。

RecommendationなしのDecision、Decisionへ至らないRecommendationも正常な状態として扱う。

この意味境界はADR-0010へ確定し、current `sei.decision-memory/v1alpha1`へ引き継いだ。

## Current evidence state

current repositoryでは、historical planning fixtureだけでなく次まで実体化されている。

- Decision Memory Contract Definition
- JSON Schema v1alpha1
- Recommendation without Decision fixture
- unresolved stateを残すDecision fixture
- semantic Contract conformance
- first semantic runtimeでのread / validate / reconstruct

したがってEvidence状態を次のように読む。

- Semantic / Design boundary: **Satisfied**
- Contract / fixture-scoped Executable Evidence: **Satisfied**
- first runtime read / validate / reconstruct Evidence: **Satisfied within current scope**
- durable production persistence: **Not Yet Verified**
- Authorization / Action execution crossing: **Not Yet Verified**
- Release / Operational Evidence: **Not Yet Verified**

```text
current Decision Memory fixture/runtime PASS
  != production decision service complete
  != Authorization implemented
  != Execution implemented
```

## Follow-up

参照役割はISSUE-000011 / ADR-0011、明示量はISSUE-000012 / ADR-0005へ分離した。

将来、Production PersistenceやAuthorization / Execution crossingを実装する場合も、current Decision Memory Contractから必要性を再導出し、historical M49 packageやfieldを自動継承しない。

## Natural Japanese review

historical M49 planning、ADR-0010、current Decision Memory Contract / Schema、Contract fixture、first runtime CIへ戻って内容を照合した。その後、設計史とcurrent正本、Executable Evidenceと未検証のProduction / Release / Operational範囲を分け、意味・条件・Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
