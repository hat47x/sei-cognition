# ISSUE-000073 — Candidate Requirement 再照合監査

更新日: 2026-09-16  
状態: **Evaluation-only Requirement Audit / Design Evidence / Stable Requirementではない**  
対象: ISSUE-000073 / CR-73.1〜CR-73.10

## 1. この監査の目的

ISSUE-000073で定義した10件のCandidate Requirementを、current Product Requirement / Acceptance Scenario / Product Interaction / Reference Architecture / prototype sourceへ戻って再照合し、次を分ける。

1. 既存Stable Requirement / Scenarioですでに規範上の意味を表現できるもの。
2. 既存規範はあるが、human usability / Product OutcomeのEvidenceが不足しているもの。
3. Product / Application / Persistence-local mechanismとして残すべきもの。
4. 既存Stable Requirementだけでは独立したfailureを十分に禁止できず、Stable化候補となるもの。

この監査はRequirement正本ではない。Stable Requirementを採用する場合は、`requirements/PRODUCT_REQUIREMENTS.md`と`requirements/ACCEPTANCE_SCENARIOS.md`へ別途反映する。

```text
Requirement audit
  != Stable Requirement adoption
  != Executable Evidence PASS
  != H1 / H2 human observation
  != Product Value established
```

## 2. 監査時点のbasis

監査結果を後から再読できるよう、主要basisをcurrent blob SHAとともに固定する。

| 文書 / source | blob SHA |
|---|---|
| `requirements/PRODUCT_REQUIREMENTS.md` | `0058593f89b457fb0949bda0d402b450a956131a` |
| `requirements/ACCEPTANCE_SCENARIOS.md` | `6d370c8e67c636609f4b7a3fcdad2ab4acdb30bc` |
| `product/value/SEI_DECISION_CONTINUITY.md` | `65131fcdfd929750c4b96eae5b7c491d7c26488d` |
| `product/interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md` | `5097cda51eee26d0fc2620f7621756bcda1f3107` |
| `architecture/SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md` | `784b773122fb089654b711d60e561c7858027113` |
| `plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md` | `33b7581e3da99aafa31c7b740c3021270365a99c` |
| `runtime/go/interactionprobe/commit.go` | `7b905083bc69a2e88714c89148070a2efa7d8144` |
| `runtime/go/interactionprobe/commit_test.go` | `7b072d57db68ad07266208c715c4884e622ed687` |
| `runtime/go/interactionprobe/provisional.go` | `0a48f7f8ab4b5b7b4cd03f15e7e8107e9b82c52b` |
| `runtime/go/interactionprobe/provisional_test.go` | `43b7502d2a9d10fb1d48ca5f7733745b4b29ad85` |
| `runtime/go/interactionprobe/egress.go` | `5025c10265664674b7d60c051c731506f8ef08e6` |

## 3. 読み方と停止線

本監査では次を同一視しない。

```text
existing semantic coverage
  != Product usability proven

prototype source exists
  != test actually executed

Product-local concurrency token
  != Semantic Revision

Application commit coordinator
  != Universal transaction ontology

selected AI egress context
  != canonical semantic authority
```

また、H1 / H2がまだ未観測であるCandidate Requirementについて、「意味として妥当に見える」ことだけを理由にStable化しない。

## 4. Candidate Requirementごとの再照合

### CR-73.1 — Canonical-only resume

**判定:** 既存Requirement compositionで規範上は表現可能。新Stable Requirementは現時点で不要。

主な既存coverage:

- REQ-0001 — UI / Storage / Provider等が変わっても耐久的意味を読み替えず引き継ぐ。
- REQ-0005 — Decisionを当時basis / unresolved等から歴史的に再構成する。
- REQ-0011 — Projectionをcanonical authorityにしない。
- REQ-0014 — residual / reopen informationを後続reviewへ残す。
- REQ-0019 — human / AI双方が同じcanonical meaningへ戻る。
- SCN-0003 / 0006 / 0016 / 0018。

残るgapは「canonicalだけから人間が実際に短い距離で再開できるか」というOutcome側である。これはH1 / H2で観測すべきで、Stable semantic Requirementを追加して代替しない。

**Disposition:** `no-new-stable-requirement / human-outcome-pending`

### CR-73.2 — Provisional AI boundary

**判定:** 既存REQ-0006、REQ-0013、REQ-0015、REQ-0020、およびAI outputをcanonical authorityへ直結しないInteraction境界で表現可能。

