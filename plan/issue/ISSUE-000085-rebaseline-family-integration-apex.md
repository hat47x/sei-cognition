# ISSUE-000085: 製品ファミリーの統合の頂点に向けて、Product Value / Vision / Shapeを再基線化する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0018, ADR-0021, ADR-0035**  
Updated: 2026-09-27

## Goal

ADR-0035（Proposed）で提案した、SEIを製品ファミリーの「統合の頂点」とする位置づけと、価値の中心を「判断と認識のコミットメント」の台帳として言い直す提案を、**製品の所有者が項目ごとに採否を判断できる状態**にする。

完了時には、次が判別できることを目指します。

1. どの上位文書のどの節に、何を、なぜ加えたか。
2. 各項目が、既存のV1〜V8、Requirement、Contract、既存ADRと矛盾しないか。
3. 各項目について、所有者が採用、修正、却下のどれを選んだか。
4. 採否の結果に応じて、ADR-0035のStatusと関連文書が一致しているか。

このIssueは、ADR-0018 §7が求める明示的な再基線化の作業単位です。新しいValue Axis、Universal型、Stable Requirement、Contract versionは追加しません。

## Background

### 確認済みの事実

- SEIの既存のProduct文書は、趣旨と他製品との棲み分けだけを与えて生成AIが起草したものです。人による価値評価は、まだ行われていません。
- 2026-09-27に、生成AIによる価値と境界の評価を行いました。その記録は`product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md`にあります。
- 製品ファミリーは2026-09時点で7リポジトリです。各製品は、提案と決定の分離を独立に実装しています。
- `SEI_PRODUCT_SHAPE.md` §8.3はroutingをProduct / Profile / Provider-localに留める一方、`EMERGENT_COGNITIVE_ARCHITECTURE.md` §1はSEIをCognitive Control Planeとして描いています。
- ISSUE-000079で保留していたChange 2の再開条件は、TEI側で成立しています（同Issueの2026-09-27の節）。

### 現時点の推論・仮説

- 権限や決定は宣言と記録で成り立つ制度的な事実であり、後から推論では復元できない。したがって、基盤モデルが強くなるほど、コミットメントの記録の価値は上がる。
- 文脈の圧縮、要約の生成、安価な想起、節約のためのルーティングといった容量を補う仕組みは、進歩とともに薄くなる。
- 組織と社会の水準での有用性は、すべて仮説である。

### Unknown / Conflict

- 所有者が、統合の頂点という位置づけやコミットメントの台帳という言い直しを妥当と判断するか。
- 4つの空白（委任、注意の範囲、期待、消去と系譜）が、既存契約で表せない独立の失敗を生むか（ISSUE-000086）。
- 兄弟製品の実在の記録を読むとき、意味の損失が起きるか（ISSUE-000087）。

### Product Value / Accepted ADRとの関係

- ADR-0018 §7: Product Valueの意味に関わる変更は、理由、影響、互換性、Revisit条件を明示した再基線化として扱う。
- ADR-0014: SEIとTEIのProduct Boundaryを分離する。本Issueでも維持する。
- ADR-0021: Contractの権威と版管理。本Issueではversionを変えない。

## Questions

1. 頂点の三つの意味（抽象・時間・統合）を採り、三つ（指揮・所有・可用性）を採らないという定義は、「central AI brainではない」「固定pipelineではない」「関連製品を特権化しない」という既存の原則と矛盾しないか。
2. コミットメントの台帳という言い直しは、V1〜V8の意味を変えずに、価値の説明力を高めているか。
3. 「制御の仕組みはRealization、制御の判断の意味はCore」という規則は、Emergent Cognitive Architectureの評価仮説を失わずに、自己像の分裂を解いているか。
4. 組織と社会の場面、社会像は、Evidenceと誤読されない形で仮説として書けているか。
5. Value Propositionの約束への追加文は、既存の約束の強さを変えずに、肯定形の価値を加えているか。
6. 所有者が退けるべき項目、または修正すべき項目はどれか。

## Constraints

- V1〜V8、Decision Continuity、Evidenceの5段階の意味を変えない。
- REQ-0001〜REQ-0023、SCN-0001〜SCN-0019を変えない。新しいREQ / SCNを追加しない。
- 5つのSemantic Contractを`v1alpha1`のまま保つ。Contract versionを変えない。
- 既存のAccepted ADRを書き換えない。
- 兄弟製品に依存や義務を作らない。関係が深いことを依存の理由にしない。
- 神経系の比喩から型、field、要件を導かない。
- 規制への言及を、適合の保証として書かない。
- 社会的な価値を、Evidenceとして扱わない。
- すべての変更を、未mergeブランチ上の提案として扱う。mergeによる所有者の受け入れが関門である。

## 再基線化の項目

