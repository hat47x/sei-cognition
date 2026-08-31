# SOZA `plan/` 運用規約

更新日: 2026-08-31  
状態: **Accepted Planning Convention**

## 1. `plan/`の役割

`plan/`は、SOZAの価値そのものを定義する場所ではありません。

`product/`と`requirements/`を前提として、**何を決める必要があるか、なぜその判断が必要か、何を調査するか、どの設計判断を採用したか**を記録します。

主に次を扱います。

- ADR（Architecture Decision Record）
- Issue（未決論点、調査、比較、反証、委任課題）
- ADR / Issueの状態と関連を管理するregistry
- 採番・検査・文書監査等の管理補助
- KJ統合や再基線化等、設計判断へ至る思考・報告資料

## 2. 文書の高さと配置

SOZAでは、文書を作成時期や担当者ではなく、**何を定義・決定する文書か**で分けます。

```text
product/
  ├─ value/        # なぜSOZAが存在するか、何を守り、どう価値を評価するか
  ├─ vision/       # 長期的にどのような利用状態を目指すか
  └─ principles/   # 下位設計で反復して適用する製品原則

requirements/      # Product Valueを満たすために必要な要求とScenario

plan/
  ├─ adr/          # 設計判断
  ├─ issue/        # 未決論点、調査、比較、委任課題
  ├─ kj/           # 設計統合・思考記録
  ├─ scripts/      # 採番・検査などの管理補助
  ├─ registry.yaml # ADR / Issueの状態と関連
  └─ document_review_registry.yaml # 文書監査の進捗台帳

architecture/      # RequirementsとADRを構造・境界へ落としたcurrent design view
contracts/         # 相互運用・検証が必要な意味契約とRepresentation Profile
runtime/           # Contractを実装する交換可能なruntime realization
fixtures/          # Executable Evidenceの入力・境界例
tools/             # checker / probe等の検証補助
```

`product/value/`では、少なくとも次を分けます。

- Product Value — なぜ存在するか、何を中核価値とするか
- Value Model — 価値の優先関係、V1〜V8、Core境界、失敗条件
- Value Acceptance — V1〜V8を満たしたと主張するためのEvidence境界
- Value Traceability — 上位価値からcurrent下位設計・Evidence gapへ戻る索引

概念上の依存方向は、おおむね次のとおりです。

```text
Product Value
  → Requirements
  → Issue / ADR
  → Architecture
  → Contract / Representation Profile
  → Runtime / Provider Adapter / Fixture / Test
  → Evidence
```

下位の実装・検証から上位仮説への反証が得られた場合は上位文書へ戻ります。ただし、**既存実装を温存するためだけにProduct Valueを書き換えません。**

## 3. ADRの役割

ADRは、SOZAに関する**設計上の判断**を残します。

少なくとも、必要に応じて次を含めます。

- Status
- Related Issue
- Context
- DecisionまたはDecision to make
- 選択肢と比較
- Constraints
- Consequences
- Revisit conditions
- Evidence / acceptance material

Product Valueが主な判断根拠となる場合は、V1〜V8のうち実際に関係する軸を示します。8軸すべてを形式的に付ける必要はありません。

未決の場合は`Proposed`または`Decision Deferred`とし、判断できない理由と追加Evidenceを明示します。「まだ決めない」こと自体が境界を固定する場合はADRにできますが、単なる調査不足を無理にADR化しません。

## 4. Issueの役割

Issueは、調査・比較・反証・実体化等の**作業単位**を扱います。

たとえば次を置きます。

- 調査・比較・pressure test
- Acceptance Scenarioの作成
- 実装前の設計精緻化
- ADRを決定可能にする材料収集
- schema / fixture / runtime等の実体化
- 他のAIや担当者へ委任できる課題

Issueの完了は「何かを採用した」ことを意味しません。`Coreへ追加しない`、`Deferredとする`、`調査の結果変更不要`という結論も正当です。

設計判断が確定した一方で実体化が残る場合は、設計Issueを無理にOpenのまま維持せず、**設計IssueをResolvedにし、実装・検証を別Issueへ分離**できます。何が未決で、何が未実装なのかを混同しないためです。

## 5. 採番

ADRは4桁固定です。

```text
ADR-0001 ... ADR-9999
```

ファイル名は`plan/adr/ADR-0001-short-title.md`形式とします。

Issueは6桁固定です。

```text
ISSUE-000001 ... ISSUE-999999
```

ファイル名は`plan/issue/ISSUE-000001-short-title.md`形式とします。

ADRとIssueは別々の番号空間です。同じ番号でも自動的な関連はなく、本文と`plan/registry.yaml`で明示します。

状態をIDへ埋め込みません。状態変更で恒久IDやファイル名を変えないためです。

## 6. 推奨状態

ADR:

- `Proposed`
- `Decision Deferred`
- `Accepted`
- `Rejected`
- `Superseded`
- `Deprecated`

