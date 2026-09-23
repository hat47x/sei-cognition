# ISSUE-000078: Decision成立前のInquiry Continuityを比較実証する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0028**  
Updated: 2026-09-22

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

#### E78.2 / E78.4 / E78.5 exact execution-input binding — 2026-09-22

human reviewを開始する前のrepository-local mechanics gateについて、正規入口 `inquiry_continuity_review_runner.py` とそのimport closure、focused tests、matched-set manifest、3 source fixtureをexact sourceへ固定した。

bindingは次である。

```text
evaluation/personal-inquiry-decision/evidence/issue-000078/
  e78_matched_review_execution_input_binding_2026-09-22.json
```

- exact source commit: `1de126f6cddea9eac4cef2c5aaeb89b044f1f89b`
- binding Git blob SHA-1: `90178c356b7a1eea0f5a4a36230cf65efebc49b6`
- bound files: 15
- execution tracking: GitHub Issue #576

15 filesは、canonical runner / import closure 7、focused tests 4、matched-set manifest 1、source fixtures 3で構成する。actual Python executionでは、15 / 15 Git blob SHA-1 exact一致を確認した後だけfocused testsへ進む。

このbinding自体はPASSを意味しない。

```text
exact-source binding
  != matched-review local mechanics PASS
  != human review result
  != actual long-gap Evidence
  != actual team handoff
  != Product Value decision
  != Stable Requirement authorization
```

human responseそのものをAI生成してhuman reviewとして記録しない。local mechanics PASSがactualに固定されるまではhuman review開始条件を満たしたと扱わない。

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

synthetic matched reviewでのhandoff刺激と、実際の別readerによるteam handoffは分けて扱う。actual team handoffの実観測追跡は **GitHub Issue #592** に一本化する。#592では新しいrunner / schema / fixtureを追加せず、既存 `dogfood_cli.py handoff` projectionを最初の提示面として使い、別readerのhuman-authored responseと必要なsource/chat reopenを観測する。

現在の`dogfood_evaluation_cli.py resume-add`はresumption surface用であり、`sei-handoff`を持たない。そのenumをactual handoff記録の都合だけで拡張せず、最初のactual observationは必要最小限のanonymized Evidence / checkpointとして保持する。

```text
synthetic E78.4 review
  != actual team handoff

handoff projection renders
  != another reader understood the Inquiry
```


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

## Execution readiness checkpoint — 2026-09-16

本Issueは、比較設計そのものを考える段階から、human reviewを安全に実施できる評価基盤を揃える段階まで進んだ。ただし、ここで成立しているのは主として**Design / Executable scaffold**であり、Inquiry ContinuityのProduct Valueを示すHuman / Adoption / Outcome Evidenceではない。

### E78.1 — Long interruption without Decision

actual dogfood caseは初期化済みであり、calendar上はmulti-day条件にも到達した。しかし、2026-09-16の上流整理と継続作業でcurrent Inquiry stateへmaterialに再露出しているため、その時点をclean resumptionとして扱わない。

```text
calendar gap reached
  + material state re-exposed
  != clean cognitive resumption
```

したがって、E78.1のactual long-gap resumptionは**Not Yet Observed**のままとする。再開品質、負担、継続利用価値を推測で埋めない。

actual clean long-gap resumptionの実観測追跡は **GitHub Issue #590** に一本化する。#590は新しいrunner / schema / fixtureを追加せず、既存actual dogfood case、Orientation、evaluation sidecar、`dogfood_evaluation_cli.py resume-add`をそのまま使う。tracker自体にはunderlying InquiryのQuestion / Observation / Unknown / Hypothesisを再掲せず、読むだけで認知的gapを壊さないようにする。

```text
calendar gap
  != clean cognitive gap

Issue #590 open
  != resumption observed
```


### E78.2 / E78.4 / E78.5 — matched comparison / handoff / later evidence

3件のmatched synthetic caseと、raw chat / chronological note / SEI resumeの3条件をR1〜R3でcounterbalanceするfixture setを用意した。`matched_review_session.py`では、session開始時のfixture内容を固定し、全phase 1回答が確定するまで中断後Evidenceを開かず、全post回答が確定するまでreference state / audit materialを開かない。

さらに、`inquiry_continuity_review_analysis.py`でhuman responseの形式、historical correctness、Observation / Hypothesis / Unknownのrole separation、unresolved preservation、temporal integrity、false continuity、first useful action、source reopen、attention / correction burdenを互いに潰さず記録・比較できるようにした。総合score、ranking、winnerは生成しない。

synthetic handoffは`reader_context`として記録できるが、actual team handoffとは分ける。

現時点のEvidence高さは次のとおりである。

```text
matched fixture / stage gate / analysis scaffold
  = executable evaluation scaffold

human review result
  = Not Yet Observed

actual team handoff
  = Not Yet Observed
```

### E78.3 — AI summary distortion

E78.3の正規経路は、`inquiry_continuity_summary_distortion_probe_v1.json`と`inquiry_continuity_summary_distortion_probe.py`へ一本化した。以前並存していた`inquiry_continuity_distortion_*`系は、同じexperimentに二つのoperational pathを持たせないため廃止した。

正規probeは、certainty inflation、alternate hypothesisの脱落、later informationの遡及混入に加え、探索を早く収束させる`distorted_next_question`をevaluation stimulusとして保持する。各source fixtureはGit blob SHA-1で固定し、review packetではaudit key、reference state、post-interruption evidenceを開示しない。human responseを固定した後のaudit packetでのみ、それらを照合できる。

同一reviewerがE78.2 / E78.4 / E78.5のmatched reviewにも参加する場合は、**matched reviewを先に完了・固定してからE78.3を提示する**。意図的に歪めたsummaryやnext questionを先に見せると、その後のbase comparisonへ学習・期待・語彙を持ち込み、cleanな比較条件を汚染するためである。別reviewerを使う場合でも、元sourceに対する初期回答を固定する前に歪んだsuggestionを見せない。

repo rootからの正規経路は次である。

