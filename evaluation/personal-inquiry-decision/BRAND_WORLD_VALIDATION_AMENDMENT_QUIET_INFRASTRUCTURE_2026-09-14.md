# Brand World Validation Amendment — Quiet Infrastructure

更新日: 2026-09-14  
状態: **Evaluation Protocol Amendment / Not Product Requirement**  
関連: `SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md` / `BRAND_WORLD_DISCOVERY_REBASELINE_2026-09-14.md` / `VALUE_VALIDATION_PROTOCOL.md`

## 1. この文書の役割

SEI Cognitionのブランド世界をProduct Value探索へ接続したとき、「静かな井」というイメージから、**利用者のattentionを常時奪わず、必要なときに深く認知資源へアクセスできること**がProduct品質として重要ではないかという問いが生まれた。

この問いは、色調やanimationを穏やかにするというVisual Designの話ではない。

高度なAIが多数のRecommendation、next question、relation candidate、warning、summaryを生成できるようになったとき、生成できるものをすべて前面へ出すことが、利用者のInquiryを本当に助けるとは限らない。

AIが提示した候補が多すぎることで、

- もともと何が気になっていたのかを見失う。
- 自分が観察したUnknownより、AIが作った問いへattentionが移る。
- Recommendationが「選ぶべき候補一覧」のように見え、Decision pressureが強まる。
- 重要なConflictが大量のsuggestionへ埋もれる。
- 再開時に必要なcueより、生成された情報の読解が主作業になる。

というfailureが起こる可能性がある。

一方、静かさを重視しすぎてmaterialなwarning、changed premise、reopen conditionまで見えにくくすれば、それも失敗である。

したがって本amendmentでは、Quiet Infrastructureを次のbalanceとして扱う。

> **SEIは、利用者のInquiryをAIの出力で埋めず、必要な認知差へ到達できる余白を保つ。同時に、見落とすと意味を誤る重要な変化や不確実性は適切に表面化させる。**

この文書は、existing `VALUE_VALIDATION_PROTOCOL.md`と`RESEARCH_DERIVED_VALIDATION_AMENDMENTS.md`を置き換えない。Brand World Discoveryから追加で得られた、attentionとproactive assistanceのtrade-offだけを補う。

## 2. 既存protocolで既に測れていること

既存Personal Inquiry Continuity系列は、Quiet Infrastructureに近い論点をすでに多く扱っている。

- M2 Recovery Effort — 再開に必要なsource / chat再読や時間。
- M6 Capture Burden — capture / correctionが本作業を邪魔しないか。
- M10 Correction Trust — AIの抽出・要約を利用者が訂正できるか。
- R1 Queryless Resume — queryを思い出さなくても再開できるか。
- R2 Generic Summary vs Orientation — 長いsummaryよりsemantic cueが価値を持つか。
- R10 Capture Friction — 実作業中の記録がattentionを奪わないか。
- O4 Cue Utility — 表示されたcueが有用か、単なるnoiseか。
- False Continuity — 速く戻れたように見えて意味を誤るfailure。

したがって、新しい大規模な評価frameworkは不要である。

不足しているのは、**AIが先回りして多数の候補を提示すること自体が、InquiryのorientationとAgencyに与える影響**を比較する観点である。

## 3. Product hypothesis

仮説は次である。

> Personal Inquiry Continuityにおいて、AI-generated suggestionを常時大量に前面表示するより、canonicalなInquiry stateと少数のmaterial cueを先に提示し、追加候補へ必要時に降りられるInteractionの方が、original concern、Unknown、historical stateを保ちながら次の有用な行動へ戻りやすい場合がある。

これは「proactive AIは悪い」という仮説ではない。

別の条件では、AIによるproactiveな指摘が、利用者が見落としていたConflictやchanged premiseを発見する重要な価値になり得る。

したがって比較したいのは、

```text
quiet = less AI
```

ではなく、

```text
quiet infrastructure
  = user inquiry remains primary
  + material semantic risk remains visible
  + optional AI assistance can be reached when useful
```

というbalanceである。

## 4. Test Q1 — Minimal Orientation vs Proactive Suggestion Surface

### Setup

同程度のInquiry snapshotを用い、再開Surfaceを二つ比較する。

### Condition A — Quiet / Minimal Orientation

最初に表示するのは、existing SEI Orientationから選んだ必要最小限のcueとする。

例:

- current inquiry / focus
- material Unknown / Conflict
- DecisionがあればDecisionとbasis
- materialなdelta
- Resume Anchor候補

AI-generated next question / relation / recommendation候補は、利用者が要求するか、追加支援へ降りたときに表示する。

### Condition B — Proactive Assistance

同じcanonical stateから、AIが生成した複数の候補を初期Surfaceへ追加する。

