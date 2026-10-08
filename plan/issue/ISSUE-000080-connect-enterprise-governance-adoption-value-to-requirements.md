# ISSUE-000080: 企業の統治・意思決定基盤としての初期認知と導入容易性を、Product Valueからrequirementへ接続する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0027, ADR-0028, ADR-0029, ADR-0030, ADR-0033, ADR-0034**  
Updated: 2026-10-06

## Goal

複数のAIツールを使う企業が、それらの出力を一つの責任ある意思決定主体の判断として扱えるようにする。そのための最初の導入体験を、Product Value、Product Milestone、Candidate Requirement、Experiment、Requirement auditの順につなぐ。

このIssueで判別できるようにすることは次の五点である。

1. 企業の統治・意思決定基盤という利用場面が、既存のV1〜V8とDecision Continuityで説明できるか、新しい価値を要するか。
2. 「統合された意思決定主体」という考え方を、SEIの非目標(中央のAI、実行基盤の囲い込み)と矛盾させずに製品へ置く方法。
3. 初期認知と導入容易性を、どの観測可能な基準で評価するか。
4. 既存のREQ-0001〜0023とSCN-0001〜0019で足りない部分が、実際にあるか。
5. 実装の最初の着地点(Go製のCLIと常駐サービス、AIツール接続)をどのADR候補へ切り出すか。

成果物はIssue本文、Candidate Requirementの監査結果、Experimentの結果である。RequirementやADRの確定は、監査を通ったものに限る。

## Background

### 確認済みの事実

- SEIの意味核であるsemantic runtimeはGoで実装されている(`runtime/go/semanticruntime`ほか、ADR-0027)。Pythonはtool、evaluation、証跡採取スクリプトに限られ、全面的な書き直しを要する状態ではない。
- 起票時点では、利用者が直接使うGo製のCLIと常駐サービスは存在せず、`runtime/go/cmd/`にあるのはprobe類だけだった。2026-10-06に、CLIの最小版`sei`(`init`、`add`、`resume`、`verify`、`export`)を実装した。範囲と留保は`runtime/SEI_CLI_FIRST_SLICE_EVIDENCE_2026-10-06.md`にある。常駐サービスとAction Intentの確認は未実装である。
- Product Shape 4.6にEvidence / Governance Surfaceがあり、ADR-0030でProduct AccessとResponsibilityは分離済みである。
- Authority、Responsibility、Recommendation / Decision分離は、REQ-0006、0008、0013、0017で定義済みである。
- 非機能要件(性能、可用性、security、import / export等)は、Product Shape 8.6でdeployment scopeごとに未定義のまま残っている。
- 外部利用者によるAdoption / Outcome Evidenceはない。

### 現時点の推論と仮説

- 2028年前後には、企業内で多数のAIエージェントが判断を下書きし、一部は委任を受けて決める。このとき問題になるのは個々のツールの精度よりも、全体として誰の判断で、どの権限の範囲で、何が未解決のまま決まったのかを説明できるかである。(仮説。`plan/SEI_FUTURE_POSITIONING_2026-10.md`)
- 企業の導入は、中央のIT部門による全社導入からではなく、チーム単位で入れて効果を出し、後から統治へ昇格する経路のほうが現実的である。(仮説)
- 初期認知は、構造の正しさの説明ではなく、最初の五分から十五分で得られる具体的な成果で決まる。(仮説)

### 既存方針との緊張

利用者(プロダクト責任者)から「AIツール類を束ね、統合された意思決定主体としてのふるまいを持たせることが鍵」という方向が示された。これは、Product Vision 12が長期目標にしないとした「最も賢い中央AI」「あらゆる判断を自動決定するシステム」と、読み方によって衝突する。

このIssueでは、統合の層を認知(誰が賢く考えるか)ではなく説明責任(誰の判断として扱うか)に置くことで両立させる案を取る。

```text
統合する
  = 複数ツールの提案を、一つのAuthority / Delegation / Policyの下で受け、
    決定と実行意図の発行を一つの責任主体の名で記録する

統合しない
  = 推論の中央集約、実行の囲い込み、ツールの内部モデルの共通化
```

この読み方を仮にGoverned Decision Subjectと呼ぶ。Universal ontologyの型としては導入しない。製品上の振る舞いの呼称であり、意味の実体はAuthority、Delegation、Policy、Decision、Action Intentの組み合わせで表す。

## Questions

1. 統合された意思決定主体は、判断を受け付けて記録し、実行意図の発行を制御する層(Decision Gateway)にとどめるか。それとも、SEI自身が判断を下書きする参照エージェントを含むか。
2. 企業の最初の導入単位をチームとするか、全社の統治部門とするか。
3. 初期認知で、どの一文と、どの最初の体験を示すか。
4. 導入容易性を何で測るか。
5. 既存Requirementで足りない意味が実際にあるか。

