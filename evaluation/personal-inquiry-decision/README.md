# SOZA Personal Inquiry / Decision Prototype

更新日: 2026-09-10  
状態: **Evaluation-only Product Hypothesis / Prototype Boundary**

## 1. 目的

SOZAのProduct Valueを、組織導入や複雑なProvider連携より先に、**一人の利用者が自分のために使って価値を感じられる最小領域**で検証する。

最初の対象は、数分で終わる単発質問ではない。一方、組織的な承認、監査、複数人協働がなければ成立しない仕事にも置かない。

対象を次のように絞る。

> **AI、Web、ファイル、手元のメモを行き来しながら、数日から数か月かけて比較・検討する個人の判断について、後から「何を考えていたか」「何を根拠に決めたか」「何がまだ分からないか」「何が変われば見直すか」へ短時間で戻れるようにする。**

仮称を **Personal Inquiry / Decision Workspace** とする。これは製品名の決定ではない。

## 2. なぜこの領域から始めるか

SOZAのcurrent Product Valueには、個人利用だけでも必要になる価値が多い。

- V1 Historical Reconstruction — 過去の判断時点へ戻る。
- V2 Semantic Separation — Observation、Recommendation、Decision等を混ぜない。
- V3 Revision Integrity — 後から得た知識で過去を上書きしない。
- V5 Uncertainty Preservation — 分からなかったことや食い違いを残す。
- V6 Human / AI Readability — 人間とAIの双方が同じ意味を読める。
- V7 Progressive Explicitness — 軽く始め、必要なときだけ詳しくする。
- V8 Execution Independence — AIや会話環境が変わっても判断記憶を残す。

V4 Provider Independenceも関係するが、最初の価値検証では複数Provider交換そのものを主目的にしない。

個人利用ではResponsibility holderは多くの場合一人であり、enterprise IdP、RBAC、複数組織のSelective Disclosure等を初期価値検証から外せる。そのためSOZAの認知・判断部分そのものが役に立つかを確認しやすい。

## 3. Target Job

利用者が行いたいことを次の一文に絞る。

> **以前の調査やAI会話を読み直し直すことなく、判断の現在地と当時の根拠へ戻り、新しい情報が来たらそこから再検討したい。**

### 適する題材

最初のdogfoodingでは、低〜中程度の影響で、複数回の検討が自然に発生する題材を使う。

- 個人プロジェクトの技術・ツール選択
- 学習方法や教材の比較
- 日用品・サービス・機器等の比較検討
- 旅行や趣味の計画上の選択
- 自宅環境や個人作業環境の改善判断

### first sliceから外す題材

最初のProduct Value検証では、次を主対象にしない。

- 医療、法律、重大な資産判断等のhigh-stakes decision
- 多人数の承認や職務権限が中心となる業務
- 一度きりで後から読み直す必要がほぼない質問
- deterministicな変換だけで完結する処理
- 汎用タスク管理、日記、全文書管理そのもの

除外はSOZAが将来扱えないことを意味しない。個人レベルの中核価値を先に分離して測るためのprototype scopeである。

## 4. 先鋭化したCandidate Product Requirements

以下はこのprototypeのCandidate Requirementであり、current Stable Requirementへ自動昇格させない。

### P-C1 — 一つの問いだけで始められる

最初の必須入力は、原則として「何を考えたいか」という問いだけでよい。

Goal、Constraint、Source、Responsibility、Exact Binding等を開始時に一律要求しない。必要になった意味は後から追加できる。

### P-C2 — 情報追加を分類作業にしない

利用者は文章、URL由来の要点、ファイル由来の要点、AIから得た情報等を自然な形で追加できる。

SOZA側は必要に応じてObservation、Interpretation、Unknown、Conflict等の候補を支援できるが、利用者にContract型名の選択を常時要求しない。

AIによる自動分類をcanonical truthにはしない。

