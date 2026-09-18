# TEI Version Exchange Evidence — 2026-09-05

## 1. この文書の位置づけ

この文書は、PMS-06で未検証として残っているTEI executableの取得・version交換について、2026-09-05に行った追加実証を記録します。

対象は、ISSUE-000065で成立したfixed-artifact actual TEI CLI executionを起点に、別source revisionへ交換しても同じProvider integration surfaceを追跡できるかという後続探索です。現在はISSUE-000072でこの探索を継続します。

今回の中心は次です。

```text
artifact acquisition path
  != artifact identity
  != Provider surface compatibility
  != SEI Capability Observation identity
```

また、GitHub Actionsのjobが開始できなかったことをTEI CLI互換性の失敗へ読み替えません。

## 2. Revision A — 既存actual artifactの再取得と再検証

ISSUE-000065で利用した既存Evidence artifactは2026-09-05時点でもGitHub上に保持されていました。

- TEI source commit: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- Workflow Run: `33589084290`
- Artifact ID: `9831112092`
- Artifact name: `tei-soza-e3b-p2-linux-amd64`
- GitHub artifact digest: `sha256:1ee8bf4112d9ae97e1f66b3165f70278663951e9dd4bd6020b465471f563a287`
- Expiration: `2026-09-16T03:59:55Z`

GitHub connectorのartifact download経路からZIPを取得し、その中の`tei-e3b-p2-linux-amd64.tar.gz`を現在の作業containerへ配置しました。

bundle内のactual bytesを再計算した結果は次です。

```text
metadata.source_commit
  48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67

actual bin/tei SHA-256
  31f0298b47f9caaa93cd4b2da538cda72e23e5b518f2d0ddad2cf98c46882154

actual provider-plan.json SHA-256
  39eafb26cf189681e0bd2ff46fcaf000cbe2f860cf698765bbadac6dfbd2a950
```

いずれも2026-09-02のEvidence文書とmetadataの固定値へ一致しました。`bin/tei`にはexecutable bitがあり、container内で起動すると`deployment-provider-plan`を含む既知CLI surfaceを表示できました。

この再取得は、GitHub Actions artifactという一つのacquisition pathからactual bytesを再び取り出せることの観測です。artifact retentionの永続性や正式なTEI配布方式を証明するものではありません。

## 3. Acquisitionから独立したbundle verifier

外部artifactの取得方法とidentity検証を分離するため、次のrepository-local verifierを追加しました。

- `runtime/integration/verify_tei_evidence_bundle.py`
- `runtime/integration/test_verify_tei_evidence_bundle.py`

verifierは`.tar.gz`を展開せずread-onlyに読み、少なくとも次を確認します。

- archive memberにabsolute path / `..` traversalがない。
- symlink / hardlink / device memberを受理しない。
- `metadata.json`、`provider-plan.json`、`bin/tei`が存在する。
- metadata schema / repository / entry pointが既知境界と一致する。
- source commitが40桁lowercase hexadecimalである。
- actual binary SHA-256がmetadataと一致する。
- actual Provider Plan SHA-256がmetadataと一致する。
- Provider Planのtop-level fieldが既知Adapter-local surface内にある。
- Provider Planに認識可能な情報が存在する。
- `bin/tei`にexecutable bitがある。
- 必要ならexpected source / binary / Provider Plan digestへ追加照合できる。

出力には`qualityJudgement = not_evaluated`を保持します。

```text
TEI Evidence bundle identity verified
  != SEI Adapter compatibility verified
  != TEI version exchange PASS
  != Operational Evidence
```

### ローカル検証

同一内容のverifierを作業containerでrevision Aのactual bundleへ適用し、上記3 identityの一致を確認しました。

さらにsynthetic bundleを用いた7件のtestを実行し、すべてPASSしました。

- valid bundle
- binary digest drift
- unknown Provider Plan top-level field
- path traversal member
- symlink member
- non-executable binary
- expected source commit mismatch

この7件はartifact identity / archive safetyのrepository-local検査であり、actual TEI revision B executionではありません。

## 4. Revision B — current TEI mainを固定

version交換候補Bとして、2026-09-05時点のTEI current mainを固定しました。

- Repository: `hat47x/tei-platform`
- Source commit: `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`
- Evidence branch: `evidence/soza-e3b-p2-version-exchange-2026-09-05`
- Evidence workflow commit: `5e87cd18967b6d86001cc4d5229bd4886b94e30d`

旧revision Aと同じ`deployment-provider-plan`入力条件を使い、Bのactual CLIをbuild・実行して別artifactを作るEvidence workflowをbranch上で起動しました。

出力bytesの一致は要求していません。確認したいのは、少なくとも次の境界です。

```text
revision A source != revision B source

same intended Provider surface
same fixed reference invocation

→ B actual CLI build / execution
→ B Provider Plan identity
→ SEI Adapter compatibility
```

## 5. Revision B workflowの観測

Evidence workflow Run `33913500170`は2回実行を試みましたが、いずれもjob stepを一つも開始しないまま`failure`となりました。

