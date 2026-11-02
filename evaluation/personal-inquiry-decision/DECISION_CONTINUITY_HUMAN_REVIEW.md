# Decision Continuity — H1 / H2 Human Review Execution

更新日: 2026-11-02  
状態: **Evaluation-only / Human Review Ready / H1・H2 Not Yet Observed / Not Product Requirement**  
関連: ISSUE-000073 / `DOGFOOD_SURFACE.md` / `DOGFOOD_EVALUATION_RECORDING.md` / `decision_continuity_counterfactual_matched_set_v1.json` / `inquiry_continuity_review_runner.py` / `matched_review_session.py` / `decision_continuity_review_analysis.py`

## 1. この文書の役割

ISSUE-000073のhuman reviewは、性質の異なる二つの観測を分けて扱う。

- **H1 — actual resume usability**: actual prototypeとreal Inquiryを使い、時間が空いた後に人間が実際の判断仕事へ戻れるかを見る。
- **H2 — counterfactual Decision Continuity review**: 同等の判断素材について、raw chat、chronological note、SEI Resume Projectionから再開したときの差をsynthetic human reviewで比較する。

H1とH2は相互に代用しない。H1ではreal Inquiryとactual capture burdenを観測し、H2では比較条件を統制してhistorical integrityとorientation負担の差を見やすくする。

```text
H1 actual resumption
  != H2 matched synthetic review

H2 matched synthetic review
  != H1 actual resume usability
  != actual capture burden
  != Product Value established
```

H2についてはfixture、rotation、blinded packet、Decision-specific semantic preflightが既に存在する。本手順では、それらを実際のhuman reviewへ接続する際に、**後から知った情報を先に見せないこと**と、**synthetic reviewをH1やProduct Valueへ過大解釈しないこと**を固定する。

H1については新しいsession managerや保存schemaを作らない。既存のPersonal Inquiry Continuity dogfood surfaceとevaluation sidecarを再利用し、actual resumptionに必要な手順だけを本書後半で固定する。

### 1.1 2026-10-10の実行ゲート

E1〜E8は2026-10-09にgo1.25.14でactual PASSし、2026-10-10にはtested commitからcurrent developまでの実行対象source closure 39 fileが全て同じGit blobであることを確認した。したがって、H1 / H2を始めるためのmachine prerequisiteは満たしている。

```text
E1〜E8 Scoped Executable Evidence available
  + current source closure unchanged
  → H1 / H2 human reviewへ進める

machine prerequisite satisfied
  != H1 / H2 observed
  != Product Value established
```

H1 / H2を始めるためにE1〜E8を毎回再実行しない。`interactionprobe`、`semanticruntime`、Go依存定義、またはrunnerの意味が変わった場合に再実行する。H2 native clean-HEAD captureやexternal Git-bundle actual runは再現性を高める補助Evidenceであり、human review開始の前提にはしない。


### 1.2 2026-10-21のH2比較素材同等性補正

H2 human reviewの開始前に、matched setの3条件で判断に必要な意味情報が揃っているかをoperator側で照合した。ケース②では請求関連のlow-confidence事例が複数あった事実の明示性、ケース③ではsource external IDの今後の安定性というUnknownと、Decisionのdry-run候補抽出方法の記述に差があった。元の`scenario.phase_1`と`reference_state`は変えず、条件ごとの`surface_text`だけを補正した。

- ケース①：変更なし。既存のTEI Stage 0 Reference向け固定sourceと独立に保持する。
- ケース②：Git blob `54e1e244cba4f4859e661b3590a5d3f25adb0cb0` → `d326ef24d1a954c565c9867040990952137aaa5a`。
- ケース③：Git blob `9d72729d8425ae0f68b7569107c281b4f3e479b8` → `1e6810b1f014dd571a1eab3250a769697b538296`。

変更後のoperator-side静的照合は36項目すべて一致した。ただし、これは既存Python regressionの実行結果ではない。2026-09-18のH2 Decision review runner regression 8/8 PASSは**旧fixture blobを入力として得たhistorical Evidence**であり、新しいblobへPASSを転用しない。現在のH2 fixtureを固定したうえで既存preflight / runner回帰試験を再実行することが、次の技術的確認である。新しいGateやschemaは追加しない。

この修正と静的照合は、評価者のpre-stimulus provenance、blinding、H1 actual resumption、H2 human observation、capture / review overhead、Product Valueの成立を意味しない。過去にR1相当materialへ露出したreaderも引き続き`known-material-exposure`として扱う。E1〜E8のGo実行対象source closureとは別の変更であり、E1〜E8の既存PASS自体は変更しない。


