# SEI Decision Continuity — Product Value Synthesis

更新日: 2026-09-18  
状態: **Cross-axis Product Value Synthesis — Design Baseline / Executable & Human Outcome Evidence Pending**

## 1. この文書の役割

この文書は、SEIのProduct Value、V1〜V8、resume-first Product Sliceを、利用者が最終的に受け取る一つの横断的な成果へ接続します。

その成果を本書では**Decision Continuity（判断継続性）**と呼びます。

```text
Decision Continuity
  = 時間が空いても
  + SurfaceやAIが変わっても
  + 新しい情報が増えても
  + 不確実性が残っていても
  過去を捏造せず、判断仕事の続きを始められること
```

Decision Continuityは新しいUniversal Core概念ではありません。また、V1〜V8に追加する`V9`でもありません。

既存Value Axisを、実際の利用者成果として束ねて検証するための**cross-axis Product Outcome**です。

## 2. なぜ「保存」だけでは足りないか

SEIはこれまで、判断時点のbasis、Unknown / Conflict、Recommendation / Decision、Revision、Provider Independence等を耐久的な意味として守ってきました。

しかし、意味が保存されていることと、利用者が仕事を再開できることは同じではありません。

数日後、別のAI session、別の端末、別の担当者、あるいはUI stateを失った状態から戻ったとき、利用者は実際には次を再構成します。

- 何をしようとしていたのか。
- どこまで進んでいたのか。
- 何を知っていたのか。
- 何をまだ知らなかったのか。
- 何を決めたのか。
- なぜそう決めたのか。
- その後何が変わったのか。
- いま何を見直すべきか。

この再構成に大きな負荷がかかれば、canonical recordが正しくても利用者価値は弱いままです。

SEIは、判断記憶を単に保管するのではなく、**判断文脈を壊れにくい外部認知基盤として外在化し、必要なときに再び思考へ戻せる状態にすること**を価値とします。

## 3. 外部研究から得られる示唆

本節の研究はSEIの規範上の正本ではありません。Product hypothesisを反証可能にし、prototype / human reviewで観測すべき点を選ぶための参考です。

### 3.1 中断後の再開には文脈の再構成が必要である

中断研究では、task goalの再活性化や文脈手掛かりが再開を助けることが報告されています。長い中断では、working memoryだけでなく外部環境からのcontext reconstructionが重要になります。

これはSEIに対し、「すべてを保存する」よりも、**再開時に正しいcontext cueを出せること**を評価すべきことを示唆します。

### 3.2 外部記憶は有効だが、壊れやすい外部記憶への依存にはコストがある

cognitive offloading研究では、メモ等の外部記憶が内部記憶負荷を下げ、task performanceを助ける一方、offload先を突然失うと性能が悪化し得ることも整理されています。

SEIがchat historyや一時UIを外部記憶として使うだけなら、同じ脆弱性を抱えます。

したがって価値は、単に「外へ覚えさせる」ことではなく、**transient surfaceを失ってもcanonical meaningから再構成できる耐久的なoffloading**にあります。

### 3.3 再開手掛かりはrawな履歴より構成の仕方が重要になり得る

programming taskの研究では、開発者が中断後の再開にnote-takingを多用しており、自動生成されたcontextual cueがnoteだけより再開を助けた実験結果があります。

SEIにとって重要なのは「大量の履歴を見せること」ではなく、Current question、Decision、basis、unresolved、post-decision change等の**意味のある再開手掛かり**をcanonical dataから作れるかです。

### 3.4 AIは訂正可能でなければ判断継続性を弱める

Human-AI Interaction研究では、AIの誤りを容易にdismiss / correctできること、不確実なときにgracefully degradeすること、利用者へsystem behaviorや変更を理解可能にすることが重要とされています。

AIのsuggestionが直接canonical authorityになる設計は、Decision Continuityと逆方向です。

SEIではAIをprovisionalな共同作業者として扱い、利用者または許可された主体が意味変更を確認・訂正・却下できることを重視します。

## 4. Decision Continuityの五つの側面

Decision Continuityは一つのscoreではなく、少なくとも次の五つの継続性が同時に壊れていない状態として考えます。

### 4.1 Temporal continuity — 時間をまたげる

中断、休止、担当変更の後でも、過去の記憶力やchat履歴へ依存せず再開できる。

### 4.2 Epistemic continuity — 認識状態を取り違えない

当時知っていたこと、Unknown / Conflict、後から得た情報を分けられる。

```text
what is known now
  != what was known at Decision time
```

### 4.3 Agency continuity — 誰が何を提案・判断したかを失わない

AI、他者、人間自身のRecommendation、Decision、Authorityを混同しない。

### 4.4 Realization continuity — 手段が変わっても続けられる

AI model、Provider、workflow、UI、runtime、Storage等が交換されても、判断の意味を持ち越せる。

### 4.5 Control continuity — AIや自動化が失敗しても仕事を続けられる

AI suggestionを修正・却下でき、AI unavailableでもmanualなopen / read / record / review / reopenが成立する。

