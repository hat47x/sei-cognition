# ISSUE-000088: 基盤モデルの進歩に対する頑健さの台帳を維持する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0001, ADR-0018, ADR-0021, ADR-0023, ADR-0035**  
Updated: 2026-09-27

## Goal

基盤モデルが強くなると、SEIの仕組みの一部は不要になり、一部はかえって重要になります。本Issueでは、その見極めを場当たりにせず、**各仕組みがなぜ必要なのか、何が起きたら縮小するのかを先に書いた台帳**を作り、維持します。

台帳は次の七つを扱います（評価記録のR1〜R7）。

1. **正当化の札** — 各仕組みが、制度、容量、経済・物理のどれに由来するか。
2. **縮小の条件（tripwire）** — 何が観測されたら、その仕組みを縮小または再設計するか。
3. **モデルの世代ごとの再評価** — 新しい世代の基盤モデルが出たら、比較評価とE1〜E8を再実行し、`historical PASS != current PASS`として記録する。これをADR-0001の「動く地平線」を実際に動かすきっかけにする。
4. **プロバイダ離脱訓練** — 主なLLMや記憶の提供元を切り替え、失われた意味を数える。V4のOperational Evidenceの候補にする。
5. **承認の実質の観測** — 提案から決定までの時間、修正の有無、却下率などを、形だけの承認を見つける観測として持つ。
6. **Observationの出所の区分** — 人の観察、センサー、AIの生成、AIの要約、外部資料（C2PAのmanifestがあればその参照）を分ける。
7. **長く読めることと暗号の更新** — JSON、JCS、人向けの投影で書き出せること、ハッシュのProfileに版を持たせ、古い束縛を再検証した記録を残すこと。

完了とは台帳を一度作ることではなく、**台帳を維持する手順が定まり、最初の再評価と最初の離脱訓練の設計が確かめられた状態**を指します。

## Background

### 確認済みの事実

- `product/principles/SEI_PRODUCT_PRINCIPLES.md` §16は評価時点から10〜50倍先を見ることを、§18はcode / prompt sheddingを前提とすることを定めています。ADR-0001は「動く地平線」を定めています。
- `evaluation/cognitive-workspace-comparison/README.md` §2は、「Raw ContextでもUnknown / Conflict / Decision basisが同程度に保持されるなら、Workspaceやstaged routingを縮小・再設計する」という反証の条件を持っています。これを仕組み全体へ広げるのが、本Issueの台帳です。
- 5つのSemantic Contractは、すべて`v1alpha1`です。Representation Profileは`sei.jcs+sha256/v1alpha1`と`sei.raw-bytes+sha256/v1alpha1`です（ADR-0023）。

### 観測された事例 — 外部リポジトリの履歴の書き換え（2026-09-27に記録）

ISSUE-000058（E3a）では、CSWの日本語版`weave` Skillを次のように固定しました。

- repository: `hat47x/cultural-substrate-weaving`
- commit: `aa3651f3460a6db7dc70bd848f93b600f149ffe8`
- path: `plugins/cultural-substrate-weaving-ja/skills/weave/SKILL.md`
- Git blob SHA-1: `4d1cd77a3561c4da58bc030936f28ae2386a81ce`
- 検証済みのbytesのSHA-256も記録

2026-09-10の観測（`evaluation/failure-behavior/actual_provider_missing_revision_observation_20260910.json`）の時点では、このcommitはGitHub APIから取得できました。

CSW側の報告では、2026-09-24頃にCSWが履歴を書き換え（`backup-before-author-rewrite-20260924`というtagが残されています）、このcommitはどのrefからも到達できなくなりました。一方、固定したblobはCSWの履歴に残っており、`af7aa55`で追加された形で見つかります。2026-09-27に手元のCSWのcloneで、commitが存在しないことと、blobが`af7aa55`の履歴に残っていることを確かめました（読み取りのみ）。

