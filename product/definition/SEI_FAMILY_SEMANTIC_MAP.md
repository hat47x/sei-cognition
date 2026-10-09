# SEI Family Semantic Map

更新日: 2026-09-27  
状態: **Informative Family Semantic Map — non-contract / all sibling mappings are candidates / proposed via ADR-0035**

## 1. この文書の役割

この文書は、hat47xの製品ファミリーの各製品が持つ判断の記録を、SEIの語でどう読めるかをまとめた**参考の対応表**です。

2026-09時点の家族は、SEI Cognition、SUI Sensemaking、TEI、EKI Fabric、Cultural Substrate Weaving（CSW）、Markdown Matrix Injector（MMI）、vs-bear-simulatorの7製品です。各製品は、それぞれの領域で提案と決定を分ける仕組みを独立に実装しています。SEIは、それらを一つにまとめるのではなく、翻訳します。

本書は次のいずれでもありません。

- Semantic Contract、Representation Profile、共通protocol
- Stable Requirement、Acceptance Scenario
- 兄弟製品への義務や、兄弟製品の成熟度についての主張

本書はADR-0035（Proposed）の「抽象の頂点」と「統合の頂点」に対応する参考文書です。実在の記録からの導出はISSUE-000087で行います。それまで、各製品との対応はすべて**候補**です。

## 2. 基本規則

本書を読むとき、また更新するときは、次を守ります。

1. **SEIは翻訳し、統合しない。** 各製品の記録をSEIの語で読むことはあっても、SEIの語へ置き換えたり、家族共通のontologyを作ったりしません。
2. **各製品が正本である。** 意味、要求、非目標、証拠の主張は、それぞれのリポジトリが正本です。本書と兄弟製品の文書が食い違う場合は、兄弟製品の文書を正とし、本書を直します。
3. **必須の依存を作らない。** どの製品も、この対応表がなくても成り立ちます。SEIへ記録を送ることも任意です。
4. **関連製品に特権を与えない。** 対応表に載っていることは、優先度、信頼、Authorityの理由になりません（Product Principles §22）。
5. **SEIの読みは、兄弟製品の権限を移さない。** たとえばSEIのRecommendationはTEIのAuthorizationになりません。SUIの昇格の判断はSUIの権限に残ります。
6. **各行の状態は候補である。** 実在の記録で意味の損失を確かめるまで、合意された対応として扱いません。

```text
translation != unification
product affinity != required dependency
mapping candidate != agreed contract
SEI reading != sibling authority
```

## 3. 判断の意味論の対応表

右端から二番目の列は、翻訳しても変えてはいけないことです。

| 製品 | 固有の記録 | SEIでの読み（候補） | 変えないこと | 状態 |
|---|---|---|---|---|
| 萃 SUI | AIのproposal / `human_reviewed`への昇格（ADR-0086。ReviewかAuthorityかはSUI側で未決） / `artifactId`・`revisionId`・`contentDigest` | Recommendation / 人によるReview、またはDecisionとAuthority evidence ref（どちらで読むかはISSUE-000087で確認する論点） / Logical Reference・revision・digest（正規化方式はSUI側で未決。JCS互換は選択肢の一つ） | 昇格の判断はSUIの権限にある | 候補 |
| 鼎 TEI | 共有受理境界のAccept（`.tei/decisions/`。TEI自身が「記録はauthorityではない」とする） / Authorization / Commandの結果 / Observation | Decisionの記録とAuthority evidence ref / 外部のAuthority / Execution receipt / Observation | SEIのRecommendationは、TEIのAuthorizationにならない | 候補（判断の時刻が失われる候補あり。§4.2） |
| 益 EKI | 署名付きAuthority Decision（WorkOrder、Lease、Placement Approval。COSE_Sign1） / Result Verification / Contribution | 外部のAuthority evidence / Assurance / Capability Observation | `valid signature != trusted Authority != current authorization`をそのまま運ぶ | 候補 |
| vs-bear | M5の採否記録（EXPERIMENT_ONLY / REJECTED / DEFAULT_ELIGIBLE。候補のSHAへ束縛） / Providerの試行 / モデルの限定権限（進路±0.18rad、コードが最終権限） | Decision（basisはExact Binding） / Capability Observation / 範囲つき委任の実例 | ゲームの結果は現実の指針にならない | 候補 |
| MMI | ADR-0018のAuthority PlaneとCognitive Assistance Plane / 別紙マニフェスト（`sourcePath,sheet,range,reason,caption,id`） / Source Identity Contract v1による出所の同一性とdigest / 構造化資料の観測契約（`hat47x.structured-artifact-observation/v0`） | AuthorityとRecommendation / Artifact Reference（表の範囲への論理参照） / Exact Binding / Observation | 表の正本は元のファイルにある | 候補 |
| CSW | `target_supported` / `framework_generated` / `cross_field_emergent` / `unresolved` / 著者の採否 | 対象で支持されたObservation / 出所つきのHypothesis / 創発のHypothesis / Unknown / 著者のDecision | ラベルは採否や公開を許可しない | 候補 |