```text
PROBE=evaluation/personal-inquiry-decision/inquiry_continuity_summary_distortion_probe.py
PROBE_SET=evaluation/personal-inquiry-decision/inquiry_continuity_summary_distortion_probe_v1.json
EVIDENCE_TOOL=evaluation/personal-inquiry-decision/inquiry_continuity_summary_distortion_evidence.py
LOCAL_CHECKS=evaluation/personal-inquiry-decision/run_inquiry_continuity_summary_distortion_checks.py
LOCAL_RESULT=<checkout外または意図的に管理するe78-3-local-check-result.json>
REVIEW_RECEIPT=<checkout外または意図的に管理するreview-start-receipt.json>
RESPONSE=<checkout外または意図的に管理するhuman-response.json>
REVEAL_RECEIPT=<checkout外または意図的に管理するaudit-reveal-receipt.json>
AUDIT_RESPONSE=<checkout外または意図的に管理するsemantic-audit-response.json>
EVIDENCE=<checkout外または意図的に管理するe78-3-evidence.json>

# repository-local mechanics gate。probe/evidence focused unit test、canonical validate、
# 3 fixture全てのEvidence preflightを一括実行する。result JSONは上書きしない。
# result schema v2はcanonical probe semantic SHA-256、mechanics file SHA-256、
# frozen source fixtureのexpected/actual Git blob SHA-1、Python runtimeへ結びつく。
# 加えて各checkのcommand、repo相対cwd、stdout/stderrのSHA-256とbyte数を記録する。
# raw stdout/stderr本文やローカル絶対pathはresult JSONへ保存しない。
# launch errorはtype/errnoだけへ縮約し、OS messageやhost pathを保存しない。
# source fixtureがprobeのfreezeと一致しなければcheck開始前にfail-closedする。
# 保存時にもresult v2全体を再検証し、count/order/status、正規check名と
# portable command / repo相対cwdの一致、timeout / launch-error metadataの整合、
# stoppedEarlyと実行完了性の整合、first-failureで停止したprefixであること、
# non-empty execution、全checkの同一timeout、launch error時にprocess outputを持たないことも
# 検証する。さらにcontractSnapshotを
# 現在checkoutから再計算し、probe / mechanics / fixture / Python runtimeのdigest差し替えも
# 拒否する。stream digestとEvidence stoplineの改変も拒否する。
python3 "$LOCAL_CHECKS" --stop-on-failure --result-output "$LOCAL_RESULT"

# validateは3 source fixtureのGit blob freezeを全件検証し、current probe /
# response / review-start / audit-reveal schemaとtyped audit dimensionsを表示する。
python3 "$PROBE" --probe "$PROBE_SET" --repo-root . validate

# preflightはhuman review artifactを作らず、選択fixtureについてcurrent
# audit-response / durable Evidence schemaとdimension-specific allowed valuesを表示する。
# current contractはv1専用であり、pre-v1 review/audit artifactを再利用しない。
python3 "$EVIDENCE_TOOL" --probe "$PROBE_SET" --repo-root . \
  --fixture-id <fixture-id> preflight

python3 "$PROBE" --probe "$PROBE_SET" --repo-root . \
  --fixture-id <fixture-id> review \
  --review-receipt "$REVIEW_RECEIPT" \
  --reviewer-id <opaque-reviewer-id> \
  --prior-exposure <none-declared|known-material-exposure|unknown> \
  --response-authorship <human-direct|human-transcribed> \
  > <review-packet.json>

# review commandはstimulusをstdoutへ出す前に、reviewer id / prior exposure /
# response authorship / exact probe / fixture / started_atをexclusive-createの
# REVIEW_RECEIPTへ保存する。保存失敗時はstimulusを出力しない。
#
# review packetのresponse_templateはresponse schema v1で、REVIEW_RECEIPTの
# SHA-256とpre-stimulus provenanceを既に含む。answers、review provenance note、
# review burden等を埋め、audit materialを開く前にRESPONSEを固定する。
python3 "$PROBE" --probe "$PROBE_SET" --repo-root . \
  --fixture-id <fixture-id> audit \
  --response "$RESPONSE" \
  --review-receipt "$REVIEW_RECEIPT" \
  --receipt "$REVEAL_RECEIPT" > <audit-packet.json>

# audit commandはreference materialをstdoutへ出す前に、開示予定materialを先に
# canonical SHA-256へ固定し、固定済みRESPONSE、exact probe content、fixture、
# REVIEW_RECEIPT SHA-256、review started_at、audit material SHA-256、revealed_atを
# audit-reveal receipt v1へ保存する。
# packet構築に失敗した場合はreceiptを作らず、receiptが既に存在する場合も
# 上書きせずfail-closedし、reference materialを出力しない。
#
# audit-packetでreference materialを開いた後にだけsemantic auditを作る。
# audit-templateは固定済みRESPONSEと同じREVEAL_RECEIPTへ結びつく。
python3 "$EVIDENCE_TOOL" --probe "$PROBE_SET" --repo-root . \
  --fixture-id <fixture-id> audit-template \
  --response "$RESPONSE" \
  --review-receipt "$REVIEW_RECEIPT" \
  --receipt "$REVEAL_RECEIPT" > "$AUDIT_RESPONSE"

# AUDIT_RESPONSEのfindings、opaque auditor id、human authorship、completed_at等を
# post-revealに記録してからEvidenceをexportする。
# findingsは共通pass/failではなくprobe schema v1のdimension-specific contractへ従う。
# detectionはdetected/not-detected/not-applicable/not-observed、
# preservationはpreserved/not-preserved/not-applicable/not-observed、
# correction_burdenはlow/medium/high/not-observed等として異種観測を混ぜない。
python3 "$EVIDENCE_TOOL" --probe "$PROBE_SET" --repo-root . \
  --fixture-id <fixture-id> export-evidence \
  --response "$RESPONSE" \
  --review-receipt "$REVIEW_RECEIPT" \
  --receipt "$REVEAL_RECEIPT" \
  --audit-response "$AUDIT_RESPONSE" \
  --output "$EVIDENCE"
```

#### E78.3 actual mechanics checkpoint — 2026-09-19

GitHub正本のblobを固定して一時実行環境へ再構成し、Python 3.13.5でE78.3 mechanicsの一部をactual実行した。machine-readable recordは `evaluation/personal-inquiry-decision/evidence/issue-000078/e78_summary_distortion_partial_runtime_2026-09-19.json` とする。

- canonical probe `validate`: exit 0。
- probe focused tests: **23 / 23 PASS**。
- Evidence focused tests: **18 / 18 PASS**。
- Evidence focused testsのactual実行前に、preflight testがcomplete 3-fixture setではなく1 fixtureだけを渡していた点と、tamper testが元値と同じblob値を代入して実際には改変になっていなかった点をtest fixture側で修正した。production contractは弱めていない。
- canonical runner focused tests、7-check aggregate local gate、result schema v2 artifact生成は **Not Yet Verified** のままとする。
- full aggregateの追加実行では、実行環境へGitHub正本を一括取得する経路を確立できず、connectorからlocalへ再構成する途中でblob mismatchを検知した。正本一致しなかった試行はPASS / FAILのどちらにも数えず、full local gate Evidenceへ昇格させない。

#### E78.3 exact execution-input binding — 2026-09-20

前回のsource-reconstruction mismatchを実行結果と混同しないため、既存runnerへ渡すexact sourceを `evaluation/personal-inquiry-decision/evidence/issue-000078/e78_summary_distortion_execution_input_binding_2026-09-20.json` に固定した。これは新しいrunner / exporter / Evidence schemaを追加するものではなく、既存の正規local-check経路へ入る前の入力同一性を明示するsidecarである。

2026-09-20時点の `develop/v0.2.0` HEAD `e785a7ad0e7070fafe9d187f458ce9cca587a7f6` で、probe set、probe、Evidence tool、probe / Evidence / runner focused tests、runner、3 source fixtureの計10ファイルをGit blob SHA-1で再照合した。直前のE78.3 checkpointから10 blobはすべて不変であり、同時に取り込まれたSEI-B7a変更はE78.3の正本へ触れていない。

