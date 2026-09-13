# Personal Inquiry Continuity — Value Validation Protocol

更新日: 2026-09-10  
状態: **Evaluation Protocol Candidate — Adoption / Outcome Not Yet Verified**  
関連: GitHub Issue #359 / `PRODUCT_PROFILE_REQUIREMENTS_CANDIDATE.md` / `REQUIREMENT_GAP_AUDIT.md`

## 1. 目的

Personal Inquiry Continuity Profileについて、semantic structureが正しいだけでなく、**一人の利用者が実際に継続して使う価値があるか**を確認する。

このprotocolはProduct Requirementではない。

```text
conformance
  != usability
  != personal outcome
  != adoption
```

PrototypeがContract上正しくても、通常のchat、note、bookmark等より負担が大きく、再開時にも役立たないならPersonal Product Profileとしては失敗である。

## 2. 検証する中心仮説

### H1 — Reorientation Value

数日〜数週間以上空いたInquiryでも、SEI Profileを使うと、元chatや全sourceを大量に再読せずに現在地へ戻れる。

### H2 — Historical Integrity Value

Decision時のbasis、Unknown / Conflict、later Evidenceを分けて保存することで、後から「当時知っていたこと」と「後から分かったこと」を混同しにくくなる。

### H3 — Inquiry Continuity Value

Decisionへ到達していないopen Inquiryでも、途中状態を保持して再開できるため、chat thread単位の断絶を減らせる。

### H4 — AI Portability Value

特定AI conversationを失っても、canonical SEI contextから別AI / toolへ続きを渡せる。

### H5 — Friction Sustainability

H1〜H4の価値を得るためのcapture / correction / Decision記録負担が、個人利用で継続可能な範囲に収まる。

## 3. 比較対象

最低限、次の三形態を比較する。

### B0 — Chat-only

AI conversation history、browser history、元資料等だけを残し、別途structured memoryを作らない。

### B1 — Final-note

利用終了時に、結論または短い自由形式メモだけを残す。

### P1 — SEI Personal Profile

Inquiry、重要なObservation / Evidence、Unknown / Conflict、Hypothesis / Recommendation、Decisionがあればそのbasis / unresolved / reopen情報を意味上区別して保持する。

比較の目的は「SEIが必ず勝つ」ことを証明することではない。

B0/B1で十分な領域を明らかにすることも成果とする。

## 4. Evaluation Stage

### Stage E0 — Semantic / Mechanical Safety

実利用前に、fixture / prototypeで少なくとも次を確認する。

- Recommendation != Decision
- Unknown / Conflict survives Decision
- post-Decision Evidence does not enter historical basis retroactively
- Projection generation does not rewrite canonical state
- LLM absence does not prevent read / manual update
- export / import時にidentity / basis / unresolvedが保持される（実装後）

E0だけでProduct Value成立とはしない。

### Stage E1 — Short-cycle Personal Dogfooding

複数の低〜中影響Inquiryで、実際のcapture → 中断 → reopenを行う。

protocol目安として次を狙うが、Product Requirementにはしない。

- 4件以上のreal Inquiry
- 少なくとも3種類の題材
- Decisionあり / Decisionなしを両方含む
- 少なくとも2件は7日以上空けて再開
- 可能なら1件は21日以上空けて再開

数字自体を成功条件にせず、短期記憶だけで再構成できる状態を避けるためのsampling目安とする。

### Stage E2 — Baseline Comparison

B0 / B1 / P1で類似した題材を扱い、再開時の負担とsemantic integrityを比較する。

同一Inquiryを完全に平行運用すると記憶が相互汚染するため、次のいずれかを使う。

- 類似難度の別題材を交互に割り当てる。
- synthetic scenarioで同一source setを比較する。
- real Inquiryでは過去利用履歴とのqualitative comparisonを行う。

厳密な学術実験ではなく、Product Hypothesis falsificationに十分なEvidenceを狙う。

### Stage E3 — Cross-AI / Cross-session Handoff

元conversationを参照できない条件で、SEI Handoff Projectionだけを別AI / sessionへ渡す。

そのAIが少なくとも次を区別して読み取れるかを確認する。

- current inquiry
- current observation / source claim
- unknown / conflict
- hypothesis / recommendation
- user Decision if any
- historical basis
- later evidence
- reopen condition

回答品質そのものをSEIのsemantic correctnessと同一視しない。

### Stage E4 — Voluntary Reuse Signal

評価用に指定された題材ではなく、利用者が新しいInquiryに自発的にProfileを使うかを観察する。

