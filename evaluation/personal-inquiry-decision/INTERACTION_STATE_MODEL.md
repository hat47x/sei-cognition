# Personal Inquiry Continuity — Interaction and State Model

更新日: 2026-09-10  
状態: **Product Interaction Design Candidate — Not Universal State Model**  
関連: GitHub Issue #359

## 1. 目的

Personal Inquiry Continuity Profileを実装するとき、利用者に必要な「現在地」とSEIが耐久的に保持するsemantic stateを混同しないための境界を定める。

この文書はworkflow state machineをUniversal Coreへ追加しない。

```text
product interaction state
  != canonical semantic meaning
  != Universal lifecycle state
```

## 2. 一つのInquiryをどう見るか

個人Surfaceでは、一つのInquiryを「作業単位」として開く必要がある。

しかし利用者が見る一枚の画面は、多数のdurable semantic recordとproduct-local stateを合成したProjectionでよい。

概念モデルは次のとおりです。

```text
Durable semantic records
  Inquiry / Question
  Observation / Evidence
  Interpretation / Hypothesis
  Unknown / Conflict
  Method Application
  Recommendation
  Decision
  Reference / Provenance
  Revision / Lineage
  residual / reopen information

        +

Product-local interaction state
  recent/opened
  display ordering
  collapsed/expanded detail
  draft input
  last viewed cursor
  local importance pin

        ↓

Orientation / Detail / Handoff Projections
```

Product-local stateが失われても、Decision historyやUnknownの意味が失われないことを優先する。

## 3. Mandatory lifecycleを作らない

Personal Profileで次の固定state machineを導入しない。

```text
NEW -> RESEARCHING -> RECOMMENDED -> DECIDED -> CLOSED
```

理由は次のとおりです。

- Decisionへ到達しないInquiryがある。
- Decision後もInquiryは生き続け得る。
- 複数Decisionが異なる論点について存在し得る。
- 一度closedに見えるInquiryも新Evidenceで再開し得る。
- 「完了」の意味はdomain依存である。

UIが便宜上status labelを表示しても、そのlabelからDecisionやUnknownの意味を推定しない。

## 4. Derived Product State

操作性のため、Surfaceがdurable dataから状態を導出することは許容する。

例は次のとおりです。

### `exploring`

Decisionが無い、またはcurrent questionに対するclosureを表すDecisionが無い。

### `decision-recorded`

少なくとも一つのDecisionが存在する。

### `new-material-since-decision`

latest relevant Decision後に新しいObservation / Evidenceが追加されている。

### `revisit-candidate`

新materialがreopen conditionに関係する可能性がある。

ただし、これらはProjection / convenience stateであり、次を自動推定してはならない。

```text
exploring != incomplete
new-material-since-decision != Decision invalid
revisit-candidate != Decision must be reversed
```

## 5. Current stateとHistorical state

Orientationでは少なくとも二つの時点を区別する必要がある。

### Current Inquiry State

現在までに得られたObservation、Unknown、Conflict、Hypothesis、Recommendation等から構成する。

### Historical Decision State

Decision Dが成立した時点で明示的にbasisとされた情報、および当時残っていたUnknown / Conflict等から構成する。

```text
current inquiry state
  may include later evidence

historical decision state
  must not include later evidence retroactively
```

UIが一画面に両方を表示する場合も、視覚上または文言上区別可能でなければならない。

## 6. 「重要な情報」の扱い

Orientation Projectionでは全Observationを表示できないため、重要情報の選択が必要になる。

しかし`important`をUniversal truth propertyにしない。

重要度は次のいずれかで決め得る。

- 利用者がpinする。
- Decision basisに含まれている。
- unresolved itemに関連する。
- deterministic policyが選ぶ。
- LLMが候補選択する。
- sparse associative cognitionが候補活性化する。

これらは同じ権威ではない。

```text
selected for orientation
  != more true
  != more authoritative
  != decision basis unless explicitly bound
```

AI / sparse layerによる選択では、元detailへ戻れることを優先する。

## 7. Capture Pipeline

free-form captureとcanonical meaningの間に次の論理段階を置ける。

```text
Material Intake
  -> Source / Raw Reference
  -> Semantic Candidate Extraction (optional)
  -> Review / Policy Application (optional)
  -> Durable Semantic Record
  -> Projection
```

すべてのmaterialが全段階を通る必要はない。

### 7.1 Material Intake

入力例は次のとおりです。

- 自然文メモ
- URL
- file reference
- pasted chat transcript
- AI response
- code / log excerpt

この時点で内容がTruthになったとは扱わない。

### 7.2 Source / Raw Reference

可能な場合、どこから来たmaterialかを辿れる。

完全なraw content複製を必須にはしない。privacy、copyright、storage制約に応じてreference、excerpt、digest、metadata等を使い分ける。

### 7.3 Semantic Candidate Extraction

AI / heuristic処理が候補を作る。

例は次のとおりです。

- Observation候補
- Unknown候補
- Conflict候補
- Hypothesis候補
- Recommendation候補

candidateが誤っている可能性を保持する。

### 7.4 Durable Semantic Record

Product Policy上必要な確認・自動化境界を通過したものをcanonical contextへ追加する。

どの候補にhuman confirmationが必要かはimpact / reversibility / meaning typeによって変え得る。

