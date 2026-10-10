# Cross-stage Benchmark Preregistration

更新日: 2026-09-19  
状態: **Preregistration-only / Evaluation Locked**

## 1. 目的

B1/B2/B3/B4/B6/B6b/B6c/SEI-B7にはlimited synthetic executable evidenceがある。

ただし、個別synthetic fixtureで局所的な改善や失敗境界が見えたことは、実SUI/SEIデータで意味品質が改善することを示さない。

したがって次に必要なのは、新しい機構を増やすことではなく、**human-adjudicatedな実評価へ移る前に比較条件と停止線を固定すること**である。

```text
synthetic executable evidence
  ↓
cross-stage preregistration
  ↓
human adjudication freeze
  ↓
explicit evaluation-run artifact
  ↓
execution-attempt artifact
  ↓ success only
immutable result artifact
  ↓
non-decisional interpretation artifact
  ↓
B5 review disposition decision record
  ↓
future B5 review / product governance
```

この文書と `cross_stage_benchmark_preregistration.json` は、evaluation runそのものではない。

## 2. なぜcross-stage gateが必要か

現在のEvidenceには、単独段階では見えにくい相互作用がある。

- B1 normalizationはfeature massを補正する。
- B2 competitionはwinner budgetをfamily / global residualへ分配する。
- B3 bounded priorはB1/B2後にもrankingへ離散的な影響を与える。
- B6 capacity scalingは同じactive fractionでもselection pressureを変える。
- B6b/B6c diagnosticsはpath saturation / residual containmentを観測する。
- B4 familiarityはretrievalそのものではなく、event attention / escalationを変える。
- B7 route policyはSACS内部ではなく、Outcome後のupper control planeを変える。

したがって、各段階を個別に「改善」とみなして積み上げるのではなく、frozen variantとして横並びに比較する。

## 3. Retrieval track

human-adjudicated semantic retrievalで比較するvariantは事前に固定する。

1. B0
2. B1
3. B1 + B2
4. B1 + B2 + B3

B6 small / medium / large profileを同じvariant setへ適用する。

B6b / B6cはdiagnosticだけを出す。

```text
observed winner share
local incremental dimensions
residual containment
  != semantic quality score
```

### B6d / B6e stress track

作業中にB6d / B6eでstatic global-residual scalingの条件依存性が追加観測されたため、主評価profileへ混ぜず、oversized stress trackとして別に固定する。

- profile: 32768 dimensions / 512 active / fanout 8 / seed 47
- proportional baseline
- residual cap 128
- residual cap 64

これはrobustness比較であり、production default選定ではない。

またB6eでtext-heavyとstructure-heavyの挙動が異なったため、feature-family cardinalityをそのままsemantic importanceへ変換しない。

```text
feature cardinality
  may explain a failure mode
  != semantic priority
  != automatic routing/policy rule
```

## 4. B3 prior leakageを防ぐ

B3は特にevaluation label leakageへ弱い。

評価対象の正解を見てから「重要feature」を定義すると、priorの有効性ではなく答えの埋め込みを測ることになる。

したがってB3 priorは、

- provenance必須
- exact Channel + exact Key
- evaluation前にmanifest freeze
- evaluation labelsをauthoringに使わない

を必須にする。

## 5. B4は別trackにする

familiarity modulationはsemantic retrieval accuracyとは別の問題を扱う。

評価対象は次のとおりです。

- duplicate escalation reduction
- content delta recovery
- expiry recovery
- high-stakes recovery
- missed-change rate

fingerprintはcaller-ownedであり、evaluation labelを使って作ってはならない。

特に、

```text
unchanged caller fingerprint
  != unchanged underlying content
```

を維持する。

## 6. B7はOutcome train / holdout replayを分ける

Outcome-informed routingはtraining Outcomeとholdout replayを分離する。

- training Outcomeからcandidate policyを作る
- holdout replayはcandidateを作るために使わない
- holdoutはcounterfactually completeなsynthetic / curated replayに限定する
- static baselineとのregretを独立指標にする

実運用で未実行routeのcounterfactual outcomeが通常得られない問題は、別途selection-bias研究として残す。

## 7. 単一scoreを作らない

次を独立に扱う。

### Quality
- recall@k
- pairwise ordering accuracy
- false activation rate

### Robustness
- perturbation stability
- cross-profile ordering stability

### Resource
- p50 / p95 latency
- memory footprint
- allocation count

### Safety / failure
- B3 prior misapplication
- B4 missed change
- B7 regret against static
- minimum escalation floor preservation

### Diagnostics
- touched dimensions
- winner share
- local incremental dimensions
- residual containment

一つの加重scoreへ圧縮しない。

## 8. Freeze kit

preregistrationだけでは、human adjudication結果、dataset digest、split、B3 priorをどの形式で固定するかまでは扱わない。

そのため `cross-stage-freeze/` にfreeze kitを分離する。

- dataset manifest
- human adjudication manifest
- split manifest
- B3 prior manifest
- freeze bundle
- canonical SHA-256 validator