### 3.1 参照した兄弟製品の文書

参照はすべて読み取りのみです。パスは`hat47x/<repo>:<path>`の形で示します。

- SUI: `hat47x/sui-sensemaking:01_Plans/adr/ADR-0086-sensemaking-artifact-identity-provenance-authority-events.md`、`hat47x/sui-sensemaking:01_Plans/cross-repo/2026-09-18-product-family-positioning.md`
- TEI: `hat47x/tei-platform:docs/status.md`（`.tei/decisions/`の記録）、`hat47x/tei-platform:tools/reference-shared-acceptance/README.md`、`hat47x/tei-platform:plan/adr/0028-human-ai-builder-agent-shared-knowledge-plane.md`
- EKI: `hat47x/eki-fabric:plan/adr/0004-signed-decision-cryptographic-profile.md`、`hat47x/eki-fabric:product/value.md`、`hat47x/eki-fabric:product/principles.md`
- vs-bear: `hat47x/vs-bear-simulator:docs/M5_DECISION_GATE.md`、`hat47x/vs-bear-simulator:docs/LOCAL_TYPED_COGNITION.md`、`hat47x/vs-bear-simulator:docs/M5_ADOPTION_EVIDENCE_JOIN.md`
- MMI: `hat47x/markdown-matrix-injector:01_Plans/adr/ADR-0018-cognitive-assistance-plane.md`、`hat47x/markdown-matrix-injector:04_Documentation/spec/mmi-notation-v1.md`（§8.1）、`hat47x/markdown-matrix-injector:02_Architecture/source-identity-contract-v1.md`、`hat47x/markdown-matrix-injector:02_Architecture/structured-artifact-neutral-observation-v0.md`
- CSW: `hat47x/cultural-substrate-weaving:AGENTS.md`

兄弟製品の側でも、SEIとの対応を記した文書が、各リポジトリの未mergeブランチ`docs/family-apex-backflow-20260927`（CSWは`research/family-apex-backflow-20260927`）で提案されています。次の文書は、新規のものはそのブランチ上にだけ存在し、既存のものはそのブランチ上で追記されています。

