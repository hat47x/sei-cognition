# Personal Inquiry Continuity — Evaluation Entry Point

更新日: 2026-09-17  
状態: **Evaluation-only Product Hypothesis / Root Concept and Execution Entry**  
関連: ISSUE-000073 / ISSUE-000078

## 1. このディレクトリで確かめたいこと

このディレクトリの目的は、SEIのProduct Valueを、組織導入や複雑なProvider連携より先に、**一人の利用者が自分の長期的な問いを中断・再開する場面で本当に役立つか**という小さな領域で確かめることである。

ここで最初に守りたいのは、情報量でも検索精度でもAIの回答品質でもない。

> **時間が空き、AIや資料や作業環境が変わっても、そのInquiryについて「当時どこまで知っていたか、何がまだ分からなかったか、何をどう考え、何を決め、その後何が変わったか」を壊さずに保ち、そこから続きを始められること。**

この中心仮説を **Personal Inquiry Continuity** と呼ぶ。

Decisionは重要な一部だが、InquiryはDecisionへ到達しなくても成立する。

```text
Personal Inquiry Continuity
  contains Decision Memory when Decision exists
  != Decision tracker only
  != chat archive
  != note-taking app
  != task manager
```

ここにある文書・prototypeは、原則としてStable Product RequirementやUniversal Contractそのものではない。current Stable Requirementへ昇格した意味は`requirements/`を正本とし、このディレクトリには、そこへ至った評価・監査・実証準備と、まだProduct hypothesisのまま残る領域を置く。

## 2. 根幹の問題

個人が数日から数か月以上にわたり何かを考えるとき、情報は一つの場所に閉じない。

- AI conversation
- Web page
- PDF / document
- code / repository
- personal note
- later observation
- 別のAIやtoolで行った追加検討

このとき単に「情報を保存できる」だけでは、次の問題が残る。

### 2.1 内容を覚えていても、認識状態は失われる

過去の文章や会話を検索できても、次が分からなくなることがある。

- その時点で何を事実として見ていたか
- 何が解釈や仮説だったか
- 何がまだUnknownだったか
- Conflictがどこに残っていたか
- AIのRecommendationと本人のDecisionのどちらだったか
- Decision時点で何をbasisとしていたか
- その後初めて知った情報は何か

したがって、ここで扱う問題は単なるcontent memoryではない。

```text
content memory
  != epistemic state memory
  != historical decision memory
  != cognitive resumption support
```

### 2.2 正確な記録だけでも、人間はすぐ再開できない

逆に、canonical dataを細かく完全に保存しても、それをすべて読み直さなければ作業へ戻れないなら、個人Productとしての価値は弱い。

必要なのは、正確な記録と、人間が続きを始めるための再開支援を分けることである。

```text
Durable Inquiry Memory
  = precise / historical / inspectable / portable meaning

Resumption Projection
  = compact / selective / regenerable cue

Resumption Projection != canonical authority
```

### 2.3 速く戻れたように見えるだけでは成功ではない

再開を高速化しても、later Evidenceをpast basisと誤認したり、RecommendationをDecisionと取り違えたりすれば、かえって危険である。

この状態をこのevaluationでは **False Continuity** と呼ぶ。

```text
fast resume
+ wrong historical state
= failure
```

SEI Personal Profileの価値は、単に再開時間を短くすることではなく、**認識状態を壊さずに再開負担を下げられるか**で判断する。

## 3. Product Hypothesis

個人向けSEIを、既存のChat、PKM、document repository、Web research toolを置き換える製品として始めない。

それらをSourceとして利用し、その上に薄い意味・再開層を置く。

```text
Source Plane
  external chat / web / document / note / code
        ↓
Meaning Plane
  durable Inquiry semantics
        ↓
Resume Plane
  Orientation / Delta / Anchor / Handoff
```

設計上の仮称として、SEIがこの範囲で担う役割を **Epistemic Resume Layer** と表現する。

これは製品名ではなく、Product Boundaryを考えるための説明である。

### Source Plane

元情報を保持・参照する場所。

SEI自身が汎用全文書repositoryになることを要求しない。

### Meaning Plane

時間を越えて持ち運びたい意味を保持する。

中心となるのはcurrent SEI semanticsの範囲である。