現在repoにあるmanifestはすべて `draft` であり、human-adjudicated datasetの代用品ではない。

freeze kitは、空dataset、mixed draft/frozen state、stale digest、split overlap、evaluation-label-derived prior、digest binding不一致をfail-closedにする。

human disagreementは `unresolved` として保存でき、強制的なconsensusへ潰さない。

freeze後もbundleは `result_generation_enabled=false`、`b5_entry_gate_changed=false` を維持する。

```text
preregistration
  ↓
draft freeze manifests
  ↓
human adjudication / split / prior preparation
  ↓
frozen freeze bundle
  ↓
explicit evaluation-run artifact
  ↓
execution-attempt artifact
  ↓ success only
result artifact
```

詳細は `cross-stage-freeze/README.md` を参照する。

## 9. Unlock条件

現在はlockedである。

evaluation runを作成する前に、別artifactで少なくとも次を満たす。

- human adjudication state = frozen
- dataset digest固定
- adjudication manifest固定
- variant set固定
- retrieval / familiarity / routing split固定
- B3 prior manifest固定
- explicit evaluation-run artifact作成

preregistration artifact自身の `result_generation.enabled` は将来も `false` のままにする。

## 10. Execution-attempt artifact

authorized runの実行試行は、run artifactやresult artifactへ直接書き込まず、`cross-stage-attempt/` の別artifactとして記録する。

completed attemptは、

- authorized runのexact digest
- executor identity
- observed environment
- started / completed time
- exit code / outcome
- runner-log / environment-capture
- successful attemptではraw-output

へbindする。

success / failureの双方を履歴として保存できるが、result生成へ進めるのはsuccessful attemptだけである。

```text
failed attempt
  != unavailable metric
  != zero metric
  != benchmark result
```

詳細は `cross-stage-attempt/README.md` を参照する。

## 11. Result artifact

successful execution attemptから得られる測定結果はrun artifactへ書き戻さず、`cross-stage-result/` の別artifactとして記録する。

completed resultは、

- authorized runのexact digest
- preregistration / frozen bundle
- run identity
- observed environment
- executor identity
- requested metric set
- raw-output / environment-capture digest

へbindする。

requested metricはexactly once記録し、測定不能は欠落や0ではなく `unavailable` と理由を明示する。

retrieval diagnosticは `diagnostic` のまま保持し、qualityへ昇格させない。

completed resultはcanonical SHA-256でself-bindするが、result artifact自身はwinner、B5判断、production defaultを所有しない。

```text
result artifact
  != benchmark interpretation
  != variant winner
  != B5 decision
  != production adoption
```

詳細は `cross-stage-result/README.md` を参照する。

## 12. Interpretation artifact

result artifactとdecision recordの間に、`cross-stage-interpretation/` の非決定的interpretation artifactを置く。

interpretationはcompleted resultのdigest、track / variant / capacity / stress identity、analyst provenance、参照metricへbindする。

ただし次は常にfalseのまま維持する。

```text
semantic_truth_claimed
variant_winner_declared
recommendation_generated
b5_decision_generated
production_default_changed
```

したがっては次のとおりです。

```text
result measurement
  != interpretation
  != decision
```

をartifact contractとして分離する。実human-adjudicated completed resultが存在するまでchecked-in interpretationはdraft / emptyである。

詳細は `cross-stage-interpretation/README.md` を参照する。

## 13. Decision record

interpreted artifactの後段には、`cross-stage-decision/` のB5 review disposition decision recordを置く。

許可するdispositionは:

- `defer-for-evidence`
- `retain-current-stage`
- `request-b5-review`

の3つだけである。

decision recordはexact interpretation digest、source scope identity、decision authority provenance、rationale refs、upstream limitationsへbindする。

`request-b5-review` はB5 gateをopenする操作ではない。

```text
decision record != semantic truth
decision scope variant != variant winner
request-b5-review != B5 gate open
decision record != production adoption
```

実human-adjudicated interpreted artifactが存在するまでchecked-in decisionはdraft / not-assessedである。

詳細は `cross-stage-decision/README.md` を参照する。

## 14. B5との関係

B5 learned sparse projectionのentry gateは変更しない。

B5を開けるには、少なくともfrozen human-adjudicated evaluationでB0-B3のmeaning quality不足を確認し、そのうえでstatic semantic adapterでも不足する必要がある。

decision recordの `request-b5-review` は、その条件をreview対象として提示するだけであり、gate stateを変更しない。

```text
cross-stage preregistration
  != B5 gate open
request-b5-review
  != B5 gate open
```

## 15. Evidence境界

この作業が提供するのはDesign / Evaluation-boundary Evidenceである。

現在repoのfreeze / run / attempt / result / interpretation / decision artifactはdraft / locked stateであり、human-adjudicated benchmarkは未実行である。

証明しないもの。

- 実SUI/SEI意味品質
- production runtime適性
- B3 priorの正しさ
- B4 fingerprint品質
- B7 routingの実運用有効性
- learned projectionの必要性
- variant winner
- B5 gate open
- production adoption
- Product Value / Operational / Adoption / Outcome Evidence
