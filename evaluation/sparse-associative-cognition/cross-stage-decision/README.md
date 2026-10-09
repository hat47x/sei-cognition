# Cross-stage Decision Record

状態: **Draft / B5 gate unchanged**  
更新日: 2026-09-19

## 1. 目的

このdirectoryは、cross-stage interpretationの後段で行うB5 review dispositionを、解釈そのものやB5 gate操作・production採用と混同せず記録するためのcontractを定義する。

current `decision.json` はdraft / not-assessed templateであり、実decisionは存在しない。

```text
result artifact
  ↓
interpretation artifact
  ↓
decision record
  ↓
future B5 review / product governance
```

## 2. このsliceが扱うdecision

`decision_kind` はは次のとおりです。

`b5-review-disposition`

に固定する。

decided artifactで許可するdisposition:

- `defer-for-evidence`
- `retain-current-stage`
- `request-b5-review`

`request-b5-review` はB5 gateをopenする操作ではない。

```text
request-b5-review != B5 gate open
```

## 3. Binding

decided artifactは:

- exact `interpretation_digest`
- interpretationのtrack / variant / capacity / stress identity
- decision authority stable ref
- exact Git commit SHA
- rationale refs
- interpretationで明示されたlimitations
- canonical decision digest

へbindする。

scope上のvariantはsource identityであり、winner選択を意味しない。

## 4. Limitation preservation

decisionはupstream interpretationのlimitationsを削除してはならない。

`limitations_acknowledged` はinterpreted artifactの `limitations` とexact一致させる。

これはdecision段で不都合な制約だけを落として結論を強くすることを防ぐためのprovenance boundaryである。

## 5. Non-authority flags

次は常にfalse:

```text
semantic_truth_claimed
variant_winner_selected
b5_gate_opened
production_default_changed
```

strict schemaのため `winner` や未登録decision fieldも拒否する。

## 6. B5 review request

decided artifactでは `b5_entry_condition_assessed=true` を要求する。

`b5_review_requested=true` はdispositionが `request-b5-review` の場合に限る。

ただしは次のとおりです。

```text
B5 review requested
  != B5 gate opened
  != B5 implementation authorized
  != production default changed
```

## 7. Draft state

checked-in `decision.json` は:

- state = draft
- disposition = not-assessed
- interpreted digest bindingなし
- authorityなし
- scope空
- rationaleなし
- acknowledged limitationなし
- B5 entry assessmentなし
- B5 review requestなし
- B5 gate openなし
- production changeなし

を維持する。

## 8. Validation

current draft:

```bash
python validate_decision.py
```

decided validationではinterpretation validatorを介して:

- preregistration
- frozen bundle
- authorized run
- completed result
- interpreted artifact
- full unlock

を再検証する。

## 9. 停止線

```text
decision record != semantic truth
decision scope variant != variant winner
request-b5-review != B5 gate open
decision record != production adoption
synthetic decided path != human-adjudicated benchmark decision
```

実human-adjudicated benchmark interpretationが存在するまで、checked-in `decision.json` をdecidedへ変更しない。


## 10. Evidence

machine-readable contract Evidence:

`decision_contract_evidence_2026-09-19.json`

GitHub source inspectionで次の回帰定義を確認した。

- decision: 27 tests
- preregistration: 38 tests
- research plan: 39 tests
- total: 104 tests defined

今回のcontract更新では実行環境からGitHub checkoutできなかったため、runtime test PASSは主張しない。

```text
defined tests != executed tests
decision contract != B5 gate open
decision contract != production adoption
```

## 11. Actual runtime verification

2026-09-19、GitHub正本22 source / manifestを一時環境へ再構成し、各fileの `git hash-object` がGitHub blob SHAと一致することを確認してからactual executionを行った。

Environment:

- Python 3.13.5
- Linux 6.18.44 x86_64 GNU/Linux
- GitHub Actions: 未使用
- full repository checkout: false
- execution model: exact Git-blob-validated temporary reconstruction

Actual result:

- decision validator: PASS / current decision remains draft-not-assessed
- interpretation validator: PASS / current interpretation remains draft-empty
- result validator: PASS / current result remains draft-empty
- run validator: PASS / current run remains draft-locked
- freeze validator: PASS / current bundle remains draft-locked
- preregistration validator: PASS / evaluation remains locked
- decision tests: **27 / 27 PASS**
- interpretation regression: **27 / 27 PASS**
- result regression: **24 / 24 PASS**
- run regression: **20 / 20 PASS**
- freeze regression: **18 / 18 PASS**
- preregistration regression: **38 / 38 PASS**
- total: **154 tests PASS / 0 failures**

machine-readable Evidence:

`decision_runtime_evidence_2026-09-19.json`

synthetic `retain-current-stage` / `defer-for-evidence` / `request-b5-review` の3 pathはactual upstream chainを通過した。特に `request-b5-review` はvalidでも `b5_gate_opened=false` のままである。

```text
runtime PASS != human-adjudicated benchmark decision
decision record != semantic truth
decision scope variant != variant winner
request-b5-review != B5 gate open
runtime Evidence != production adoption
```

checked-in `decision.json` は引き続きdraft / not-assessedであり、B5 gateとproduction defaultは変更していない。
