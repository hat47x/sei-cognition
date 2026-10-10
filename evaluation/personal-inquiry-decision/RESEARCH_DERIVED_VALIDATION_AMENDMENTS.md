# Personal Inquiry Continuity — Research-derived Validation Amendments

更新日: 2026-09-10  
状態: **Evaluation Protocol Amendment / Not Product Requirement**  
関連: Issue #362 / `VALUE_VALIDATION_PROTOCOL.md` / `EXTERNAL_RESEARCH_SYNTHESIS.md`

## 1. 目的

外部researchを踏まえ、existing `VALUE_VALIDATION_PROTOCOL.md`に不足していた検証を追加する。

この文書は既存protocolを置き換えない。Issue #362段階のresearch amendmentであり、dogfood実装前に統合・簡素化してよい。

## 2. 新しい中心比較

従来の比較は次のとおりです。

```text
B0 chat-only
B1 final-note
P1 SEI Personal Profile
```

に加えて、同じSEI source stateから二種類の再開支援を比較する。

```text
S0 Generic Summary
  = source / current notesから一般的な要約を生成

S1 SEI Orientation
  = semantic roles + historical state + unresolved + deltaを用いたresumption cue
```

目的はS1が必ず勝つことを証明することではない。

S0で十分なら、Orientation固有設計を縮小する。

## 3. Test R1 — Queryless Resume

### Setup

- real Inquiryを数日以上中断する
- reopen時に検索queryやAI質問を入力しない
- Inquiryを開いた直後のOrientationだけを読む

### Observe

- Inquiryのcurrent focusを正しく復元できたか
- first useful actionへ進む前に開いたsource / chat数
- detailを開いた回数
- 誤ったbranch / outdated assumptionへ戻らなかったか
- 「次に何をすればよいか」を追加質問なしで判断できたか

### Failure signal

queryを作らなければ意味のある再開ができない場合、PIC-010のProduct Valueは弱い。

## 4. Test R2 — Generic Summary vs Orientation

### Setup

同じInquiry snapshotについて、次を別々に作る。

- S0: semantic roleを特に指定しないgeneric summary
- S1: SEI Orientation

可能なら順序を入れ替え、記憶汚染を減らす。

### Observe

- Unknown / Conflictの保持
- Recommendation / Decisionの区別
- past basis / later evidenceの区別
- current focusの復元
- next actionへの到達
- source再読量
- 読む量 / 認知負担

### Interpretation

S1がより長いだけなら成功ではない。

SEI固有のsemantic separationが、再開の正確さまたは再読削減へ寄与したかを見る。

## 5. Test R3 — Late-arriving Evidence

### Setup

1. Subject time T1で成立した外部事実を用意する。
2. T1より後にDecision Dを記録するが、その時点ではその事実を知らない状態にする。
3. Dより後のCapture time T2で、その事実を初めてSEIへ追加する。

### Expected

- Observationのsubject timeとcapture timeを区別できる
- Dのhistorical basisへObservationを遡及混入しない
- current stateでは新Evidenceとして読める
- Orientationでは`new / learned later`として扱える

### Hard failure

T1がD以前だからという理由だけで、そのObservationをD時点で既知だったbasisとして表示する。

## 6. Test R4 — Premise Change

### Setup

DecisionまたはHypothesisがmaterialなpremise Pに依存する状態を作る。

後からPを変えるObservationを追加する。

### Expected

- old Decision / Hypothesisをhistorical stateとして保持する
- Pが変わったことをcurrent reorientation cueへ出せる
- review / reopenを促してよい
- old Decisionを自動的に`wrong`へ書き換えない
- new Decisionを自動確定しない

### Observe

利用者が「なぜ以前そう考えたか」と「なぜ今は再検討が必要か」を同時に説明できるか。

## 7. Test R5 — Unknown / Abstention

### Setup

意図的に答えが得られていないInquiryを中断・再開する。

### Expected

- Unknownを現在地として表示できる
- AI Orientationを用いる場合も、根拠なしにresolutionを生成しない
- `not known`と`not shown`を混同しない

### Hard failure

orientationを読みやすくするため、Unknownを推測で埋める。

## 8. Test R6 — Resume Anchor A/B

### Setup

類似したInquiryで、

- A: 中断時にResume Anchorを残す
- B: Anchorを残さずcanonical stateだけ残す

を比較する。

### Observe

- first useful actionまでの再読
- wrong branchへの復帰
- Anchor記録負担
- Anchorが古くなった場合の害

### Decision rule

Anchorが明確に有用でも記録率が低い場合、manual mandatory fieldにせずautomatic candidate / lightweight one-action captureを検討する。

効果が弱ければ独立機能化しない。

## 9. Test R7 — Review-time Delta

### Setup

T3aでInquiryをreviewし、その後複数のrecordを追加する。

T3bで再開する。

### Expected

