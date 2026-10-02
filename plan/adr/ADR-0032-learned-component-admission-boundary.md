# ADR-0032: Learned Componentの導入をProduct Residualと段階的比較に基づいて判断する

Status: **Proposed**  
Related Issue: **GitHub #546 — cross-repository cognitive task atlas**  
Updated: 2026-10-02

## Context

SEI Cognitionと周辺Productでは、LightGBM、embedding、local SLM、Jev teacher、
recurrent model、connectome reservoir等、性質の異なる認知系技術を利用できる余地が広がっている。

一方、技術的に学習できることと、学習系ComponentをProductへ導入する価値があることは同じではない。

実際の横断研究では、次の傾向が繰り返し観測されている。

- SEI #603では、決定論的な因果履歴特徴と小さなLightGBMが、事前登録したsynthetic temporal benchmarkの大半を高い精度で解き、より重いMaleCNS reservoirが意味のある改善幅を示せるheadroom自体が残らなかった。
- 同じ#603で再確認したVS Bearの実consumer residualも、学習表現不足ではなく、小さな決定論的controller omissionとして説明・修正できた。
- SUI #3157では、learned affinity rankingを意味形成やisland acceptanceへ直接昇格させず、既存baselineの評価結果が後続experimentを正当化した場合だけproposal-onlyの候補生成として進める設計になっている。
- MMI #218では、近似・学習系の候補生成と、現在sourceに対するexact verification、明示的な利用者選択、authoritative referenceを分離している。
- EKI #19では、hard policy eligibilityをmodel scoreから分離し、学習系schedulerをshadow observationから段階的に扱う。
- #556では、teacher acquisition自体を目的化せず、real residual、cheap baseline、評価headroom、teacher provenance、delivery failureとlabel outcomeの分離を先に要求している。
- VS Bear #44では、recurrent modelを導入する前にcurrent state、明示的なengineered memory、固定causal historyを比較し、短い履歴で同等なら単純な方式を優先する方針を明示している。

これらは個別技術の優劣というより、共通したProduct判断を示している。

~~~text
learnable
  != worth learning

better benchmark score
  != Product Value improvement

model confidence
  != authority

expensive / biologically inspired / generative
  != higher-value cognition
~~~

ADR-0018はProduct Valueを下位設計の正当化基準とし、実装容易性や性能だけで上位の意味境界を変更しないと定めている。
ADR-0017とADR-0025は、Reference ModelやCognitive MethodをUniversalな意味から分離している。

しかし現時点では、学習系Componentを新たに導入する前に何を満たす必要があるかを横断的に定めたDecisionはない。

この空白があると、次の問題が起こり得る。

- modelやteacherを利用できること自体が導入理由になる。
- cheap baselineで既に解ける課題へ、より重いComponentを追加する。
- benchmarkを見た後で閾値やsplitを変更し、導入理由を後付けする。
- learned scoreがRecommendationやAuthorityへ暗黙に昇格する。
- rare / residual / Unknownを低scoreとして消す。
- train/evaluation leakageやteacher provenance不足を、精度値だけで覆い隠す。
- shadow experimentの成功を、そのままproduction activationへ昇格する。
- negative resultを失敗とみなし、採用できる課題が見つかるまでbenchmarkを作り続ける。

## Decision

### 1. Learned Componentの導入は、技術候補ではなくProduct Residualから始める

新しいlearned componentを導入する最初の問いは、「何を学習できるか」ではなく、
「現在のProduct Valueを妨げている、実在する未解決のresidualは何か」とする。

Product residualには、少なくとも次のいずれかを必要とする。

- current product / consumerで観測されたfailure、cost、latency、review burden、coverage不足等。
- frozen benchmarkまたはactual traceで再現できる未解決差。
- current methodでは満たせない明示的なProduct Requirement / Acceptance条件。
- 将来仮説の場合は、actual residualではなくDesign Hypothesisであることを明示した限定experiment。

「使えるmodelがある」「teacher dataを生成できる」「新しい技術として興味深い」だけではProduct-directed admission理由にしない。

~~~text
technology availability
  != product residual
  != admission
~~~

