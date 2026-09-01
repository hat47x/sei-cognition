# ISSUE-000059: v0.2.0 Release Candidateのsupported scopeと統合gateを実体化する

Status: **In Progress**  
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

v0.2.0 candidateでは、同じsource commitについて少なくとも次を再検査する。

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

- [ ] version-aware candidate checkerを実装し、v0.1.0 policyの再現性を維持する。
- [ ] `release/v0.2.0/release-candidate.json`を追加する。
- [ ] v0.2.0 Release Candidate Gateを`develop/v0.2.0` / `v0.2.0` tagで実行できる。
- [ ] Local Reference Packageのdeterministic artifact検査をcandidate gateへ含める。
- [ ] candidate reportへsource commit / tree / executed gates / non-claimsを記録する。
- [ ] candidate gateの途中でOpen / In Progress / Blocked Issueを検出した場合はFAILする。
- [ ] component CIとcandidate gateがactual GitHub Actionsでsuccessする。

### Evidence / documentation

- [ ] `release/v0.2.0/RELEASE_ACCEPTANCE.md`を正本化する。
- [ ] `release/README.md`とPMS-07をcurrent stateへ同期する。
- [ ] Document Review Registryへ新規文書を反映する。
- [ ] candidate PASSをRelease / Operational / Adoption・Outcomeへ昇格させない。
- [ ] 全文を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行う。

## CI failure handling

本Issueの作業中にCI failureが発生した場合、release条件を弱めて通さない。

1. failureしたgateを特定する。
2. Product policy、checker、workflow、runtime、fixtureのどの層に原因があるかを切り分ける。
3. 原因のある層を修正する。
4. 同じ検査を再実行する。
5. successを確認した後にのみ本IssueをResolvedへ進める。

## Non-goals

- actual `v0.2.0` tag / GitHub Releaseの作成
- production platform supportの決定
- E3b live TEI / SaaS / AI integrationの実装
- production credential / secret management
- production Storage / HA / DR設計の完成
- Operational / Adoption KPIの固定

## Natural Japanese review

Product Value、PMS-04〜07、v0.1.0 Release Acceptance、Local Reference Package、Product Interaction、Product Access、Realization / Provider Exchange、E3a外部artifact integration、5段階Evidenceへ戻ってscopeを整理した。v0.2.0をproduction完成版へ見せず、現在再現できるLocal Reference Product Baselineをrelease候補として固定すること、actual releaseとcandidate gateを分けること、E3b / E4やproduction securityを非主張範囲へ残すことを中心に据えている。そのうえで、意味・規範強度・Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。