### 1.3 2026-10-25のH2回帰試験capture拡張

比較素材②・③の補正後、既存の`tools/capture_issue_000073_h2_runner_selftest.py`を拡張し、従来のshared-runner 8テストに加えてpreflight 7テストとanalysis 5テストを同じ`unittest discover`実行に含めた。source bindingにも追加のテストファイル2件を含め、合計15ファイルのHEAD一致・clean checkout・独立指定expected HEADを検査する。既存capture scriptとEvidence schemaを再利用し、新しいsession・Human Evidence schemaやGateは追加しない。

実行順序は次のとおり。expected HEADは実行checkoutとは独立のGitHub等から取得したcanonical commit SHAを指定する。

```bash
python tools/test_capture_issue_000073_h2_runner_selftest.py
python tools/capture_issue_000073_h2_runner_selftest.py \
  --expected-head <independently-verified-commit-SHA> \
  --output /tmp/issue-000073-h2-decision-20-regressions.json
```

2026-10-25のGitHub source監査では、対象テストが7+8+5=20件、captureのsource bindingが15ファイルであること、修正済みfixture②・③が前回の固定blobと一致することを静的に確認した。**Pythonテストのactual実行結果は未取得**のため、20/20 PASSやsynthetic capture self-test PASSとは記録しない。過去の8/8 PASSは旧fixtureに紐づいたhistorical Executable Evidenceとしてそのまま保持する。

capture結果が得られても、H2 clean blinded human observation・H1 actual resumption・capture/review overhead・Product Valueは別途評価する。

## 2. H2の責務分離

H2の実行系を一つに寄せる。

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

Decision Continuity専用のsession managerは作らない。`inquiry_continuity_review_runner.py`を073/078で共有し、その下で`matched_review_session.py`のstage gateを利用する。Issueごとの差はresponse validationと意味監査に限定する。

## 3. H2でglobal stage gateを使う理由

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

## 4. H2 session開始

H2では、reviewerへ最初のstimulusを提示する前にprovenanceを固定する。正規入口は073/078で共有する`inquiry_continuity_review_runner.py`である。

```bash
RUNNER=evaluation/personal-inquiry-decision/inquiry_continuity_review_runner.py
MANIFEST=evaluation/personal-inquiry-decision/decision_continuity_counterfactual_matched_set_v1.json

python "$RUNNER" --manifest "$MANIFEST" --repo-root . init \
  /tmp/e73-r1-session.json \
  --rotation R1 \
  --session-id e73-r1-reader-001 \
  --created-at '2026-09-18T13:30:00+09:00' \
  --reviewer-id reviewer-opaque-001 \
  --prior-exposure none-declared \
  --response-authorship human-direct
```

`reviewer-id`は個人名・メールアドレス・account idではなく、evaluation内だけで用いるopaque idとする。`prior-exposure`は次から選ぶ。

- `none-declared` — 割当fixtureのmaterialをstimulus提示前に見ていないとreviewerが申告する。
- `known-material-exposure` — 割当case、同caseの別Surface、reference material等を既に見ている。
- `unknown` — exposureの有無を確定できない。

これらは申告metadataであり、盲検やhuman authorshipを独立に証明するものではない。既知または不明のexposureがあるsessionもpilot observationとして残せるが、clean blinded reviewとは呼ばない。

共有runnerの`init`は、provenanceを付けた初期sessionをexclusive-createで保存する。同じsession pathが既に存在する場合は上書きせず停止する。これにより、stimulus提示後に同じpathへ`init`し直してpre-stimulus provenanceを置き換える事故経路を閉じる。以後の`record`は固定済みsessionを前進させるため同じpathを更新するが、runner自身はreview provenanceを差し替えない。

```text
exclusive-create at review init
  = accidental/post-hoc re-initを拒否

exclusive-create
  != reviewer identityの独立証明
  != actual blindnessの独立証明
  != manual file tamperingを暗号学的に排除
```

provenance付きsessionについては、低レベルの`matched_review_session.py` CLIから`packets`または`record`を直接実行しない。低レベルCLI側もこの迂回を拒否する。human reviewでは必ず共有runnerの`bundle` / `record`を使い、Issue固有response validationとreview provenance確認をstage gateの前提にする。`matched_review_session.py`は共有内部基盤であり、provenance付きhuman reviewのoperational entry pointではない。

現在提示してよいpacketだけを確認する。