### P-C3 — 「まだ分からない」を一級の現在地として残す

Unknown、Conflict、保留事項を、未入力やエラーとして消さない。

Decisionを記録しても、それらを自動的にresolvedへ変更しない。

### P-C4 — AIの提案と自分の判断を別に残せる

Recommendationが存在しても、利用者自身のDecisionがまだ無い状態を自然に扱える。

Decisionを記録するとき、RecommendationをそのままDecision identityへ流用しない。

### P-C5 — Decisionの最小記録は「何を決めたか」だけではない

個人利用のlightweight Decisionでも、後日の再読に必要な範囲で次へ戻れる必要がある。

- 何を決めたか。
- 主なbasisは何だったか。
- 何が未解決のままだったか。
- 何が起きたら見直すか。

詳細な監査情報を常時表示することは要求しない。

### P-C6 — 再度開いたとき、5つの問いへすぐ戻れる

light viewから、少なくとも次を読み取れることを目標とする。

1. 今回、何を考えていたのか。
2. 現在重要なObservationは何か。
3. 何がまだ分からない、または食い違っているのか。
4. RecommendationとDecisionはそれぞれ何か。
5. 何が変われば再検討するのか。

この5項目をUIの固定field layoutとはしない。個人利用での再定位に必要な意味上の質問である。

### P-C7 — 後から来た情報で過去Decisionを書き換えない

Decision後のObservationは新しい情報として追加する。

過去Decisionのbasisへ遡って混入させず、必要ならreview / reopen候補として扱う。

### P-C8 — AIが変わっても、無くても、判断記憶は読める

特定LLM、Prompt、chat threadが利用不能になっても、保存済みのInquiry、Observation、Unknown / Conflict、Recommendation、Decision、basis、reopen informationを人間が読めることを目標とする。

AIは入力整理、Cognitive Method、Recommendation、説明等を補助できるが、保存済み判断記憶の読解に必須としない。

### P-C9 — 最初はsingle-user localで成立できる

first prototypeはlogin、team workspace、enterprise directoryを必須にしない。

current Local Single-Node Packagingの方向と整合する形で、一人が自分の判断記憶を保存・再開できることを優先する。

### P-C10 — 人間向け再読と機械向け再利用を両立する

人間向けlight viewだけでなく、AIやtoolが後から同じcanonical meaningを構造化して読めることを維持する。

ただし、prototypeでAPI / MCP等のsupported protocolを先に固定しない。

## 5. first prototypeで意図的に削るもの

価値検証をぼかさないため、次は初期画面・初期workflowの中心に置かない。

- Capability Provider選択UI
- Authorization / delegation UI
- multi-user collaboration
- workflow automation
- agent orchestration
- 汎用document repository
- 万能knowledge graph
- dashboard / BI
- 複雑なontology editor
- sparse associative cognitionを含む高度な自動想起

Sparse Associative Cognitive Substrateは、後から関連Inquiry / Artifactを想起する補助層として評価できる。ただし、Personal Inquiry / Decision WorkspaceのProduct Valueは、この認知層が無くても成立する必要がある。

## 6. 最小の利用体験

### Session A — 始める

利用者は問いを一つ入力する。

その後、調べながらObservation、気になる点、分からない点を追加する。AIを使ってもよいし、人間だけで入力してもよい。

### Session B — 比較して決める

AIまたは人間のRecommendationがあればDecisionとは別に保持する。

利用者が決める場合、Decisionと主要basis、未解決点、reopen conditionを必要な範囲で残す。

### Session C — 後から戻る

元の長い会話や資料を最初から読み直さず、light viewで5つの再定位質問へ答える。

必要な場合だけsource、provenance、revision等のdetailへ降りる。

### Session D — 新しいEvidenceが来る

Decision後に新しいObservationを追加する。

過去Decisionは書き換えず、新しいObservationがreopen conditionに関係する場合は再検討できる。

