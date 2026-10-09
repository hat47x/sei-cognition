# SEIの全体構成

更新日: 2026-10-10  
状態: **現行の設計基準（作業再開を優先する対話用作業集合の設計を反映）。本文は現行の設計基準である。** 一方、§2で示す`SEI_REFERENCE_ARCHITECTURE.md`の§20.1（境界B1〜B8）は提案であり、§2・§10のADR-0035（Proposed）への参照も提案として扱う。これらの採否は未決である。提案は現行の設計基準の一部ではない。

## 1. このディレクトリの役割

`architecture/`は、現行の製品価値、要求、採用済みADRを踏まえ、SEIの構造と責務の境界、構成要素の関係を説明します。

新しい設計判断を、この文書の本文だけで確定しません。重要な判断が必要になった場合は、課題またはADRに戻して扱います。

```text
Product Value
  → Requirement / Candidate Requirement
  → ADR
  → Architecture
  → Contract / Representation Profile
  → Runtime / Provider Adapter / Test / Evidence
```

```text
Architecture description != Architecture Decision Record
Architecture concern != runtime component
Deployment component != semantic concern
```

## 2. 正本となる文書

```text
architecture/
  README.md
  SEI_REFERENCE_ARCHITECTURE.md
  SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md
  SEI_DEPLOYMENT_ARCHITECTURE.md
  SEI_PRODUCT_ACCESS_ARCHITECTURE.md
  IMPLEMENTATION_LANGUAGE_POLICY.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

- `SEI_REFERENCE_ARCHITECTURE.md` — 現行のSEI全体を示す参照構成。§20.1に、外部の強い仕組みとの境界B1〜B8の提案を置いている。これはADR-0035（Proposed）の影響範囲にある提案節であり、採否は未決である。§20.1は現行の基準（baseline）ではない。
- `SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md` — ISSUE-000073の作業再開を優先する製品機能について、意味の正本・派生情報・一時情報・外部状態の管理主体、作業集合、再開時の表示、AIの提案、意味変更の確定、古い状態からの書き込みや部分的な確定を扱う境界を定義する。
- `SEI_DEPLOYMENT_ARCHITECTURE.md` — ADR-0029に基づくLocal Single-Node Packageの構成要素の配置、永続化、保存・再開、書き出し・取り込みの境界。
- `SEI_PRODUCT_ACCESS_ARCHITECTURE.md` — ADR-0030に基づく認証、識別情報の対応付け、製品利用権限、保護された正本アクセス、選択的な情報開示の配置。
- `IMPLEMENTATION_LANGUAGE_POLICY.md` — ADR-0027に基づく本番向け実行環境と研究・外部実装の言語上の境界。
- `TRACEABILITY.md` — 製品価値、要求、ADR、設計上の関心領域、現在の実行可能な成果物を対応付けるための索引。
- `history/HISTORICAL_ARCHITECTURE_MAPPING.md` — 過去のM48・M49・M50などと現行の設計との対応。

扱う設計上の関心が大きくなった場合は、文書を分割できます。重要な判断はADRの識別子で追跡するため、構成文書だけの連番体系は設けません。

## 3. 全体構成の読み方

SEIの全体構成は、固定された処理順序やサービスの配置図ではありません。**意味を失わないために分けた関心領域と、その境界の関係**を示します。

たとえば判断の記録（Decision Memory）、能力（Capability）、認知方式（Cognitive Method）、永続化（Persistence）、製品の利用権限（Product Access）は重要な関心領域ですが、それぞれを独立したマイクロサービスやGoのパッケージにすることを意味しません。

同様に、図中の矢印は原則として固定された作業手順を表しません。情報が参照・派生・判断材料・実行境界として関係し得ることを示します。

単一端末への配備（Local Single-Node Deployment）では、複数の論理上の構成要素を一つのGoプロセスで動かせます。これは配布や起動を小さく始めるための配置です。同じプロセスで動くという理由だけで、利用者とのやり取り、意味の実行、永続化、外部提供元との連携、製品の利用権限を、一つの関心領域にまとめることはしません。

ISSUE-000073では、この原則を利用者とのやり取りに適用します。作業中の情報の集合（working set）、再開時の要約（Resume Brief）、意味を変更する計画（semantic change plan）、状態を識別するトークン（snapshot token）などは、操作体験やアプリケーションの仕組みとして重要です。ただし、存在するだけで汎用の意味上の実体になるわけではありません。

## 4. 現行の構成で守る上位の境界

少なくとも次を弱めません。

```text
Observation != Interpretation / Hypothesis
Recommendation != Decision
Decision != Authority
Authority != Action Intent
Action Intent != Execution
Execution != Business Outcome
Capability != Provider
Capability Definition != Capability Observation
Provider state != Capability interpretation
Matching != Decision
Pattern != Cognitive Method
Method Application != Assurance
Logical Reference != Exact Historical Binding
Semantic Contract != Representation Profile != verifier implementation
not observed != unavailable
binding not_verified != binding failed
Projection != Canonical Semantic Authority
runtime executable != canonical semantic data
filesystem locator != Logical Reference
Storage migration != Semantic Revision
authentication identity != Bounded Subject
Bounded Subject != product access permission
product access permission != semantic Responsibility / Authority
SEI product access authorization != external execution authorization
withheld != unknown
working-set membership != semantic relation
AI suggestion != canonical commit
concurrency version != Semantic Revision
post-decision observation != historical decision basis
```

これらの境界を変更する必要が生じた場合は、構成文書だけを書き換えず、対応する要求やADRを再審査します。

## 5. 現在の実装との関係

現在のリポジトリには設計全体を実現した完成版はありませんが、次の限定された実体があります。

- 現行の意味の契約（Semantic Contract）群と試験用データ（fixture）
- JCSとSHA-256、元のバイト列とSHA-256を組み合わせる表現規則（Representation Profile）
- Goによる意味の実行環境
- Goによる外部提供元との接続部の一部
- Goによる製品利用の流れを一貫して確かめる試験環境
- Goによる利用者操作の参照検証
- Goによる配布と永続化の参照検証
- Goによる利用権限と共同作業の参照検証
- ローカル参照パッケージの公開用成果物
- PythonによるV6・V7の用途別表現の評価など、評価・開発の補助

これらは設計の一部の境界を確かめた、対象を限定した実行検証根拠（Scoped Executable Evidence）です。設計上の関心領域を実行時の構成要素に一対一で対応させたことや、全体構成の実装を完了したことは意味しません。

`SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`は2026年9月18日時点では設計上の根拠（Design Evidence）です。作業集合の解決、再開時の表示、意味変更の計画、確定処理の調整、外部に渡す文脈の計画などについて、試作段階の実行検証根拠をISSUE-000073で確認します。

ADR-0027に従い、SEI自身が管理する本番向け実行環境の標準言語はGoとします。ただし、意味の契約や、外部で動く認知方式・能力の提供元までGoに固定するものではありません。詳細は`IMPLEMENTATION_LANGUAGE_POLICY.md`を参照します。

ADR-0029では、最初の配布・配備形態としてLocal Single-Node Packageを採用しました。Goの単一実行ファイルとファイルシステムは初期実装の利点として利用しますが、実行ファイルやファイル配置に意味を確定する権限は持たせません。詳細は`SEI_DEPLOYMENT_ARCHITECTURE.md`を参照します。

ADR-0030では、認証に用いる識別情報、権限を扱う範囲内の主体（Bounded Subject）、製品の利用許可、意味上の責任・権限を分離しました。製品の利用範囲、識別情報の対応付け、利用規則、開示する情報の表示は製品の安全管理を担う部分に配置します。テナントや作業領域、権限名の一覧を汎用の中核へ取り込むことはしません。詳細は`SEI_PRODUCT_ACCESS_ARCHITECTURE.md`を参照します。

## 6. 検証根拠の扱い

製品価値の定義に従い、検証根拠を次の5段階に分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

構成設計の本文と対応関係の索引は、設計上の根拠（Design Evidence）です。

現行の契約の試験用データ、表現規則の検証器、意味の実行環境、提供元との接続部、製品利用の試験環境、利用者操作・配布・永続化・利用権限の各参照検証には、対象範囲を限定した実行検証根拠があります。

```text
Architecture exists
  != Architecture executable coverage complete
  != Product Release proven
  != production UX proven
  != Operational Evidence
  != user-value realization
