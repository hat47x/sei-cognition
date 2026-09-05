# Runtime Version Exchange Evidence — 2026-09-05

状態: **Scoped Executable Evidence available**
対象: **ISSUE-000070 / fixed model artifact下のOllama runtime version交換**

## 1. この文書の役割

この文書は、同じKJ Atlas source、同じMethod input、同じactual model artifact、同じmodel promptを使い、Ollama runtimeだけを`0.32.13`から`0.32.14`へ交換したrepository-local actual runを記録します。

中心命題は次です。

```text
runtime version exchange
  → new exact Realization revision
  != historical Application rewrite
```

今回の成立範囲をruntime-version-exchangeの**Scoped Executable Evidence**とします。任意のruntime versionや別runtime実装との互換性、生成品質、Operational / Release / Adoption・Outcome Evidenceへは広げません。

## 2. 実行identity

- 実行日: 2026-09-05 JST
- execution ID: `local-20260904T193531Z-7855`
- execution surface: `repository-local-harness`
- SOZA source commit: `ae9f631b7d570a6c3853bb71b794d501761fdf63`
- host: Linux / amd64
- Go: `1.25.14`
- Python: `3.11.2`
- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- parent backend tree: `7d71ac2b4d32bef90f3a481ade1b4c92ddddd084`
- runtime surface tree: `208bea71eef4afed3ddfd3fabb36b0969d167a90`
- KJ Atlas source mode: `verified-runtime-bundle`
- source acquisition: `git-archive-from-pinned-commit`

KJ Atlas checkoutは固定commit objectの取得元としてだけ利用しました。actual processへ渡したのは、そのcommit objectからexportし、Git object identityを再検証したruntime surfaceです。

## 3. 固定入力

### Runtime archive

| revision | actual binary version | archive size | actual SHA-256 |
| --- | --- | ---: | --- |
| A | `0.32.13` | `1421793186` bytes | `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` |
| B | `0.32.14` | `1421191399` bytes | `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |

両archiveはrepository外へ事前配置し、canonical preparation helperの`--verify-only`で実行前に再検証しました。actual binary versionも各archiveを展開した実体から観測しています。

### Model artifact

- model: `qwen2.5:0.5b`
- manifest raw bytes SHA-256: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`
- referenced blobs: `5`
- referenced bytes total: `397821319`
- storage mode: `prepositioned`
- static verification: manifest / declared size / actual blob SHA-256すべてPASS

A / B双方のactual `/api/tags`でも、この同じfull digestを確認しました。model tagや事前配置pathだけから同一性を推論していません。

### Method input / prompt

- Method input: 固定3-card input
- held card: `c-held`
- prompt SHA-256: `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`

A / Bのprompt SHA-256は一致しました。

## 4. Actual inference

| observation | A / `0.32.13` | B / `0.32.14` |
| --- | ---: | ---: |
| `ollama_done` | `true` | `true` |
| `ollama_done_reason` | `stop` | `stop` |
| `prompt_eval_count` | `196` | `196` |
| `eval_count` | `78` | `78` |
| `load_duration` | `2555581433` ns | `1801241256` ns |
| `total_duration` | `8908153391` ns | `7125363617` ns |

両runtimeでprompt評価とtoken生成を伴うactual inferenceが成立し、KJ Atlasのresponse境界を通過しました。二つの在宅勤務カードは同じgroupへ入り、`c-held`は`excludedCardIds`へ分離され、`truncated=false`でした。

今回のA / B出力は同一でしたが、出力一致はResolution条件ではありません。durationやtoken countもsemantic identityには含めません。

## 5. Exact Bindingとhistorical Application

actual A / B結果を入力にしたlive Go test `TestLiveKJAtlasRuntimeVersionExchangePreservesHistoricalApplication`はPASSしました。

このtestで次を同時に確認しています。

- A / Bは同じlogical Method Realization `MR-KJ-ATLAS-RUNTIME-EXCHANGE`を持つ。
- runtime versionとruntime archive identityを含むRealization payloadは、異なるRaw Bytes SHA-256 Exact Bindingになる。
- Application A / Bは、それぞれ当時のExact Realization Referenceを保持する。
- B追加後もApplication AのExact Reference、Provenance、outputは変化しない。
- 両Applicationは同じMethod Definitionを参照する。
- 両Provenanceは同じ固定model artifactを参照し、runtime versionだけを区別して保持する。
- Method outputをRecommendation / Decisionへ自動昇格しない。

```text
same logical Realization
  + different exact revision
  + immutable historical Application A
```

## 6. Portable historical reconstruction

同じlive test内で、A / BのRealization revisionとApplicationを一つのSemantic Interchangeへ格納し、`semanticruntime.LoadInterchange`で再読込しました。

- Realization payloadのRaw Bytes SHA-256検証: PASS
- Application Aからrevision Aへの解決: PASS
- Application Bからrevision Bへの解決: PASS
- 同じidentityからのBinding再構成: PASS
- 存在しないrevision digestへの差し替え拒否: PASS
- runtime / runtime artifact / model artifact identity変更時のBinding変化を確認するnon-live control: PASS

したがって、今回の固定A / B範囲では、runtime交換をlatest-winsの上書きとして扱わず、当時のExact Bindingへ戻せます。

## 7. Evidence + Provenance verification

標準入口`run_runtime_version_exchange_prepositioned.py`から、preflight、strict entrypoint、actual harness、独立verifierまでを一続きに実行しました。

