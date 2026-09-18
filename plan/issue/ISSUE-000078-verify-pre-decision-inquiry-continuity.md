# ISSUE-000078: Decision成立前のInquiry Continuityを比較実証する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0028**  
Updated: 2026-09-18

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
# 保存時にもresult v2全体を再検証し、count/order/status、portable command/cwd、
# stream digest、mechanics/source identity、Evidence stoplineの改変を拒否する。
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

review開始前に、repository-local mechanics runnerが全checkを完走し、加えて`validate`と対象fixtureの`preflight`がcurrent v1 contractを示すことを確認する。runnerはprobe/evidence focused unit tests、canonical validate、3 fixture全てのpreflightを一つの入口で実行し、途中停止や未実行checkをPASSへ数えない。local-check result schema v2は、canonical probeのsemantic SHA-256、runner / probe / Evidence tool / focused test等のexact file SHA-256、3 source fixtureのexpected / actual Git blob SHA-1、Python implementation / versionを`contractSnapshot`へ保存する。さらに各実行についてcommand、repo相対cwd、exit code、timeout、stdout/stderrのSHA-256とbyte数を保存し、rawログ本文やローカル絶対pathは保存しない。source fixtureがprobeのfreezeと一致しない場合はcheck実行前にfail-closedする。これにより、後からprobeやmechanicsが変わったPASSを同一条件の検証結果として読み替えず、同じsnapshotでも実際に何を実行し何が返ったかをdigestで追跡できる。result JSONは保存直前にもschema v2全体をfail-closedで再検証し、空checkによるvacuous PASS、check順序/count/statusの矛盾、host-escaping command、stream digest不正、mechanics/source identity差し替え、Evidence stopline変更を拒否したうえでexclusive-createする。launch errorはtype / errnoだけを残し、OS error messageやhost pathをartifactへ持ち込まない。ただしそのPASSはHuman Evidenceではなく、actual long-gap resumption、Product Value、Stable Requirement authorizationも成立させない。

`validate`と`preflight`では3 source fixtureのGit blob SHA-1、probe / response / receipt / audit-response / Evidence schema、typed audit dimension契約がcurrent v1であることを確認する。pre-v1 artifactはcurrent contractへ移行済みとはみなさず、human review開始後のschema差し替えを行わない。

review packetに含まれる`provisional_ai_summary`と`provisional_ai_next_question`は、意図的に誤りを含む**evaluation-only stimulus**であり、canonical Question / Observation / Unknown / Hypothesis、Recommendation、Decision、Evidence reportへ自動昇格させない。

`review`では、歪んだsummary / next-question suggestionを出力する前に、opaque reviewer id、`prior_exposure`、`response_authorship`をreview-start receiptへ固定する。human responseはそのreceipt SHA-256と同じ三つのprovenance値を保持しなければauditへ進めない。このためstimulusを見た後に`none-declared`へ書き換える等のpost-hoc provenance変更を機械的に拒否できる。ただし、これらはあくまでreviewer / operatorによる申告metadataであり、実際の盲検状態、本人性、human authorshipを独立に証明するものではない。review-start receiptも上書き不可とする。さらに直接API経路でも、receiptのsemantic JSON valueと、そのSHA-256対象となるraw bytesが同じJSON値を表すことを検証する。value=A / raw=Bの不一致pairはresponse templateやaudit packetへ進めない。

`audit`はまず、開示予定の`distortion_key`、`reference_state`、`post_interruption_evidence`、audit dimensions、stopline群から**exact audit material**をメモリ上で組み立て、そのcanonical SHA-256を確定する。次にhuman response SHA-256、exact probe content、fixture、audit material SHA-256、machine-recorded `revealed_at`をexclusive-createのaudit-reveal receiptへ結び、receiptの永続化に成功した場合だけ、事前構築済みの同じaudit materialをstdoutへ出力する。packet構築が失敗した段階ではreceiptを残さず、receiptの永続化が失敗した場合もreference materialを出力しない。audit-reveal receipt v1はreview-start receipt SHA-256と`review_started_at`へ直接結び、`revealed_at < review_started_at`を拒否する。さらにpost-reveal auditの`completed_at`が`revealed_at`より前の場合も拒否する。

これにより「開示後にhuman responseを書き直したもの」をpre-reveal responseとして扱う経路、review開始より前にaudit revealが起きたように見える不正な時系列、receipt作成後に別のreference materialへ差し替える経路を機械的に狭める。ただしreceiptは利用者が実際に画面を見た時刻やhuman authorshipそのものを独立に証明するものではない。