- EKI: `hat47x/eki-fabric:research/sei-cognition-mapping.md`（Cognitive EnvelopeからEKIのTaskRequestへの一方向の対応、署名付きAuthority DecisionをSEIの外部Authority evidenceとして読むこと）、`research/contribution-accounting.md`（ContributionとCapability Observationの対応。詳しいContributionの記録は従業員の不在を推測させ得るというprivacyの注意）、`requirements/ACCEPTANCE_SCENARIOS.md`（候補PAS-CAND-01〜06、評価待ち）、`product/value.md`（反射弓の小節）
- TEI: `hat47x/tei-platform:plan/issue/000070-sei-reference-adoption-change2-resumption.md`（Change 2の再開。TEI-4の付録で`.tei/decisions/`の投影、TEI-6の付録でRQ-013）、`plan/ACTOR_CONTEXT_PROJECTIONS_2026-09.md` §11.1（委任の参照）、`product/value/TEI_PRODUCT_VALUE.md` §8
- MMI: `hat47x/markdown-matrix-injector:02_Architecture/sei-decision-semantics-mapping.md`、`01_Plans/issues/issue-0192-sei-decision-basis-table-binding.md`、`04_Documentation/spec/mmi-notation-v1.md`の非規範の付録
- CSW: `hat47x/cultural-substrate-weaving:docs/ja/maintainers/sibling-product-semantic-correspondence.md`、`research/skill-prototypes/REFERENCE-CLASSIFICATION.md`の付録A
- vs-bear: `hat47x/vs-bear-simulator:docs/LOCAL_TYPED_COGNITION.md` §32.1（範囲つき委任の実例として、ISSUE-000086の入力）・§32.2（Providerの同一性）、`docs/M5_ADOPTION_EVIDENCE_JOIN.md`（採否記録をdecision memoryとして読むこと）、`docs/PRODUCT_VALUE_IDEAS.md` §20
- SUI: `hat47x/sui-sensemaking:02_Architecture/sensemaking_artifact_sei_mapping_candidate.md`（ADR-0086と`sei.semantic-reference`の対応、承認イベントの書き出し、ADR-0049とCognitive Envelopeの比較）、`01_Plans/cross-repo/2026-09-18-product-family-positioning.md`（頂点の定義と、CSW・MMI・vs-bearの行）、`01_Plans/issues/issue-ARCH-TEI-MIGRATION-01-tei-reference-adoption-and-development-load-validation.md`（SEIのdecision memoryで記録する任意のdogfoodの節）、`01_Plans/issues/issue-COGNITIVE-ASSOC-01-affinity-semantic-field-poc.md` §12（`suiassocprovider`の実行を含む次の手順）

これらは各製品の提案であり、SEIの対応表と同じく、各製品の所有者がmergeするまで確定しません。

## 4. 各製品の読みの注記

### 4.1 SUI

SUIでは、AIの提案を人が確かめ、`human_reviewed`へ昇格させることができます（ADR-0086）。この昇格をReviewの記録とみなすか、Authorityの記録とみなすかは、ADR-0086とそのartifact contractでも開かれたままであり、**SUI側で未決**です。

したがってSEIでも、人によるReviewとして読むか、人によるDecisionとAuthority evidence refとして読むかを、現時点では決めません。どちらで読むべきかは、ISSUE-000087で確認する論点です。いずれの場合も、昇格そのものはSUIの権限に残り、SEIが昇格を代行したり、SEIの記録から昇格を推定したりしません。

`artifactId`、`revisionId`、`contentDigest`は、SEIのLogical Reference、revision、Exact Bindingに近い役割を持ちます。ただし、SUIはpayloadの正規化方式をまだ定めていません。JCSと互換にすることは選択肢の一つです。方式が定まり、確かめられるまでは、SUIのdigestがSEIの`sei.jcs+sha256/v1alpha1`と同じ値になるとは扱いません。

### 4.2 TEI

TEIの共有受理境界を通った受理は、`.tei/decisions/`に記録されます。記録には、意図、Evidence、基準のrevision、書き換えたfile、意味の差分、残った未解決が含まれます。TEI自身は、この記録を「authorityではない」としています。記録を消しても、model revisionや受理された意味は変わりません。

SEIでは、この記録をDecisionの記録と、TEIのAuthorityを指すevidence refとして読めます。SEIがこの記録を取り込んでも、それがTEIのAuthorizationになることはありません。TEIのAI Business Actorが受理済みのActionを実行するとき、どの委任とどの判断の文脈が使われたかをSEIで参照できるかは、ISSUE-000086の委任の試験で扱います。

TEI側の検討では、`.tei/decisions/`の記録にtimestampのfieldがないことが見つかっています。この記録をSEIのDecisionとして読むと、判断の時刻が失われ、当時の根拠と判断後の情報を分ける読み方（V1 / V3）に影響する可能性があります。これは意味の損失の最初の候補であり、SEIの要求の不足として確定したものではありません。Git commitの時刻で補える可能性も、TEI側で明示的なfieldを持つ可能性もあります。ISSUE-000087で最初に確かめます。TEIはこの点を`hat47x/tei-platform:plan/issue/000070-sei-reference-adoption-change2-resumption.md`（TEI-4の付録）に記録しており、この文書は未mergeブランチ`docs/family-apex-backflow-20260927`上にだけ存在します。

### 4.3 EKI

EKIの署名付きAuthority Decisionは、署名が有効であること、その署名者が信頼されたAuthorityであること、そしてその判断が現在も有効であることを分けています。SEIでもこの三つを一つに潰さず、そのまま運びます。

