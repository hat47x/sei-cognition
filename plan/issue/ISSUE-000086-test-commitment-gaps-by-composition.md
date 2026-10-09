# ISSUE-000086: 委任・注意の範囲・期待・消去と系譜の4つの空白を、既存契約の組合せで試す

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0003, ADR-0004, ADR-0010, ADR-0016, ADR-0035**  
Updated: 2026-09-27

## Goal

ADR-0035（Proposed）は、SEIの価値の中心を「判断と認識のコミットメント」の台帳として言い直すことを提案しています。そのコミットメントのうち、次の4つは現在の契約で受け皿が明確ではありません。

1. **委任** — 誰に、どの範囲で、いつまで判断を任せたか。いつ撤回したか。
2. **注意の範囲** — 何を見て、何を意図的に見送ったか。誰が、どの手段で絞り込んだか。
3. **期待** — 判断が正しければ、何が観測されるはずか。外れた観測が来たとき、見直しを起こせるか。
4. **消去と系譜** — プライバシーのために内容を消しても、存在と系譜を残せるか。

本Issueでは、これらを新しいUniversal型として追加する前に、**既存のSemantic Contractと既存の概念の組合せで表せるか**を、具体的な失敗の場面を使って試します。

完了時には、4つの空白それぞれについて、次のどれに当たるかを理由とともに判別できることを目指します。

```text
A. 既存契約の組合せで十分に表せる
B. Profileや運用の規約を足せば表せる
C. Product-localな設計や表示で扱うべきである
D. 既存契約では表せない独立の失敗があり、Candidate Requirementへ進む
E. 失敗の場面が現実的でなく、変更は不要
```

どの結論も正当な成果です。Aの「既存契約で十分」という結論は、とくに歓迎します。

## Background

### 確認済みの事実

- `product/value/SEI_VALUE_PROPOSITION.md` §4.3は、「どこまでを誰に委ねたか」を後から読める状態を価値としています。しかし、委任の範囲、期間、撤回を表す契約上の受け皿は明示されていません。
- `sei.decision-memory/v1alpha1`は、context、basis、recommendation、unresolved、Responsibilityへの参照、Rationale、Authority evidence reference、review / reopen conditionを扱えます。Decisionの記録へAuthorityを直接埋め込むことは拒否します。
- `sei.semantic-reference/v1alpha1`は、`revises`、`supersedes`、`withdraws`を区別し、`withdraws`とphysical delete / retention purgeを同一視しないとしています。
- `sei.cognitive-method/v1alpha1`は、Method Definition、Realization、Applicationと、そのinput / output / residualへの参照を扱います。
- ADR-0004はResponsibilityをGlobal Identityなしに文脈へ結び付け、ADR-0016はAuthorizationのEvidenceをProviderの境界に置いています。
- Exact Bindingの検証結果は、`not_verified`と`failed`を分けています（ADR-0009）。

### 外部の入力（読み取りのみ。依存ではない）

- **vs-bear-simulatorの限定権限** — モデルの判断は、typed decisionの水準で進路の偏り±0.18radに限られます。決定論のcontrollerが最終権限を持ち、モデルの出力が遅い、無効、欠けている、古い場合は、controllerがそのまま動き続けます（`hat47x/vs-bear-simulator:docs/M5_DECISION_GATE.md`、`docs/LOCAL_TYPED_COGNITION.md`）。vs-bear側では、これを範囲つき委任の実例としてSEIへ提供する節（`docs/LOCAL_TYPED_COGNITION.md` §32.1）が、未mergeブランチ`docs/family-apex-backflow-20260927`上で提案されています。
- **TEIのAI Business Actor** — TEI ADR-0028（採用）は、TEIの成果物を人間、AI Builder、AI Business Actorの共通の知識面として扱います（`hat47x/tei-platform:plan/adr/0028-human-ai-builder-agent-shared-knowledge-plane.md`）。受理済みのActionをAI Business Actorが実行するとき、委任の付与と判断の文脈をSEIで参照できる形は、TEI側の`plan/ACTOR_CONTEXT_PROJECTIONS_2026-09.md` §11.1で、同じ未mergeブランチ上に提案されています。
- **W3C PROV** — `prov:actedOnBehalfOf`は、ある主体が別の主体に代わって活動したことを表す委任の関係です。`prov:wasAttributedTo`は帰属を表します（`contracts/EXTERNAL_STANDARD_MAPPING.md`）。
- **削除の墓標** — MacPawのPortable Memoryは、記憶の削除に墓標を残す設計を持つと報告されています（外部資料。要確認）。