`since last review`として、少なくともmaterialな新規・変更情報を区別できる。

### Observe

- timelineを最初から読む場合とのsource reopening差
- deltaだけで誤ったcurrent stateを作らないか
- importance selectionが重要なConflictを落とさないか

### Boundary

Review timeはProduct Interaction metadataとしてまず扱い、Universal semantic meaningへ先取りしない。

## 10. Test R8 — Cross-AI Role Integrity

### Setup

元AI conversationを利用不能にし、SEI Handoff Projectionだけを別AI / sessionへ渡す。

### Ask

新AIに、次を明示させる。

- observationとして扱っているもの
- unresolvedなもの
- hypothesis / recommendation
- user Decision
- historical basis
- later evidence
- changed premise

### Observe

text内容を思い出せたかではなく、**semantic roleを取り違えなかったか**を評価する。

### Failure signal

Recommendationをuser Decisionとして継承する、later evidenceをpast basisとして継承する等。

## 11. Test R9 — Retrieval vs Resumption Separation

Inquiry数が増えた段階で、二つを別metricにする。

### Findability

目的のInquiryを見つけられたか。

### Resumability

見つけたInquiryのmental contextへ戻れたか。

```text
high retrieval recall
  != successful cognitive resumption
```

Sparse Associative Cognitive Substrate等を導入する場合も、まずFindability改善として評価し、Resumability改善を自動的に主張しない。

## 12. Test R10 — Capture Friction under Real Interruption

rationale captureは、評価時に丁寧に入力できてもreal useでは省略されやすい。

### Observe

- work中にUnknownを残す率
- material basisを残す率
- subject timeを入力 / 推定 / 未記録とする率
- Resume Anchorを使う率
- semantic candidate correctionを放置する率
- captureのために本作業が中断された感覚

### Important

「全部入力されたfixture」はfriction Evidenceにならない。

## 13. Outcome indicatorsの追加

existing Metricsに次を補助指標として追加する候補とする。

### O1 — First Useful Action

reopen後、sourceを探し直す行為ではなくInquiryを前進させる最初の操作へ到達できたか。

### O2 — Source Reopen Count

Orientation後、過去source / chatを何件再び開いたか。

ゼロを目標にしない。detailへ降りるべきときに降りられることも重要。

### O3 — False Continuity

「分かった気になって再開したが、実際にはold state / later state / recommendation / decisionを混同していた」ケース。

これは速さより重大なfailureとする。

### O4 — Cue Utility

Orientationの各cueについて、実際に次の作業へ役立ったか、単なる表示ノイズだったかを後から記録する。

将来のimportance selection改善に使う。

## 14. Minimum dogfood matrix

厳密なsample sizeではなく、failure modeを踏むためのcoverage目安。

| Case | Decision | Unknown | Later evidence | Premise change | Cross-AI | Long gap |
|---|---|---|---|---|---|---|
| A | no | yes | no | no | optional | yes |
| B | yes | yes | yes | no | no | yes |
| C | yes | optional | yes | yes | optional | yes |
| D | no/yes | yes | optional | optional | yes | optional |

real Inquiryのprivacyを守るため、repositoryには内容でなくevaluation metadataだけを残してよい。

## 15. Falsificationを強める

次のいずれかが複数ケースで成立すれば、Product Valueを縮小・pivotする。

### F-A — Generic summary equivalence

S0 Generic SummaryがS1 Orientationと同程度にUnknown / temporal integrityを保ち、同等以下の再読で再開できる。

**Implication:** Orientation-specific structureを減らし、SEIはhistorical snapshot / handoff layerへ薄くする。

### F-B — Delta has no value

`since review / since decision`を見ても次の行動や再読量が変わらない。

**Implication:** PIC-012をMUSTへ上げない。

### F-C — Time distinction is rarely material

subject time / capture timeを区別してもreal Inquiryでhistorical misreadingをほぼ防がず、入力負担だけ増える。

**Implication:** explicit UI fieldを常用せず、必要時だけdetailとして扱う。

### F-D — Resume Anchor decays

Anchorが頻繁に古くなり、むしろ誤誘導する。

**Implication:** automatic current-focus inferenceまたはAnchor廃止を検討する。

### F-E — Source plane duplication dominates

SEIへsourceを複製・整理する作業が中心になり、既存PKMとの二重管理が発生する。

**Implication:** source reference中心へ縮小し、SEIをMeaning / Resume layerへ戻す。

## 16. Advancement condition

formal requirementsへ近づけるためのEvidenceは、次を複数real Inquiryで確認できた場合に強くなる。

```text
queryless orientation helps resume
+ unknown / conflict remain visible
+ temporal updates do not rewrite historical basis
+ change cues reduce rereading or false continuity
+ capture burden remains acceptable
+ user voluntarily reuses the profile
```

この状態でも、まずAcceptance Scenarioへ反映し、Stable Requirement追加は独立必要性を再監査する。