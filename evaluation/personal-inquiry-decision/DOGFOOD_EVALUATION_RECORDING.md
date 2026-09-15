# Personal Inquiry Continuity — Dogfood Evaluation Recording

更新日: 2026-09-16  
状態: **Evaluation-only Observation Sidecar / Not Product Requirement**  
関連: `VALUE_VALIDATION_PROTOCOL.md` / `RESEARCH_DERIVED_VALIDATION_AMENDMENTS.md` / `BRAND_WORLD_VALIDATION_AMENDMENT_QUIET_INFRASTRUCTURE_2026-09-14.md` / ISSUE-000078

## 1. この文書の役割

既存のPersonal Inquiry Continuity dogfood surfaceは、Inquiryの意味状態をlocal JSONへ保存し、Orientation、Generic Summary用baseline material、handoffを生成できる。

actual dogfoodでProduct Valueを比較するには、それとは別に、再開時の負担、誤認、historical correctness、attention等の**評価観測**を残す必要がある。

そこで二つの状態を分離する。

```text
Inquiry state
  dogfood_core.py / dogfood_cli.py
  = evaluation対象となる意味状態

Evaluation sidecar
  dogfood_evaluation.py / dogfood_evaluation_cli.py
  = その利用をどう観測したか
```

Evaluation sidecarはSEI Universal ContractでもProduct storage formatでもない。

## 2. sidecarへ分ける理由

`attention_load`、`source_reopens`、`false_continuity`等は、現在のProduct Value仮説を評価するための観測語彙である。これらをInquiryのcanonical meaningへ直接追加すると、評価設計がProduct ontologyを逆向きに規定してしまう。

本sidecarでは次を保つ。

```text
observed Product behavior
  != canonical Inquiry meaning

Evaluation metric
  != Product field

Human review result
  != semantic fact
```

sidecarからStable RequirementやUniversal型を直接導かない。

## 3. ファイルとauthority

- `dogfood_evaluation.py` — sidecar validation、mutation、non-scored comparison Projection
- `dogfood_evaluation_cli.py` — local JSONへ評価観測を記録するCLI
- `test_dogfood_evaluation.py` — focused test

schema識別子は `sei.personal-inquiry-continuity-evaluation/v0` とする。これはevaluation artifactを識別するための名前であり、portable Contractではない。

Pythonを使うのは既存Personal Inquiry Continuity dogfood surfaceと同じevaluation-only prototypeだからであり、ADR-0027のproduction runtime language policyを変更しない。

## 4. caseの開始

P1 SEI caseの例:

```bash
python dogfood_evaluation_cli.py init evaluation.json \
  --case-id pic-real-001 \
  --inquiry-ref 'local://inquiry-001.json' \
  --profile P1-sei \
  --created-at '2026-09-14T03:30:00+09:00'
```

比較profileは既存protocolをそのまま用いる。

```text
B0-chat-only
B1-final-note
P1-sei
```

## 5. Capture burden

Inquiry作業中に、意味を残すための補正や負担を観測する。

```bash
python dogfood_evaluation_cli.py capture-add evaluation.json \
  --id capture-001 \
  --observed-at '2026-09-14T03:40:00+09:00' \
  --semantic-corrections 1 \
  --burden low \
  --notes 'Unknownの表現だけ一度修正した'
```

`burden`は現段階では `low | medium | high | not-observed` の粗い観測に留める。固定scoreや成功閾値にはしない。

## 6. Resume observation

再開観測では、surfaceや結果だけでなく、**その観測が何のEvidenceなのか**を明示する。

```bash
python dogfood_evaluation_cli.py resume-add evaluation.json \
  --id resume-001 \
  --observed-at '2026-09-21T10:00:00+09:00' \
  --surface sei-orientation \
  --evidence-role resumption \
  --context-gap multi-day \
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

### 6.1 Evidence role

`evidence_role`は次だけを使う。

```text
calibration
  = mechanics / Surface sanity check

resumption
  = context loss後の再開観測

