# SOZA v0.2.0 Release Acceptance

更新日: 2026-09-02  
状態: **Actual develop Release Candidate Evidence available / Release Evidence Not Yet Verified**

## 1. この文書の役割

この文書は、SOZA v0.2.0について、**何をrelease可能な最小supported scopeとして扱い、その候補をどの検査で確認するか**を定めます。

v0.2.0はproduction完成版ではありません。現在のrepositoryで再現できる意味・操作・保存・配布・責務分離・交換可能性を、開発者や評価者が検証できる **Local Reference Product Baseline** として固定します。

Product Value上のEvidence高さは`product/value/SOZA_VALUE_ACCEPTANCE.md`とADR-0018を正とします。

```text
Executable Evidence
  != Release Candidate Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Release Candidate Evidenceは、5段階Evidenceに新しいUniversal段階を加えるものではありません。特定の候補commitについて、release前に必要なExecutable Evidenceをまとめて再検査した記録です。

## 2. v0.2.0のsupported scope

v0.2.0では、次をLocal Reference Product Baselineとして扱います。

### 2.1 Product / semantic baseline

- Product Value / Value Proposition / Product Shape
- Deadline-free Product Milestones
- Product Requirements / Acceptance Scenarios / Product Journey
- Reference Architecture / traceability
- current 5 Semantic Contract family
- current Representation Profiles
- JSON Schema / fixture / semantic validator
- Go semantic runtime

### 2.2 Product Interaction reference baseline

- human-oriented Surface
- machine-oriented Surface
- 同じcanonical sourceへの接続
- Recommendation / Decision等の意味差の保持
- light / audit Projection境界

このscopeは、正式なWeb UI、CLI、API、MCP等のsupport方式を固定しません。

### 2.3 Local Single-Node Packaging baseline

- GoによるLocal Reference Package
- Linux / amd64 reference artifact
- deterministic build / archive
- build identity / checksum
- durable data rootへのsave / reload
- archive展開後の独立processによるresume

Linux / amd64は、このreference artifactで実際に検査したtargetです。正式なProduct support matrixや将来の唯一のtargetを意味しません。

### 2.4 Product Access / Collaboration separation baseline

- authentication identityとBounded Subjectの分離
- Product access permissionとsemantic Responsibility / Authorityの分離
- denied / not_evaluatedの区別
- Selective Disclosureでの`withheld`保持
- canonical sourceの非改変

reference probe固有のpermission vocabularyを正式RBAC / ABAC仕様へ昇格させません。

### 2.5 Realization / Provider exchange baseline

PMS-06では、次までをv0.2.0 scopeに含めます。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
```

E3aでは、別repositoryでversion管理されるartifactをsource identity付きで扱い、既存Cognitive Method / Capability Observation boundaryへ戻せることを確認しています。

次はscope外です。

```text
E3b live external process / service integration
E4 Operational portability
```

## 3. v0.2.0で主張しないこと

Release Candidate Gateがsuccessしても、次を自動的にSatisfiedへ上げません。

- actual Product Releaseの存在
- E3b live external AI / SaaS / TEI process・service integration
- E4 Operational portability
- production Provider interoperability
- production Storage integration
- production IdP / IAM / credential / session lifecycle
- formal RBAC / ABAC
- production security assessment
- production HA / backup / DR / SLA
- formal OS / architecture support matrix
- production installer / package manager / signing
- Operational Evidence
- Adoption / Outcome Evidence

```text
Local Reference Product Baseline candidate PASS
  != production service proven
```

## 4. candidate identity

candidateは少なくとも次で特定します。

```text
repository = hat47x/soza
version = 0.2.0
source commit SHA
source tree SHA
```

source commitを`release-candidate.json`へ固定しません。設定ファイル自身を書き換えるたびにcommitが変わる自己参照を避けるためです。

Release Candidate Gateは実行時にGitからcommit / tree SHAを取得し、derived reportへ記録します。

## 5. v0.2.0 Release Candidate Gate

同じsource commitをcheckoutした環境で、次を再検査します。