## 暫定決定

2026-10-06に、プロダクト責任者がQuestion 1と2について、Claudeの推奨どおりに進めることを指示した。いずれも暫定であり、E-80.1〜4の結果で見直す。

1. Question 1: Governed Decision Subjectは、Decision Gatewayにとどめる。判断を下書きする参照エージェントをSEI自身は持たない。必要な場合は、Cognitive MethodまたはProviderとして外部に置く。
2. Question 2: 最初の導入単位はチームとする。全社の統治部門への展開は、チームでの効果をE-80.1〜3で確かめた後に扱う。

この二点を受けて、ADR-0033(Proposed)でDecision Gatewayの境界と最初の導入面を起票した。Question 3〜5は未決のままである。

## Product failure

Requirementを増やす前に、利用者の世界で何が壊れるかを先に書く。

1. 複数のAIツールが別々に推薦し、どれがどの根拠で、誰の権限のもとで採用されたのかが後から分からない。
2. AIが自分の出力を決定として扱い、委任を受けていない範囲まで実行意図が発行される。
3. 委任の範囲、期限、取り消しが記録されず、ある時点の権限を後から再現できない。
4. ツール間で推薦が食い違ったとき、新しいほうが勝った形で食い違いが消える。
5. 監査人や規制対応の担当者が、SEIの実行環境を持たずに、根拠と権限と未解決事項を検証できない。
6. 導入の最初の手順が重く、効果が見える前に利用者が離れる。
7. 既存ツールを入れ替えないと始められず、現場が採用できない。
8. 導入が全社の合意を前提にしており、チーム単位の試行ができない。
9. 構造だけが増え、ログやADR文書と比べた実質的な差が利用者に見えない。

失敗6〜9はProduct failureとして扱う。SEIの意味構造が正しいことを、価値の証明にしない。

## Product Valueからの流れ

```text
Product Value / V1〜V8 / Decision Continuity
  ↓
Value Proposition候補(企業の統治・意思決定基盤、導入容易性)
  ↓
Product Milestone候補(PMS-09)
  ↓
Open Question / Experiment / Human Review
  ↓
Candidate Requirement(CR-80.x)
  ↓
Requirement audit
  ↓
Stable Requirement / 既存Requirementへの統合 / No Change・Deferred
  ↓
ADR候補 → Architecture / Contract / Profile
  ↓
Go runtime(CLI、常駐サービス、Adapter) / Fixture / Test
  ↓
Executable Evidence → Release / Operational / Adoption Evidence
```

### 価値との対応

| 利用場面の要点 | 守る価値 | 備考 |
|---|---|---|
| 複数ツールの提案を一つの責任主体の判断として扱う | V2、V4、V8 | 実行手段とProviderの交換でも責任の意味を保つ |
| 委任範囲と権限を時点付きで再現する | V1、V3 | Revision Integrityと歴史的再構成 |
| ツール間の食い違いを消さない | V5 | Conflict != latest-wins |
| 監査人がSEI無しで検証する | V1、V6 | 人とAIが同じ正本を読む |
| 初期導入を軽くし、必要なときだけ厚くする | V7 | 新しいValue Axisにはしない |

導入容易性と初期認知は、新しいValue Axisとして立てない。V7のProgressive Explicitnessと、Product Shape 8.6の非機能要件として扱う。Quiet Infrastructureと同じ扱いである。

### Value Proposition候補(未反映)

次をSEI_VALUE_PROPOSITION.mdへ反映するかを、このIssueの監査後に判断する。

- 主な利用場面に、「複数のAIツールと人が関与する、企業の意思決定と統治」を明示する。
- 利用者に約束したいことへ、「既存のツールを入れ替えずに、最初の判断から記録と再開を始められること」を追加する。ただしOutcome Evidenceがない間は、Design方向と明記する。

### Product Milestone候補(未反映)

PMS-09 Governance Entry の案を示す。期限ではなくOutcomeとEvidenceで定義する。

- Outcome: チーム一つが既存のAIツールを変えずにSEIを導入し、最初の委任付きDecisionの記録、再開、第三者による検証までを、追加の専任担当無しで行える。
- Minimum Evidence: 空の環境での初期導入の観測(E-80.1)、異種ツールのConflict保持(E-80.2)、実行環境無しの検証(E-80.3)。
- 現在の状態: Not Yet Verified。

## 既存Requirementとの照合

Candidate Requirementを立てる前に、既存のREQ / SCNで表せる範囲を先に使う。

