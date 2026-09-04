# ISSUE-000059: v0.2.0 Release Candidateのsupported scopeと統合gateを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021, ADR-0029**  
Updated: 2026-09-02

## Goal

PMS-07「release可能な製品として成立する」へ進むため、SOZA v0.2.0で実際にsupportする範囲と、release candidateとして同一source commitを再検査する統合gateを定義・実装する。

v0.2.0はproduction完成版として扱わない。現在Executable Evidenceが揃っている範囲を、開発者・評価者が再現可能な **Local Reference Product Baseline** として固定する。

```text
reference product baseline
  != production service
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## 背景

v0.1.0ではsemantic development baselineをsource release候補として検査するRelease Candidate Gateを実装した。その後、v0.2.0では次の範囲が増えた。

- Cognitive Method current Contract / runtime
- cross-Contract bundle-local Exact Binding consistency
- end-to-end Product Journey harness
- human / machine Product Interaction reference probe
- Local Single-Node Packaging / Persistence probe
- Linux / amd64 Local Reference Package artifact
- Product Access / Selective Disclosure reference probe
- out-of-process Realization / Provider exchange
- version-pinned external artifact integration（PMS-06 E3a）

一方、E3b live external process / service integration、E4 Operational portability、production IAM / Storage / security、formal platform support matrix等は未検証である。

そのため、v0.2.0 Release Candidateでは「既に実証した範囲を一つの候補commitへ束ねて再検査すること」と「未検証領域をrelease scopeへ紛れ込ませないこと」を同時に求めた。

## Resolution

v0.2.0のRelease Candidateを、production完成版ではなく **Local Reference Product Baseline** の候補として定義した。

release candidate checkerはv0.1.0 / v0.2.0のversion固有policyを読み分ける構造へ一般化し、release scope、required path、required gate、Deferred Issueのallow-list、非主張範囲は各versionのpolicyへ残した。共通checkerを使っても、v0.1.0とv0.2.0のrelease scopeは混在しない。

v0.2.0では従来のsemantic / Requirements / Contract / Representation Profile / Projection検査に加え、Linux / amd64 Local Reference Packageについて、同じ候補commitからの二重build一致、deterministic archive、checksum、archive展開後の独立process save / resumeを統合gateへ含めた。

### bootstrap verification

PR #34のbootstrap Run `33531336681`ではGate 1〜8がsuccessし、Gate 9だけが`ISSUE-000059 = In Progress`を意図どおりblockした。これにより、「未解決Issueを候補へ持ち込まない」というPlan blocker policyがExecutableに確認できた。

本Issue自身がcandidate blockerであったため、実装成立を確認した時点でIssueをResolvedへ移し、同一PRで全9 gateを再実行した。

### failure and recovery

closure後の初回Run `33568527280`では、Registry全置換時に既存`ISSUE-000013`のファイル名を誤って転記したためGate 1がfailureした。release条件を弱めず、実ファイル名へ戻した後に再実行し、Plan integrity Run `33568653098`とRelease Candidate Gate Run `33568653099`をsuccessさせた。

最終文書同期後のPR test mergeでも、Release Candidate Gate Run `33568925573`、Plan integrity Run `33568925534`、External Integration E3a Run `33568925477`がsuccessした。

### actual develop verification

PR #34を`develop/v0.2.0`へmergeしたcommit `724cba2a744582252c6ccba8322fc34a55b76b1b`について、push-triggered検査を改めて実行した。

- Release Candidate Gate Run `33569004831` — **success**
- Plan integrity Run `33569004843` — **success**
- External Integration E3a Run `33569004842` — **success**

Release Candidate Gateでは9 gateすべてに加え、candidate reportとLocal Reference Packageのartifact uploadもsuccessした。

- candidate report artifact ID: `9824232506`
- candidate report artifact digest: `sha256:f6c9326e6af415654df80446893c5ba5c847fccd4e2d7192806b7056eb6c781d`
- Local Reference Package artifact ID: `9824232197`
- Local Reference Package artifact digest: `sha256:13bb5ed0ba8ab39e817a5dadc952e8bfb8934df9965474aa8435718136138ac7`

このcommitを、v0.2.0の最初の**actual develop candidate Evidence point**として扱う。

```text
implementation boundary resolved
  + actual develop candidate Evidence point established
  != v0.2.0 tag exists
  != Release Evidence
```

## Supported scope

v0.2.0 Release Candidateが直接対象とするLocal Reference Product Baselineは次のとおりである。

### 1. semantic baseline

- Product Value / Product Shape / Product Milestone
- current Requirements / Acceptance Scenarios
- current Architecture / Contract / Representation Profile
- 39-fixture Contract Conformance baseline
- Go semantic runtime

### 2. usable reference interaction

- human-oriented / machine-oriented reference Surface
- canonical stateの共有
- light / audit Projection境界

正式Web UI、MCP、API protocol等は固定しない。

### 3. local package / persistence

- Local Single-Node Profile
- Linux / amd64 Local Reference Package
- deterministic build / archive
- durable data rootへのsave / reload
- archive展開後の別processからのresume

正式installer、package manager、全platform supportはscope外である。

### 4. access / collaboration separation

- authentication identityとBounded Subjectの分離
- Product access permissionとsemantic Responsibility / Authorityの分離
- Selective Disclosureでの`withheld`保持

production IAM / RBAC / ABACを意味しない。

### 5. Realization / Provider portability

- in-process synthetic exchange
- out-of-process reference exchange
- version-pinned external artifact integration（E3a）

E3b live external service integrationとE4 Operational portabilityはscope外とする。

## Release Candidate Gate

v0.2.0 candidateでは、同じsource commitについて次を再検査する。

1. Plan integrity
2. Requirements Registry
3. Contract Conformance
4. Representation Profile fixtures
5. commit-pinned RFC 8785 JCS probe
6. semantic runtime / reference probesのGo test
7. V6 / V7 Projection evaluation
8. Local Reference Packageのdeterministic build / archive / independent-process resume
9. v0.2.0 candidate policy / bound report

過去の個別workflowがgreenであることを、この統合gateの代わりにはしない。

## Version boundary

v0.1.0とv0.2.0は別々のrelease policyを持つ。

```text
shared checker
  != shared release scope