### Unknown / Conflict

- 4つの空白が、実際の利用で独立した失敗を生むかどうかは分かっていません。
- 「注意の範囲」の記録が、利用者に過剰な記録の負担を課すおそれがあります（V7との緊張）。
- 消去の記録が、消した内容の存在そのものを推測させるおそれがあります（プライバシーとの緊張）。

## Questions

1. 委任を、Decision（委任するという判断）、Responsibilityへの参照、Authority evidence reference、Constraintへの参照、reopen condition、後の`supersedes` / `withdraws`の組合せで表せるか。
2. 委任の範囲の内側の決定と、範囲の外の提案を、後から読み分けられるか。
3. 「意図的に見送ったもの」「まだ見ていないもの（Unknown）」「観測できないもの」を、既存の概念で区別できるか。
4. 絞り込みを行った主体や手段（人、ルール、分類器、SACS等）を、Cognitive Method Applicationとして記録すれば足りるか。
5. 期待を、reopen conditionと、そこから参照するHypothesisやObservationの組合せで表せるか。
6. 期待から外れた観測を、後から結び付けて読めるか。後知恵と区別できるか。
7. 根拠に使った内容を消したとき、`not_verified`や`failed`と区別して「消去された」ことを読めるか。
8. 消去（redaction）を改訂（revision）と取り違えずに読めるか。派生した記録の系譜は残るか。

## Constraints

- 独立の失敗が観測されない限り、新しいUniversal型、Universal field、Stable Requirementを追加しない（ADR-0018 §6、Product Principles §11）。
- 神経系の比喩（予測誤差等）から型やfieldを導かない。
- vs-bear、TEI、W3C PROV、Portable Memoryは入力であり、依存ではない。兄弟製品に義務を作らない。
- SEIのRecommendationをTEIのAuthorizationとして扱わない。vs-bearのゲームの結果を現実の指針として扱わない。
- 失敗の場面に使うfixtureやサンプルに、実在の個人情報を含めない。
- `Responsibility != Authorization`、`Decision != Authority != Execution`を維持する。
- 消去の検討で、監視の拠点になるような記録（誰が何を消したかの過剰な追跡）を作らない。

## 空白ごとの失敗の場面

### G1 — 委任

失敗の場面:

- **F1.1 範囲の超過** — 個人のAIエージェントに「5万円以内で出張の宿を予約する」ことを任せた。エージェントは7万円の宿を予約した。後から、その予約が任せた範囲の内側だったのか外側だったのかを、記録だけでは判定できない。
- **F1.2 撤回後の実行** — 委任を3日に撤回したが、4日のエージェントの決定が、記録の上ではまだ権限のある決定に見える。撤回の時点が残っていない。
- **F1.3 範囲つきの適用と、古い出力の破棄** — vs-bearと同じ形の場面。モデルは進路を0.3rad変える提案を出したが、controllerは±0.18radに切り詰めて適用した。別の時点では、モデルの出力が古かったため捨てられた。記録は「モデルの提案」「範囲内に切り詰めた適用」「controllerの最終権限」「古さによる破棄（内容の良し悪しによる却下ではない）」を区別できなければならない。
- **F1.4 他製品の権限との混同** — TEIのAI Business Actorが受理済みのActionを実行した。SEIの記録が、どの委任とどの判断の文脈に基づいたかを参照するとき、SEIの記録がTEIのAuthorizationの代わりに見えてはならない。

