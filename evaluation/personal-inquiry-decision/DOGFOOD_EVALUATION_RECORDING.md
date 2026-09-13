# Personal Inquiry Continuity — Dogfood Evaluation Recording

更新日: 2026-09-14  
状態: **Evaluation-only Observation Sidecar / Not Product Requirement**  
関連: `VALUE_VALIDATION_PROTOCOL.md` / `RESEARCH_DERIVED_VALIDATION_AMENDMENTS.md` / `BRAND_WORLD_VALIDATION_AMENDMENT_QUIET_INFRASTRUCTURE_2026-09-14.md` / ISSUE-000078

## 1. この文書の役割

既存のPersonal Inquiry Continuity dogfood surfaceは、Inquiryの意味状態をlocal JSONへ保存し、Orientation、Generic Summary用baseline material、handoffを生成できます。

一方、actual dogfoodでProduct Valueを比較するには、canonical Inquiry stateとは別に、次のような**評価観測**を残す必要があります。

- 再開時に元sourceやchatを何件開き直したか。
- original concernへ正しく戻れたか。
- Unknown / Conflictを取り落としていないか。
- later informationをpast stateへ混ぜなかったか。
- RecommendationとDecisionを取り違えなかったか。
- False Continuityが起きなかったか。
- captureやsemantic correctionの負担がどの程度だったか。
- Quiet SurfaceとProactive Surfaceでattention burdenやoriginal concern driftに差があったか。

これらをInquiryのcanonical meaningへ混ぜると、評価のための一時的な観測語彙がProduct semanticsを侵食します。

そこで、actual dogfoodでは二つのファイルを明確に分けます。

```text
Inquiry state
  dogfood_core.py / dogfood_cli.py
  = evaluation対象となる意味状態

Evaluation sidecar
  dogfood_evaluation.py / dogfood_evaluation_cli.py
  = その利用をどう観測したか
```

Evaluation sidecarはSEI Universal ContractでもProduct storage formatでもありません。

## 2. なぜsidecarにするか

Product Value評価では、評価項目そのものが実装を歪める危険があります。

たとえば`attention_load`や`source_reopens`をInquiry recordへ直接追加すると、現在の評価protocolで便利だからという理由だけでProduct ontologyへ観測用fieldが入り込みます。

本sidecarでは、次の非同一性を保ちます。

```text
observed Product behavior
  != canonical Inquiry meaning

Evaluation metric
  != Product field

Human review result
  != semantic fact
```

sidecarからStable RequirementやUniversal型を直接作りません。

## 3. ファイル

- `dogfood_evaluation.py` — evaluation sidecarのvalidation、mutation、non-scored comparison Projection
- `dogfood_evaluation_cli.py` — sidecarをlocal JSONへ記録するCLI
- `test_dogfood_evaluation.py` — focused test

schema識別子は次です。

```text
sei.personal-inquiry-continuity-evaluation/v0
```

これはevaluation artifactを見分けるためだけの名前です。

## 4. 最小の開始方法

P1 SEI caseの例です。

```bash
python dogfood_evaluation_cli.py init evaluation.json \
  --case-id pic-real-001 \
  --inquiry-ref 'local://inquiry-001.json' \
  --profile P1-sei \
  --created-at '2026-09-14T03:30:00+09:00'
```

比較profileは次の三つに限定します。

```text
B0-chat-only
B1-final-note
P1-sei
```

この区別は既存`VALUE_VALIDATION_PROTOCOL.md`を再利用しており、新しいProduct Profile定義ではありません。

## 5. Capture burdenを記録する

Inquiry作業中に、SEIへ意味を残すための負担を観測します。

```bash
python dogfood_evaluation_cli.py capture-add evaluation.json \
  --id capture-001 \
  --observed-at '2026-09-14T03:40:00+09:00' \
  --semantic-corrections 1 \
  --burden low \
  --notes 'Unknownの表現だけ一度修正した'
```

`burden`は現段階では次の粗い観測だけに留めます。

```text
low | medium | high | not-observed
```

精密な数値尺度や閾値をProduct Requirementへ先取りしません。

## 6. Resume observationを記録する

数日以上の中断後を主対象とします。ただしCLI mechanics確認の短周期runも、Evidence高さを分ければ記録できます。

```bash
python dogfood_evaluation_cli.py resume-add evaluation.json \
  --id resume-001 \
  --observed-at '2026-09-21T10:00:00+09:00' \
  --surface sei-orientation \
  --source-reopens 1 \
  --chat-reopens 0 \
  --detail-descents 2 \
  --original-concern-retention pass \
  --unresolved-preservation pass \
  --temporal-integrity pass \
  --recommendation-decision-integrity not-applicable \
  --attention-load low \
  --first-useful-action '未確認のProvider条件を調べる'
```

主な観測項目は次です。

- `original_concern_retention`
- `unresolved_preservation`
- `temporal_integrity`
- `recommendation_decision_integrity`
- `false_continuity`
- `source_reopens`
- `chat_reopens`
- `detail_descents`
- `attention_load`