first low-impact profileでは、すべてのObservation候補へ逐一confirm modalを要求しない。

ただしDecisionだけはRecommendation等から黙って自動生成しない。

## 8. DraftとDurable Record

入力途中の文章、AIが生成中のsummary、未採用candidate等はProduct-local draftとして保持できる。

```text
draft
  != durable semantic record
```

draft lossはUX上問題になり得るが、draftをUniversal semantic entityにする必要性は未確認である。

## 9. Decision Recording Model

Decision記録Surfaceでは、最低限次を分けて扱う。

### statement

何を決めたか。

### basis

何を明示的にDecisionの根拠として用いたか。

### unresolved

Decision時に残っていたUnknown / Conflict。

### rationale / constraint

後から読み直すために重要な場合だけ詳細化する。

### revisit condition

どの条件変化で再検討する可能性があるか。

revisit conditionが空でもDecisionをinvalidにしない。

## 10. Decision後の変化

Decision D1後にObservation O2を追加したとき、Product Surfaceは次を行う。

```text
append O2 to current inquiry context
keep D1 basis unchanged
show O2 as later material relative to D1
optionally evaluate whether O2 relates to reopen condition
```

行ってはならないこと。

```text
append O2 to D1 historical basis automatically
mark D1 wrong automatically
create D2 automatically
resolve old Unknown automatically
```

## 11. Reopen Model

`reopen`を一つのUniversal status switchとして扱わない。

再開とは、利用者またはAIが過去のInquiry / Decision contextを再び現在の認知作業へ持ち込むProduct Interactionである。

Durableに必要な場合は、新Inquiry、new Method Application、new Recommendation、new Decision、semantic lineage等として表現する。

「画面を開いた」こと自体を必ずsemantic eventにしない。

## 12. Last Reviewの扱い

`changes since last review`は有用だが、`last reviewed at`をUniversal semantic fieldへ追加する根拠はまだない。

first prototypeではProduct-local cursorとして実装できる。

```text
last-viewed cursor
  = product convenience
  != decision timestamp
  != evidence timestamp
```

将来、review行為自体がResponsibility / Assurance上重要になるdomainでは、別のdurable semantic requirementとして再検討する。

## 13. Inquiry Discovery

複数Inquiryから対象を見つけるために、first profileでは最低限recent navigationを持つ。

検索方式は段階化する。

### Baseline

- recent
- title / question text
- explicit metadata

### Later

- full-text
- relation-based recall
- semantic similarity
- Sparse Associative Cognitive Substrate

類似度やactivationをInquiryのsemantic relation truthとして保存しない。

## 14. Handoff Model

AI Handoffはcurrent Inquiryから作るProjectionである。

推奨構造は次のとおりです。

```text
Inquiry
Current observations / source claims
Unknown / Conflict
Hypotheses / interpretations
Recommendations
Decisions and historical basis
Later changes
Constraints / reopen conditions
References
```

Handoff生成AIが要約した場合も、canonical recordへ戻れるreferenceを持てることが望ましい。

別AIの回答は新しいObservation / Interpretation / Recommendation等のinputになり得るが、handoff先AIが過去Decisionを書き換える権威を自動取得しない。

## 15. Local Data Control

Personal Profileのlocal stateを次へ分ける。

### Durable Inquiry Data

portable semantic dataとしてexport対象となる。

### Product-local Convenience State

window state、recent ordering、last-view cursor、draft等。

### Optional Provider Cache

LLM response cache、retrieval index等。

削除・backup・exportの期待値が異なるため、一つのopaque databaseへ意味を閉じ込めないことが望ましい。

## 16. Minimal Product Flow

first dogfood Surfaceの論理flow:

```text
[Recent inquiries]
      |
      v
[Orientation]
  question
  current important material
  unresolved
  recommendation / decision
  changes
      |
      +--> [Add material]
      |       -> free-form first
      |       -> semantic assistance optional
      |
      +--> [Detail]
      |       -> source / provenance / history
      |
      +--> [Decision]
      |       -> statement / basis / unresolved / revisit
      |
      +--> [Handoff / Export]
```

この構成は画面数を規定しない。

CLIでは同じflowをcommandとして、desktopではpaneとして実現できる。

## 17. Negative Interaction Cases

prototypeで少なくとも次を試す。

1. DecisionなしのInquiryを閉じて再開する。
2. Recommendationだけ存在し、Decisionはない。
3. Decision後にcontradictory Evidenceを追加する。
4. bulk importのAI分類を利用者が訂正する。
5. 元chatを削除してSEIだけで再開する。
6. networkを切りmanual updateする。
7. old chatを後日importし、capture timeを過去時点と誤認しない。
8. similarity retrievalが無関係なInquiryを上位表示してもTruthへ昇格しない。

## 18. 要件化へ与える示唆

このInteraction modelから新しいUniversal entityは現時点で必要ない。

重要なのは、Product Requirement / Acceptanceで次のnegative boundaryを守ることにある。

```text
Inquiry != workflow session
no Decision != invalid
current state != historical Decision basis
importance selection != truth
AI candidate != accepted semantic meaning
last viewed != semantic review
reopen != mandatory lifecycle status
```

これらがexisting REQ / SCNで十分に守れるかをdogfooding後に再監査する。