組合せの候補:

- 委任するという判断 = Decision
- 任された主体 = Responsibilityへの参照
- 付与の根拠 = 外部のAuthority ProviderへのAuthority evidence reference
- 範囲 = Constraintへの参照
- 期限や撤回の条件 = reopen condition
- 撤回 = 後のDecisionと、`supersedes`または`withdraws`

W3C PROVの`actedOnBehalfOf`への写し方は、`contracts/EXTERNAL_STANDARD_MAPPING.md`で候補として扱います。

### G2 — 注意の範囲

失敗の場面:

- **F2.1 見た範囲の過大な読み** — レビューで「リスクなし」と結論したが、実際に確かめた資料は10件のうち3件だった。後の読み手は、10件すべてを確かめたと読んでしまう。見ていない範囲のUnknownが、Noへ変わっている。
- **F2.2 見えない絞り込み** — ルーターや分類器が、人が見る前に資料を落としていた。Decisionの根拠には、誰がどの手段で絞り込んだかが残っていない。
- **F2.3 見送りの種類の混同** — 意図的に範囲外とした資料、まだ見ていない資料、観測できなかった資料が、区別されずに「未確認」とだけ残る。

組合せの候補:

- 絞り込み = Cognitive Method Application（input refs、output refs、residual）
- 見ていない範囲 = unresolved refs（Unknown）
- 手段の選択 = Capability Choiceとしての既存Decision
- 評価仮説のCognitive Envelopeの選択記録（`evaluation/sei-cognition-orchestration/EMERGENT_COGNITIVE_ARCHITECTURE.md` §4）を広げる案は、Contractへ入れずにProduct-localな候補として比べる

### G3 — 期待

失敗の場面:

- **F3.1 惰性の継続** — 「2週間以内に問い合わせが3割減る」と期待して判断したが、減らなかった。期待が記録されておらず、誰も見直しを始めなかった。
- **F3.2 後からの期待** — 結果が出た後で、関係者が「最初からそうなると思っていた」と語る。判断の時点の期待が残っていないため、後知恵と区別できない。
- **F3.3 外れた観測の見落とし** — 期待から外れた観測が届いたが、通常の観測として扱われ、見直しにつながらなかった。

組合せの候補:

- 期待 = reopen conditionと、そこから参照するHypothesis（判断が正しければ観測されるはずのこと）
- 外れた観測 = 後から加わるObservationと、Semantic Lineage
- 判断の時点の記録と、判断後の情報の分離（`post-decision information != historical basis`）は、既存の境界を使う

### G4 — 消去と系譜

失敗の場面:

- **F4.1 検証の失敗との混同** — Observationに含まれていた個人情報を、本人の求めで消した。そのObservationを根拠にExact Bindingしていたため、検証ができなくなった。記録は、改ざんによる`failed`や、単なる`not_verified`ではなく、「根拠は存在したが、消去された」と読める必要がある。
- **F4.2 改訂との取り違え** — 後の読み手が、消去を意味の変更（改訂）と取り違え、判断の根拠が変わったと読んでしまう。
- **F4.3 系譜の断絶** — 消去によって、派生した記録の出所の連なりが切れる。

組合せの候補:

- 消去 = 内容の削除（retention purge）と、`withdraws`等のsemantic relationを分けたうえでの記録
- 検証の結果 = `not_verified`と、消去の理由を示すProvenance
- 墓標 = 存在と系譜だけを残し、内容を残さない記録として、既存のProvenanceとSemantic Lineageで表せるかを試す

```text
redaction != revision
physical deletion != semantic withdrawal
binding not_verified != binding failed
```

## Required scenarios / experiments

