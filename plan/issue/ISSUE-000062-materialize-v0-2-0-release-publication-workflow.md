# ISSUE-000062: v0.2.0 actual release publication workflowを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021, ADR-0029**  
Updated: 2026-09-02

## Goal

v0.2.0のRelease Candidate Gateが成功したcommitだけを、再現可能な手順でactual `v0.2.0` tag / GitHub Releaseへpublishできるようにする。

手作業で一度だけtagを作るのではなく、candidate検査、配布bundleの準備、tag作成、GitHub Release作成、release asset添付の境界をworkflowとして固定する。

```text
candidate gate PASS
  → release publication workflow
  → tag / GitHub Release
  → Release Evidence audit
```

本Issueはpublication mechanismを扱う。actual Release Evidenceの評価とPMS-07の最終判定は、publish後の別Issueで行う。

## 背景

ISSUE-000059により、v0.2.0はLocal Reference Product Baselineとしてcandidate scopeが定義された。その後もdevelopではE3b-P1 public live Provider integrationと、actual TEI実行の前段となるexternal executable injection boundaryまで実装が進んでいる。

実装開始時の基準点 `c8c6fab583a60fc31f13348ccd2a895ef058eba2` では、Release Candidate Gate Run `33572742329`、Plan integrity Run `33572742370`、External Integration E3a Run `33572742330`、External Integration E3b Run `33572742309`、Semantic Runtime Conformance Run `33572742418`、Local Package Artifact Run `33572742415`がsuccessしていた。

一方、repositoryにはまだ`v0.2.0` tagもGitHub Releaseも存在しない。

また、E3b-P1やTEI executable注入境界がrepository内に存在することと、v0.2.0のsupported scopeへ含めることは同じではない。v0.2.0のrelease scopeは既存Release AcceptanceどおりE3aまでとし、後続のE3b実証は追加のscoped Evidenceとして保持する。

Release Acceptanceでは、Release Evidenceへ進む条件として少なくとも次を求めている。

- tag / release identityが存在する。
- tagが検査済みsource commitへexactに結び付く。
- 配布Artifactがsource commitへ追跡できる。
- Local Reference Package bytesをdigestで識別できる。
- release notesがsupported scopeと非主張範囲を明示する。
- tag対象commitでcandidate検査がsuccessしている。

これらを人手の記憶に依存させず、repository内のrelease policyと同じく再現可能にする必要がある。

## Resolution

v0.2.0のpublicationを、既存Release Candidate Gateの後段に置く二段階構成として実装した。

PRでは`prepare-v0-2-0-release` jobだけが動作し、candidate report、Local Reference Package、checksum、Release Notes、release requestをread-onlyで照合する。actual `v0.2.0` tag / GitHub Releaseを作る`publish-v0-2-0` jobは、`develop/v0.2.0`へのpushでRelease Candidate Gateとrelease preparationが成功した場合だけ実行される。

write権限はpublication jobだけへ限定した。PR上の検査や通常のcandidate jobには`contents: write`を与えない。

既存tagがある場合は、検査済みsource commitと一致する場合だけ再利用する。別commitを指すtagは上書きせずfailureとする。tag作成後にRelease作成だけが失敗した場合は、同じcommitを指すtagを確認したうえで再実行できる。

Release Notesでは、repositoryにE3b-P1やTEI executable injection boundaryのScoped Evidenceが存在していても、v0.2.0のsupported scopeはE3aまでであることを明記した。

bootstrap PR #40のRun `33574397299`ではGate 1〜8がすべてsuccessし、Gate 9だけが`ISSUE-000062`をblocking Plan Issueとして検出してfailureした。これはpublication実装の不具合ではなく、未解決Issueをcandidateへ持ち込まない既存policyが意図どおり機能した結果である。

本Issue自身がcandidate blockerであるため、実装成立とblocker動作を確認したこの時点でResolvedへ移す。closure後は同じPRで全9 gateとread-only release preparationを再実行し、失敗した場合は本IssueをReopenする。

## Design

### 1. Release Candidate Gateをpublicationの前提にする

actual publicationは独立した無条件workflowにしない。

既存`Release Candidate Gate` workflowへ、release-candidate jobを前提とするrelease preparation / publication jobを追加する。

```text
release-candidate job success
  → release-preparation
  → publish-v0.2.0 (develop push only)
```

PRではpublicationしない。read-onlyのrelease preparationだけを実行し、release assetとして必要な入力が一貫していることを検査する。

### 2. write権限をpublication jobだけへ限定する

release-candidateとrelease-preparationは`contents: read`で動作させる。

`contents: write`は、`develop/v0.2.0`へのpushかつrelease-candidate success後に動く`publish-v0-2-0` jobだけへ与える。

PR上のコードがwrite権限で実行される構成にはしない。

### 3. release requestをmachine-readableにする

`release/v0.2.0/release-request.json`へ、version、tag、target branch、release scope、artifact target、publication request state等を固定する。

release requestはUniversal Semantic Contractではなく、v0.2.0固有のrelease operation policyである。

### 4. PRでrelease bundleをdry-runする

Release Candidate Gateが生成したcandidate reportとLocal Reference Packageをdownloadし、`tools/prepare_v0_2_0_release.py`で次を検査する。

- candidate reportのversion / repository / release scope
- candidate reportのsource commitが現在のworkflow commitと一致する。
- candidate gate resultがPASSである。
- package checksumが実bytesと一致する。
- release requestとrelease notesがv0.2.0 scopeに一致する。

