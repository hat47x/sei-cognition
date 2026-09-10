# Personal Inquiry Continuity — Requirements Formalization Plan

更新日: 2026-09-10  
状態: **Formalization Design — No canonical Requirement change yet**  
関連: GitHub Issue #359

## 1. 目的

Personal Inquiry Continuity Profileの設計を、将来actual `requirements/`へ登録するときの正本構造まで検討する。

current `requirements/README.md`では、Product Requirementの正本入口を`PRODUCT_REQUIREMENTS.md`、Acceptance Scenarioの正本入口を`ACCEPTANCE_SCENARIOS.md`としている。

また、補助分析文書を第二の正本にしないこと、stable IDにProfile等の配置意味を埋め込まないことが明示されている。

したがって、個人向けprototypeのためだけに新しいRequirement authority modelを追加しない。

## 2. 現時点で避ける案

### 2.1 `PIC-*`をそのままStable Requirementへする

避ける。

PIC-001〜025の多くはcurrent REQの個人UX具体化、Acceptance、Packaging constraintであり、独立したcross-product semantic requirementではない。

### 2.2 `requirements/profiles/`を無審査で第二の正本にする

避ける。

Product Profileという正本階層自体がcurrent Requirements authorityに存在しないため、導入するなら別Issue / ADRで正本関係、stable ID、conflict resolutionを決める必要がある。

### 2.3 prototype UIをRequirementへ固定する

避ける。

`recent list`、`orientation screen`、`paste box`、`timeline tab`等は有力なRealization候補だが、価値検証前にstable requirementへ固定しない。

## 3. 推奨する段階的Formalization

### Phase F0 — Evaluation-only design

現在地。

`evaluation/personal-inquiry-decision/`で以下を保持する。

- product hypothesis
- candidate requirements
- gap audit
- value validation protocol
- executable prototype / fixture

この段階ではcanonical Requirementを変更しない。

### Phase F1 — Acceptance-first formalization

Personal dogfoodingで価値仮説が一定程度支持され、current Stable REQの意味でmechanicsが表現できることが確認できた場合、まず`ACCEPTANCE_SCENARIOS.md`へ個人利用を代表するScenarioを追加する。

理由:

- current REQが意味上かなり十分である。
- 不足しているのは「その意味差が個人利用でどう必要になるか」の具体化が大きい。
- Scenario追加はUIやUniversal ontologyを増やさずProduct Valueを実利用へ接続できる。

### Phase F2 — Stable Requirement gap review

F1でScenarioを書いた結果、既存REQだけでは「何が必要か」を規範的に説明できない意味差が残る場合だけ、新しいREQを`PRODUCT_REQUIREMENTS.md`へ追加する。

候補は現時点で次の3領域に限定する。

1. Decisionを要求しないInquiry lifecycle boundary
2. Product data retention / deletion agency
3. automated semantic extraction candidate boundary

いずれも、既存REQの組合せで十分なら追加しない。

### Phase F3 — Product-profile composition document

Personal Inquiry Continuityがactual supported Product Shapeとして継続する場合、`requirements/`配下に個人Profileのcomposition文書を置くことを検討する。

候補path:

```text
requirements/PERSONAL_INQUIRY_CONTINUITY.md
```

ただし役割は第二のRequirement正本ではなく、次の索引・compositionを第一候補とする。

- このProfileがrequiredとするStable REQ / SCN
- Profile固有のsupported / optional capability
- Packaging / Interactionへのtrace
- Evidence状態
- non-goals

Stable normative statementは可能な限りREQ / SCNの正本へ置く。

この方式はcurrent `PRODUCT_JOURNEY_COMPOSITION.md`に近い。

### Phase F4 — Profile authority modelが本当に必要ならADR

将来、Personal / Team / Hosted / Embedded等の複数Product Profileが成立し、各Profile固有MUSTをstableに管理する必要が生じた場合のみ、Product Profile Requirementという新しい正本層をADRで導入する。

それまでは抽象化を先取りしない。

