# ISSUE-000041: v0.1.0 Release Evidence境界とrelease candidate gateを定義する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-09-01

## Goal

SOZA v0.1.0について、current Executable Evidenceを「release済み」と誤認せず、**どのcommit / artifact / gate結果が揃えばrelease candidateと呼べるか、さらに何が起きた後にだけRelease Evidenceへ昇格できるか**を具体化する。

```text
release candidate gate PASS
  != Release Evidence

Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

新しいUniversal semantic conceptは追加しない。ADR-0018でAccepted済みの5段階Evidenceを、v0.1.0 release processへ具体化する。

## Background

current repositoryでは、Product / Requirements / Architecture / Contract / Profile / runtimeの基線と、限定されたExecutable Evidenceが成立している。

一方、`SOZA_VALUE_ACCEPTANCE.md`が定めるRelease Evidenceは、**実際に配布・releaseされたArtifactについて必要な性質を確認できること**である。

現在はまだ、次が一つの再現可能なrelease candidate gateとして固定されていない。

- release対象version / scope
- candidate source commit identity
- Plan / Requirements / Contract / Profile / runtime / Projection evaluationの統合再検査
- Deferred Issueをrelease blockerとして扱うかの明示policy
- actual tag / releaseとcandidate commitの一致条件
- release後に記録するEvidence
- Release EvidenceからOperational / Outcomeへ過大昇格しない条件

## Product / Requirement trace

主に次へ関係する。

- V1 Historical Reconstruction
- V3 Revision Integrity
- V6 Human / AI Readability
- V8 Execution Independence
- REQ-0001 — 耐久的な意味の連続性
- REQ-0009 — Revision / Supersessionの完全性
- REQ-0018 — Storage実装から意味を独立させる
- REQ-0020 — Evidenceを超える達成主張をしない
- ADR-0018 — Product Value / Evidence高さ
- ADR-0020 — Requirements traceability / Evidence boundary
- ADR-0021 — Architecture / Contract authority and versioning

## v0.1.0 release scope

v0.1.0は、production operational productの完成版ではなく、**current semantic development baselineを再現可能なsource releaseとして固定する段階**とする。

release対象には、少なくとも次を含む。

- Product Value / Vision / Principles
- Product Requirements / Acceptance Scenarios
- Accepted ADR / current Plan registry
- Reference Architecture
- current Semantic Contract / JSON Schema
- current Representation Profile
- fixture / validator / conformance tool
- first semantic runtime
- synthetic Provider Adapter
- Representation Verifier Registry
- synthetic Payload Source
- V6 / V7 Projection evaluation harness

次はv0.1.0 Release Evidenceの必須主張にしない。

- production Provider integration
- production Storage integration
- production workflow / agent execution
- live authorization provider
- Operational Evidence
- Adoption / Outcome Evidence
- historical M47 digest Profile verification

## Release candidate boundary

### Candidate identity

release candidateは少なくとも次で一意に特定する。

```text
repository
version
source commit SHA
source tree SHA
```

candidate gateのreportは検査したcommit / treeを記録する。

### Integrated candidate gate

同一checkoutで少なくとも次を再実行する。

1. Plan registry integrity
2. Requirements Registry checker self-test / current registry conformance
3. current Contract fixture conformance
4. current Representation Profile fixture conformance
5. commit-pinned JCS Go probe
6. semantic runtime / Provider Adapter / Verifier / Payload Source Go tests
7. V6 / V7 Projection evaluation
8. release candidate policy / required-path check

個別workflowの過去runがgreenだったという事実だけをcandidate gateの代替にしない。

### Plan status policy

candidate gateでは、原則として次をrelease blockerとする。

```text
Open
In Progress
Blocked
```

`Deferred`は自動的に許可せず、v0.1.0 policyで明示的に列挙したIssueだけ許可する。

current baselineでは、historical chat export等が得られた場合の再監査留保である`ISSUE-000021`だけをcandidate-local allowed deferred issueとする。

このallow-listはUniversal Plan ontologyではない。

## Release Evidence boundary

candidate gateがPASSしてもRelease Evidenceにはしない。

Release Evidenceへ昇格するには、少なくとも次が必要である。

1. actual release tag / release identityが存在する。
2. release tagがcandidate gateを通したsource commitへexactに結び付く。
3. 配布Artifactがそのrelease identityへ追跡できる。
4. custom配布Artifactを作る場合はdigest等でArtifact bytesを識別できる。
5. release notesがv0.1.0 scopeと非主張範囲を明示する。
6. tag / release対象commitについてcandidate gate相当の検査がsuccessしている。
7. release後のEvidence recordがtag、commit、artifact、gate結果を結び付ける。

```text
source commit tested
  != artifact released

