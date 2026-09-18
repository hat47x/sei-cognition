# Cross-stage Result Interpretation

状態: **Draft / Non-decisional**  
更新日: 2026-09-19

## 1. 目的

このdirectoryは、completed cross-stage resultに対する解釈を、測定結果そのものや後段の意思決定と混同せずに記録するためのcontractを定義する。

現在の `interpretation.json` は空のdraft templateである。

```text
preregistration
  ↓
frozen bundle
  ↓
authorized run
  ↓
result artifact
  ↓
interpretation artifact
  ↓
future decision artifact
```

interpretationは「結果から何を読み取ったか」を外在化するが、winner、recommendation、B5 decision、production adoptionを所有しない。

## 2. State

### draft

checked-in templateは次を維持する。

- `generated_at = null`
- result digest bindingなし
- analyst provenanceなし
- findingなし
- limitationなし
- `interpretation_digest = ""`

### interpreted

interpreted artifactは少なくとも次へbindされる。

- completed resultのexact `result_digest`
- resultのtrack / variant / capacity / stress identity
- analyst provenance ref
- 40桁lowercase Git commit SHA
- findingが参照したresult metric名
- explicit limitation
- canonical SHA-256 interpretation digest

## 3. Finding

findingは次のkindだけを許可する。

- `metric-observation`
- `cross-metric-observation`
- `limitation-aware-hypothesis`

claim strengthは:

- `observation`
- `hypothesis`

のみ。

findingはresult metricをstable nameで参照し、metric valueを別値として再定義しない。

## 4. 非決定性

interpretation artifactは次のflagを常にfalseに保つ。

```text
semantic_truth_claimed
variant_winner_declared
recommendation_generated
b5_decision_generated
production_default_changed
```

strict schemaのため `winner` や `composite_score` 等の未登録fieldも拒否する。

自由記述のstatementは非権威的な観測・仮説の記録であり、後段のDecision semanticsではない。

## 5. Limitation

interpreted artifactは最低1件の明示的limitationを必須とする。

測定結果が存在しても、dataset scope、sample size、missing metric、environment、generalization等の限界を消去しない。

## 6. Provenance

interpretationはanalyst provenanceとして:

- opaque ref
- exact Git commit

を保持する。

個人名をartifact contract上の必須identifierにしない。

## 7. Immutability

interpreted artifactはcanonical `interpretation_digest` を持つ。

canonicalization:

- UTF-8 JSON
- key sort
- compact separator
- `interpretation_digest` 自身だけ除外
- SHA-256

解釈後にfinding、limitation、scope、provenanceを変更するとdigest mismatchになる。

## 8. Validation

current draft:

```bash
python validate_interpretation.py
```

期待値:

```text
Cross-stage interpretation validated; current interpretation remains draft/empty
```

interpreted validationではupstreamの:

- preregistration
- frozen bundle
- authorized run
- completed result
- full unlock state

も再検証する。

## 9. 停止線

```text
interpretation != semantic truth
interpretation != variant winner
interpretation != recommendation
interpretation != B5 decision
interpretation != production default
synthetic interpreted path != human-adjudicated benchmark interpretation
```

実human-adjudicated benchmark resultが存在するまで、checked-in `interpretation.json` をinterpretedへ変更しない。


## 10. Evidence

machine-readable contract Evidence:

`interpretation_contract_evidence_2026-09-19.json`

このEvidenceはGitHub source inspectionと定義済み回帰coverageを記録する。今回のcontract更新ではruntime test PASSを主張しない。

```text
defined tests != executed tests
source contract != human benchmark interpretation
```
