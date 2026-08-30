# SOZA `plan/` 運用規約

更新日: 2026-08-31  
状態: **Accepted Planning Convention**

## 1. `plan/` の役割

`plan/` は、SOZAの価値そのものを定義する場所ではありません。

ここには、`product/` と `requirements/` を前提として、**何を決める必要があるか、なぜその判断が必要か、何を調査するか、どの設計判断を採用したか**を記録します。

主に次を扱います。

- ADR（Architecture Decision Record）
- Issue（未決論点、調査、比較、反証、委任課題）
- ADR / Issueの状態と関連を管理するregistry
- 採番・検査・テンプレート等の管理補助
- 再基線化やマイルストーン編成等の計画文書

## 2. 文書の高さと配置

SOZAでは、文書を作成時期や担当者ではなく、**何を定義・決定する文書か**で分けます。

```text
product/
  ├─ value/        # なぜSOZAが存在するか、どんな価値を守るか
  ├─ vision/       # 長期的にどのような状態を目指すか
  └─ principles/   # 長期に維持する製品原則

requirements/      # product価値を満たすために必要な要求

plan/
  ├─ adr/          # 設計判断
  ├─ issue/        # 未決論点、調査、比較、委任課題
  ├─ scripts/      # 採番・検査などの管理補助
  ├─ registry.yaml # ADR / Issueの状態と関連
  └─ README.md     # 本運用規約

architecture/      # requirementsとADRを具体的な構造へ落とした設計
implementation/    # 実装
```

概念上の依存方向は、原則として次のとおりです。

```text
Product Value
  → Value Model
  → Vision / Principles
  → Value Scenarios
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture
  → Implementation / Test / Evidence
```

実装や検証から上位の仮説が誤っていると分かった場合は上位文書へ戻ります。ただし、**既存実装を温存するためだけにProduct Valueを書き換えない**ことを原則とします。

現在のactual repositoryにまだ存在しない階層は、概念図にあることだけを理由に「実体化済み」と扱いません。

## 3. ADRの役割

ADRは、SOZAに関する**設計上の判断**を残します。

ADRには、少なくとも次を含めます。

- Status
- Related Issue
- Context
- Product Value trace（重要判断では省略しない）
- Decision または Decision to make
- 選択肢と比較
- Constraints
- Consequences
- Revisit conditions
- Evidence / acceptance material
- Natural Japanese review

未決の場合は `Proposed` または `Decision Deferred` とし、判断できない理由と追加Evidenceを明示します。

「まだ決めない」という判断も、境界を固定する価値がある場合はADRにできます。ただし、単に調査不足なだけの状態を無理にADR化しません。

ADRが`Accepted`であることは、Decision boundaryがAcceptedであることを意味します。schema、fixture、runtime、production operation等まで完成したことを自動的には意味しません。

## 4. Issueの役割

Issueは、答えがまだない作業を扱います。

たとえば次を置きます。

- 調査
- 比較
- 圧力試験
- 反証
- Acceptance Scenarioの作成
- 実装前の設計精緻化
- ADRを決定可能にするための材料収集
- actual repositoryへのmaterialization
- 他のAIや担当者へ委任できる単位の課題

Issueの完了は「何かを採用した」ことを意味しません。

`Coreへ追加しない`、`現時点では決めない`、`追加Evidenceが得られるまでDeferredとする`といった結論も正当です。

Decision boundaryがADRで確定した後にschema / fixture / implementationが残る場合は、一つのIssueを曖昧にOpenし続けず、Decision IssueをResolvedとし、後続実装Issueへ分けることを検討します。

## 5. 採番

ADRは4桁固定とします。

```text
ADR-0001
ADR-0002
...
ADR-9999
```

ファイル名:

```text
plan/adr/ADR-0001-short-title.md
```

Issueは6桁固定とします。

```text
ISSUE-000001
ISSUE-000002
...
ISSUE-999999
```

ファイル名:

```text
plan/issue/ISSUE-000001-short-title.md
```

ADRとIssueは別々の番号空間です。番号が同じでも自動的な関連はありません。関連は本文と`plan/registry.yaml`で明示します。

状態を`CAND`、`PROPOSED`等の接頭辞としてIDへ埋め込みません。状態変更で恒久IDやファイル名を変えないためです。

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

独自状態を増やす場合は、既存状態では意味を表せないことを確認します。

`Blocked — reason`のように理由をStatus文字列へ埋め込むのではなく、Statusは規定値に保ち、blocked reasonやdependencyを本文へ分離します。

## 7. Product Valueから実装まで追跡する

重要なADR / Issueでは、可能な範囲で次の追跡線を明示します。

```text
Product Value / Value Model
  → Value Scenario
  → Product Requirement / NFR
  → Issue
  → ADR
  → Architecture
  → Implementation / Fixture / Test
  → Evidence
```

すべての文書へ機械的に同じ欄を要求するのではなく、Core境界、Product Boundary、高影響なDecision、Evidence claim、重要Acceptanceでは省略しません。