```bash
python "$RUNNER" --manifest "$MANIFEST" --repo-root . bundle \
  /tmp/e73-r1-session.json
```

初期状態では3件とも`phase1`だけが返り、condition label、`post_decision_evidence`、`reference_state`はreviewer bundleへ出さない。

### 4.1 2026-09-18のpre-stimulus provenance上の注意

本Issueの作業過程では、R1相当のphase1 materialをreviewer provenance固定前に一度提示したが、human responseは固定されなかった。この提示自体はH2 observationではない。

同じreaderが今後このmatched setをreviewする場合、その事前提示をなかったことにはせず、少なくとも`known-material-exposure`として記録する。clean blinded H2が必要なら、割当materialへ未露出の別readerを用いる。

```text
stimulus shown before provenance is fixed
  != human H2 observation

known prior material exposure
  != clean blinded review
```

## 5. H2 phase1 response

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

記録例は次のとおりです。

```bash
python "$RUNNER" --manifest "$MANIFEST" --repo-root . record \
  /tmp/e73-r1-session.json \
  --fixture-id e73-decision-continuity-001-provider-pilot \
  --stage phase1 \
  --recorded-at '2026-09-18T13:35:00+09:00' \
  --response /tmp/e73-f1-phase1.json
```

3caseすべてのphase1を固定するまでpost packetは開かない。

## 6. H2 post response

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

## 7. H2 audit response

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

## 8. H2 Decision固有validation

sessionを保存しただけでは、response内容がDecision Continuityの評価形式に沿っているとは限らない。

```bash
python "$RUNNER" --manifest "$MANIFEST" --repo-root . validate \
  /tmp/e73-r1-session.json \
  --require-complete

# Decision固有の独立validationを明示的に再確認したい場合
python evaluation/personal-inquiry-decision/decision_continuity_review_analysis.py \
  --manifest "$MANIFEST" --repo-root . \
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

## 9. H2 counterbalanced comparison

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

## 10. H2のEvidence境界

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

complete sessionは共有runnerからEvidence bundleへexportできる。

```bash
python "$RUNNER" --manifest "$MANIFEST" --repo-root . export-evidence \
  /tmp/e73-r1-session.json \
  --output /tmp/e73-r1-evidence.json
```

Evidence bundleではphase1 / postのhuman review observationと、reference state開示後のsemantic auditを別layerとして保持する。review provenanceも併記するが、そのmetadataだけをhuman authorshipやblindnessの独立証明にはしない。

## 11. H1 actual resume usability

H1ではsynthetic fixtureではなく、`DOGFOOD_SURFACE.md`で扱う**real Inquiryのactual prototype state**を人間が再開する。

目的は、Orientation Projectionに必要な意味が表示されることを再確認することではない。時間が空き、元chatや作業中のmental contextが失われた状態で、内部schemaを読み直さずに次へ戻れるかを観測する。

- 何を考えていたか。
- 何をDecisionしたか。Decisionがなければ、その不在を正しく認識できるか。
- Decisionがある場合、なぜそうDecisionしたか。
- 何がまだ分からないか、またはConflictとして残っているか。
- Decisionまたは前回review以後に何が変わったか。
- 次に何を確認・再検討すべきか。

H1のために新しいProduct field、review schema、session managerを作らない。actual Inquiry stateは`dogfood_core.py` / `dogfood_cli.py`、評価観測は`dogfood_evaluation.py` / `dogfood_evaluation_cli.py`へ置く。

```text
actual Inquiry state
  != evaluation observation

human H1 answer
  != canonical semantic fact
```

### 11.1 H1として数えてよい条件

H1を`resumption`として扱う前に、少なくとも次を確認する。

1. synthetic fixtureではなくreal Inquiryである。
2. Inquiry作業を中断してからcontext gapがある。
3. 再開直前に元chat、source、canonical stateの詳細、評価設計の説明等へmaterialな再露出をしていない。
4. 再開前にreference answerやaudit結果を見ていない。
5. Orientationを見る前の状態を、後から都合よく再構成しない。

暦上multi-dayでも、直前にcurrent concernやUnknown / Decision basisを思い出せる説明へ再露出した場合はclean H1として数えない。その場合はprotocol observationとして残し、actual `resume_observation`を架空に追加しない。

```text
calendar gap
  != cognitive gap

pre-orientation material exposure
  != H1 resumption observation
