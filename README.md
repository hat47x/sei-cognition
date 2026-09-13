# 井 / SEI Cognition

更新日: 2026-09-13  
状態: **v0.2.0 Local Reference Product Baseline released / development continues**

SEI Cognitionは、人間・AI・組織・既存システム・外部サービスが入れ替わっても、**何を見て、何を問い、何を根拠とし、何を決め、何を未解決として残したか**を失わないための、可搬な認知・意思決定基盤です。

中心にあるのは、workflowやAI agent runtimeを自前で囲い込むことではありません。実行手段が変わっても残るもの、すなわち意味、不確実性、判断、責任、Capability、Provenance、Semantic Lineageを扱います。

名前は易経の卦「井」から採っています。井は、汲んでも尽きず、誰が汲みに来ても同じ水を返す共有の泉です。町が移っても井戸は動かせないという卦の像が、実行手段も人も組織も入れ替わるなかで何を動かさずに残すのか、という本製品の立場に重なります。

## 1. 守る意味境界

この製品が最も避けたいのは、性質の違うものを同じ一つの記録へ潰してしまうことです。少なくとも次を同一視しません。

```text
Observation
  != Interpretation / Hypothesis
  != Recommendation
  != Decision
  != Authority
  != Action Intent
  != Execution
  != Business Outcome
```

観測したことと、そこから立てた解釈は違います。誰かが薦めたことと、実際に決めたことも違います。決めたことと、決める権限があったことも、実行したことも、業務上の結果が出たことも、それぞれ別です。これらが混ざると、後から「なぜそう決めたのか」へ戻れなくなります。

さらに、次の非同一性を守ります。

- `Unknown != No` — まだ分からないことを、否定として記録しません。
- `Conflict != latest-wins` — 食い違いを、新しい方の採用で消しません。
- `not observed != unavailable` — 観測していないことは、存在しないことではありません。
- `not_verified != failed` — 検証していないことは、失敗ではありません。
- `Capability != Provider` — 能力そのものと、それを提供する手段は別です。
- `Capability Definition != Capability Observation` — 定義と、実際に観測された状態は別です。
- `Matching != Decision` — 候補が合致したことは、決めたことではありません。
- `Pattern != Cognitive Method` — 見出したパターンと、手順として定めた方法は別です。
- `Method Application != Assurance` — 方法を適用したことは、品質の保証ではありません。
- `Logical Reference != Exact Historical Binding` — 論理的な参照と、当時の実体への束縛は別です。
- `Projection != Canonical Semantic Authority` — 読みやすく射影した表現は、正本ではありません。
- `Requirement != Acceptance Scenario != Test Case` — 要求と、受入シナリオと、テストは別の層です。
- `Semantic Contract != Representation Profile` — 意味の契約と、その表現形式は別のversion空間を持ちます。
- `Product access permission != semantic Responsibility / Authority` — 製品上の操作権限は、意味上の責任や権限ではありません。

## 2. Product Valueの見方

価値を単一のスコアへ還元しません。次の8軸で別々に確認します。

- V1 — Historical Reconstruction: 当時の根拠へ戻れること
- V2 — Semantic Separation: RecommendationとDecision等を取り違えないこと
- V3 — Revision Integrity: 後から得た情報で過去を書き換えないこと
- V4 — Provider Independence: 特定の提供者に意味を縛られないこと
- V5 — Uncertainty Preservation: 未解決を未解決のまま次へ渡せること
- V6 — Human / AI Readability: 人とAIの双方が同じ正本を読めること
- V7 — Progressive Explicitness: 必要な分だけ明示度を上げられること
- V8 — Execution Independence: 実行手段が変わっても意味が残ること

受入れの境界は`product/value/SEI_VALUE_ACCEPTANCE.md`、現在の追跡状態は`product/value/SEI_VALUE_TRACEABILITY.md`を正本とします。

## 3. Semantic ContractとRepresentation Profile

