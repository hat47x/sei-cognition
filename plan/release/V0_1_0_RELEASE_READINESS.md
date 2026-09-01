# SOZA v0.1.0 Release Readiness

更新日: 2026-09-01  
状態: **Release Candidate Readiness Baseline — Gate Verified**

## 1. この文書の役割

この文書は、SOZA v0.1.0のrelease candidateについて、**同一commit上で何を再検査すれば「release候補として検査可能な状態」と判断できるか**を定めます。

実際のtag作成やGitHub Release公開の手順書ではありません。

```text
Release Candidate Readiness
  != Released Artifact
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Product Value AcceptanceにおけるRelease Evidenceは、実際に配布・releaseされたArtifactを対象とします。本readiness gateの成功だけではRelease Evidenceは成立しません。

## 2. Gateの原則

### 2.1 同一commitを再検査する

個別workflowの過去PASSを寄せ集めてrelease候補のPASSとはみなしません。

release候補commitに対して、current checkerを一つのworkflow内で再実行します。

### 2.2 正本を増やさない

Release Readiness workflowは、既存のPlan、Requirements、Contract、Representation Profile、Runtime、Projection Evaluationの意味を再定義しません。

それぞれのcheckerをそのまま呼び出します。

### 2.3 failureを情報として扱う

failureが出た場合、gateを弱めて通すことを目的にしません。

- actual baseline defect
- checker defect
- dependency / environment defect

を分け、責任を持つ層で修正します。

### 2.4 文書監査を構造的に確認する

自然な日本語の品質そのものを自動採点しません。

一方で、current Markdown文書が`plan/document_review_registry.yaml`のreviewed scopeから漏れていないこと、`pending`が残っていないことは機械検査します。

negative self-testでは無効status、stale scope、未収載Markdown、duplicate scope、pending reviewを拒否できることも確認します。

## 3. Gate構成

Release Readiness workflowでは、次を同一commitで実行します。

### A. Planning

```bash
python3 -m py_compile \
  plan/scripts/check_plan_registry.py \
  plan/scripts/next_plan_id.py \
  plan/scripts/check_requirements_registry.py \
  plan/scripts/test_check_requirements_registry.py \
  plan/scripts/check_document_review_registry.py \
  plan/scripts/test_check_document_review_registry.py

python3 plan/scripts/check_plan_registry.py
cd plan/scripts && python3 test_check_document_review_registry.py && cd ../..
python3 plan/scripts/check_document_review_registry.py
```

### B. Requirements

```bash
python3 plan/scripts/test_check_requirements_registry.py
python3 plan/scripts/check_requirements_registry.py
```

### C. Contract

```bash
python -m pip install --disable-pip-version-check -r tools/contract-check-requirements.txt
python tools/check_contract_conformance.py
```

### D. Representation Profile

```bash
python3 tools/check_representation_profiles.py
```

RFC 8785 JCSについては、current Representation Profile workflowと同じcommit-pinned Go probeを別temp moduleで実行します。

### E. Semantic Runtime

```bash
cd runtime/go
go test ./...
```

対象にはcurrent semantic runtime、synthetic Provider Adapter、Representation Verifier Registry、Payload Source boundaryが含まれます。

### F. V6 / V7 Projection Evaluation

```bash
python evaluation/v6-v7/check_projection_evaluation.py
```

## 4. Release candidateとして固定するもの

readiness判定の単位はGit commit SHAです。

```text
release candidate identity = exact Git commit SHA
```

branch名だけでは候補を固定しません。

workflow success後にbranchが進んだ場合、新しいcommitは別candidateとして再検査します。

## 5. Gate成功時に言えること

同一commitで全stepがsuccessした場合、次を主張できます。

- current Plan / Issue / ADR registryが構造的に整合している。
- current Markdown開発文書がdocument review registryのreviewed scopeから漏れていない。
- document review checkerが主要なnegative caseを拒否できる。
- current Requirements / Scenario registryが構造的に整合している。
- current Contract fixtureがconformanceを満たす。
- current Representation Profile fixtureとJCS probeがconformanceを満たす。
- current Go runtime testが成功する。
- current V6 / V7 evaluation harnessが成功する。
- これらを**同じcandidate commit**で再現できる。

## 6. Gate成功時にも言えないこと

次は自動的には成立しません。

- v0.1.0が実際にreleaseされた。
- 公開・配布Artifactが同じ性質を持つ。
- production Provider / Storage / Executionで成立した。
- 実利用者が意味を十分理解できた。
- 判断品質や業務成果が改善した。

```text
Release Readiness Gate PASS
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## 7. Executable Evidence

### 初回failure

Release Readiness Run #1:

- Run ID: `33461668149`
- Head SHA: `de834d77902646e4d3373aab69fef0e84cd8a33b`
- conclusion: **failure**

Plan integrityが、`ISSUE-000041`のregistry未登録を検出した。checkerを弱めず、`plan/registry.yaml`をactual issue fileへ同期して解消した。

### baseline同期後のsuccess

Release Readiness Run #3:

- Run ID: `33461800915`
- Head SHA: `06ba51455a511235cab99356bd578fac2c5db149`
- conclusion: **success**

Plan、document review、Requirements、Contract、Representation Profile / JCS、Go runtime、V6 / V7 evaluationが同一commitでsuccessした。

### negative self-test追加後の確認

Release Readiness Run #4:

- Run ID: `33462118480`
- Head SHA: `d4539322bf5cd4eca55c339c57b98a61cfa72f69`
- conclusion: **success**

追加したdocument review checker self-testを含め、全stepがsuccessした。

### closure更新後の確認

Release Readiness Run #5:

- Run ID: `33462347620`
- Head SHA: `a0726d5ff65845e3b417632d4dccc5eaee196b6a`
- conclusion: **success**

Issue / registry / Value Traceabilityのclosure更新後も全stepがsuccessし、Status変更を含む候補headに回帰がないことを確認した。

これらはrelease-candidate readinessに対するExecutable Evidenceです。

```text
Release Readiness Gate PASS
  = release-readiness scoped Executable Evidence
  != Release Evidence
```

## 8. historical M47の扱い

ISSUE-000034では、GitHub reachable history、Library、code inventory等からhistorical M47 digest-producing sourceを回収できず、**現在保持された直接Evidenceからdigest ruleを回収不能であることを確定**しました。

そのためIssueはResolvedですが、historical bindingは`not_verified`のまま保持します。

```text
ISSUE-000034 Resolved
  != historical M47 Profile verified
```

current Profile / Runtime / Release Readinessが成立しても、historical digestをcurrent Profileへ推測で対応付けません。新たな一次資料が得られた場合は別途再開できます。

## 9. 実際のreleaseへ進む条件

本readiness gateがsuccessした後も、実際のtag / GitHub Releaseを作る場合は別Issueで少なくとも次を固定します。

- release対象commit SHA
- tag名
- 配布Artifactの範囲
- Artifact integrityの検査方法
- release notes
- Release Evidenceとして何を記録するか
- rollback / supersession方針

## 10. 自然な日本語ドラフト

Product Value Acceptance、Value Traceability、current workflowとchecker、ISSUE-000034のrecovery closure、Run `33461668149`のfailure、Run `33461800915` / `33462118480` / `33462347620`のsuccess、ISSUE-000041のEvidence境界へ戻って内容を照合しました。その後、候補準備と実release、Issue closureとVerification、Executable EvidenceとRelease Evidenceを混同しないことを固定し、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
