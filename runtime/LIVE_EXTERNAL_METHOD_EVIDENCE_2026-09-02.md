# Live External Cognitive Method Evidence — 2026-09-02

状態: **Scoped Executable Evidence**  
対象: **PMS-06 / E3b-M1a live KJ Atlas process + deterministic model stub**

## 1. この文書の役割

この文書は、current plan上の`ISSUE-000062`で扱う最初のlive external Cognitive Method integrationについて、**実際に確認できたことと、まだ確認していないことを分けて記録するEvidence文書**です。

本作業はPR #38の開始時点では`ISSUE-000061`として実施されました。その後、並行開発のPR #39が先にmergeされ、current `develop/v0.2.0`では`ISSUE-000061`がTEI executable注入境界の正本となりました。このため、本作業は一意性を保つため`ISSUE-000062`へ改番しています。旧CI logに現れる`ISSUE-000061`は改番前の歴史的な参照です。

今回の実証では、SOZAとは別repositoryで開発されているKJ Atlasを固定commitから取得し、KJ AtlasのFastAPI backendとmodel processをSOZAとは別processとして実際に起動しました。そのうえで、KJ Atlas自身が提供する`POST /ai/suggest-card-groups`をHTTP経由で呼び、返されたgrouping候補をSOZAの既存Cognitive Method Applicationへ結び付けられることを確認しました。

一方、model processにはKJ Atlas repositoryに含まれる決定的mockを使っています。このため、今回の結果を実外部AI modelの接続、model品質、KJ法としての成果品質、E3b-M1全体、Operational portability、Product Releaseへ拡張しません。

```text
E3b-M1a live KJ Atlas process + deterministic model stub
  != E3b-M1b live external model-backed KJ execution
```

## 2. 実際に通した実行経路

専用`External Method Integration E3b` workflowでは、次の経路を実際に実行しました。

```text
SOZA GitHub Actions runner
        │
        ├─ checkout pinned hat47x/kj-atlas commit
        │
        ├─ install KJ Atlas backend
        │
        ├─ Alembic migration → SQLite
        │
        ├─ start deterministic model stub process
        │
        ├─ start KJ Atlas FastAPI process
        │
        └─ HTTP POST /ai/suggest-card-groups
                    │
                    ▼
           KJ Atlas LLM input IR / SafeMode
                    │
                    ▼
           KJ Atlas grouping response
                    │
                    ▼
        SOZA reference Adapter boundary
                    │
                    ├─ opaque Method output (not_verified)
                    ├─ opaque Provenance
                    └─ current Cognitive Method Application
```

KJ Atlas sourceは次へ固定しました。

- repository: `hat47x/kj-atlas`
- commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- entry point: `POST /ai/suggest-card-groups`

このcommitはGitのcommit SHAです。tree SHAをsource revisionとして代用していません。

## 3. KJ Atlas側で確認したこと

実行requestには、人間がreview済みのカードを3件渡しました。そのうち1件は`doc.cards`側で`holdState = held`としました。

実際のresponseは次の性質を持ちました。

- grouping候補が返る。
- held card `c-held`は`excludedCardIds`へ入り、grouping候補から除外される。
- `truncated`は`false`である。

これは単なるhealth checkではありません。KJ Atlasのcurrent request model、LLM input IR、SafeModeによるhold-state filtering、local model routing、response filteringを含む実処理経路を通しています。

ただし、grouping内容そのものはdeterministic model stubが生成しています。したがって、「得られたgroupingが認知的に優れている」「実AI modelでも同じ結果が得られる」とは評価しません。

## 4. SOZA側へ戻した意味

KJ Atlas固有のresponse shapeをSOZAのUniversal Cognitive Method Contractへ昇格させていません。

```text
KJ Atlas response shape
  != SOZA Universal Cognitive Method Contract
```

reference Adapterは、version固定したKJ Atlas responseについて最小限のshapeだけを検査します。その後、responseのJSON内容をopaqueなMethod outputとして保持し、statusを`not_verified`とします。

`not_verified`は「捨てる」という意味ではありません。SOZAがそのopaque payloadの意味をUniversal Contractとして理解・検証済みだとは宣言しない、という境界です。

また、次のProvenanceをopaque recordとして保持します。

- source repository
- source commit
- entry point
- result SHA-256

Cognitive Method Applicationは、既存Contractの`method_ref`、`realization_ref`、`output_refs`、`provenance_refs`を使ってこれらを参照します。

## 5. Recommendation / Decisionへの非昇格

KJ Atlasが返すcard grouping候補はCognitive Methodの出力です。それだけでSOZAのRecommendationでもDecisionでもありません。

```text
grouping suggestion
  != Recommendation
  != Decision
```

reference probeではMethod Applicationだけを成立させ、RecommendationやDecision Memoryを自動生成しないことをtestで確認しました。

この分離により、KJ Atlasやmodelを交換した後に別のgrouping候補が得られても、それだけを理由にhistorical Decisionを書き換えません。

## 6. Negative caseと実装中に見つかった境界

### 6.1 invalid result / duplicate target

通常のGo testでは少なくとも次を確認しています。

- 必須の`groups`がないresponseを受理しない。
- group labelやcard IDの空値を受理しない。
- output logical refが既存recordと衝突する場合、Method ApplicationやProvenanceを部分追加しない。
- failure前後でcanonical digestが変わらない。

