# ISSUE-000078: Decision成立前のInquiry Continuityを比較実証する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0028**  
Updated: 2026-09-14

## Goal

Decisionがまだ成立していない長期的なInquiryについて、時間・AI session・担当者・Surfaceが変わっても、**何を気にしていたか、何を観察し、何がまだ分からず、次に何を確かめようとしていたかを、過去を捏造せず再構成して探索を続けられること**がSEI固有のProduct Valueになり得るかを、単純な代替手段との比較を通して反証可能にする。

本Issueでは、この状態を仮に**Inquiry Continuity**と呼ぶ。

Inquiry Continuityは現時点で新しいValue Axis、Universal semantic entity、Stable Requirementではない。

ISSUE-000077のBrand World Product Value Discovery Reviewで、Decision ContinuityがDecision成立後の継続性を強く扱う一方、Decision以前の探索状態については独立したProduct failureが十分に検証されていないことが見つかったため、その差が実利用上意味を持つかを確認するためのfollow-up探索である。

最終的には、次のいずれかをEvidenceに基づいて判断できる状態を目指す。

```text
A. current V1〜V8 / Decision Continuityで十分
B. Decision Continuityの適用範囲を広げれば十分
C. Cognitive Continuityという上位Product Outcomeへ再整理する価値がある
D. Inquiry Continuityを独立したcross-axis Product Outcomeとして扱う必要がある
E. SEIの追加構造はraw chat / noteに対して実質的な価値差を生まない
```

どの結論も正当な成果とする。

## Background

### 1. Decision Continuityとの違い

currentのDecision Continuityは、利用者が時間を置いて戻ったときに、current question、Decision、basis、Unknown / Conflict、Decision後の変化、reopen condition等へ戻れることを中心にしている。

これはSEIの強いProduct Value hypothesisであり、ISSUE-000073でresume-first Product Sliceとしてactual prototype / human reviewへ進めている。

一方、実務の認知活動には、Decisionが一度も成立しないまま長期間続くものがある。

たとえば次のような状態である。

- 何かがおかしいと感じるが、まだ問題を特定できない。
- 複数のObservationはあるが、共通原因があるか分からない。
- 問い自体を何度も書き換えながら調査している。
- いくつかのHypothesisがあるが、どれもRecommendationへ進めるほど強くない。
- 調査を数日・数週間止めた後、別の担当者や別のAIが続きを引き継ぐ。

この段階では「Decision basisへ戻る」というanchorが存在しない。

そのため、Decision Continuityがそのまま十分なのか、より手前の認知状態に別のProduct guaranteeが必要なのかをactualに確認する必要がある。

### 2. Brand World Discoveryから得た問い

ISSUE-000077では、SEI Cognitionの「井」を、答えを持つ中心ではなく、まだ十分に形を得ていないものへ近づき、問いを置き直せる共有認知基盤として読み直した。

そのReviewで最も独立性が高く残ったのが、`Durable Cognitive Aperture`という仮説だった。

ただし、本Issueは「井」という比喩を実証するものではない。

検証するのは、**Decision前のInquiryを失うというactualなProduct failureが存在し、それをSEIが妥当な負担で改善できるか**である。

```text
brand insight
  → Product hypothesis
  → actual comparison
  → Product decision
```

の順序を維持する。

### 3. current semantic baselineとの関係

SEIはすでにQuestion、Observation、Unknown、Conflict、Hypothesis等を扱い、不確実性を消さず、human / AIが同じcanonical meaningへ戻る方向を持っている。

したがって、このIssueの目的は新しい型を追加することではない。

既存の意味境界を実利用へ組み合わせたときに、Decision前の探索を再開するProduct Valueが本当に成立するかを見る。

もし既存意味だけで十分に成立するなら、新しいUniversal概念を追加しないことが最善である。

## Product hypothesis

仮説は次である。

> SEIは、DecisionがまだないInquiryについても、外在化されたQuestion、Observation、Unknown、Hypothesis、Artifact reference、Provenance等を意味のある再開手掛かりとして保持・投影することで、raw chatやchronological noteだけに比べ、長い中断後の再構成誤りと再探索負担を減らせる可能性がある。

この価値が成立するには、単に多くのrecordを残せるだけでは不十分である。

```text
stored inquiry artifacts
  != Inquiry Continuity
```

利用者が実際に、過去の探索状態を誤って作り直さず、次の有用な探索へ戻れる必要がある。

## Product failure candidates

少なくとも次をfailure候補として扱う。

