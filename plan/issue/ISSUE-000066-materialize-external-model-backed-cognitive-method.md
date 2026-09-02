# ISSUE-000066: external model-backed Cognitive Method executionを実証する

- Status: Open
- Priority: 1
- Related ADRs: ADR-0017, ADR-0021, ADR-0025
- Product Milestone: PMS-06

## 背景

ISSUE-000064では、固定revisionのKJ AtlasをSOZAとは別processとして起動し、`POST /ai/suggest-card-groups`を実行した結果を、SOZAのCognitive Method Applicationと`not_verified`なMethod outputへ写像するE3b-M1aを実証しました。

ただし、M1aでKJ Atlasが接続したmodel endpointはdeterministic model stubです。外部Cognitive Methodのprocess境界は実在化できていますが、実際の生成modelを介したMethod実行まではEvidence化していません。

本IssueではM1aの境界を保ったままmodel transportだけを実modelへ交換し、E3b-M1bとして次の経路を最小範囲で実証します。

```text
SOZAのsynthetic input
  → 固定revisionのKJ Atlas process
  → KJ AtlasのLLM provider boundary
  → 別processのactual model inference
  → KJ AtlasのMethod output
  → SOZA Cognitive Method Application
  → opaque / not_verified Method output
```

## 目的

固定revisionのKJ Atlasがactual model inferenceを伴って実行され、その結果を既存のSOZA Method境界を壊さずに取り込めることをScoped Executable Evidenceとして残します。

ここで確認するのは「実modelを含む外部Method executionの接続性」です。model出力の品質、KJ法としての妥当性、RecommendationやDecisionの正しさは評価対象にしません。

## 固定する外部source

- Repository: `hat47x/kj-atlas`
- Commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Method entry point: `POST /ai/suggest-card-groups`

M1aと同じsource revisionを使います。M1bのためにKJ Atlas source自体を書き換えません。

## 実証方法

CI runner上でOllamaをKJ Atlasとは別processとして起動し、`qwen2.5:1.5b`を実際に読み込んで推論させます。Ollamaが公開するOpenAI互換`/v1/chat/completions`を、固定revisionのKJ Atlasが持つ既存transportから呼び出します。

固定KJ Atlasでは、このOpenAI互換transportの実装名と`providerKind`が`deepseek`です。本Issueでは、この名称を実modelの提供主体と読み替えません。`deepseek`は固定source内のtransport実装名であり、今回のactual model runtimeはOllama、modelは`qwen2.5:1.5b`です。

modelをpullしただけでは実推論のEvidenceとしません。Method request前にmodelが未loadであることを確認し、request後に`ollama ps`でmodelがload済みとなったこと、KJ Atlasのprovider call countが増加したこと、Method request自体が成功したことを組み合わせて確認します。また、Ollamaのmodel一覧から解決されたdigestも記録します。

### 最初のGitHub Models probeについて

当初はGitHub Actionsの短命`GITHUB_TOKEN`とGitHub Modelsを使う案を実装し、Run `33608892506`でprobeしました。KJ Atlasの起動、`models: read`権限、provider設定までは成立しましたが、推論APIはHTTP 410を返しました。

調査の結果、GitHub Modelsは2026年7月30日にサービス自体が終了しており、推論APIも利用できないことをGitHub公式文書で確認しました。この経路は成立しない外部依存として撤回し、後続probeをOllamaへ切り替えます。HTTP 410をmodel品質やKJ AtlasのMethod失敗とは解釈しません。

## Evidenceとして確認すること

- [ ] 固定revisionのKJ Atlasが別processとして起動する。
- [ ] OllamaがKJ Atlasとは別processとして起動する。
- [ ] `qwen2.5:1.5b`のmodel digestを実行時に取得する。
- [ ] actual Method request前のKJ Atlas provider call countが0である。
- [ ] actual Method request前には対象modelがOllamaで未loadである。
- [ ] `POST /ai/suggest-card-groups`がactual model inferenceを経て成功する。
- [ ] request後のKJ Atlas provider call countが増加する。
- [ ] request後には対象modelがOllamaでload済みである。
- [ ] held cardがKJ AtlasのMethod outputで`excludedCardIds`へ保持される。
- [ ] actual Method outputを既存のSOZA `livemethodintegration`境界へ入力できる。
- [ ] SOZA側では結果をopaque / `not_verified` outputとして保持し、Recommendation / Decisionへ自動昇格させない。
- [ ] source repository / commit / entry point / result digestのProvenance境界を維持する。
- [ ] 対象CIがsuccessする。

## 明示的な停止線

```text
external Method process execution
  != external model invocation
  != model output quality
  != Recommendation
  != Decision
```

M1bでexternal model invocationが成立しても、次は主張しません。

- modelの回答内容が高品質であること
- KJ法として適切な島形成ができたこと
- 人間の探索や判断に実用上寄与したこと
- Method outputがRecommendationであること
- RecommendationやDecisionが正しいこと
- production向けmodel runtime / credential運用が成立したこと
- OllamaまたはQwen2.5がSOZAやKJ Atlasの標準Provider / 標準modelであること
- 固定KJ Atlas内の`deepseek`というtransport名が実際のProvider主体を意味すること
- v0.2.0のsupported scopeがE3b-M1bまで拡張されたこと
- Release / Operational / Adoption / Outcome Evidence

## Requirement / Scenarioの扱い

本Issueでは新しいStable Requirement / Scenarioを追加しません。

REQ-0001、REQ-0004、REQ-0005、REQ-0021、およびSCN-0005、SCN-0014、SCN-0018が保持している既存境界の上で、M1aより一段だけ実在性の高いEvidenceを追加します。実model接続のための特定runtime、model ID、transport実装をSOZA Universal Coreの要件へ昇格させません。

## 完了条件

固定revisionのKJ Atlasから別processのactual model inferenceを一度以上実行し、そのactual Method outputを既存SOZA Method mappingへ通したことをCI Evidenceで確認できた時点でResolvedとします。

model processの起動やmodelのpullだけでは完了としません。actual Method requestがmodel推論を経て成功しない場合は、Not Yet Verifiedの事実をそのまま残します。