Recommendation、Decision、Authority、Executionを分ける既存規範が、AI suggestionを受信しただけでcanonical Decisionへ昇格させない根拠になる。`ProvisionalRecommendation`はProduct-local draftであり、Universal Draft型を必要としない。

**Disposition:** `no-new-stable-requirement`

### CR-73.3 — Efficient correction / dismissal

**判定:** semantic safetyと操作効率を分ける。

- 修正前suggestionをcanonicalへ黙って残さないこと、dismissalをDecision / negative factとして捏造しないことはREQ-0006 / 0011 / 0013等で説明できる。
- 「efficient」であること、schema / JSON直接編集なしに実務上許容できる負担で訂正できることはhuman interaction Outcomeである。

したがって現在の段階で「効率」をStable semantic Requirementとして数値化しない。H1 / H2でcorrection burdenを観測し、独立したProduct failureが反復して確認された場合にProduct Requirementとして再検討する。

**Disposition:** `existing-semantic-boundary / human-usability-pending`

### CR-73.4 — Change-oriented review

**判定:** 既存coverageで十分。

- REQ-0005 — Decision当時のbasisを後知恵で書き換えない。
- REQ-0009 — revision / supersessionをlatest-winsへ潰さない。
- REQ-0014 — residual / reopenへ戻れる。
- SCN-0003 / 0010 / 0016 / 0018。

`what changed since Decision`はderived Product Projectionとして成立し、新しいUniversal `ChangeSummary`型を要求しない。

**Disposition:** `no-new-stable-requirement`

### CR-73.5 — Progressive explicitness

**判定:** REQ-0010が直接coverageしている。

minimal start、必要になった時点でbasis / Responsibility / Exact Binding等を厚くすること、簡略UIでもcanonical meaningを失わないことは既存REQ-0010、SCN-0004 / 0013で明示済みである。

Product-localなimpact判定をUniversal risk ontologyへ昇格させない。

**Disposition:** `covered-by-REQ-0010`

### CR-73.6 — Graceful AI degradation

**判定:** 新しいUniversal semantic Requirementは不要。既存のRealization / Provider independenceとfirst-slice Product profileの組合せで扱う。

- REQ-0001 — AI / Provider変更・喪失でも耐久的意味を維持する。
- REQ-0007 / 0021 — Provider / Realization交換可能性。
- REQ-0011 — Surfaceをauthorityにしない。
- REQ-0019 — human-readable pathを保持する。
- SCN-0011 / 0014 / 0018。

AI unavailableを案件上の`No`やDecision failureへ変換しないことはsemantic boundaryとして必要だが、AI停止時の具体的manual UXはProduct Interaction / Packaging側のAcceptanceである。

**Disposition:** `existing-independence-requirements / degraded-mode-human-evidence-pending`

### CR-73.7 — Working-set non-authority

**判定:** REQ-0011とREQ-0021で十分。新しいWorkspace / Case / Session / Thread型を追加しない。

working set、recent、pin、filter、form draft、chat state等はProjection / Product-local convenienceであり、破棄してもcanonical meaningを失わない方向を維持する。

**Disposition:** `covered-by-REQ-0011-and-REQ-0021`

### CR-73.8 — Meaning-preserving commit

**判定:** 独立したStable obligation候補。

既存REQ-0001 / 0009 / 0018は耐久性、revision integrity、Storage independenceを要求するが、一つの利用者操作をsuccessful commitとして公開する瞬間に、意味上半端なcanonical stateを成功として見せてはならないことはcurrent Requirement本文で直接禁止されていない。

Product SliceとInteraction ArchitectureではCommit Coordinatorの責務として明示され、`commit.go`には全変更をstagingしてから一括公開するprobe-local実装、`commit_test.go`には途中fault / 後続validation failureでcanonical digestと公開recordを変えないtest sourceが存在する。

ただし、本監査ではrepository checkout上でそのtestを実行していない。source存在をExecutable PASSへ昇格しない。

**Disposition:** `stable-requirement-formalization-candidate`

### CR-73.9 — Stale-write protection

**判定:** CR-73.8と同じStable obligationへ統合するのが適切。

REQ-0009はSemantic Revisionとstorage revisionを区別するが、古いInteraction snapshotから作られたdraftが、その後のcanonical changeを黙って無視・上書きしてsuccessful commitとなることを直接禁止してはいない。

