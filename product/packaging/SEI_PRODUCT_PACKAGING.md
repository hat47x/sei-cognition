# SEI Product Packaging / Deployment

更新日: 2026-09-01  
状態: **Current Product Packaging / Deployment Baseline**

## 1. この文書の役割

本書では、SEIを起動し、情報を保存し、終了後に再開できる最小の製品単位を、製品価値と既存の意味上の境界に基づいて定めます。

本書で定めるのは、最初に実現する配備形態と、将来、保存方式や利用画面が変わっても守るべき境界です。特定のクラウド、Kubernetes、データベース、Web開発基盤などを、製品が扱う概念として固定しません。

```text
Product Packaging
  = executable runtime
  + replaceable persistence
  + explicit durable data root
  + portable semantic data
  != semantic ontology
  != one mandatory deployment topology
```

## 2. 中心原則

### 2.1 実行物と耐久データを分ける

SEIの実行ファイルを削除・更新・再配布しても、判断の記録や来歴が失われない構成を基本とします。

```text
runtime executable
  != canonical semantic data
```

Goで単一の実行ファイルにまとめる利点は配布に活用できますが、そのファイル自体を意味上の正本にはしません。

### 2.2 deployment unitとsemantic boundaryを分ける

初期段階では、一つのプロセスに複数の論理的な利用窓口をまとめても構いません。

```text
one process
  may contain
    Interaction Adapter
    Canonical Semantic Runtime
    Persistence Adapter
    Integration Adapter
```

同じプロセスで動くことを理由に、それぞれが扱う意味まで一つにまとめることはしません。将来、サービスを分割しても、正本となる意味が変わらない構造を維持します。

### 2.3 Storageは交換可能なRealizationとする

ファイルシステム、RDB、オブジェクトストア、イベントストアなどは、永続化を実現するための選択肢です。

論理参照（Logical Reference）、意味の変遷（Semantic Lineage）、厳密な結び付け（Exact Binding）、来歴（Provenance）などの意味を、ファイルのパス、行ID、オブジェクトのキー、イベントの連番に依存させません。

```text
filesystem locator != Logical Reference
Storage migration != Semantic Revision
```

### 2.4 保存できたことと意味を理解できたことを分ける

未知の版や未知の契約を含む可搬なデータを保持できても、その意味を検証済みとは主張しません。

```text
bytes retained
  != semantics understood
  != validation succeeded
```

### 2.5 artifact identityとsemantic identityを分ける

配布用の書庫ファイルには、ビルドの版、元のコミット、対象環境などを識別する情報を持たせられます。ただし、それらは配布物の追跡情報です。

```text
artifact identity
  != semantic identity
  != Semantic Contract version
```

書庫のファイル名や実行ファイルの版番号を、論理参照、判断の識別子、意味の契約の識別子として流用しません。

## 3. 最初のPackaging Profile

最初に実現する最小構成は、**単一端末向けの配布形態（Local Single-Node Package）**とします。

```text
┌─────────────────────────────────────┐
│ SEI local runtime                  │
│                                     │
│ Interaction / machine adapters      │
│ Canonical semantic runtime          │
│ Persistence boundary                │
│ Provider / Integration boundary     │
└─────────────────┬───────────────────┘
                  │
                  ▼
        local durable data root
                  │
          portable semantic data
```

SEIが提供する実行環境では、ADR-0027に従ってGoを標準言語とします。最小構成では、一台のホスト上の一つのプロセスで始められることを優先します。最初から複数の常駐プログラム、サービスメッシュ、Kubernetesなどは求めません。

実行環境の外側に、永続データの保存先となるディレクトリを明示します。最初のファイルシステムによる実装では、持ち運べる意味データのまとまりを中心に保存します。端末内の付随データや実行環境固有の付帯情報を加える場合も、それらが意味の正本としての権威を持つかどうかを明確に区別します。

## 4. portable semantic data

現行の設計基準では、配布用に新しい汎用契約を追加しません。持ち運べる意味データの書き出しと取り込みには、`sei.semantic-interchange/v1alpha1`を引き続き使用します。

```text
Persistence internal form
  -> portable Semantic Interchange
  -> another Persistence Realization
```

永続化の提供元が内部で使う索引、取引履歴、データベースの構造などを、持ち運ぶ意味データの形式には含めません。

取り込み・書き出しで未知のレコードを保持する場合も、実行環境が理解していないレコードを、知らないうちに再構成・正規化することはしません。保存先の移行だけを理由に、意味の改訂（Semantic Revision）を生成することもしません。

