# ISSUE-000066: 実モデルを用いたCognitive Method実行を検証する

Status: **Open**  
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

最初の実証では次を用いる。

- Inference runtime: Ollama `0.32.14`
- Model: `qwen2.5:0.5b`
- Expected Ollama model ID prefix: `a8b0c5157701`
- Model size: 約398 MB
- Execution: GitHub Actions runner上のactual local inference

このmodel選択はM1bの最初の実証条件であり、SOZAの標準model、推奨model、品質基準ではない。

小型modelを選ぶ理由は、GitHub Actions上で資格情報なしにactual inferenceを再現しやすくし、model接続成立とmodel品質を分離するためである。

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

M1bでは、`prompt_eval_count > 0`かつ`eval_count > 0`をactual inference成立の最低条件とする。

これらのOllama固有fieldはintegration Evidenceであり、SOZA Universal Cognitive Method Contractではない。

## Workflow

`.github/workflows/external-model-method-integration-e3b-m1b.yml`で次を一続きに実行する。

1. SOZAをcheckoutする。
2. 固定commitのKJ Atlasをcheckoutする。
3. Ollama `0.32.14`を取得する。
4. Ollama processを起動する。
5. `qwen2.5:0.5b`を取得する。
6. `ollama list`でmodel ID prefixを確認する。
7. KJ Atlas backendをinstallし、SQLite schemaをmigrationする。
8. integration-only Ollama Adapterを起動する。
9. KJ Atlas FastAPI backendを別processとして起動する。
10. actual `POST /ai/suggest-card-groups`を呼ぶ。
11. grouping responseが成立していることを確認する。
12. actual model inference countersを確認する。
13. existing SOZA Method mapping boundary testを再実行する。
14. actual model-backed resultを既存Cognitive Method Applicationへ戻す。

## Requirement / Scenario監査

新しいStable Requirement / Scenarioは追加しない。

今回のProduct failureは、既存の次で表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0008 — Cognitive Methodの実現手段を意味から分離する
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

actual model接続によって既存Requirementでは表せない独立したProduct failureが見つかった場合だけ、Candidate Requirementとして上流へ戻す。

## Provenanceの停止線

M1bでは、KJ Atlas source identityとactual model identityの双方をEvidenceとして追跡する。

ただし、今回だけを根拠にmodel repository、Ollama tag、Ollama model ID等をUniversal Provenance fieldへ昇格させない。

model version交換をまたぐhistorical reconstructionに必要な最小Provenanceは、M1bの実行結果を入力として別途検討する。

## Non-goals / 未検証範囲

- `qwen2.5:0.5b`の生成品質を評価すること
- KJ法としてのgrouping品質をSatisfiedとすること
- OllamaをSOZAまたはKJ Atlasの標準runtimeへ固定すること
- `POST /generate`をSOZAのUniversal integration protocolへ昇格させること
- model provider固有fieldをUniversal Contractへ追加すること
- actual TEI E3b-P2を検証すること
- E4 Operational portabilityを検証すること
- production credential / model distribution policyを決めること
- v0.2.0 supported scopeを遡及的に拡張すること
- Product Release / Operational / Adoption・Outcome Evidenceを成立させること

## 完了条件

- [x] actual model用integration-only Adapterを追加する。
- [x] KJ Atlas固定revisionとactual model executionを同一workflowへ置く。
- [x] Ollama runtime versionとmodel identityの期待値を明示する。
- [x] model process起動とactual inferenceを別条件として確認する。
- [x] model出力品質をM1b execution Evidenceから分離する。
- [ ] actual GitHub Actionsでmodel取得を成功させる。
- [ ] actual inferenceで`prompt_eval_count > 0`を確認する。
- [ ] actual inferenceで`eval_count > 0`を確認する。
- [ ] KJ Atlas `POST /ai/suggest-card-groups`がactual model outputを受理する。
- [ ] actual resultをSOZAの既存Cognitive Method Applicationへ戻す。
- [ ] M1b Evidence文書をactual runへ同期する。
- [ ] Product Milestone / Product入口 / 上流計画 / Plan台帳を同期する。
- [ ] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。
- [ ] merge後の`develop/v0.2.0`で回帰CIを確認する。

## Evidence state

- E3b-M1a live KJ Atlas + deterministic model stub: **Scoped Executable Evidence available**
- E3b-M1b actual model-backed execution: **Not Yet Verified**
- actual model output quality: **Not Evaluated**
- KJ-method outcome quality: **Not Evaluated**
- E3b-P2 actual TEI: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- actual modelは起動するがKJ Atlas promptから有効なJSONを生成できない。
- actual model outputをKJ Atlas parserが受理できない。
- model runtime固有の補正をMethod意味論へ混ぜないと成立しない。
- model identityを追跡しないとhistorical reconstruction上の重大な欠落が生じる。
- actual model executionによってM1aでは見えなかったtimeout、resource、process lifecycle上の問題が確認される。

## 自然な日本語レビュー

PMS-06、ISSUE-000064、current Cognitive Method Contract、KJ Atlas固定commitの`local` Provider / `POST /generate`境界、M1a workflow、Ollamaのactual model execution条件を照合した。今回の焦点をmodel品質ではなく「実際に推論するmodel artifactを通しても、KJ AtlasのMethod出力を既存SOZA境界へ戻せるか」に限定している。

Adapterに意味判断やgrouping補正を持たせず、actual inferenceの成立とmodel出力品質を分離した。意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