- Inquiry
- Observation / source claim
- Interpretation / Hypothesis
- Unknown / Conflict
- Recommendation
- Decision
- basis
- Constraint / material premise
- residual / reopen information
- provenance / revision / lineage

### Resume Plane

人間または別AIが続きを始めるためのProjectionを生成する。

- Orientation
- change since Decision / last review
- Resume Anchor
- detail trail
- AI/tool handoff

Resume PlaneはMeaning Planeを読むが、過去の意味を権威的に書き換えない。

## 4. 誰のどんな場面から始めるか

first value validationでは、一人の利用者が数日から数か月以上かけて扱う、低〜中影響のInquiryを主対象とする。

例:

- 個人プロジェクトの技術・方式選定
- 学習テーマや教材の比較
- 機器、サービス、作業環境の比較
- 趣味、旅行、創作、調査の計画
- 長期的な設計課題や個人研究

一度きりで終わる質問より、**一度中断し、後から状況や情報が変わった状態で再開する問い**が適している。

first profileでは、医療・法務・重大な金融判断等のhigh-stakes用途、多人数承認、enterprise IdP / RBAC、汎用task management、常時agent orchestration等を中心に置かない。

## 5. 根幹から導かれる能力

個別Requirementへ入る前に、上の趣旨から最低限どの能力が必要になるかを整理する。

### Capability A — Faithful State Preservation

当時のObservation、Unknown、Conflict、Recommendation、Decision、basis等を意味上区別し、後から得た知識で過去を黙って書き換えない。

### Capability B — Low-friction Capture

利用者がContract型を逐一操作しなくても、問いや材料を軽く追加でき、必要なsemantic commitmentは後から深められる。

### Capability C — Queryless Reorientation

Inquiryを開いたとき、正しい検索語やAIへの質問を思い出さなくても、現在地へ戻るためのcueを得られる。

### Capability D — Epistemic Delta

Decisionまたは前回review以後に何が変わったかを、past stateを壊さずに確認できる。

### Capability E — Detail and Provenance Descent

light Orientationだけを権威化せず、必要なときsource、basis、time、revision、provenanceへ降りられる。

### Capability F — Independence and Handoff

元chat、特定LLM、特定Providerがなくても保存済みInquiryを読み、別AI / tool / environmentへ意味を渡せる。

これらはStable Requirementの新設を自動的に意味しない。多くはcurrent SEI Requirementの組合せを個人Profileへ具体化したものである。

## 6. 能力から個別課題へ降りる

詳細な設計・要件は、上位のProduct Intentから導出できることを前提とする。

```text
Root Intent
  認識状態を壊さず、中断したInquiryを再開できる
    ↓
Problem
  content保存だけではstate of knowingとmental contextが失われる
    ↓
Product Hypothesis
  Sourceの上にMeaning + Resume layerを置く
    ↓
Capabilities
  preservation / capture / orientation / delta / detail / handoff
    ↓
Candidate Requirements
  PIC-* / ISSUE-local CR-*
    ↓
Acceptance / Falsification
  queryless resume / generic summary comparison /
  late evidence / false continuity / commit integrity ...
    ↓
Prototype / review tooling
  local evaluation CLI / interaction probe / matched review
    ↓
Evidence
  mechanics → actual resumption → comparison → Adoption / Outcome
```

個別のfield、CLI command、timestamp rule、UI state等から上位趣旨を逆算するのではなく、原則としてこの方向へ降りる。

具体的な対応関係は`CONCEPT_TO_REQUIREMENT_DERIVATION.md`を参照する。

## 7. 二つのcurrent検証レーン

2026-09-17時点では、同じPersonal Inquiry Continuity基盤上で二つのIssueが異なる問いを扱っている。

### ISSUE-000073 — Decision Continuity / first usable resume-first slice

Decisionを含む判断仕事について、canonical-only resume、AI provisional boundary、partial commit / stale write、external AI context、H1 actual resume、H2 counterfactual reviewを扱う。

CR-73.1〜10のRequirement auditは完了しており、既存REQでは直接禁止できなかったpartial commitとstale writeだけを一つの意味境界へ統合した。

- `REQ-0023 — Canonical commitの整合性`
- `SCN-0019 — 途中失敗・stale draftを含むcanonical commit`

これはDesign / Requirement formalizationであり、E1〜E8 actual PASSやhuman Product Valueを意味しない。