以下の変更を、ブランチ`docs/family-apex-backflow-20260927`で提案しています。

| ID | 対象 | 変更の内容 | 理由（弱み） | 互換性 |
|---|---|---|---|---|
| SEI-1 | `product/value/SEI_PRODUCT_VALUE.md` §1 / §3.10 / §7 | コミットメントの台帳という言い直し、モデルが強くなるほど価値が上がる理由、家族の統合の頂点の一文 | W5、W1、W8 | V1〜V8は不変。既存の中心の言い直し |
| SEI-2 | `product/vision/SEI_PRODUCT_VISION.md` §11、`product/definition/SEI_PRODUCT_SHAPE.md` §6 / §8.3 / §8.5 | 統合の頂点の定義、制御の仕組みと制御の判断の意味の分離、参考の対応表 | W1、W8 | 「中央の頭脳ではない」「固定pipelineではない」「特権なし」を維持 |
| SEI-3 | `product/value/SEI_VALUE_PROPOSITION.md` §2 / §6 / §7 | 約束への追加文、組織と社会の関与者と場面（仮説） | W5、W6 | 既存の約束は変更しない |
| SEI-4 | `product/vision/SEI_PRODUCT_VISION.md` §4 | 社会像をVision上の仮説として追加 | W6 | 新しいValue Axisにしない |
| SEI-5 | ADR-0035、本Issue | 再基線化の判断と手続き | W1 | 既存ADRをSupersedeしない |
| SEI-6 | ISSUE-000086 | 4つの空白の組合せ試験 | W3 | 新しいUniversal型を先に作らない |
| SEI-7 | ISSUE-000087 | 実在の記録からの求心プロファイル | W8 | 兄弟製品に義務を作らない |
| SEI-8 | ISSUE-000079 | Change 2の再開条件の成立を記録 | — | Statusは変えない。実行はまだ |
| SEI-9 | ISSUE-000073、`product/value/SEI_DECISION_CONTINUITY.md` §8 | H1 / H2の主指標と副次指標 | W2 | Resolution条件の強さは変えない |
| SEI-10 | `product/value/SEI_VALUE_ACCEPTANCE.md`（V4） | プロバイダ離脱訓練をOperational Evidence候補として記載 | W4、D2 | 未取得のまま |
| SEI-11 | `contracts/CONTRACT_CATALOG.md` | 契約を長く安定させる経路（提案節） | W4 | Contract versionは変えない |
| SEI-12 | `evaluation/cognitive-workspace-comparison/README.md` §2、`product/principles/SEI_PRODUCT_PRINCIPLES.md` §18 | 脱皮台帳と正当化の札 | S2 / S3の一般化 | 既存の反証条件を維持 |
| SEI-13 | `architecture/SEI_REFERENCE_ARCHITECTURE.md` | 境界B1〜B8を提案節として記録 | W1、W3 | current baselineにはしない |
| SEI-14 | `contracts/EXTERNAL_STANDARD_MAPPING.md`（新規） | W3C PROV-O、Open Memory Protocol、C2PAとの対応（参考） | D3、D9 | 非規範 |
| SEI-15 | `evaluation/sei-cognition-orchestration/EMERGENT_COGNITIVE_ARCHITECTURE.md` §1 / §7 / §16 | ADR-0035での読み方、予期された不確実性と予期しない不確実性、期待の記録（比喩由来の仮説） | W1 | Evaluation-onlyのまま |
| SEI-16 | `evaluation/distributed-execution-fabric/README.md` | 実在の後継製品eki-fabricとの関係 | — | SEIはschedulingを所有しない |
| SEI-17 | `product/definition/SEI_FAMILY_SEMANTIC_MAP.md`（新規） | 家族の判断の意味論、証拠段階の翻訳、求心・遠心プロファイルの候補 | W8 | 非Contract。各行は候補 |
| SEI-18 | `product/vision/SEI_BRAND_WORLD_SOURCE.md` §17 | 神経系の比喩にも同じ停止線を適用 | 比喩の誤用のリスク | 非規範sourceのまま |
| — | `product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md`（新規） | 評価記録と仮説ごとの採否 | — | 新しいValue Axisなし |

これに合わせて、`plan/registry.yaml`、`plan/document_review_registry.yaml`、`plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`、`product/README.md`、`contracts/README.md`、`architecture/README.md`、`product/value/SEI_VALUE_TRACEABILITY.md`を更新しています。

## Required scenarios / experiments

### R80.1 — 所有者によるレビュー

製品の所有者が、上の項目を一つずつ読み、採用、修正、却下を判断します。

読み方:

- **PASS** — 既存の原則との矛盾がなく、所有者が採用した項目。
- **FAIL** — 既存の原則と矛盾する、または所有者が却下した項目。却下した項目は、該当する文書から取り除くか、却下の理由とともに記録します。
- **NOT_VERIFIED** — まだレビューしていない項目。