not-observed
  = まだ分類できない
```

同日または同一sessionでProjectionが正しく表示されたことを、long-gap resumption Evidenceとして集計しない。

### 6.2 Context gap

`context_gap`は次の粗い区分を用いる。

```text
same-session
same-day
multi-day
multi-week
not-observed
```

これは「何日ならProduct Valueが成立する」というRequirementではない。短期記憶が残る条件と、実際にmental contextを再構成する条件を後から区別するための評価metadataである。

暦上のgapだけでは認知的context lossを保証しない。resume対象のInquiry state、元chat、source、評価設計等へ直前にmaterialな再露出があった場合は、その事実をhuman reviewのnotesへ残し、Evidenceを保守的に読む。

## 7. 観測する意味上の失敗

主な観測項目は次である。

- `original_concern_retention`
- `unresolved_preservation`
- `temporal_integrity`
- `recommendation_decision_integrity`
- `suggestion_attribution_integrity`
- `material_change_visibility`
- `false_continuity`
- `source_reopens`
- `chat_reopens`
- `detail_descents`
- `attention_load`

判断できないものを推測で埋めず、`not-observed`または`not-applicable`を用いる。

## 8. Quiet Infrastructureの比較

Brand World Discoveryから追加した検証では、同じunderlying Inquiry stateから次を比較する。

```text
sei-quiet
  = current concern / unresolved / material changeを中心にし、
    proactive suggestionを自動的に前面へ出さない

sei-proactive
  = AI-generated recommendation / next-question候補を
    再開Surfaceから積極的に提示する
```

比較対象は、original concern retention、suggestion attribution integrity、attention load、material change visibility、source reopen、False Continuity等である。

Quiet-firstが優れることを前提にしない。Proactive Surfaceが重要なConflictやchanged premiseを見つけるなら、それも正当なEvidenceである。

```text
quiet
  != fewer suggestions at any cost

proactive
  != better merely because more is shown
```

## 9. Generic Summaryとの比較

既存`dogfood_cli.py baseline-material`から得たflat materialを通常summaryへ渡した場合は、surfaceを`generic-summary`として記録する。

SEI Orientationとの差は、文章の読みやすさだけでなく、historical state、Unknown / Conflict、Recommendation / Decision、original concern、first useful actionまでの再読量で見る。

Generic Summaryで十分なら、それはSEI固有resume構造を縮小するEvidenceである。

## 10. 比較ProjectionはEvidence高さを混ぜない

```bash
python dogfood_evaluation_cli.py compare evaluation.json
```

`compare`は最初に`evidence_role`で分け、その内側をsurface別に集計する。

概念上は次の形になる。

```text
by_evidence_role
  calibration
    sei-orientation
    sei-quiet
    ...
  resumption
    sei-orientation
    generic-summary
    ...
```

各surfaceにはattempt数、context gap内訳、source / chat reopen、detail descent、False Continuity、historical integrity failure、original concern loss等のraw countを保持する。

**calibrationとresumptionを合算した総計は作らない。**

また、単一scoreやwinnerも出さない。

```text
same-day calibration PASS
  != multi-day resumption PASS

lower reopen count
  + historical corruption
  = successではない
```

## 11. Privacy

real Inquiry本文をrepositoryへcommitする必要はない。個人的・社内的なInquiryでは、原文やsource locatorを公開Evidenceへ含めず、必要ならlocal ID、category、profile / surface、context gap、評価観測、failureの性質、匿名化memoだけを残す。

sidecar自体もlocal-onlyでよい。

## 12. Evidenceの高さ

次を常に分ける。

```text
sidecar code test PASS
  != real dogfood completed

calibration
  != resumption

same-day observation
  != long-gap resumption Evidence

long-gap resumption observation
  != voluntary reuse

voluntary reuse
  != broad Adoption / Outcome