### 2. 最も単純で信頼できる比較対象から段階的に上げる

課題ごとに、意味のある範囲で次の順に比較する。

~~~text
existing behavior / manual workflow
  -> deterministic rule / exact method
  -> simple statistical / linear / retrieval baseline
  -> bounded small learned model
  -> heavier learned / recurrent / generative component
~~~

すべての課題に同じ段数を強制しない。
自由生成では決定論的ruleが適切な直接比較にならない場合もある。その場合も、current manual process、retrieval、template、既存Method等、その課題に対する最も単純なcredible comparatorを置く。

重要なのは「LightGBMを必ず通す」ことではなく、より重い手段が、より単純な手段では得られない価値を示すことである。

### 3. 高コストComponentを評価する前に、意味のある改善幅とheadroomを固定する

可能な場合、結果を見る前に次を定める。

- primary metric。
- split / held-out family / source-group identity。
- meaningful effectの最小幅。
- 許容できるregression。
- latency、memory、model size、teacher cost等のresource budget。
- false-positive / false-negative等、Productに固有の重大failure。
- residual / minority / Unknown / Conflictを保持する条件。

cheap baselineが既に高く、理論上の最大改善でも meaningful effect thresholdへ届かない場合、そのbenchmarkは重いComponentのadmission根拠として閉じる。

~~~text
insufficient headroom
  = useful negative Evidence
  != reason to lower the threshold
~~~

新しい課題familyを試す場合は、既存結果を見て採用可能な課題を探すのではなく、異なるProduct hypothesisとして先に目的と評価を固定する。

### 4. Data / teacher / splitのEvidenceが揃う前にモデル比較をProduct判断へ使わない

learned componentのadmission判断では、少なくとも必要な範囲で次を保持する。

- input/source identity。
- feature/schema version。
- teacher / label classとprovenance。
- concrete split-group identity。
- evaluator-onlyのgeneralization family。
- held-out setのfreeze時点。
- teacher取得時のmodel/method/version。
- active acquisitionを使う場合はselection時点の理由とsignal snapshot。
- transport/environment failureとteacher outcomeの分離。

同じ抽象familyがtrain/testに現れることと、同じ具体source/session/cohortが漏洩することを混同しない。

~~~text
generalization family reuse
  != concrete source reuse
~~~

teacher response、AI proxy、synthetic labelは、そのprovenanceの高さを保持する。精度が高いことを理由にground truthへ自動昇格させない。

### 5. Learned outputは、明示的に昇格されるまでproposal / observationの範囲に置く

初期段階では、learned outputを次のいずれかに限定する。

- candidate。
- ranking。
- estimate。
- anomaly / OOD signal。
- shadow observation。
- Recommendation input。

Learned scoreだけから、semantic truth、Evidenceの真偽、Decision、Authority、permission、destructive action、canonical source rewrite、residual / minority materialの削除を導かない。

必要なdeterministic authority、hard policy、exact validation、human/user decisionはmodelの外側に残す。

~~~text
learned score
  != semantic authority
  != execution permission
~~~

productionでより強いAuthorityを与える場合は、別途Requirement / ADR / Acceptance Evidenceを必要とする。

### 6. Activationはofflineから段階的に行い、rollbackをadmission条件に含める

Product-directed learned componentは、原則として次の段階を区別する。

~~~text
offline evaluation
  -> shadow observation
  -> candidate / assisted mode
  -> explicit activation
~~~

課題によって一部段階を省略できるが、省略理由を明示する。

少なくともproduction activation前には次を確認する。

- exact deployed artifact identity。
- runtime/backend/precision/feature adapter等のdeployment identity。
- abstention / OOD behavior。
- fallbackまたはrollback。
- monitoring可能なProduct failure。
- activation / disable authority。
- retrain、recalibration、quantization、backend変更時の再評価条件。

training checkpointの系譜が同じでも、deployment artifactが変われば過去Evidenceを自動継承しない。

### 7. Negative EvidenceをProduct判断として保持する

次は正当な成果である。