つまり、**commitの識別子による束縛は切れ、内容（blob）による束縛は生き残りました。** SEIのE3aの記録はcommitに加えてblobの識別子とSHA-256を保持していたため、設計としては持ちこたえています。これはSEIのContractの失敗ではなく、Design上の観測です。記録済みのEvidenceのファイルそのものは変更しません。

この事例から、台帳に次の規則を置きます。

- 外部リポジトリへのExact Bindingは、commitやrevisionの識別子に**加えて**内容のdigestを持つ。commitの識別子の代わりにはしない。
- 過去の束縛は定期的に再検証し、その結果を当時のPASSとは別の記録として残す。

### 現時点の推論

- 制度に由来する仕組み（Recommendation ≠ Decision ≠ Authority、当時の根拠とExact Binding、UnknownとConflictの保持、Revisionの完全性、Providerからの独立、限定された共有）は、モデルが強くなっても残るか、強まる。
- 容量を補う仕組み（Resume projectionの生成、型付きの閉選択、文脈の圧縮）は、薄くなる。
- 経済・物理に由来する仕組み（SACS、コストのためのルーティング、Locality-first）は、一部が残る。
- 2026-09時点の駆動力（文脈長の横ばい、ベンダー内蔵の記憶、利用者所有の記憶の標準化、自律エージェント、ルーティングの基盤化、規制の要請、合成コンテンツ等）は、評価記録の§10.1にまとめている。

### Unknown / Conflict

- 次の世代のモデルが、いつ、どの程度の変化をもたらすか。
- 承認の実質の観測が、個人の監視として受け取られないか。
- 離脱訓練で「失われた意味」を、どの単位で数えるのが妥当か。

## Questions

1. 評価記録の§10.2に挙げた仕組みの札と向きは、妥当か。見落とした仕組みはないか。
2. 各仕組みの縮小の条件を、観測できる形で書けるか。
3. モデルの世代ごとの再評価は、何をきっかけに、何を再実行すればよいか。
4. プロバイダ離脱訓練で、何を切り替え、何を数えれば、V4のOperational Evidenceの候補として意味を持つか。
5. 承認の実質を、個人の評価や監視にせずに観測できるか。
6. Observationの出所の区分は、既存のProvenanceの参照で表せるか。新しい型が要るか。
7. ハッシュのProfileを更新するとき、古い束縛の再検証をどう記録すればよいか。

## Constraints

- 新しいValue Axis、Universal型、Stable Requirementを追加しない。台帳は計画の資料であり、規範ではない。
- Contract versionを変えない。安定化の経路は`contracts/CONTRACT_CATALOG.md`の提案節に留め、ADR-0021の手続きに従う。
- 過去のPASSを現在のPASSとして扱わない。記録済みのEvidenceのファイルを書き換えない。
- 離脱訓練で、秘密や認証情報をEvidenceへ残さない。
- 承認の実質の観測を、KPIや個人の評価にしない。集計の粒度で扱い、個人を特定する記録を作らない。
- 規制への言及を、適合の保証として書かない。
- 評価の都合で、制度に由来する仕組みを縮小しない。

## 台帳の初期内容

評価記録（`product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md` §10.2）を出発点とします。縮小の条件は、まだ草案です。