Issue:

- `Open`
- `In Progress`
- `Blocked`
- `Resolved`
- `Deferred`
- `Closed — No Change`

独自状態を増やす場合は、既存状態では意味を表せないことを先に確認します。

## 7. Product ValueからEvidenceまでの追跡

重要なADR / Issueでは、必要な範囲で次の線を辿れるようにします。

```text
Product Value
  → Value Model V1〜V8
  → Value Acceptance
  → Requirement / Acceptance Scenario
  → Issue / ADR
  → Architecture
  → Contract / Representation Profile
  → Runtime / Provider Adapter / Fixture / Test
  → Evidence
```

### 7.1 V1〜V8

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence

関係しない軸を形式的に付けると追跡の意味が薄れるため、判断に効く軸を示します。

### 7.2 Evidenceの高さ

`SOZA_VALUE_ACCEPTANCE.md`に従い、次の5段階を区別します。

1. Design Evidence
2. Executable Evidence
3. Release Evidence
4. Operational Evidence
5. Adoption / Outcome Evidence

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

設計文書の完成をactual repositoryのPASSとは呼びません。fixtureやCIがPASSしたことをrelease readinessとも呼びません。本番で安定して動作したことだけから、利用者・組織へProduct Valueが届いたとも判断しません。

IssueのAcceptanceは、必要に応じて次の高さへ分けます。

```text
Semantic / Design Acceptance
Executable Acceptance
Release Acceptance
Operational Acceptance
Adoption / Outcome Acceptance
```

すべてのIssueへ5欄を機械的に要求するのではなく、達成主張を誤読しやすい場合に明示します。

## 8. 将来耐性

将来耐性は固定された「100倍未来」ではなく、**評価時点の現実からおおむね10〜50倍程度先を見る移動基準**として扱います。

10や50はbenchmark scoreではありません。現在のAIや実装制約へ過適合していないかを考えるための距離です。詳細はADR-0001を正とします。

## 9. 文書作成の必須工程

SOZAの開発文書は、次の順序で作成・更新します。

1. **意味と目的を定める。**
2. **事実・前提・Evidenceを確認する。**
3. **構造を作る。**
4. **技術的一貫性を監査する。**
5. **自然な日本語となることを最重要視して全文をドラフトし直す。**
6. **再ドラフトによって意味・仕様・留保・Evidence強度が変わっていないか最終監査する。**

第5工程は省略しません。新規文書だけでなく、既存開発文書もISSUE-000015と`plan/document_review_registry.yaml`で順次同じ工程へ通します。

## 10. 自然な日本語ドラフトの基準

優先順位は次のとおりです。

1. 意味・仕様・留保・Evidence強度を変えない。
2. 日本語として自然な語順と接続にする。
3. 不要な英単語の混在を減らす。ただし識別に必要な技術用語は保持する。
4. 名詞を連結しすぎず、必要に応じて述語を補う。
5. 同じ概念を文書内で不用意に別名へ揺らさない。
6. `!=`等の境界式には、重要な箇所で自然な日本語の説明も添える。
7. 生成AI向けの断片的な作業メモを正式文書へ残さない。
8. 意味上必要な曖昧さを、読みやすさのために勝手に確定させない。

## 11. 既存文書の監査

既存文書の監査状態は`plan/document_review_registry.yaml`を管理入口とし、ISSUE-000015で完了条件を追跡します。

監査順は原則として次のとおりです。

1. Product文書
2. ADR / Issue
3. Requirements
4. Architecture / Contracts
5. Runtime / Fixture / Toolの説明文書
6. KJ統合・historical mapping・報告文書
7. Template等の補助文書

原文そのものがEvidenceであるhistorical資料や固定fixtureは、自然な日本語化を理由に改変しません。

## 12. `registry.yaml`

`plan/registry.yaml`はADR / IssueのID、ファイル、状態、関連、優先度を一覧化する台帳です。検索と機械検査のための補助であり、判断理由の意味上の正本は各ADR / Issue本文です。

IssueまたはADR本文のStatusを変更した場合は、同じ作業単位でregistryも更新します。本文とregistryのStatusが食い違ったまま作業を終えません。

Plan文書とregistryを同時に変更する場合は、可能な範囲でatomic commitとし、一時的な不整合によるCI failureを避けます。

## 13. CI failureの扱い

CI failureを検出した場合は、**その時点で原因を特定・修正し、successを確認してから次の作業へ進みます。**

検査を通すために意味契約やnegative caseを安易に弱めません。失敗がContract、fixture、test、tool、文書台帳のどこに由来するかを切り分け、正しい層を修正します。

## 14. Natural Japanese review

Product Value traceability、5段階Evidence、current ADR / Issue / Contract / Runtime / Provider Adapter、文書監査台帳へ戻って運用規約を再構成した。その後、採番、Status、権威関係、Evidence強度、CI handlingを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