`provisional.go`はcanonical digestをProduct-local snapshot preconditionとして保持し、後続canonical change後のcommitをstaleとして拒否する。`provisional_test.go`には、文言をReviseしてもsnapshotを暗黙更新せず、fresh proposalを明示的に作り直すtest sourceがある。

stale-writeはCR-73.8とは別のontologyではなく、canonical commit integrityを壊す別failure modeである。

**Disposition:** `merge-with-CR-73.8-into-one-stable-requirement-candidate`

### CR-73.10 — AI egress visibility

**判定:** 現時点で新Stable Requirementは追加しない。

主なexisting coverage:

- REQ-0012 — Bounded Collaboration / Selective Disclosure。
- REQ-0013 — actor / Provider kindからAuthorityを推定しない。
- REQ-0021 — external Realizationを交換可能な層に置く。
- REQ-0006 — response受信をDecision / Authorityへ昇格させない。

`egress.go`は選択したLogical Referenceだけからinspection可能なProduct-local `ContextEgressPlan`を作り、external responseをprovisional Recommendationとして受け取る。これはfirst sliceのApplication boundaryを具体化するが、Universal permission modelを新設しない。

今後privacy / security / Product Access policyとして独立した義務が必要になる可能性はある。しかし、「selected contextを見せるUI」や特定Provider送信方式をStable semantic Requirementへ先取りしない。

**Disposition:** `existing-selective-disclosure-and-authority-boundary / policy-and-human-evidence-pending`

## 5. Stable化候補はCR-73.8 / 73.9を一件へ統合する

CR-73.8とCR-73.9を別々のRequirementにすると、同じwrite / commit境界を「atomicity」と「concurrency」に分断して追跡することになる。

利用者にとって守るべき意味は共通している。

```text
commit succeeded
  => 利用者が確定した意味とcanonical stateが矛盾していない
```

したがって、Stable化する場合の最小候補を次とする。

### REQ-0023候補 — Canonical commitの整合性

**候補Type:** Constraint / Non-functional  
**候補Value:** V1 Historical Reconstruction / V3 Revision Integrity / V8 Execution Independence

**候補Requirement:**

一つのProduct Interactionが一つの意味変更としてcanonicalへcommitされる場合、successful commitとして公開されるcanonical stateは、操作前のvalid stateまたは全変更反映後のvalid stateのいずれかでなければならない。途中失敗や後続validation failureによる意味上半端なstateを正常完了として露出してはならない。

また、canonical snapshotを前提に作られたdraft / semantic change planについて、その後に関連するcanonical stateが変化した場合、古いplanが新しい意味を黙って無視・上書きしてsuccessful commitとなってはならない。reject、explicit conflict、明示的なre-plan / rebase等として扱えること。

Persistence transaction、atomic replace、append protocol、ETag、generation、digest、snapshot token等の実現方式をUniversal semanticsとして固定しない。それらからSemantic Revision、Logical Reference、Decision revisionを自動推定しない。

**候補Rationale:**

SEIでは「保存した／commitした」というProduct operationとcanonical meaningがずれると、historical reconstruction、revision integrity、AI correction可能性そのものへの信頼が失われる。partial writeとstale writeはmechanismこそ異なるが、どちらも「successful commitがcanonical truthを誤って表す」という同じfailure boundaryを破る。

## 6. 対応するAcceptance Scenario候補

### SCN-0019候補 — 途中失敗・stale draftを含むcanonical commit

**状況:**

利用者またはmachine clientがcanonical state S0を読み、複数recordを含むsemantic change planを作る。commit途中でfailureまたは後続validation failureが起きるvariantがある。別variantではplan作成後、別操作によってcanonical stateがS1へ変化し、その後S0由来planをcommitしようとする。

**期待:**

- 正常完了として読めるcanonical stateは操作前のvalid stateか全変更反映後のvalid stateである。
- 途中までstagingされた変更をsuccessful canonical stateとして露出しない。
- 後続validation failureで先行変更だけを公開しない。
- stale planがS1の意味を黙って無視・上書きしない。
- staleはreject / explicit conflict / re-plan等として観測可能である。
- concurrency tokenをSemantic Revision / Logical Referenceへ昇格させない。
- Persistence / transaction方式をScenarioからUniversal ontologyへ固定しない。
- commit failureを案件上のnegative factやDecision failureへ自動変換しない。

**必須variant候補:**

