# Model-backed Cognitive Method Evidence — 2026-09-02

状態: **Scoped Executable Evidence available**  
対象: **PMS-06 / E3b-M1b actual model-backed Cognitive Method execution**

## 1. この文書の役割

この文書は、E3b-M1bとして、実際に推論するmodel artifactをKJ Atlasのlive Cognitive Method経路へ接続し、その結果をSOZAの既存Cognitive Method Applicationへ戻した実行Evidenceを記録します。

最初の実証はPR #48で成立し、その後E3b-P2のfixed-artifact Evidenceが`develop/v0.2.0`へ先に統合されたため、最新develop基線からM1b変更だけを再適用したPR #50でも同じ実行経路を再検査しました。いずれもGitHub Actions上でKJ Atlas、Ollama、actual modelを別processとして起動し、modelの実推論からKJ Atlasのresponse解析、SOZAへのmappingまでをskipなしで実行しています。

```text
actual model acquired
  → actual inference executed
  → KJ Atlas accepted model output
  → SOZA Method mapping passed
```

この成立範囲を**Scoped Executable Evidence**とします。model出力の品質やKJ法としての成果品質までSatisfiedになったとは扱いません。

## 2. 実行identity

### 先行実証

SOZA側:

- Repository: `hat47x/soza`
- Original PR: `#48`
- Behavior-complete head: `fc88cee28fd67049922327384f7fafbbc56315d6`
- PR test merge commit: `27476bb6a1e9583282ae59f54395abbdef185186`
- Workflow: `External Model-backed Method E3b M1b`
- Workflow Run: `33596839607`
- Job: `100141890796` / `actual-model-backed-kj-atlas`

### E3b-P2統合後の再実証

SOZA側:

- Repository: `hat47x/soza`
- PR: `#50`
- Tested head: `95c3e4a51564bd5642775e5ba8d1fafafa7af14b`
- PR test merge commit: `67eea410de79e07e40895e84b51b6ae591c6a7e7`
- Base: `develop/v0.2.0@cef81daafe32d5943ab78b1b9599265988d6c28c`
- Workflow: `External Model-backed Method E3b M1b`
- Workflow Run: `33608342203`
- Job: `100177412784` / `actual-model-backed-kj-atlas`
- Runner: Ubuntu 24.04 / CPU-only inference

KJ Atlas側は両runで同一です。

- Repository: `hat47x/kj-atlas`
- Commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Entry point: `POST /ai/suggest-card-groups`
- KJ Atlas Provider kind: `local`
- KJ Atlas model boundary: `POST /generate`

model側も同一条件です。

- Inference runtime: Ollama `0.32.14`
- Model: `qwen2.5:0.5b`
- Observed Ollama model ID: `a8b0c5157701`
- Observed model size: `397 MB`

このidentityは今回の実証再現性のために固定したものであり、SOZAの標準modelや推奨modelを定めるものではありません。

## 3. M1aとの違い

E3b-M1aでは、固定revisionのKJ Atlas FastAPI backendとKJ Atlas repositoryに含まれるdeterministic model stubをSOZAとは別processとして起動し、actual `POST /ai/suggest-card-groups`を通しました。

M1bではKJ Atlas側のMethod surfaceを変えず、model processだけを実際に推論するartifactへ置き換えています。

```text
E3b-M1a
  KJ Atlas + deterministic model stub

E3b-M1b
  KJ Atlas + actual inference model
```

このため、M1aからM1bへ進んだことで新たに確認できた中心点は、「KJ Atlasの既存model境界をactual inferenceへ接続しても、既存SOZA Method境界へ戻せること」です。

## 4. Integration-only Adapter

`runtime/integration/e3b_m1b_ollama_adapter.py`は、KJ Atlasの既存`local` Provider境界をOllamaへ接続するためだけの薄いAdapterです。

```text
KJ Atlas POST /generate
  → integration-only Adapter
  → Ollama POST /api/generate
  → actual model-generated JSON
  → KJ Atlas parser
```

