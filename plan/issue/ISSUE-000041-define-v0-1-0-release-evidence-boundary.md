# ISSUE-000041: v0.1.0 Release Evidence境界とrelease candidate gateを定義する

Status: **Resolved**  
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

新しいUniversal semantic conceptは追加しない。ADR-0018でAccepted済みの5段階Evidenceをv0.1.0 release processへ具体化する。

## Resolution

v0.1.0を**semantic development baselineのsource release**として扱うrelease acceptanceと、同一checkoutでcurrent主要gateを再実行するRelease Candidate Gateを実体化した。

actual GitHub ReleaseやtagはこのIssueでは作成しない。

したがって、このIssueのResolvedは次を意味する。

```text
release candidate boundary implemented
  != v0.1.0 released
  != Release Evidence satisfied
```

## Implemented deliverables

### Release governance

```text
release/README.md
release/v0.1.0/RELEASE_ACCEPTANCE.md
release/v0.1.0/release-candidate.json
```

`RELEASE_ACCEPTANCE.md`では次を固定した。

- v0.1.0 release scope
- explicit non-claims
- candidate commit / tree identity
- integrated candidate gate
- Deferred Issue allow-list policy
- actual tag / releaseへの昇格条件
- `main`統合後にcommitが変わる場合の再検査
- actual release後のEvidence record

### Candidate policy checker

```text
tools/check_release_candidate.py
```

checkerは少なくとも次を検査する。

- configuration schema / version / repository / release scope
- mandatory required-path anchorsがpolicyから削除されていないこと
- declared required pathsがcandidate treeに存在すること
- required gate setが弱められていないこと
- explicit non-claimsがfalseのままであること
- Plan registryのOpen / In Progress / Blockedが存在しないこと
- Deferredがcandidate-local allow-listに限定されること
- allow-listのstale entryがないこと
- Git HEAD commit / tree SHAを取得できること

成功時はmachine-readable candidate reportを生成する。

### Integrated workflow

```text
.github/workflows/release-candidate.yml
```

同一checkoutで次を再実行する。

1. Plan registry integrity
2. Requirements Registry checker self-test / conformance
3. Contract conformance
4. Representation Profile fixture conformance
5. commit-pinned RFC 8785 JCS Go probe
6. semantic runtime / Provider Adapter / Verifier / Payload Source Go tests
7. V6 / V7 Projection evaluation
8. release candidate policy / bound report

reportはCI artifactとして保存する。

## v0.1.0 release scope

v0.1.0はproduction operational product完成版ではない。

対象:

- Product Value / Vision / Principles
- Requirements / Acceptance Scenarios
- ADR / Plan
- Reference Architecture
- Semantic Contract / Schema
- Representation Profile
- fixtures / validators / tools
- first semantic runtime
- synthetic Provider Adapter
- Representation Verifier Registry
- synthetic Payload Source
- V6 / V7 evaluation harness

非主張:

- production Provider integration
- production Storage integration
- production workflow / agent execution
- live authorization provider
- Operational Evidence
- Adoption / Outcome Evidence
- historical M47 digest Profile verification

## Plan status policy

release candidate blocker:

```text
Open
In Progress
Blocked
```

`Deferred`は無条件許可せず、v0.1.0 configのallow-listへ列挙したIssueだけ許可する。

current allow-list:

```text
ISSUE-000021
```

ISSUE-000021はhistorical chat export等が得られた場合のdesign-history provenance再監査であり、current semantic baselineのrelease再現性を止めないためである。

## Release Evidence boundary

candidate gateがPASSしてもRelease Evidenceへ昇格しない。

actual Release Evidenceには少なくとも次を要求する。

1. actual release tag / release identity
2. tagとcandidate-tested source commitのexactな対応
3. 配布Artifactからtag / commitへの追跡
4. custom artifactがある場合のbytes digest
5. scope / non-claimsを明示したrelease notes
6. tag対象commitでのRelease Candidate Gate相当のsuccess
7. tag / commit / artifact / gateを結ぶrelease Evidence record

## Completion criteria

- [x] v0.1.0 release scopeと非主張範囲を明記した。
- [x] candidateとactual releaseのEvidence高さを分離した。
- [x] 同一checkoutでcurrent主要gateを再実行するworkflowを実装した。
- [x] candidate commit SHA / tree SHAをreportへ記録する実装を追加した。
- [x] required path欠落を検出できる。
- [x] Open / In Progress / Blocked Issueをrelease blockerにするpolicyを追加した。
- [x] Deferredをcandidate-local allow-listに限定した。
- [x] ISSUE-000021を許可Deferredとして明示した。
- [x] candidate gate PASSをRelease Evidenceへ過大昇格しない境界を固定した。
- [x] 文書を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行った。
- [x] closure commitに対するRelease Candidate Gateのactual CI successをEvidenceとして確認した。

## Closure Evidence

Release Candidate Gateを追加したclosure commitそのものについて、actual GitHub Actionsで統合gateのsuccessを確認した。

- source commit: `4ee3f75753972e56fff8ab9f88b977cfe3d7b67b`
- source tree: `0f7bcfa297fe83ca05b9e297c5897b6f1a354b70`
- Release Candidate Gate Run: `33462821768` — **success**
- job: `99716406410` — **success**
- Plan integrity Run: `33462821772` — **success**
- candidate report artifact ID: `9783773779`
- artifact name: `soza-v0.1.0-release-candidate-4ee3f75753972e56fff8ab9f88b977cfe3d7b67b`
- artifact digest: `sha256:3efef517ffdcc1c5588f9ab5893059ae1c4239354e58c79036b0e4c244697113`

Release Candidate Gateでは、Plan、Requirements、Contract、Representation Profile、commit-pinned JCS probe、semantic runtime、V6/V7 Projection、candidate policy / reportの各gateが同一checkoutでsuccessした。

この記録は`4ee3f757...`という特定候補commitに対するRelease Candidate Evidenceである。Evidence追記などでsource treeが変わった場合は、新しいcommitについてgateを再実行する。

また、CI artifactにはretention期限があるため、artifactの存在期間をRelease Evidenceの恒久性と同一視しない。Run metadata、source commit / tree、実release後のEvidence recordを別途結び付ける。

```text
candidate report artifact exists
  != source released
  != Release Evidence satisfied
```

## Follow-up / actual release

v0.1.0 Release EvidenceはこのIssue closure時点では**Not Yet Verified**である。

actual release段階では後続Issueで、少なくとも次を行う。

- candidate source commitを固定する。
- `main`統合方法を確認する。
- tag / releaseを作る。
- tag対象commitでRelease Candidate Gateを再確認する。
- release Artifact identity / digestを記録する。
- `release/v0.1.0/RELEASE_EVIDENCE.md`へactual Evidenceを記録する。
- その時点で初めて対象scopeのRelease Evidence状態を更新する。

## CI / verification

closure commitのactual Evidence:

- Plan integrity Run `33462821772`: **success**
- Release Candidate Gate Run `33462821768`: **success**
- candidate gate内の全sub-gate: **success**

今後の変更でCI failureを検出した場合も、原因のある層を修正し、successを確認してから後続作業へ進む。

## Natural Japanese review

SOZA_VALUE_ACCEPTANCE、ADR-0018、ADR-0020、ADR-0021、DEVELOPMENT_WORKFLOW、current CI、current Plan、実装したrelease policy / checker / workflow、actual closure CIを相互照合した。そのうえで、v0.1.0をpre-operationalなsemantic source baselineとして扱い、candidate gateとactual releaseを分離した。最後に、意味、Evidence強度、非主張範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