今後connector等を介して一時実行環境へ再構成する場合は、**10ファイルを同一bound commitからmaterializeし、全件のGit blob SHA-1一致を確認してからのみcanonical runnerを実行する**。1件でも不一致なら、その試行はcanonical local gateのPASS / FAILへ数えず、再構成失敗として破棄する。runnerが生成するresult schema v2も従来どおり`validate_result`成功後だけ保存する。

actual runtimeの残工程は GitHub Issue #532 `E78.3: exact-source bindingからcanonical local gateをactual実行する` に集約する。同一ISSUE-000078の継続作業として `develop/v0.2.0` を集約先に保ち、transport/reconstructionだけを理由にtopic branchを増やさない。Issue #532は10-blob一致、runner focused tests、7-check aggregate、validated result schema v2生成だけを完了条件とし、source reconstruction mismatchはcanonical PASS / FAILへ数えない。

2026-09-20、execution-input binding v1 に `execution_recipe` を追加し、repository-root要件、runner focused test command、canonical aggregate command、期待check数7、result schema v2、exclusive-create、実行後に記録すべきprovenanceを機械可読で固定した。これはrunner追加ではなく既存canonical pathの再現手順を固定するものであり、runtime PASSそのものではない。

同日のtransport試行は `evaluation/personal-inquiry-decision/evidence/issue-000078/e78_summary_distortion_materialization_checkpoint_2026-09-20.json` に分離して記録した。probe setと3 source fixtureの4/10 filesはGit blob SHA-1一致を実測した一方、残る6 Python mechanicsはcurrent connector→execution-container境界でbyte-faithful materialization未達であり、CRC32 / full-file blob検査で不一致となった再構成は全て破棄した。canonical runnerはこのcheckpointでは未実行で、新しいPASS / FAILを主張しない。

```text
exact 10-blob source binding
  != E78.3 local gate PASS
  != human review result
  != actual long-gap Evidence
  != Product Value decision
  != Stable Requirement authorization
```

このbinding checkpointでは新しいruntime PASSを主張しない。canonical runner focused tests、7-check aggregate local gate、result schema v2 artifact生成は引き続き **Not Yet Verified** とし、次のactual executionでのみ更新する。

```text
partial focused mechanics PASS
  != full E78.3 local gate PASS
  != human review result
  != actual long-gap Evidence
  != Product Value decision
  != Stable Requirement authorization
```

review開始前に、repository-local mechanics runnerが全checkを完走し、加えて`validate`と対象fixtureの`preflight`がcurrent v1 contractを示すことを確認する。runnerはprobe/evidence focused unit tests、canonical validate、3 fixture全てのpreflightを一つの入口で実行し、途中停止や未実行checkをPASSへ数えない。local-check result schema v2は、canonical probeのsemantic SHA-256、runner / probe / Evidence tool / focused test等のexact file SHA-256、3 source fixtureのexpected / actual Git blob SHA-1、Python implementation / versionを`contractSnapshot`へ保存する。さらに各実行についてcommand、repo相対cwd、exit code、timeout、stdout/stderrのSHA-256とbyte数を保存し、rawログ本文やローカル絶対pathは保存しない。source fixtureがprobeのfreezeと一致しない場合はcheck実行前にfail-closedする。これにより、後からprobeやmechanicsが変わったPASSを同一条件の検証結果として読み替えず、同じsnapshotでも実際に何を実行し何が返ったかをdigestで追跡できる。result JSONは保存直前にもschema v2全体をfail-closedで再検証し、空checkによるvacuous PASS、check順序/count/statusの矛盾、host-escaping command、stream digest不正、mechanics/source identity差し替え、Evidence stopline変更を拒否したうえでexclusive-createする。launch errorはtype / errnoだけを残し、OS error messageやhost pathをartifactへ持ち込まない。ただしそのPASSはHuman Evidenceではなく、actual long-gap resumption、Product Value、Stable Requirement authorizationも成立させない。

`validate`と`preflight`では3 source fixtureのGit blob SHA-1、probe / response / receipt / audit-response / Evidence schema、typed audit dimension契約がcurrent v1であることを確認する。pre-v1 artifactはcurrent contractへ移行済みとはみなさず、human review開始後のschema差し替えを行わない。

review packetに含まれる`provisional_ai_summary`と`provisional_ai_next_question`は、意図的に誤りを含む**evaluation-only stimulus**であり、canonical Question / Observation / Unknown / Hypothesis、Recommendation、Decision、Evidence reportへ自動昇格させない。

`review`では、歪んだsummary / next-question suggestionを出力する前に、opaque reviewer id、`prior_exposure`、`response_authorship`をreview-start receiptへ固定する。human responseはそのreceipt SHA-256と同じ三つのprovenance値を保持しなければauditへ進めない。このためstimulusを見た後に`none-declared`へ書き換える等のpost-hoc provenance変更を機械的に拒否できる。ただし、これらはあくまでreviewer / operatorによる申告metadataであり、実際の盲検状態、本人性、human authorshipを独立に証明するものではない。review-start receiptも上書き不可とする。さらに直接API経路でも、receiptのsemantic JSON valueと、そのSHA-256対象となるraw bytesが同じJSON値を表すことを検証する。value=A / raw=Bの不一致pairはresponse templateやaudit packetへ進めない。

`audit`はまず、開示予定の`distortion_key`、`reference_state`、`post_interruption_evidence`、audit dimensions、stopline群から**exact audit material**をメモリ上で組み立て、そのcanonical SHA-256を確定する。次にhuman response SHA-256、exact probe content、fixture、audit material SHA-256、machine-recorded `revealed_at`をexclusive-createのaudit-reveal receiptへ結び、receiptの永続化に成功した場合だけ、事前構築済みの同じaudit materialをstdoutへ出力する。packet構築が失敗した段階ではreceiptを残さず、receiptの永続化が失敗した場合もreference materialを出力しない。audit-reveal receipt v1はreview-start receipt SHA-256と`review_started_at`へ直接結び、`revealed_at < review_started_at`を拒否する。さらにpost-reveal auditの`completed_at`が`revealed_at`より前の場合も拒否する。

これにより「開示後にhuman responseを書き直したもの」をpre-reveal responseとして扱う経路、review開始より前にaudit revealが起きたように見える不正な時系列、receipt作成後に別のreference materialへ差し替える経路を機械的に狭める。ただしreceiptは利用者が実際に画面を見た時刻やhuman authorshipそのものを独立に証明するものではない。