`pass / fail`を判断できない場合は推測せず`not-observed`または`not-applicable`を使います。

## 7. Quiet Infrastructureの比較

Brand World Discoveryから追加された検証では、同一または十分に近いInquiry stateについて、次を比較できます。

```text
sei-quiet
  = current focus / unresolved / material changeを中心に、proactive suggestionを前面へ出さない

sei-proactive
  = AI-generated recommendation / next-question候補を再開面で積極提示する
```

sidecarでは、その差を次で観測します。

- `original_concern_retention`
- `suggestion_attribution_integrity`
- `attention_load`
- `material_change_visibility`
- `source_reopens`
- `false_continuity`

Quiet Surfaceが必ず優れるとは仮定しません。

Proactive Surfaceが重要なConflictやchanged premiseを見つけやすくするなら、それも正当なProduct Value Evidenceです。

```text
quiet
  != fewer suggestions at any cost

proactive
  != better merely because more is shown
```

## 8. Generic Summaryとの比較

既存`dogfood_cli.py baseline-material`から得たflat materialを通常summaryへ渡した場合は、sidecarのsurfaceを`generic-summary`として記録します。

SEI Orientationとの比較では、読みやすさだけではなく次を優先します。

- historical stateを壊していないか。
- Unknown / Conflictが消えていないか。
- Recommendation / Decisionが融合していないか。
- original concernへ戻れるか。
- first useful actionまでの再読量がどう違うか。

Generic Summaryが十分なら、それはSEI固有resume構造を縮小するEvidenceです。

## 9. 比較Projection

```bash
python dogfood_evaluation_cli.py compare evaluation.json
```

`compare`はsurfaceごとに次のraw countをまとめます。

- attempt数
- source / chat reopen数
- detail descent数
- False Continuity数
- historical integrity failure数
- original concern loss数

意図的に総合scoreやwinnerを出しません。

```text
lower reopen count
  + historical corruption
  = successではない
```

また、1回の短周期runからProduct Valueの優劣を決めません。

## 10. Privacyとrepositoryへの保存

real Inquiryの本文をrepositoryへcommitする必要はありません。

特に個人的・社内的なInquiryでは、原文やsource locatorを公開Evidenceへ含めず、必要なら次だけを残します。

- caseを識別できないlocal ID
- category
- profile / surface
-中断期間の粗い区分
- 評価観測
- failureの性質
- Product判断へ必要な匿名化memo

sidecar自体もlocal-onlyでよく、repositoryへ置く必要はありません。

## 11. Evidenceの高さ

次を明確に分けます。

```text
sidecar code test PASS
  != real dogfood completed

short-cycle calibration
  != long-gap resumption Evidence

long-gap resumption observation
  != voluntary reuse

voluntary reuse
  != broad Adoption / Outcome
```

ISSUE-000078で必要なのは、新しいschemaを増やすことではなく、既存Personal Inquiry Continuity仮説がreal Inquiryで価値差を生むかを反証可能にすることです。

## 12. 現在のfocused executable確認

2026-09-14に、repository外のisolated source executionとして次を確認しました。

- `test_dogfood_evaluation.py`相当の5件がPASS。
- `init → resume-add → compare`のCLI smoke pathがexit code 0で完走。
- `compare`がwinnerや単一scoreを生成せず、surface別raw countだけを返すことを確認。

実行環境のPython起動時に本検証と無関係なspreadsheet runtime warmup stderrが出力されましたが、対象test / CLI processはいずれもexit code 0でした。

これはfull repository checkout上のCI Evidenceではなく、sidecar mechanicsに限定したScoped Executable Evidenceです。

## 13. 次のactual dogfood

次は文書やfieldを増やさず、real Inquiryを選びます。

優先するcaseは次です。

1. Decisionがまだないopen Inquiry。
2. 数日以上中断できる。
3. UnknownまたはHypothesisが残る。
4. 元chat / sourceを再読したくなる程度には複雑だが、high-stakesではない。
5. P1 SEIだけでなく、B0またはB1との比較が可能である。

まず一件を丁寧に取り、次に複数caseへ広げます。

actual観測で独立したfailureが出るまで、Stable Requirement、Universal Contract、Product ontologyは変更しません。

## 14. Natural Japanese review

本sidecarは、「評価したいもの」をProduct semanticsへ逆輸入しないことを最重要視して設計しました。

そのため、Inquiryそのものの意味状態と、その利用時に人間が感じた負担や起こした誤認を別のファイルへ置いています。Quiet Infrastructureについても、静かな画面を正解とせず、original concernを保てるか、重要な変化を隠していないか、proactive suggestionによって新しい発見が得られるかを同じ評価面で比較できるようにしました。

自然な日本語として全体を再読し、Product Value、Evaluation、Stable Requirement、Universal Contractのauthority差が曖昧になっていないことを最終監査済みです。
