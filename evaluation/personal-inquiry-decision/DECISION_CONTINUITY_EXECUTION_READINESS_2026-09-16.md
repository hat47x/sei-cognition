# ISSUE-000073 — Decision Continuity 実行準備状態

更新日: 2026-09-17  
状態: **Current Execution Readiness / Executable and Human Evidence Pending**

## 1. この文書の役割

この文書は、ISSUE-000073で進めているresume-first Product Sliceについて、Candidate Requirement監査、Stable Requirementへのformalization、E1〜E8 prototype、Evidence runner / verifier、H1 / H2 human reviewの現在位置を一つにまとめるcurrent-state文書です。

実行手順の詳細は、機械実行とhuman reviewで入口を分けます。

- E1〜E8: 本書のrunner / verifier手順
- H1 / H2: `DECISION_CONTINUITY_HUMAN_REVIEW.md`

既存の`DECISION_CONTINUITY_REQUIREMENT_AUDIT_2026-09-16.md`は、formalization前に行った監査時点のDesign Evidenceとして保持します。後から得た結論でその監査記録を書き換えません。

```text
historical Requirement audit
  != current Stable Requirement baseline
  != Executable Evidence
  != human Product Evidence
```

## 2. Requirement formalizationの現在地

CR-73.1〜CR-73.10を一件ずつ再照合した結果、すべてを新しいStable Requirementへ昇格させる判断は採りませんでした。

CR-73.1〜73.7および73.10は、既存REQ / SCNで表現できるsemantic boundary、Product / Policy localな責務、またはH1 / H2で観測すべきhuman outcomeへ戻しています。

一方、CR-73.8 Meaning-preserving commitとCR-73.9 Stale-write protectionについては、既存REQだけではsuccessful canonical commitのfailure boundaryを直接禁止しきれないと判断しました。両者は別々のUniversal mechanismへ分けず、一つの規範へ統合しています。

- **REQ-0023 — Canonical commitの整合性**
- **SCN-0019 — 途中失敗・stale draftを含むcanonical commit**

このformalizationで要求しているのは、successful commitとして公開されるcanonical meaningの整合性です。transaction、atomic replace、generation、digest、snapshot token等の実現方式をUniversal semanticsへ固定していません。

```text
REQ-0023 / SCN-0019
  != Universal Transaction entity
  != Universal Snapshot entity
  != Semantic Revision = concurrency version
```

Design Evidenceは成立していますが、actual E6 / E7 runをまだ回収していないためExecutable Evidenceへは昇格していません。

## 3. E1〜E8 prototypeの現在地

`runtime/go/interactionprobe`には、E1〜E8へ対応するprototype / test sourceがあります。

- E1 — canonical-only resume
- E2 — AI correction / dismissal
- E3 — AI unavailable
- E4 — progressive explicitness
- E5 — working-set rebuild
- E6 — semantic commit fault injection
- E7 — stale draft
- E8 — external AI context boundary

sourceやtest名が存在することはExecutable Evidenceではありません。実行結果を固定するため、次のrunnerを用います。

```text
tools/run_issue_000073_resume_first_evidence.py
```

runnerはGo 1.25.xを要求し、`GOTOOLCHAIN=local`で`runtime/go/interactionprobe`を実行します。

さらに、次の条件を満たさないcheckoutではE1〜E8を実行せず`blocked`とします。

- readableなGit HEADがある。
- working treeがcleanである。
- runner自身、`go.mod` / `go.sum`、主要test sourceがHEADと一致する。
- required sourceが欠けていない。
- active Go toolchainが1.25.xである。

低いGo versionやdirty checkoutで得たPASSをISSUE-000073のEvidenceへ読み替えません。

## 4. Evidence verifier

runnerが出力したJSONも自己申告のまま受理しません。次のvalidatorで、recorded tested commitへ戻って再検証します。

```text
tools/verify_issue_000073_resume_first_evidence.py
```

validatorは少なくとも次を確認します。

