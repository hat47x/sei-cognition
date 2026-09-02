# ISSUE-000066: 実モデルを用いたCognitive Method実行を検証する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0017, ADR-0021, ADR-0025**  
Updated: 2026-09-02

## Goal

PMS-06のE3b-M1bとして、E3b-M1aで確認したKJ Atlasのlive Cognitive Method経路を、決定的model stubではなく**実際に推論するmodel artifact**へ接続し、同じSOZAの意味境界へ戻せることをScoped Executable Evidenceとして確認する。

今回の中心はmodel品質の評価ではない。次を明確に分ける。

```text
KJ Atlas processが動くこと
  != model processが実際に推論すること
  != model出力の品質
  != Cognitive Methodとしての成果品質
  != Recommendation
  != Decision
```

## E3b-M1aから引き継ぐ境界

E3b-M1aでは、固定revisionのKJ Atlas FastAPI backendと、KJ Atlas repositoryに含まれるdeterministic model stubを別processとして起動し、actual `POST /ai/suggest-card-groups`の結果を既存Cognitive Method Applicationへ戻せることを確認した。

M1bではKJ AtlasのMethod surfaceを変えない。

- Repository: `hat47x/kj-atlas`
- Commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Entry point: `POST /ai/suggest-card-groups`
- KJ Atlas Provider kind: `local`
- KJ Atlas model boundary: `POST /generate`

この固定により、M1aとM1bの差を主としてmodel executionへ限定する。

## 最初のactual model

最初の実証では次を用いた。

- Inference runtime: Ollama `0.32.14`
- Model: `qwen2.5:0.5b`
- Observed Ollama model ID: `a8b0c5157701`
- Observed model size: `397 MB`
- Execution: GitHub Actions runner上のCPU-only actual local inference

このmodel選択はM1bの最初の実証条件であり、SOZAの標準model、推奨model、品質基準ではない。

小型modelを選んだ理由は、GitHub Actions上で資格情報なしにactual inferenceを再現しやすくし、model接続成立とmodel品質を分離するためである。

## Adapter境界

KJ Atlasの`local` Providerは次の形で外部model processを呼ぶ。

```text
POST /generate
{
  task,
  prompt,
  temperature,
  max_tokens,
  model
}
```

応答は次である。

```text
{"text": "<model-generated JSON>"}
```

`runtime/integration/e3b_m1b_ollama_adapter.py`は、この既存境界をOllamaの`/api/generate`へ変換するintegration-only Adapterとする。

Adapterは次を行わない。

- KJ Atlasのprompt内容を書き換える。
- grouping候補をAdapter側で生成する。
- modelが返したgroup labelやcard IDを補正する。
- SOZAのRecommendation / Decisionを生成する。
- Ollama固有fieldをSOZA Universal Contractへ追加する。

Ollama側では`format = json`を用いてJSONとしての出力形式を拘束する。ただし、groupingの意味内容はactual modelが生成する。

## Actual inferenceの確認

単にOllama processが起動しているだけではM1bのEvidenceにしない。

Adapterは各actual inferenceについて、少なくとも次をintegration Evidenceとして記録する。

- model ID
- task
- prompt SHA-256
- Ollama `done`
- `done_reason`
- `prompt_eval_count`
- `eval_count`
- `total_duration`
- `load_duration`

M1bでは、`prompt_eval_count > 0`かつ`eval_count > 0`をactual inference成立の最低条件とした。

先行PR #48のRun `33596839607`では`prompt_eval_count = 196`、`eval_count = 78`を観測した。さらにE3b-P2統合後の最新develop基線から作り直したPR #50のRun `33608342203`でも、次を観測した。

- `ollama_done = true`
- `done_reason = stop`
- `prompt_eval_count = 196`
- `eval_count = 83`
- prompt SHA-256: `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`

したがって、model processの起動だけではなく、prompt評価とtoken生成を伴うactual inferenceが、P2統合後の基線でも成立したと判断する。

`eval_count`の差は生成token数の観測値であり、同一値であることをM1bの要件にはしない。これらのOllama固有fieldはintegration Evidenceであって、SOZA Universal Cognitive Method Contractではない。