### Attempt 1

- Run: `33913500170`
- Run attempt: `1`
- Head commit: `5e87cd18967b6d86001cc4d5229bd4886b94e30d`
- Job: `actual-tei-cli`
- Job ID: `101155229525`
- Job conclusion: `failure`
- 実行されたjob steps: **0**
- Evidence artifact: **なし**

### Attempt 2

attempt 1が一時的なrunner割当failureだった可能性だけを切り分けるため、同じfailed jobを一度だけ再実行しました。

- Run: `33913500170`
- Run attempt: `2`
- Job: `actual-tei-cli`
- Job ID: `101156710003`
- Job conclusion: `failure`
- 実行されたjob steps: **0**
- Evidence artifact: **なし**

attempt 1 / 2ともstepが一つも開始していないため、次は今回のrunから観測していません。

- revision B source checkout
- Go setup
- `cmd/tei` build
- `deployment-provider-plan`実行
- Provider Plan decode
- Evidence artifact生成

したがって、このrunをTEI revision Bの互換性failureへ数えません。

```text
workflow run failure before job steps
  != TEI build failure
  != deployment-provider-plan incompatibility
  != SEI Adapter incompatibility
```

同じ停止点が2回観測されたため、少なくとも今回のGitHub-hosted実行面ではjob開始前に継続して停止する状態として扱います。ただし、その原因をTEI Product側へ帰属させません。

## 6. TEI配布面の現状

2026-09-05時点で`hat47x/tei-platform`のGitHub Releasesは0件でした。

したがって、現在確認できるactual binary取得経路は少なくとも次の性質を持ちます。

- source revisionからbuildする。
- または過去のGitHub Actions Evidence artifactをretention期間内に取得する。

これを正式なTEI distribution contractとは扱いません。Release asset、署名、更新channel、retention、credential lifecycleは別の未確定領域です。

## 7. bootstrap/final-source調査で確認した境界

GitHub-hosted workflowとは別のrevision B取得経路として、TEI repositoryに残る`bootstrap/final-source/*`を調査しました。

2026-09-05のcurrent TEI main `c1451327557a2b84a8748a225d0ed4f173602127`では、`bootstrap/final-source`に`0000`から`0061`まで62個のchunkが存在します。`.github/workflows/normalize-source.yml`には、それらを連結してBase64 decodeし、XZ archiveへ戻す手順と固定SHA-256が残っています。

```text
bootstrap/final-source/0000 ... 0061
  → concatenate
  → Base64 decode
  → tei-source.tar.xz

fixed SHA-256
  6e0d22efaa4896c4fc44adf1c543d8950abfa910e2a6a0306ec84b3655acc801
```

ただし、このworkflow自身の名称は`Normalize TEI M0.22.1 source`であり、archiveを展開する処理は`git checkout -B normalize origin/main`の後に行われます。したがって、このpayloadはcurrent Git revisionの完全なsource archiveではなく、M0.22.1 source normalizationに使う固定payloadとして扱うのが妥当です。

このため、payloadがrevision Bを含むtree上に存在することだけから、payload bytesをrevision B source bytesへ同一視しません。

```text
bootstrap payload digest verified
  != payload proven identical to Git revision B source
  != revision B CLI Executable Evidence
```

また、revision A `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`からrevision B `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`まではGitHub compare上で1748 commits aheadでした。多数の追加・変更ファイルがあるため、revision A artifactやM0.22.1 normalization payloadへ小さな差分だけを適用してBを再構成する前提も採用しません。

current TEI mainは調査中に`c1451327557a2b84a8748a225d0ed4f173602127`まで進みましたが、ISSUE-000072のrevision B identityは既に固定した`1a7028d444fcae60a1c4f2f2d247456f4c7c35be`から無言で差し替えません。current mainの追随は、必要なら別revision Cとして明示的に扱います。

今回利用可能だったDesktop実行環境はオフラインで、そこからprivate repositoryをcloneする経路も成立しませんでした。この取得failureもTEI product incompatibilityへ読み替えません。

## 8. Revision Bの実行source Git identity

revision Bのactual source archiveを現在の作業containerへ取得する経路は成立しませんでしたが、Git object identityから、実行に関係するsource境界を追加で確認しました。

revision B `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`のroot treeは`630d3e9e2acaea70312bee19cf8a0f7235655cd6`です。このtreeから、今回のfixed invocationに関係する主要なsource / input identityを次のように固定できます。

```text
cmd tree
  ac4d4406dfa590a2078cf91217c4fe30797e7f8e

internal tree
  10d2bfea4932c308fa6537e3b081bc6ea5501205

reference tree
  57fafb742988ecb936b9ab261fa8a991e37ed5c7

go.mod blob
  f8763f8fb2d64d73f1b40b905f62b5e09c44493b

go.sum blob
  c7cd14781271dca2b014daf2f53d49d95b8e8826
```

mainの第一親履歴を遡り、この5 objectがBと一致する境界を調べました。

