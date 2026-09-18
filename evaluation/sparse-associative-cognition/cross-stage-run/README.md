# Cross-stage Evaluation Run

状態: **Draft / Execution Locked**  
更新日: 2026-09-18

## 1. 役割

このdirectoryは、frozen cross-stage bundleを入力としてhuman-adjudicated benchmarkを実行する直前の**実行許可スナップショット**を扱う。

現在の `evaluation_run.json` はtemplateであり、`draft` のままである。

```text
preregistration
  ↓
freeze kit
  ↓
frozen bundle
  ↓
explicit evaluation-run artifact
  ↓
authorized
  ↓
future executor / result artifact
```

この段階ではexecutorもresult artifactも実装しない。

## 2. state

### draft

- `authorized_at = null`
- `execution_authorized = false`
- freeze/prereg/split/prior verification flag = false
- `results_generated = false`

current repository templateはこの状態である。

### authorized

run artifactがauthorizedになれるのは、次が同時に成立する場合だけ。

- freeze bundleがfrozenでvalid
- freeze bundle digestがrun bindingと一致
- preregistration unlock条件が成立
- track / variant / capacity profile / stress policy / metricが事前登録済み
- implementation refと40桁lowercase Git commit SHAが明示
- opaqueなauthorization refが明示
- environment descriptorが明示
- canonical run digestがrun内容と一致
- evaluation tuningを行わない
- single composite scoreを使わない
- B5 gateを変更しない
- production defaultを変更しない

authorizedになっても `results_generated=false` のままである。

## 3. Track

### retrieval

variant:

- B0
- B1
- B1-B2
- B1-B2-B3

primary capacity:

- small
- medium
- large

primary profileでは `stress_policy=null` を要求する。

### oversized stress

`capacity_profile=oversized-stress` の場合だけ、

- proportional-baseline
- cap128
- cap64

のpreregistered stress policyを指定できる。

また `oversized_residual_policy_stress` metricを必須にする。

これはproduction default探索ではなくrobustness stress testである。

### familiarity

- variant = SAC-B4
- capacity profileなし
- stress policyなし

### routing

- variant = SEI-B7
- capacity profileなし
- stress policyなし

## 4. Metrics

requested metricはtrackごとのpreregistrationから選ぶ。

run側で新しいmetricを追加できない。

特に、run artifactへ独自のcomposite scoreを追加することはできない。

retrievalのdiagnostic metricは要求できるが、それはsemantic scoreではない。

## 5. Freeze binding

`freeze_bundle.digest` は、実際に検証したfrozen `freeze_bundle.json` のcanonical bundle digestと一致しなければならない。

current repository bundleはdraftでdigestが空のため、current runはauthorizeできない。

## 6. Implementation binding

authorized runは、

- implementation ref
- 40桁lowercase Git commit SHA

を固定する。

これにより「どの実装で測ったか」をrun単位で外在化する。

commit bindingはproduction releaseを意味しない。

## 7. Authorized runのimmutability

authorized runは自身の `run_digest` を持つ。

canonicalizationはfreeze kitと同じく、

- UTF-8 JSON
- sorted keys
- compact separators
- `run_digest` fieldだけ除外

としてSHA-256を計算する。

authorization後にvariant、metric、output ref、environment等を変更すればdigest mismatchとなる。

`authorization_ref` は実名を格納する場所ではなく、承認記録へのopaque provenance refとして扱う。

## 8. Resultとの分離

run artifactは結果を所有しない。

常に:

```json
"results_generated": false,
"result_artifact_ref": ""
```

とする。

将来executorが実行された場合、結果は別schemaのresult artifactとして生成する。

run artifactを実行後に書き換えて結果を埋め込まない。

## 9. 検証

current draft:

```bash
python validate_evaluation_run.py
```

期待値:

```text
Cross-stage evaluation-run validated; current run remains draft/locked
```

unit testsではsynthetic frozen bundleをmemory上で作り、

- compliant primary retrieval
- compliant oversized stress
- familiarity
- routing

のauthorized pathだけを確認する。

synthetic authorizationは実human benchmarkのunlockではない。

## 10. 停止線

```text
authorized run != benchmark success
authorized run != result artifact
frozen bundle != semantic correctness
implementation commit != production release
requested diagnostics != semantic score
authorized run != B5 gate open
authorized run != production adoption
```

実dataset/adjudicationがfreezeされるまで、checked-in templateをauthorizedへ変更しない。