| 仕組み | 札 | 向き | 扱い | 縮小の条件（草案） |
|---|---|---|---|---|
| Recommendation ≠ Decision ≠ Authority | 制度 | ↑ | 核 | 縮小しない。意味の区別を保てない事例が出た場合は、強化を検討する |
| 当時の根拠とExact Binding | 制度 | ↑ | 核 | 縮小しない。外部リポジトリへの束縛は、識別子に加えて内容のdigestを持つ（上の観測事例） |
| UnknownとConflictの保持 | 制度 | ↑ | 核 | 縮小しない |
| Revisionの完全性（V3） | 制度 | ↑ | 核 | 縮小しない |
| Providerからの独立（V4） | 制度・経済 | ↑ | 核 | 縮小しない。離脱訓練で失われる意味が続けてゼロなら、訓練の頻度を下げる |
| 限定された共有とSelective Disclosure | 制度・法 | ↑ | 核 | 縮小しない |
| Progressive Explicitness | 人の注意は有限 | ↑ | 核の運用原則 | 縮小しない。入力の負担が価値を上回る場合は、既定の明示度を下げる |
| Cognitive Workspace | 容量 → 開示範囲 | → | 正当化を「何を見せてよいか」へ移す | Raw ContextでもUnknown / Conflict / Decision basisが同程度に保たれ、開示範囲を制御する必要もない場合 |
| 人とAIが読めること（V6） | AIの側は容量、人の側は制度 | → | AI向けの工夫は薄くする | AI向けの整形がなくても、AIの読み取りの誤りが増えない場合 |
| Locality-first、常時の軽量認知 | 経済・物理・法 | → | Profile・Realization | 端末上の処理と中央の処理で、コスト、遅延、プライバシーの差が消えた場合 |
| Resume projectionの生成 | 容量・利便 | ↓ | 生成はProviderへ。混ぜてはいけないものの規則はSEIに残す | Providerが生成した要約でも、当時の根拠と判断後の情報を混ぜない場合 |
| SACS（安価な想起） | 経済 | ↓ | Realization | 汎用モデルでの想起のコストと遅延が、SACSと同等以下になった場合 |
| コスト最適化のルーティング | 経済 | ↓ | Realization。選択の判断は核へ記録する | プラットフォームの機能が同等以上の選択を提供し、選択の理由をSEIへ記録できる場合 |
| 型付きの閉選択 | 容量 | ↓ | Realization | 小型モデルでも、自由形式の出力で意味の種類を誤らなくなった場合 |

## Required scenarios / experiments

### E83.1 — 台帳の初期化

上の表を、各仕組みの正本の文書（Principles、Architecture、Evaluation）と照合し、札、向き、縮小の条件を確かめます。`SEI_PRODUCT_PRINCIPLES.md` §18と`evaluation/cognitive-workspace-comparison/README.md` §2に、台帳への入口を置きます（2026-09-27に提案として追記済み）。

### E83.2 — モデルの世代ごとの再評価の手順

新しい世代の基盤モデルが利用できるようになったとき、次を再実行する手順を定めます。

- Cognitive Workspaceの比較（A: Raw Context、B: Cognitive Workspace、C: Staged Route）
- ISSUE-000073のE1〜E8（Go 1.25.xの環境が必要）
- 必要に応じて、Cognitive Methodの成果品質のreview

結果は、当時のPASSを上書きせず、新しい記録として残します。

```text
historical PASS != current PASS
```

### E83.3 — プロバイダ離脱訓練の設計

主なLLMまたは記憶の提供元を切り替え、切り替えの前後で次を数えます。

- 過去のDecisionの根拠を、切り替え後も読み直せたか。
- Recommendation、Decision、Authorityの区別が保たれたか。
- 未解決と見直しの条件が保たれたか。
- 失われた意味の数と、その種類。

repositoryのfixtureで行う訓練はExecutable Evidenceに留まります。実運用の環境で行い、その結果を観測した場合に限り、V4のOperational Evidenceの候補になります。2026-09-27時点では、どちらも**未取得**です。

### E83.4 — 承認の実質の観測

ISSUE-000073のH1 / H2や、ISSUE-000078のdogfoodで、次を集計の粒度で観測できるかを確かめます。

- 提案から決定までの時間
- 決定の前に提案を修正したか
- 提案を却下した割合

これは、自動化バイアス（EU AI Act 14条4項(b)で注意が求められているもの）への備えを考える材料です。SEIが規制への適合を保証するものではありません。

### E83.5 — 出所の区分

Observationの出所を、人の観察、センサー、AIの生成、AIの要約、外部資料（C2PAのmanifestの参照）に分けて記録できるかを、既存のProvenanceの参照で試します。C2PAとの対応は`contracts/EXTERNAL_STANDARD_MAPPING.md`で扱います。

