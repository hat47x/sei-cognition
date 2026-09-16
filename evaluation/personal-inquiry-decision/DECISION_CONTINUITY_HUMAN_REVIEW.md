# Decision Continuity — H2 Human Review Execution

更新日: 2026-09-16  
状態: **Evaluation-only / Human Review Execution Guide / Not Product Requirement**  
関連: ISSUE-000073 / `decision_continuity_counterfactual_matched_set_v1.json` / `matched_review_session.py` / `decision_continuity_review_analysis.py`

## 1. この文書の役割

ISSUE-000073のH2では、同等の判断素材について、raw chat、chronological note、SEI Resume Projectionから再開したときの差をhuman reviewで観測する。

fixture、rotation、blinded packet、Decision-specific semantic preflightは既に存在する。本手順では、それらを実際のhuman reviewへ接続する際に、**後から知った情報を先に見せないこと**と、**synthetic reviewをH1やProduct Valueへ過大解釈しないこと**を固定する。

```text
matched synthetic human review
  = H2 pilotの観測手段

matched synthetic human review
  != H1 actual resume usability
  != actual capture burden
  != Product Value established
```

## 2. 責務分離

実行系を一つに寄せる。

```text
decision_continuity_counterfactual_*.json
  = 判断素材、Surface、reference state

decision_continuity_counterfactual_matched_set_v1.json
  = rotation、比較条件、解釈停止線

inquiry_continuity_packet.py
  = blinded packet生成

decision_continuity_preflight.py
  = Decision時点のbasis / Recommendation / unresolved /
    post-decision境界のsemantic consistency

matched_review_session.py
  = source snapshot固定、global stage gate、response固定

decision_continuity_review_analysis.py
  = Decision固有のresponse形式、audit finding、
    operator observation、非採点comparison
```

Decision Continuity専用のsession managerは作らない。Inquiry Continuityと共有できるstage gateは共有し、意味監査だけをDecision側へ残す。

## 3. なぜglobal stage gateにするか

一つのfixtureで`phase1 → post → audit`を終えてから次のfixtureへ移ると、最初のcaseで「後発Evidenceを見る観点」や「auditで何を正解とするか」を学習し、その知識が次のcaseへ持ち込まれる。

そのため、一つのrotationでは次の順序にする。

```text
3 caseすべてのphase1を回答・固定
  ↓
3 caseすべてのpostを回答・固定
  ↓
3 caseすべてのauditを回答・固定
  ↓
complete
```

`matched_review_session.py`はこの順序を強制し、session開始時のmanifest / fixture SHA-256も固定する。途中で評価素材が変更された場合は同じsessionを継続しない。

## 4. session開始

例:

```bash
python evaluation/personal-inquiry-decision/matched_review_session.py init \
  /tmp/e73-r1-session.json \
  --manifest evaluation/personal-inquiry-decision/decision_continuity_counterfactual_matched_set_v1.json \
  --repo-root . \
  --rotation R1 \
  --session-id e73-r1-reader-001 \
  --created-at '2026-09-16T12:00:00+09:00'
```

現在提示してよいpacketだけを確認する。

```bash
python evaluation/personal-inquiry-decision/matched_review_session.py packets \
  /tmp/e73-r1-session.json \
  --manifest evaluation/personal-inquiry-decision/decision_continuity_counterfactual_matched_set_v1.json \
  --repo-root .
```

初期状態では3件とも`phase1`だけが返る。`post_decision_evidence`や`reference_state`は返らない。

## 5. phase1 response

各caseの質問へ回答し、同じresponse JSONにorientation時の観測を残す。

```json
{
  "answers": [
    "回答1",
    "回答2",
    "回答3",
    "回答4",
    "回答5"
  ],
  "operator_observation": {
    "time_to_orientation_seconds": 18.4,
    "source_reopen_count": 0,
    "mental_effort_1_to_5": 2
  }
}
```

判断できない観測値は推測せず`not-observed`を使う。

記録例:

```bash
python evaluation/personal-inquiry-decision/matched_review_session.py record \
  /tmp/e73-r1-session.json \
  --fixture-id e73-decision-continuity-001-provider-pilot \
  --stage phase1 \
  --recorded-at '2026-09-16T12:05:00+09:00' \
  --response /tmp/e73-f1-phase1.json
```

3caseすべてのphase1を固定するまでpost packetは開かない。