さらにreview response、audit-reveal receipt、audit response、Evidence bundleをcanonicalized probe JSONのSHA-256へ結び、summary、next question、review questions等のprobe内容が後から変更された場合に別の評価を同一Evidenceとして読み替えられないようにする。probe schema v1では`audit_dimensions`を`id / value_kind / allowed_values`の契約として保持し、異質な観測を共通のpass/failへ押し込めない。`unsupported_generalization_detection`は、実際の3ケースにovergeneralizationとunsupported dismissalの双方があるため、より正確な`unsupported_claim_detection`へ一般化した。audit responseはv1のtyped contractを維持し、durable Evidence bundleはv2へ更新する。Evidence v2は`probe_snapshot.canonical_probe`としてcomplete canonical probeを自己完結的に保存し、そのcanonicalized JSONからSHA-256を保存時に再計算する。選択fixtureのsummary / next question / review questions / audit dimensions / source path / source blob SHA-1も同じcanonical probeへ再結合し、digestだけを据え置いたstimulus差し替えを拒否する。human review observation、audit reveal、semantic auditは別layerとして保持し、保存直前にもbundle全体を再検証してdigest、時系列、review provenance、typed findings、review-start / audit-reveal binding、source path、Evidence境界の改変や余分な昇格fieldを拒否してからexclusive-createする。`audit-template`以後に記録するsemantic auditは、**post-revealなoperator / auditor Evidence**であり、開示前のhuman responseへ混ぜ戻さない。既存Evidence outputは上書きしない。

reviewer / auditorのopaque id、prior exposure、response authorship等は評価上の申告metadataであり、review-start receiptによって申告時点をstimulus提示前へ固定しても、それだけで盲検やhuman authorshipを独立に証明するものではない。`human-direct` / `human-transcribed`以外をhuman reviewとして受理しないが、その機械検証自体をHuman Evidenceと読み替えない。

歪みを流暢に修正できたことだけをSEI固有価値の証明にせず、検出できなかった歪みも反証Evidenceとして残す。検出数を単一scoreへ畳まず、さらにcorrection burdenを「pass / fail」へ読み替えず、raw chat / noteでも同程度に訂正できる可能性を比較対象として維持する。

probe、Evidence exporter、focused testが存在することは、利用者が実際に誤りを発見・修正・却下できたEvidenceではない。E78.3のhuman correction / rejection Evidenceは**Not Yet Observed**とする。

### E78.6 — Quiet vs proactive assistance

既存3 synthetic caseへ、次の3条件をrotationするevaluation-only probeを用意した。

- Proactive-first: AI候補を初期表示からすべて見せる。
- Quiet-first: canonical orientationを保ちつつAI候補は必要時まで前面に出さない。
- Adaptive progressive disclosure: 最も直接的な候補だけを初期表示し、残りへ段階的に降りる。

初期回答を固定する前に全候補を見せないこと、AI候補をcanonical meaningとみなさないこと、Quiet表示でもoriginal concern / current Question / material Observation / Unknown / Hypothesis / next useful investigationを隠さないことを停止線としている。

これも比較実行のscaffoldが成立した段階であり、Quiet / Proactive / Adaptiveのどれかを採用する根拠はまだない。human reviewは**Not Yet Observed**である。

### E78.7 — Closure / dormancy

active / dormant / closed without Decision / later Decision connectionを比較するlifecycle probeを用意した。これらはUniversal Inquiry statusではなく、Product-localなattention projectionとして扱う。

dormantやclosedにしても元InquiryへDecisionを自動生成せず、unresolved meaningを消さず、後日のDecisionは別recordへの文脈linkとして扱う境界を固定している。ここでもhuman reviewは**Not Yet Observed**であり、Universal status typeを提案しない。

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

現時点では次を維持する。

```text
Design / executable evaluation scaffold
  != human review result
  != actual long-gap Evidence
  != Product Value decision
  != Stable Requirement authorization
  != Adoption / Outcome Evidence
```

focused testによって各評価器の停止線や入力検証は確認しているが、それ自体をhuman reviewやProduct Value Evidenceへ読み替えない。GitHub Actionsは使用せず、current repository方針どおりlocal verificationを前提とする。

ISSUE-000078の継続作業は`develop/v0.2.0`を元ブランチとして集約する。同一Issueの小さな継続作業ごとにtopic branchを増やさず、独立した責務や並行作業が実際に必要になった場合だけ分岐を検討する。

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