### ISSUE-000078 — Decision成立前を含むInquiry Continuity

Brand World Product Value Reviewから残った、Decision成立前のopen Inquiryを時間を越えて保てるかをactual dogfoodで検証する。

first actual caseは開始済みでmulti-dayの暦条件へ到達したが、2026-09-16の上流整理でmaterialな事前露出が生じたため、clean resumptionはまだ観測していない。

両Issueのために別々の評価ontologyやsession基盤を作らない。共有できるdogfood state、evaluation sidecar、matched review stage gateは共有し、Issue固有の意味監査だけを分ける。

## 8. 推奨Reading Order

このディレクトリを理解するときは、filename順ではなく次の順に読む。

### Stage 1 — 趣旨とProduct Boundary

1. `README.md` — 根幹の趣旨、問題、Product Hypothesis、必要能力
2. `EXTERNAL_RESEARCH_SYNTHESIS.md` — なぜこの問題が既存研究・製品でどのように現れるか
3. `COGNITIVE_RESUMPTION_MODEL.md` — Durable MemoryとCognitive Resumptionをどう分けるか

### Stage 2 — 趣旨から要件への導出

4. `CONCEPT_TO_REQUIREMENT_DERIVATION.md` — 根幹→能力→候補要件→検証の対応
5. `PRODUCT_PROFILE_REQUIREMENTS_CANDIDATE.md` — PIC-* の詳細
6. `REQUIREMENT_GAP_AUDIT.md` — current REQとの重複・gap
7. `RESEARCH_DERIVED_REQUIREMENT_REVIEW.md` — external researchを受けた優先度・表現再検討
8. `DECISION_CONTINUITY_REQUIREMENT_AUDIT_2026-09-16.md` — ISSUE-000073のCR-73.1〜10をcurrent REQ / SCNへ再照合した監査記録

`DECISION_CONTINUITY_REQUIREMENT_AUDIT_2026-09-16.md`は監査時点のDesign Evidenceである。formalization後のcurrent baselineは`requirements/PRODUCT_REQUIREMENTS.md`と`requirements/ACCEPTANCE_SCENARIOS.md`を正とする。

### Stage 3 — Product Interactionと検証原則

9. `INTERACTION_STATE_MODEL.md` — Product-local stateとdurable semanticsの境界
10. `VALUE_VALIDATION_PROTOCOL.md` — Product Valueをどう反証可能に検証するか
11. `RESEARCH_DERIVED_VALIDATION_AMENDMENTS.md` — queryless resume、late evidence、False Continuity等の追加検証
12. `BRAND_WORLD_DISCOVERY_REBASELINE_2026-09-14.md` — Brand World Discoveryを既存Personal Inquiry Continuityへ再統合した判断
13. `BRAND_WORLD_VALIDATION_AMENDMENT_QUIET_INFRASTRUCTURE_2026-09-14.md` — quiet / proactive surfaceのtrade-off検証

### Stage 4 — actual dogfood

14. `DOGFOOD_SURFACE.md` — evaluation CLIとSource / Meaning / Resume Plane
15. `DOGFOOD_EVALUATION_RECORDING.md` — capture burden、resumption、context gap、False Continuity等をProduct semanticsと分離して記録するsidecar
16. `ACTUAL_DOGFOOD_CASE_QUIET_INFRASTRUCTURE_2026-09-14.md` — first actual open Inquiryの開始記録
17. `ACTUAL_DOGFOOD_CHECKPOINT_2026-09-16.md` — multi-day条件とpre-orientation exposureを分離したcurrent checkpoint

### Stage 5 — ISSUE-000073の実行・human review

18. `DECISION_CONTINUITY_EXECUTION_READINESS_2026-09-16.md` — REQ-0023 / SCN-0019、E1〜E8 runner / verifier、H1 / H2のcurrent実行準備状態
19. `DECISION_CONTINUITY_HUMAN_REVIEW.md` — H1 actual resumptionとH2 matched counterfactual reviewの共通実行入口。H2は`inquiry_continuity_review_runner.py`を073/078で共有し、stimulus提示前のreviewer provenance固定、condition非表示bundle、Decision固有validation、Evidence exportまでを一つの経路で扱う
20. `decision_continuity_counterfactual_matched_set_v1.json`と関連script — H2のrotation、shared stage gate、Decision固有validation、非採点comparison

