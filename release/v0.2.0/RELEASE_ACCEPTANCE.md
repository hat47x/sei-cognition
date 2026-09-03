# SOZA v0.2.0 Release Acceptance

更新日: 2026-09-03  
状態: **Release Evidence Satisfied for the Local Reference Product Baseline**

## 1. この文書の役割

この文書は、SOZA v0.2.0について、**何をsupported scopeとしてreleaseし、candidateからactual releaseまでをどのEvidenceで判断するか**を定めます。

v0.2.0はproduction完成版ではありません。repositoryで再現できる意味・操作・保存・配布・責務分離・交換可能性を、開発者や評価者が検証できるLocal Reference Product Baselineとして固定します。

Product Value上のEvidence高さは`product/value/SOZA_VALUE_ACCEPTANCE.md`とADR-0018を正とします。

```text
Executable Evidence
  != Release Candidate Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Release Candidate Evidenceは5段階Evidenceに新しいUniversal段階を加えるものではありません。特定のcandidate commitについて、release前に必要なExecutable Evidenceをまとめて再検査した記録です。

Release Evidenceは、その候補がactual tag / release / artifactとして配布され、検査済みsource commitへ追跡できることを示します。

## 2. v0.2.0のsupported scope

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

v0.2.0でsupportを主張する範囲は次までです。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
```

E3aでは、別repositoryでversion管理されるartifactをsource identity付きで扱い、既存Cognitive Method / Capability Observation boundaryへ戻せることを確認しています。

release source commitには、E3b-P1 public live Provider integrationやTEI executable injection boundaryのScoped Executable Evidenceも存在します。しかし、repositoryに後続Evidenceが存在することだけを理由に、v0.2.0のsupported scopeを広げません。

```text
later scoped Evidence exists
  != v0.2.0 supported scope expanded
```

## 3. v0.2.0で主張しないこと

actual v0.2.0 Releaseが成立しても、次をSatisfiedへ上げません。

- production serviceとしての完成
- E3b live external AI / SaaS / TEI process・service integration全体
- actual TEI CLI integrationの完了
- external Cognitive Methodのlive実行
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

source commitを`release-candidate.json`へ固定しません。設定ファイル自身の変更でcommitが変わる自己参照を避けるためです。

repository-local candidate checkerは実行時にGitからcommit / tree SHAを取得し、derived reportへ記録します。どのautomation providerから実行したかはcandidate identityに含めません。

## 5. v0.2.0 Release Candidate Gate

同じsource commitをcheckoutした環境で、次の9責務を再検査します。

1. Plan registry / Document Review Registry integrity
2. Requirements Registry checker self-testとcurrent REQ / SCN整合
3. current Contract fixture conformance
4. Representation Profile fixture conformance
5. commit-pinned RFC 8785 JCS probe
6. semantic runtimeと各reference probeのGo test
7. V6 / V7 Projection evaluation
8. Local Reference Packageのdeterministic build / archive / checksum / independent-process resume
9. v0.2.0 candidate policy / required-path validation / bound report

`release-candidate.json`の`required_gates`は、この検査責務をmachine-readableに固定します。

GitHub Actionsは当面完全に停止しているため、current再検証では各gateに対応するchecker、test、probeをローカルで個別に実行します。Actions workflowやjobの存在そのものをRelease Acceptance条件にしません。

```text
required gate
  = required verification responsibility
  != GitHub Actions job required
```

過去のworkflowがgreenだったことはactual v0.2.0 releaseの履歴Evidenceとして保持しますが、後続source commitの再検証を代替しません。

## 6. Plan status policy

candidateでは次をblockerとします。

```text
Open
In Progress
Blocked
```

`Deferred`はversion固有allow-listに列挙したものだけを許可します。v0.2.0では`ISSUE-000021`だけを許可しています。

historicalには、PR #34のbootstrap Run `33531336681`で`ISSUE-000059`が、PR #40のbootstrap Run `33574397299`で`ISSUE-000062`が、それぞれGate 9で意図どおりblockされました。未解決Issueをrelease candidateへ持ち込まないpolicyが実際に機能したEvidenceとして保持します。

