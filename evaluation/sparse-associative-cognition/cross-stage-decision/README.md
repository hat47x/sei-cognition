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

`decision_kind` は:

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

ただし:

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