- deterministic methodで十分だった。
- simple learned baselineで十分だった。
- heavy modelの改善headroomがなかった。
- accuracyは上がったがProduct metricが改善しなかった。
- minority/residual preservationが悪化した。
- resource costが価値差に見合わなかった。
- evaluation leakageを除くと改善が消えた。
- teacher / source provenanceがProduct判断に必要な高さへ達しなかった。

この場合、結果を捨てて別のbenchmarkを探すのではなく、そのtask familyに対するadmissionを停止または延期する。

### 8. Cross-repositoryで共有するのはadmission semanticsであり、modelそのものではない

SEI、SUI、TEI、EKI、MMI、VS Bear等で共有し得るのは、主として次である。

- residualの定義。
- baseline ladder。
- split / leakage境界。
- meaningful-effect / headroomの考え方。
- authority分離。
- activation段階。
- provenance。
- negative Evidenceの扱い。
- revisit条件。

feature、teacher、model、threshold、runtime budgetはdomain / productごとに異なってよい。

~~~text
shared admission semantics
  != shared model
  != shared threshold
  != shared authority
~~~

### 9. Admission Recordは軽量なDecision Evidenceとして残す

新しいUniversal ContractはこのADRでは作らない。
ただし、Product-directed learned componentを開始するときは、Issue、experiment plan、ADR等の適切な場所で、少なくとも次を追えるようにする。

~~~text
task / product residual
current behavior
simplest credible comparator
cheap learned comparator when relevant
frozen evaluation identity
meaningful-effect criterion
remaining headroom
teacher / label provenance
authority kept outside model
resource budget
abstention / fallback
activation stage
rollback / revisit trigger
current Evidence height
admission = admitted | deferred | rejected | research-only
~~~

この記録を単一scoreへ変換しない。

### 10. Admission DecisionとProduct Value実証を分ける

admissionは「限定されたexperimentまたはactivationへ進む理由がある」という判断である。

~~~text
admission
  != model quality established
  != operational value established
  != adoption / outcome established
~~~

ADR-0018のEvidence階層を維持する。

- Design Evidence
- Executable Evidence
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

modelのbenchmark PASSだけでProduct Valueを実証済みにしない。

## Alternatives considered

### A. Model-firstで候補を比較し、最も高精度なものを採用する

採用しない。

性能比較自体は必要だが、task residual、authority、resource cost、leakage、headroomを後回しにすると、「精度の高い不要なComponent」を導入できてしまう。

### B. deterministic-firstを絶対規則にする

採用しない。

生成、曖昧な候補探索、連続身体制御等では、決定論的ruleが適切な直接比較にならない場合がある。
必要なのはdeterministic方式の強制ではなく、その課題に対する最も単純なcredible comparatorとの比較である。

### C. 全repo共通の精度・latency閾値を定める

採用しない。

誤りのcost、実行cadence、model size、privacy、Authority、held-out familyはProductごとに異なる。
共通化するのは判断手順と意味境界であり、数値閾値ではない。

### D. learned componentは常にproposal-onlyに固定する

採用しない。

将来、十分なOperational / Adoption Evidenceと明示的なAuthority設計が得られれば、より強い自動化を正当化できる可能性がある。
このADRは永久にproposal-onlyを要求するのではなく、強いAuthorityへの昇格を別の明示的Decisionにする。

### E. 技術調査はProduct residualが出るまで行わない

採用しない。

Research-onlyの探索は許容する。
ただし、科学的興味や将来仮説とProduct-directed admissionを明確に分ける。
#603のMaleCNS研究のように、科学的関心を保持しつつProduct-directed実装を延期できる。

## Consequences

### Positive

- modelを使えること自体が開発目的になるのを防ぎやすい。
- cheap baselineで十分な課題へ不要なruntime・model・運用負荷を追加しにくい。
- negative resultをProduct判断として再利用できる。
- benchmarkを見た後の閾値・split変更を抑えやすい。
- learned scoreとsemantic authority / permissionを分離しやすい。
- minority、residual、Unknown、Conflictを効率最適化で消しにくい。
- 複数Productで異なるmodelを使っても、導入判断の意味を比較できる。
- teacher acquisitionやactive curriculumを、task-level headroomがないまま拡大しにくい。
- heavy model / recurrent model / biological reservoir等を、単純方式では解けない実residualへ集中できる。

