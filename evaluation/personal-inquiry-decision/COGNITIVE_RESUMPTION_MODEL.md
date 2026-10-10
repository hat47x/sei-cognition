# Personal Inquiry Continuity — Cognitive Resumption Model

更新日: 2026-09-10  
状態: **Research-derived Product Model / Evaluation-only**  
関連: Issue #362 / `EXTERNAL_RESEARCH_SYNTHESIS.md`

## 1. 問題設定

Personal Inquiry Continuityを「長期記憶」とだけ呼ぶと、AI memory / RAG / PKM searchと同じ問題に見える。

しかし個人利用で解きたい問題は二つに分かれる。

1. **Durable Inquiry Memory** — 後から意味を誤読しないために、何を知り、何が不明で、何を根拠に何を決めたかを保存する。
2. **Cognitive Resumption Support** — 中断後、人間が元のmental contextを短時間で再構成し、続きを始められるようにする。

この二つは同一ではない。

```text
Durable Inquiry Memory
  = record of meaning

Resumption Support
  = cue / projection for returning to work

Resumption Support
  reads Durable Inquiry Memory
  but does not authoritatively rewrite it
```

この分離をPersonal Inquiry ContinuityのProduct Model候補とする。

## 2. なぜ分ける必要があるか

### 2.1 summaryは便利だがhistorical authorityではない

AI summaryは再開に有用でも、次の危険がある。

- Unknownを省略する
- Conflictの一方だけを残す
- later evidenceをpast basisへ混ぜる
- RecommendationをDecisionのように短縮する
- source claimとinterpretationを融合する

したがってsummaryを唯一のmemoryにしてはいけない。

### 2.2 canonical dataだけでは再開しにくい

逆に、正確なcanonical recordをすべて表示しても、人間は大量の情報からmental contextを再構成しなければならない。

正確さと再開容易性は別問題である。

### 2.3 Productとして必要なのは二層構造

```text
Layer A: Durable Inquiry Memory
  precise
  historical
  inspectable
  portable

Layer B: Resumption Projection / Cue Layer
  compact
  selective
  replaceable
  regenerable
  personalized
```

Layer Bの誤りは修正可能であり、Layer Aへ戻れることを必須とする。

## 3. Durable Inquiry Memory

Personal ProfileでLayer Aが保持する中心は、current SEI semanticsの範囲を使う。

- Inquiry / question context
- Observation / source claim
- Interpretation / Hypothesis
- Unknown / Conflict
- Cognitive Method Application when material
- Recommendation
- Decision
- principal basis
- Constraint / premise when material
- residual / reopen information
- provenance / reference
- revision / supersession / lineage

新しい`PersonalMemory` Universal型を追加しない。

## 4. Resumption Projection

Layer Bの第一目的は「正しい答えを生成すること」ではない。

> **利用者のmental contextを、続きを始められる程度まで再活性化すること。**

task interruption研究のcontext cue / goal retrievalの考え方をProduct Interactionへ翻訳する。

### 4.1 Orientation Core

再開時に毎回候補となる情報。

- このInquiryは何か
- 直近または現在のfocus
- 重要なUnknown / Conflict
- materialなHypothesis / Recommendation / Decision
- Decisionがあれば主要basis

### 4.2 Epistemic Delta

前回reviewまたはDecision以後の変化。

- new Observation / Evidence
- newly discovered Conflict
- resolved / superseded item
- changed premise / constraint
- new Recommendation / Decision

`Delta`は新しいUniversal typeである必要はない。既存recordのtime / lineageからProjectionとして計算できる可能性がある。

### 4.3 Resume Anchor

「次に何へ戻るか」を短く示すcue。

例は次のとおりです。

- 次はAとBの費用差を確認する
- 仕様Xが不明なためここで停止
- 新資料Yを読んだ後に仮説Hを再検討する

Resume Anchorの性質:

```text
resume anchor
  != Observation
  != Decision
  != truth
  != mandatory workflow next state
```

既存residual / reopen情報として表現できる場合、新規semantic conceptは不要。

### 4.4 Detail Trail

Orientation CoreやDeltaから、必要なsource / evidence / historical detailへ降りるpath。

再開Projectionだけで全情報を閉じない。

## 5. Queryless Reorientation

長期memory systemが優秀でも、利用者が適切なretrieval queryを作れなければ再開できない。

Personal Profileでは、Inquiryを選んだ後の第一操作を検索質問にしない。

```text
find inquiry
  -> open
  -> orientation cues are available
  -> inspect / ask / continue
```

keyword / semantic searchは「どのInquiryかを探す」ためには重要だが、Inquiry内部でのcontext recoveryをquery formulationへ依存させない。

## 6. Three-clock model

Personal Inquiry Continuityでは、少なくとも三種類の時点を区別して考える。

### T1 — Subject / Valid Time

Observation、外部条件、Decision等が対象世界・利用者文脈で成立した時点。

例は次のとおりです。

- 9月1日にサービス価格が変更された
- 9月2日に利用者がDecisionした

### T2 — Capture / Knowledge-entry Time

その情報がSEIへ追加された時点。

例は次のとおりです。

- 9月1日の価格変更を9月5日に初めて記録した

T1とT2を混ぜると、9月2日のDecision時点ですでに価格変更を知っていたように誤読する危険がある。

### T3 — Review Time

利用者がそのInquiryを最後に再定位・reviewした時点。