「使いたい」と回答したことより、実際の再利用を強いAdoption兆候とする。

## 5. Reorientation Task

Inquiryを再開したとき、元資料を開く前にOrientation Projectionだけを読み、次へ回答する。

1. このInquiryは何についてのものか。
2. 現在重要な情報は何か。
3. 何がまだ分からないか。
4. どこにConflictがあるか。
5. 現在の仮説 / Recommendationは何か。
6. Decisionがあるなら何を決め、主なbasisは何か。
7. Decision / 前回review以後に何が変わったか。
8. 次に何を確認すべきか、または何が起きればreopenするか。

項目が当該Inquiryに存在しない場合は`not applicable / not recorded`を明示できればよい。空欄を推測で埋めることを成功としない。

## 6. 独立して観察するMetrics

単一scoreへまとめない。

### M1 — Reorientation Completeness

上記8問のうち、保存状態から回答可能な項目を正しく回収できたか。

「回答できないことが正しい」場合もあるため、coverage率だけでなく誤った補完を別に見る。

### M2 — Recovery Effort

- 元chatを何回開いたか
- 元sourceを何件開いたか
- orientation以外のdetailへ何回降りたか
- 再開から「次の作業を始められる」と判断するまでの経過

時間は環境差が大きいため、固定latency requirementには直結させない。

### M3 — Unknown / Conflict Preservation

Decision時または中断時に存在したUnknown / Conflictを、再開時に取り落とさず識別できたか。

### M4 — Temporal Integrity

later Evidenceをpast basisと誤認しなかったか。

これは重要なhard failureとして扱う。

### M5 — Recommendation / Decision Integrity

AI Recommendationと利用者Decisionを誤って同一視しなかったか。

### M6 — Capture Burden

- Inquiry開始時の必須操作数
- material追加時の必須操作数
- semantic correction回数
- Decision記録時の必須入力
- captureに費やした主観的負担

「操作数最小」だけを目標にせず、意味保存とのtrade-offを記録する。

### M7 — Handoff Continuity

別AI / toolへ渡した際、主要なsemantic distinctionを維持できたか。

### M8 — Portability / Independence

特定LLM / chat / networkなしにread / manual update / exportが成立したか。

### M9 — Voluntary Reuse

評価指定外の新しいInquiryへ自発的に再利用したか。

### M10 — Correction Trust

AI抽出・要約・重要度判断に誤りがあった場合、利用者が元sourceへ戻って理解・訂正できたか。

## 7. Hard Failure

次は一回でも原因分析を要する重大失敗とする。

- RecommendationがDecisionとして保存・表示された。
- Decision後Evidenceがhistorical basisへ混入した。
- open Unknown / Conflictが自動resolvedされた。
- AI summaryがsource/canonical dataを置き換え、元へ戻れなくなった。
- LLM/provider障害により保存済みInquiry自体を読めなくなった。
- import/exportでDecision identityまたはhistorical basisを黙って変更した。
- userが明示的に削除した対象が、通常UI上で意図せず復活した。

Hard Failureがあっても即Product Hypothesis全体を棄却するとは限らないが、「便利だった」という主観評価で相殺しない。

## 8. Candidate Value Gate

次をすべて単一scoreにせず確認する。

### Gate G1 — Mechanics

複数Inquiryで、Orientation Projectionからcurrent state / unresolved / Decision basis / later changeを必要な範囲で再構成できる。

### Gate G2 — Historical Safety

評価中に把握されたhistorical basis retroactive contamination、Recommendation/Decision混同、Unknown自動消失がない。

### Gate G3 — Recovery Benefit

少なくとも一部のreal Inquiryで、B0/B1よりも元chat/sourceの再読が明確に少なく、かつ重要なUnknown / basisをより確実に回収できる。

「全ケースで勝つ」は要求しない。SEIを使う価値が高い問題領域を発見することを重視する。

### Gate G4 — Sustainable Capture

benefitが得られたケースで、利用者が「保存のための監査作業をしている」と感じるほどの過剰入力を常時必要としない。

### Gate G5 — Independence

元chat / current LLMなしでも、保存済みInquiryのread / manual continuationが成立する。

### Gate G6 — Reuse Signal

評価指定外でも再利用したい、または実際に再利用する兆候がある。

G1〜G5を満たしてもG6が無ければ、semantic technologyとして成立していてもPersonal Product Valueは弱いと評価する。

## 9. Falsification / Pivot Conditions

### F1 — Chat summary is enough

