# Personal Inquiry Continuity — Actual Dogfood Checkpoint 2026-09-16

更新日: 2026-09-16  
状態: **Actual Dogfood In Progress / Context Gap Reset After Material Exposure / Human Observation Not Yet Recorded**  
関連: `ACTUAL_DOGFOOD_CASE_QUIET_INFRASTRUCTURE_2026-09-14.md` / `actual_dogfood_quiet_infrastructure_2026-09-14.inquiry.json` / `actual_dogfood_quiet_infrastructure_2026-09-14.evaluation.json` / ISSUE-000078

## 1. このcheckpointの目的

2026-09-14に開始した最初のactual dogfood caseについて、same-session / same-day calibrationから分離された**multi-day resumptionを実行できる時間条件へ一度到達したこと**と、その後2026-09-16の上流整理でmaterialな事前露出が生じたため、cleanな認知的gapを改めて置く必要が生じたことを記録する。

この文書は再開結果そのものではない。利用者が実際に何を覚えていたか、SEI Orientationだけでどこまで元のconcernへ戻れたか、どの程度sourceを開き直したかは、まだ観測していない。

したがって、現在のEvidenceは次の高さに留める。

```text
actual Inquiry seeded
+ calendar multi-day gap reached once
+ resumption procedure prepared
+ pre-orientation material exposure observed
+ clean context gap reset
!= human resumption observed
!= Inquiry Continuity value established
!= Quiet-first validated
!= Proactive-first validated
```

時間が経過したことや、実験条件上の汚染を発見できたことだけをProduct Value Evidenceへ昇格させない。

## 2. current Inquiry state

現在の問いは次である。

> SEIのInquiry再開Surfaceでは、Quiet-firstとProactive-firstのどちらがoriginal concernを保ちつつmaterial change discoveryとnext useful actionを改善するか。

seed時点ではDecisionを置いていない。

保持している中心状態は次である。

### Observation

- 既存Personal Inquiry Continuity protocolは、reorientation、historical integrity、capture burden、False Continuity、AI handoffをすでに評価対象としている。
- AI-generated recommendationやnext-questionを前面へ大量提示すること自体がoriginal concernを奪う可能性は、既存protocolで独立には測っていなかった。
- Quiet Infrastructureは、materialなConflictやchanged premiseを隠すことではない。progressive disclosureとsemantic omissionを分ける必要がある。

### Unknown

- realなlong-gap Inquiryで、Proactive-firstがQuiet-firstよりoriginal concern driftを増やすか。
- Quiet-firstが重要なmaterial changeの発見を遅らせるか。
- Quiet / Proactiveの適否がInquiryの複雑性、成熟度、risk、利用者状態によって変わるか。

### Hypothesis

- Quiet-firstはoriginal concernとunresolvedの保持を助け、attention loadを下げる可能性がある。
- Proactive-firstはattention loadを増やす一方、material changeやnext useful questionの発見を助ける可能性がある。
- 固定的な二択ではなく、materialityと利用者の要求に応じたadaptive progressive disclosureが優れる可能性がある。

これらは2026-09-14時点のexternalized stateであり、2026-09-16時点の新しい結論ではない。

## 3. 今回の時間条件

case作成時刻は `2026-09-14T03:19:05+09:00` である。

2026-09-16には、case作成からの**暦上のmulti-day gap**へ一度到達した。ただし、その後のbranch統合・上流計画整理の過程でcurrent Inquiry stateへmaterialな再露出が生じたため、現在はcleanなresumptionを実行できる状態とは扱わない。

次回、最後のmaterial exposureから改めて十分なgapが成立し、実際にhuman resumptionを行った場合にのみ、sidecarへ次のような分類を記録する。

```text
evidence_role = resumption
context_gap   = multi-day  # 実際の経過条件に応じる
```

`multi-day`は時間条件の分類であり、十分な認知的忘却が実際に生じたことを保証しない。

特に、評価対象を直前まで読み返していた場合、形式上は数日経過していても強いcontext lossが生じていない可能性がある。この場合はその事実をnotesへ残し、結果を過大評価しない。

## 4. human resumptionで守る順序

次回のhuman observationでは、元chatやsourceを先に開いてはいけない。

最初に利用してよいのは、SEIのcanonical Inquiry stateから生成されたOrientationだけとする。

推奨順序は次である。

