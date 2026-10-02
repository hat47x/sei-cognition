# Runtime Version Exchange — Current Contract Revalidation

更新日: 2026-09-05  
対象: ISSUE-000070 / execution `local-20260904T193531Z-7855`

## 1. 目的

`codex/issue-000070-actual-evidence`から回収したactual runtime version交換Evidenceが、実行当時だけでなく現在の`develop/v0.2.0`のResolution Criteria / Requirement / Contractにもそのまま適用できるかを、Git object identityで再監査する。

この監査はactual Ollama A/Bを再実行したものではない。保存済みactual Evidenceが検証された基準と、現在の基準が同一であるかを確認するcurrent-contract equivalence auditである。

```text
current-contract equivalence audit
  != new actual A/B execution
  != model output quality evaluation
  != KJ-method outcome quality evaluation
  != E4 Operational portability
```

## 2. actual run時の基準

actual runのSOZA source commit:

- `ae9f631b7d570a6c3853bb71b794d501761fdf63`

回収済みEvidence:

- execution ID: `local-20260904T193531Z-7855`
- Evidence directory archive: `runtime/evidence/runtime-version-exchange-local-20260904T193531Z/`
- narrative Evidence: `runtime/RUNTIME_VERSION_EXCHANGE_EVIDENCE_2026-09-05.md`

保存済みverification:

- `blockers = []`
- `coreEvidenceResult = ready-to-review`
- `result = ready-to-review`
- runner `completed = true`
- runner `exitCode = 0`
- runner `preflightResult = ready`
- `evidenceDirectoryCreatedBy = strict-entrypoint`
- `qualityJudgement = not_evaluated`

A / B actual model-call Evidenceでは、両方とも次を直接記録している。

- `ollama_done = true`
- `ollama_done_reason = stop`
- `prompt_eval_count = 196`
- `eval_count = 78`
- prompt SHA-256 = `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`

## 3. current developとのobject-level同一性

actual run commitとcurrent `develop/v0.2.0`をGit object identityで比較した。

### ISSUE-000070 Resolution Criteria

`plan/issue/ISSUE-000070-verify-runtime-version-exchange-history.md`

- actual run commit blob: `19e4802c8254bb4f76ce168f14aeff128cb2159c`
- current develop blob: `19e4802c8254bb4f76ce168f14aeff128cb2159c`
- 判定: identical

したがって、actual run後にResolution Criteriaが追加・変更された事実はない。

### Core Evidence verifier

`runtime/integration/verify_runtime_version_exchange_evidence.py`

- actual run commit blob: `1e9f382e51b81f72e625824a1ebb8de58095f5c8`
- current develop blob: `1e9f382e51b81f72e625824a1ebb8de58095f5c8`
- 判定: identical

### Evidence + Provenance verifier

`runtime/integration/verify_runtime_version_exchange_provenance.py`

- actual run commit blob: `6243d4bb8607b290b2494135a08840fffb4415c8`
- current develop blob: `6243d4bb8607b290b2494135a08840fffb4415c8`
- 判定: identical

保存済み`verification.json`を生成した機械判定と、current canonical verifierの判定ロジックは同一である。

### Fixed artifact manifest

`runtime/integration/runtime_version_exchange_artifacts.json`

- actual run commit blob: `c567edfa90d452f1945585a775ac5f8eef6ffc38`
- current develop blob: `c567edfa90d452f1945585a775ac5f8eef6ffc38`
- 判定: identical

runtime A / B、KJ Atlas source、model artifact等の固定条件も漂流していない。

### Product Requirements

`requirements/PRODUCT_REQUIREMENTS.md`

- actual run commit blob: `deb59d99c7c6bd56d8cc9a79db6e1d25beb7eba1`
- current develop blob: `deb59d99c7c6bd56d8cc9a79db6e1d25beb7eba1`
- 判定: identical

### Acceptance Scenarios

`requirements/ACCEPTANCE_SCENARIOS.md`

- actual run commit blob: `efaa2317afaf8f77d15ae8d49b4e269970e062dc`
- current develop blob: `efaa2317afaf8f77d15ae8d49b4e269970e062dc`
- 判定: identical

### Semantic Contract baseline

actual run commitとcurrent developで、少なくとも次のContract正本・tree identityが一致する。

