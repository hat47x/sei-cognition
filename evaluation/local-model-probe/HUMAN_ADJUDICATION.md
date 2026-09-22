# Local Model Probe — Human Adjudication

更新日: 2026-09-20  
状態: **Evaluation-only Human Review Sidecar**  
関連: Issue #375 / `README.md` / `MODEL_MATRIX.md`

## 1. 目的

model outputの品質判定をmodel自身へ委ねない。

```text
machine evaluator
  -> structural / semantic contract checks

human adjudication
  -> task success / semantic acceptability judgment
```

両者は別Evidenceとして保存する。

human reviewはmodel outputをTruthやDecisionへ昇格させる手続きではない。

current sidecar/report schema:

```text
sei-cognition.local-model-human-adjudication/v1
sei-cognition.local-model-human-adjudication-report/v1
```

`v1` はmodel artifact identityを含む現行形式である。旧human adjudication `v0` は同じ意味へ暗黙upgradeせずrejectする。

## 2. template生成

current complete matrix artifact（`sei-cognition.local-model-matrix-run/v1`）からreview templateを生成する。Host Evidence導入前のmatrix `v0` はcurrent validatorで暗黙upgradeせずrejectする。

```bash
go run ./cmd/modeladjudicate \
  --matrix qwen08-matrix.json \
  --reviewer-label reviewer-1 \
  --output qwen08-review.json
```

templateはactual model resultが存在するfixtureだけを含む。

- raw: model resultがあるfixture;
- workspace: model resultがあるfixture;
- staged: local modelを実際に呼んだfixture;
- staged routing skip: 対象外.

生成時点では全entryが未評価である。

```json
{
  "task_success": "unassessed",
  "semantic_boundary": "unassessed"
}
```

AIがtemplate生成時にpass/failを先取りしない。

## 3. 人が記入する値

`reviewed_at`は実際のreview時刻をRFC3339で記録する。

`task_success`:

- `pass`
- `fail`
- `uncertain`

`semantic_boundary`:

- `preserved`
- `violated`
- `uncertain`

`fail` / `uncertain` / `violated`を含むentryでは`notes`を必須とする。

## 4. validation

人が記入したsidecarをmatrixへ再結合する。

```bash
go run ./cmd/modeladjudicate \
  --matrix qwen08-matrix.json \
  --review qwen08-review.json \
  --output qwen08-human-report.json
```

validatorは次をfail-closedで確認する。

- schema / status;
- exact `source_git_sha`;
- exact model identifier;
- matrixにmodel artifact identityがある場合、そのSHA-256 / size;
- matrixがcompleteであること;
- raw / workspace / staged artifact identity;
- entry重複なし;
- actual evaluated resultだけを対象にしていること;
- required fixtureの全件coverage;
- `unassessed`が残っていないこと;
- `reviewed_at`がRFC3339であること;
- fail / uncertain系にnotesがあること.

## 5. report

reportはmode別の**件数**を保持する。

- assessed;
- task pass / fail / uncertain;
- semantic boundary preserved / violated / uncertain.

単一のoverall scoreやmodel順位は自動生成しない。

```text
human pass count
  != model adoption

human adjudication
  != canonical Truth
  != Decision

machine contract PASS
  != human task success

routing skip
  != successful model answer
```

## 6. reviewer label

`reviewer_label`はEvidence内でreview単位を識別するためのlabelであり、実名を要求しない。

複数reviewerを比較する場合は、それぞれ独立sidecarとして保存し、一つの値へ暗黙統合しない。

review template / validated reportはmatrixの`model_artifact` identityも引き継ぐ。これによりmodel名が同じでも異なるGGUF bytesへのreview取り違えを防ぐ。ただしmodel artifact digestはruntime load attestationではない。