## 5. V1〜V8との関係 — V9にはしない

Decision Continuityは既存Value Axisの重複ではなく、複数軸が利用者の一つの仕事で同時に成立した結果です。

| Value Axis | Decision Continuityへの寄与 |
|---|---|
| V1 Historical Reconstruction | 当時のbasisへ戻れる |
| V2 Semantic Separation | Observation / Recommendation / Decision等を取り違えない |
| V3 Revision Integrity | 新情報で過去を上書きしない |
| V4 Provider Independence | 手段交換後も判断文脈を継続できる |
| V5 Uncertainty Preservation | 未解決を消さず次回へ持ち越せる |
| V6 Human / AI Readability | 人間とAIの双方が続きを読める |
| V7 Progressive Explicitness | 継続利用の入力負担を抑えつつ必要時に深められる |
| V8 Execution Independence | workflow / runtime交換後も判断記憶が残る |

```text
Decision Continuity
  = cross-axis Product Outcome
  != V9
  != new Universal semantic entity
```

V9を追加すると、既存軸の受入れと同じ内容を別名で再採点し、重大な欠損を総合scoreで隠す危険があります。

## 6. SEIが生む価値の構造

SEIのProduct Valueは、概念的には次の差分として考えられます。

```text
Decision Continuity value
  ≈ avoided reconstruction cost
  + avoided semantic drift / false recollection
  + preserved ability to revise and switch providers
  + reduced dependence on transient AI / UI state
  - capture / review / explicitness overhead
```

これは金額換算式やUniversal KPIではありません。

重要なのは、SEI自身が記録負担を増やすだけなら価値が成立しない、という停止線です。

### 価値が大きくなりやすい仕事

- 判断寿命が長く、数日〜数年後に戻る可能性がある。
- 中断・引継ぎ・並行作業が多い。
- AIや外部Providerが複数関与する。
- 情報が後から更新される。
- Unknown / Conflictを抱えたまま進める。
- 「当時なぜそうしたか」の誤再構成コストが高い。
- ProviderやAI modelが途中で変わる可能性が高い。

### 価値が小さくなりやすい仕事

- 数分で完結し再訪しない。
- deterministicで判断がほぼない。
- raw outputだけ残せば十分である。
- capture overheadの方が再構成コストより大きい。

SEIをあらゆるtaskへ広げるのではなく、**Decision Continuityの損失が現実の問題になる領域からProduct fitを探す**べきです。

## 7. 他の記録手段との差は「形式」ではなくcontinuity guaranteeで見る

SEIはchat、note、wiki、audit log、workflow、issue tracker等を価値の低いものとして否定しません。それらは有効なArtifact / Surface / Providerになり得ます。

違いは、何をProduct guaranteeとして引き受けるかです。

### raw chat / transcript

会話の流れは豊かですが、Observation / Recommendation / Decision / historical basis等の区別を後から再構成する責務が利用者側に残ることがあります。

### note / document

柔軟で人間には読みやすい一方、current stateとhistorical basis、Unknown、lineage、AI suggestionのrole等を一貫して機械利用できるとは限りません。

### workflow / audit log

state transitionやeventは強く残せますが、なぜその判断をしたか、何が不明だったか、Recommendationをどう扱ったかは別途必要になることがあります。

SEIの差別化仮説は、これらを置き換えることではありません。

```text
existing tools
  + SEI canonical meaning / continuity layer
  → durable decision context
```

この仮説も、実利用比較で価値が確認できなければ維持しません。

## 8. Product Value hypothesisを反証可能にする

Decision ContinuityをProduct Valueへ置くなら、「SEIの方がよいはず」という主張だけでは不十分です。

ISSUE-000073のhuman reviewでは、可能な範囲で単純な代替手段とのcounterfactualを持ちます。

例:

```text
A: raw chat / chronological notesだけから再開
B: SEI canonical stateからResume Briefで再開
```

比較で見るのはspeedだけではありません。

### Orientation

- current questionを正しく言えるか。
- current DecisionをRecommendationと混同しないか。
- unresolvedを発見できるか。

### Historical integrity

- Decision後のObservationを、当時から知っていたbasisとして誤帰属しないか。
- current artifactでpast Decisionを読み替えないか。

### Correction / control

- 誤ったAI suggestionを発見・修正・却下できるか。
- AI unavailableでも作業を続けられるか。

### Burden

- first useful saveまでの入力負担。
- resumeまでの時間と操作。
- audit detailへ降りる回数。
- 継続利用したいと感じるか、その理由は何か。

## 9. Product Value Gate

first sliceが技術的にPASSしても、次が確認できなければDecision ContinuityのAdoption / Outcome Evidenceとはしません。

1. 利用者がtransient stateなしで判断の現在地へ戻れる。
2. その再開がsemanticに正しく、過去と現在を混同しない。
3. raw transcript / simple note等の妥当な代替と比べ、少なくとも一つの重要なfailureまたは負担を実質的に減らす。
4. capture / review overheadが価値を相殺していない。
5. AI支援を増やしても利用者の訂正可能性とDecision Authorityが弱くならない。