- `contracts/CONTRACT_CATALOG.md`: `62ef3ef44399830f8c486fe70fa6c6585984d6ec`
- `contracts/TRACEABILITY.md`: `58c5bbf41b8ab705b5bc1f7996bdc937a2acbeb3`
- `contracts/cognitive-method/` tree: `2498d324114fecd496e3f419eb6eda496c6d2296`
- `contracts/interchange/` tree: `d99ea55a59ceb157c1e7b97512b57603b970ea9c`
- `contracts/semantic-reference/` tree: `687f7ee88fd704062676ab9734aaaea301babf30`
- `contracts/profiles/` tree: `0eeaab829fb662ff3e8d9ccf41a7a2baf7d32635`
- `contracts/schemas/` tree: `170de592eade6402887b75d71cdd12a815983846`

したがって、actual EvidenceのRequirement / Contract再照合後に、今回のResolution判断を覆すSemantic Contract driftは観測されない。

## 4. Resolution Criteria再照合

current ISSUE-000070の12条件へ、回収済みEvidenceを再対応させる。

1. **fixed KJ Atlas verified runtime surface** — satisfied。固定commit / backend tree / runtime surface treeをEvidence + verifierが確認。
2. **fixed runtime A/B actual bytes SHA-256** — satisfied。A/B archive SHA-256を固定値へ照合。
3. **actual binary version A/B** — satisfied。Ollama `0.32.13` / `0.32.14`を実体から観測。
4. **same fixed model + same prompt digest** — satisfied。A/B `/api/tags` full digestと同一prompt SHA-256を確認。
5. **actual inference on both runtimes** — satisfied。A/Bとも`ollama_done=true`、prompt/eval count > 0。
6. **same logical / different Exact Realization revision** — satisfied。live Go testで確認。
7. **historical Application A immutability** — satisfied。Reference / Provenance / output不変性を確認。
8. **payload verification / portable reconstruction / unknown revision negative control** — satisfied。
9. **no automatic Recommendation / Decision promotion** — satisfied。
10. **complete run Evidence preservation** — satisfied。run identity、source、runtime、model、input、A/B Evidence、runner observation / logへ復帰可能。
11. **independent Evidence + Provenance verification** — satisfied。保存済みverificationは`ready-to-review`、`blockers=[]`。current verifierと実行時verifierは同一blob。
12. **Requirement / Contract再照合 + natural Japanese final audit** — satisfied。Evidence narrativeでREQ-0001 / REQ-0004 / REQ-0021、SCN-0005 / SCN-0015、Cognitive Method / Semantic Reference / Interchangeを再照合し、自然な日本語レビューを実施。Requirement / Scenario / Contract正本はactual run時からcurrent developまで同一objectである。

## 5. 「current canonical verifierを再実行していない」ことの扱い

回収記録では、保守的に次を未実施として残していた。

```text
historical actual Evidence recovered
  != current-contract revalidation PASS
```

今回の監査で、次がすべて同一Git objectであることを確認した。

- Resolution Criteria
- core verifier
- Provenance verifier
- fixed artifact manifest
- Product Requirements
- Acceptance Scenarios
- relevant Semantic Contract baseline

したがって、「後から強化された別verifier / 別contractへまだ通していない」という前提自体が成立しない。保存済みverificationは、current canonical verifierと同じ実装・current fixed artifact manifestと同じ固定条件に対する結果である。

repository内archiveを別pathで再実行することは再現性確認として有用だが、current IssueのResolution Criteriaに新しく追加された条件ではなく、今回のResolution判定を保留する理由にはしない。

```text
same canonical verifier object
+ same fixed artifact manifest object
+ same Requirement / Scenario objects
+ same relevant Contract objects
+ recovered actual Evidence ready-to-review
+ Requirement / Contract / natural-language audit recorded
= current ISSUE-000070 Resolution Criteria satisfied
```

## 6. 成果品質との停止線

今回のrevalidationはexecution / historical reconstructionの成立範囲だけを扱う。

- `qualityJudgement = not_evaluated`
- model output quality = Not Evaluated
- language suitability = Not Evaluated
- KJ-method outcome quality = Not Evaluated
- Recommendation correctness = Not Evaluated
- Decision correctness = Not Evaluated
- E4 Operational portability = Not Established

```text
ISSUE-000070 Resolution Criteria satisfied
  != arbitrary runtime portability
  != output quality satisfied
  != Operational Evidence
  != E4 Operational portability
```