1. Plan registry / Document Review Registry integrity
2. Requirements Registry checker self-testとcurrent REQ / SCN整合
3. current Contract fixture conformance
4. Representation Profile fixture conformance
5. commit-pinned RFC 8785 JCS probe
6. semantic runtimeと各reference probeのGo test
7. V6 / V7 Projection evaluation
8. Local Reference Packageのdeterministic build / archive / checksum / independent-process resume
9. v0.2.0 candidate policy / required-path validation / bound report

過去の個別workflowがgreenであることは有用な履歴Evidenceですが、この統合gateの代替にはしません。

## 6. Plan status policy

candidateでは次をblockerとします。

```text
Open
In Progress
Blocked
```

`Deferred`はversion固有allow-listに列挙したものだけを許可します。v0.2.0では`ISSUE-000021`だけを許可しています。これはhistorical design provenanceの再監査であり、current Local Reference Product Baselineの意味、build、配布再現性を止める課題ではないためです。

PR #34のbootstrap Run `33531336681`では、Gate 1〜8がsuccessした後、Gate 9が`ISSUE-000059 = In Progress`を意図どおりblockしました。未解決Issue blockerが実際に機能することを、このRunで確認しています。

## 7. required paths

candidate policyは、v0.2.0 scopeを支える主要な正本とExecutable Evidenceをanchorとして列挙します。

対象には少なくとも、Product Value / Shape / Milestone、Interaction、Packaging、Identity / Access / Collaboration、Realization / Provider Exchange、Requirements / Scenarios / Journey、Architecture、current Contract / Profile / fixture、Go runtime / reference probes、Local Reference Package資料、V6 / V7 evaluation、Plan registry、v0.2.0 Release Acceptanceを含めます。

required pathはcoverage指標ではありません。重要な正本をcandidate scopeから黙って外してgateを通すことを防ぐためのものです。

## 8. Local Reference Package gate

`go test ./...`だけでは、配布artifactの再現性までは確認できません。そのためv0.2.0 candidateでは、Local Reference Packageについて次を同じsource commitから再現します。

- `CGO_ENABLED=0`, Linux / amd64でreference binaryを2回buildする。
- 二つのbinaryがbyte-for-byteで一致する。
- version / source commit / targetをbuild identityとして埋め込む。
- file order、mtime、owner / groupを固定したarchiveを生成する。
- archiveのSHA-256を記録する。
- archiveを別directoryへ展開する。
- 展開したbinaryでSemantic Interchangeを保存してprocessを終了する。
- 別processでdurable data rootから再読し、期待bundleを再構成する。

この検査はreference artifactの再現性を示します。正式なcross-platform supportやproduction durabilityを示しません。

## 9. candidate report

candidate gateが最後まで成功した場合、machine-readable reportへ少なくとも次を記録します。

- schema / version / repository / release scope
- source commit SHA / source tree SHA
- executed gate names
- observed allowed Deferred Issue
- candidate gate result
- explicit non-claims

reportやartifactはderived Evidenceです。Product ValueやSemantic Contractのauthorityではありません。

## 10. actual Release Evidenceへの昇格条件

Release Evidenceへ昇格するには、candidate gate PASSに加えて少なくとも次が必要です。

1. actual `v0.2.0` tag / release identityが存在する。
2. tagがcandidate gateを通したsource commitへexactに結び付く。
3. 配布Artifactがtag / source commitへ追跡できる。
4. Local Reference Package bytesをdigest等で識別できる。
5. release notesがsupported scopeと非主張範囲を明示する。
6. tag対象commitでv0.2.0 Release Candidate Gateがsuccessしている。
7. release後のEvidence recordがtag、commit、artifact、gate resultを結び付ける。

```text
candidate PASS
  + no actual release
  != Release Evidence
```

## 11. v0.1.0との境界

v0.1.0とv0.2.0ではrelease scopeが異なります。

```text
shared checker
  != shared policy
  != shared supported scope
```

checkerやworkflowを共通化しても、各versionの`release-candidate.json`を独立したpolicyとして保持します。v0.1.0のhistorical candidate Evidenceも、その時点のcommit / tree / gate resultへ結び付いた記録として維持します。

## 12. branch / tag boundary

自動candidate gateはversionごとにpolicyを選びます。

