# TEI Version Exchange — Requirement / Scenario Pre-audit

更新日: 2026-09-05  
対象: ISSUE-000072 / PMS-06

## この文書の役割

この文書は、ISSUE-000072のactual revision B実行後に行うRequirement / Acceptance Scenario再照合について、**actual結果を見る前の判定基準**を固定するためのpre-auditです。

actual revision Bの成功・失敗を先に知ったうえでRequirementの意味を後付けしないことを目的とします。

ISSUE-000072のResolution Criteria、Requirement本文、Scenario本文を置き換えません。actual BがまだNot Yet Verifiedであるため、この文書自体をExecutable EvidenceやRequirement changeの根拠へ昇格させません。

```text
pre-audit completed
  != revision B actual executable PASS
  != Provider Plan compatibility PASS
  != current SOZA Adapter compatibility PASS
  != Requirement change required
  != ISSUE-000072 Resolved
```

## 現在の比較軸

ISSUE-000072では、version交換以外の入力差をできるだけ除くため、比較軸を次へ固定しています。

```text
revision A
  source / executable = exact A
  reference input     = exact A

revision B
  source / executable = exact B
  reference input     = exact A
```

revision AとBでは`reference/workspace` treeが異なるため、B checkout内のreference inputを使うとexecutable revisionとinput interpretationの両方を交換してしまいます。したがってactual Bではhistorical Aのfixed reference inputを別checkoutから与えます。

この固定はTEI固有のUniversal Requirementではなく、一変数比較を成立させるためのExperiment / Evidence条件です。

actual E2 → E3のcanonical combined entrypointは`runtime/integration/run_tei_version_exchange_evidence.py`です。E2 historical build用GoとE3 current SOZA live-test用Goを別executableとして明示し、単一PATHの`go`を両段階へ使い回しません。

```text
canonical combined execution surface fixed
  != either toolchain installed
  != revision B build PASS
  != current Adapter compatibility PASS
```

## REQ-0001 — 耐久的な意味の連続性

current Requirementは、AIモデル、Prompt、Skill、実装言語、UI、Storage、Capability Provider、Execution Provider等が変わっても、Intent、Observation、Decision、Responsibility、Provenance等の耐久的意味を別の意味へ黙って読み替えずに引き継ぐことを要求しています。

### ISSUE-000072で見ること

TEI executableをrevision AからBへ交換しても、次を確認します。

- Capability identityをrevision A / Bのbinary identityと同一視しない。
- revision Aのhistorical source / binary / Provider Plan Evidenceをrevision B追加で書き換えない。
- revision BのProvider Plan bytesがAと異なっても、それだけをsemantic continuity failureとは扱わない。
- acquisition path、artifact identity、build source、fixed reference input、Provider surface、Capability Observationを別々に追跡できる。

### Requirement changeが不要と判断できる条件

actual Bがcurrent Adapterで扱える場合、または扱えなくてもfailureがTEI Provider surface / Adapter-local compatibilityへ局所化でき、Durable Semantic Coreの意味変更を必要としない場合は、REQ-0001の新規拡張は不要です。

### Requirement再検討を開始する反証

次のようなactual failureが確認された場合はCandidate Requirementを再検討します。

- historical Aを保持したままBを追加するために、Capability identityそのものをTEI revisionへ結び付けなければならない。
- acquisition / distribution方式をsemantic identityへ含めないとhistorical Observationを再構成できない。
- Provider-specific version差をUniversal Coreへ持ち込まないと過去の意味が黙って変わる。

単なるbuild failure、Provider Plan process failure、JSON surface差、Adapter-local field追加だけではこの反証にしません。

## REQ-0007 — Capability / Providerの中立性

current Requirementは、CapabilityとProviderを区別し、人間、AI、SaaS、外部組織、TEI、custom code等を同じIntentに対する異質な候補として扱えることを要求しています。Provider kindやSOZAとの近さからPriority / Trust / Authorityを自動付与してはなりません。

### ISSUE-000072で見ること