current再検証でも同じPlan status policyを`tools/check_release_candidate.py`から適用します。

## 7. required paths

candidate policyは、v0.2.0 scopeを支える主要な正本とExecutable Evidenceをanchorとして列挙します。

Product Value / Shape / Milestone、Interaction、Packaging、Identity / Access / Collaboration、Realization / Provider Exchange、Requirements / Scenarios / Journey、Architecture、current Contract / Profile / fixture、Go runtime / reference probes、Local Reference Package資料、V6 / V7 evaluation、Plan registry、Release Acceptance、Release Notes、release request、repository-local candidate checkerとその境界test、historical publication bundle preparation scriptをrequired pathへ含めます。

GitHub Actions停止中のcurrent policyでは、削除済みworkflowをrequired pathへ含めません。actual v0.2.0 publication時にworkflowを利用した事実は、source commitとRelease Evidenceからhistoricalに追跡します。

required pathはcoverage指標ではありません。重要な正本を黙ってcandidate scopeから外してgateを通すことを防ぐためのanchorです。

## 8. Local Reference Package gate

`go test ./...`だけでは配布artifactの再現性まで確認できないため、v0.2.0 candidateでは次を同じsource commitから再現します。

- `CGO_ENABLED=0`, Linux / amd64でreference binaryを2回buildする。
- 二つのbinaryがbyte-for-byteで一致する。
- version / source commit / targetをbuild identityとして埋め込む。
- file order、mtime、owner / groupを固定したarchiveを生成する。
- archiveのSHA-256を記録する。
- archiveを別directoryへ展開する。
- 展開したbinaryでSemantic Interchangeを保存してprocessを終了する。
- 別processでdurable data rootから再読し、期待bundleを再構成する。

この検査はreference artifactの再現性を示します。正式なcross-platform supportやproduction durabilityを示しません。

## 9. candidate reportとpublication preparation

9つの検査責務が実際に成功したcandidateについて、machine-readable reportへ少なくとも次を記録します。

- schema / version / repository / release scope
- source commit SHA / source tree SHA
- executed gate names
- observed allowed Deferred Issue
- candidate gate result
- explicit non-claims

`tools/check_release_candidate.py`は、candidate policyそのもの、required paths、Plan snapshot等を検査し、candidate reportを生成できます。このreportで`executed_gates`が列挙されることは、他の8責務をchecker自身が実行したという意味ではありません。各責務の実行結果を別途確認したうえでcandidate Evidenceを成立させます。

v0.2.0のactual publication時には、candidate reportとLocal Reference Packageをpublication前にもう一度照合しました。`tools/prepare_v0_2_0_release.py`はcandidate reportのsource commit、package checksum、release request、Release Notesを確認し、publicationへ渡すread-only bundleを作成するhistorical publication toolingとして保持します。

現在の`release-request.json`はpublication完了状態であり、current再検証から既存v0.2.0を再publicationしません。

## 10. actual Release Evidenceへの昇格条件

Release Evidenceへ昇格するには、candidate gate PASSに加えて少なくとも次が必要です。

1. actual `v0.2.0` tag / release identityが存在する。
2. tagがcandidate gateを通したsource commitへexactに結び付く。
3. 配布Artifactがtag / source commitへ追跡できる。
4. Local Reference Package bytesをdigest等で識別できる。
5. Release Notesがsupported scopeと非主張範囲を明示する。
6. tag対象commitでv0.2.0 Release Candidate Gateがsuccessしている。
7. release後のEvidence recordがtag、commit、artifact、gate resultを結び付ける。

v0.2.0では、これらを`release/v0.2.0/RELEASE_EVIDENCE.md`で確認済みです。

## 11. v0.1.0との境界

v0.1.0とv0.2.0ではrelease scopeが異なります。

```text
shared checker
  != shared policy
  != shared supported scope
```

repository-local checkerを共通化しても、各versionの`release-candidate.json`を独立したpolicyとして保持します。v0.1.0のhistorical candidate Evidenceも、その時点のcommit / tree / gate resultへ結び付いた記録として維持します。

## 12. branch / tag boundary