```text
develop/v0.1.0 → release/v0.1.0 policy
develop/v0.2.0 → release/v0.2.0 policy
v0.1.0 tag     → release/v0.1.0 policy
v0.2.0 tag     → release/v0.2.0 policy
```

`workflow_dispatch`ではpolicy versionを明示して再検査できます。将来versionのOpen Issueを過去versionのrelease blockerとして誤検出しないよう、version固有の境界を維持します。

## 13. failure時の扱い

candidate gate failureはrelease条件を弱める理由にはしません。

1. failureしたsub-gateを特定する。
2. Product policy、checker、workflow、runtime、artifact buildのどこに原因があるか切り分ける。
3. 原因のある層を修正する。
4. 同じcandidate gateを再実行する。
5. success後にのみEvidence状態を更新する。

PR #34では、Registry全置換時に`ISSUE-000013`の既存ファイル名を誤って転記したため、Run `33568527280`のGate 1がfailureしました。実ファイル名へ戻した後、Plan integrityとRelease Candidate Gateを通し直してsuccessを確認しています。

このfailureを条件緩和で回避せず、原因を直して同じ検査を再実行した履歴を残します。

## 14. Release Candidate Evidence

### 14.1 PR #34 test merge

PR #34では、merge前のtest merge状態で9 gateがsuccessしました。最終文書同期後のRelease Candidate Gate Run `33568925573`もsuccessしています。

これは、base branchとPR差分を組み合わせた状態が候補条件を満たすことを確認したEvidenceです。

### 14.2 actual `develop/v0.2.0` Evidence point

PR #34をmergeしたactual `develop/v0.2.0` commit
`724cba2a744582252c6ccba8322fc34a55b76b1b`について、push-triggered Release Candidate Gate Run `33569004831`がsuccessしました。

同じcommitで次もsuccessしています。

- Plan integrity Run `33569004843`
- External Integration E3a Run `33569004842`

Release Candidate Gateでは9 gateすべてに加え、candidate reportとLocal Reference Packageのartifact uploadもsuccessしました。

- candidate report artifact ID: `9824232506`
- candidate report artifact digest: `sha256:f6c9326e6af415654df80446893c5ba5c847fccd4e2d7192806b7056eb6c781d`
- Local Reference Package artifact ID: `9824232197`
- Local Reference Package artifact digest: `sha256:13bb5ed0ba8ab39e817a5dadc952e8bfb8934df9965474aa8435718136138ac7`

このcommitを、v0.2.0における最初のactual develop candidate Evidence pointとして固定します。

Evidence文書を更新するとbranch HEAD自身は変わるため、文書中のEvidence pointを常に最新HEADへ追従させる自己参照は行いません。後続commitの回帰はCIで確認し、Release Evidenceへ進む際にはactual tag対象commitを改めてexactに検査します。

```text
actual develop candidate Evidence point established
  != every future develop commit automatically verified
  != v0.2.0 tag exists
  != Release Evidence
```

## 15. current state

現時点の状態は次です。

- v0.2.0 Release Candidate Design: **Satisfied**
- PR #34 test merge candidate Evidence: **Satisfied**
- actual `develop/v0.2.0` candidate Evidence point: **Satisfied** — commit `724cba2a...`, Run `33569004831`
- actual `v0.2.0` tag / release: **Not Yet Created**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

candidate Evidenceの成立を、actual Product Releaseやproduction readinessへ読み替えません。

## 16. Natural Japanese review

Product Value、PMS-03〜07、v0.1.0 Release Acceptance、Product Interaction、Local Single-Node Packaging、Product Access、Realization / Provider Exchange、ISSUE-000055〜000059、E3a external artifact integration、PR #34とactual `develop/v0.2.0`のGitHub Actions Evidenceを照合しました。

そのうえで、v0.2.0で実際にsupportする範囲をLocal Reference Product Baselineへ限定し、E3b / E4、production security / Storage / formal support matrixを非主張範囲へ残しています。PR test merge、actual develop candidate Evidence point、後続commit、actual tag / release、Operational / Adoption Evidenceを分け、reference artifactの検査をproduction readinessへ拡張しないよう整理しました。

最後に、意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