1. 元chat / source /今回の設計議論を開かない。
2. `dogfood_cli.py orient actual_dogfood_quiet_infrastructure_2026-09-14.inquiry.json` 相当のOrientationだけを見る。
3. Orientationを読んだ時点で、次を言語化する。
   - 元々何を気にしていたか。
   - 現在の問いは何か。
   - 何がObservationで、何がまだUnknownか。
   - どのHypothesisが残っているか。
   - 次に何を調べる／比較するのが有用か。
4. その後に必要なdetailへ降りる。
5. source / chatを開き直した回数と理由を記録する。
6. 読み返した結果、Orientationだけでは誤って理解していた点があればFalse Continuityとして扱う。

重要なのは「少ない再読で済んだ」ことだけではない。

```text
fast resume
+ wrong historical understanding
= failure
```

である。

## 5. sidecarへ記録する項目

human resumptionを実施した場合、少なくとも次をactual observationとして残す。

- `evidence_role = resumption`
- `context_gap = multi-day`
- `surface = sei-orientation` または比較対象Surface
- `original_concern_retention`
- `unresolved_preservation`
- `temporal_integrity`
- `false_continuity`
- `source_reopens`
- `chat_reopens`
- `detail_descents`
- `attention_load`
- `first_useful_action`

Decisionが存在しないcurrent caseでは、`recommendation_decision_integrity`は無理に評価せず `not-applicable` としてよい。

判断できない項目を推測で`pass`へしない。

## 6. Quiet / Proactive比較を急がない

最初のcleanなmulti-day resumptionでは、まずP1 SEI OrientationがInquiry Continuityとして成立するかを見る。

Quiet-firstとProactive-firstを同時に大量提示すると、比較そのものが再開時のworking memoryへ干渉する。そのため、最初の観測から二Surfaceの優劣を確定しない。

順序効果を避けるには、今後の複数caseで条件を入れ替えるか、同程度の別Inquiryを使う。

```text
first actual resumption
  -> resumption mechanics / meaning preservation

later counterfactual comparison
  -> Quiet vs Proactive trade-off
```

と段階を分ける。

## 7. Generic Summary / B1との比較

P1のcleanなmulti-day resumptionを一件観測できた後に、Generic SummaryまたはB1 Final-note相当との比較へ進む。

ここでもP1を有利にするため比較対象を意図的に弱くしない。

比較対象が十分に機能する場合は、SEI固有の構造を減らすEvidenceとして扱う。

特に確認するのは、

- Unknownが落ちないか。
- ObservationとHypothesisが融合しないか。
- original concernが現在の推測へ置換されないか。
- first useful actionまでに必要な再読がどう異なるか。
- structured capture burdenが差分価値を上回らないか。

である。

## 8. branch運用上の現在地

ISSUE-000078のcheckpointとregistry同期は、`evaluation/issue-000078-dogfood`に集約したDraft PR #408として`develop/v0.2.0`へ統合済みである。

現在は、同じIssueのために新しい継続topic branchを作り直さない。Accepted Development Conventionどおり、通常開発の集約先である`develop/v0.2.0`上で、actual human resumption、counterfactual comparison、sidecar更新、planning同期を**まとまりのよいEvidence単位まで継続**する。

```text
main
  = stable baseline

develop/v0.2.0
  = current ISSUE-000078 continuation lane
```

独立した責務や並行作業が実際に必要になった場合だけtopic branchを使う。同じIssueの細かな作業単位ごとにbranchを増やさない。

`main`へは開発途中の小変更を直接積まず、Evidence bundleと上流判断がまとまった段階で統合する。

branch名やPR番号そのものをProduct ontologyやEvidence authorityとして扱わない。

## 9. 現時点で行わないこと

このcheckpointでは次を行わない。

- sidecarへ架空のhuman observationを書く。
- 暦上のmulti-day gapだけをInquiry Continuity成功とみなす。
- Quiet-firstをProduct PrincipleやStable Requirementへ昇格する。
- `Inquiry`をUniversal semantic entityとして固定する。
- Value Axisを追加する。
- actual failureがないままUI機能を増やす。

## 10. 2026-09-16の事前露出とclean resumption境界

2026-09-16の作業では、branch統合、registry、上流計画を整理する過程で、利用者へcurrent Inquiryの問い、未解決点、Quiet / Proactive比較、次の評価手順を再度説明した。