### Stage 6 — ISSUE-000078の比較・human review

21. `inquiry_continuity_counterfactual_matched_set_v1.json` — raw chat / chronological note / SEI resumeをR1〜R3でcounterbalanceするE78.2 / E78.4 / E78.5のmatched set
22. `inquiry_continuity_review_runner.py` — reviewer provenanceを固定し、phase1 → post → auditを一方向に進めるhuman reviewの正規入口
23. `inquiry_continuity_review_analysis.py` — historical correctness、role separation、unresolved、temporal integrity、burden等をscoreへ潰さず監査するvalidation / projection
24. `inquiry_continuity_review_evidence.py` — complete sessionからhuman observation、semantic audit、review provenanceを分離してexportするEvidence境界
25. `inquiry_continuity_summary_distortion_probe_v1.json` / `inquiry_continuity_summary_distortion_probe.py` — E78.3の正規AI-summary-distortion経路。review-start / audit-reveal receiptではsemantic JSON valueとSHA対象raw bytesが同じJSON値であることを直接API経路でも検証し、value/raw mismatchを拒否する。`validate`は3 source fixtureのGit blob freezeを全件確認し、current probe / packet / response / receipt schemaとtyped audit dimensionsをoperatorへ表示する。probe schema v1はaudit dimensionごとに`id / value_kind / allowed_values`を持ち、detection / preservation / burden / controlを共通pass/failへ正規化しない。reviewer id / prior exposure / response authorshipをexclusive review-start receiptへstimulus提示前に固定し、response schema v1をそのreceipt SHA-256へ結ぶ。歪んだsummary / next questionはhuman response固定前にaudit keyを開かず、matched reviewを同一reviewerで行う場合はその完了後に提示する
26. `inquiry_continuity_summary_distortion_evidence.py` — E78.3でreview-start receiptへ結んだ固定済みhuman responseにpost-reveal semantic auditをSHA-256で結び、review start / human observation / audit reveal / semantic audit / provenanceを分離してEvidence exportする。`preflight`はreview artifactを作らず、選択fixtureのsource blob binding、audit-response / Evidence schema v1、typed dimension契約を表示し、pre-v1 artifactをcurrent contractとして扱わない。audit response / Evidence schema v1はprobeのdimension-specific allowed valuesを検証し、`correction_burden`をlow / medium / high、検出系をdetected / not-detected等として意味を保つ。probeの`audit`は開示予定reference materialを先にcanonical SHA-256へ固定してpacketをメモリ上で構築し、その後exclusive-createのaudit-reveal receipt v1を保存してから同じmaterialを出力する。receipt v1はreview-start receipt SHA-256 / `review_started_at` / response / probe / fixture / audit material / `revealed_at`へ結び、`revealed_at < review_started_at`を拒否する。Evidence exporterでも同じchainを再計算して検証する。Evidence bundleへ実際のstimulus / review questionsを`probe_snapshot`として残す。保存直前にもbundle全体のdigest / chronology / provenance / typed findings / receipt binding / source path / Evidence boundariesを再検証し、tampered bundleや余分な昇格fieldを拒否してからexclusive-createする
27. `run_inquiry_continuity_summary_distortion_checks.py` — E78.3のrepository-local mechanics gate。probe/evidence focused unit tests、canonical validate、3 frozen fixtureのEvidence preflightを一括実行する。local-check result schema v2はcanonical probe semantic SHA-256、runner / probe / Evidence tool / focused testのfile SHA-256、source fixtureのexpected / actual Git blob SHA-1、Python runtimeを`contractSnapshot`へ保存し、source freeze不一致をcheck開始前に拒否する。各checkについてportable command、repo相対cwd、exit code、timeout、stdout/stderr SHA-256とbyte数を保存する一方、rawログ本文とローカル絶対pathは保存しない。launch errorはtype / errnoだけへ縮約する。result全体は保存直前にcount/order/status、digest、mechanics/source identity、Evidence stoplineまで再検証し、tampered / vacuous artifactを拒否してからexclusive-createする。PASSはHuman Evidence / actual long-gap / Product Value / Stable Requirement authorizationではない
28. `inquiry_continuity_assistance_probe_v1.json` / `inquiry_continuity_assistance_probe.py` — E78.6 quiet / proactive / adaptiveの比較scaffold
29. `inquiry_continuity_lifecycle_probe_v1.json` / `inquiry_continuity_lifecycle_probe.py` — E78.7 closure / dormancyのProduct-local比較scaffold

