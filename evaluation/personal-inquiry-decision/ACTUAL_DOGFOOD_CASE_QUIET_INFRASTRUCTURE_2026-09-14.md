# Actual Dogfood Case — Quiet Infrastructure / Proactive Assistance

更新日: 2026-09-14  
状態: **Actual Dogfood Initialized — Long-gap Resumption Not Yet Observed**  
関連: ISSUE-000078 / `DOGFOOD_EVALUATION_RECORDING.md` / `BRAND_WORLD_VALIDATION_AMENDMENT_QUIET_INFRASTRUCTURE_2026-09-14.md`

## 1. このcaseの目的

ISSUE-000078を文書設計からactual dogfoodへ進める最初のcaseとして、**Decisionがまだ成立していないopen Inquiry**を一件初期化する。

対象とする問いは次である。

> SEIのInquiry再開Surfaceでは、Quiet-firstとProactive-firstのどちらがoriginal concernを保ちつつmaterial change discoveryとnext useful actionを改善するか。

この問いは、Brand World Discoveryから生じた`Quiet Infrastructure`仮説を、Visual Toneや好みではなくProduct Valueとして反証可能にするためのものである。

本caseは2026-09-14 03:19:05 JSTに開始した。これは、現在の作業を続ける指示を受けてISSUE-000078をactual dogfoodへ進め始めた時点をcase開始時刻とする。

## 2. なぜこのcaseを選ぶか

first actual caseには、次の条件が必要だった。

- Decisionがまだ存在しない。
- Unknownと複数Hypothesisが自然に残る。
- 数日以上中断した後に再開できる。
- high-stakesではない。
- current SEI Product Valueそのものに関係し、再開時の意味差を観測しやすい。
- Quiet / Proactiveという異なるSurfaceを同じunderlying Inquiry stateから比較できる。

このcaseはこれらを満たす。

また、既存Personal Inquiry Continuity protocolがすでに扱っているreorientation、historical integrity、capture burden、False Continuityと、Brand World Discoveryから新しく追加したattention / proactive assistanceの論点を一つのcaseで接続できる。

## 3. authorityとEvidenceの境界

このcaseはProduct Valueを証明したEvidenceではない。

現時点で成立しているのは、

```text
real open Inquiry selected
+ canonical evaluation state initialized
+ observation sidecar initialized
```

までである。

まだ成立していないものは次である。

```text
long-gap resumption
human review
Quiet vs Proactive comparison result
Generic Summary comparison result
voluntary reuse
Adoption / Outcome Evidence
```

したがって、このcaseを理由にProduct Vision、Value Axis、Stable Requirement、Universal Contractを変更しない。

## 4. initial semantic state

machine-readableな初期状態は次を正とする。

- `actual_dogfood_quiet_infrastructure_2026-09-14.inquiry.json`

そこには、開始時点で明示的に外在化できていたObservation、Unknown、Hypothesisだけを置いた。

Decision、Recommendation、review checkpointはまだ置いていない。

### Initial observations

1. 既存Personal Inquiry Continuity protocolは、reorientation、historical integrity、capture burden、False Continuity、AI handoffをすでに扱う。
2. Brand World Discoveryにより、AI-generated recommendationやnext-questionを前面へ大量提示すること自体がoriginal concernを奪う可能性は、既存protocolで独立には測っていなかったと整理された。
3. Quiet InfrastructureはmaterialなConflictやchanged premiseを隠すことではない。

### Initial unknowns

- Proactive-firstがreal long-gap Inquiryでoriginal concern driftを増やすか。
- Quiet-firstがmaterial changeの発見を遅らせるか。
- Quiet / Proactiveの適否がInquiryの性質によって変わるか。

### Initial hypotheses

- Quiet-firstはoriginal concernとunresolvedを保持し、attention loadを下げる可能性がある。
- Proactive-firstはattention loadを増やす一方、material changeやnext useful questionの発見を助ける可能性がある。
- 固定二択よりadaptive progressive disclosureが良い可能性がある。

これらをcurrent truthとして扱わない。

