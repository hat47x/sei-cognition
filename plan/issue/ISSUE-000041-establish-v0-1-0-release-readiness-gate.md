# ISSUE-000041: v0.1.0 Release Candidate Readiness Gateを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021, ADR-0022, ADR-0023**  
Updated: 2026-09-01

## Goal

SOZA v0.1.0について、現在actual repositoryに存在するProduct Value、Requirements、Plan、Architecture、Contract、Representation Profile、Semantic Runtime、Provider Adapter、Payload Source、V6 / V7評価を、**同一commit上で再現可能に再検査するRelease Candidate Readiness Gate**として実体化する。

本Issueは、Git tagやGitHub Releaseを公開することを目的としない。

```text
Release Candidate Readiness
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## Resolution

### 1. Release Readiness Gateを実体化した

次を追加した。

```text
.github/workflows/release-readiness.yml
plan/release/V0_1_0_RELEASE_READINESS.md
```

workflowはrelease candidateの**同一Git commit**に対して、current checkerとtestを一括して再実行する。

実行対象は次である。

1. Plan registry integrity
2. Document review checker self-test
3. Document review registry integrity
4. Requirements registry checker self-test
5. Requirements / Scenario registry conformance
6. Contract v1alpha1 conformance
7. Representation Profile fixture conformance
8. commit-pinned RFC 8785 JCS Go probe
9. Go semantic runtime / Provider Adapter / Verifier / Payload Source tests
10. V6 / V7 Projection evaluation

既存checkerの意味をrelease用に再実装していない。

### 2. 文書監査台帳の構造checkerを実装した

次を追加した。

```text
plan/scripts/check_document_review_registry.py
plan/scripts/test_check_document_review_registry.py
```

checkerは日本語の自然さを自動採点しない。

検査対象は、監査工程の構造的な漏れである。

- schema
- `pending: []`
- reviewed / exclusion status語彙
- stale scope
- current Markdownの未収載
- duplicate scope

negative self-testでは、少なくとも次を実際に拒否できることを確認した。

- 無効status
- stale scope
- 未収載Markdown
- duplicate scope
- pending review

```text
Document review registry PASS
  != prose quality automatically proven
```

### 3. 初回CI failureをbaseline defectとして検出・解消した

Release Readiness Run #1:

- Run ID: `33461668149`
- Head SHA: `de834d77902646e4d3373aab69fef0e84cd8a33b`
- conclusion: **failure**
- failed step: **Check Plan registry integrity**

原因は、新規`ISSUE-000041`を作成した一方、`plan/registry.yaml`へまだ登録していなかったことである。

```text
Issueファイルがregistryにありません:
plan/issue/ISSUE-000041-establish-v0-1-0-release-readiness-gate.md
```

checker defectではなくactual planning baselineの不整合だったため、`plan/registry.yaml`を正しく同期した。failureを無視したりcheckerを弱めたりしていない。

### 4. 文書監査台帳をcurrent scopeへ同期した

`plan/document_review_registry.yaml`へ次を反映した。

- ISSUE coverageを`ISSUE-000001..ISSUE-000041`へ更新
- `plan/release/*.md`をreviewed scopeへ追加
- `pending: []`を維持

### 5. Release Readiness Gateをsuccessさせた

negative self-testを追加した確認Run:

- Workflow: `v0.1.0 Release Readiness`
- Run number: **4**
- Run ID: `33462118480`
- candidate Head SHA: `d4539322bf5cd4eca55c339c57b98a61cfa72f69`
- conclusion: **success**

全stepがsuccessした。

- Plan registry integrity: **success**
- Document review checker self-tests: **success**
- Document review registry integrity: **success**
- Requirements checker self-tests: **success**
- Requirements / Scenario registry: **success**
- Contract baseline: **success**
- Representation Profile fixtures: **success**
- commit-pinned RFC 8785 JCS probe: **success**
- semantic runtime / Provider Adapter / Verifier / Payload Source tests: **success**
- V6 / V7 Projection evaluation: **success**

Issue / registry / Traceabilityのclosure更新後も、Run #5（Run ID `33462347620`）で同じGateを再実行し、全stepがsuccessした。

## Product Value trace

### Value / Evidence boundary

本GateはV1〜V8のcurrent executable baselineを横断する。

主な統治境界:

- ADR-0018 — Product Value / Evidence governance
- ADR-0020 — Requirements / Scenario traceability
- ADR-0021 — Architecture / Contract authority
- ADR-0022 — runtime first slice
- ADR-0023 — Representation Profile

### Evidence state after resolution

- Design: **Satisfied within the readiness definition**
- Executable: **Satisfied within the release-readiness gate boundary**
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

このExecutable Evidenceは、v0.1.0候補としてcurrent baselineを同一commitで再検査できることを示す。

実際に配布されたArtifactについてのRelease Evidenceではない。

## Completion criteria

- [x] Document review registry checkerがactual repositoryで実行できる。
- [x] checkerがpending、未収載Markdown、無効status、stale scope、duplicate scopeをnegative self-testで検出できる。
- [x] Release Readiness workflowが既存のcurrent checkerを同一commitで再実行する。
- [x] Release Readiness workflowがsuccessする。
- [x] Plan integrityが本Issue / registry更新後もsuccessする。
- [x] Release / Operational / Adoption・OutcomeをSatisfiedへ昇格していない。
- [x] 文書を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行った。

## Evidence boundary

本Issueで成立したのは、**release-candidate readiness scoped Executable Evidence**までである。

```text
Release Readiness Gate PASS
  != Git tag created
  != GitHub Release published
  != distributed Artifact verified
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Product Value AcceptanceにおけるRelease Evidenceは、実際にrelease・配布されたArtifactを検証して初めて評価する。

ISSUE-000034は、保持されている直接Evidenceからhistorical M47 digest ruleを回収不能であることを確定し、historical bindingを`not_verified`のまま保持する方針でResolvedしている。Release Readinessの成功からhistorical digest規則を推測したり、過去bindingを`verified`へ昇格させたりしない。

## Follow-up

実際のv0.1.0 releaseへ進む場合は別Issueで、少なくとも次を固定する。

- release対象commit SHA
- tag
- 配布Artifact範囲
- Artifact integrity
- release notes
- Release Evidenceの記録方法
- rollback / supersession

その後のproduction利用はOperational Evidence、実利用による判断・説明・継続性等の改善はAdoption / Outcome Evidenceとして、さらに別の評価sliceで扱う。

## Reopen conditions

次の場合は本Issueを再開するか、release-readiness gateの修正Issueを作成する。

- current checkerを追加・変更したのにreadiness gateから漏れた。
- document review registry checkerがactual Markdownを正しく追跡できない反例が見つかった。
- 同一candidate commitで再実行できない非決定的なgateが見つかった。
- readiness PASSがRelease Evidenceとして誤用される運用が発生した。

## Natural Japanese review

Product Value Acceptance、SOZA Value Traceability、ADR-0018 / 0020 / 0021 / 0022 / 0023、ISSUE-000034のrecovery closure、Release Readiness Run `33461668149`のfailure、修正後のRun `33461800915`、negative self-test追加後のRun `33462118480`、closure Run `33462347620`、current checkerとdocument review registryへ戻ってResolutionを照合した。その後、release readinessと実release、Executable EvidenceとRelease Evidenceを混同しないことを固定し、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