## 7. Product Valueをどう確認するか

このprototypeでは、構造が正しいだけでは価値が確認できたとは扱わない。

### 比較対象

最低限、同じ題材について次を比較する。

1. **chat-only** — AIとの会話履歴だけを残す。
2. **final-note** — 最終結論と短いメモだけを残す。
3. **SOZA prototype** — 問い、主要Observation、Unknown / Conflict、Recommendation、Decision、basis、reopen informationを意味上分けて残す。

### 再定位タスク

一定時間を空けて再開し、次を確認する。

- 5つの再定位質問へ答えられるか。
- 元のchat / sourceをどれだけ読み直す必要があったか。
- Decision時に未解決だった点を取り落とさないか。
- 後から得た情報を、当時から知っていた情報と混同しないか。
- 新しいEvidenceから再検討を始められるか。

### 利用負担

価値があっても記録負担が大きければ個人では継続されない。

そのため、少なくとも次を別軸で観察する。

- Inquiry開始時に要求された入力数
- 情報一件を追加するときの明示操作数
- Decision記録時に強制された項目数
- sourceやchatを再読した時間 / 回数
- light viewだけで再定位できたか
- 利用者が「次の題材にも使いたい」と自発的に判断するか

単一の総合scoreへ潰さない。

## 8. prototype-level value gate

以下を満たした場合に、**個人向けProduct Hypothesisを次段階へ進める根拠が得られた**と扱う。

1. 複数の低〜中影響な題材で、SOZA prototypeから5つの再定位質問を再構成できる。
2. 新しいEvidence追加後も、過去Decisionのbasisを当時の状態として読める。
3. chat-only / final-noteと比べ、未解決点や判断理由を回収するための再読が明確に減るケースが確認できる。
4. その改善のために、利用者が毎回監査帳票のような入力を強制されない。
5. 特定LLMや元chat threadを失っても、保存した判断記憶だけで現在地を読める。
6. 利用者が別の題材でも再利用したいと判断する。

1〜5はProduct Valueのmechanicsとusable interaction、6は個人レベルのAdoption兆候を見る。

一件の成功だけで一般的なAdoption / Outcome Evidenceへ昇格させない。

## 9. falsification / pivot条件

次の結果が繰り返される場合、Product Shapeを見直す。

- chatの要約だけで同程度に再定位でき、SOZAの意味分離が実質的な追加価値を生まない。
- Unknown / Conflict / basis / reopen conditionを残しても、後日の行動や再検討に使われない。
- 記録負担が高く、利用者が継続利用を避ける。
- Decision Memoryより単なる検索・全文履歴の方が主要価値になる。
- AIなしでは保存済み情報の意味を読み取れない。
- 個人利用では再構成よりもtask execution / reminder等の方が支配的ニーズとなる。

この場合、SOZAのProduct Value自体を直ちに否定するのではなく、個人向けfirst wedgeが不適切だった可能性と、Universal Coreの意味分離が過剰だった可能性を分けて検討する。

## 10. current判断

current Product Value、Product Interaction、Local Single-Node Packaging、既存Requirementを照合すると、この個人向けprototypeを作るために新しいUniversal semantic conceptは必要ない。

特に既存REQ-0001、0002、0005、0006、0010、0011、0014、0015、0019、0021で中核を説明できる。

一方、**個人が実際に継続利用するか、chatや通常のnoteより再定位負担が下がるかは未実証**である。

したがって現時点の主張は次に限定する。

```text
personal product wedge is coherent with current SOZA value
  + candidate requirements can be stated without new Universal semantics
  + value can be falsified by a small single-user experiment

!= personal Adoption / Outcome Evidence available
!= production UX validated
!= SOZA is proven useful for every personal decision
```

次の実装課題は、既存canonical meaningからこの5-question light viewを生成し、Decision後のObservationをhistorical basisへ混入させない最小single-user prototypeを作ることである。