実装、Provider、Storage、versionをまたいで同じ意味として交換・検証する必要がある境界だけを、独立したContractとして固定しています。現在は5つです。

- `sei.semantic-reference/v1alpha1`
- `sei.decision-memory/v1alpha1`
- `sei.capability-observation/v1alpha1`
- `sei.cognitive-method/v1alpha1`
- `sei.semantic-interchange/v1alpha1`

意味をどう表現し、どう同一性を検証するかは、Contractとは別のversion空間で扱います。

- `sei.jcs+sha256/v1alpha1`
- `sei.raw-bytes+sha256/v1alpha1`

重要な概念であることが、そのままContract化の理由にはなりません。Contractを増やすこと自体は目的ではなく、実装やProviderをまたいで意味を固定する必要がある場合にだけ作ります。詳細は`contracts/CONTRACT_CATALOG.md`にあります。

現在のRequirementは`REQ-0001`〜`REQ-0022`、Acceptance Scenarioは`SCN-0001`〜`SCN-0018`です。

## 4. repositoryの構成

```text
product/       なぜ存在し、何を失ってはならないのか
requirements/  満たすべき要求と受入シナリオ
architecture/  現在の構造と境界
contracts/     実装をまたいで固定する意味の契約
fixtures/      契約を検証するための固定入力
runtime/       Go実装、Provider Adapter、probe、実行記録
evaluation/    評価と探索。まだ要求へ昇格していない領域
tools/         checkerと検証script
plan/          ADR、Issue、開発workflow
release/       release受入れとEvidence
```

正本の関係は上から下へ流れます。

```text
Product Value / Value Proposition / Product Shape
  ↓
Product Milestone
  ↓
Requirements / Acceptance Scenarios
  ↓
ADR
  ↓
Reference Architecture
  ↓
Semantic Contract / Representation Profile
  ↓
Schema / Fixture / Validator
  ↓
Runtime / Adapter / Probe / Evaluation
  ↓
Executable Evidence
  ↓
Release Candidate / Release Evidence
```

下位の実装や検証手段が、上位の意味を自動的に決めることはありません。実装の都合で意味を動かしたくなったときは、上位文書へ戻って、それが何を証明したEvidenceなのかを確認します。

## 5. Evidenceの読み方

達成状態を、次の5段階で区別します。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

設計として筋が通っていることと、実際に動いたことは別です。動いたことと、releaseできる状態であることも別です。さらに、継続的に運用できることと、利用者に価値が届いたことも、それぞれ別に確かめます。

現在は、v0.2.0 Local Reference Product BaselineについてRelease Evidenceまで成立しています。運用の継続性や、実利用で価値が届いたことを示すEvidenceはまだありません。

過去のPASSを現在のPASSとしても扱いません。

```text
historical PASS != current PASS
not_verified != failed
```

検証できなかった項目は`Not Yet Verified`のまま残します。GitHub Actionsは当面停止しており、必要なchecker、test、probeは変更範囲に応じてローカルで個別に実行します。実行方針は`plan/DEVELOPMENT_WORKFLOW.md`を正本とします。

## 6. 現在動かせるもの

限定されたExecutable Evidence、またはそれを再実行するための資産として、次があります。

**意味の読み取りと検証** — Go実装のsemantic runtime、Representation Verifier Registry、JSON Schemaとfixtureに対する検証器、Contract横断でbundle内のExact Bindingが整合しているかの確認。

**Providerとの接続** — 合成Providerに対するAdapter、別プロセスとして起動するRealization / Provider交換、versionを固定した外部artifactとの連携、公開Providerに対する実接続、固定artifactを用いた実TEI CLIとの連携。

**Cognitive Method** — 型付きruntime、決定論的なmodel stubを用いた連携、Ollamaを用いた実modelによる実行、成果品質を評価するための境界定義。

**製品としての通し確認** — end-to-endのSemantic Product Journey harness、人と機械の双方から同じ正本へ戻るProduct Interaction probe、単一node向けpackagingとresumeおよびStorage移行のprobe、Product AccessとCollaborationの責任分離probe。