AdapterはKJ Atlasが作ったpromptをそのままmodelへ渡します。grouping候補の意味内容をAdapterで作成・補正していません。

OllamaではJSON形式の出力を安定して受け取るため、transport-localな設定として`format = json`を使いました。これはSOZAのUniversal Contractではありません。

## 5. Actual inferenceの実行結果

### Run 33596839607

- task: `suggest_card_groups`
- model: `qwen2.5:0.5b`
- prompt SHA-256: `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`
- `ollama_done`: `true`
- `ollama_done_reason`: `stop`
- `prompt_eval_count`: `196`
- `eval_count`: `78`
- `load_duration`: `1573025931` ns
- `total_duration`: `8008415140` ns

### Run 33608342203

- task: `suggest_card_groups`
- model: `qwen2.5:0.5b`
- prompt SHA-256: `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`
- `ollama_done`: `true`
- `ollama_done_reason`: `stop`
- `prompt_eval_count`: `196`
- `eval_count`: `83`
- `load_duration`: `1242363571` ns
- `total_duration`: `7197821634` ns

両runとも、事前に定めた最低条件である次の三点を満たしました。

```text
ollama_done = true
prompt_eval_count > 0
eval_count > 0
```

したがって、単なるmodel processの起動ではなく、**promptの評価とtoken生成を伴うactual inferenceが実行された**と判定します。

`eval_count`やdurationの一致は要求しません。これらは実行時の観測値であり、同じ値を再現することをCognitive Methodの意味契約には含めないためです。

これらのOllama固有fieldはintegration Evidenceであり、SOZAのUniversal Cognitive Method Contractへ追加しません。

## 6. KJ Atlasによるresponse受理

両runで、actual modelは二つの在宅勤務カードを一つのgroup候補として返しました。KJ Atlasがfilteringとresponse validationを行った後の結果では、次を確認しています。

- `groups`は空ではない。
- `c-remote-time`と`c-remote-load`が同一group候補に含まれた。
- `holdState = held`の`c-held`は`excludedCardIds`へ分離された。
- `truncated = false`だった。

今回のmodelはgroup labelとして「生活習慣」を生成しました。rationaleも両runで同じ内容になりましたが、この再現をmodel品質やKJ法上の妥当性の根拠にはしません。

ここで確認したのは、**actual modelが生成したJSONをKJ Atlas自身の既存parser / filtering経路が受理し、Method responseとして成立させられたこと**です。

## 7. model品質との境界

今回のrunが成功しても、model出力の認知的品質を評価済みとは扱いません。

```text
actual model inference succeeded
  != grouping quality satisfied
  != KJ-method quality satisfied
  != Recommendation
  != Decision
```

特に今回のgroup labelを人間のKJ法実践と比較して高品質だと評価する根拠はありません。小型modelで既存実行経路が成立したことと、そのmodelが実用上十分なCognitive Method Realizationであることは別です。

model品質を扱う場合は、semantic execution conformanceとは分離した評価系を用意します。

## 8. SOZAへ戻した結果

actual model-backed KJ Atlas responseについて、M1aと同じSOZA mapping boundaryを再利用しました。

両runで次がsuccessしています。

1. `go test ./livemethodintegration -count=1`
2. actual resultを入力した`TestLiveKJAtlasMethodExecution`

KJ Atlas固有JSONはopaqueな`not_verified` Method outputとして保持し、existing Cognitive Method Applicationからoutput / provenanceを参照します。

```text
actual model output
  → KJ Atlas Method response
  → opaque SOZA Method output
  != SOZA Recommendation
  != SOZA Decision
```

今回の成立によってgrouping候補をRecommendationやDecisionへ自動昇格させていません。

## 9. E3b-P2統合後の再実証が示す範囲

PR #50は、E3b-P2 fixed-artifact actual TEI CLI Evidenceが`develop/v0.2.0`へ統合された後の基線から作り直しました。Run `33608342203`でM1b経路を再実行し、P2側の正本を保持した状態でもM1bが成立することを確認しています。