## 4. Acceptance-firstで追加するScenario候補

current SCN-0001〜0018を置き換えず、既存Scenarioでは十分に表現されない個人Product Journeyだけを候補化する。

IDは正式採用時にcurrent registryを確認して割り当てる。以下の`PSC-*`はdraft IDである。

### PSC-01 — DecisionなしのInquiryを後日再開する

#### 状況

利用者は個人研究の問いを開始し、ObservationとUnknownを数件記録したが、結論やRecommendationへ到達せず作業を中断する。

数日後、別sessionから再開する。

#### 期待

- DecisionがなくてもInquiryの保存・再読が成立する。
- Unknownがopenのまま残る。
- 「未完了」だからという理由でDecision作成を要求しない。
- 元chatがなくても現在地を確認できる。

#### 主なexisting REQ

REQ-0001 / 0002 / 0010 / 0014 / 0019 / 0021

### PSC-02 — AI会話を取り込み、意味候補を訂正する

#### 状況

外部AIとの長いconversationを後からSOZAへsourceとして取り込み、AIまたはheuristic RealizationがObservation、Unknown、Recommendation等の候補を抽出する。

一つの候補は誤分類されている。

#### 期待

- raw source / source referenceと抽出candidateを区別できる。
- 誤分類を訂正できる。
- AI抽出candidateをDecisionまたはTruthへ自動昇格しない。
- capture timeとconversation内のsubject timeを混同しない。

#### 主なexisting REQ

REQ-0003 / 0010 / 0011 / 0016 / 0020

### PSC-03 — Decision後の新情報から再検討する

#### 状況

利用者がDecision D1を記録した後、新しいObservation O2を得る。O2はrevisit conditionに関係する。

#### 期待

- D1のhistorical basisへO2を混入しない。
- `D1当時`と`現在`を区別して読める。
- D1を削除せず再検討を開始できる。
- 新Decisionが生じた場合はsemantic lineageを辿れる。

#### 主なexisting REQ

REQ-0005 / 0008 / 0009 / 0014

### PSC-04 — 元AIを失って別AIへInquiryを渡す

#### 状況

Provider Aのchat threadまたはmodelが利用不能になる。利用者はSOZAに保存されたInquiryからhandoff Projectionを作り、Provider Bまたは別toolで続きを行う。

#### 期待

- Inquiry、Unknown / Conflict、Recommendation、Decisionを混同しない。
- past Decision basisとlater Evidenceを区別する。
- private chain-of-thoughtを必要としない。
- Handoff Projectionをcanonical authorityにしない。

#### 主なexisting REQ

REQ-0001 / 0011 / 0015 / 0019 / 0021

### PSC-05 — local / offlineで個人判断記憶を再開する

#### 状況

外部AI / networkが利用不能な状態で、利用者がlocal packageを起動し、保存済みInquiryを開いてUnknownを追加し、必要ならDecisionを記録する。

#### 期待

- read / manual update / saveが外部LLMを要求しない。
- process再起動後に再読できる。
- local implementation detailをcanonical meaningへ混入しない。

#### 主なexisting REQ

REQ-0001 / 0015 / 0018 / 0019 / 0021

### PSC-06 — portable exportから別環境で再開する

#### 状況

利用者がlocal dataをexportし、別data rootまたは別instanceへ移す。

#### 期待

- Inquiry / Decision identityの意味が維持される。
- Decision basis / unresolved / lineageが失われない。
- Storage固有identityだけに依存しない。

#### 主なexisting REQ

REQ-0001 / 0005 / 0018 / 0021

## 5. 新REQ候補の詳細審査

### 5.1 Candidate R-A — Decision-independent Inquiry Continuity

候補文:

> SOZAは、Inquiryの保存、再読、継続をDecisionの存在へ依存させてはならず、未解決のObservation、Unknown、Conflict、Hypothesis、residual等を保持したまま再開できなければならない。

#### 採用に慎重な理由

REQ-0001 / 0002 / 0014の組合せとProduct Interaction baselineから既に導ける可能性が高い。

