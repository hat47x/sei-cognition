# SAC-B6i workload-class governance

状態: **Evaluation-only / fail-closed**  
関連: Issue #519 / SAC-B6g / SAC-B6h

## 目的

B6gのcaller-owned workload classを、単なる文字列mappingのまま恒久利用しないためのlifecycle / review境界です。

このcontractはclassを推測しません。callerが明示したclassについて、

- version
- owner / provenance
- declared / valid / review-due / expiry時刻
- review metadata / Evidence
- supersession
- resolution可否

を検証します。

## current state

checked-in declarationは2件とも `candidate` です。

- `general -> cap128`
- `structure-preserving -> baseline`
- `resolution_allowed=false`
- `review=null`

つまり、governance contractを追加しただけで現在のresidual policyを有効化していません。

時刻判定にはwall clockを使わず、manifestの固定 `validation_as_of` を使います。これによりvalidatorの判定を決定論的に再現できます。

## reviewed state

`reviewed` へ進む場合だけ、strict review metadataが必要です。

- reviewer ref
- reviewed_at
- change-review ref
- non-empty Evidence refs

さらに `valid_from <= validation_as_of < review_due_at < expires_at` のlifecycle境界を満たす必要があります。

review期限到来後やexpiry後にreviewed/resolvableのまま残ることをfail-closedで拒否します。

## version / supersession

version 2以上は過去versionへの `supersedes_version` が必須です。

superseded versionと後続versionは双方向に結び、旧versionがresolution可能なまま残ることを拒否します。

## B6g binding

governance artifactは次へexact bindingします。

- envelope ref: `../workload_policy_envelope_evidence_2026-09-19.json`
- envelope id: `b6g-grid-eval-v1`
- allowed policies: `baseline / cap128 / cap64`
- exact mapping:
  - `general -> cap128`
  - `structure-preserving -> baseline`

## 実行

```bash
python3 workload-class-governance/validate_governance.py
python3 -m unittest -v workload-class-governance/test_validate_governance.py
```

current exact-source runtime Evidence:

`workload_class_governance_runtime_evidence_2026-09-19.json`

## 停止線

```text
valid declaration != correct declaration
reviewed != semantic truth
provenance != correctness
expiry/review contract != automatic classifier
governance validity != production adoption
resolution_allowed in evaluation contract != provider / production activation
```

B6hで観測したmisdeclaration sensitivityは、review制度が正しさを保証する根拠ではありません。review / expiry / versioningは誤りを追跡し、期限切れや古い宣言をfail-closedにするgovernance mechanismです。