検査後、publicationに必要なpackage / checksum / candidate report / release metadataを一つのprepared release artifactとして保存する。

### 5. develop pushだけがactual publishする

PR merge後の`develop/v0.2.0` pushでRelease Candidate Gateがsuccessした場合だけ、prepared release artifactを使って次を行う。

1. `v0.2.0` tagがなければ、検査した`GITHUB_SHA`へlightweight tagを作る。
2. tagが既にある場合は、同じcommitを指すことを確認する。異なるcommitならfailureとする。
3. GitHub Releaseがなければ、`RELEASE_NOTES.md`を本文として作成する。
4. Local Reference Package、checksum、candidate report、release metadataをrelease assetとして添付する。
5. 同じreleaseが既に存在する場合は、同一tagを確認したうえでno-opとする。

publication途中でtagだけが作られた場合も、同じcommitを指していれば再実行でRelease作成を継続できるようにする。

## Release notes

`release/v0.2.0/RELEASE_NOTES.md`では、少なくとも次を自然な日本語で明示する。

- v0.2.0はLocal Reference Product Baselineである。
- semantic / Product Interaction / Local Packaging / Product Access責務分離 / E3aまでがsupported scopeである。
- repository内にE3b-P1やTEI executable injectionのScoped Evidenceが存在しても、それらをv0.2.0のsupported scopeへ自動昇格させない。
- E3b全体 / E4、production IAM / Storage / security、formal platform supportは主張しない。
- Release EvidenceとOperational / Adoption Evidenceは別である。

## Acceptance criteria

### Design / implementation

- [x] release requestをmachine-readableに追加する。
- [x] release notesを自然な日本語で正本化する。
- [x] candidate report / package checksumを検査するrelease preparation scriptを追加する。
- [x] Release Candidate Gateへread-only release preparation jobを追加する。
- [x] actual publication jobのwrite権限を`develop/v0.2.0` push時だけに限定する。
- [x] tagの既存・不一致・部分publishを安全に扱う。
- [x] package / checksum / candidate report / metadataをRelease assetへ含める。

### PR verification

- [x] IssueがIn Progressの状態でGate 9がblockerとして機能することを確認する。Run `33574397299`でGate 1〜8 success、Gate 9のself-blockを確認した。
- [x] implementation確認後に本IssueをResolvedへ移す。
- [ ] closure headで9 gateすべてをsuccessさせる。
- [ ] PR上のrelease preparation dry-runをsuccessさせる。
- [ ] PRではtag / GitHub Releaseが作られないことを確認する。

### Post-merge verification

- [ ] develop merge commitでRelease Candidate Gateがsuccessする。
- [ ] publication jobが`v0.2.0` tag / GitHub Releaseを作成する。
- [ ] tag対象commitのcandidate gateがsuccessしていることを確認する。
- [ ] actual Release Evidence評価を別Issueへ引き継ぐ。

## Evidence state

- Design Evidence: **Satisfied for the publication boundary**
- Executable Evidence: **bootstrap scoped evidence available** — Run `33574397299`でGate 1〜8 success、Gate 9 self-blockを確認
- closure-head Release Candidate / preparation Evidence: **Not Yet Verified until post-closure CI success**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Evidence boundary

本Issueでpublication workflowが成立しても、その時点だけではRelease EvidenceをSatisfiedへ上げない。

```text
publication mechanism verified
  != release exists

release exists
  != Operational Evidence
  != Adoption / Outcome Evidence
```

actual tag、GitHub Release、release asset、tag対象commitのgate resultを確認した後、別IssueでRelease Evidenceを評価する。

## CI failure handling

closure後の全9 gate、release preparation、またはdevelop merge後のpublicationがfailureした場合、release条件を弱めて通さない。

1. failureしたjob / stepを特定する。
2. candidate policy、preparation script、workflow、artifact identity、GitHub publicationのどこに原因があるか切り分ける。
3. 本IssueをReopenする。
4. 原因のある層を修正する。
5. 同じ検査を再実行する。
6. success確認後にのみclosureを維持する。

## Non-goals

- E3b-P2 actual TEI executionの実装
- external Cognitive Methodのlive実行
- E4 Operational portability
- production signing / notarization
- cross-platform installer
- package repositoryへの配布
- production security assessment
- Operational / Adoption KPIの評価

## Reopen条件

- PRではpublicationしないという境界が破れる。
- release-candidate failureでもpublishできてしまう。
- tagが別commitを指していても上書きできてしまう。
- package checksumとrelease asset bytesの対応を検証できない。
- closure headの9 gateまたはrelease preparationがfailureする。
- actual develop publicationがfailureする。

## Natural Japanese review

v0.2.0 Release Acceptance、ISSUE-000059〜000061、Product Milestone、Release Candidate Gate、Local Reference Package、E3b-P1とTEI executable injection boundary、5段階Evidenceへ戻り、candidate検査とactual publicationを別の責務として整理した。とくに、PRではread-onlyの準備だけを検証し、write権限はcandidate success後のdevelop pushへ限定することで、release操作を安全側に倒している。

bootstrap Runの結果も反映し、Gate 1〜8の成功とGate 9のself-blockを、publication成立やRelease Evidenceへ過大評価せず記録した。E3b-P1等の後続実験が存在してもv0.2.0のsupported scopeはE3aまでとし、repositoryに存在するEvidenceとreleaseでsupportを主張する範囲を分離した。actual Release Evidenceはpublication mechanismの成立とは別に扱い、tag / GitHub Release / asset / gate resultを実観測した後に評価する。意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