T3は対象世界の事実ではなくProduct Interaction metadataである場合が多い。

用途は次のとおりです。

- what changed since I last looked?
- unread / unreviewed evidence
- Orientation Deltaの基準

```text
subject time
  != capture time
  != review time
```

T3をUniversal semanticsへ追加する必要はない。Profile-local metadataで十分かをprototypeで検証する。

## 7. bitemporal researchとの関係

bitemporal databaseでは、`valid time`と`transaction time`を分け、現実でfactが成立していた時点とdatabaseがそれを保持していた時点を別に扱う。

SEI Personal Profileはtemporal databaseそのものではないが、次のfailureを避けるために同じ区別が有効である。

```text
observed later
  != known earlier

corrected now
  != always believed corrected value
```

ただし、SEIでいうObservation / Hypothesis / Decisionは単純な真偽factではないため、bitemporal schemaをそのままUniversal Contractへ移植しない。

## 8. Premise / Validity Context

LongMemEval-V2の`premise awareness`は、memoryが内容だけでなく「その前提が現在も有効か」を扱う必要性を示す。

Personal Inquiryでmaterialな場合、次へ戻れることが望ましい。

- このRecommendationは何を前提にしていたか
- DecisionはどのConstraintのもとで行われたか
- 後からその前提が変わったか

ただしSEIは自動的に`valid / invalid`をTruth判定しない。

```text
premise changed
  may trigger review cue
  != old Decision was irrational
  != new Decision is automatic
```

## 9. Orientation is not a current-state collapse

「現在地」を一つのlatest summaryへ平坦化しない。

Inquiryには同時に次が存在し得る。

- conflictするObservation
- competing Hypothesis
- unresolved Unknown
- old Decisionとnew evidence
-複数Recommendation

Orientation Projectionは重要なものを選択してよいが、選択されなかったものが消えたことにはしない。

```text
not shown in orientation
  != resolved
  != rejected
  != superseded
```

## 10. Importance selectionの境界

Orientation Projectionは全recordを表示しないため、importance selectionが必要になる。

候補Realization:

- deterministic rule
- user pin / manual importance
- recency + semantic role rule
- LLM candidate ranking
- sparse associative activation

ただしrankingはsemantic authorityではない。

```text
importance rank
  != truth
  != confidence
  != current validity
```

first prototypeではdeterministic rule + user correctionをbaselineとし、LLM / sparse cognitionは比較対象にするのがよい。

## 11. Resumption packet候補

UIを固定しないが、evaluation用のlogical packetを次のように置ける。

```yaml
orientation:
  inquiry: ...
  current_focus: ...
  unresolved: ...
  material_position: ...

historical:
  latest_decision: ...
  principal_basis: ...

change:
  since_review: ...
  since_decision: ...
  premise_changes: ...

resume:
  anchor: ...
  reopen_conditions: ...

links:
  supporting_detail: ...
```

このschemaをContractとして採用しない。Prototype Projectionの思考補助である。

## 12. Product Interactionへの含意

### start

問いだけで開始可能。

### work

free-form materialを追加し、必要なsemantic commitmentだけ段階的に行う。

### suspend

明示的な終了処理は必須にしない。

任意でResume Anchorを残せる。

### reopen

queryなしでOrientation + Deltaへ触れられる。

### inspect

必要なsource / historical detailへ降りる。

### continue

new materialを現在時点へ追加する。

### decide / revise

Decisionが必要な場合のみ記録し、later evidenceはpast basisへbackfillしない。

## 13. 新しいCandidate Requirementへの影響

### PIC-010 Reorientation Projection

強化候補は次のとおりです。

> Reorientation Projectionは単なる全体要約ではなく、元sourceを大量に再読せずmental contextを再構成して次の作業へ移るためのcue setを提供する。

### PIC-012 Change-since-*

MUST候補へ引き上げてdogfoodする。

理由: current summaryだけではtemporal updateを見落としやすく、再開時に重要なのは「以前から何を知っているか」だけでなく「何が変わったか」である。

### PIC-021 Capture Time / Subject Time

MUST候補へ引き上げてdogfoodする。

historical Decision integrityの成立条件と直接関係する。

### PIC-026 Queryless Orientation

PIC-010へ統合する方が有力。独立Stable REQにはしない。

### PIC-027 Resume Anchor

Product Profile / Interaction要件候補。既存residual semanticsで実現可能性を先に確認する。

### PIC-028 Premise / Validity Context

既存Constraint / Observation / historical contextで表現可能か監査する。新Universal typeを追加しない。

## 14. Prototypeで優先して検査すること

1. Orientation Projectionと普通のsummaryを比較する。
2. queryless openで次の作業へ戻れるか測る。
3. `since_review` deltaが再読source数を減らすか測る。
4. subject timeとcapture timeが異なるlate-arriving evidenceを投入する。
5. changed premiseを入れてold Decisionがhistoricalに保たれるか測る。
6. optional Resume Anchorの有無でreorientationを比較する。
7. orientation rankingの誤りをuserが訂正できるか確認する。

## 15. Stop lines

```text
Resumption Projection != canonical authority
Resume Anchor != Decision
Review Time != Subject Time
Importance != Truth
Current summary != historical state
Premise change != automatic invalidation
AI-generated orientation != authoritative memory
```

これらを守る限り、再開UXを積極的に最適化してもSEIのdurable semantic valueを壊しにくい。