さらにreview response、audit-reveal receipt、audit response、Evidence bundleをcanonicalized probe JSONのSHA-256へ結び、summary、next question、review questions等のprobe内容が後から変更された場合に別の評価を同一Evidenceとして読み替えられないようにする。probe schema v1では`audit_dimensions`を`id / value_kind / allowed_values`の契約として保持し、異質な観測を共通のpass/failへ押し込めない。`unsupported_generalization_detection`は、実際の3ケースにovergeneralizationとunsupported dismissalの双方があるため、より正確な`unsupported_claim_detection`へ一般化した。audit responseはv1のtyped contractを維持し、durable Evidence bundleはv2へ更新する。Evidence v2は`probe_snapshot.canonical_probe`としてcomplete canonical probeを自己完結的に保存し、そのcanonicalized JSONからSHA-256を保存時に再計算する。選択fixtureのsummary / next question / review questions / audit dimensions / source path / source blob SHA-1も同じcanonical probeへ再結合し、digestだけを据え置いたstimulus差し替えを拒否する。さらに保存時にはhuman answer数をreview questions数へ一致させ、operator observationのshape / 値域を再検証する。semantic auditのdistortion keyはcanonical probeのselected caseへ固定し、bundle内のreference state / post-interruption evidenceとcanonical probeのaudit dimensions / evidence boundary / stopline群からaudit materialを再構成してSHA-256を再計算し、audit-reveal receiptが指すmaterialとの不一致を拒否する。human review observation、audit reveal、semantic auditは別layerとして保持し、保存直前にもbundle全体を再検証してdigest、時系列、review provenance、typed findings、review-start / audit-reveal binding、source path、Evidence境界の改変や余分な昇格fieldを拒否してからexclusive-createする。`audit-template`以後に記録するsemantic auditは、**post-revealなoperator / auditor Evidence**であり、開示前のhuman responseへ混ぜ戻さない。既存Evidence outputは上書きしない。

reviewer / auditorのopaque id、prior exposure、response authorship等は評価上の申告metadataであり、review-start receiptによって申告時点をstimulus提示前へ固定しても、それだけで盲検やhuman authorshipを独立に証明するものではない。`human-direct` / `human-transcribed`以外をhuman reviewとして受理しないが、その機械検証自体をHuman Evidenceと読み替えない。

歪みを流暢に修正できたことだけをSEI固有価値の証明にせず、検出できなかった歪みも反証Evidenceとして残す。検出数を単一scoreへ畳まず、さらにcorrection burdenを「pass / fail」へ読み替えず、raw chat / noteでも同程度に訂正できる可能性を比較対象として維持する。

probe、Evidence exporter、focused testが存在することは、利用者が実際に誤りを発見・修正・却下できたEvidenceではない。E78.3のhuman correction / rejection Evidenceは**Not Yet Observed**とする。

### E78.6 — Quiet vs proactive assistance

既存3 synthetic caseへ、次の3条件をrotationするevaluation-only probeを用意した。

- Proactive-first: AI候補を初期表示からすべて見せる。
- Quiet-first: canonical orientationを保ちつつAI候補は必要時まで前面に出さない。
- Adaptive progressive disclosure: 最も直接的な候補だけを初期表示し、残りへ段階的に降りる。

probe / packet / responseはv1へ更新した。initial / reveal packetでは`A_proactive_first` / `B_quiet_first` / `C_adaptive_progressive`のcondition名を出さず、rotation内の`presentation_id`だけを提示する。condition mappingはinitialとrevealのstructured responseが両方固定された後のauditでのみ開示する。responseはcanonical probe SHA-256、rotation、stage、presentation順、fixture順へ固定し、各stage questionへの1回答、completion time、source reopen count、attention loadを別々に保持する。単なる任意JSONをresponseとしてSHA固定する旧経路は受理しない。

source fixture単体だけでなく、元となるmatched-set manifest自体もGit blob SHA-1で固定し、そのordered fixture id / path列がassistance probeのcase列と一致しなければpacket生成を停止する。

初期回答を固定する前に全候補を見せないこと、AI候補をcanonical meaningとみなさないこと、Quiet表示でもoriginal concern / current Question / material Observation / Unknown / Hypothesis / next useful investigationを隠さないことを停止線としている。

さらに、initial response固定後に全候補を開く前にexclusive-createのreveal receipt v1を保存し、canonical probe / rotation / fixed initial response SHA-256 / exact reveal material SHA-256 / reveal timestampへ結ぶ。reveal response固定後にcondition mapping / reference state / audit keyを開く前にはaudit receipt v1を保存し、reveal receipt SHA-256 / fixed initial・reveal response SHA-256 / exact audit material SHA-256 / audit timestampへ結ぶ。audit timestampがreveal timestampより前の場合、responseがreceipt固定後に変更された場合、receiptのsemantic valueとraw bytesが一致しない場合を拒否する。CLIはreceiptをexclusive-createできた後にだけpacketをstdoutへ出す。

pre-stimulus reviewer provenanceもreview-start receipt v1へ固定する。initial packetを出力する前にopaque reviewer id、declared prior exposure、response authorship、started_at、canonical probe / rotationをexclusive-createし、そのexact raw bytes SHA-256をpacket v2、response v3、reveal receipt v2、audit receipt v2へ一貫して伝播する。response schema v3ではinitial / revealの双方が同じreview-start receiptへ結ばれ、initial responseはprior-stage gateを持たず、reveal responseはさらにvalidated reveal receiptのexact raw bytes SHA-256を`stage_gate_sha256`として必須で保持する。audit receipt作成時・検証時にも両receipt bindingを再検証するため、別reviewer provenanceや別reveal receiptへ結ばれたresponseを後から同じaudit chainへ差し込めない。

post-audit経路も`inquiry_continuity_assistance_evidence.py`へ一本化した。audit response schema v2では、AI suggestionのcanonical昇格、Quiet-firstでcanonical orientationを隠す、候補数だけでProduct Value / discovery改善を断定する、といった**presentation単位のsemantic hard failure**と、「同一readerへ回答固定前に同一fixtureの複数conditionを提示する」という**session単位のprotocol hard failure**を分離して記録する。session failureを各conditionへ三重に帰属させない。

durable Evidence schema v3はreview-start receipt → initial response → reveal receipt → reveal response → audit receipt → semantic auditの各artifactについて、semantic valueだけでなくexact UTF-8 JSON text、raw SHA-256、canonical semantic SHA-256を保持する。保存時にはraw JSONを再parseしてsemantic valueとの一致を確認し、bundle validatorではembedded raw textからSHA-256を再計算するため、stage hash chainをEvidence artifact単体で再検証できる。保存はexclusive-createであり、overall score、ranking、winner、preferred condition、Product Value成立、Stable Requirement変更を生成しない。

ここまででE78.6はhuman reviewを安全に実行し、結果をdurable Evidenceへ保存するmechanicsまで揃った。さらに`run_inquiry_continuity_assistance_checks.py`をrepository-localの正規mechanics gateとして追加した。runnerはcanonical probe-set、matched-set manifest、3 source fixture、probe / Evidence / focused tests / runner自身のfile SHA-256を実行前にsnapshotし、manifest / fixtureのGit blob freezeとrepo外path混入をfail-closedで検出する。focused probe test、Evidence test、runner test、canonical probe `validate`をsanitized environmentで順に実行し、commandはportable表現、stdout / stderrは本文ではなくSHA-256とbyte数だけをresultへ保存する。optional result JSONはexclusive-createであり、途中停止や未実行checkをPASSへ数えない。保存・summary表示前には、selected check名・portable command・repo相対cwdがcanonical runner定義と一致すること、non-empty execution、全checkの同一timeout、timeout / launch-error metadata、first-failure stop prefix、launch error時の空streamを再検証し、contractSnapshotも現在checkoutから再計算して完全一致させる。