```

`tools/check_release_candidate.py`はversion-awareに共通化したが、各versionのscope、required path、required gate、非主張範囲はversion固有policyとして保持する。

## Plan blocker policy

candidateでは`Open`、`In Progress`、`Blocked`をblockerとする。`Deferred`はversion固有allow-listに列挙したものだけを許可する。

v0.2.0では`ISSUE-000021`だけを許可対象とする。これはhistorical design provenanceの再監査であり、current Product baselineの意味・build・candidate再現性を止める課題ではないためである。

bootstrap Run `33531336681`で、本policyが実際に未解決Issueを拒否することを確認した。

## Explicit non-claims

candidate gateがsuccessしても、actual tag / releaseが存在するまではRelease Evidenceへ昇格しない。

また、v0.2.0 candidateから次を主張しない。

- production Provider integration
- E3b live external process / service integration
- E4 Operational portability
- production Storage integration
- production identity / security
- formal platform support matrix
- Operational Evidence
- Adoption / Outcome Evidence

```text
candidate gate PASS
  != actual release
  != production readiness
```

## Acceptance criteria

### Design

- [x] v0.2.0のsupported scopeをLocal Reference Product Baselineとして限定する。
- [x] E3aをscopeへ含め、E3b / E4を非主張範囲へ残す。
- [x] v0.1.0とv0.2.0のrelease policyを分離する。

### Executable

- [x] version-aware candidate checkerを実装し、v0.1.0 policyの意味を維持する。
- [x] `release/v0.2.0/release-candidate.json`を追加する。
- [x] v0.2.0 Release Candidate Gateを`develop/v0.2.0` / `v0.2.0` tag / 対象PRで実行できる。
- [x] Local Reference Packageのdeterministic artifact検査をcandidate gateへ含める。
- [x] Open / In Progress / Blocked IssueをGate 9でblockする。
- [x] PR test mergeで全9 gateをsuccessさせる。
- [x] actual `develop/v0.2.0` Evidence pointで全9 gateをsuccessさせる。Run `33569004831`。

### Evidence / documentation

- [x] `release/v0.2.0/RELEASE_ACCEPTANCE.md`を正本化する。
- [x] v0.2.0 candidate policyへsupported scopeと非主張範囲をmachine-readableに固定する。
- [x] Document Review Registryへ新規文書を反映する。
- [x] candidate reportとLocal Reference Package artifactのidentityを記録する。
- [x] candidate PASSをRelease / Operational / Adoption・Outcomeへ昇格させない。
- [x] 全文を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行う。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Satisfied for the scoped v0.2.0 candidate boundary**
- PR #34 test merge Release Candidate Evidence: **Satisfied**
- actual `develop/v0.2.0` candidate Evidence point: **Satisfied** — commit `724cba2a...`, Run `33569004831`
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

Evidence文書の更新自身によってHEADが変わるため、Evidence pointを「常に最新HEADでなければならない」とはしない。Releaseへ進む際には、actual tag対象commitを改めてexactに検査する。

## CI failure handling

本Issueのclosure後にRelease Candidate Gateがfailureした場合、release条件を弱めて通さない。

1. failureしたgateを特定する。
2. Product policy、checker、workflow、runtime、fixtureのどの層に原因があるかを切り分ける。
3. 必要なら本IssueをReopenする。
4. 原因のある層を修正する。
5. 同じ検査を再実行する。
6. successを確認した後にのみclosureを維持する。

Run `33568527280`ではこの手順に従い、Registry転記ミスを修正してから再検証した。

## Non-goals

- actual `v0.2.0` tag / GitHub Releaseの作成
- production platform supportの決定
- E3b live TEI / SaaS / AI integrationの実装
- production credential / secret management
- production Storage / HA / DR設計の完成
- Operational / Adoption KPIの固定

## Reopen条件

- Release Candidate Gateで9 gateのいずれかが再現不能になる。
- v0.1.0 policyがv0.2.0対応によって意味的に変質したことが判明する。
- Local Reference Packageのartifact identityまたはresume検査が再現できない。
- E3b / E4やproduction領域をv0.2.0 candidateが暗黙に主張してしまう。
- blocker policyがOpen / In Progress / Blocked Issueを見逃す。

## Natural Japanese review

Product Value、PMS-04〜07、v0.1.0 / v0.2.0 Release Acceptance、Local Reference Package、Product Interaction、Product Access、Realization / Provider Exchange、E3a external artifact integration、PR #34、actual `develop/v0.2.0`のGitHub Actions Evidenceへ戻ってscopeを整理した。

bootstrap self-block、途中のRegistry転記ミス、PR test mergeの全gate success、actual developでの再検証を一続きのEvidence履歴として整理しつつ、candidate成立をactual Releaseやproduction readinessへ拡張しない境界を維持している。意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