E78.3では以前の`inquiry_continuity_distortion_*`並行経路を廃止しており、`inquiry_continuity_summary_distortion_*`を唯一の維持対象とする。repository-local mechanics確認は`run_inquiry_continuity_summary_distortion_checks.py`を正規入口とし、probe/evidence focused tests、canonical `validate`、3 fixture全てのEvidence `preflight`を一括して確認する。途中停止・未実行checkをPASSへ数えず、source freeze不一致はcheck開始前にfail-closedする。result schema v2の`contractSnapshot`でprobe semantic digest、mechanics file digest、source fixture blob binding、Python runtimeを固定し、各checkのcommand / repo相対cwd / stdout・stderr digestも記録する。rawログ本文とローカル絶対pathは保存せず、launch errorもtype / errnoだけへ縮約する。保存直前にresult v2全体を再検証してtampered / vacuous artifactを拒否し、optional result JSONは上書きしない。PASSはHuman EvidenceやProduct Valueではない。human review開始前にはprobe `validate`と対象fixtureのEvidence `preflight`でもsource freezeとcurrent v1 schema / typed audit contractを確認する。pre-v1 artifactはcurrent review chainへ持ち込まない。`review`はstimulusを出力する前にreviewer id / prior exposure / response authorshipをexclusive review-start receiptへ固定し、response schema v1をそのreceipt SHA-256へ結ぶ。audit / Evidenceではresponseのprovenanceがpre-stimulus declarationと一致しない場合を拒否する。これらの申告metadataは盲検やhuman authorshipの独立証明ではない。human responseはaudit material開示前に固定する。probeの`audit`はまず開示予定reference materialをcanonical SHA-256へ固定してpacketをメモリ上で組み立て、その構築に成功した後でreview-start receipt SHA-256、`review_started_at`、response SHA-256、exact probe、fixture、audit material SHA-256、`revealed_at`をexclusive-create audit-reveal receipt v1へ保存し、`revealed_at < review_started_at`を拒否する。保存成功後にだけ同じmaterialを出力する。post-reveal semantic auditは同じreceiptへ結び、`completed_at`がrevealより前のものを拒否する。Evidence exporterでもaudit material SHA-256を再計算し、receipt作成後のmaterial差し替えを拒否する。receiptのsemantic valueとexact raw bytesも一致しなければならず、durable Evidenceは保存直前に自己整合を再検証してtampered artifactを拒否する。加えてcanonicalized probe JSONのSHA-256でreview response、receipt、audit responseを同じ評価刺激へ固定し、Evidence bundleへそのstimulusとreview questionsを自己完結的に残す。post-reveal findingsはprobe schema v1のtyped audit contractに従い、異質なdimensionを共通pass/failへ畳まない。`unsupported_claim_detection`はovergeneralizationとunsupported dismissalの双方を覆う。どのprobeやEvidence exporterも、実行可能であること自体をhuman review resultやProduct Valueへ昇格させない。

### Stage 7 — EvidenceからRequirementへ戻る

30. `REQUIREMENTS_FORMALIZATION_PLAN.md` — Evidenceからactual Requirementへ進む条件

この順序は「必ず全て読む」という意味ではない。上流の判断に疑問がある場合、下流detailへ進む前に上流へ戻れることを重視する。

## 9. 今後の文書整備順

新しい課題を発見した場合、原則として次の順序で文書化する。

1. **Root Intentとの関係** — 何を守るための課題か。
2. **Problem** — どの失敗・不便・意味損失を防ぐのか。
3. **Evidence / Observation** — research、dogfood、actual repositoryのどこから問題が見えたか。
4. **Design Principle / Capability** — 問題を解くために何が必要か。
5. **Existing Coverage** — current Product Value / REQ / Contractで既に表現されていないか。
6. **Candidate Requirement / Acceptance** — 独立規範が必要な場合だけ具体化する。
7. **Realization** — UI、CLI、schema、algorithm、storage等を選ぶ。
8. **Evidence** — 実装が何を確認でき、何をまだ確認していないかを分ける。

次の進め方は避ける。

```text
implementation idea
  -> field / command / typeを追加
  -> 後から理由を探す
```