ただし、このrunner自体をrepository上で実Python実行した結果はまだ得ていない。したがってmechanics PASSとは記録せず、human reviewも依然**Not Yet Observed**、actual long-gap comparisonやProduct Valueも未成立のままとする。将来local checksがPASSしても、それだけでQuiet / Proactive / Adaptiveの採用根拠、Product Value成立、Stable Requirement変更には使わない。

### E78.7 — Closure / dormancy

active / dormant / closed without Decision / later Decision connectionを比較するlifecycle probeを、condition-blindedなstage-gated human reviewへ更新した。これらはUniversal Inquiry statusではなく、Product-localなattention projectionとして扱う。

current contractはprobe schema v2、packet / response schema v1、review-start / audit receipt v1である。A=always open / B=age hidden / C=explicit attention projectionの3条件はR1〜R3で提示順をcounterbalanceし、review中はcondition identifierと設計側の`intended_tradeoff`を隠す。pre-revealのhuman review questionは、実際のhandling surfaceを読んでattention burden、recoverability、誤認、reopen cue、historical continuity、操作負担を観察するL1〜L6へ限定する。age-based automationの条件を問うL7とStable Requirement / Universal status型の必要性を問うL8は、他conditionや上位設計論を先に想起させないよう`audit_key.design_reflection_questions`へ移し、response固定後のauditでだけ開示する。

stimulus提示前にopaque reviewer id、declared prior exposure、response authorship、started_at、probe / rotationをexclusive-create review-start receiptへ固定する。human responseは3 presentationを一つのstructured artifactへまとめ、presentation順、question id、completion time、attention loadを固定する。responseを固定した後にだけaudit receiptをexclusive-createし、condition mapping、full handling contract、intended tradeoff、semantic hard failure、Product failure signal、acceptable outcomeを開く。audit receiptはreview-start receiptのexact raw SHA-256、fixed response SHA-256、canonical audit material SHA-256へ結び、`revealed_at < review_started_at`を拒否する。receiptのsemantic valueとraw bytesが一致しない経路も拒否する。

dormantやclosedにしても元InquiryへDecisionを自動生成せず、unresolved meaningを消さず、後日のDecisionは別recordへの文脈linkとして扱う境界は維持している。また、explicit attention projectionを自動遷移させず、Product-local attention stateからUniversal status型を先取りしない。

post-audit経路も`inquiry_continuity_lifecycle_evidence.py`へ一本化した。current audit response / durable Evidenceはv3で、semantic hard failureは`present / not-present / not-applicable`、Product failure signalは`risk-indicated / not-indicated / not-assessable`として別の値域を持つ。後者はsynthetic review上のrisk assessmentであり、actual user behaviorを「観測した」ことにはしない。L7/L8は`design_reflection_answers`としてpost-revealで必須記録し、pre-reveal human observationとは別layerに保つ。acceptable outcomeは候補ごとのnoteとして保持するだけで、選択・ranking・winnerへ変換しない。

durable Evidenceはcanonical probe、review-start receipt、structured response、audit receipt、post-audit responseについてexact UTF-8 JSON、raw SHA-256、canonical semantic SHA-256、semantic valueを保持し、artifact単体でchainとtamperを再検証する。Product-local attention stateからUniversal status型、Product Value、Stable Requirementへ自動昇格しない。

reader assignmentは一人につき一rotationだけを原則とし、複数readerではR1〜R3をbalanceする。同一readerの反復rotationは許さず、single-reader pilotからcondition effectとpresentation-order effectを分離したとは主張しない。

さらに`run_inquiry_continuity_lifecycle_checks.py`をrepository-local mechanics gateとして追加した。probe / Evidence / runner focused testsとcanonical probe validateをsanitized environmentで実行し、probeとmechanics file digest、portable command、stdout/stderr digestを保存できる。result自己検証ではcanonical selected check / command / cwd、non-empty execution、全checkの同一timeout、timeout / launch-error metadata、first-failure stop prefix、launch error時の空stream、現在checkoutから再計算したcontractSnapshotとの完全一致まで確認し、summary表示前にも同じ検証を通す。local mechanics gateではOpenRouterを含む外部provider API keyを環境から除外し、外部モデルを使う検証は明示的なintegration testとして分離する。ただしrunner sourceの存在はPASSではなく、human reviewも依然**Not Yet Observed**、Universal status typeは**not-proposed**、Product Value / Stable Requirementも未成立のままである。


## E78.7 local runtime checkpoint — 2026-09-21

E78.7のrepository-local mechanics gateは、current `develop/v0.2.0` と一致する7ファイルを同一execution containerへmaterializeし、実行前に7/7全てのGit blob SHA-1がGitHub正本と完全一致することを確認したうえでactual実行した。実行直前に並行レーンで`develop/v0.2.0`が2コミット進んだが、差分は`evaluation/local-model-probe`と`evaluation/sparse-associative-cognition`に限定され、E78.7の7ファイルには重複しないことも確認した。

実測結果は次のとおりである。

```text
bound lifecycle mechanics exact materialization
  = 7 / 7

lifecycle probe focused tests
  = 15 / 15 PASS

lifecycle Evidence focused tests
  = 7 / 7 PASS

lifecycle local runner focused tests
  = 10 / 10 PASS

canonical aggregate
  = selected 4
  = executed 4
  = failed 0
  = result ok

canonical probe validate
  = exit 0
```

validated result v1は次へdurable保存した。

```text
evaluation/personal-inquiry-decision/evidence/issue-000078/
  e78_lifecycle_local_check_result_v1_2026-09-21.json
```

artifact identityは、schema `sei.inquiry-continuity-lifecycle-local-check-result/v1`、4,811 bytes、SHA-256 `59b170723ecf32ab049c0dee54b05c3cca924d08e622f06ab4639f4559b9a390`、Git blob SHA-1 `76e12cae3ed85da3cbbaac0a9415e989d3a75921`である。Python runtimeはCPython 3.13.5だった。

したがってE78.7について、以前の「runner sourceは存在するがrepository上のactual PASSは未記録」という状態は解消した。ただし成立したEvidence高さは**repository-local mechanics PASS**までであり、human reviewは依然Not Yet Observedである。

```text
E78.7 local mechanics actual PASS
  != human lifecycle comparison
  != preferred lifecycle condition
  != Product Value decision
  != Universal Inquiry status authorization
  != Stable Requirement authorization
```

特にA / B / Cのどれを採用すべきか、Product-local attention Projectionが実利用で価値を持つか、Universal status型が必要かについて、このmechanics resultから結論を出さない。次のEvidence段階はstage-gated human reviewであり、reader assignment / condition blinding / post-reveal auditの既存canonical pathをそのまま使う。別runnerや別Evidence schemaは追加しない。