直前のmain側commit `694ff4fb77141ee671c0e847b8bc5a203bdaef27`では、Bとのcompareに`internal/driver/queryruntime/oracle/runner.go`とそのtestの差分が残ります。その次のmain merge `5e89975fe188b190a95df071eda79fa60fcff607`では、上記5 object SHAがrevision Bとすべて一致します。

`5e89975fe188b190a95df071eda79fa60fcff607`は、`Oracle actual readでdriver観測のraw列metadataを保持する`をmainへ取り込んだmergeで、commit時刻は`2026-09-04T10:48:14Z`、日本時間では`2026-09-04T19:48:14+09:00`です。

一方、`5e89975fe188b190a95df071eda79fa60fcff607`とrevision Bでは`plan`と`tools`のtree SHAが異なります。したがって、repository commit全体を同一とは扱いません。確認できたのは、今回のCLI buildとfixed reference invocationに直接関係する上記object群のcontent-addressed identityです。

```text
same cmd/internal/reference/go.mod/go.sum Git object identity
  != same repository commit
  != actual executable bytes
  != revision B Provider Plan execution
  != SEI Adapter compatibility
```

この同一性からhistorical artifactの`metadata.source_commit`を書き換えることもしません。artifactが別commitから生成されたなら、そのprovenanceは別commitのまま保持します。

また、`5e89975fe188b190a95df071eda79fa60fcff607`自身に紐づくGitHub Actions runは0件でした。その後、revision BまでのB-equivalent source区間についても、確認したrepository-level Actions実行履歴から再利用可能なactual CLI artifactは見つかりませんでした。

したがって、今回の調査で強くなったのはrevision Bの**静的な実行source identity**です。revision Bのactual CLI bytesをbuild・取得・実行したというExecutable Evidenceへはまだ昇格させません。

## 9. 現在のEvidence状態

```text
revision A fixed source / actual CLI
  = Scoped Executable Evidence available

revision A Evidence artifact re-acquisition
  = observed

revision A bundle identity re-verification
  = verified in current work session

acquisition-independent bundle verifier
  = implemented; 7 local tests passed

revision B source identity
  = fixed to 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

revision B execution-source Git identity
  = cmd/internal/reference/go.mod/go.sum object SHA fixed

main第一親履歴上で確認したB-equivalent実行source成立境界
  = 5e89975fe188b190a95df071eda79fa60fcff607

B-equivalent source区間のactual executable artifact
  = Not Observed

revision B GitHub-hosted attempts
  = 2 failures before any job step

revision B actual CLI build / execution
  = Not Yet Verified

revision B Provider Plan
  = Not Yet Observed

bootstrap M0.22.1 payload
  = reconstruction method and fixed digest observed; not revision B Evidence

A/B SEI Adapter compatibility comparison
  = Not Yet Verified

formal TEI executable distribution
  = Not Yet Defined

credential lifecycle / Operational portability
  = Not Yet Verified
```

## 10. 次の成立条件

次にEvidence強度が上がるのは、revision Bについて実際のEvidence bundleを取得できた時です。

取得経路はGitHub Actionsに限定しません。どの経路で取得しても、まず`verify_tei_evidence_bundle.py`へ戻してsource / binary / Provider Plan identityを確認します。その後、SEIのcurrent `teiintegration` Adapterでactual B binaryを起動し、current Capability Observationへmappingできるかを確認します。

今回固定したGit object identityは、取得したsource treeが意図したBの実行sourceと一致するかを確認する補助線として利用できます。ただし、Git object identityだけからbinary digestやProvider Planを推定しません。

A/BでProvider Plan bytesやbinary digestが異なっても、それ自体をfailureにはしません。一方、既存Adapter-local surfaceで意味を壊さず解釈できない場合は、Provider compatibilityの独立したEvidenceとして上流Requirement / Contractへ戻します。

新しいStable RequirementやUniversal TEI fieldは、actual B Evidenceを得る前に追加しません。

## 11. 自然な日本語レビュー

PMS-06、ISSUE-000061 / 000065 / 000072、既存Actual TEI CLI Evidence、current `teiintegration`、TEI current main、TEI Evidence workflow、revision A artifact、revision B workflow attempt 1 / 2、`bootstrap/final-source`、`normalize-source.yml`、revision Bおよびその第一親履歴のGit tree identityを照合しました。

今回前進したのは、過去artifactを再取得してactual bytesを再検証できたこと、そのidentity検証をGitHub Actionsやcredentialから独立したrepository-local toolへ分離したこと、bootstrap payloadをrevision B sourceと誤認しない境界を明示できたことに加え、revision Bの`cmd` / `internal` / `reference` / module filesについてcontent-addressed identityを固定できたことです。

一方、この静的identityはactual binaryを取得した証拠ではありません。revision Bのworkflowは2回ともjob step開始前に停止し、B-equivalent source区間にも再利用可能なactual executable artifactは観測できなかったため、BのCLI実行、Provider Plan、SEI Adapter互換性について結果を推定していません。

Evidenceの高さと未検証範囲を変えず、自然な日本語となることを最重要視して記録しています。