初期prototypeでは固定数値thresholdをStable Requirementにしません。

結果が次のいずれであっても有効なEvidenceです。

- 明確な価値差がある。
- 特定種類の判断だけ価値差がある。
- semantic integrityは高いが操作負担が大きすぎる。
- raw note / chatで十分で、SEIの追加構造に価値差がない。

最後の結果であればProduct hypothesisを修正します。

## 10. 設計への帰結

Decision Continuityを中心価値へつなぐと、first sliceの設計優先順位は次になります。

1. **resume accuracy before feature breadth** — 機能数より、正しく戻れること。
2. **change visibility before summary fluency** — 流暢な要約より、何が後から変わったかを区別すること。
3. **correction before autonomy** — AI自律性より、修正・却下・再分類可能性。
4. **durable canonical cues before chat memory** — chat contextより、再生成可能なcanonical Projection。
5. **low capture tax before exhaustive explicitness** — 最大記録量より、価値を損なわない最小明示。
6. **counterfactual value before scale** — team / hosted展開より、single-userで代替手段を上回る価値があるかの確認。

## 11. Evidence状態

```text
Decision Continuity as Product Value synthesis: Design baseline
first Product Slice mapping: Design baseline
REQ-0023 / SCN-0019 formalization: Accepted / Design Satisfied
E1-E8 prototype / test source: Available
Evidence runner / verifier / one-command capture: Available
E1-E8 actual Go 1.25.x execution: Not Yet Verified
H1 resume usability Evidence: Not Yet Observed
H2 human comparative Evidence: Not Yet Observed
Decision Continuity Product Value: Not Established
Operational Evidence: Not Yet Verified
Adoption / Outcome Evidence: Not Yet Verified
```

既存のContract / Interaction / Packaging probe PASS、REQ-0023 / SCN-0019のformalization、E1〜E8 sourceや受入れtoolingの存在を、Decision Continuityの利用者成果へ昇格させません。actual Executable PASSとhuman observationを分離し、H1 / H2が未観測の間はProduct ValueをEstablishedと扱いません。

## 12. 参考研究

- Trafton, J. G., Altmann, E. M., Brock, D. P., & Mintz, F. E. (2003). *Preparing to resume an interrupted task: effects of prospective goal encoding and retrospective rehearsal*. International Journal of Human-Computer Studies, 58(5), 583–603. DOI: `10.1016/S1071-5819(03)00023-5`.
- Parnin, C., & DeLine, R. (2010). *Evaluating cues for resuming interrupted programming tasks*. CHI 2010, 93–102. DOI: `10.1145/1753326.1753342`.
- Labonté, K., & Vachon, F. (2021). *Resuming a Dynamic Task Following Increasingly Long Interruptions: The Role of Working Memory and Reconstruction*. Frontiers in Psychology, 12:659451. DOI: `10.3389/fpsyg.2021.659451`.
- Richmond, L. L., & Taylor, R. G. (2025). *The benefits and potential costs of cognitive offloading for retrospective information*. Nature Reviews Psychology, 4, 312–321. DOI: `10.1038/s44159-025-00432-2`.
- Amershi, S., et al. (2019). *Guidelines for Human-AI Interaction*. CHI 2019. DOI: `10.1145/3290605.3300233`.

これらの研究結果をSEIのRequirementへ直接輸入しません。Research EvidenceとSEI Product Evidenceを分離し、実際のprototype / human reviewで再検証します。

## 13. 関連文書

- `SEI_PRODUCT_VALUE.md`
- `SEI_VALUE_PROPOSITION.md`
- `SEI_VALUE_MODEL.md`
- `SEI_VALUE_ACCEPTANCE.md`
- `../interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md`
- `../../plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`

## 14. Natural Japanese review

既存Product Value、V1〜V8、resume-first Product Sliceを起点に、中断・task resumption、cognitive offloading、Human-AI Interaction研究をProduct hypothesisの反証材料として照合した。

その結果、resume-firstをUI機能として独立させるのではなく、「時間・Surface・AI・Provider・情報更新をまたいで、過去を捏造せず判断の続きを始められる」というDecision Continuityへ統合した。Decision ContinuityはV1〜V8の横断Outcomeであり、V9やUniversal型へは昇格させていない。

また、semantic integrityが高いだけではProduct Valueとせず、raw chat / simple note等の妥当な代替と比較して再構成負担・誤帰属・AI correction・継続利用負担に実質的な差があるかをAdoption / Outcome側の停止線とした。2026-09-18時点ではREQ-0023 / SCN-0019のDesign formalizationとE1〜E8のtest / capture基盤まで進んでいるが、actual Go 1.25.x executionはNot Yet Verified、H1 / H2はNot Yet Observed、Decision Continuity Product ValueはNot Establishedである。意味、要求強度、Evidence階層を混同しないよう再監査し、自然な日本語として全文を整えた。