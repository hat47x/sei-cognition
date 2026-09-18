# Cross-stage Freeze Kit

状態: **Draft manifests / Evaluation Locked**  
更新日: 2026-09-18

## 1. 目的

`cross_stage_benchmark_preregistration.json` で固定したcross-stage evaluationを、human-adjudicated datasetが用意された時点で再現可能にfreezeするためのartifact群である。

このdirectoryに置くtemplateは現在すべて `draft` であり、実semantic benchmark dataの代用品ではない。

既存のcontract fixture、synthetic SACS fixture、B6 stress fixtureをhuman-adjudicated datasetとして流用しない。

## 2. Artifact

- `dataset_manifest.json`
  - item ID
  - source ref
  - content SHA-256
  - dataset digest
- `adjudication_manifest.json`
  - dataset digest binding
  - opaque reviewer ref
  - judgment
  - unresolved disagreement
- `split_manifest.json`
  - retrieval calibration / evaluation
  - familiarity calibration / evaluation
  - routing training / holdout
- `b3_prior_manifest.json`
  - exact Channel + Key selector
  - bounded multiplier
  - provenance
  - authoring source
  - dataset / adjudication digest binding
- `freeze_bundle.json`
  - 上記4 manifestのdigest binding

## 3. Dataをmanifestから分離する

dataset manifestは本文を保持せず、source refとcontent digestを保持する。

```text
source material
  -> stable source ref
  -> content SHA-256
  -> dataset manifest
```

これにより、freeze時点で何を評価したかを固定しつつ、元資料のownershipや保存場所をmanifestへ混ぜない。

source refの解決規則は評価実行側が明示する。

## 4. Human adjudication

reviewerは実名・メールアドレスではなく、opaqueな `reviewer:...` refで記録する。

各dataset itemは、freeze時に次のいずれかでcoverageされる必要がある。

- 一つ以上のjudgment
- unresolved entry

不一致を多数決で強制的に消す必要はない。

```text
disagreement
  -> unresolved
  != forced consensus
```

実際のlabel ontologyはhuman adjudication policyでversion管理する。freeze kit自身はsemantic truthを定義しない。

## 5. Split

freeze時には次の各trackで左右partitionが非空かつdisjointである必要がある。

- retrieval: calibration / evaluation
- familiarity: calibration / evaluation
- routing: training Outcome / holdout replay

dataset itemは少なくとも一つの登録track partitionへ割り当てる。

B7 holdout replayのcounterfactual completenessはpreregistration側の追加条件であり、このmanifestのID分割だけで保証されるものではない。

## 6. B3 prior

B3 priorは評価前にfreezeする。

rule:

- exact `channel`
- exact `key`
- multiplier `(0, 2]`
- provenance ref
- authoring source

`evaluation-label-derived` はvalidatorが拒否する。

`evaluation_labels_used_for_authoring` は常に `false` でなければならない。

## 7. Canonical digest

各manifestはJSONを

- key sort
- UTF-8
- compact separator
- 自身のdigest fieldだけ除外

してSHA-256を計算する。

`frozen_at` と `state` はdigest対象に含むため、同じcontentでもfreeze timestampを変えれば別snapshotになる。

同一content + 同一 `frozen_at` では同じdigestになる。

## 8. 検証

draft templateの検証:

```bash
python freeze_manifests.py --validate-only
```

現在の期待結果:

```text
Cross-stage freeze manifests validated; current bundle remains draft/locked
```

空datasetはfreezeできない。

## 9. Freeze手順

実dataを別directoryへmaterializeし、5 manifestを埋める。

入力directoryを直接変更しない。freeze結果は新しいoutput directoryへ出す。

```bash
python freeze_manifests.py \
  --input-dir /path/to/prepared-manifests \
  --freeze-output-dir /path/to/frozen-bundle \
  --frozen-at 2026-09-18T12:00:00Z
```

`--frozen-at` は必須で、自動的な現在時刻は使わない。再現性のためfreeze eventが明示的に与える。

freeze成功条件:

1. datasetが空でない
2. content digestが妥当
3. reviewer refがopaque
4. adjudicationが全dataset itemをjudgmentまたはunresolvedでcoverage
5. split overlapがない
6. 全dataset itemが少なくとも一つのtrackへ割り当て済み
7. B3 prior leakageがない
8. 各manifest digestがcanonical contentと一致
9. freeze bundleのcomponent bindingが一致

## 10. Freeze後も評価は始まらない

`freeze_bundle.json` はfrozen後も、

```json
"result_generation_enabled": false,
"b5_entry_gate_changed": false
```

を維持する。

次段では、frozen bundleを入力として**別のexplicit evaluation-run artifact**を作る。

```text
frozen bundle
  != benchmark result
  != production adoption
  != B5 gate open
```

## 11. 現在地

現在repoに置かれている5 manifestは空のdraft templateである。

human adjudication、dataset source、split、B3 priorが提供されていないため、現時点でfrozen状態へ変更してはならない。