例:

- next questions
- related issues
- possible hypotheses
- recommendations
- suggested sources / actions

候補はprovisionalであり、canonical fact / Decisionへ自動昇格させない。

### Observe

- 利用者がoriginal concernを自分の言葉で再構成できるか。
- material Unknown / Conflictを取り落とさないか。
- AIが提案した論点を、元から自分が考えていた論点として誤帰属しないか。
- first useful actionへ到達するまでに読む情報量。
- suggestionを無視・修正・却下する負担。
- 利用者が「次に何をするか」を自分で選べる感覚を失わないか。
- proactive suggestionによって初めて発見できたmaterialな見落としがあるか。

### Failure signals

Condition Bで、

- original concernの再構成が悪化する。
- AI suggestionをhistorical contextへ誤帰属する。
- Unknown / Conflictの想起が落ちる。
- suggestionの読解・選別が本来のresume作業より重くなる。

場合、proactive surfaceがProduct Valueを下げている可能性がある。

逆にCondition Aでmaterialなchanged premiseや重大Conflictを見落とすなら、quiet surfaceが過度に情報を抑制している。

## 5. Test Q2 — Original Concern Drift

### Setup

Inquiry開始時に、利用者自身の短いconcern / question contextを外在化する。

中断後の再開時に、AI-generated next questionsを複数提示する条件と、提示しない条件を比較する。

### Observe

再開後に利用者へ、

1. もともと何が気になっていたか。
2. 現在その問いをどう捉えているか。
3. AIが新しく提案した問いは何か。

を分けて説明してもらう。

重要なのは、Inquiryが発展すること自体をdriftとみなさないことである。

良い発展では、

```text
original concern
  remains reconstructable

new question
  is explicitly recognized as later development
```

となる。

失敗は、AIが新しく提示した問いを、当初から中心だったconcernとして記憶・表示してしまうことである。

これはV3 Revision Integrity、V6 Human / AI Readability、Personal Inquiry ContinuityのHistorical Integrityと接続する。

## 6. Test Q3 — Suggestion Adoption Pressure

### Setup

AIが複数のRecommendationまたはnext action候補を生成する。

一部は妥当、一部は不要、一部は不確実とする。

### Compare

- 候補を初期画面で強く並べるSurface。
- `AI suggestions available`程度に留め、利用者が開いたときだけ詳細を示すSurface。

### Observe

- AI Recommendationと利用者Decisionを区別できるか。
- 選ばなかった候補を「却下したDecision」と誤って記録しないか。
- 利用者が候補外の次の行動を自然に選べるか。
- suggestionを読むこと自体が義務のように感じられないか。
- high-valueな提案を見逃していないか。

### Interpretation

AI suggestionを開く率が高いこと自体を成功としない。

見るべきなのは、Inquiryを前進させながらRecommendation / Decision境界とAgencyを保てるかである。

## 7. Test Q4 — Quiet Surface must not hide Material Change

Quiet Infrastructureを誤って実装すると、重要なchange cueまで隠れる危険がある。

### Setup

Inquiry中断後に、少なくとも次のいずれかを追加する。

- materialなnew Evidence
- changed premise
- newly discovered Conflict
- previous Recommendationを弱めるObservation
- review / reopen conditionに該当する変化

### Expected

quiet modeであっても、利用者がcurrent stateを誤解する危険が高いchangeは、初期Orientationから到達可能でなければならない。

ただし、detailをすべて展開する必要はない。

```text
quiet
  != hidden material change

progressive disclosure
  != semantic omission
```

### Hard failure candidate

UIを静かにするためmaterialなConflictやchanged premiseを通常表示から落とし、利用者がold stateのまま作業を再開する。

## 8. Test Q5 — Assistance Availability without Dependence

### Setup

同じInquiryで、

1. AI assistance available
2. AI assistance unavailable

を比較する。

### Expected

AIがなくても、

- current Inquiryを読める。
- Unknown / Conflictを確認できる。
- manual updateできる。
- Decisionがある場合はbasisを読める。
- next actionを人間が自分で記録できる。

AIが利用できる場合は追加価値を提供してよいが、Productの基本continuityを成立条件として依存させない。

これは既存H4 AI Portability / M8 Independenceと重なるため、別Requirementへはしない。

## 9. 補助指標候補

既存Metricsへ正式追加するかはactual evaluation後に判断する。

### Q-M1 — Original Concern Retention

再開時に、AI suggestionとは別にoriginal concernを再構成できたか。

### Q-M2 — Suggestion Attribution Integrity

AIが後から生成したQuestion / Recommendationを、historical user stateへ誤帰属しなかったか。

### Q-M3 — Attention Load