1. Evidence format / Issue / stop lineが期待値と一致する。
2. `status=pass`であり、clean checkoutとして記録されている。
3. recorded `repository.head`が実際のGit commitとして解決できる。
4. recorded `head_tree`がそのcommitのtreeと一致する。
5. Go 1.25.xが記録されている。
6. 実行commandが`go test -count=1 -json ./interactionprobe`で、`GOTOOLCHAIN=local`である。
7. runnerが列挙した各source bindingについて、recorded HEAD上のblobと一致する。
8. 各sourceのSHA-256をrecorded HEADのbytesから再計算し、一致する。
9. E1〜E8の全experimentが`pass`である。
10. 各experimentに必要な個別testがすべて`pass`である。

Evidence JSON自体を後からrepositoryへcommitしてHEADが進んでも、validatorはrecorded tested commitを参照します。そのため、Evidence保存commitとtested commitを同一commitに見せかける必要はありません。

```text
commit T: actual test対象
  ↓ runner
Evidence JSON records T
  ↓
commit T+1: Evidence JSONを保存
  ↓ verifier
Git object T + source blobsを再検証
```

## 5. verifier self-test

validatorについてはstdlibだけでsynthetic Git repositoryを作るself-testを追加しています。

```text
tools/test_verify_issue_000073_resume_first_evidence.py
```

現在確認したcase:

- cleanなPASS recordを受理する。
- Evidence保存後にHEADが進んでもrecorded tested HEADを検証できる。
- source SHA-256改ざんを拒否する。
- dirtyと記録されたEvidenceを拒否する。
- E8 failを拒否する。
- repositoryに存在しないtested HEADを拒否する。
- Go 1.24.xを拒否する。

このself-testは実際に実行し、PASSを確認しています。

```text
PASS: ISSUE-000073 evidence verifier self-tests
```

これはE1〜E8自体のGo Executable Evidenceではありません。

## 6. actual E1〜E8実行手順

Go 1.25.xが利用可能なclean checkoutで、対象commitを固定して実行します。

例:

```text
git status --porcelain=v1
python tools/run_issue_000073_resume_first_evidence.py \
  --output evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json
```

runnerが`pass`を返した後、保存前または保存後にvalidatorを実行します。

```text
python tools/verify_issue_000073_resume_first_evidence.py \
  evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json \
  --json-out evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json
```

Evidenceをrepositoryへ保存する場合、その保存commitによってcurrent HEADがtested HEADから進むこと自体は問題にしません。validatorはJSON内に記録されたtested HEADを再検証します。

## 7. PASS後に更新してよいEvidence

runnerとvalidatorがともにPASSした場合、E1〜E8については対象commitに限定したScoped Executable Evidenceとして扱えます。

特にE6 / E7については、REQ-0023 / SCN-0019が求める次のfailure behaviorに対するExecutable Evidence候補になります。

- mid-commit faultでpartial canonical stateをsuccessful commitとして公開しない。
- later validation failureで先行changeだけを公開しない。
- stale draftがnewer canonical stateを黙ってoverwriteしない。

ただし、次を自動的には更新しません。

```text
E1-E8 Executable PASS
  != H1 human resume usability observed
  != H2 counterfactual Product Value observed
  != capture / review overhead acceptable
  != Operational Evidence
  != Adoption / Outcome Evidence
  != ISSUE-000073 Resolved
```

## 8. H1 / H2の現在地

H1 actual resume usability reviewとH2 counterfactual Decision Continuity reviewは、実際の人間による観測が必要です。

現時点ではいずれも**Not Yet Observed**です。

具体的な実行手順は`DECISION_CONTINUITY_HUMAN_REVIEW.md`へ一本化しています。

### H1 — real Inquiryのactual resumption

H1では、`DOGFOOD_SURFACE.md`のactual Inquiry stateと`DOGFOOD_EVALUATION_RECORDING.md`のevaluation sidecarを再利用します。別のH1専用schemaやsession managerは作りません。

chat historyや内部schemaの知識へ戻らず、Orientationからcurrent question、Decision、historical basis、unresolved、post-decision changes、next review pointへ戻れるかを観測します。

暦上のgapだけではH1にしません。再開直前にcurrent concernやDecision basisへmaterialな再露出があった場合はclean resumptionとして数えず、架空の`resume_observation`を追加しません。