- TEI revision A / Bを、Capabilityそのもののrevisionへ自動変換しない。
- TEI executable revisionや取得方式からCapabilityのPriority / Trust / Authorityを推定しない。
- Provider Planのversion差をProvider-local compatibilityとして評価できる。
- revision BのProvider-specific fieldをcurrent Capability ObservationのUniversal fieldへ漏らさない。

### Requirement changeが不要と判断できる条件

current Adapter境界でrevision Bを受理できる、またはAdapter-local compatibility changeだけで対応可能なら、REQ-0007は現行の意味で十分です。

### Requirement再検討を開始する反証

- Provider revisionをCapability identityへ昇格しないと異Provider / 異revisionを区別できない。
- TEI固有version semanticsをUniversal Provider ontologyへ入れないとCapability選択の意味が保持できない。

これは「current AdapterがBをdecodeできなかった」だけでは成立しません。Provider-local DTOの更新で解消できるかを先に評価します。

## REQ-0021 — Realization / Executionを交換可能にする

current Requirementは、Cognitive Method Realization、Capability Provider、Execution Provider、Projection、Storage等の交換可能な実現層を変更・簡素化・削除しても、Durable Semantic Coreの意味を不必要に変更しない構造を維持することを要求しています。

### ISSUE-000072で見ること

revision A / Bの交換で、次を確認します。

- executable / Provider Plan revisionを交換してもcurrent Capability Observation境界へ戻れる。
- binary / output byte equalityを交換成立条件にしない。
- historical Aを残したままBを追加できる。
- build sourceとfixed reference inputを別Provenanceとして保持できる。
- distribution / credential方式をUniversal Contractへ昇格させない。

### Requirement changeが不要と判断できる条件

Bがcurrent AdapterでPASSする場合だけでなく、Bが不成立でもfailureがProvider / Adapter-local implementation boundaryへ閉じ、Durable Semantic Coreの変更を要求しない場合はREQ-0021の意味変更は不要です。

### Requirement再検討を開始する反証

- revision交換を表現するためにcurrent Durable Semantic Coreでは不可欠なhistorical execution identityを保持できない。
- Provider / Realization交換を行うたびにcanonical Decision / Capability / Observationの意味を書き換える必要がある。

## SCN-0014 — Execution Providerを交換する

current Scenarioは、同じIntent / Decisionに対する実行をworkflow engine A、AI agent runtime B、TEI等へ交換してもlogical meaningを維持し、Provider固有run IDをDecision identityの唯一の根拠にせず、Provider廃止後もhistorical Decisionを読めることを期待しています。

current Evidence欄ではExecution Provider交換はNot Yet Verifiedです。

### ISSUE-000072との関係

TEI executable revision A / B交換は、SCN-0014全体のExecution Provider交換を直接Satisfiedにする実験ではありません。今回の対象はCapability Provider側のTEI executable / Provider Plan compatibilityとCapability Observation mappingです。

したがってactual BがPASSしても、SCN-0014をSatisfiedへ昇格しません。

一方、次の観点はSCN-0014の将来検証設計に利用できます。

- Provider固有execution identityとDecision identityを分離する。
- provider executableが交換・廃止されてもhistorical semantic recordを再読できる。
- Provider runtime lifecycleをUniversal Coreへ取り込まない。

```text
TEI executable version exchange PASS
  != SCN-0014 Execution Provider exchange Satisfied
```

## SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

current Scenarioは、Provider / Projectionを交換してもcanonical meaningとhistorical basisを再読できること、Provider固有run IDをDecision canonical identityにしないこと、実行後Observationで過去Decision basisを上書きしないこと等を統合的に要求しています。

current Evidenceはfixture-scopedでPartially Satisfiedです。

### ISSUE-000072で見ること

- Provider revision B追加後もhistorical A Observation / provenanceを読み直せる。
- current Provider revisionへlatest-winsでhistorical basisを書き換えない。
- TEI固有のProvider Plan fieldがProduct Journeyのcanonical meaningを代替しない。
- revision Bのcompatibility結果をDecision correctnessやBusiness Outcomeへ昇格させない。