| 意味 | 既存の受け皿 | 未充足の可能性 |
|---|---|---|
| 提案と決定と権限と実行の分離 | REQ-0006 | なし |
| actor種別から権限を推定しない | REQ-0013 | なし |
| 責任を文脈に結び付ける | REQ-0017、REQ-0008 | 委任の範囲、期限、取り消しを時点付きで再構成する部分 |
| Provider中立 | REQ-0007、0021、0022 | なし |
| 食い違いを消さない | REQ-0002、0003 | 複数ツールが同時に推薦した場面のScenario |
| Storage、実行系から独立 | REQ-0018 | なし |
| 検証可能性 | REQ-0020、0023 | SEIの実行環境無しで検証できること |
| 軽く始め、厚くできる | REQ-0010 | 導入初期の観測基準が未定義 |

## Candidate Requirement

いずれもStableではない。優先順位は上から採用検討の価値が高い順である。

### CR-80.1 委任の時点付き再構成

AIまたはツールが、どのAuthorityから、どの範囲、どの期限で委任を受けて決定したかを、後から時点付きで再構成できる。

- 既存の受け皿: REQ-0017、0008、0009。
- 暫定の判断: 既存Requirementの拡張で足りる可能性が高い。Delegationを新しいUniversal型にせず、Authority関係のRevisionとして表せるかをまず確かめる。

### CR-80.2 実行意図の発行前確認

Action Intentの発行時に、参照するDecisionとAuthority basisの有無を確認でき、確認の失敗時の振る舞い(fail-closedまたはfail-open)を方針として選び、記録できる。

- 既存の受け皿: REQ-0006。
- 注意: SEIをworkflow engineやscheduler化しない。確認は発行の許否の判定に限り、実行の順序制御や再試行は外部Providerに置く。
- 暫定の判断: Profileまたは方針の層に置き、Requirement化は慎重に判断する。
- 実装状況(2026-10-06): `sei gate check`として、記録済みDecisionが方針を満たすかを確認する機能として実装した。判断の記録(決定のstore)は変更せず、確認のたびに、その結果を判断の記録とは別の運用ログ(`gate-checks.jsonl`)に追記する。方針は呼び出し側が選び、終了コードで許可、拒否、確認不能を分ける。Action Intentそのものの記録型と、確認結果のContract化は、必要性のEvidenceが出るまで先送りし、ADR-0034(Proposed)に判断を記した。Authorityと行為の範囲は確認せず、`not_verified`として出力する。

### CR-80.3 異種ツールの提案の保持

複数のAIツールが、同じ問いについて異なる推薦を出したとき、各ツールのProvenanceと食い違いを保ち、決定後に一つのツールの推薦が改訂されても過去のbasisは変わらない。

- 既存の受け皿: REQ-0002、0003、0007、0009。
- 暫定の判断: 新しいRequirementではなく、Acceptance Scenarioの追加で足りる可能性が高い。

### CR-80.4 実行環境無しの第三者検証

監査人が、SEIのruntimeやStorageにアクセスせず、書き出されたbundleだけで、根拠、権限、未解決事項、改訂の履歴を検証できる。

- 既存の受け皿: REQ-0018、0020、0023、Semantic Interchange Contract。
- 暫定の判断: 既存のContractで満たせるかを、独立した小さな検証器(Goの単体バイナリ)で確かめる。

### CR-80.5 First-Contact Adoption(非機能)

初期導入が、追加のインフラや既存ツールの変更を必要とせず、最初の記録と再開までを短い手順で行える。

- 既存の受け皿: REQ-0010、ADR-0029(単一node packaging)、Product Shape 8.6。
- 観測基準の案は次のとおり。固定のしきい値は先取りしない。
  - 空の端末から最初のDecision記録と再開までの経過時間と手順数。
  - 事前に必要な外部サービスの数。
  - 既存ツールへの変更の要否。
  - 初回で利用者が自力で完了できたか、助けが必要だったか。
- 暫定の探索目標として、初回導入を十五分以内とする。これは仮の目標であり、最初の観測の後に見直す。
- 暫定の判断: 製品の制約として記述する案と、Acceptance Scenarioに留める案を、E-80.1の結果で比べる。

### CR-80.6 既存ツールへの後付け接続

既存のAIツールの出力(MCP呼び出し、OpenTelemetryのspan、ticket、ログ)を、ツール側を変更せずにObservationまたはRecommendationとして取り込み、AIが付けた分類と、権限者が確認した分類を別のものとして保てる。

- 既存の受け皿: REQ-0010、0015、0016、0019。
- 注意: MCPやOpenTelemetryを、Stable Requirementにしない。Integration SurfaceのProfileとAdapterとして扱う。

### CR-80.7 企業のIDとの対応(Deferred)

OIDC、SCIM等の企業の識別基盤から得たIDを、Product Accessとして扱い、そこからResponsibilityやAuthorityを推定しない。