### E81.1〜E81.4 — 空白ごとの組合せ試験

各空白について、上の失敗の場面を、既存のContract Definitionに沿った記録の組合せとして書き出します。

1. 失敗の場面ごとに、最小の記録の組（Designの草案）を作る。
2. 各記録が、現在のContract Definitionの意味と矛盾しないかを確かめる。
3. 後の読み手が、失敗を避けて正しく読めるかを確かめる。
4. 必要であれば、既存のschemaとvalidatorで検査できるfixtureの候補にする。

読み方:

- **PASS** — 既存の組合せで、失敗の場面を正しく読み分けられる。
- **FAIL** — 既存の組合せでは、失敗の場面を読み分けられない。その理由が、表示や運用ではなく意味の欠落にある。
- **NOT_VERIFIED** — 草案はあるが、まだ確かめていない。

FAILが出た場合も、直ちにUniversal型を追加しません。Profile、運用の規約、Product-localな設計で解けないかを先に確かめ、それでも残る場合だけCandidate Requirementへ進めます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

草案の作成と照合はDesign Evidenceです。fixtureを実行して初めてExecutable Evidenceになります。

## Deliverables

- 空白ごとの組合せの記録と、A〜Eのどれに当たるかの判断（本Issueへ追記するか、`evaluation/`へ評価資料として置く）
- 必要な場合のfixture候補
- 結果に応じた、`SEI_FAMILY_SEMANTIC_MAP.md`と`contracts/EXTERNAL_STANDARD_MAPPING.md`の更新
- Dに当たる空白があった場合のCandidate Requirementと、Requirement audit

## Resolution

次をすべて満たしたとき、Resolved候補とします。

1. 4つの空白のそれぞれについて、少なくとも一つの失敗の場面で組合せ試験を行った。
2. 各空白を、A〜Eのどれかに理由とともに分類した。
3. Dに分類した空白がある場合は、既存のREQ / SCNとの重複を監査し、Candidate Requirementとして記録した。
4. 新しいUniversal型を追加していないか、追加した場合はその独立の失敗と新しいADRがある。

Resolvedになることは、委任や期待の記録が利用者に価値を届けたことを意味しません。

## Reopen conditions

- 実際の利用で、組合せでは読み分けられない委任、注意の範囲、期待、消去の失敗が見つかった。
- 兄弟製品の実在の記録（ISSUE-000087）から、ここで想定しなかった失敗が見つかった。
- 消去の求めに応える運用で、系譜を残すこととプライバシーを守ることが両立しない事例が見つかった。
- Product Value、ADR-0004、ADR-0016、ADR-0035が変更された。

## CI / verification

組合せ試験をfixtureとして実体化する場合は、Contractのconformance checkerとGoのsemantic runtimeのtestを、変更範囲に応じてローカルで個別に実行します。Planの変更では`plan/scripts/check_plan_registry.py`と`plan/scripts/check_document_review_registry.py`を実行します。

2026-09-27の起票時点では、PythonとGoがない環境で作業したため、どのcheckerも実行していません。手作業での確認はISSUE-000085の「2026-09-27の検証（手作業）」に記録しています。

## Natural Japanese review

ADR-0035、Decision Memory、Semantic Reference、Cognitive Methodの各Contract Definition、ADR-0004 / 0009 / 0016、Value Proposition §4.3、vs-bearとTEIの該当文書を照合し、4つの空白を具体的な失敗の場面と組合せの候補へ落としました。新しい型を足す前に既存の組合せを試すこと、どの結論も正当であることを、Goalと読み方の両方に書いています。

内容、Constraints、読み方、完了条件を固定した後、失敗の場面を利用者の言葉で読めるように、**自然な日本語となることを最重要視して全文を再ドラフトしました。** 最後に、Goal、Questions、Constraints、Resolution条件、Evidenceの高さが再ドラフトの前後で変わっていないことを再監査しました。