大きなバイナリデータや外部の情報源を、すべてデータ本体に埋め込むことは求めません。データ本体の場所を示す情報は、永続化と実行環境の実装上の詳細です。論理参照や厳密な結び付けに、ファイルシステム上のパスを埋め込むことも求めません。

## 5. 保存と再開

単一端末向けの配布形態では、少なくとも次の条件を満たす必要があります。

1. portable semantic dataをdurable data rootへ保存できる。
2. processを終了した後、同じdata rootから別processで再読できる。
3. 再読後もlogical identity、Decision basis、Unknown / Conflict、Responsibility、Provenance等の意味差を保てる。
4. 保存途中の不完全な状態を正常に確定したpackageとして見せない。
5. supported Contract範囲ではruntime executableを交換してもsemantic dataを引き継げる方向を保つ。
6. Surface-local stateが失われてもcanonical semantic dataを失わない。

ISSUE-000054では、同じ版のGo実行ファイルを生成しました。独立した保存用プロセスを終了し、別のプロセスを起動して、永続データだけからデータのまとまりを再構成できることを確認しました。

```text
same-version process restart: scoped Executable Evidence available
version-upgrade resume: not yet verified
```

プロセスの再起動が成立したことを、実行ファイルの版を更新した場合や製品のリリースに関する検証根拠にまで一般化しません。

## 6. filesystem Persistence

最初のファイルシステム実装では、保存先のディレクトリにある`semantic.bundle.json`を、正本となるデータファイルとして扱います。

参照用の検証では、すべてのバイト列を一時ファイルに書き込み、同期とクローズを終えてから正本のファイル名へ変更します。これはfirst filesystem Realizationのmechanicsであり、Universal Persistence要件ではありません。

この実装だけから、電源断時の耐久性、ディレクトリの同期を含む保証、WindowsやmacOSなどすべての環境で同じ動作が得られるとは推定しません。

## 7. backup / restore

最小構成では、バックアップを実行中のプロセスのメモリ内容の複製とは定義しません。別processで意味を再構成するために必要なdurable dataを対象とします。

reference probeではcanonical semantic bundle fileを別directoryへcopyし、そのrestore先から同じportable bytesを再読できることを確認しました。

これは正本となるデータファイルに限った検証根拠です。今後追加される外部データ、資格情報、索引なども含む本番環境の完全なバックアップ、オンラインバックアップ、差分バックアップ、特定時点への復旧（PITR）などは未検証です。

## 8. Persistence交換とStorage migration

最小の交換境界は次です。

```text
Persistence A
  -> portable export
  -> Persistence B
  -> reload
  -> semantic comparison
```

reference probeではfilesystemからmemory Persistenceへoriginal Semantic Interchange bytesを移し、同じbundleを再読できることを確認しました。

これは永続化方式を交換できることに関する補助的な実行検証根拠です。メモリを使う永続化方式は評価用です。SCN-0008が想定する本番用のRDBやオブジェクトストアへの実際のデータ移行を証明するものではありません。

## 9. Local Reference Package

PMS-04の最小限の配布に関する検証根拠を得るため、ISSUE-000055ではLinux / amd64向けの**ローカル参照パッケージ（Local Reference Package）**を実際に作成しました。

current reference profileは次です。

- version: `0.2.0-reference`
- target: `linux-amd64`
- archive: `sei-local-reference-linux-amd64.tar.gz`
- executable: `sei-local-reference`
- build metadata format: `sei.local-reference/v1`

配布物の作成手順では、同じ入力から実行ファイルを二度ビルドし、バイト単位で一致することを確認します。さらにbuild identityを検査し、決定的なarchiveとSHA-256 checksumを作成します。

作成した書庫ファイルを別のディレクトリへ展開します。そこに含まれる実行ファイルを独立したプロセスとして起動し、意味データの保存、プロセスの終了、再読み込みを検査します。

Local Package Artifact Run `33509521544`はsuccessし、workflow artifact ID `9801021136`、workflow artifact digest `sha256:6282a2fe0b58dd023090d363e3323ce963a9f29c097f869ebab79b73aab2ba85`が記録されています。

```text
Local Reference Package PASS
  = PMS-04 Minimum scoped Executable Evidence
  != Product Release
  != formal platform support matrix
```

Linux / amd64、tar.gz、チェックサム、現在の管理コマンドは、参照配布形態を実現するための選択です。汎用的な製品要求や、恒久的に使うリリース形式ではありません。

## 10. Product Interactionとの境界