1. 数日後に戻ると、最初に何が気になっていたかを思い出せない。
2. 後から得た情報を、当初から知っていたObservationとして誤って再構成する。
3. AI summaryが複数のHypothesisを一つの確定解釈へ潰す。
4. chat transcriptを失うと、Questionの変遷や未解決点も失う。
5. 担当者が変わると、どのObservationが重要視されていたか分からない。
6. Unknownが「まだ調べていない」のか「調べたが分からなかった」のか区別できない。
7. 大量のcaptureを要求した結果、利用者が記録をやめる。
8. SEIの構造を使っても、raw chat / noteより再開品質が実質的に良くならない。
9. Inquiryを長く保持することで、不要な探索を終えられず認知負債が増える。
10. AIが次の問いを積極的に生成しすぎ、元のconcernが見えなくなる。

8〜10も重要な反証である。

## Questions

1. Decision前のInquiryを再開するとき、利用者が最低限取り戻す必要があるのは何か。
2. current Questionだけでなく、Questionがなぜ生まれ、どう変わったかまで必要か。
3. Observation / Hypothesis / Unknownのどこまでを再開Projectionに出すと、情報量と正確性のbalanceがよいか。
4. post-observationな新情報を、initial concernやhistorical observationへ混ぜないために何が必要か。
5. raw chat、chronological note、issue tracker等と比べ、SEI canonical meaningはどのfailureを減らせるか。
6. Inquiry Continuityのために新しいUniversal entityは本当に必要か。existing reference / artifact / relationだけで十分ではないか。
7. `Inquiry`、`Case`、`Workspace`、`Session`等のnavigation概念をProduct-localに留めたまま再開できるか。
8. AI-generated summary / next-question suggestionをprovisionalのまま利用し、元のUnknownやHypothesisを失わないInteractionはどうあるべきか。
9. どの時点でInquiryを閉じる、休眠させる、Decisionへ接続するのが自然か。
10. Inquiryを継続可能にする追加capture / review burdenは、利用者価値を上回らないか。
11. Inquiry Continuityが成立した場合、Decision Continuityの拡張、Cognitive Continuityへの再編、独立Outcomeのどれが最も重複が少ないか。
12. 個人Inquiryで得た結果をteam / organizationへ共有するとき、Selective DisclosureとResponsibilityをどう保つか。

## Constraints

- Inquiry Continuityは現時点でV9ではない。
- `Inquiry`をUniversal semantic entityとして先取りしない。
- `Workspace` / `Case` / `Session` / `Thread`をProduct navigation都合だけでCoreへ追加しない。
- private chain-of-thoughtや非外在化の心的状態を保存条件にしない。
- AI summaryをhistorical Observationやcanonical interpretationへ黙って昇格させない。
- current informationで過去のQuestion / Observationを上書きしない。
- Questionが変化したことと、過去のQuestionが誤りだったことを同一視しない。
- Unknown / Conflict / Hypothesisを早く閉じることをProduct successとみなさない。
- 逆に、未解決を永続的に残すこと自体もProduct successとみなさない。
- Brand World SourceをRequirement根拠にしない。
- raw chat / simple note等の代替手段を弱い比較対象として意図的に不利にしない。
- structured record量やschema completenessをOutcome指標にしない。
- Product Valueの評価とMethod output quality評価を混同しない。

## Required scenarios / experiments

### E78.1 — Long interruption without Decision

一つのInquiryについてQuestion、Observation、Unknown、Hypothesisを残すが、Decisionは作らない。

数日相当のcontext lossを再現し、transient UI state / chat contextを破棄した状態から再開する。

確認する。

- original concernを説明できるか。
- current Questionを説明できるか。
- 何がObservationで何がHypothesisか区別できるか。
- unresolvedを列挙できるか。
- next useful investigationへ進めるか。

### E78.2 — Raw chat / chronological note comparison

同じ素材を、少なくとも次の方法で保持する。

```text
A. raw chat / transcript
B. chronological note
C. SEI canonical meaning + derived resume Projection
```

比較するのはspeedだけではない。

- historical attribution error
- Observation / Hypothesis confusion
- unresolved omission
- original concern drift
- time / effort to first useful next step
- capture burden
- correction burden

を観測する。

### E78.3 — AI summary distortion

AIにInquiry summaryとnext question候補を生成させる。

意図的に、

- uncertain observationを断定する。
- alternate hypothesisを落とす。
- later informationをinitial contextへ混ぜる。

ような誤りを含むsuggestionを与え、利用者が発見・修正・却下できるか確認する。

AI suggestion自体をcanonical factへ自動昇格させない。

### E78.4 — Handoff to another reader

元の利用者とは別のreaderがInquiryを引き継ぐ。

元の会話履歴やworking memoryを持たない条件で、