```text
valid signature
  != trusted Authority
  != current authorization
```

EKIのContribution（計算資源の提供）は、SEIのCapability Observationとして読めます。ただしEKIのworkerや配置の判断をSEIのUniversal Coreへ取り込みません（Product Shape §3.5 / §6.3）。

EKI側の対応ノートは、詳しいContributionの記録が従業員の不在を推測させ得ると注意しています。SEIが資源の観測として読む場合も、利用者の在席を推測できる粒度では取り込まず、頂点が監視の拠点にならないという境界（B8）を守ります。

### 4.4 vs-bear

vs-bearのM5の採否記録は、候補のSHAへ束縛されており、SEIのDecisionとExact Bindingで読める形をしています。

vs-bearでは、モデルの判断が進路の偏り±0.18radの範囲だけに限られ、決定論のcontrollerが最終権限を持ちます。モデルの出力が遅い、無効、欠けている、古い場合は、決定論のcontrollerがそのまま動き続けます。これは、範囲つきの委任を実装した具体例として、ISSUE-000086の入力にします。

ゲームの結果は現実の指針になりません。SEIの記録として読む場合も、野生動物への対応や安全の指導として表示しません。

### 4.5 MMI

MMIは、parserやresolverなど決定論的なAuthority Planeと、認知技術を置くCognitive Assistance Planeを分けています（MMI ADR-0018）。SEIのAuthorityとRecommendationの区別に対応します。

MMIの別紙マニフェスト（仕様§8.1）は、`sourcePath`、`sheet`、`range`、`reason`、`caption`、`id`を持ちますが、**digestは持ちません**。出所の同一性とdigestは、MMIのSource Identity Contract v1が扱います。したがって、表の範囲をSEIのDecisionの根拠として正確に束縛するには、マニフェストの行（論理参照）とSource Identity Contract v1のdigest（当時の内容への束縛）を組み合わせて読む必要があります。

digestの互換性には、次の差があります。

- MMIの出所ファイルのdigestは、SEIの`sei.raw-bytes+sha256/v1alpha1`と同じ規則で計算されており、そのまま整合します。
- MMIの`hat47x.structured-artifact-observation/v0`は、keyを並べ替えてJSONを書き、末尾に改行を加える方式であり、JCS（RFC 8785）ではありません。そのため、SEIの`sei.jcs+sha256/v1alpha1`とはdigestの値が異なります。この二つを収束させるには、canonicalizationの対応を明示的に定める必要があります。

表の正本は、常に元のファイルにあります。文書に写した表は正本ではありません。

### 4.6 CSW

CSWの帰属ラベルは、候補がどこから来たかを示します。`target_supported`は対象で支持されたもの、`framework_generated`は文化や哲学の体系を一時的に働かせて生成した候補、`cross_field_emergent`は分野をまたいで現れた候補、`unresolved`は未解決です。

SEIでは、それぞれObservation、出所つきのHypothesis、創発のHypothesis、Unknownとして読めます。ラベルは、採否や公開を許可しません。採否は著者のDecisionです。

SEIは、神経系やブランドの比喩を扱うときにも、この帰属の規律を借ります。比喩から生じた問いは`framework_generated`として扱い、対象で確かめるまで要件にしません（`../vision/SEI_BRAND_WORLD_SOURCE.md` §17）。

## 5. 証拠段階の翻訳表

SEIの5段階（Design / Executable / Release / Operational / Adoption・Outcome）を参照軸として、各製品の現在地を読んだ候補です。**これは各製品の成熟度についての主張ではありません。** 各製品の証拠の語彙と判定は、それぞれのリポジトリが正本です。

2026-09-27時点のsnapshotです。