そのため、この直後にOrientationを提示してhuman resumptionを実施しても、**multi-dayという暦上のgapはあっても、cleanなcontext-loss条件ではない**。この状態をP1のresumption成功または失敗としてsidecarへ記録しない。

```text
multi-day elapsed
+ recent pre-orientation exposure
!= clean multi-day resumption
```

これは実験設計上のprotocol observationとして扱う。evaluation sidecarの`resume_observations`は、実際に比較対象Surfaceを用いて再開を試みたhuman observationだけを記録するため、今回の事前露出だけでは追加しない。

first case自体は破棄しない。2026-09-16の最後の事前露出後から、再び十分なcontext gapを置き、その間に元chat / source /本checkpoint /Inquiry stateを読み返さなかった条件でP1 Orientationから再開する。

次回の実施時には、暦上の経過時間だけでなく、直前の関連情報への露出があったかをnotesへ残す。強い再露出があった場合は、`context_gap=multi-day`であってもEvidence強度を保守的に読む。

この観測により、今後のdogfood protocolでは、単にcase作成時刻からの経過時間だけではなく、**last material exposureからの認知的gap**もhuman review時に確認する必要があることが分かった。ただし、この時点では新しいschema fieldやStable Requirementを追加しない。

## 11. 次の高情報量Evidence

現在もっとも価値が高い次のEvidenceは、**利用者が元chat / sourceを先に開かず、最後のmaterial exposureから十分なgapを置いた後に、Orientationから実際に再開したhuman observation**である。

その観測が得られた後に初めて、

- current Personal Inquiry Continuityで十分か。
- Orientationが過剰／不足か。
- Quiet / Proactive比較をどう組むか。
- Generic Summary / Final-noteとの差が意味を持つか。

を再評価する。

それまでは、Product Value成立を保留する。

## 12. 自然な日本語とEvidence監査

本checkpointは、実行可能になったことと実行済みであることを混同しないために起票した。

2026-09-16には、さらに「時間が経過したこと」と「直前に関連情報を再提示されていないこと」も分ける必要がactual作業から確認された。clean resumptionを急いで成立させず、事前露出があった回をhuman outcomeへ数えない停止線を追加した。

「数日経ったので再開価値が証明された」という近道を避け、時間条件、material exposure、human observation、counterfactual comparison、Product判断を分離している。SEI Cognitionのブランド世界から得たQuiet Infrastructureの着想は、引き続き評価仮説の源泉として利用するが、結果を先取りする規範としては扱わない。

本文を自然な日本語として再読し、Design / Evaluation / Human Evidence / Product Value / Stable Requirementの高さが混在していないことを最終確認した。

## 13. 2026-09-19 Lane F継続時のmaterial exposure

2026-09-19のLane F継続作業では、ISSUE-000078のE78.1 / E78.3、actual dogfood case、Quiet / Proactive比較、clean resumptionの停止線を再確認した。この過程で、利用者へcurrent Inquiryの問いと未解決点、過去のmaterial exposure、次に必要なEvidence条件が再び提示された。

したがって、2026-09-16以後に暦上のgapが伸びていても、2026-09-19時点をclean multi-day resumptionとして扱わない。今回の作業を最後のmaterial exposureとして、認知的gapの起点を改めて後ろへ送る。

```text
calendar gap since 2026-09-16
+ 2026-09-19 material re-exposure
!= clean cognitive resumption
```

この観測だけでは比較対象Surfaceを使った再開を行っていないため、`actual_dogfood_quiet_infrastructure_2026-09-14.evaluation.json`の`resume_observations`は空のまま保持する。架空の`resumption`や`calibration`を追加しない。

次にhuman resumptionを行う場合は、2026-09-19のmaterial exposure以後に十分なgapがあり、その間に元chat、source、Inquiry state、E78.1 / E78.3の評価説明へmaterialに再露出していないことを確認してから、Orientationを最初のSurfaceとして使う。gapの暦上の長さだけでなく、current stateを実質的に思い出せる情報へ触れていなかったかをnotesで明示する。

この追記はProduct ValueやStable Requirementを変更しない。むしろ、actual workの継続そのものがclean resumption条件を壊し得ることをEvidenceとして保守的に扱い、成立していないhuman outcomeを成立済みに見せないためのprotocol checkpointである。