resume時に、本来のInquiryを前進させる前に読解・選別したAI-generated candidateの量と主観負担。

### Q-M4 — Material Discovery Gain

proactive assistanceによって初めて発見できたmaterial Unknown / Conflict / premise changeがあったか。

### Q-M5 — Dismissal / Deferral Cost

不要なsuggestionを無視、保留、却下するために必要だった操作・認知負担。

これらを単一scoreへまとめない。

## 10. 成功条件を「静かな方が勝つ」にしない

Brand World Discoveryから来た仮説だからといって、Quiet Surfaceが常に優れることを証明する実験にしない。

考えられる結果は複数ある。

### Result A — Quiet-firstが明確に有利

大量のproactive suggestionがconcern driftやselection burdenを増やす。

**Implication:** defaultはminimal Orientation、AI suggestionsはprogressive disclosureを優先する。

### Result B — Proactive assistanceが明確に有利

利用者自身では見落とすmaterialなConflict / premise changeを高い確率で発見し、burdenも許容範囲である。

**Implication:** proactive assistanceを強める。ただしhistorical attributionとDecision boundaryを維持する。

### Result C — Inquiry typeによって異なる

探索的な創作・研究ではquiet-firstがよく、boundedなtechnical comparisonではproactive assistanceが有用、など差が出る。

**Implication:** one-size-fits-allのUI ruleにせずProfile / user control / context-sensitive presentationを検討する。

### Result D — 差が小さい

Product Valueへ影響するほどの差がない。

**Implication:** Quiet Infrastructureをnormative interaction ruleへ昇格させず、Brand / Design preferenceとして留める。

どの結果も正当である。

## 11. Cognitive Commonsとの境界

Quiet Infrastructureの評価は、current Personal Inquiry Continuityのsingle-user範囲で行える。

一方、Cognitive Commonsはteam / organizationでの共有、Selective Disclosure、Responsibility、Access Control等を含み得るため、本amendmentへ混ぜない。

single-userで得た結果から、

```text
quiet personal inquiry UX
  → organization-wide sharing rule
```

を直接導かない。

将来、bounded Cognitive Commonsをactualに評価するときは、shared attention、notification propagation、cross-person recommendation pressure等が別論点になる可能性がある。

## 12. Requirementへの停止線

このamendmentから、直ちに次のRequirementを作らない。

- AI suggestionsは必ずcollapsedでなければならない。
- 初期画面に表示できるsuggestion数はN件以下である。
- proactive AIは禁止する。
- quiet modeをUniversal Product設定として持つ。
- attention scoreをUniversal semantic fieldとして保存する。

まずactual dogfoodでProduct failureを観測する。

既存V2 / V3 / V5 / V6 / V7、Product Interaction、PIC-*候補で十分ならNo Changeとする。

## 13. 既存protocolへの適用方法

新しいparallel runを作るのではなく、existing Evaluation Stageへ組み込む。

### E1 — Short-cycle Personal Dogfooding

一部Inquiryでquiet-first / proactive-firstの違いをqualitativeに観察する。

### E2 — Baseline Comparison

B0 / B1 / P1のP1内で、必要に応じて二つのPresentation conditionを比較する。

### E3 — Cross-AI Handoff

別AIへ渡した際、AIが大量の新規suggestionを生成してもhistorical roleを維持できるかを見る。

このamendment専用のProduct Profileやstorage schemaを追加しない。

## 14. Evidenceの読み方

```text
quiet surface preferred by user
  != Quiet Infrastructure Product Value proven

proactive suggestions often opened
  != proactive assistance improves outcomes

AI found more candidate questions
  != Inquiry Continuity improved

fewer visible items
  != lower cognitive burden automatically proven
```

見るべきなのは、historical correctness、original concern retention、material Unknown / Conflictの保持、first useful action、capture / correction burdenの組み合わせである。

## 15. Natural Japanese review

このamendmentでは、ブランド世界の「静かな井」という表現をそのままUI仕様へ変えず、AIが多数の候補を生成できる時代に、利用者のInquiryとattentionをどのように守るかという反証可能なProduct hypothesisへ翻訳した。

既存Personal Inquiry Continuityが持つRecovery Effort、Capture Burden、Correction Trust、Generic Summary比較、Cue Utility、False Continuity等を再利用し、足りなかったproactive suggestionによるconcern drift、suggestion attribution、selection burdenだけを追加している。

また、Quiet Surfaceが常に優れるとは仮定せず、proactive assistanceがmaterialな見落としを発見する価値や、Inquiry typeによる差も同じ強さで検証対象にした。

内容、authority、反証条件を整理した後、**自然な日本語としてProduct hypothesisと過剰適用の危険が同時に読めることを最重要視して全文を再ドラフトし、最終意味監査を実施済み**とする。