current local検証では、対象versionのpolicyを明示してcandidate checkerを実行します。

```bash
python3 tools/check_release_candidate.py \
  --config release/v0.2.0/release-candidate.json
```

branch名やtag eventによってGitHub Actions workflowが自動選択されることを、現在の検証経路にはしません。

actual v0.2.0 publication時には、`develop/v0.2.0`のRelease Candidate Gateがsuccessした後、同じRunの`GITHUB_TOKEN`でtagを作成しました。GitHub Actionsの再帰抑制により、このtag作成から通常のtag-push Runは別途起動していません。

このhistorical経路では、tag対象commitをpre-publication gateで検査し、その同じ`GITHUB_SHA`へtagを作ることでRelease Acceptanceを満たしました。

```text
historical publication used GitHub Actions
  != current validation uses GitHub Actions
```

GitHub Actionsを将来再開する場合は、`plan/DEVELOPMENT_WORKFLOW.md`に従って明示的にPlanを更新してから実行面を設計し直します。

## 13. failure時の扱い

candidate検査やpublication preparationのfailureは、release条件を弱める理由にはしません。

1. failureしたchecker / test / probeを特定する。
2. Product policy、checker、runtime、artifact build、release preparationのどこに原因があるか切り分ける。
3. 原因のある層を修正する。
4. 同じ検査を再実行する。
5. success後にのみEvidence状態を更新する。

`failed`を`not_verified`やPASSへ読み替えません。ローカル環境で必要な検査を実行できない場合も、未実行のまま`Not Yet Verified`として残します。

## 14. Release Candidateからactual ReleaseまでのEvidence

### 14.1 初期Release Candidate境界

PR #34ではRelease Candidate boundaryを実装し、test mergeとactual develop上で9 gateのsuccessを確認しました。actual developの最初のcandidate Evidence pointはcommit `724cba2a744582252c6ccba8322fc34a55b76b1b`、Run `33569004831`です。

このEvidenceは、その時点のcandidate成立を示すものであり、後のactual releaseそのものではありません。

### 14.2 actual v0.2.0 release source

actual release sourceは次です。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- historical Release Candidate Gate: Run `33574947445` — **success**
- GitHub Release ID: `380902898`
- Release: draft `false`, prerelease `false`

同Runでは9 gate、release preparation、publicationがすべてsuccessしています。

Local Reference Packageは、release preparationで算出したSHA-256とactual GitHub Release asset digestが一致しました。

```text
37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17
```

actual releaseのasset ID / digestを含む詳細は`RELEASE_EVIDENCE.md`を正とします。

## 15. current state

現時点の状態は次です。

- v0.2.0 Release Candidate Design: **Satisfied**
- v0.2.0 historical Release Candidate Evidence: **Satisfied**
- actual `v0.2.0` tag / GitHub Release: **Created and verified**
- Release Evidence: **Satisfied for the Local Reference Product Baseline**
- current develop再検証: **必要なときにローカル個別検査で実施**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

```text
Release Evidence Satisfied
  != every later develop commit revalidated
  != production readiness
```

## 16. Natural Japanese review

Product Value、PMS-03〜07、v0.1.0 Release Acceptance、Product Interaction、Local Single-Node Packaging、Product Access、Realization / Provider Exchange、ISSUE-000055〜000063、E3a / E3b-P1、repository-local candidate checker、release-candidate policy、historical Release Candidate Gate、actual tag / GitHub Release / asset digestを照合しました。

過去のactual publicationがGitHub Actionsで成立した事実はEvidenceとして保存しながら、現在の検証手段からは分離しました。current `release-candidate.json`は削除済みworkflowをrequired pathへ要求せず、candidate検査責務をローカルchecker、test、probeから再現できる形にしています。

candidate policy checkerが9つのgate名をreportへ記録することと、9責務を実際にすべて実行したことも分けました。未実行の検査をPASSへ読み替えず、candidate、publication、actual Release Evidence、Operational / Adoption Evidenceをそれぞれ独立して読めることを重視しています。

意味、規範強度、historical Evidenceを変えず、現在の運用として自然な日本語で読み通せることを最重要視して全文を再ドラフトしました。
