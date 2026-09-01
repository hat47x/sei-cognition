# SOZA v0.2.0 Release Acceptance

更新日: 2026-09-02  
状態: **Release Candidate Design Baseline / Release Evidence Not Yet Verified**

## 1. この文書の役割

この文書は、SOZA v0.2.0について、**何をrelease可能な最小supported scopeとして扱い、どの検査を同一候補commitへ結び付けるか**を定めます。

v0.2.0はproduction完成版ではありません。現在のrepositoryで再現可能な意味・操作・保存・配布・責務分離・交換可能性を、開発者や評価者が検証できる **Local Reference Product Baseline** として固定します。

Product Value上のEvidence高さは`product/value/SOZA_VALUE_ACCEPTANCE.md`とADR-0018を正とします。

```text
Executable Evidence
  != Release Candidate Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Release Candidate Evidenceは5段階Evidenceへ新しいUniversal段階を追加するものではありません。Executable Evidenceのうち、特定のrelease候補commitを統合的に再検査したというrelease準備上の記録です。

## 2. v0.2.0のrelease scope

v0.2.0では、次の範囲をLocal Reference Product Baselineとして扱います。

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

reference Surfaceの存在は、正式Web UI、CLI、API、MCP等のsupport方式を固定しません。

### 2.3 Local Single-Node Packaging baseline

- GoによるLocal Reference Package
- Linux / amd64 reference artifact
- deterministic build / archive
- build identity
- checksum
- durable data rootへのsave / reload
- archive展開後の独立processによるresume

Linux / amd64は**このreference artifactを検査するtarget**です。正式なProduct support matrixや将来の唯一のtargetを意味しません。

### 2.4 Product Access / Collaboration separation baseline

- authentication identityとBounded Subjectの分離
- Product access permissionとsemantic Responsibility / Authorityの分離
- denied / not_evaluatedの区別
- Selective Disclosureでの`withheld`保持
- canonical sourceの非改変

reference probe固有のpermission vocabularyを正式RBAC / ABAC仕様へ昇格させません。

### 2.5 Realization / Provider exchange baseline

PMS-06のうち、次をscopeへ含めます。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
```

E3aでは、別repositoryでversion管理されるartifactをsource identity付きで扱い、既存Cognitive Method / Capability Observation boundaryへ戻せることを確認しています。

次はscope外です。

```text
E3b live external process / service integration
E4 operational portability
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
Local Reference Product Baseline released
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

過去の個別workflowがgreenであることは有用な履歴Evidenceですが、candidate gateの代替にはしません。

## 6. Plan status policy

candidateでは次をblockerとします。

```text
Open
In Progress
Blocked
```

`Deferred`はversion固有allow-listに列挙したものだけを許可します。

v0.2.0では`ISSUE-000021`だけを許可します。これはhistorical chat export等が得られた場合のdesign-history provenance再監査であり、current Local Reference Product Baselineの意味、build、配布再現性を止める課題ではありません。

このallow-listはSOZA Universal Plan ontologyではなくv0.2.0 candidate policyです。

## 7. required paths

candidate policyは、v0.2.0 scopeを支える正本・Executable Evidenceの主要anchorを列挙します。

少なくとも次の領域を黙って外せないようにします。

- Product Value / Product Shape / Product Milestone
- Product Interaction
- Product Packaging
- Product Identity / Access / Collaboration
- Realization / Provider Exchange
- Requirements / Scenarios / Journey
- Architecture / Deployment / Product Access
- current Contract / Profile / fixture
- Go runtime / reference probes
- Local Reference Package資料
- V6 / V7 evaluation
- Plan registry
- v0.2.0 Release Acceptance

required pathはcoverage指標ではありません。candidate scopeから重要な正本を落としてgateを通すことを防ぐためのanchorです。

## 8. Local Reference Package gate

v0.2.0では、`go test ./...`だけでは配布artifactの再現性を十分に確認できません。

candidate gateではLocal Reference Packageについて、少なくとも次を同じsource commitから再現します。

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

- schema
- version
- repository
- release scope
- source commit SHA
- source tree SHA
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

checkerやworkflowを共通化しても、v0.1.0のscope・required gate・non-claimsをv0.2.0へ暗黙に置き換えません。各versionの`release-candidate.json`を独立したpolicyとして保持します。

v0.1.0のhistorical candidate Evidenceは、その時点のcommit / tree / gate resultへ結び付いた記録として維持します。

## 12. branch / tag boundary

自動candidate gateの対象はversionごとに明示します。

```text
develop/v0.1.0 → release/v0.1.0 policy
develop/v0.2.0 → release/v0.2.0 policy
v0.1.0 tag     → release/v0.1.0 policy
v0.2.0 tag     → release/v0.2.0 policy
```

`workflow_dispatch`では必要なrefとpolicy versionを明示して再検査できる形を許容します。

将来versionのOpen Issueを過去versionのrelease blockerとして誤検出しないよう、version固有workflow境界を維持します。

## 13. failure時の扱い

candidate gate failureはrelease条件を弱める理由にはしません。

1. failureしたsub-gateを特定する。
2. Product policy、checker、workflow、runtime、artifact buildのどこに原因があるか切り分ける。
3. 原因のある層を修正する。
4. 同じcandidate gateを再実行する。
5. success後にのみcandidate statusを更新する。

## 14. current state

現時点ではこの文書はDesign baselineです。

- v0.2.0 Release Candidate Design: **Satisfied by this baseline**
- v0.2.0 integrated candidate gate: **Not Yet Verified until actual CI success**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

componentごとの既存Executable Evidenceを、この文書だけでv0.2.0 candidate PASSへ読み替えません。

## 15. Natural Japanese review

Product Value、PMS-03〜07、v0.1.0 Release Acceptance、Product Interaction、Local Single-Node Packaging、Product Access、Realization / Provider Exchange、ISSUE-000055〜000058、E3a external artifact integration、current CI Evidenceを照合した。そのうえで、v0.2.0で実際にsupportする範囲をLocal Reference Product Baselineへ限定し、E3b / E4、production security / Storage / formal support matrixを非主張範囲へ残した。candidate gate、actual release、Operational / Adoption Evidenceを明確に分け、reference artifactのLinux / amd64検査を正式な全platform supportへ拡張しないよう整理している。最後に、意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。