### V1〜V8 / Decision Continuity coverage audit

`inquiry_continuity_coverage_audit_2026-09-16.json`でcurrent V1〜V8 / Decision Continuityを再照合した。現段階の読みは、Observation / Hypothesis / Unknown等の既存semantic axisにはDecision前にも利用できるcoverageが広く存在する一方、Decisionが一度も成立していないInquiryのresumeをcross-axis Product Acceptanceとしてどこまで保証すべきか、またその価値をhuman comparisonで裏付けられるかが未確定、というものである。

したがって、このauditだけを理由に新Value Axis、Stable Requirement、Universal entity、Product Vision再編へ進まない。

### Human review execution path — 2026-09-17

E78.2 / E78.4 / E78.5のmatched human reviewは、`inquiry_continuity_review_runner.py`を唯一の実行入口とする。generic `matched_review_session.py`を直接操作してhuman reviewを開始せず、session開始時にreview provenanceを固定してからstage gateへ入る。

repo rootからの基本経路は次である。

```text
RUNNER=evaluation/personal-inquiry-decision/inquiry_continuity_review_runner.py
SESSION=<checkout外または意図的に管理するsession.json>
EVIDENCE=<checkout外または意図的に管理するevidence.json>

python3 "$RUNNER" init "$SESSION" \
  --rotation R1 \
  --session-id <opaque-session-id> \
  --created-at <ISO-8601> \
  --reviewer-id <opaque-reviewer-id> \
  --prior-exposure <none-declared|known-material-exposure|unknown> \
  --response-authorship <human-direct|human-transcribed>

python3 "$RUNNER" bundle "$SESSION"

# bundleが示すcurrent stageとresponse_templateに従ってhuman responseを作成する。
# phase1を全fixtureで固定してからpostへ進み、postを全fixtureで固定してからauditへ進む。
python3 "$RUNNER" record "$SESSION" \
  --fixture-id <fixture-id> \
  --stage <phase1|post|audit> \
  --recorded-at <ISO-8601> \
  --response <human-response.json>

python3 "$RUNNER" validate "$SESSION" --require-complete
python3 "$RUNNER" export-evidence "$SESSION" --output "$EVIDENCE"
```

`reviewer-id`には氏名、email、account id等を保存せず、その評価内だけで一貫するopaque idを使う。`response-authorship=human-transcribed`は、humanが作成した回答をAIまたはoperatorが転記した場合を表す。AIが回答内容そのものを生成したsessionをhuman reviewとして記録してはならない。

`prior-exposure`はreviewerの既知の事前露出を隠さないための申告である。

```text
none-declared
  = reviewerがmaterialな事前露出なしと申告した
  = clean blinded review candidate
  != blindingが客観的に証明された

known-material-exposure / unknown
  = pilot observationとしては保存可能
  != clean blinded review
```

review中はcondition labelをreviewer bundleへ出さず、全phase1回答が固定されるまでpost-interruption materialを開かず、全post回答が固定されるまでreference state / audit keyを開かない。完了済みsessionを同じsession内で巻き戻して再回答しない。

`export-evidence`はcomplete sessionだけを受理し、少なくとも次を分離したまま保存する。

- `human_review_observations` — human回答とoperator observation。
- `semantic_audits` — reference materialを開いた後の意味監査。
- `review_provenance` — opaque reviewer id、declared prior exposure、response authorship。

このexportはoverall score、ranking、winner、preferred conditionを生成しない。また、synthetic matched reviewをactual long-gap resumptionやactual team handoffへ読み替えず、reviewが完了したことだけでProduct ValueやStable Requirement変更を承認しない。

### current Evidence stopline

2026-09-22時点では、repository-local mechanicsについてはDesign / scaffold段階を越え、次のactual PASSがdurable Evidenceへ固定済みである。

- E78.2 / E78.4 / E78.5 matched-review mechanics:
  - exact materialization 15 / 15
  - focused tests 34 / 34 PASS
  - result Git blob SHA-1 `21d195b52acfe29195232ea3f2d7940ec7253a68`
- E78.3 summary-distortion mechanics: actual local PASS
- E78.6 Quiet / Proactive / Adaptive assistance mechanics: actual local PASS
- E78.7 lifecycle mechanics: actual local PASS

したがって、current Evidence stoplineは次へ更新する。

```text
repository-local mechanics actual PASS
  != matched human review result
  != E78.3 human correction / rejection observed
  != E78.1 clean long-gap resumption observed
  != actual team handoff observed
  != Product Value decision
  != Stable Requirement authorization
  != Adoption / Outcome Evidence
```

E78.2 / E78.4 / E78.5の次のvalid transitionはGitHub Issue #575のactual matched human reviewである。新しいrunner、review template、Evidence schemaを追加せず、既存canonical runnerを唯一の入口とする。human回答本文をAI生成して`human-direct`または`human-transcribed`へ読み替えない。

同一reviewerについては、matched reviewが完了・固定される前にE78.3のdistortion刺激を提示しない。current ChatGPT conversation participantをreviewerに使う場合、E78設計・順序・Evidence境界へのmaterial exposureは既知であり、`none-declared`へ読み替えない。

E78.1については2026-09-22のmaterial re-exposureが既にprotocol checkpointへ記録済みであり、その再露出をclean resumption成功・失敗として数えない。次のclean resumption候補は、このmaterial exposure以後の新しい認知的gapを必要とする。

ISSUE-000078の継続作業は引き続き`develop/v0.2.0`を元ブランチとし、`evaluation/issue-000078-dogfood`を再利用する。完了単位はparentへsquash mergeし、reusable branchをparent HEADへrealignしてahead / behind 0 / 0へ戻す。


## Lane F continuation checkpoint — 2026-09-19

前回のE78.3 local mechanics gate追加後、`develop/v0.2.0`には他レーンの変更も集約され、E78.3の正規runner自体もresult schema v2まで強化された。現在の`run_inquiry_continuity_summary_distortion_checks.py`は、canonical probeのsemantic SHA-256、mechanics fileのSHA-256、source fixtureのexpected / actual Git blob SHA-1、Python runtime、各checkのportable command / repository相対cwd / stdout・stderr digestを保存し、source freeze不一致、host path混入、tampered / vacuous result、既存result上書きを拒否する。

このcheckpointでは、これ以上E78.3専用scaffoldを増やさない。現行の`inquiry_continuity_summary_distortion_*`とlocal-check runnerを正規経路として凍結し、同じexperimentに別runner、別exporter、別Evidence schemaを並立させない。

現在もEvidence高さは次のままである。

```text
repository-local mechanics implementation
  != repository-local actual PASS recorded
  != human correction / rejection observed
  != clean long-gap resumption observed
  != Product Value established
  != Stable Requirement authorized
```