- preflight: `ready`, blockers `[]`
- strict / harness exit code: `0`
- Evidence directory creator: `strict-entrypoint`
- runner completed: `true`
- runner combined output: `20320` bytes
- runner log SHA-256: `4fb5833f8522ad65ab6552629a4982175337b73431d0d4e2913f8ffea827f48d`
- core Evidence result: `ready-to-review`
- Evidence + Provenance result: `ready-to-review`
- verifier checks: `107 ok / 0 blocked`
- verification report SHA-256: `121b4167e7d0deb13f831cbcf7031c2d3f20a5195f55dd3a891f582ebe6c6774`

実行時Evidenceはrepository外に作成しました。完了後、26個のEvidence fileと外置きverification reportを、バイト列を変えず次へ保存しています。

`runtime/evidence/runtime-version-exchange-local-20260904T193531Z/`

保存コピーは実行時出力pathではなくpost-run archiveです。`.gitattributes`でEOL変換を無効にし、runner observationが記録したlog digestをcheckout後も再検証できるようにしています。

repository rootから次で保存コピーを再検証できます。

```bash
python3 runtime/integration/verify_runtime_version_exchange_provenance.py \
  --evidence-dir runtime/evidence/runtime-version-exchange-local-20260904T193531Z \
  --json
```

## 8. Requirement / Scenario / Contract再照合

新しいStable Requirement、Acceptance Scenario、Universal Contract fieldは追加しません。

- REQ-0001: runtime revision交換後も先行Applicationの意味と来歴を保持した。
- REQ-0004: MethodをOllama versionと同一視せず、当時のApplicationをExact Realization revisionへ戻せた。
- REQ-0021: runtimeという交換可能な実現層を変更してもDurable Semantic Coreを書き換えなかった。
- SCN-0005: Definition / Realization / Applicationを分離し、Realization変更で過去Applicationを上書きしなかった。
- SCN-0015: Method outputをRecommendation / Decision / Assuranceへ自動昇格しなかった。

既存Cognitive Method Contract、Semantic Reference、Semantic Interchange、Raw Bytes SHA-256 Profileで今回必要な意味を表現できました。runtime名、version、archive digest、model digest、prompt digestはRealization-local metadata / Provenance / Evidenceに留まり、Universal field追加の必要性は確認されませんでした。

各Requirement / ScenarioのExecutable Evidenceは引き続き`Partially Satisfied`です。今回確認したのは固定KJ Atlas、固定model、Ollama 2 revisionのscopedな実証であり、production全体や任意のRealization交換ではないためです。

## 9. 成果品質との境界

Evidenceにあるgrouping resultは構造上受理されました。ただし、label「生活習慣」やrationaleの意味・日本語表現がKJ法の成果として十分かは評価していません。

- `qualityJudgement = not_evaluated`
- model output quality: **Not Evaluated**
- language suitability: **Not Evaluated**
- KJ-method outcome quality: **Not Evaluated**
- Recommendation correctness: **Not Evaluated**
- Decision correctness: **Not Evaluated**

actual inferenceとhistorical reconstructionの成立を、成果品質の成立へ読み替えません。

## 10. 今回成立した範囲

- fixed KJ Atlas runtime surface: **Verified**
- fixed runtime A / B archive actual bytes: **Verified**
- actual Ollama `0.32.13` / `0.32.14` binary execution: **Verified**
- fixed model static identity and actual `/api/tags` identity: **Verified**
- same Method input / prompt: **Verified**
- A / B actual inference and KJ Atlas response acceptance: **Verified**
- same logical Realization / different Exact Binding: **Verified**
- historical Application A immutability: **Verified**
- portable historical reconstruction and negative control: **Verified**
- no automatic semantic promotion: **Verified**
- Evidence + Provenance independent verification: **ready-to-review**
- runtime-version-exchange scope: **Scoped Executable Evidence available**

以上により、ISSUE-000070のResolution Criteriaは満たされています。

## 11. 今回も成立させないもの

- arbitrary runtime version portability
- other runtime implementation portability
- fully offline execution guarantee
- production long-running operation
- model output quality / language suitability
- KJ-method outcome quality
- actual human outcome review
- E4 Operational portability
- v0.2.0 supported scopeの遡及的拡張
- 新しいRelease Evidence
- Adoption / Outcome Evidence

固定artifactを事前配置すればnetworkなしで再検証・actual実行へ入れる経路は確認しましたが、今回の環境構築ではKJ Atlas Python依存をnetworkから取得しています。このため、fully offline executionの成立は主張しません。

## 12. 自然な日本語レビュー

ISSUE-000067 / 000068 / 000070 / 000071、REQ-0001 / 0004 / 0021、SCN-0005 / 0015、Cognitive Method Contract、Semantic Reference / Interchange、actual Evidence 26 file、verification report、live Go testの検査内容を照合しました。

実行前に定めた固定条件とResolution Criteriaへ結果を一件ずつ対応させ、取得元、配置path、artifact identity、logical Realization、Exact Binding、Application、成果品質を混同しないよう整理しました。実行時Evidenceとrepository内のpost-run archiveも区別しています。

今回初めて成立したのは、固定model artifact下でOllama runtimeの2 revisionをactualに交換しても、先行Applicationを保持し、portableに当時revisionへ戻せるという限定Evidenceです。その範囲を超える互換性、品質、運用、release、利用成果は未検証のまま残します。