代わりに、

```text
root purpose
  -> observed problem
  -> required capability
  -> minimum normative difference
  -> realization
```

の順を優先する。

新しい詳細を追加するとき、既存の上位文書で説明できない場合は、詳細を先に正本化せず、上位仮説自体の不足またはscope creepを先に検討する。

## 10. 現時点のEvidence

### Design / Requirement

- Personal Inquiry ContinuityのProduct hypothesis / candidate requirement
- external researchによるproblem validityの補強
- Source / Meaning / Resume model
- ISSUE-000073 Candidate Requirement audit
- CR-73.8 / CR-73.9を`REQ-0023 / SCN-0019`へformalizeしたcurrent Design baseline

### Executable mechanics / readiness

- local evaluation CLIによるscoped executable mechanics
- dogfood evaluation sidecarとfocused tests
- ISSUE-000073 E1〜E8 interaction probe source
- checkout外で独立に取得したcanonical expected HEAD、clean committed HEAD、source blobを固定するEvidence runner / one-command capture
- Evidence record内の`expected_head == head`、recorded tested commit、source blobへ戻って検証するEvidence verifier
- H2 matched reviewのblinded packet、pre-stimulus reviewer provenance、073/078共通runner、global stage gate、Decision固有validation、evidence export
- ISSUE-000078 matched reviewのreviewer provenance、phase1 / post / audit stage gate、非採点analysis、complete-session Evidence export
- ISSUE-000078 E78.3のsource-fixture blob固定、provisional summary / next question、human response固定後だけのaudit reveal
- ISSUE-000078 E78.3のpre-stimulus reviewer provenance固定、exclusive-create review-start receipt、pre-reveal response SHA-256固定、exact audit material SHA-256固定、exclusive-create audit-reveal receipt、post-reveal semantic audit、review start / human observation / audit reveal / semantic audit / provenance分離、exclusive-create Evidence export
- E78.6 assistance probeとE78.7 lifecycle probeのevaluation-only scaffold

ただし、sourceやrunnerが存在することをactual E1〜E8 Executable PASSやhuman review resultへ読み替えない。ISSUE-000073のGo 1.25.x actual runはまだNot Yet Verifiedであり、ISSUE-000078の各human reviewも未実施である。

### Human / Product Value

- ISSUE-000078 first actual Inquiryは開始済み
- clean long-gap resumption: **Not Yet Observed**
- ISSUE-000078 matched comparison human review: **Not Yet Observed**
- ISSUE-000078 E78.3 human correction / rejection: **Not Yet Observed**
- actual team handoff: **Not Yet Observed**
- ISSUE-000073 H1 actual resume usability: **Not Yet Observed**
- ISSUE-000073 H2 counterfactual human pilot: **Not Yet Observed**。R1相当materialのprovenance固定前提示は回答未固定のためhuman observationへ数えず、同一readerの後続reviewではknown exposureとして扱う
- capture burdenが継続利用可能であること: **Not Yet Established**
- Generic Summary / raw chat / chronological noteに対する価値差: **Not Yet Established**
- voluntary reuse: **Not Yet Observed**
- Adoption / Outcome Evidence: **Not Yet Verified**

したがって、prototypeやreview toolingが整ったことをProduct Value成立と同一視しない。

## 11. 次に進める順序

文書や機能を増やすことより、既に準備した経路からactual Evidenceを得ることを優先する。

1. Go 1.25.xを使えるclean checkoutで、GitHub等の独立したrepository正本からcanonical commit SHAを取得し、`capture_issue_000073_resume_first_evidence.py --expected-head <canonical-commit-sha>`をactual実行して、recorded tested commit / source blob / test結果を再検証する。
2. materialなpre-orientation exposureのないreal InquiryでH1 actual resumptionを実施し、既存sidecarへ`evidence_role=resumption`として記録する。
3. ISSUE-000073 H2 matched counterfactual reviewを`inquiry_continuity_review_runner.py`からhuman readerで少なくとも一rotation実施し、reviewer provenanceを保持したsynthetic pilotとして保存する。known exposureのあるreaderをclean blinded扱いにしない。
4. ISSUE-000078 E78.2 / E78.4 / E78.5 matched reviewを`inquiry_continuity_review_runner.py`からhuman readerで少なくとも一rotation実施し、review provenanceを保持したcomplete sessionからEvidenceをexportする。
5. 同一reviewerでE78.3も行う場合は4を完了・固定した後、`inquiry_continuity_summary_distortion_probe.py`で歪んだsummary / next questionを提示してhuman responseを固定する。probeのaudit packetでreference materialを開いた後、`inquiry_continuity_summary_distortion_evidence.py audit-template`からpost-reveal semantic auditを記録し、`export-evidence`でreview observationとsemantic auditを分離したEvidenceを保存する。
6. ISSUE-000078 actual Inquiryについて十分なcognitive gapが得られた時点でclean resumptionを観測する。
7. Generic Summary / B0 / B1 / P1との比較、capture burden、False Continuity、First Useful Actionを横断して読む。
8. 有効でなかったCapability / cue / candidate requirementを削る。
9. current REQで表現できない独立必要性がactual Evidenceから残った場合だけ、Stable Requirement追加を再検討する。