```text
calendar gap
  != cognitive gap

pre-orientation material exposure
  != H1 resumption Evidence
```

### H2 — matched counterfactual review

H2では、raw chat、chronological note、SEI Resume Projectionを同等素材で比較します。blinded packet、global stage gate、Decision固有validationを用い、reference stateを先に見ないようにします。

completed reviewのEvidence exportは、既存Inquiry Continuity review runnerの`export-evidence`へ統合されています。別のoperational pathを増やしません。

例:

```text
python evaluation/personal-inquiry-decision/inquiry_continuity_review_runner.py \
  export-evidence /tmp/review-session.json \
  --output /tmp/review-evidence.json
```

exportはcompleted sessionだけを受理し、human-review observationとsemantic auditを別collectionとして保持します。synthetic reviewをactual long-gap resumptionやProduct Valueへ昇格させません。

```text
H2 evidence bundle
  != H1 actual resumption
  != actual capture burden
  != Product Value established
```

synthetic fixtureやAI生成回答をhuman observationとして代用しません。また、同じ人がreference stateを事前に見たcaseをblind reviewとして扱いません。

## 9. 現在のEvidence状態

| 項目 | 状態 |
|---|---|
| Product / Architecture Design | Satisfied for current design scope |
| Candidate Requirement audit | Completed as Design Evidence |
| REQ-0023 / SCN-0019 formalization | Accepted / Design Satisfied |
| E1〜E8 test source | Available |
| Evidence runner preflight self-test | PASS |
| Evidence verifier self-test | PASS |
| E1〜E8 actual Go 1.25.x run | **Not Yet Verified** |
| REQ-0023 / SCN-0019 Executable Evidence | **Not Yet Verified** |
| H1 actual human review | **Not Yet Observed** |
| H2 counterfactual human review | **Not Yet Observed** |
| H2 review / evidence-export tooling | Available; actual human session pending |
| Decision Continuity Product Value | **Not Established** |
| Operational Evidence | **Not Yet Verified** |
| Adoption / Outcome Evidence | **Not Yet Verified** |

## 10. 次の停止線

次に必要なのは文書量を増やすことではありません。既存の実行経路からactual Evidenceを得ることを優先します。

優先順位は次です。

1. clean checkout + Go 1.25.xでrunnerをactual実行する。
2. validatorでrecorded tested commit / source blobs / E1〜E8結果を再検証する。
3. actual Evidenceを保存し、REQ-0023 / SCN-0019を含むEvidence状態を再監査する。
4. materialなpre-orientation exposureのないreal InquiryでH1 actual resumptionを実施する。
5. H2 matched reviewをhuman readerで少なくとも一rotation実施し、completed sessionからevidence bundleをexportする。
6. capture / review overheadをH1のreal Inquiryと合わせて読む。
7. human observationを踏まえて、残るCandidate RequirementとDecision Continuity Product hypothesisを再評価する。

実行環境がないことを理由に、Go 1.23.x等の低いtoolchainで代替PASSを作らないことを優先します。human reviewについても、synthetic回答や事前露出済みの記憶をactual resumptionへ読み替えません。

## 11. Natural Japanese review

2026-09-17の更新では、E1〜E8 runner / verifierの既存停止線を変えず、H1 / H2の実行入口を`DECISION_CONTINUITY_HUMAN_REVIEW.md`へ一本化しました。

H1は既存dogfood stateとevaluation sidecarを利用し、real Inquiryのactual resumptionだけを観測します。H1専用のschemaやsession managerは増やしていません。H2は既存matched review基盤を利用し、completed sessionのEvidence exportも既存Inquiry Continuity review runnerへ統合された経路を使います。

これにより、実行準備文書からH1 / H2へ進む経路は一本化しつつ、real Inquiryとsynthetic matched review、human observationとsemantic audit、mechanicsとProduct Valueの意味差は維持しました。

自然な日本語として全文を再読し、REQ-0023 / SCN-0019のDesign Evidence、E1〜E8 Executable Evidence、H1 / H2 human observation、Adoption / Outcome Evidenceの高さを混同していないことを最終監査しました。