## 実行結果

PR #48の先行Run `33596839607`と、最新develop基線から再構成したPR #50のRun `33608342203`で、いずれも次をskipなしで成功させた。

1. 固定commitのKJ Atlasを取得した。
2. Ollama `0.32.14`を導入した。
3. `qwen2.5:0.5b`を取得し、model IDを確認した。
4. KJ Atlas backendをinstallし、SQLite schemaをmigrationした。
5. integration-only Ollama AdapterとKJ Atlas backendを別processとして起動した。
6. actual `POST /ai/suggest-card-groups`を呼んだ。
7. actual model inference countersが成立条件を満たすことを確認した。
8. KJ Atlasがactual model outputを受理し、grouping responseを生成した。
9. existing SOZA Method mapping boundary testを再実行した。
10. actual model-backed resultを既存Cognitive Method Applicationへ戻した。

両runとも、KJ Atlasは二つの在宅勤務カードを一つのgroup候補として返し、`holdState = held`のカードを`excludedCardIds`へ分離した。実際に生成されたgroup labelやrationaleの品質は、このIssueの完了条件には含めない。

## merge後の回帰CI

PR #50を`develop/v0.2.0`へ統合したmerge commit `51ec4502bf0a34097f975a5445069c26ea831f32`について、merge後のpush CIを確認した。

同commitでは9系統のworkflowが実行され、いずれもsuccessした。M1b固有の`External Model-backed Method E3b M1b` Run `33609470323`でも、実モデルを介したKJ AtlasのMethod実行経路がmerge後のdevelop上で成立している。

あわせて、Plan integrity Run `33609470271`、Semantic Runtime Conformance Run `33609470262`、External TEI Integration E3b P2 Run `33609470337`、Release Candidate Gate Run `33609470278`を含む既存の回帰検査もsuccessした。

これにより、M1bの変更を`develop/v0.2.0`へ統合した後も、既存のPlan、Semantic Runtime、E3b-P2、release境界を壊していないことを確認した。

このmerge後CIの成立は、model出力品質、KJ法としての成果品質、任意のmodel / runtime versionとの互換性、E4 Operational portability、Operational Evidence、Adoption / Outcome Evidenceを新たに成立させるものではない。また、公開済みv0.2.0のsupported scopeを遡及的に広げるものでもない。

## Requirement / Scenario監査

新しいStable Requirement / Scenarioは追加しない。

今回のProduct failureは、既存の次で表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0008 — Cognitive Methodの実現手段を意味から分離する
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

actual model接続によって既存Requirementでは表せない独立したProduct failureは、今回の実証では確認していない。そのため、新しいRequirementは追加しない。

## Provenanceの停止線

M1bでは、KJ Atlas source identityとactual model identityの双方をEvidenceとして追跡した。

少なくとも次のidentityを区別する必要性が、実行上は明確になった。

- Cognitive Method source: KJ Atlas repository / commit
- inference runtime: Ollama version
- model artifact: model tag / observed model ID
- actual invocation: prompt digestとinference counters

ただし、今回だけを根拠にmodel repository、Ollama tag、Ollama model ID等をUniversal Provenance fieldへ昇格させない。

model / runtime version交換をまたぐhistorical reconstructionに必要な最小Provenanceは、今回のEvidenceと今後のversion交換実証を入力として別途検討する。

## Non-goals / 未検証範囲

- `qwen2.5:0.5b`の生成品質を評価すること
- KJ法としてのgrouping品質をSatisfiedとすること
- OllamaをSOZAまたはKJ Atlasの標準runtimeへ固定すること
- `POST /generate`をSOZAのUniversal integration protocolへ昇格させること
- model provider固有fieldをUniversal Contractへ追加すること
- E4 Operational portabilityを検証すること
- production credential / model distribution policyを決めること
- 任意のmodel / runtime versionとの互換性を保証すること
- v0.2.0 supported scopeを遡及的に拡張すること
- Product Release / Operational / Adoption・Outcome Evidenceを成立させること