#### 昇格条件

- PSC-01をexisting REQだけで説明するとnormative ambiguityが残る。
- 複数Product Surfaceで`Decision = completion`へ誤実装される実例が生じる。
- 個人以外のProfileでも同じ境界が必要となる。

### 5.2 Candidate R-B — Explicit Product Data Agency

候補文:

> SOZAは、surviving semantic recordのhistorical integrityと、権限ある利用者がProduct dataの保持・削除を明示的に制御することを区別しなければならない。

#### 独立性

current Stable REQでは直接表現されていない可能性が高い。

#### 注意

Personal Profileだけで決めず、identity、authorization、backup、shared data、legal retention等と合わせる必要がある。

#### 昇格条件

Product Security / Privacy設計で同じ意味境界が必要と確認される。

### 5.3 Candidate R-C — Automated Semantic Candidate Non-authority

候補文:

> 自動抽出・分類・要約によって生成されたsemantic candidateは、その生成だけを理由にsource statement、Observation truth、Recommendation acceptance、Decision等へ自動昇格してはならない。

#### 採用に慎重な理由

REQ-0003 / 0006 / 0011 / 0016 / 0020で既に意味上カバーできる可能性が高い。

また「candidate」というdurable Universal conceptが本当に必要かは未確認。

#### 昇格条件

bulk import / AI-assisted capture prototypeで、draft-local stateだけでは意味保存が不十分と実証される。

## 6. 個人Profileの最低製品境界

正式要件化前でも、Product Value実証のためのminimum supported behaviorは次へ絞る。

```text
one local user
  + multiple inquiries
  + free-form capture
  + unknown/conflict
  + optional recommendation
  + optional decision with basis
  + close/reopen
  + orientation projection
  + later evidence separation
  + portable export
```

AI extraction、handoff、semantic recallは価値を強めるが、first mechanics成立条件にはしない。

## 7. UI Realizationを要件へ混ぜないための境界

候補UI:

```text
Home / Recent
  -> Inquiry Orientation
      -> Add Material
      -> Unknown / Conflict
      -> Recommendation
      -> Decision
      -> Evidence Detail
      -> Handoff / Export
```

これはdogfooding用Realization案でありRequirementではない。

次の置換を許容する。

- CLI
- local Web
- desktop application
- MCP + minimal human viewer
- editor / note integration

いずれでもPSCの意味が満たされればよい。

## 8. Requirement登録前のDefinition of Ready

actual `requirements/`へ変更を入れる前に、少なくとも次を満たす。

1. Personal Inquiry ContinuityがDecision-onlyより適切な中心であることをdogfoodingで再確認する。
2. Decisionあり / なしのreal Inquiryを少なくとも一度ずつ再開する。
3. orientationの不足情報を記録する。
4. capture burdenがどこで発生するか観察する。
5. bulk chat intake / AI handoffの価値順位を確認する。
6. Requirement Gap Auditをactual Evidenceで更新する。
7. PSC候補をcurrent SCNと再度重複監査する。
8. 新REQ候補がexisting REQから本当に独立しているか確認する。
9. Requirement変更が必要な場合、関連Value Axis / ADR / Traceability更新範囲を決める。
10. `requirements/README.md`のauthority modelを変更する必要があるか判定する。

## 9. 現時点の推奨Formalization

最も保守的かつSOZAのcurrent governanceに整合する順序は次である。

```text
current evaluation design
  -> executable personal dogfood surface
  -> personal Outcome evidence
  -> add only necessary Acceptance Scenario(s)
  -> reassess Stable Requirement gaps
  -> add Stable REQ only if independently necessary
  -> optionally add requirements composition document
```

したがって、**最終的にGitHubへ要件文書として登録する方針は維持するが、現時点では正本Requirementを先取りしない。**

この順序により、個人prototypeのProduct Valueから生じた実際の必要性を要件化し、設計上美しいだけの概念をRequirementへ焼き付けることを避ける。