- multi-record successful commit
- injected mid-commit failure
- later validation failure
- stale snapshot / fresh explicit re-plan

## 7. CR-73.1〜10の最終Disposition一覧

| CR | 判定 | Stable化判断 |
|---|---|---|
| CR-73.1 Canonical-only resume | 既存REQ composition + Outcome評価 | 新規REQなし。H1/H2待ち |
| CR-73.2 Provisional AI boundary | 既存semantic separation | 新規REQなし |
| CR-73.3 Efficient correction / dismissal | semantic boundary既存、efficiency未観測 | 新規REQなし。human evidence待ち |
| CR-73.4 Change-oriented review | historical / revision / residualでcoverage | 新規REQなし |
| CR-73.5 Progressive explicitness | REQ-0010直接coverage | 新規REQなし |
| CR-73.6 Graceful AI degradation | independence requirement + Product profile | 新規REQなし。degraded UXはhuman evidence待ち |
| CR-73.7 Working-set non-authority | REQ-0011 / 0021 | 新規REQなし |
| CR-73.8 Meaning-preserving commit | 独立commit-integrity failure | CR-73.9と統合してStable化候補 |
| CR-73.9 Stale-write protection | 独立commit-integrity failure | CR-73.8と統合してStable化候補 |
| CR-73.10 AI egress visibility | Selective Disclosure / Authority / Realization境界 | 新規REQなし。Policy / privacy要件は別監査 |

結果として、10件のCandidate Requirementから10件のStable Requirementを作るのではなく、1件だけが新しい規範上の義務候補として残る。

## 8. Evidence監査

### Design Evidence

- CR-73.1〜10のProduct / Architecture境界: Available
- CR-73.8 / 73.9を一つのcommit-integrity obligationとしてまとめる根拠: Available

### Executable Evidence

- `commit.go` / `commit_test.go`: E6を表現する実装・test sourceは存在する。
- `provisional.go` / `provisional_test.go`: E7 stale-draft境界を表現する実装・test sourceは存在する。
- `egress.go`: E8 selected-context / provisional response境界の実装sourceは存在する。

ただし本監査作業ではrepository checkout上のGo testを実行していないため、これらを新たなExecutable PASSとして記録しない。

### Human / Product Outcome Evidence

- H1 actual resume usability: Not Yet Observed
- H2 counterfactual human pilot: Not Yet Observed
- first useful saveまでのactual capture burden: Not Yet Observed
- Decision Continuity Product Value: Not Established

Stable化候補REQの採否と、Decision Continuity Product Outcomeの成立は別判断である。

## 9. 次の作業

1. 本監査をDesign Evidenceとして保存する。
2. CR-73.8 / 73.9統合案をRequirements正本へ反映する場合、REQ-0023 / SCN-0019として一つの整合した変更単位で採番・追跡する。
3. formalization時は`PRODUCT_REQUIREMENTS.md`、`ACCEPTANCE_SCENARIOS.md`、Requirements README、Product / Architecture traceabilityを同時に更新し、第二の正本を作らない。
4. test sourceの存在だけをExecutable PASSへ昇格させず、実行可能な環境でE6 / E7をactualに確認する。
5. H1 / H2はhuman observationを実際に得るまで未観測のまま維持する。
6. CR-73.3 / 73.6 / 73.10はhuman / policy Evidenceが得られるまで、UIやProvider方式をStable Requirementへ先取りしない。

## 10. Natural Japanese review

ISSUE-000073のCandidate Requirementを、Product Value、current REQ-0001〜0022、SCN-0001〜0018、first usable Product Slice、Interaction Working-Set Architecture、current interaction probeへ戻って一件ずつ再照合した。

その結果、resume、AI provisional境界、change-oriented review、Progressive Explicitness、AI degradation、working-set非権威、selected-context egressの主要な意味は、既存RequirementとProduct / Architecture境界の組合せで説明できた。これらをInteractionの都合だけで新しいUniversal型やStable Requirementへ増やさない。

一方、multi-record operationの途中失敗とstale snapshotは、どちらも「successful commitとして公開されたcanonical stateが利用者の確定した意味と食い違う」という共通の独立failureを形成する。そこでCR-73.8 / 73.9を二つへ分割せず、Canonical commitの整合性という一つのStable Requirement候補へ統合した。

この監査自体をStable Requirement adoption、test PASS、human usability、Product Value成立へ拡大解釈せず、formalizationとhuman reviewを後続作業として残す。