今回使った一時storeによる事前検査はreference probeの安全策です。production transaction guaranteeを定義するものではありません。

### 6.2 初回live runでの422

最初の専用workflow Run `33571948264`では、KJ Atlasのcheckout、backend install、migration、model/backend process起動までは成功しましたが、actual grouping requestがHTTP 422で拒否されました。

原因は、top-level `cards`の要素へ`holdState`を渡したことです。KJ Atlasの`SuggestCardGroupsRequest.cards`は`_CardRef`であり、`extra=forbid`です。`holdState`は`doc.cards`側で表現されます。

そこでtop-level cardから`holdState`を外し、`doc.cards`には残しました。これはKJ AtlasのSafeMode / IR契約を弱めた修正ではなく、current契約に合わせてSOZA側probeを修正したものです。

### 6.3 JSONのbyte一致を要求しすぎたtest

二回目のRun `33572079736`では、KJ Atlasのactual HTTP grouping自体は成功しましたが、SOZA側testが失敗しました。

原因は、opaque JSONをCanonicalStoreから再読した際にも、元responseの空白や改行までbyte-for-byte一致することを要求していたためです。CanonicalStoreはJSONを再serializeするので、表現上の空白は正規化されます。

SOZAが今回守るべき境界は、KJ Atlas responseをUniversal意味として推測せず`not_verified`のopaque outputとして保持し、JSON内容を失わないことです。空白まで同一のsource bytesを保存することではありません。

そのためtestをJSON意味等価の検査へ修正しました。source bytesの完全同一性が将来必要なら、Semantic Interchange上のopaque payloadとは別に、明示的なartifact / exact-binding要件として検討します。

## 7. Executable Evidence

改番前の修正後head `078b33e29272668a7ed2074e23e18c91225e1832`では、次を確認しました。

- External Method Integration E3b Run `33572160458`: **success**
  - pinned KJ Atlas checkout: success
  - backend install: success
  - SQLite migration: success
  - deterministic model stub process start: success
  - KJ Atlas FastAPI process start: success
  - actual HTTP grouping: success
  - held-card filtering確認: success
  - SOZA mapping boundary tests: success
  - actual external result → Method Application mapping: success
- Semantic Runtime Conformance Run `33572160466`: **success**
- Plan integrity Run `33572160460`: **success**
- External Integration E3a Run `33572160463`: **success**
- External Integration E3b Provider Run `33572160510`: **success**
- Local Package Artifact Run `33572160459`: **success**

さらに改番前検査点 `44adf21ebfa38d976560514360eebdbbf08cbc25`でも、External Method Integration E3b Run `33572621975`を含む実装・回帰系CIはsuccessしました。同じ検査点のRelease Candidate Gate Run `33572621894`だけは、当時の本作業Issueが`In Progress`だったためGate 9でfailureしました。

これはM1aの実行失敗ではなく、candidate policyの未解決Issue blockerが機能した結果です。current baseへ載せ直した状態では、TEI境界の`ISSUE-000061`と本作業の`ISSUE-000062`を一意に分け、両者をResolvedとしてGate 9を再検査します。

## 8. Evidenceの読み方

今回成立したのはE3b-M1aに限ったScoped Executable Evidenceです。

```text
E3b-M1a PASS
  != live external AI/model quality proven
  != E3b-M1b PASS
  != live TEI process / service PASS
  != production credential portability
  != production retry / rate-limit / circuit-breaker design
  != E4 Operational portability
  != Product Release / Release Evidence
  != Adoption / Outcome Evidence
```

特に、mock modelが返したgrouping内容を「KJ法として正しい」「認知的に高品質」と評価していません。今回確認したのは、独立した実KJ Atlas processの処理経路と、SOZAのsemantic boundaryへの接続です。

## 9. Requirement / Scenario再監査

新しいStable Requirement / Scenarioは追加しません。

今回の実証で確認したfailure boundaryは、既存の次で表現できます。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Cognitive Methodを交換可能にする
- REQ-0005 — historical Decisionを再構成できる
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

KJ Atlas、FastAPI、HTTP、SQLite、mock modelという現在のRealizationだけを理由に、新しいProduct Requirementを作りません。

## 10. 次に残るE3b

少なくとも次が残っています。

- E3b-M1b: 実外部model-backed KJ execution
- E3b-P2: actual TEI process / service integration
- private credentialの扱い
- model / Method version change時のProvenanceとhistorical reconstruction
- network degradation / rate limit
- formal Method / Provider integration protocolを本当に必要とするかの再判断

これらはM1aの実装をそのまま標準化せず、対象ごとに必要な意味差を確認して進めます。

## 11. Natural Japanese review

PMS-06、`product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`、ISSUE-000057 / 000058 / 000060 / 000061 / 000062、current Cognitive Method Contract、`runtime/go/interactionprobe`、`runtime/go/livemethodintegration`、KJ Atlas固定commitのbackend README、request model、LLM input IR integration test、KJ session E2E、PR #38のactual workflow、current baseへ先行mergeされたPR #39のTEI境界を照合した。KJ Atlas本体のlive実行とdeterministic model stubの生成品質を分離し、external Method output、Recommendation、Decisionを混同しない境界を確認した。また、実装中に発生した422とJSON byte一致testの失敗、並行開発によるIssue番号衝突を、Evidence強度を過大化せず現在の意味境界へ修正した経緯として残した。そのうえで、実証内容、negative case、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