```

ISSUE-000073で作業再開を優先する設計が成立しても、正本の情報だけによる再開、AIの提案の修正、障害の注入、古い状態による書き込みの防止、実際の利用者にとっての使いやすさが検証済みになるわけではありません。

配布の参照検証やローカル参照パッケージの確認が通っても、停電時の永続性、本番データベースの移行、正式な対応環境の一覧を保証するものではありません。

製品利用権限の参照検証が通っても、本番でのOIDC・IAM連携、正式なRBAC・ABAC、認証情報の管理周期、チーム利用時の安全性、本番での選択的な情報開示までは検証できていません。

Goの実行環境に実行検証根拠があっても、Goがあらゆる将来要件で最適であることは意味しません。言語方針は、配布・配備・運用上の根拠を通じて継続的に確かめます。

詳細は`../product/value/SEI_VALUE_ACCEPTANCE.md`と`TRACEABILITY.md`を参照します。

## 7. 過去の設計候補の扱い

ライブラリや履歴には、第1段階で検討した構成設計の文書が多数残っています。

現行の設計基準では、過去の資料から意味の境界、反例、採用しなかった理由、受け入れ判断の論点、設計の経緯を再利用できます。一方、古いパッケージ・フィールド・スキーマの形、過去のローカル試験の合格、旧マイルストーンの識別子は、現行の設計へ自動的には引き継ぎません。

JCS・SHA-256・JSONなど、過去に選んだ実装方式も、それだけを理由に再採用しません。現行の採用判断では、採用済みADRと実際の検証根拠を確認します。

同様に、Local Single-Node Package、ファイルシステムへの永続化、製品利用の範囲、権限名の一覧、利用者の作業集合なども、初期構成や試作で使うという理由だけで汎用の中核へ固定しません。

詳細は`history/HISTORICAL_ARCHITECTURE_MAPPING.md`を参照します。

## 8. 契約と表現規則との境界

全体構成の文書では、意味の構造と構成要素を配置する理由を説明します。

複数の実装・提供元・保存方式・版をまたいで検証できる取り決めが必要な場合は、`contracts/`に意味の契約として分離します。バイト列、正規化、ダイジェストなどの表現規則は、意味の契約とは別の表現規則（Representation Profile）で定めます。

```text
Architecture explains structure and boundaries
Contract defines portable / verifiable semantic agreement
Representation Profile defines bytes / canonicalization / digest agreement
Implementation language defines one realization choice
Deployment profile defines one component placement
Product Interaction working set defines one product-level navigation / projection concern
```

契約や表現規則の種類を増やすこと自体は目的ではありません。

ISSUE-000073の`semantic change plan`や状態を識別するトークンについても、複数の実装間で持ち運べる取り決めが必要だと検証根拠から確認できるまでは、契約として固定しません。

## 9. 文書の品質

構成設計の文書は、内容と構造を固めた後、意味、規則の強さ、例外、未決事項を変えず、**自然な日本語で全文を推敲**します。

その後、中核・表現規則・提供元・接続部・用途別表現・永続化・利用権限・利用者の作業集合などの境界や、検証根拠の強さが変わっていないか最終確認します。

## 10. 関連文書

- `../product/value/SEI_PRODUCT_VALUE.md`
- `../product/value/SEI_VALUE_MODEL.md`
- `../product/value/SEI_VALUE_ACCEPTANCE.md`
- `../product/value/SEI_VALUE_TRACEABILITY.md`
- `../product/interaction/SEI_PRODUCT_INTERACTION.md`
- `../product/interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md`
- `../product/packaging/SEI_PRODUCT_PACKAGING.md`
- `../product/security/SEI_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`
- `../requirements/PRODUCT_REQUIREMENTS.md`
- `../requirements/ACCEPTANCE_SCENARIOS.md`
- `SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`
- `SEI_DEPLOYMENT_ARCHITECTURE.md`
- `SEI_PRODUCT_ACCESS_ARCHITECTURE.md`
- `TRACEABILITY.md`
- `IMPLEMENTATION_LANGUAGE_POLICY.md`
- `../plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`
- `../plan/adr/ADR-0027-go-as-standard-production-runtime-language.md`
- `../plan/adr/ADR-0028-product-interaction-canonical-operation-boundary.md`
- `../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../plan/adr/ADR-0030-product-access-control-separation.md`
- `../plan/adr/ADR-0035-family-integration-apex-and-control-meaning-boundary.md` — 提案（ADR-0035, Proposed）。採否は未決であり、現行の基準ではない。

## 11. 日本語の推敲記録

2026-09-11時点のProduct Value、Requirements、Accepted ADR、Semantic Contract / Representation Profile、Go semantic runtime、Provider Adapter、Product Interaction probe、Packaging / Persistence、Product Access、Local Reference Package、ISSUE-000073を参照して、Architectureの入口の記述を確認した。

新しいInteraction Working-Set Architectureをcurrent canonical fileとして登録し、working set / Resume Brief等を製品設計上の重要な関心として扱いつつUniversal Coreへ昇格させない境界を追加した。また、AI suggestionとcanonical commit、concurrency versionとSemantic Revision、post-decision Observationとhistorical basisの非同一性をArchitecture入口でも読めるようにした。

2026-10-10の変更では、次を行った。

- 更新日を2026-09-11から2026-10-10に改めた。
- 状態行を、本文が基準版であることと、§2・§10のADR-0035（Proposed）への参照が提案であることを分けて書く形に改めた。
- §2の`SEI_REFERENCE_ARCHITECTURE.md`の説明で、§20.1のB1〜B8を提案として示し、§20.1が現行の基準ではないことを明記した。
- §5の`SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`に関する日付を、2026年9月11日から9月18日に改めた（参照先の更新日に合わせた）。
- §10に`ADR-0027`と`ADR-0035`のパスを加えた。
- §11の2026-09-11段落の文言を、main側の原文に戻した。
- §11で、監査の実施を述べていた段落を削除した。