重要な計画判断では、少なくとも次を検討します。

- 関連するValue Model validation axis（V1〜V9）
- 関連するValue Scenarioまたは同等の具体Scenario
- 守る意味境界
- 現在のEvidence level
- 次に必要なEvidence level

`product/value/SOZA_VALUE_TRACEABILITY.md`を現行の追跡基線として参照します。

## 8. Evidence levelを混同しない

少なくとも次を区別します。

```text
Value Definition
  != Design / Requirement Coverage
  != Executable Conformance
  != Operational Evidence
  != Adoption / Outcome Evidence
```

さらに、historical / local candidateとactual GitHub repositoryのEvidenceも分けます。

たとえば、local fixtureがPASSしていてもactual repositoryにfixtureやtest toolが存在しなければ、actual repository PASSとは記録しません。productionで動作したとしても、それだけで利用者の判断が改善したというOutcome Evidenceにはしません。

IssueやADRのStatusも、Evidence levelの代用にしません。

## 9. 将来耐性の扱い

将来耐性は固定された「100倍未来」ではなく、**評価時点の現実からおおむね10〜50倍程度先を見る移動基準**として扱います。

10や50という値はbenchmark scoreではありません。現在のAIや実装制約へ過適合していないかを考えるための距離です。

この原則の設計判断は`ADR-0001`で管理します。

## 10. 文書作成の必須工程

SOZAの開発文書は、次の順序で作成・更新します。

1. **意味と目的を定める**  
   文書が何を決めるか、何を決めないかを明確にします。
2. **事実・前提・Evidenceを確認する**  
   未確認事項を確定事項として書きません。
3. **構造を作る**  
   論点、選択肢、判断、結果、未決事項を配置します。
4. **技術的一貫性を監査する**  
   Product Value、Value Scenario、Requirement、既存ADR、Architectureとの矛盾を確認します。
5. **Evidence強度を監査する**  
   historical / local / actual repository / operational / outcomeを取り違えていないか確認します。
6. **自然な日本語で全文をドラフトし直す**  
   意味・仕様・留保・Evidence強度を変えず、自然な日本語となることを最重要視して文章全体を見直します。
7. **最終意味監査を行う**  
   日本語を整えたことで技術的意味、条件、例外、強度が変わっていないかを再確認します。

**第6工程は省略しません。**

新規文書だけでなく、既存のactiveな開発文書もすべて同じ工程を順次通します。

## 11. 自然な日本語ドラフトの基準

自然な日本語に直す工程では、単なる表記統一ではなく、読み手が意味を追いやすい文章へ整えます。

優先順位は次のとおりです。

1. 意味・仕様・留保・Evidence強度を変えない。
2. 日本語として自然な語順と接続にする。
3. 不要な英単語の混在を減らす。ただし技術概念の識別に必要な用語は保持する。
4. 名詞を連結しすぎず、必要に応じて述語を補う。
5. 同じ概念を文書内で別の言葉へ揺らしすぎない。
6. `!=` 等の短い境界式は、本文の自然な説明と併用する。
7. 生成AI向けの断片的なメモ口調を、そのまま正式文書へ残さない。
8. 曖昧さが意味上必要な箇所は、文章を滑らかにするために勝手に確定させない。

## 12. 既存文書の日本語監査

既存文書は、優先度の高い順に自然な日本語ドラフト工程へ通します。

優先順位:

1. `product/value`, `product/vision`, `product/principles`
2. `plan/adr`, `plan/issue`
3. `requirements`
4. `architecture`, `contracts`
5. `plan/rebaseline`等の報告・計画文書
6. README、補助文書

この移行作業は`ISSUE-000015`で追跡します。

## 13. `registry.yaml`

`plan/registry.yaml`は、ADR / IssueのID、ファイル、状態、関連、優先度を一覧化します。

registryは検索と検査のための台帳であり、本文より強い意味上の正本ではありません。状態や判断理由の詳細は対応文書を正とします。

本文とregistryでStatusや関連が変わった場合は、同じ変更単位で両方を更新します。

## 14. 現在の最優先planning queue

2026-08-31時点では、次を優先します。

1. `ISSUE-000024` — Product Value / Value ScenarioからRequirement / NFR / Acceptanceへの追跡基線
2. `ISSUE-000015` — active開発文書の自然な日本語監査継続
3. `ISSUE-000022` — actual repository baseline materializationとEvidence claim再整合
4. `ISSUE-000009` — Portable Exact Binding verification。ISSUE-000022のactual実体化待ち
5. `ISSUE-000025` — Provider-neutral Capability Observation contract / fixture。ISSUE-000022待ち
6. `ISSUE-000021` — 原文Evidenceを取得できるまでDeferred

この順序はProduct ontologyでも固定ロードマップでもありません。Product Valueから見た現在のgap、依存関係、Evidence不足に応じて見直します。

## 15. 自然な日本語ドラフト

Product Value、Value Scenario、Evidence level、現行Issue状態との整合を確認した後、運用上の意味と強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