### E83.6 — 長く読めることとハッシュの更新

`contracts/CONTRACT_CATALOG.md`の提案節に沿って、次を確かめます。

- 記録をJSON、JCS、人向けの投影で書き出し、Contractを知らない読み手でも意味を追えるか。
- 新しいハッシュ方式のProfileを加えるとき、古い束縛を再検証した記録（いつ、誰が、どのProfileで、結果はどうだったか）を残せるか。
- 外部リポジトリへの束縛を定期的に再検証し、commitが到達できなくなった場合でも、内容のdigestで照合できるか（上の観測事例）。

読み方:

- **PASS** — 手順が定まり、少なくとも一度、実際に実行して記録を残せた。
- **FAIL** — 手順を実行した結果、意味の損失や再検証の不能が見つかった。
- **NOT_VERIFIED** — 手順は草案だが、まだ実行していない。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## Deliverables

- 頑健さの台帳（まず本Issueの「台帳の初期内容」として維持し、必要になれば評価資料として独立させる）
- モデルの世代ごとの再評価の手順
- プロバイダ離脱訓練の手順と、最初の実施記録
- 承認の実質の観測の手順
- `contracts/CONTRACT_CATALOG.md`の提案節の更新（安定化の経路、長期の互換性、ハッシュの更新手順）
- 外部リポジトリへの束縛の再検証の記録

## Resolution

次をすべて満たしたとき、Resolved候補とします。

1. 台帳の初期内容を、正本の文書と照合して確かめた。
2. モデルの世代ごとの再評価の手順を定め、少なくとも一度、実行した記録がある。
3. プロバイダ離脱訓練を少なくとも一度行い、失われた意味の数と種類を記録した。実運用で行っていない場合は、Operational Evidenceとして扱わない。
4. 外部リポジトリへの束縛を少なくとも一度再検証し、その結果を当時のPASSと分けて記録した。
5. 台帳を維持する手順（いつ、誰が見直すか）が定まっている。

台帳は継続して維持するものです。ResolvedになったあともADR-0001の「動く地平線」に従って見直します。Resolvedになることは、Operational EvidenceやAdoption / Outcome Evidenceが成立したことを意味しません。

## Reopen conditions

- 新しい世代の基盤モデルで、制度に由来するとした仕組みまで薄くなることが観測された。
- 容量に由来するとした仕組みが、予想に反して重要なままであることが観測された。
- 離脱訓練で、既存の契約では防げない意味の損失が見つかった。
- 外部リポジトリの束縛で、内容のdigestでも照合できない事例が見つかった。
- ハッシュ方式の脆弱化など、Representation Profileの更新が必要になった。

## CI / verification

再評価と離脱訓練では、変更範囲に応じて、Cognitive Workspaceの比較のGo package、ISSUE-000073のcapture、Contractのconformance checkerをローカルで個別に実行します。Planの変更では`plan/scripts/check_plan_registry.py`と`plan/scripts/check_document_review_registry.py`を実行します。

2026-09-27の起票時点では、PythonとGoがない環境で作業したため、どのcheckerも実行していません。手作業での確認はISSUE-000085の「2026-09-27の検証（手作業）」に記録しています。

## Natural Japanese review

評価記録のR1〜R7、Product Principles §16 / §18、ADR-0001 / 0021 / 0023、Cognitive Workspaceの比較の反証条件、ISSUE-000058のE3aの記録と2026-09-10の観測を照合し、頑健さの台帳の初期内容と維持の手順を定めました。CSWの履歴の書き換えで、commitの束縛が切れて内容の束縛が生き残った事例を、SEIの失敗ではなくDesign上の観測として記録し、そこから導いた規則を台帳へ置いています。

内容、Constraints、読み方、完了条件を固定した後、**自然な日本語となることを最重要視して全文を再ドラフトしました。** 最後に、Goal、Questions、Constraints、Resolution条件、Evidenceの高さが変わっていないことを再監査しました。