E3b-P2 actual TEI CLIについては、別Issue / Evidence trackでfixed-artifact Scoped Executable Evidenceが成立しており、本Issueの成功条件とは分ける。

## 完了条件

- [x] actual model用integration-only Adapterを追加する。
- [x] KJ Atlas固定revisionとactual model executionを同一workflowへ置く。
- [x] Ollama runtime versionとmodel identityの期待値を明示する。
- [x] model process起動とactual inferenceを別条件として確認する。
- [x] model出力品質をM1b execution Evidenceから分離する。
- [x] actual GitHub Actionsでmodel取得を成功させる。
- [x] actual inferenceで`prompt_eval_count > 0`を確認する。
- [x] actual inferenceで`eval_count > 0`を確認する。
- [x] KJ Atlas `POST /ai/suggest-card-groups`がactual model outputを受理する。
- [x] actual resultをSOZAの既存Cognitive Method Applicationへ戻す。
- [x] M1b Evidence文書をactual runへ同期する。
- [x] Product Milestone / Product入口 / Realization / Provider Exchange / Value Traceability / 上流計画 / Plan台帳を同期する。
- [x] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。
- [x] merge後の`develop/v0.2.0`でM1b workflowを含む回帰CIを確認する。

## Evidence state

- E3b-M1a live KJ Atlas + deterministic model stub: **Scoped Executable Evidence available**
- E3b-M1b actual model-backed execution: **Scoped Executable Evidence available in Runs 33596839607 / 33608342203**
- latest-develop rebaseline execution before merge: **Verified in Run 33608342203**
- merge後の`develop/v0.2.0`回帰: **Verified in Run 33609470323**
- actual model output quality: **Not Evaluated**
- KJ-method outcome quality: **Not Evaluated**
- E3b-P2 actual TEI: **Scoped Executable Evidence available on its separate fixed-artifact track**
- E4 Operational portability: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Resolution

E3b-M1bとして定めた完了条件は、PR #48 / #50のactual model-backed executionと、PR #50のmerge後に`develop/v0.2.0`で実行されたRun `33609470323`を含む回帰CIによってすべて満たされた。

このため、本IssueをResolvedとする。今後、model / runtimeの交換、historical reconstructionに必要な最小Provenance、model品質の評価、E4 Operational portabilityなどを検証する場合は、本Issueを再び未完了へ戻すのではなく、それぞれの目的とEvidence境界を持つ後続課題として扱う。

## Reopen / escalation条件

- actual modelは起動するがKJ Atlas promptから有効なJSONを生成できなくなる。
- actual model outputをKJ Atlas parserが受理できなくなる。
- model runtime固有の補正をMethod意味論へ混ぜないと成立しなくなる。
- model identityを追跡しないとhistorical reconstruction上の重大な欠落が生じる。
- actual model executionによってM1aでは見えなかったtimeout、resource、process lifecycle上の問題が確認される。
- 別model / runtimeへ交換したとき、現在のProvenanceでは過去Applicationを十分に区別できないことが分かる。

## 自然な日本語レビュー

PMS-06、ISSUE-000064 / 000065、current Cognitive Method Contract、KJ Atlas固定commitの`local` Provider / `POST /generate`境界、M1a workflow、M1b workflow、integration-only Ollama Adapter、Runs `33596839607` / `33608342203`、merge後のRun `33609470323`、Product Milestone、Product入口、Realization / Provider Exchange、Value Traceability、上流計画を照合した。

実証前に置いた成功条件とactual runを一つずつ対応させ、actual model取得、actual inference、KJ Atlasによるresponse受理、SOZAへのmapping、merge後のdevelop回帰が成立した範囲だけをScoped Executable Evidenceへ更新した。一方、実際に生成されたgroup labelやrationaleの妥当性を含むmodel品質、KJ法としての成果品質は評価しておらず、Recommendation / Decisionにも昇格させていない。

E3b-P2統合後の基線とM1b統合後のdevelopでも同じ意味境界が保たれたことを確認したが、この再現結果を任意version互換性やOperational portabilityへは拡張しない。意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を読み直し、最終意味監査を実施した。