### R80.2 — Stage 0の関門

レビューでは、少なくとも次の三つの原則との整合を確かめます。

```text
SEI != central AI brain
SUI / SEI / TEI / EKI != fixed pipeline
related product != privileged provider
```

いずれかと矛盾する項目は、採用しません。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

所有者のレビューが済んでも、それはDesign上の判断です。利用者の価値が実証されたことにはなりません。

## Deliverables

- ADR-0035（Proposed）
- `product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md` — 評価記録と仮説ごとの採否
- `product/definition/SEI_FAMILY_SEMANTIC_MAP.md` — 参考の対応表
- `contracts/EXTERNAL_STANDARD_MAPPING.md` — 外部標準との対応（参考）
- 上の表に示したProduct / Architecture / Contract / Evaluation / Plan文書の提案節
- 所有者のレビュー記録（本Issueへ追記する）

## Resolution

次をすべて満たしたとき、Resolved候補とします。

1. 所有者が、再基線化の各項目について採用、修正、却下を判断し、本Issueへ記録した。
2. 却下または修正した項目が、該当する文書へ反映された。
3. ADR-0035のStatusが、判断の結果（Accepted、Rejected、または一部を修正したうえでのAccepted）に更新された。
4. `plan/registry.yaml`と`plan/document_review_registry.yaml`が、文書のStatusと一致している。
5. 新しいValue Axis、Universal型、Stable Requirement、Contract versionが追加されていないことを再確認した。

後続のISSUE-000086〜000088の完了は、本IssueのResolution条件に含めません。本IssueがResolvedになることは、Operational EvidenceやAdoption / Outcome Evidenceが成立したことを意味しません。

## Reopen conditions

- ISSUE-000086で、既存契約の組合せでは表せない独立の失敗が観測され、Product Valueの表現を改める必要が生じた。
- ISSUE-000087で、兄弟製品の記録を読むときの意味の損失が、統合の頂点という位置づけを揺るがすほど大きいことが分かった。
- ISSUE-000073のH1 / H2で、誤帰属やプロバイダ交換後の継続に改善が見られなかった。
- ある製品の局所のループが、SEIの稼働に依存していることが見つかった。
- ADR-0035のRevisit条件のいずれかが成立した。

## CI / verification

このIssueで変更する対象はPlanとProduct / Architecture / Contract / Evaluationの文書です。通常は次のcheckerを実行します。

```text
python3 plan/scripts/check_plan_registry.py
python3 plan/scripts/check_document_review_registry.py
python3 plan/scripts/check_requirements_registry.py
python3 plan/scripts/check_github_actions_disabled.py
python3 plan/scripts/check_sei_operator_identity.py
```

### 2026-09-27の検証（手作業）

この作業を行った環境には、Python、Go、make、Nodeがありませんでした。そのため、**上のcheckerはどれも実行していません。** 未実行をPASSとは扱いません。

代わりに、次を手作業で確認しました。

- `plan/registry.yaml`: ADR-0035（Proposed）とISSUE-000085〜000088（Open）のentryが、各文書の見出しのIDとStatusの行に一致すること。ファイル名が4桁 / 6桁の採番規則に従うこと。IDの重複がないこと。related_issues / related_adrsが実在するIDだけを指すこと。
- ADR / IssueのStatusの語彙: checkerが許容する値（ADRは`Proposed`、Issueは`Open`）に収まること。
- `plan/document_review_registry.yaml`: 新しいcurrent Markdown文書が、既存のscopeのglobまたは新しいscopeに含まれること。`pending: []`が保たれていること。
- 追加・編集した文書の相対linkが、実在するファイルを指すこと。
- 追加した節の番号が重複せず、後続の節番号を正しく繰り下げたこと。
- 兄弟製品への参照は`hat47x/<repo>:<path>`の形で書き、未mergeブランチにだけ存在する文書にはその旨を添えたこと。参照したmain上のパスは、各リポジトリのremote-tracking refで存在を確認した（読み取りのみ）。

## Natural Japanese review

ADR-0035、評価記録、ADR-0018 §7、既存のProduct Value / Vision / Shape / Value Proposition、Emergent Cognitive Architectureを照合し、再基線化の項目を理由と互換性とともに一つの表へまとめました。所有者が項目ごとに採否を判断できることをGoalに置き、後続Issueの完了をResolution条件へ混ぜないようにしています。

内容、Constraints、完了条件、Reopen条件、未実行のchecker、Evidenceの高さを固定した後、自然な日本語となることを最重要視して全文を再ドラフトしました。最後に、再ドラフトの前後でGoal、Questions、Constraints、Resolution条件、Evidenceの高さが変わっていないことを再監査しました。