したがって、次に必要なのは設計追加ではなくactual executionである。特に同一reviewerで進める場合、E78.3の意図的なdistortionを先に見せてbase comparisonを汚染しないよう、E78.2 / E78.4 / E78.5のmatched human reviewを先に完了・固定し、その後にE78.3を実施する。既知のmaterial exposureがあるreaderは`known-material-exposure`として扱い、clean blinded reviewへ読み替えない。

このcheckpointでは新しいhuman observation、clean resumption、actual team handoff、Product Value判断を生成していない。既存の未観測状態を維持し、次の進行条件をactual Evidenceへ限定する。

また、2026-09-19のLane F継続ではactual dogfood caseのcurrent concern、Unknown、Quiet / Proactive比較、clean resumption条件へmaterialに再露出した。これはE78.1のclean resumptionではなくprotocol observationであるため、evaluation sidecarの`resume_observations`は空のまま維持し、`ACTUAL_DOGFOOD_CHECKPOINT_2026-09-16.md`へ再露出事実だけを追記した。次のclean resumptionでは、この2026-09-19 exposure以後の認知的gapを基準にする。

branch運用についても、同一Issueの継続作業は引き続き`develop/v0.2.0`へ集約する。小さな継続作業ごとにtopic branchを増やさず、元ブランチから分岐した未統合branchを残さない。



## E78.3 local runtime checkpoint — 2026-09-21

E78.3のrepository-local mechanics gateは、execution-input bindingで固定した10ファイルを**同一execution container上**へmaterializeし、実行前に10/10全てのGit blob SHA-1がbindingと完全一致することを確認したうえでactual実行した。

実測結果は次のとおりである。

```text
bound source / mechanics exact materialization
  = 10 / 10

runner-focused tests
  = 25 / 25 PASS
  = exit 0

canonical seven-check aggregate
  = selected 7
  = executed 7
  = failed 0
  = result ok
  = exit 0

canonical validate_result
  = PASS
```

validated result v2は次へdurable保存した。

```text
evaluation/personal-inquiry-decision/evidence/issue-000078/
  e78_summary_distortion_local_check_result_v2_2026-09-21.json
```

identityは、schema `sei.inquiry-continuity-summary-distortion-local-check-result/v2`、8,859 bytes、SHA-256 `65e69a8fa2334021063eabef584e4563dc0d680b83d40d28395d2d59e0ab483b`、Git blob SHA-1 `fc203bea767aa36f5d2a194099c28df5002235fe`である。GitHubへ保存したartifactも同じblob SHA-1であり、local validated artifactとのbyte identityを確認済みである。

したがって、以前の

```text
repository-local mechanics implementation
  != repository-local actual PASS recorded
```

という未実行状態は解消した。ただし、成立したEvidence高さは**repository-local mechanics PASS**までである。

```text
repository-local mechanics actual PASS
  != human correction / rejection observed
  != actual long-gap Evidence
  != Product Value established
  != Stable Requirement authorized
```

E78.3のhuman reviewはまだ開始しない。同一reviewerがE78.2 / E78.4 / E78.5のmatched reviewにも参加する場合、意図的なdistortion刺激による汚染を避けるため、matched reviewを先に完了・固定する。別reviewerを用いる場合も、sourceに対する初期回答を固定する前にdistorted summary / next-questionを提示しない。

よってE78.3について次に追加すべきものは別runnerや別Evidence schemaではなく、protocol順序を守ったactual human reviewと、その後のsemantic auditである。local mechanicsの再設計は、新しいfailureが見つからない限りここで止める。



## E78.6 local runtime checkpoint — 2026-09-22

E78.6のQuiet / Proactive / Adaptive assistance mechanicsは、execution-input bindingで固定したexact source commit `60269a11439d06b05317a9dc66ac80b21589d5aa`から11ファイルを同一execution rootへmaterializeし、**11 / 11全件のGit blob SHA-1がbindingと一致した後だけ**actual Python executionへ進めた。

実測結果は次のとおりである。

```text
bound source / mechanics exact materialization
  = 11 / 11

runner-focused tests
  = 14 / 14 PASS
  = exit 0

canonical four-check aggregate
  = selected 4
  = executed 4
  = failed 0
  = stoppedEarly false
  = result ok
  = exit 0

canonical validate_result
  = PASS

Python
  = CPython 3.13.5
```

canonical aggregateは、probe tests、Evidence tests、local runner tests、probe validateの4checkを実行した。probe content SHA-256は `d3a9a917d8f043f7cecba623524d1bcce64fed806cb31c6202f9379eaf337a28` である。

validated result v1は次へdurable保存した。

```text
evaluation/personal-inquiry-decision/evidence/issue-000078/
  e78_assistance_local_check_result_v1_2026-09-22.json
```

artifact identityは、schema `sei.inquiry-continuity-assistance-local-check-result/v1`、6,139 bytes、SHA-256 `73898b8052e1141ad1a502845ec2dd90b52373b236d9f13aa8c038cc6ace1086`、Git blob SHA-1 `faae8fd8574653d1a86c38d273ffb9f055dd246c` である。GitHubへ保存したartifactも同じGit blob SHA-1であり、local validated artifactとのbyte identityを確認した。

実行環境ではPython startup時にrepository外のspreadsheet runtime warmup警告がstderrへ出たが、canonical 4checkはいずれもexit 0であり、resultはraw stderr本文を保存せずbyte数とSHA-256だけを保持している。

このcheckpointで成立したのは**E78.6 repository-local mechanics PASS**までである。Quiet / Proactive / Adaptiveのどれを望ましい方式とするかはhuman review前には決めない。

```text
E78.6 local checks PASS
  != human review result
  != actual long-gap comparison
  != preferred assistance condition
  != Product Value decision
  != Stable Requirement authorization
```

したがって次の段階は、同一fixtureの複数conditionを固定回答前に同じreaderへ見せないという既存stage gateを守ったhuman reviewである。local mechanics PASSだけを根拠にSurface preferenceやStable Requirementを確定しない。

## E78.2 / E78.4 / E78.5 local runtime checkpoint — 2026-09-22

matched human-reviewのrepository-local mechanics gateは、execution-input bindingで固定したexact source commit `1de126f6cddea9eac4cef2c5aaeb89b044f1f89b` の15ファイルを同一execution rootへmaterializeし、実行前に **15 / 15全件のGit blob SHA-1とbyte数がbindingへ完全一致すること**を確認したうえでactual実行した。

実測結果は次のとおりである。

```text
bound source / mechanics exact materialization
  = 15 / 15

test_matched_review_session.py
  = 7 / 7 PASS
  = exit 0

test_inquiry_continuity_review_analysis.py
  = 7 / 7 PASS
  = exit 0

test_inquiry_continuity_review_evidence.py
  = 5 / 5 PASS
  = exit 0

test_inquiry_continuity_review_runner.py
  = 15 / 15 PASS
  = exit 0

focused tests total
  = 34 / 34 PASS
  = failed 0

Python
  = CPython 3.13.5

Git
  = 2.47.3
```

validated local resultは次へdurable保存した。

```text
evaluation/personal-inquiry-decision/evidence/issue-000078/
  e78_matched_review_local_check_result_v1_2026-09-22.json
```