```text
P2-integrated baselineでM1b再実行 PASS
  != P2とM1bが一つのruntimeへ統合された
  != arbitrary Provider / Method combination proven
  != Operational portability
```

P2とM1bは異なるEvidence trackです。両方が同じrepository基線に存在できることと、それらを組み合わせたproduction operationが成立することを混同しません。

## 10. Provenanceについて今回分かったこと

M1bでは、少なくとも次のidentityを区別して追跡する必要性が実行上明確になりました。

- Cognitive Method source: KJ Atlas repository / commit
- inference runtime: Ollama version
- model artifact: model tag / observed model ID
- actual invocation: prompt digestとinference counters

ただし、今回だけを根拠にこれらを新しいUniversal Provenance fieldへ昇格させません。

model / runtime version交換をまたぐhistorical reconstructionに必要な最小Provenanceは、今回得たEvidenceと今後のversion交換実証を入力として検討します。

## 11. Evidence state

- E3b-M1a live KJ Atlas + deterministic model stub: **Scoped Executable Evidence available**
- actual Ollama runtime acquisition: **Verified in Runs 33596839607 / 33608342203**
- actual `qwen2.5:0.5b` acquisition / identity check: **Verified in Runs 33596839607 / 33608342203**
- actual model inference: **Verified in Runs 33596839607 / 33608342203**
- KJ Atlas acceptance of actual model output: **Verified in Runs 33596839607 / 33608342203**
- SOZA Method Application mapping: **Verified in Runs 33596839607 / 33608342203**
- E3b-M1b actual model-backed execution: **Scoped Executable Evidence available**
- model output quality: **Not Evaluated**
- KJ-method outcome quality: **Not Evaluated**
- E3b-P2 actual TEI: **Scoped Executable Evidence available on its separate fixed-artifact track**
- E4 Operational portability: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 12. v0.2.0との関係

v0.2.0のsupported Realization / Provider exchange scopeはE3aまでです。

M1bはrelease後に得られたScoped Executable Evidenceであり、公開済みv0.2.0のsupported scopeやRelease Evidenceを遡及的に広げません。

```text
post-release E3b-M1b Evidence exists
  != v0.2.0 supported scope expanded
  != v0.2.0 Release Evidence expanded
```

## 13. 次の検討点

M1bによってactual model executionの成立自体は確認できました。次に残る論点は、少なくとも次です。

- model versionを交換したときに、historical Method Applicationをどのidentityまで追跡できれば十分か。
- inference runtimeの変更とmodel artifactの変更をProvenance上どう分けるか。
- model品質を評価する場合、semantic execution Evidenceとどのように別系統で管理するか。
- 同一Method Definitionに対して複数model Realizationを交換する実証をどう設計するか。
- E4 Operational portabilityで、実環境の継続利用をどの観測値で確認するか。

これらはM1bの成立を遡って未成立にするものではありません。次段階のOpen Questionとして扱います。

## 14. 自然な日本語レビュー

ISSUE-000066、E3b-M1a Evidence、E3b-P2 fixed-artifact Evidence、current Cognitive Method Contract、KJ Atlas固定revisionの`local` Provider境界、M1b専用workflow、integration-only Ollama Adapter、Runs `33596839607` / `33608342203`の実行ログ、Product Milestone、Realization / Provider Exchange、Value Traceability、上流計画を照合しました。

実証前に置いた成功条件へ実行結果を一つずつ対応させ、actual model取得、actual inference、KJ Atlasによるresponse受理、SOZAへのmappingがskipなしで成立した範囲だけをScoped Executable Evidenceへ更新しました。一方、実際に生成されたgroup labelの妥当性を含むmodel品質やKJ法としての成果品質は評価しておらず、Recommendation / Decisionにも昇格させていません。

E3b-P2統合後の基線で再実行できたことも、任意version互換性やOperational portabilityへは拡張していません。意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。