```

### 11.1.1 H1 pre-stimulus provenance gate

H1でも、Orientationを最初に提示する前にreviewer自身の直前露出を固定する。新しいmachine-readable schemaは追加せず、local-only review memoの先頭へ次のいずれかを記録する。

```text
none-declared
  = 最後の既知のmaterial exposure以後、
    元chat / source / Inquiry state / 評価説明を
    current stateを思い出せる程度には見返していない

known-material-exposure
  = 上記のいずれかへmaterialに再露出した

unknown
  = 再露出の有無を確定できない
```

`none-declared`は自己申告であり、独立したblindness証明ではない。`known-material-exposure`または`unknown`でもpilotとしてOrientationを試すことはできるが、clean H1 resumptionには数えない。

重要なのは、**この申告を固定する前にOrientationやInquiry内容を提示しないこと**である。operatorが刺激内容を先に説明した場合、その回はclean H1候補から外す。

### 11.2 H1実行順序

H1は次の順序で実施する。

1. 元chat、元source、Inquiry JSON本文、Orientationを開く前に、pre-stimulus provenanceをlocal memoへ固定する。
2. clean候補として進める場合は`none-declared`であることを確認し、開始時刻を記録する。
3. `dogfood_cli.py orient`だけを実行し、Orientationを読む。
4. 上の6問へ回答し、回答を一度固定する。
5. 「次の作業を始められる」と判断した時点とFirst Useful Actionを記録する。
6. 必要になった場合だけdetail、元source、元chatへ降り、その回数を数える。
7. 回答を固定した後にcanonical state / sourceへ戻り、historical misattribution、Recommendation / Decision混同、Unknown / Conflictの欠落、post-decision情報の遡及混入がなかったかをauditする。
8. clean条件を満たした場合だけ`dogfood_evaluation_cli.py resume-add`でactual observationをsidecarへ記録する。known / unknown exposureのpilotはsidecarの`resumption`へ自動昇格させない。

Orientationの例:

```bash
cd evaluation/personal-inquiry-decision
python dogfood_cli.py orient /path/to/inquiry.json
```

H1回答はlocal-onlyのreview memoでよい。現時点ではmachine-readableな新schemaを設けない。最低限、pre-stimulus provenance、6問への回答、開始時刻、first useful action到達時刻または経過を残す。

### 11.3 H1 observationの記録

H1がclean resumption条件を満たした場合、既存sidecarへ`evidence_role=resumption`として記録する。

```bash
python dogfood_evaluation_cli.py resume-add /path/to/evaluation.json \
  --id resume-h1-001 \
  --observed-at '2026-09-24T10:00:00+09:00' \
  --surface sei-orientation \
  --evidence-role resumption \
  --context-gap multi-day \
  --source-reopens 1 \
  --chat-reopens 0 \
  --detail-descents 2 \
  --original-concern-retention pass \
  --unresolved-preservation pass \
  --temporal-integrity pass \
  --recommendation-decision-integrity pass \
  --attention-load low \
  --first-useful-action '次に確認すべき条件を一つ調べる'
```

`context-gap`はactual条件に合わせる。判断できない項目は推測せず`not-observed`または`not-applicable`を用いる。

H1の回答が速くても、historical basisを誤認した場合は成功へ丸めない。

```text
fast orientation
  + historical misattribution
  = H1 failure observation
```

### 11.4 capture / review overheadとの接続

ISSUE-000073のResolutionではresume時の使いやすさだけでなく、capture / review overheadも必要である。

そのため、H1対象Inquiryについて作業中の負担を観測できる場合は、既存sidecarの`capture-add`を使う。

```bash
python dogfood_evaluation_cli.py capture-add /path/to/evaluation.json \
  --id capture-001 \
  --observed-at '2026-09-20T20:00:00+09:00' \
  --semantic-corrections 1 \
  --burden low \
  --notes 'Unknownの意味種別を一度だけ修正した'
```

resume後に記憶だけでcapture burdenを精密に捏造しない。未観測なら`not-observed`のまま残し、次のreal Inquiryで前向きに観測する。

## 12. H1とH2を合わせたEvidenceの読み方

H1とH2は、同じDecision Continuity仮説を異なる角度から反証する。

```text
H1
  = real Inquiry
  + actual prototype
  + actual capture / resumption context

H2
  = matched material
  + controlled Surface comparison
  + historical-integrity audit
```

H1が良くH2でSEIの比較差が弱い場合、単純baselineでも十分な可能性を残す。H2で差が出てもH1のcapture burdenが高い場合、Product Value成立とは扱わない。

一つのH1と一つのH2 pilotが存在しても、広いAdoption / Outcome Evidenceには昇格しない。

```text
H1 observed
  + H2 pilot observed
  != generalizable user evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
  != ISSUE-000073 automatically Resolved