PMS-04で扱うpackage lifecycle controlと、PMS-03で扱うProduct Interaction Surfaceを分けます。

```text
package lifecycle control
  != human / AI Product Interaction
```

`sei-local-reference`の`version`・`save`・`inspect`は、配布形態を検証するための管理操作です。Inquiry、Observation、Recommendation、Decision等を扱う正式なSEI CLIではありません。

人間やAIが利用する正式な操作窓口は、引き続きPMS-03で検討する未決事項です。

## 11. Requirement / Acceptance監査

current Packaging境界とartifact実証は、主に既存のREQ-0001 / 0005 / 0009 / 0011 / 0018 / 0020 / 0021、SCN-0008 / 0010で表現できます。

literal process restartとreference distribution artifactまで実証した結果も、既存Requirementでは表現できない独立したfailureを示しませんでした。そのため、新しいstable Requirement / Scenarioは追加していません。

書庫の形式、対象環境、チェックサム、ビルド識別情報、配布物の管理コマンドは、現行の参照構成で採用する方法であり、汎用要求ではありません。

## 12. Current Evidence

```text
Packaging / Deployment Design: established
filesystem persistence: scoped Executable Evidence available
runtime-state-independent reconstruction: scoped Executable Evidence available
same-version literal process restart: scoped Executable Evidence available
canonical bundle copy / restore: scoped Executable Evidence available
filesystem -> memory Persistence exchange: scoped Executable Evidence available
Local Reference Package distribution artifact: scoped Executable Evidence available
Product Release: not yet verified
formal platform support matrix: not yet verified
version upgrade resume: not yet verified
actual production Storage migration: not yet verified
Release / Operational / Adoption: not yet verified
```

主なCIは次です。

- Semantic Runtime Conformance Run `33508376230` — literal process probe success
- Local Package Artifact Run `33509521544` — distribution artifact build / extract / save / reload / upload success
- Plan integrity Run `33509521580` — success
- Semantic Runtime Conformance Run `33509521596` — success

詳細は`../../runtime/PACKAGING_PROBE_EVIDENCE_2026-09-01.md`と`../../runtime/LOCAL_PACKAGE_ARTIFACT_EVIDENCE_2026-09-01.md`を参照します。

## 13. 次に固定しないこと

次はOpen Questionのまま残します。

- Product Releaseとして最初にsupportするOS / architecture
- production archive、installer、package manager、code signing、auto-update
- executable version upgrade後のresume
- productionで最初に採用するhuman-facing / AI-facing Product Interaction Surface
- RDBを最初のserver-side Storageとするか
- team / multi-user deployment topology
- online migration、HA / replication、production backup SLA
- container imageやcloud-managed deploymentを正式配布形態とするか
- background daemonを必須にするか

これらはローカル参照パッケージの検証が合格したという理由だけで、正式な要求へ昇格させません。

## 14. 関連文書

- `../definition/SEI_PRODUCT_SHAPE.md`
- `../roadmap/SEI_PRODUCT_MILESTONES.md`
- `../interaction/SEI_PRODUCT_INTERACTION.md`
- `../../architecture/SEI_DEPLOYMENT_ARCHITECTURE.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/adr/ADR-0007-canonical-persistence-boundary.md`
- `../../plan/adr/ADR-0027-go-as-standard-production-runtime-language.md`
- `../../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../../plan/issue/ISSUE-000046-define-v0-2-0-product-packaging-and-deployment-boundary.md`
- `../../plan/issue/ISSUE-000054-materialize-packaged-resume-and-storage-migration-probe.md`
- `../../plan/issue/ISSUE-000055-materialize-first-supported-local-package-artifact.md`
- `../../runtime/PACKAGING_PROBE_EVIDENCE_2026-09-01.md`
- `../../runtime/LOCAL_PACKAGE_ARTIFACT_EVIDENCE_2026-09-01.md`

## 15. Natural Japanese review

Product Value、Product Shape、PMS-04、Product Interaction、REQ-0001 / 0005 / 0009 / 0011 / 0018 / 0020 / 0021、SCN-0008 / 0010、ADR-0007 / 0027 / 0029、current Semantic Interchange runtime、Packaging probe、Local Reference Package、Local Package Artifact Run `33509521544`とartifact metadataを照合しました。Packagingをsemantic ontologyではなく、実行物・Persistence・durable data・portable semantic dataの組み合わせとして整理し、same-version process restartとversion upgrade、Persistence交換probeとactual production Storage migration、reference distribution artifactとProduct Release、package lifecycle controlと正式Product Interactionを分けています。そのうえで、意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。