artifact identityは、schema `sei.inquiry-continuity-matched-review-local-check-result/v1`、9,640 bytes、SHA-256 `77603218f515de28849aed2afb25d1108ec43e467d70c4a1e48af587933a8b31`、Git blob SHA-1 `21d195b52acfe29195232ea3f2d7940ec7253a68` である。

実行時のstderrにはrepository外のspreadsheet runtime warmup diagnosticsが含まれたが、4 processはいずれもexit 0かつunittest `OK` で終了した。durable resultにはraw stdout/stderr本文を保存せず、byte数とSHA-256のみを保持した。

これにより、E78.2 / E78.4 / E78.5について、human review開始前のrepository-local mechanics gateはactual PASSまで進んだ。ただし、成立したEvidence高さはここまでである。

```text
matched-review local mechanics PASS
  != human review result
  != actual long-gap resumption
  != actual team handoff
  != Product Value decision
  != Stable Requirement authorization
```

したがって次段は既存の`inquiry_continuity_review_runner.py`を唯一の入口とするactual human reviewである。同一reviewerがE78.3にも参加する場合は、matched reviewを先に完了・固定してからdistorted summary / next-questionを提示する。human回答そのものをAI生成してhuman reviewとして記録しない。


## Human review launch gate — 2026-09-22

repository-local mechanicsは、E78.2 / E78.4 / E78.5 matched review、E78.3 summary distortion、E78.6 assistance、E78.7 lifecycleまでactual PASSがdurable Evidenceへ固定された。ここから先の主な未観測はHuman / actual long-gap / actual team handoff / Product Valueであり、machine gateを増やすこと自体を進捗としない。

actual matched human reviewの追跡先はGitHub Issue #575へ一本化する。新しいreview template、runner、Evidence schemaは追加せず、既存の `inquiry_continuity_review_runner.py` を唯一の入口とする。

2026-09-22時点の該当ChatGPT実行環境では、private repositoryのexact bound-source checkoutを直接materializeしてcanonical runnerを起動できなかった。この制約はexecution environmentのblockerであり、canonical runnerやreview mechanicsのfailureではない。環境制約を回避するためにsource identity checkを弱めたり、別runnerを増設したりしない。

また、このconversation participantをreviewerとして用いる場合、すでにE78設計、実行順序、Evidence boundaryへmaterialに露出しており、fixture 001もcanonical `init` 前に提示された履歴がある。そのため、そのreviewerを `none-declared` として扱わず、truthfulなprovenanceとして `known-material-exposure` を保持する。human response本文をAIが生成して `human-direct` / `human-transcribed` として記録しない。

同一reviewerを使う場合の順序は次で固定する。

```text
E78.2 / E78.4 / E78.5 matched review
  -> phase1(all fixtures) fixed
  -> post(all fixtures) fixed
  -> audit(all fixtures) fixed
  -> validate --require-complete
  -> export-evidence

then, for the same reviewer:
  E78.3 distorted summary / next-question review
```

E78.6は既存stage gateを守り、同一fixtureの複数conditionを固定回答前に同じreaderへ見せない。Quiet / Proactive / Adaptiveのpreferred conditionをmachine PASSから決めない。E78.1のclean long-gap resumptionは引き続き**Not Yet Observed**であり、synthetic reviewや事前露出済みsessionをactual long-gap Evidenceへ読み替えない。

execution-input binding内の `current_observation` はbinding作成時点のpoint-in-time snapshotとして保持し、後からruntime PASSへ合わせて過去artifactを書き換えない。後続execution stateはdurable local-check resultと本Issueのruntime checkpointを参照する。

```text
machine mechanics PASS
  -> human review may start

human review may start
  != human review observed
  != Product Value established
  != Stable Requirement authorization
```


### Human review execution readiness update — 2026-09-23

並行レーンのGitHub Issue #575で、frozen source commit `1de126f6cddea9eac4cef2c5aaeb89b044f1f89b` のcanonical human-review実行に必要な11ファイルのexact materializationを**11 / 11 Git blob SHA-1一致**として確認した。manifestと3 source fixturesのcanonical JSON SHA-256も事前oracleに**4 / 4一致**した。non-mutating canonical smokeとして`inquiry_continuity_review_runner.py --help`および`inquiry_continuity_packet.py --validate-only`がPASSした。以前のtransport blockerは、その実行contextについては解消済みである。

これは別のChatGPT実行コンテナへのファイル共有や、human reviewの開始・実施を意味しない。実際のreviewerが参加する際は、exact materialization済みの実行contextで既存runnerの`init`を開始し、reviewerの事前露出を正直に記録する。現conversation参加者によるpilotなら`known-material-exposure`とし、既存CLIの`--provenance-note`へ「E78設計への事前露出、canonical init前にfixture 001 phase1を一度見たがhuman回答は未記録」を保存する。review sessionを未開始のままfixture素材を再提示したり、AIがhuman responseを代作したりしない。

```text
11/11 exact materialization + canonical non-mutating smoke PASS
  != canonical human review init
  != human response observed
  != clean blinded review
  != actual long-gap / handoff Evidence
  != Product Value / Stable Requirement authorization
```


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

2026-09-16の実行準備同期では、各experimentについて「評価器やfixtureを実行できること」と「人間が実際に価値を得たこと」を分け、actual long-gap、actual handoff、capture burden、Product Value、Stable Requirement判断を未観測・未決定のまま保持した。また、同一Issueの継続作業を`develop/v0.2.0`へ集約するbranch運用を明記し、評価作業のためにbranch構造そのものを細分化しない方針を確認した。

2026-09-17の同期では、human review runnerを実行の正規入口として固定し、reviewerの事前露出とresponse authorshipをsession開始時に保存する経路、stage gate、complete sessionだけを受理するEvidence exportを本文へ接続した。`none-declared`は盲検の客観的証明ではなく申告に基づくclean blinded candidateに留め、known / unknown exposureも隠さずpilot observationとして保持する。

さらにE78.3について、重複していたdistortion probeを`inquiry_continuity_summary_distortion_*`へ一本化し、source fixture固定、review→auditの開示順、歪んだsummary / next questionによるmatched comparison汚染の防止、human response固定後のauditという一続きの実行経路へ整理した。これは評価手順の明確化であり、human correction EvidenceやProduct Valueを新たに成立させる変更ではない。

同日の追加同期では、E78.3のpost-reveal semantic auditとdurable Evidence exportまで正規経路へ接続した。固定済みhuman responseとsemantic auditをSHA-256で結びつけながら別Evidence layerとして保存し、既存Evidenceを上書きしない。reviewer / auditor provenanceは申告metadataに留め、actual human correction / rejection、clean resumption、SEI固有のProduct Valueを未観測のまま保持した。

意味、仮説強度、未検証範囲を固定した後、**自然な日本語として背景・failure・実験・停止線が連続して読めることを最重要視して全文を再読し、Design / Executable scaffoldとHuman / Outcome Evidenceを混同していないことを最終監査済み**とする。