実行環境が足りないことを理由にEvidence条件を弱めない。Go 1.25.xを要求したE1〜E8を低いtoolchainのPASSで代替せず、clean resumptionに必要な認知的gapを暦上のgapだけで代用しない。E78.3の意図的な歪みを先に見たreviewerの回答を、suggestion提示前のclean matched comparisonやclean resumption Evidenceへ混ぜない。post-reveal semantic auditも、human responseが固定される前の回答として扱わない。

```text
working prototype
  != actual Evidence
  != Product Value proven
  != Stable Requirement justified
```

## 12. この評価で守るstop lines

```text
content retrieved != inquiry resumed
summary != historical authority
later evidence != past decision basis
recommendation != decision
unknown != missing field
retrieval rank != truth
resume cue != canonical meaning
calendar gap != cognitive gap
synthetic human review != actual resumption
post-reveal audit != pre-reveal human response
prototype mechanics != adoption evidence
personal profile convenience != universal semantic requirement
```

この境界を保ちながら、個人にとってSEIが本当に必要な部分だけを残す。

## 13. Natural Japanese review

2026-09-17の更新では、9月10日時点のRoot Concept文書としての役割を維持しながら、その後に増えたDecision Continuity Requirement audit、execution readiness、H1 / H2 human review、Brand WorldからのInquiry Continuity再統合、actual dogfood checkpointをReading Orderへ接続した。

ISSUE-000073とISSUE-000078を別々の評価体系として並立させず、同じPersonal Inquiry Continuity基盤上で、前者はDecisionを含むfirst usable sliceとcommit integrity、後者はDecision成立前を含むopen Inquiryの継続性を検証するレーンとして整理した。dogfood state、evaluation sidecar、matched review stage gateは共有し、意味上必要な監査だけをIssueごとに分ける。

また、REQ-0023 / SCN-0019のformalizationをactual Executable Evidenceへ昇格させず、E1〜E8 actual、H1、H2、clean Inquiry resumption、capture burden、比較上の価値差を未観測のまま明示した。

同日の追加同期では、ISSUE-000078についてmatched human review、Evidence export、E78.3 summary distortion、E78.6 assistance、E78.7 lifecycleまでをReading Orderへ接続した。E78.3は重複していた旧distortion pathを廃止し、source fixture固定とreview→audit順序を持つ`inquiry_continuity_summary_distortion_*`だけを正規入口としたが、これらはすべて実証準備でありhuman / Product Value Evidenceではない。

さらに、E78.3のpost-reveal semantic auditとEvidence exportをReading Orderへ接続した。固定済みhuman responseと後段auditをSHA-256で結びながら別Evidence layerとして保存し、既存Evidenceの上書きを拒否する。これにより実行経路は明確になったが、actual human correction / rejection、clean resumption、SEI固有のProduct Valueは引き続き未観測である。

2026-09-18にはISSUE-000073のH2も078と同じreview runnerへ統合し、stimulus提示前のreviewer provenance固定とcondition非表示bundleを共通化した。R1相当materialがこの固定前に提示された事実は、回答未固定のprotocol exposureとしてのみ扱い、同一readerの後続reviewをclean blindedへ読み替えない。

自然な日本語として全文を再ドラフトし、Root Intent、Product hypothesis、Stable Requirement、evaluation tooling、actual Evidence、Adoption / Outcome Evidenceの境界が変わっていないことを最終監査した。