| 製品 | 各製品が示している状態 | SEIの参照軸での読み（候補） |
|---|---|---|
| CSW | v0.4.0をrelease。Living Labで公開観測3件。効果は未確立 | Releaseに相当する記録あり。Living Labの観測は利用の観測の入口だが、Adoption / Outcomeは未確立 |
| SUI | 基本機能を実装。CHANGELOG 0.1.0（tagなし）。4条件比較と第三者セッションは未実施 | Executableに相当する記録あり。tagがないためReleaseは未確認。Outcomeの比較は未実施 |
| SEI | v0.2.0のRelease Evidence。V1〜V8は対象を限定して確認 | Release Evidenceあり（Local Reference Product Baselineの範囲）。Operational / Adoption・OutcomeはNot Yet Verified |
| TEI | Gate B / Gate C Ready（Referenceの範囲。見た目の忠実度は単一のAI評価者による判定） | Executableに相当するEvidence（Reference範囲）。人による見た目の確認と、Operational / Outcomeは未確認 |
| EKI | Architecture Baseline 0.1。protocolのconformance test。M0へ移行中 | Designと、限定されたExecutableに相当する記録 |
| MMI | tag v0.1.0のVSIX。Marketplaceは未公開。仕様はDraft | Releaseに相当するtagつき成果物あり。仕様はDesignの段階。配布と利用は未確認 |
| vs-bear | M0〜M4をmerge。M5の関門は判定待ち | Executableに相当する記録あり。M5の採否は未判定 |

**7つの製品のどれにも、OperationalとAdoption / OutcomeのEvidenceがまだありません。** これは家族全体に共通する空白です。

## 6. 求心・遠心プロファイルの候補

神経系の比喩にならい、製品からSEIへ向かう流れを求心、SEIから製品へ向かう流れを遠心と呼びます。これは内部の設計言語であり、比喩から型やfieldを作りません。

製品はSEIへ送ってもよいし、送らなくても成り立ちます。SEIからの遠心の信号は、すべて**依頼**です。受け取った製品が、自らの権限で判断します。

| 製品 | 求心の候補（製品 → SEI） | 遠心の候補（SEI → 製品、依頼のみ） | 状態 |
|---|---|---|---|
| SUI | 未整理な材料の知覚（Observation、Method Application、Artifact Reference）、`human_reviewed`への昇格の記録（Reviewとして読むか、Decision + Authority evidence refとして読むかは未決） | 問いの種（問いと材料を渡す。意味形成はSUIが行う） | 候補 |
| MMI | 構造化資料の観測（Observation）、表の範囲とSource Identityのdigest（Artifact Reference + Exact Binding） | —（現時点では想定しない） | 候補 |
| vs-bear | 身体化された体験、M5の採否記録（Decision）、Providerの試行（Capability Observation） | —（現時点では想定しない） | 候補 |
| CSW | 想像と代替の見方、帰属ラベルつきの候補（出所つきのHypothesis） | 見方を開く依頼 | 候補 |
| TEI | 実行後のObservation、受理の記録（Decision + Authority evidence ref）、Commandの結果（Execution receipt） | Action Intent（TEIが自らの権限で実行を判断する） | 候補 |
| EKI | 資源、電力、利用者の在席（内受容。Capability Observation）、署名付きAuthority Decision（外部のAuthority evidence）、Contribution | 認知jobの意味（workload contractへ投影される。配置はEKIが決める） | 候補 |
| 外部AI・将来の製品 | MCP・A2A経由の文脈提供 | 書き込みは提案として受ける（B3） | 候補 |

求心のプロファイルとして何を最小限に定めるべきかは、ISSUE-000087で、TEIの`.tei/decisions/`とSUIの承認イベントという実在の記録から導きます。実際の統合の失敗が観測されない限り、プロファイルを先に固定しません。

## 7. 反射弓 — SEIを経由しない局所のループ

どの製品の局所のループも、SEIの稼働を必要としません。SEIが止まっても、次のループは動きます。

| 製品 | 局所のループ | 出所 |
|---|---|---|
| SUI | LLMなし（`SUI_LLM_PROVIDER=none`）でも主な価値が動く | SUIの製品文書 |
| EKI | 業務端末では、利用者の復帰、ネットワーク、温度、電源、局所の方針、明示的なopt-outを中央のschedulerより優先する | `hat47x/eki-fabric:product/principles.md` |
| TEI | Driverと共有受理境界で単独に完結する | `hat47x/tei-platform:docs/status.md` |
| vs-bear | 既定は決定論のcontroller。モデルは進路±0.18radの範囲だけ | `hat47x/vs-bear-simulator:docs/M5_DECISION_GATE.md` |
| MMI | 決定論的なAuthority Planeが、認知の補助なしで参照を解決する | `hat47x/markdown-matrix-injector:01_Plans/adr/ADR-0018-cognitive-assistance-plane.md` |
| CSW | Skillとして、SEIなしで帰属の規律を保って動く | `hat47x/cultural-substrate-weaving:AGENTS.md` |

