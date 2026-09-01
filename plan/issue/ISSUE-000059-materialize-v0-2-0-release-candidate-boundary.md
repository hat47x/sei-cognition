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

v0.1.0では、semantic development baselineをsource release候補として検査するRelease Candidate Gateを実装した。

v0.2.0では、その後に次の範囲が増えている。

- Cognitive Method current Contract / runtime
- cross-Contract bundle-local Exact Binding consistency
- end-to-end Product Journey harness
- human / machine Product Interaction reference probe
- Local Single-Node Packaging / Persistence probe
- Linux / amd64 Local Reference Package artifact
- Product Access / Selective Disclosure reference probe
- out-of-process Realization / Provider exchange
- version-pinned external artifact integration（PMS-06 E3a）

一方、次はまだ未検証である。

- E3b live external process / service integration
- E4 Operational portability
- production IdP / IAM / credential lifecycle
- production Storage / HA / backup SLA
- formal OS / architecture support matrix
- production security assessment
- Adoption / Outcome Evidence

したがって、v0.2.0 Release Candidateでは「既に実証した範囲を一つの候補commitへ束ねて再検査すること」と「未検証領域をrelease scopeへ紛れ込ませないこと」の両方が必要になる。

## Resolution

v0.2.0のRelease Candidateを、production完成版ではなく **Local Reference Product Baseline** の候補として定義した。

release candidate checkerはv0.1.0 / v0.2.0のversion固有policyを読み分ける構造へ一般化し、release scope、required path、required gate、Deferred Issueのallow-list、非主張範囲は各versionのpolicyへ残した。共通checkerを用いても、v0.1.0とv0.2.0のrelease scopeは混在しない。

v0.2.0では従来のsemantic / Requirements / Contract / Representation Profile / Projection検査に加え、Linux / amd64 Local Reference Packageについて、同じ候補commitからの二重build一致、deterministic archive、checksum、archive展開後の独立process save / resumeを統合gateへ含めた。

PR #34のbootstrap Run `33531336681`ではGate 1〜8がすべてsuccessし、Gate 9だけが`ISSUE-000059 = In Progress`をblockしてfailureとなった。これはrelease条件を弱めたfailureではなく、「未解決Issueを候補へ持ち込まない」というPlan blocker policyが実際に機能することを確認した結果である。

本Issue自身がcandidate blockerであるため、実装成立を確認した時点でIssueをResolvedへ移し、同一PRで全9 gateを再実行した。途中、Registry全置換時に`ISSUE-000013`の既存ファイル名を誤って転記し、Run `33568527280`のGate 1がfailureしたが、実ファイル名へ戻した後、Plan integrity Run `33568653098`とRelease Candidate Gate Run `33568653099`がsuccessした。

Run `33568653099`ではGate 1〜9、Local Reference Package artifact upload、candidate report uploadがすべてsuccessしている。External Integration E3a Run `33568653077`もsuccessした。

```text
implementation boundary resolved
  + PR test merge all-gate PASS
  != actual develop head PASS
  != Release Evidence
```

## Supported scope

v0.2.0 Release Candidateが直接対象とするのは、次のLocal Reference Product Baselineである。

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

このscopeは正式Web UI、MCP、API protocol等を固定しない。

### 3. local package / persistence

- Local Single-Node Profile
- Linux / amd64 Local Reference Package
- deterministic build / archive
- durable data rootへのsave / reload
- archive展開後の別processからのresume

このscopeは正式installer、package manager、全platform supportを意味しない。

### 4. access / collaboration separation

- authentication identityとBounded Subjectの分離
- Product access permissionとsemantic Responsibility / Authorityの分離
- Selective Disclosureでの`withheld`保持

このscopeはproduction IAM / RBAC / ABACを意味しない。

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

個別workflowの過去green runを集めただけでは、この統合gateの代わりにしない。

## Version boundary

v0.1.0とv0.2.0は別々のrelease policyを持つ。

`tools/check_release_candidate.py`はversion-awareに一般化するが、各versionのscope、required path、required gate、非主張範囲はversion固有policyとして保持する。

```text
shared checker
  != shared release scope
```

v0.2.0の変更によって、v0.1.0 candidate policyを暗黙に書き換えない。