**historical reconstruction** — model artifactを交換しても当時のApplicationを保持できること、Method Realizationのrevisionを可搬に再構成できること、固定modelの下でruntime versionを交換したときのScoped Executable Evidence。

これらはいずれも限定された範囲での実行結果です。release後に得たEvidenceを理由に、公開済みv0.2.0のsupport範囲を後から広げることはしません。v0.2.0がどこまでをsupported scopeとしたかは`release/v0.2.0/RELEASE_ACCEPTANCE.md`を正本とします。

## 7. v0.2.0 release

v0.2.0は、開発者と評価者が現在のProduct ValueとSemantic Contractを実際に確かめられる**Local Reference Product Baseline**としてreleaseしています。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- Local Reference PackageのSHA-256: `37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17`

releaseにあたっては、同じsource commitに対してPlan、Requirements、Contract、Representation Profile、semantic runtime、Projection評価、Local Reference Package、release policyをまとめて再検査しました。そのうえで、tag、source commit、GitHub Release、release asset、package digestを相互に照合しています。

```text
candidate PASS
  + exact tag binding
  + released artifact digest match
  → scoped Release Evidence Satisfied
```

これはproduction完成版を意味しません。

```text
v0.2.0 Release Evidence Satisfied
  != production readiness
  != Operational Evidence
  != Adoption / Outcome Evidence
```

このRelease Evidenceは当時のものとして確定しています。以降のcommitについては、必要なローカル検証を別途実行して判断します。詳細は`release/v0.2.0/`の受入れ、notes、Evidenceにあります。

## 8. SEI CognitionとTEI

鼎（TEI）はSEI Cognitionそのものではなく、SEI Cognitionから利用し得るCapability Providerの一つです。

```text
SEI Cognition = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI           = 実行可能な業務Capabilityを実現する一つの手段
```

関連製品であることだけを理由に、TEIへ優先度や信頼や権限を与えることはしません。TEI固有のApplication、Database、Release、Deploymentの構造を、SEI Cognitionの普遍的な意味核へ複製することもしません。

## 9. 読み進める順序

はじめて読む場合は、上位から下りるのが確実です。

1. `product/README.md` — なぜ存在し、何を失ってはならないのか
2. `requirements/README.md` — 何を満たすべきか
3. `architecture/README.md` — 現在どういう構造になっているか
4. `contracts/README.md` — 実装をまたいで何を固定しているか
5. `release/README.md` — どこまでreleaseとして成立しているか

現在進めている判断と作業は`plan/`にあります。ADRとIssueの現況は`plan/registry.yaml`、進め方は`plan/DEVELOPMENT_WORKFLOW.md`が正本です。各文書のStatusは、台帳ではなくその文書本文を正とします。

開発文書は、内容と構造を整えた後に、意味・仕様・留保・Evidenceの強さを変えないまま、自然な日本語となることを最重要視して全文をドラフトし直す工程を通します。詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`にあります。

## 10. Natural Japanese review

入口文書として何が必要かを問い直し、構成を作り直した。製品が何であるか、何を混同しないか、何をどこまで証明できているかを先に置き、個別のIssue進捗やADR採番範囲のような進行管理情報は`plan/`の正本へ委ねて本文から外した。過去の名称に関する記述も、改名の判断を記録したADRが正本であるため入口からは外している。

そのうえで、識別子を名詞として長く連結していた箇所と、milestone codeだけで内容を示していた箇所を、意味を落とさずに日本語の説明へ置き換えた。特に守る意味境界とEvidenceの5段階については、式だけに頼らず本文でも読めるようにした。

再ドラフトの前後で、非同一性の主張、v0.2.0のsupported scopeを後から広げないという留保、Release Evidenceが運用や利用者価値のEvidenceを意味しないこと、未検証を`Not Yet Verified`のまま残すという方針が変わっていないことを確認した。