SEIは、これらのループに入りません。ある製品の局所のループがSEIに依存していることが見つかった場合は、ADR-0035の再検討条件にあたります。

## 8. この対応表で決めないこと

- 家族共通のschema、protocol、ontology
- 兄弟製品の記録形式の変更や、SEIへ送る義務
- 兄弟製品の成熟度や証拠の判定
- SEIのUniversal Coreへの新しい型の追加
- 兄弟製品の内部概念（SUIのsensemaking object、TEIのApplication / Database / Release、EKIのworkerやscheduler等）の複製

## 9. 更新と見直しの条件

次の場合に本書を更新します。

- 兄弟製品の正本の文書が変わり、本書の読みと食い違った。
- ISSUE-000087で、実在の記録を読んだ結果、意味の損失が見つかった。あるいは損失がないことが確認された。その場合、該当する行の状態を「候補」から、Evidenceの高さを添えた状態へ改める。
- ISSUE-000086で、委任や消去の読み方が定まった。
- 新しい製品が家族に加わった、または外れた。

兄弟製品との統合の失敗が観測されず、どの製品もこの対応表を使わない状態が続く場合は、本書を縮小または廃止します。

## 10. Evidence状態

```text
Family semantic map: informative Design record
Sibling mappings: candidate（real-record mapping Not Yet Verified）
Executable Evidence: none added
Operational Evidence: Not Yet Verified
Adoption / Outcome Evidence: Not Yet Verified
```

## 11. 関連文書

- `SEI_PRODUCT_SHAPE.md` — §6 隣接Productとの境界、§8.5 家族統合の未決事項
- `../value/SEI_FAMILY_APEX_VALUE_REVIEW.md` — 本書の元になった評価記録
- `../value/SEI_PRODUCT_VALUE.md` — §3.10 隣接Productと価値の正本
- `../vision/SEI_PRODUCT_VISION.md` — §11 SUI・TEI・EKIとの関係
- `../vision/SEI_BRAND_WORLD_SOURCE.md` — §17 比喩の停止線
- `../principles/SEI_PRODUCT_PRINCIPLES.md` — §22 関連製品を特権化しない
- `../../contracts/EXTERNAL_STANDARD_MAPPING.md` — 外部標準との対応（参考）
- `../../plan/adr/ADR-0014-sei-tei-product-boundary.md`
- `../../plan/adr/ADR-0035-family-integration-apex-and-control-meaning-boundary.md`
- `../../plan/issue/ISSUE-000086-test-commitment-gaps-by-composition.md`
- `../../plan/issue/ISSUE-000087-derive-family-afferent-profile-from-sibling-records.md`

## 12. Natural Japanese review

兄弟製品の該当文書を読み取り、各製品の判断の記録をSEIの語でどう読めるかを表にまとめました。どの読みも候補であり、各製品が正本であること、必須の依存を作らないこと、SEIの読みが兄弟製品の権限を移さないことを、最初に規則として置いています。

MMIについては、別紙マニフェストがdigestを持たず、出所のdigestはSource Identity Contract v1が扱うこと、構造化資料の観測がJCSではないためSEIのJCS Profileとdigestが異なること、出所ファイルのdigestはraw-bytes Profileと整合することを、MMI側の確認に合わせて正確に書いています。TEIについては、受理記録に時刻のfieldがないという損失の候補を、要求の不足と断定せずにISSUE-000087で確かめる項目として記しました。SUIについては、`human_reviewed`への昇格がReviewかAuthorityか、digestの正規化方式をどうするかがSUI側で未決であることを、そのまま未決として書いています。証拠段階の翻訳表は、SEIの5段階を参照軸にした読みであり、各製品の成熟度の主張ではないことを明記しました。

内容と留保を固定した後、英語の名詞の連結を日本語の説明へ置き換え、表の各行と注記が一続きに読めるように、**自然な日本語となることを最重要視して全文を再ドラフトし、候補の状態、非Contract性、Evidenceの高さが変わっていないことを最終監査しました。**