```

ISSUE-000078の目的は新しいschemaを増やすことではなく、既存Personal Inquiry Continuity仮説がreal Inquiryで価値差を生むかを反証可能にすることである。

## 13. focused executable確認

2026-09-14の初回sidecar実装では、repository外のisolated source executionで6件のfocused testと`init → resume-add → compare`のCLI smoke pathを確認した。

その後、actual caseを初期化した段階で、同日calibrationとlong-gap resumptionを同じsurface集計へ混ぜ得る不足を発見した。このため本revisionでは`evidence_role`と`context_gap`を追加し、comparison ProjectionをEvidence role別へ変更した。

本revisionでは、少なくとも次の回帰条件をtestとして固定した。

- 同じsurfaceでもcalibration / resumptionを別集計にする。
- context gapを比較結果から失わない。
- 不正なEvidence role / context gapを拒否する。
- False Continuityやhistorical integrity failureを総合scoreへ潰さない。

このrevisionのtest定義が存在することと、full repository環境での実行Evidenceは分ける。GitHub Actionsを成立条件にはしない。

## 14. current actual case

最初のactual open Inquiryとして、次をstable baselineである`main`へ初期化し、その後`develop/v0.2.0`へ同期済みである。

- `ACTUAL_DOGFOOD_CASE_QUIET_INFRASTRUCTURE_2026-09-14.md`
- `actual_dogfood_quiet_infrastructure_2026-09-14.inquiry.json`
- `actual_dogfood_quiet_infrastructure_2026-09-14.evaluation.json`

開始時点ではDecision 0件、Review 0件であり、evaluation sidecarにもhuman observationを入れていない。

2026-09-16にはmulti-dayの暦条件へ到達したが、上流計画・branch整理の説明中にcurrent Inquiry stateへ再露出したため、その直後の再開はcleanなcontext-loss条件として扱わない。sidecarの`resume_observations`は引き続き空のまま保つ。

次の高情報量stepは文書追加ではなく、最後のmaterial exposureから十分なcontext gapを置いた後のactual resumptionである。同日calibrationを実施しても`evidence_role=calibration`としてのみ扱う。

## 15. Pre-orientation exposureの扱い

human resumptionの前に、元chat、source、canonical Inquiry state、評価設計の説明等から、current concernやUnknown / Hypothesisを実質的に思い出せる情報へ再露出した場合、その回をclean resumptionとして数えない。

```text
calendar gap
  != cognitive gap

pre-orientation material exposure
  + no actual surface use
  != resume observation
```

この場合は、必要に応じてcheckpointやhuman review memoへprotocol observationとして残すが、実際に比較対象Surfaceを使って再開を試みていない限り、sidecarへ架空の`resume_observation`を追加しない。

一方、軽微な関連情報を偶然見たからといってcase全体を自動破棄しない。何へ再露出したか、どの程度current stateを再活性化し得たかを記録し、その後に十分なgapを置く。

現時点では`last_material_exposure`等を新しいschema fieldへ追加しない。複数caseで同じfailureが再現し、machine-readable比較に必要だと確認された場合にだけschema変更を検討する。

## 16. Natural Japanese review

本sidecarは、「評価したいもの」をProduct semanticsへ逆輸入しないことに加え、**異なるEvidence高さを一つの数字へ混ぜないこと**を重視する。

actual caseを作ったことで、文書上は分けていたsame-day calibrationとlong-gap resumptionが、machine-readableな比較では混ざり得ることが分かった。さらに2026-09-16の継続作業では、暦上のmulti-day gapがあっても、再開前にmaterialなstate説明へ再露出すればcleanなresumption条件が崩れることをactualに確認した。

そこで、後から人が注意して読み分けるだけではなく、sidecar自体では実際に行ったresume observationだけを記録し、pre-orientation exposureは別のprotocol observationとして扱う停止線を追加した。schema fieldの追加はまだ行わず、まず複数caseで必要性を確かめる。

自然な日本語として全文を再読し、Product Value、Evaluation、Stable Requirement、Universal Contract、およびEvidence高さの境界が曖昧になっていないことを最終監査済みである。