## 5. evaluation sidecar

利用観測は次へ分離した。

- `actual_dogfood_quiet_infrastructure_2026-09-14.evaluation.json`

開始時点では`capture_observations`、`resume_observations`とも空である。

これは意図的である。

caseを作成した事実だけから、利用者のcapture burden、attention load、resume quality等を推測して記録しない。

```text
case initialized
  != human burden observed
```

## 6. B0 / B1 / P1比較の扱い

current seedはP1 SEIのmeaning stateである。

将来の比較では既存protocolに従い、必要に応じて次を作る。

- B0 — Chat-only
- B1 — Final-note
- P1 — SEI

ただし、同じInquiryを三方式で完全並行運用すると、利用者の記憶が相互汚染する。

そのため、このfirst caseでは厳密な同一被験比較より、次の順を優先する。

1. P1 stateを数日以上中断する。
2. 元chatやrepository documentを開く前にOrientation相当へ戻る。
3. actual resumptionを観測する。
4. その後、同じinitial materialからGeneric SummaryまたはFinal-note相当を生成し、historical correctnessと再読負担を比較する。

必要なら別の類似InquiryをB0 / B1へ割り当てる。

## 7. Quiet / Proactive比較の停止線

long-gap再開時には、同じunderlying stateから少なくとも二つのProjection候補を作る。

### Quiet-first

最初に出すものを、current concern、material Observation、open Unknown / Conflict、material change等へ絞る。

AI-generated next-question / Recommendation候補は自動的に前面へ置かない。

### Proactive-first

同じstateに対して、AI-generated next-question / Recommendation / relation候補を再開Surfaceから積極的に提示する。

### 観測するもの

- original concern retention
- unresolved preservation
- material change visibility
- suggestion attribution integrity
- attention load
- source / chat reopen数
- first useful action
- False Continuity

Quiet-firstが勝つことを前提にしない。

```text
fewer suggestions
  != better Product Value

more discovered relations
  != better Product Value
```

## 8. 同日calibrationとlong-gap Evidenceを分ける

初期化直後にOrientationを生成してmechanicsを確認することはできる。

しかし同日には、開始時のmental contextが残っているため、Inquiry ContinuityのProduct Valueを評価できない。

```text
same-day calibration
  = mechanics / surface sanity check

long-gap resumption
  = Product Value hypothesisへのEvidence候補
```

同日calibrationを行った場合もsidecarへ明示的に記録し、long-gap観測と混ぜない。

## 9. 長期再開時の手順

数日以上空いた後、次の順で再開する。

1. 元chat、source document、過去の会話を先に読まない。
2. case IDだけを手掛かりに再開する。
3. P1 Orientationまたは指定されたSurfaceを見る。
4. original concernを自分の言葉で説明する。
5. Observation / Hypothesis / Unknownを区別して説明する。
6. material changeがあれば認識できるか確認する。
7. next useful actionへ進む。
8. その過程で開いたsource / chat数を記録する。
9. False Continuityやsuggestion pressureがあればsidecarへ残す。
10. その後にdetail / sourceへ降り、再構成が正しかったか監査する。

ここで重要なのは、速く答えられることではなく、**速さとhistorical correctnessを同時に見ること**である。

## 10. current next step

このcaseについて、今すぐProduct結論は出さない。

次の高情報量stepは、十分なcontext gapが生じた後のactual resumptionである。

それまでに新しいfieldやSurface機能を増やさない。

必要なのは、現在の最小stateが本当に再開に役立つかを確認することである。

## 11. Natural Japanese review

この文書では、actual caseを開始したこととProduct Valueを実証したことを明確に分けた。

特に、初期化時点で人間の負担や再開品質を推測して埋めず、sidecarを空のまま開始している。Quiet-first / Proactive-firstについてもどちらかを望ましい答えとして先取りせず、original concern、material change、attention、False Continuityを同じ評価面で観測する。

自然な日本語として全文を再読し、Design、Executable mechanics、actual human observation、Adoption / OutcomeのEvidence高さが混同されていないことを最終監査済みである。