- 既存の受け皿: ADR-0030、REQ-0013。
- 暫定の判断: 単一チームの導入で必要性が実際に出るまでDeferredとする。

### CR-80.8 時刻と作成者の証明(Deferred)

署名とタイムスタンプで、記録の存在時刻と作成者を第三者が確かめられる。

- 既存の受け皿: Exact Binding、Representation Profile。
- 暫定の判断: 任意のProfileとして検討する。Contractは増やさない。外部利用者から必要性が示されるまでDeferredとする。

## Experiment

いずれも、実行前はDesign Evidenceである。実行しても、Operational EvidenceやAdoption / Outcome Evidenceには昇格させない。

### E-80.1 初期導入の観測

SEIの開発に関わっていない開発者または運用担当者が、空の端末で、書かれた手順だけを使って導入する。経過時間、つまずいた箇所、必要になった事前準備を記録する。作者の補助は、補助が入った時点で記録に残し、成功として数えない。

### E-80.2 異種ツールの接続

役割の違う三つ以上のAIツールの推薦を取り込み、食い違いを含む判断を一件完了させる。その後、一つのツールの推薦を改訂し、過去のbasisとConflictが保たれることを確かめる。

### E-80.3 実行環境無しの検証

書き出したbundleだけを、SEIを使っていない監査担当者に渡し、根拠、権限、未解決事項、決定後の変更を読み取れるかを観察する。

### E-80.4 代替との比較

ISSUE-000078の方式に倣い、ログ、ADR文書、チャット履歴と、SEIの記録で、再開の負担と誤読の件数を比べる。追加構造に実質的な差がなければ、その結果を価値の反証として残す。

## 実装方針

- 標準実装言語はGoとする(ADR-0027)。利用者が直接触れるCLIと常駐サービスは、`runtime/go/cmd/`にGoで置く。単一の静的バイナリを目標とし、外部のDBや常駐サービスを前提にしない。
- Pythonは、証跡採取、評価、fixture生成、開発用のcheckerに限る。ツールの接続Adapterがproductionへ進む場合は、ADR-0027の境界に従ってGoへの移行を判断する。現在`runtime/integration/e3b_m1b_ollama_adapter.py`がPythonで存在するが、probe用途として扱う。
- 他言語の利用者のため、Contractのmachine-readable representationとfixtureは維持し、各言語の薄い検証器をそれに対して作れるようにする。

## ADR候補

次はいずれも、Issueの成果を見てから起票する。

1. Decision Gatewayの境界(受け付けるもの、判定するもの、持たないもの、fail時の振る舞い)。
2. 利用者向けCLIと常駐サービスの面(最初のコマンド体系、単一バイナリ、設定の最小化)。
3. AIツール接続のIntegration Surface(MCP、OpenTelemetry、webhook)。Contractではなくprofileとして置く。
4. Delegationの表現(Authority関係のRevisionで表せない場合のみ)。

## 停止線

- 「統合された意思決定主体」を、SEI自身が判断や推論を行う中央のAIという意味へ読み替えない。
- Organization、Agent、Policy、Delegation等を、Universal ontologyの型として先に置かない。
- MCP、OpenTelemetry、特定のIdPを、採用しただけでStable Requirementにしない。
- SEIをworkflow engineやschedulerにしない。
- 統治基盤としての準拠(EU AI Act、ISO/IEC 42001等)を主張しない。必要な場合は証跡の形式の対応表に留める。
- 導入件数やインストール数を、Adoption / Outcome Evidenceとして扱わない。
- 作者の補助付きの導入を、導入容易性のEvidenceとして扱わない。
- Design Evidenceだけで、導入が容易であると主張しない。
- E-80.1〜4の結果を、v0.2.0のsupported scopeへ遡って加えない。

## Resolvedの条件

- Questions 1〜5に、実際の根拠付きで答えが出ている。
- Candidate Requirementのそれぞれが、Stable Requirement、既存Requirementへの統合、No Change / Deferredのいずれかに分類されている。
- E-80.1〜4のうち実施したものと、未実施のものが、Evidenceの高さとともに分けて記録されている。
- 必要なADR候補が起票され、不要なものはその理由が残っている。
- Value Proposition候補とPMS-09候補の反映可否が決まっている。

## 関連文書

- `plan/SEI_FUTURE_POSITIONING_2026-10.md`
- `plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`
- `product/vision/SEI_PRODUCT_VISION.md`
- `product/value/SEI_VALUE_PROPOSITION.md`
- `product/definition/SEI_PRODUCT_SHAPE.md`
- `product/roadmap/SEI_PRODUCT_MILESTONES.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `architecture/IMPLEMENTATION_LANGUAGE_POLICY.md`
- ISSUE-000073、ISSUE-000078
