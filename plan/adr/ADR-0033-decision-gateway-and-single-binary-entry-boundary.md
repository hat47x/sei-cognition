# ADR-0033: Decision Gatewayと単一バイナリによる最初の導入面の境界

Status: **Proposed**  
Related Issue: **ISSUE-000080**  
Updated: 2026-10-06

## Context

企業が複数のAIツールを使うとき、SEIは、それらの提案を一つの責任主体の判断として記録できる必要があります。一方で、Product Visionは「最も賢い中央AI」や「あらゆる判断の自動決定」を長期目標にしません。

ISSUE-000080で、プロダクト責任者は暫定的に次を決めました。統合された意思決定主体は、判断を受け付けて記録し、実行意図の発行を確認する層(Decision Gateway)にとどめます。最初の導入単位はチームとします。

このADRは、その二点を受けて、Decision Gatewayの境界と、利用者が最初に触れるGo製バイナリの面を定めます。

関係する既存の判断は次のとおりです。

- Product Value: V2、V4、V7、V8、Decision Continuity。
- Requirement: REQ-0006、0010、0013、0017、0018、0021。
- ADR-0027(Goを標準実装言語とする)、ADR-0028(Product Interactionはcanonical meaning上の操作境界)、ADR-0029(単一node packaging)、ADR-0030(Product Accessとsemantic Authorityの分離)。

このADRの起票時点では、Design Evidenceだけでした。その後、利用者向けCLIの最小版を実装しました(Evidenceの節を参照)。常駐サービスと、Action Intentの発行時の確認は、まだありません。`sei gate check`は、記録済みのDecisionを確認するCLIの機能です。導入容易性の観測(E-80.1)も未実施です。

このADRで固定しないものは次です。

- 具体的なコマンド名、引数、設定ファイルの形式。
- MCP、OpenTelemetry、webhookなど、AIツール接続の具体的なprotocol。
- 委任(Delegation)をAuthority関係のRevisionで表せるかどうか(CR-80.1)。
- 企業のID基盤との対応(CR-80.7)。
- 署名とタイムスタンプ(CR-80.8)。

## Decision

### 1. Decision Gatewayの責務

Decision Gatewayは、次のことを行います。

- AIツールや人からのObservation、Recommendation、Decision、Action Intentの提出を受け付け、意味の区別を保ってcanonicalに記録する。
- Action Intentの発行時に、参照するDecisionとAuthority basisがあるかを確認し、結果を記録する。確認に失敗したときの振る舞い(fail-closedまたはfail-open)は方針として選べるようにし、選択を記録に残す。
- 複数のツールの提案が食い違うとき、食い違いをConflictとして保ち、後から改訂された提案が過去のbasisを変えないようにする。

Decision Gatewayは、次のことを行いません。

- 判断を自ら下書きしない。判断の下書きが必要な場合は、Cognitive MethodまたはProviderとして外部に置く。
- 実行の順序制御、再試行、スケジューリングをしない。実行はExecution Providerの責務とする。
- ツールの内部モデルや内部状態を、共通のontologyへ取り込まない。
- Access権限の保有から、Authorityを推定しない。

```text
Decision Gateway
  != 判断を下すAI
  != workflow engine
  != Access Control

Action Intentの確認 != Executionの制御
```

### 2. 最初の導入面

SEI自身が所有する、利用者が最初に触れる面は、Goで実装した単一の静的バイナリとして提供します。

- 外部のDBや常駐サービスを事前に必要としない。ADR-0029の単一node profileに従い、ローカルのStorageだけで動く。
- 既存のAIツールを変更せずに、後付けで接続できる。接続の具体的なprotocolはIntegration Surfaceのprofileとし、このADRでは固定しない。
- 最初は軽い明示度から始められ、必要な場面だけ厚くできる(REQ-0010)。
- 書き出したbundleは、SEIの実行環境を持たない第三者が検証できる。検証器は同じバイナリの機能、または独立した小さなバイナリとして提供する。

導入の最初の単位はチームです。全社の合意や中央のIT部門の作業を前提にしません。

### 3. 実装言語