artifact released
  != production operation verified
```

## Required deliverables

- `release/README.md`
- `release/v0.1.0/RELEASE_ACCEPTANCE.md`
- `release/v0.1.0/release-candidate.json`
- `tools/check_release_candidate.py`
- `.github/workflows/release-candidate.yml`
- candidate gateが生成するmachine-readable report
- release候補のEvidence境界をREADME / traceabilityへ必要な範囲で同期

## Candidate configuration requirements

`release-candidate.json`には少なくとも次を持たせる。

- schema ID
- version
- release scope
- required repository paths
- allowed deferred issues
- prohibited Plan statuses
- required local gates
- explicit non-claims

candidate commit SHAそのものをsource tree内の設定へ埋め込まない。自己参照を避け、実行時にGitから取得してreportへ記録する。

## Candidate report requirements

candidate gateは少なくとも次をmachine-readableに出力する。

- version
- repository
- commit SHA
- tree SHA
- checked_at等のCI由来時刻を正本にしないこと
- executed gate names
- allowed deferred issues observed
- release_evidence = false
- operational_evidence = false
- adoption_outcome_evidence = false

時刻がなくてもcommit / tree / gate結果で再現できることを優先する。

## Non-goals

- このIssueだけでactual GitHub Releaseを作成すること。
- `develop/v0.1.0`のgate PASSだけでRelease EvidenceをSatisfiedへ上げること。
- production deploymentをrelease条件へ混ぜること。
- Deferred Issueを一般に無条件許可すること。
- release versionをUniversal semantic identityへすること。
- source archiveの物理URLをSOZA semantic identityへすること。
- Release EvidenceをOperational / Adoption・Outcome Evidenceへ自動昇格させること。

## Completion criteria

- [ ] v0.1.0 release scopeと非主張範囲が明記される。
- [ ] candidateとactual releaseのEvidence高さが分離される。
- [ ] 同一checkoutでcurrent主要gateを再実行できる。
- [ ] candidate commit SHA / tree SHAをreportへ記録できる。
- [ ] required path欠落を検出できる。
- [ ] Open / In Progress / Blocked Issueをrelease blockerにできる。
- [ ] Deferredはcandidate-local allow-listに限定できる。
- [ ] ISSUE-000021が許可Deferredとして明示される。
- [ ] candidate gate自身がCIでsuccessする。
- [ ] candidate gate PASSをRelease Evidenceへ過大昇格していない。
- [ ] 文書を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行う。

## Follow-up / actual release

このIssueをResolvedにしても、v0.1.0 Release Evidenceは原則として`Not Yet Verified`のままとする。

actual tag / releaseを作る段階では、必要なら後続Issueで次を行う。

- candidate source commitを固定する。
- `main`統合方式を確認する。
- tag / releaseを作る。
- tag対象commitでcandidate gateを再確認する。
- release Artifact identity / digestを記録する。
- `release/v0.1.0/RELEASE_EVIDENCE.md`等へactual release Evidenceを記録する。
- その時点で初めて、対象scopeのRelease Evidence状態を更新する。

## CI / verification

最低限、次を確認する。

- Plan integrity
- Release Candidate Gate
- candidate gate内の全sub-gate

CI failureが出た場合は、Product ValueやContractを安易に弱めず原因のある層を修正し、successを確認してから後続作業へ進む。

## Natural Japanese review

SOZA_VALUE_ACCEPTANCE、ADR-0018、ADR-0020、ADR-0021、DEVELOPMENT_WORKFLOW、current 6 CI系統、current Plan状態へ戻り、Release EvidenceとExecutable Evidenceの間に残っていた具体化不足を整理した。v0.1.0をpre-operationalなsemantic source baselineとして扱い、candidate gateとactual releaseを分離したうえで、意味、Evidence強度、非主張範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
