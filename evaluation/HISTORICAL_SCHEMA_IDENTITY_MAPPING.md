# Historical Schema Identity Mapping

更新日: 2026-09-11  
状態: **Historical Identity Mapping — 改稿対象外の記録に対する橋渡し**

## 1. この文書の役割

この文書は、2026-09-11のSOZAからSEI Cognitionへの改名にあたって、`evaluation/`配下の記録済みEvidenceに残る旧identityを、currentのidentityへ解決するための対応表です。

記録済みEvidenceを現在の名前へ書き換えたものではありません。当時のrunが実際に出力したrecordはそのまま保持し、読み替えだけをここで行います。

```text
記録の改名
  != 記録の更新
  = 記録の破壊
```

判断の本体はADR-0031です。この文書はその適用範囲を`evaluation/`について具体化するものであり、権威はADR-0031にあります。

## 2. 改稿対象外とするもの

```text
evaluation/method-quality/historical/
evaluation/failure-behavior/actual_provider_missing_revision_observation_20260910.json
evaluation/failure-behavior/scoped_go_failure_execution_20260910.json
evaluation/sparse-associative-cognition/sui_provider_cli_evidence_2026-09-12.json
evaluation/sparse-associative-cognition/sui_associative_conformance_evidence_2026-09-12.json
evaluation/sparse-associative-cognition/EXECUTION_EVIDENCE_2026-09-12.md
```

`evaluation/method-quality/historical/M1B-RUN-33596839607/review-manifest.json`は、`request.json`、`structure-report.json`、`model-evidence.json`等 6fileのsha256を記録しています。これらのfileは`soza`文字列を含みます。内容を書き換えるとmanifestのdigestと一致しなくなり、Evidence自体が自壊します。

したがってこのdirectory配下は、file内容をbyte単位で変更しません。

## 3. Identity mapping

`evaluation/`配下の記録に現れる旧identityと、currentのidentityの対応です。

| 記録済みEvidence上のidentity | currentのidentity |
|---|---|
| `soza.method-quality-review-bundle/v1` | `sei.method-quality-review-bundle/v1` |
| `soza.method-quality-structure-report/v1` | `sei.method-quality-structure-report/v1` |
| `soza.method-quality-case-catalog/v1` | `sei.method-quality-case-catalog/v1` |
| `soza.method-quality-case-catalog-validation/v1` | `sei.method-quality-case-catalog-validation/v1` |
| `soza.method-quality-historical-actual-samples/v1` | `sei.method-quality-historical-actual-samples/v1` |
| `soza.method-quality-historical-review-reconstruction/v1` | `sei.method-quality-historical-review-reconstruction/v1` |
| `soza.method-quality-ai-supplemental-observation/v1` | `sei.method-quality-ai-supplemental-observation/v1` |
| `soza.e3b-m1b-model-call/v1` | `sei.e3b-m1b-model-call/v1` |
| `soza.v6-v7-projection-evaluation/v1` | `sei.v6-v7-projection-evaluation/v1` |
| `soza.v6-v7-negative-cases/v1` | `sei.v6-v7-negative-cases/v1` |

2026-09-12にmain branchから合流した領域にも同じ規則を適用します。

| 記録済みEvidence上のidentity | currentのidentity |
|---|---|
| `soza.failure-behavior-case-catalog/v1` | `sei.failure-behavior-case-catalog/v1` |
| `soza.failure-behavior-requirement-audit/v1` | `sei.failure-behavior-requirement-audit/v1` |
| `soza.failure-behavior-probe-report/v1` | `sei.failure-behavior-probe-report/v1` |
| `soza.failure-behavior-local-check-result/v1` | `sei.failure-behavior-local-check-result/v1` |
| `soza.failure-behavior-scoped-go-execution-evidence/v1` | `sei.failure-behavior-scoped-go-execution-evidence/v1` |
| `soza.live-provider-failure-probe-result/v1` | `sei.live-provider-failure-probe-result/v1` |
| `soza.actual-provider-service-failure-observation/v1` | `sei.actual-provider-service-failure-observation/v1` |
| `soza.personal-inquiry-continuity-dogfood/v0` | `sei.personal-inquiry-continuity-dogfood/v0` |
| `soza.personal-inquiry-decision-prototype/v0` | `sei.personal-inquiry-decision-prototype/v0` |
| `soza.sparse-associative-cognition-research/v1alpha1` | `sei.sparse-associative-cognition-research/v1alpha1` |
| `soza.sui-associative-provider-cli-evidence/v1alpha1` | `sei.sui-associative-provider-cli-evidence/v1alpha1` |
| `soza.sui-associative-conformance-evidence/v1alpha1` | `sei.sui-associative-conformance-evidence/v1alpha1` |
| `soza.local-reasoning-working-set/v0` | `sei.local-reasoning-working-set/v0` |

`actual_provider_missing_revision_observation_20260910.json`が持つclaim keyとstop lineにも当時の名前が残ります。読み取り側は`evaluation/failure-behavior/test_actual_provider_missing_revision_observation.py`の`legacy_name()`で双方を受け付けます。

| 記録済みEvidence上の名前 | currentの名前 |
|---|---|
| `actualSozaGitHubCommitServiceExecution` | `actualSeiGitHubCommitServiceExecution` |
| `actualSozaLiveFailureRunnerExecution` | `actualSeiLiveFailureRunnerExecution` |
| `SOZA GitHubCommitService negative probe executed` | `SEI GitHubCommitService negative probe executed` |

versionは`v1`のまま進めていません。改名はidentifierの綴りの変更であり、schemaの意味、field、invariantは変わっていません。

```text
identifier rename
  != semantic change
  != new schema version
```

## 4. tool側の扱い

`evaluation/`配下のtoolは、ADR-0031の3に従って次のように振る舞います。

```text
emitterが書くidentity      = sei.*
readerが受け付けるidentity  = sei.* および soza.*
```

新しく出力するrecordには`sei.*`だけを書きます。読み取り側は、改名前に記録されたEvidenceを検証できるよう、旧identityも受け付けます。

この双方向受理は移行期間の暫定措置ではありません。記録済みEvidenceが存在する限り必要なため、期限を切っていません。片方だけを残す整理を行う場合は、対象の記録済みEvidenceが不要になったことを先に確認してください。

## 5. 関連

- `plan/adr/ADR-0031-product-rename-sei-cognition-identifier-boundary.md` — 改名判断の本体とmapping tableの正本
- `architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md` — Architecture領域における同趣旨の原則
- `contracts/history/HISTORICAL_CONTRACT_MAPPING.md` — Contract領域におけるhistorical mapping

## 6. Natural Japanese review

内容・構造を確定した後、自然な日本語を最重要視して全文を再ドラフトした。再ドラフト前後で、改稿対象外とする範囲、mappingの内容、versionを進めない理由、双方向受理が恒久措置であることが変わっていないことを確認した。