B0のbuilt-in chat summary / searchだけで同等以上に再定位でき、SEI固有semantic separationが実用上ほぼ使われない。

**Pivot候補:** workspaceを主製品にせず、AI間handoff / historical decision snapshotの薄いlayerへ縮小する。

### F2 — Final note is enough

自由形式の短いnoteだけで多くのInquiryが十分再開できる。

**Pivot候補:** SEIは全Inquiryではなく、Unknown / Conflict / revisionが多い高複雑度Inquiryに対象をさらに絞る。

### F3 — Structured capture is too expensive

manual semantic correctionが多く、再開benefitよりcapture burdenが勝つ。

**Pivot候補:** free-form first、AI candidate extraction、rule-based extractionを強化する。ただしsemantic correctnessを自動Truth化しない。

### F4 — Decision is rarely the center

real Inquiryの大半でDecision recordが不自然で、open explorationの方が多い。

**Pivot:** `Decision Workspace`表現を廃し、Personal Inquiry Continuityを正式な中心にする。

### F5 — AI handoff is the strongest benefit

human reorientationよりもcross-AI context portabilityが明確に高価値になる。

**Pivot:** Handoff Projection / MCP / clipboard export等をfirst supported surface候補として優先する。

### F6 — Recall becomes the bottleneck

Inquiry数が増えた後、「中身を再開する」より「該当Inquiryを見つける」負担が大きくなる。

**Pivot:** keyword / metadata baselineと比較したうえで、Sparse Associative Cognitive Substrate等によるcandidate recallを次段階評価する。

### F7 — Local-first is not the value

local packaging維持が利用負担を増やし、実際にはhosted accessの方が継続利用に重要となる。

**Pivot:** local-firstをPersonal Profileの唯一のdeploymentにせず、semantic portabilityを保ったhosted profileを検討する。

## 10. Dogfooding記録フォーマット

各Inquiryについて、内容自体をrepositoryへ保存する必要はない。privacy上必要なら評価メタデータだけを残す。

候補record:

```yaml
inquiry_id: local-eval-id
category: technical-choice | learning | purchase | planning | research | other
profile: B0-chat-only | B1-final-note | P1-sei
started_at: ...
reopened_at: ...
decision_present: true | false
original_chat_available_at_reopen: true | false

reorientation:
  answerable_questions: ...
  incorrect_inferences: ...
  source_reopens: ...
  chat_reopens: ...

integrity:
  unresolved_preserved: true | false | not-applicable
  decision_basis_preserved: true | false | not-applicable
  later_evidence_separated: true | false | not-applicable
  recommendation_decision_separated: true | false | not-applicable

burden:
  capture_notes: ...
  corrections: ...
  friction_observation: ...

reuse:
  would_use_again: yes | no | conditional
  actual_unprompted_reuse: true | false
```

内容を公開しなくてもProduct Evidenceを残せる設計とする。

## 11. Evidence Claim Boundary

評価結果の表現を次のように制限する。

```text
fixture passes
  -> scoped executable mechanics evidence

personal dogfood helps on several inquiries
  -> scoped personal outcome evidence

one person reuses voluntarily
  -> first-party adoption signal

none of the above
  -> general-market adoption proven
  -> multi-user operational suitability proven
```

一人の利用者による継続利用が確認できた場合でも、「一般ユーザーに有効」「市場適合した」とは主張しない。

## 12. Formal Requirementへの反映条件

Value validationで得た結果は次の順に反映する。

1. Profile固有の使い方・Surface条件は `requirements/profiles/PERSONAL_INQUIRY_CONTINUITY.md` 候補へ反映する。
2. 既存REQの意味で十分なものは、新REQを追加せずProfile Acceptanceを厚くする。
3. 他Profileでも独立して必要な意味差が確認された場合のみStable REQ追加をIssue / ADRで検討する。
4. UI convenienceや一時的implementation behaviorをUniversal Contractへ昇格させない。
5. Product Valueを得られない要件候補は、設計上美しくても削除・降格できる。

## 13. 次のPrototype Slice

次に実装するminimum sliceでは、少なくとも次を一続きに検証できることが望ましい。

```text
recent inquiries
  -> open orientation
  -> add free-form material
  -> record unknown / recommendation / decision when needed
  -> close process
  -> reopen later
  -> inspect change since decision
  -> export handoff
```

UI frameworkはまだ固定しない。

まずはlocal CLI / minimal Web / desktop probeのいずれでも、このProduct Value loopを安価にdogfoodできることを優先する。