### Costs / Risks

- 事前登録、baseline、split、headroom確認に追加作業が必要になる。
- early prototypeの速度が下がる場合がある。
- 「最も単純なcredible comparator」の選択自体に判断が必要で、完全な機械判定にはできない。
- 新規性の高い課題ではProduct residualをまだ観測できず、research-only状態が長くなる可能性がある。
- headroomが小さくても別の価値軸で導入する合理性がある場合、単一metricだけを見ると誤ってrejectできる。

最後の点を避けるため、headroomは単一精度指標だけでなく、latency、review burden、resource use、calibration、OOD、minority preservation等、対象Productで意味のある軸ごとに評価する。

## Revisit conditions

次の場合に再検討する。

- 複数の実Productで、この段階ゲートが明確な価値あるlearned componentの導入を繰り返し妨げる。
- simple baselineとの比較では捉えられないProduct Value差がactual Outcomeとして反復観測される。
- online adaptation等、現在のoffline/shadow/candidate/activation段階では表現できない方式がProduct要件になる。
- Authorityを限定できない種類のautonomous controlが正式なProduct Requirementになる。
- cross-repoでAdmission Recordの共通machine-readable schemaが少なくとも2つのconsumerに必要となる。
- #546 / #556の研究から、現在のbaseline ladderやheadroom規則を反証するEvidenceが得られる。

## Evidence

### Product / SEI authority

- product/value/SEI_PRODUCT_VALUE.md
- product/principles/SEI_PRODUCT_PRINCIPLES.md
- ADR-0017: Reference Model / Cognitive Method boundary
- ADR-0018: Product Value authority / evaluation boundary
- ADR-0025: Cognitive Method portable contract boundary

### Cross-repository research Evidence

- GitHub Issue #546: cross-repository cognitive task atlas
- GitHub Issue #556: active curriculum / teacher acquisition
- GitHub Issue #603: MaleCNS temporal reservoir evaluation
- SUI Sensemaking #3157: learned affinity candidate ranking with residual preservation
- Markdown Matrix Injector #218: structured-artifact intelligence pilot
- EKI Fabric #19: learned scheduling shadow research
- VS Bear Simulator #44: embodied behavior learning roadmap
- VS Bear Simulator #50: locomotion observation / dataset contract

Evidence height at this ADR:

~~~text
cross-repo Design Evidence         strong
bounded executable experiment      present in several source issues
cross-repo Operational Evidence    not established
cross-repo Adoption / Outcome      not established
~~~

そのためStatusはProposedとし、Stable RequirementやUniversal Contractへの即時昇格は行わない。

## Follow-up

1. #546の各cross-repo pilotで、このADRのAdmission Record項目を文書上のチェックとして再利用する。共通runtime/schema実装はまだ作らない。
2. #556では、real residualとtask-level headroomが確認される前にactive acquisitionを開始しない。
3. #603では、cheap deterministic/history + bounded LightGBMを超える実consumer residualが得られるまでProduct-directed MaleCNS admissionを再開しない。
4. SUI/MMI/EKI/VS Bearでは、既存の個別gateをこのADRへ置き換えず、整合する上位判断として参照する。
5. 少なくとも2つのconsumerで同じmachine-readable Admission Recordが必要になった場合だけ、shared schema化を再検討する。

## Natural Japanese review

Product Value、Product Principles、ADR-0017、ADR-0018、ADR-0025、#546、#556、#603、およびSUI/MMI/EKI/VS Bearの現行研究境界を照合した。

その結果、「学習技術を使えること」と「Productへ導入する価値があること」を分ける必要性が、単一repoの好みではなく複数の独立した研究レーンで繰り返し現れていると判断した。

特に、安価なbaselineが事前登録した評価をほぼ解いて重い方式の改善headroomを失わせた#603の負のEvidenceと、learned proposalをexact validationやAuthorityから分離しているMMI/SUI/EKIの設計を統合し、Product residual、simplest credible comparator、headroom、provenance、authority、activation、rollbackを一つの導入判断へ整理した。

意味、要求強度、Evidenceの高さを変えず、自然な日本語として全文を再監査した。