- why this matters
- what was actually observed
- what remains unknown
- what hypotheses were considered
- what to inspect next

へ到達できるか確認する。

### E78.5 — New evidence after interruption

中断後に新しいObservationを追加する。

その情報が、過去のQuestionやObservationを「当時から知っていた」状態へ遡及的に書き換えないか確認する。

### E78.6 — Quiet vs proactive assistance

AIが多数のnext question / relation候補を生成できる状況で、

- 全候補を前面表示する方式
- 必要時に候補へ降りる方式

を比較する。

見るのは好みだけではなく、original concernの保持、Unknown発見、next useful actionへの到達、attention burdenである。

### E78.7 — Closure / dormancy

長期間進展しないInquiryについて、

- active
- dormant
- closed without Decision
- connected to later Decision

のProduct上の扱いを比較する。

これらをUniversal ontologyへ先取りせず、利用者が不要なopen loopを抱え続けないためにどのProduct-local projection / navigationが必要かを観察する。

## Evaluation

固定の総合scoreは作らない。

少なくとも次を分けて観測する。

### Historical correctness

- initial concernをlater knowledgeで書き換えない。
- Observation / Hypothesis / AI suggestionのroleを取り違えない。

### Orientation

- current Questionへ到達できる。
- unresolvedを発見できる。
- next useful stepを見いだせる。

### Handoff

- 元のworking memoryがない別readerでも意味を読める。

### Control

- AI summaryを修正・却下できる。
- AI unavailableでもmanualに再開できる。

### Burden

- first useful captureまでの負担。
- resume時の読解・操作負担。
- audit detailへ降りる負担。
- 継続利用に必要なmaintenance burden。

### Counterfactual value

- raw chat / noteとの差が実質的か。
- 追加構造が生むbenefitがcapture / review overheadを上回るか。

## Deliverables

- Inquiry Continuity evaluation design。
- raw chat / note / SEI comparison fixtureまたはscenario bundle。
- human review template。
- 実行した場合のEvidence report。
- current V1〜V8 / Decision Continuity coverage audit。
- Stable Requirement化の要否判断。
- Product Value / Value Model / Decision Continuity / Product Visionの再編が必要かどうかのDecision record。

## Resolution

次を満たしたときResolvedとする。

- Decisionが存在しないInquiryについて、再開時のProduct failureをactualに観測できる比較設計を実施した。
- raw chat / chronological note等の妥当な代替と比較した。
- semantic correctnessとresume speedを分けて評価した。
- capture / review overheadを評価した。
- AI summaryの誤りとcorrection boundaryを検査した。
- current V1〜V8 / Decision Continuityで十分かを再監査した。
- 新しいValue Axis / Stable Requirement / Universal型が必要か、No ChangeかをEvidenceに基づいて判断した。
- 生成・更新した文書を自然な日本語へ全文再ドラフトし、意味・Evidence高さを最終監査した。

Designだけ完成してもResolvedにしない。

```text
Design Evidence
  != Executable / Human Review Evidence
  != Adoption / Outcome Evidence
```

## Reopen conditions

- Decision前の長期Inquiryで、current設計では説明できない再開failureが新たに見つかった。
- team / organization handoffでsingle-user比較とは異なるfailureが確認された。
- AIの能力向上によりcapture / summaryの前提が大きく変わった。
- Product ValueがDecision中心からCognitive Continuity中心へ再基線化された。
- Inquiry Continuityのために追加したProduct mechanismが過剰なcapture burdenを生んだ。

## Verification

本Issueでは、最初からStable Requirement checkerを増やすことを目的にしない。

中心となるEvidenceは、counterfactual comparisonとhuman reviewである。

```text
semantic artifacts exist
  != Inquiry Continuity proven

resume is fast
  != resume is historically correct

AI summary is fluent
  != inquiry meaning preserved
```

実験用のtoolやfixtureを作成した場合は、その実行結果の高さをDesign / Executable / Adoption等で正確に区別する。

## Natural Japanese review

本Issueは、「井の中央に問いを置ける余白がある」というブランド上の洞察を、そのまま仕様へ変換せず、Decision以前のInquiryを失うというProduct failureへ翻訳して起票した。

Decision Continuityとの違いを明確にしつつ、最終的にはDecision Continuityの拡張で十分、より広いCognitive Continuityが必要、独立したInquiry Continuityが必要、あるいはSEIの追加構造に価値差がない、という複数の結論を同じ強さで許容している。

意味、仮説強度、未検証範囲を固定した後、**自然な日本語として背景・failure・実験・停止線が連続して読めることを最重要視して全文を再ドラフトし、最終意味監査を実施済み**とする。