## 6. post response

global gateが`post`へ進んだ後、各caseの`post_decision_evidence`だけを追加で読み、質問へ回答する。

```json
{
  "answers": [
    "回答1",
    "回答2",
    "回答3",
    "回答4"
  ]
}
```

この時点でも`reference_state`は開かない。

## 7. audit response

3caseすべてのpost回答が固定された後にだけreference stateを開く。

auditは自由な「良かった／悪かった」ではなく、Decision Continuityで問題になる誤りを分解して記録する。

```json
{
  "findings": {
    "current_question_correct": "pass",
    "decision_correct": "pass",
    "recommendation_decision_integrity": "pass",
    "historical_basis_integrity": "pass",
    "unresolved_preservation": "pass",
    "post_decision_temporal_integrity": "pass"
  },
  "operator_observation": {
    "historical_misattribution_count": 0,
    "recommendation_decision_confusion": false,
    "correction_burden": "low"
  },
  "continued_use": "not-observed",
  "continued_use_reason": "",
  "notes": ""
}
```

findingは`pass | fail | not-observed`、correction burdenは`low | medium | high | not-observed`とする。

H2用のprepared Surfaceを読んだだけでは、actual workで「継続利用したいか」を十分に判断できない場合がある。その場合は`continued_use = not-observed`のままにする。

## 8. Decision固有validation

sessionを保存しただけでは、response内容がDecision Continuityの評価形式に沿っているとは限らない。

```bash
python evaluation/personal-inquiry-decision/decision_continuity_review_analysis.py \
  --manifest evaluation/personal-inquiry-decision/decision_continuity_counterfactual_matched_set_v1.json \
  --repo-root . \
  validate-session /tmp/e73-r1-session.json \
  --require-complete
```

このvalidationでは、共通session gateに加えて次を確認する。

- phase1 / postの質問数と回答数が一致する。
- orientation時間、source reopen、mental effortが所定の型に収まる。
- Recommendation / Decision混同を独立findingとして記録する。
- historical basis integrityを独立findingとして記録する。
- post-decision temporal integrityを独立findingとして記録する。
- 判断不能値を`not-observed`として保持できる。

## 9. counterbalanced comparison

R1だけでもH2 pilotの一観測にはなるが、conditionとscenarioがまだ交絡する。

R1 / R2 / R3を別readerまたは独立review sessionで実施できた場合、各fixture × conditionの9組が埋まり、counterbalance coverageを確認できる。

```bash
python evaluation/personal-inquiry-decision/decision_continuity_review_analysis.py \
  --manifest evaluation/personal-inquiry-decision/decision_continuity_counterfactual_matched_set_v1.json \
  --repo-root . \
  compare \
  /tmp/e73-r1-session.json \
  /tmp/e73-r2-session.json \
  /tmp/e73-r3-session.json
```

出力はraw observationをcondition別にまとめるだけで、overall scoreやwinnerを作らない。

比較対象には次を残す。

- semantic findingごとの`pass / fail / not-observed`
- time-to-orientationのraw値
- source reopen
- mental effort
- historical misattribution
- Recommendation / Decision confusion
- correction burden
- continued-use intent
- fixture × condition coverage

## 10. Evidence境界

一つのhuman readerが一rotationを完了した場合、少なくとも「H2 pilotのhuman observationが一件存在する」と読める。ただし、tool自身はresponseが本当にhumanによるものかを認証しない。operator provenanceは別途必要である。

また、次の飛躍をしない。

```text
H2 synthetic pilot
  != H1 actual resume usability

R1/R2/R3 counterbalance complete
  != generalizable user evidence

prepared Surfaceのreview
  != first useful saveまでのcapture burden

faster orientation
  + historical accuracy failure
  != Product Value improvement
```

chronological noteがSEIと同等以上なら、それをSEI固有構造を減らすEvidenceとして扱う。SEIに有利な結果だけを成功条件にしない。

## 11. H1への接続

ISSUE-000073のResolutionにはH1が別途必要である。

H1ではactual prototypeを人間が使い、chat historyや内部schemaの知識なしで、実際の判断仕事へ戻れるかを観測する。synthetic fixtureの内容を読んで正答できたことでは代替しない。

H2 toolingが整った後も、H1、actual capture/review overhead、Candidate Requirement auditが未観測ならIssueをResolved扱いしない。