## Plan blocker policy

candidateでは次をblockerとする。

```text
Open
In Progress
Blocked
```

`Deferred`はversion固有allow-listに列挙したものだけを許可する。

v0.2.0でも、現時点では`ISSUE-000021`だけを許可対象とする。これはhistorical design provenanceの再監査であり、current Product baselineの意味・build・candidate再現性を止める課題ではないためである。

bootstrap Run `33531336681`では、`ISSUE-000059`がIn Progressの状態でGate 9が意図どおりfailureした。これにより、blocker policyを単なる文書上の規則ではなくExecutable Evidenceとして確認できた。

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
- [x] candidate reportへsource commit / tree / executed gates / non-claimsを記録する。
- [x] Open / In Progress / Blocked IssueをGate 9でblockする。bootstrap Run `33531336681`で`ISSUE-000059`のblockを実確認した。
- [x] PR #34のclosure検証で全9 gateをsuccessさせる。Run `33568653099`で確認した。

### Evidence / documentation

- [x] `release/v0.2.0/RELEASE_ACCEPTANCE.md`を正本化する。
- [x] v0.2.0 candidate policyへsupported scopeと非主張範囲をmachine-readableに固定する。
- [x] Document Review Registryへ新規文書を反映する。
- [x] candidate PASSをRelease / Operational / Adoption・Outcomeへ昇格させない。
- [x] candidate reportとLocal Reference Package artifactのidentityを記録する。
- [x] 全文を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行う。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Satisfied for the scoped v0.2.0 candidate boundary**
- PR #34 test merge Release Candidate Evidence: **Satisfied** — Run `33568653099`
- candidate report artifact: ID `9824110337`, digest `sha256:2d71979ec4f466bd679178bae88b2ba32584ec121d8618217b9b70d2c79a216a`
- Local Reference Package artifact: ID `9824109925`, digest `sha256:6b319c6ac2cd0aeb98a13d6234e6c1d9c06ae09a10927a3b54fa48878fc46fa6`
- actual `develop/v0.2.0` head Release Candidate Evidence: **Not Yet Verified until merge後のactual headで再検査**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## CI failure handling

本Issueのclosure後に全9 gateのfailureが発生した場合、release条件を弱めて通さない。

1. failureしたgateを特定する。
2. Product policy、checker、workflow、runtime、fixtureのどの層に原因があるかを切り分ける。
3. 本IssueをReopenする。
4. 原因のある層を修正する。
5. 同じ検査を再実行する。
6. successを確認した後にのみclosureを維持する。

今回のRun `33568527280`でも、この手順に従いRegistry転記ミスを修正してからRun `33568653099`をsuccessさせた。

## Non-goals

- actual `v0.2.0` tag / GitHub Releaseの作成
- production platform supportの決定
- E3b live TEI / SaaS / AI integrationの実装
- production credential / secret management
- production Storage / HA / DR設計の完成
- Operational / Adoption KPIの固定

## Reopen条件

- Release Candidate Gateで9 gateのいずれかがfailureする。
- v0.1.0 policyがv0.2.0対応によって意味的に変質したことが判明する。
- Local Reference Packageのartifact identityまたはresume検査が再現できない。
- E3b / E4やproduction領域をv0.2.0 candidateが暗黙に主張してしまう。
- blocker policyがOpen / In Progress / Blocked Issueを見逃す。

## Natural Japanese review

Product Value、PMS-04〜07、v0.1.0 / v0.2.0 Release Acceptance、Local Reference Package、Product Interaction、Product Access、Realization / Provider Exchange、E3a外部artifact integration、5段階Evidence、actual GitHub Actions Evidenceへ戻ってscopeを整理した。v0.2.0をproduction完成版へ見せず、現在再現できるLocal Reference Product Baselineをrelease候補として固定すること、actual releaseとcandidate gateを分けること、E3b / E4やproduction securityを非主張範囲へ残すことを中心に据えている。

bootstrap Runとpost-closure Runの両方を踏まえ、Issue自身がcandidate blockerとなる自己参照、途中のRegistry転記ミス、修正後の全9 gate successを、Evidenceの強さを誇張しない形で記録した。意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