導入面とGatewayの実装はGoとします(ADR-0027)。他言語の利用者のためには、Contractのmachine-readable representationとfixtureを維持します。Pythonは、評価、証跡採取、開発用のcheckerに限ります。

### 4. 導入容易性の扱い

導入容易性は、新しいValue Axisではなく、V7の観測と非機能要件として扱います。観測の基準はISSUE-000080のCR-80.5に従い、固定のしきい値はE-80.1の結果が出るまで確定しません。

## Alternatives considered

### A. SEI自身が判断を下書きする参照エージェントを含める

導入時の見栄えはよくなります。しかし、Product Visionの非目標と衝突し、判断の質の責任がSEIに移ります。AIモデルの入れ替わりが速い世界では、SEIの価値が特定のモデルの出来に依存します。Provider独立(V4)と実行独立(V8)が損なわれるため採りません。

### B. 実行を含むworkflow基盤として統合する

「統合された主体」としては最も強い振る舞いを示せます。しかし、実行基盤の囲い込みになり、既存のworkflowやAIツールを置き換える導入負担が生じます。初期導入の容易性(最重要)と、Execution Independenceの両方に反するため採りません。

### C. 全社の統治部門から導入する

統治の価値は直接示せます。しかし、導入に全社の合意が要り、最初の効果が見えるまでに時間がかかります。初期認知の獲得に不利であり、まずチームから入れて効果を確かめる経路を優先します。

### D. 導入面をSaaSとして提供する

運用負担は利用者側で小さくなります。ただし、企業が判断記録を外部に預ける合意が先に要り、単一node profile(ADR-0029)とも異なります。hosted運用は、チームでの効果が確認された後に別のADRで扱います。

## Consequences

### Positive

- 統合された意思決定主体を、非目標と矛盾せずに製品へ置ける。
- 利用者が最初に触れる面が単一のバイナリになり、導入の手順と前提が少なくなる。
- 既存のAIツールを変えずに始められる。

### Costs / Risks

- 利用者向けのCLIとGatewayの最小実装が必要になる。起票時点ではprobeしかなかった。その後、CLIの最小版を実装した(Evidenceの節を参照)。
- 「統合された主体」の振る舞いが、Gatewayに限定されることで、期待より弱く見える可能性がある。
- Action Intentの確認が、実行の制御と混同されるおそれがある。境界を文書とテストの両方で保つ必要がある。
- fail-openを選んだチームでは、確認の失敗が実行を止めない。その選択は記録に残るが、事故を防ぐものではない。

## Revisit conditions

- E-80.1で、書かれた手順だけでは初期導入が完了しない、または作者の補助が常に必要だという結果が出た。
- E-80.2、E-80.3で、Gatewayの責務だけでは食い違いの保持や第三者の検証が成立しないことが分かった。
- 参照エージェントを外部に置く構成では、チームが実用的に使えないというEvidenceが得られた。
- 全社の統治部門から先に導入したいという、実際の需要が確認された。
- ADR-0027、0029、0030が変更された。

## Evidence

現在のEvidenceは、Design Evidenceと、CLI最小版に限ったScoped Executable Evidenceです。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

- Design Evidence: ISSUE-000080、`plan/SEI_FUTURE_POSITIONING_2026-10.md`、ADR-0027、0028、0029、0030。
- Executable Evidence: `sei` CLIの最小版(`init`、`add`、`resume`、`verify`、`export`)、`mcp`(AIツール接続のprofile)を実装し、Go 1.25.14の実際のgo.modで`runtime/go`全体のtestがPASSした。範囲と留保は`runtime/SEI_CLI_FIRST_SLICE_EVIDENCE_2026-10-06.md`に記録している。実行前の確認(`sei gate check`)は、既存のDecision Memoryを読んで確認する機能として実装した。Decision Memoryは変更しない。確認のたびに運用ログ(`gate-checks.jsonl`)へ追記するが、その運用ログは判断の記録の一部ではない。結果のContract化とAction Intentそのものの記録型は、ADR-0034(Proposed)で扱う。
- Adoption / Outcome Evidence: なし。

このADRがAcceptedになる条件は、最小のバイナリ実装とE-80.1の結果を踏まえて、プロダクト責任者が確認することです。