actual BがPASSしても、production Product Journey全体をSatisfiedへ昇格しません。今回のEvidenceはPMS-06 / Provider replacement boundaryを厚くする限定Evidenceです。

## Adjacent Requirement — REQ-0022

ISSUE-000072のResolution Criteriaには明示されていませんが、Provider-neutral Capability Observationという意味ではREQ-0022も密接に関係します。

current REQ-0022は、TEI等のProvider内部SchemaをUniversal Coreへコピーせず、Capability判断に必要な観測をProvider-neutralな意味境界から読むことを要求しています。

actual Bでは次を確認します。

- Provider Planのversion固有fieldがUniversal Capability Observationへ漏れない。
- mapping provenanceからB source / A fixed input / Provider-specific contextへ戻れる。
- Provider Plan差分をCapability identityの差へ自動変換しない。

ただし、ISSUE-000072のResolution Criteriaをこのpre-auditだけで増やしません。actual Bの結果で独立したProduct failureが見えた場合に、最終再照合へREQ-0022を正式追加するか判断します。

## actual結果ごとの判定表

| actual結果 | Requirement / Scenario上の一次解釈 | Stable Requirement change |
|---|---|---|
| E2 PASS + E3 PASS | exact-B executableをexact-A fixed inputでcurrent Adapterが扱えた限定Evidence | 原則No Change。既存REQ / SCNへEvidence追加を検討 |
| E2 FAIL before build / toolchain | execution environmentまたはbuild boundaryで未成立 | No Change。semantic incompatibilityを推定しない |
| E2 Provider Plan process FAIL | TEI process / input interpretation boundaryで不成立 | 原則No Change。machine-readable evidenceがない内部原因を推定しない |
| E2 PASS + E3 strict decode FAIL | Provider surface / Adapter-local DTO compatibilityを確認 | まずAdapter-local changeを検討。直ちにUniversal Requirement化しない |
| E2 PASS + E3 mapping / validator FAIL | Provider-specific outputからCapability Observationへの現行mapping不成立 | existing REQ-0007 / 0021 / 0022で表せるか監査 |
| acquisition pathのみ変更、artifact identity同一 | Provenance差 | No Change。Capability / semantic identity差へ昇格しない |
| binary / Provider Plan digestがAと異なる | revision差を観測 | No Change。byte driftだけでcompatibility failureにしない |
| historical A EvidenceをB追加で保持できない | V1 / V3 / V4に関わるProduct failure候補 | REQ-0001 / 0007 / 0021を再監査 |
| Universal CoreへTEI version-specific field追加が不可避 | Provider neutralityに関わるProduct failure候補 | Candidate Requirement / Contract changeを検討 |

## final audit時に記録するもの

actual B後の最終再照合では、少なくとも次を明示します。

1. E2 / E3のactual resultと停止stage。
2. revision A Evidenceが不変であること。
3. B source / A fixed input / binary / Provider Plan / SOZA source / toolchainのProvenance。
4. REQ-0001 / 0007 / 0021について `No Change | Evidence strengthened | Candidate Requirement needed` のいずれか。
5. SCN-0014 / 0018についてEvidence強度が変わるか。
6. adjacent REQ-0022を正式な再照合対象へ追加する必要があるか。
7. Stable Requirement / Universal Contractを変更する場合は、actual failureから独立した意味上の必要性が説明できるか。
8. Evidenceの高さをDesign / Executable / Release / Operational / Adoption・Outcomeで混同していないか。

## 現時点のpre-audit結論

actual revision Bをまだ実行していない現時点では、**新しいStable RequirementやUniversal Contract fieldを追加する根拠はありません**。

current REQ-0001 / REQ-0007 / REQ-0021、およびProvider-neutral Observationを扱うREQ-0022は、ISSUE-000072が検証しようとしている意味境界を既に表現しています。

次に必要なのはRequirementの先取りではなく、exact-B executable + exact-A fixed inputによるactual E2と、current SOZA Adapterによるactual E3です。

```text
current Requirement coverage appears sufficient at Design level
  != revision B compatibility proven
  != Requirement evidence strengthened
  != ISSUE-000072 Resolved
```