```

ISSUE-000073のResolution判断では、E1〜E8のScoped Executable Evidence、H1 actual resume usability、H2 counterfactual review、capture / review overheadを別々に確認し、そのうえでCandidate RequirementとDecision Continuity Product hypothesisを再評価する。

2026-10-10時点ではE1〜E8のScoped Executable Evidenceは成立済みである。したがって未観測の中心はH1、H2、capture / review overheadである。human reviewでは、SEIに有利な結果を作ることではなく、単純baselineとの差が弱い場合やoverheadが大きい場合もそのまま記録する。


### 12.1 2026-11-02追補：H2素材比較と現行製品の価値実証を分ける

**評価手順の追加注意（Evaluation-only／新schemaなし／human review NOT YET OBSERVED）。** 本節はISSUE-000073のRC-01〜06と、SEI #677/#660/#767の用途相対の確認をH1/H2へ接続するoperator用手順であり、未露出readerへ見せるstimulusや既存matched fixtureを変更しない。

**H2 operatorの事前監査（盲検readerへの提示前）。**

1. 3ケースごとにA raw chat・B chronological note・C SEI Resumeを並べ、Recommendation、Decision、historical basis、unresolved、post-decision evidence、確定度、数量、対象、時点の意味対応を記録する。既知の②/③の補正・36項目静的照合を保持し、その結果を新しい全面的意味保証へ広げない。
2. Cの`surface_text`は**人手で準備した比較用Surface**であり、現行`BuildResume()`／CLI／MCPの実出力ではない。実製品から参照・意味説明へ到達できるか、必要な原record再読取り回数・手作業の補足量を**operatorだけの別票**へ記載する。`C fixture`の認知的効果と`actual SEI product`の効果を分ける。
3. 既存R1/R2/R3、pre-stimulus provenance、全caseのphase1→post→audit固定順序を維持する。比較に先立ち未割当Surface、reference state、製品出力差のoperator分析をreaderへ見せない。既知の素材露出を新しいclean blinded observationへ塗り替えない。
4. `comparison_projection`の9/9 coverageは組合せ網羅であって、人間作成・回答の正しさ・評価者独立性を保証しない。responseの文字列形式と`findings=pass`の入力だけで正答とせず、operatorが独立参照資料との照合実施有無、評価者ID重複、事前露出、合成responseの有無を記録する。参照元は固定したsource snapshotと必要な原位置で示す。
5. 試験実行記録は`7/8/5`のスイートごとの発見・skip・結果と期待テストIDを分ける。終了コード0や合計20件だけで「全件成功」を主張しない。現在のcaptureは件数・IDを検証せず、前提失敗時の`--replace`で旧Evidence喪失の可能性もあるため、技術修正の完了前に新しいPASSを記載しない。これは**H2の人間評価を始める新しい前提条件ではない**。

**H1の直前露出ゲートと回答固定を優先する。** H1の既存6問への回答が固定されるまでは、Operatorが原資料変更・ExactBinding・Gate・現在権限の違いを教えて正答を誘導しない。回答確定後、必要がある場合にだけ次の追補をread-onlyで観測する。過去のDecisionは歴史的記録として保持し、現時点で利用できるか／誰が実行できるかを別に評価する。

| 観測欄（local-only memo） | 問い・記録方法 |
| --- | --- |
| Historical accuracy | 当時のDecision、Recommendation、根拠、未決、後から到着した情報を取り違えなかったか。誤認は具体例とともに記録 |
| Source/meaning applicability | 現在のSource、scope、Rule、外部条件と何が変化したか。確認範囲と、意味対応が未確認の候補を区別 |
| Coverage and disclosure | 回収できた原記録の範囲、本文中の候補、開示不能・未確認を区別。機密ID・件数・非開示原文を外部Harnessの評価票へ転記しない |
| Action boundary | 旧Decision／Gate allowが現時点のAuthority・Commit成功・Business Outcomeを意味すると誤認しなかったか。実操作を実行したという記録は作らない |
| Next useful action | 利用者が何を次に確認／比較／調査するか。最初の有用な一手への時間とsource reopen、修正負担を観測 |
| Capture/review tax | 実際に記録した準備・補正・確認の負担のみ数える。再開後の想像で過去の作業負担を補完しない |

**解釈停止線。** H2素材での正確な回答、9/9の組合せ、現行実装の原record読出し成功、Tool/Teamの実行成功、複数AIの同意、早いorientationは、それぞれ実製品での省力化・根拠の独立性・Owner受理・実権限・Product Valueを証明しない。判断を再開して新しい資料を読むことはできても、現在の業務操作に進めるかは対象OwnerとHost／Providerの検証が必要。単純ノートに価値差がない場合、その結果をそのまま記録する。

**研究・実装の追跡先。** Source/ExactBinding投影はSEI #697、資料の解決は#710、Lineageは#687、現在文脈は#660、組織的再開は#677、Cognitive Methodの外延・意味残差・開示・現在性と次の証拠選択は#767が所有する。本書はH1/H2の人間評価を担当し、それらのAPI・意味規則を重複実装する計画ではない。


### 12.2 後続研究への接続：問いを見失わず、次の証拠を選べるか

**追加operator票／2026-11-02（H1/H2の固定stimulus・本体session・採否条件は変更しない）。** SEI #767のP5/P6およびDraft PR #770の公開合成Referenceから、既存のH1「何を見直すべきか」という設問の理解を深める。**既存のH1回答が固定されるまで、本節にある正解候補や識別的Probeをreaderへ提示しない。** H2の3ケース×3条件を新しい研究Corpusへ混ぜず、事前露出による比較汚染を避ける。

**既存回答固定後にoperatorが記録する六つの確認欄。**

| 欄 | operatorが観測・照合すること |
| --- | --- |
| 問いQ | 利用者が答えようとしたClaimは「当時の判断」「現在の適合」「区間中の変更なし」「全件成立」「Action完了」などのどれか。対象・時点・範囲・用途を残す |
| 観測Oと被覆 | 回収したSource・snapshot・scope・資料の位置・取得範囲・観測不能。局所検査成功を対象Lの全件検査と解釈したか |
| 残る仮説 | 観測は同じだがQが異なる公開合成二世界を示せるか。過去のQに答えられても現在のQに不足があるか |
| 識別的な次の確認 | 何を追加で見ると仮説が分かれる可能性があるか。独立Source、区間履歴、実Source入力、Owner専門確認などの候補と理由 |
| 実施可能性／開示 | 提案・実Tool・現在許可・実行・取得結果・開示可能性を別にし、内部の秘匿差の存在自体も外部へ漏らさない |
| 認知的負担と成果 | 次の有用な確認に到達できたか、再閲覧回数、実際の修正負担、不要な質問、追加時間。Product利用前の作業を事後推定で埋めない |

**判別的な二問の例（operator/別合成ケース用）。** `現在、対象集合は同じか`はt2のSnapshotで答えられる場合がある。一方、`前回レビュー後に対象集合が一度も変わらなかったか`はt1で加入・離脱した履歴の有無に左右され、同じt2 Snapshotからは判別できない。W1〜W4でQを区別できたProbeも公開追加世界W5では十分でない（SEI #770の**最初の合成6件に追加7件を加えた13/13 PASS（別Draft）**）。この差は新しいH1/H2の合格実測ではなく、追加確認を選ぶための研究入力である。

**将来の外部Harness比較の扱い。** `yi-sei-inquiry`はSEI #769のProposed Skill。Skill説明・Tool呼出し・Message受信・Agent多数決を、実Source独立性、正しいClaim、公開資格、人の意味受理と区別する。既存Method v1alpha1のDefinition/Realization/Applicationとinput/output/residual参照を利用した引継ぎ可能性を評価し、新しいRunner・Truth Storeを前提としない。Skillあり／なしの比較は既存のH1/H2で値を作らず別評価票に残す。

**比較の停止線。** 同一の可視情報から異なるQが成立する場合、外部Consumerがその差を識別できたと推測しない。適切な次の根拠を提案できたかと、許可のあるProductが実際に取得・検証できたかは別。H1/H2のHuman Product Value、実Provider・権限・実操作は依然として未観測。


### 12.3 追加operator票：限定的な回答の有用性と、混合した根拠の危険を区別する

**2026-11-02／H1/H2の開始条件・stimulus・評価schemaは変更しない。** [SEI #767](https://github.com/hat47x/sei-cognition/issues/767)と[Draft PR #770](https://github.com/hat47x/sei-cognition/pull/770)に追加された「一つの観測セルでの限定判断」と「異なるRead世代を組み合わせた誤保証」を、H1回答固定後のoperator分析または独立した公開合成研究へ接続する。**#770の13/13 PASSは別Draftの純粋合成結果であり、H1/H2の実証件数ではない。**

**優先する問いは、完了した調査の数ではなく、利用者が何について判断できる状態になったかである。** 調査の対象・範囲・時点・用いたSourceを特定した上で、次の判定を区別する。

| 結果の例（研究上のラベル） | 利用者の継続に関するoperator確認 |
| --- | --- |
| `true-in-fixture` / `false-in-fixture` | 固定された合成世界内の**特定観測セル**に対する限定判断。実データと現行の用途へ一般化していないか |
| `unknown-in-fixture` | 同じ観測で結論が違う世界が残る。どの追加の証拠・Sourceへ進むと区別し得るか |
| `unmodeled-observation` | 固定した世界集合に当てはまらない。不存在・否定と扱わず、対象仮説の見直しへ進めるか |
| **単独Claimのみ成立** | 取得済みで必要依存を満たす範囲の調査を継続し、別Sourceが必要な結合Claimだけを保留できるか |
| **混合epoch／Source revision** | 個々のRead成功を全体のClaimへ誤結合していないか。共通版／有効なbridgeと実ConsumedBytesを確認したか |
| **内部では判断可能、外部開示は不可** | Claimの内部判定、外部への結果開示、説明の詳細度を独立に扱い、秘密の有無・件数・Probe名・理由を漏らさないか |

**読取りの合成反例（回答固定後または別合成ケースに限定）。** `t0:A=1,B=0`、`t1:A=0,B=1`なら、どちらの時点でも「AとBがともに正値」は偽である。A@t0とB@t1を混ぜると両方1に見える。Operatorは「Source AとBを正しく読めたか」と「共同で一つのClaimを支持するように読めたか」を別々に記録する。**同じepochラベルでも実Sourceの整合は未証明**であり、正当な世代間bridgeを持つ場合はTEI #2516等の責務で確認する。

**定量評価は分ける。** 正答／根拠の適用範囲、部分的に先へ進めた作業、誤った断定・参照混合、独立Source再取得、人への確認回数、最初の有用な次の行動までの時間を別項目で保持する。限定判断を適切に利用できたことと、後で新しい世界・変更履歴が出た際に旧判断を訂正できたことも別に観測する。取得不能や非開示を理由に、許されたread-only調査まで一律停止したかも記録する。

**Evidenceの停止線。** ここで用いる説明ラベルと対照例はoperator側の研究資料であり、現在のSEI Productが同名API・判定型を提供することを意味しない。H2のA/B/Cの公平な情報比較やblinding、H1の最初の6問の回答固定を変更しない。実Provider/Tool、公開資格、Owner業務意味、Human Product Valueの成立は別途検証する。


### 12.4 外部へ提示する調査計画の開示監査（H1回答固定後のみ）

**既存Protocolを維持する追加operator票。** H1の初回6問とH2の3条件×3ケースを変更せず、回答固定後の横断分析でだけ、SEI #767／Draft #770の調査候補自体の漏洩反例を利用する。最終回答を秘匿しても外部へ出たTool候補・Probe名・Args・呼出し順・Error/Status/Traceが秘密Actionの存在で異なり得る。**内部Productの意味判断・外部公開の可否・外部へ提示したPlanning Projectionを別に観測**する。

| 観測欄（operator-only） | 確認する範囲と停止線 |
| --- | --- |
| 必要な依存 | 問いQに本当に必要なSource/Rule/Field/Scope/時点。非表示Rule依存の有無と、必要集合が未確定な範囲 |
| 実際の取得 | 宣言されたMappingと実Provider/Toolが読んだデータの別。実Witnessが無い場合は`physical-read-unverified` |
| 公開された計画 | 実際に外部へ可視化されたProbe候補、Tool/Action名・件数、順序・Args・Error/Status・診断。最終回答だけで済ませない |
| 同一公開条件の二世界 | 公開View・公開Tool一覧・目的・許可が同じで秘密Actionのみ異なるとき、公開Plan/Tool診断に秘密依存の差がないか。正当に公開許可された差は除外 |
| 実効と認知負担 | 提案が実Toolとして存在したか、権限・実行・結果を確認できたか。余分な質問/再取得、隠れた漏洩、未解決の継続を別指標で記録 |

**Evidence資格。** Draft #770は最初の2 Moduleで13/13 PASS、その後の第三Moduleは**単独7/7 PASS**、3 Module一括は未実施。いずれも公開合成テストであり、実Provider／OS／Network／Tool List／Timing／反復照会／秘密情報の開示保証やH1/H2 human observationとは別。実行・開示ポリシーはTEI #2507/#2515、TAI #232が所有し、SEIは利用者にとって必要な次のInquiryと、その開示可能な説明を検討する。


### 12.4 調査計画・Tool候補を含むConsumer開示の追加評価

**2026-11-02／operator側・H1/H2の回答固定後または独立合成票に限定。** SEI #767 P6とDraft #770のPlanner-visible leakage、TEI #2516 J-08〜11の必要根拠／実Read／公開観測を既存H1の「次の確認」へ接続する。盲検readerに内部Tool一覧・秘密のAction・対照世界の存在を先に示さない。実資料の秘密は試験用fixtureへ転記しない。

| 観測欄 | 質問・記録内容 |
| --- | --- |
| 必要根拠 | 今の問いQが要求するSource・Rule・対象のScope／時点と、未列挙の依存があるか。表示済み値だけから必要入力を閉じたか |
| 実際の取得 | 候補Tool説明や宣言Queryと、実ProviderのRead/Cache/Source版/取得範囲を区別。実取得の独立証拠がなければ未確認 |
| 表示された計画 | Consumerが観測した候補Question、Tool/Action名、候補数、実行順、理由、Error、Trace。公開回答本文が同一でもここに差があるか |
| 公開資格 | 公開してよい結果に加え、Probeの存在・件数・失敗理由を含む計画を開示できるか。判定条件は権限あるProductに委譲 |
| 再開時の負担 | 部分的に前進できた作業、追加調査、Tool/Source再取得、修正作業、漏出や過大な断定の有無を別々に測定 |

**合成二世界の負例（operatorのみ）**：外部可視Vと許可Tool集合が同じで、内部世界S1にだけ非公開Actionが存在する。最終返答が双方`not-confirmable`であっても、外部に出すTool候補がS1だけ多ければ存在を推測できる。この対照では最終返答と公開候補の両方を比べる。真のOS/Tool/Timing/反復照会・Networkにおける非干渉試験はTAI #232/TEI #2515の責務であり、現在の合成試験から成立と主張しない。

**証拠と継続条件**：別Draft #770は追加Planner合成7/7 PASS、既存13/13 PASSをそれぞれ報告。追加後の全20件を同一runでPASSしたという証拠ではない。本書のH1/H2実人間観測は未成立。H2のEvidence取得修正候補は[Draft #771](https://github.com/hat47x/sei-cognition/pull/771)へ分離し、Python actual executionが確認できるまでは完全PASSと扱わない。

## 13. Natural Japanese review

H2用に既に成立していたmatched review手順を維持しながら、073/078で同じreview runnerを共有する形へ整理した。H2ではreviewer provenanceを最初のstimulus提示前に固定し、その初期sessionをexclusive-createして同じpathへの再initを拒否する。provenance付きsessionを低レベルstage-gate CLIから直接提示・記録する迂回も拒否し、condition labelを伏せたbundle、Issue固有response validation、complete後のEvidence exportまでを同じ入口へ集約した。また、ISSUE-000073で未接続だったH1 actual resume usabilityを既存Personal Inquiry Continuity dogfood surfaceへ接続した。

H1のために新しい評価schemaやsession managerを増やさず、Inquiry stateは既存dogfood state、評価観測は既存sidecarを使う。これによりH1 / H2を別々の評価基盤として断片化させず、real Inquiryのresumptionとcontrolled counterfactual reviewだけを意味上分離した。

また、暦上のgapと認知的context lossを同一視せず、pre-orientationのmaterial exposureがあった回を架空のH1 Evidenceへ数えない停止線を明示した。速い再開をhistorical correctnessより優先せず、capture burdenが未観測なら後知恵で埋めない。

2026-09-18の作業過程でR1 phase1 materialがprovenance固定前に提示された事実についても、回答が固定されていないためH2 observationへは数えず、同じreaderの後続reviewではknown exposureとして扱う停止線を追加した。

自然な日本語として全文を再読し、H1 / H2、canonical Inquiry state / evaluation observation、synthetic pilot / actual resumption、reviewer provenance / human authorship、Executable / Adoption・Outcome Evidenceの境界が変わっていないことを最終監査した。

2026-10-10にはE1〜E8 actual PASSとcurrent source closure一致を前提状態へ反映し、H1 / H2を次の実行ゲートとして明示した。machine rerunをhuman reviewの前提にはせず、未露出readerを使うclean blinded H2と、known exposureを正直に残すpilot observationの区別は維持した。
