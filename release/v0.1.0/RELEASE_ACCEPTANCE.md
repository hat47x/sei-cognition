# SOZA v0.1.0 Release Acceptance

更新日: 2026-09-01  
状態: **Release candidate acceptance defined / Release Evidence Not Yet Verified**

## 1. 目的

この文書は、SOZA v0.1.0について、release candidateとして何を再検査し、actual release後に何が確認できた場合だけRelease Evidenceと呼べるかを定めます。

Product Value上のEvidence高さは`product/value/SOZA_VALUE_ACCEPTANCE.md`とADR-0018を正とします。

```text
Executable Evidence
  != Release Candidate Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Release Candidate Evidenceは、5段階Evidenceへ新しいUniversal段階を追加するものではありません。Executable Evidenceのうち「特定のrelease候補commitを統合gateで検査した」というrelease準備上の下位分類です。

## 2. v0.1.0のrelease scope

v0.1.0は、production operational productの完成版ではなく、**semantic development baselineを再現可能なsource releaseとして固定するversion**です。

対象には少なくとも次を含みます。

- Product Value / Value Model / Value Acceptance
- Vision / Principles
- Product Requirements / Acceptance Scenarios
- ADR / Issue / Plan registry
- Reference Architecture / traceability
- current Semantic Contract family
- JSON Schema / fixtures / validators
- current Representation Profiles
- first semantic runtime
- synthetic Provider Adapter
- Representation Verifier Registry
- synthetic Payload Source
- V6 / V7 Projection evaluation harness

## 3. v0.1.0で主張しないこと

candidate gateやactual source releaseが成立しても、次は自動的にSatisfiedへ上げません。

- production Provider integration
- production Storage integration
- live authorization / credential integration
- production workflow / agent execution
- production streaming verification
- historical M47 digest Profile verification
- Operational Evidence
- Adoption / Outcome Evidence

```text
source baseline released
  != production system operated
```

## 4. candidate identity

release candidateは少なくとも次で特定します。

```text
repository = hat47x/soza
version = 0.1.0
source commit SHA
source tree SHA
```

commit SHAを`release-candidate.json`へ固定してはなりません。設定ファイル自身を変更するとcommitが変わる自己参照を避けるためです。

Release Candidate Gateは実行時にGitからcommit / tree SHAを取得し、derived reportへ記録します。

## 5. Release Candidate Gate

同一checkoutで次を順に再実行します。

1. Plan registry integrity
2. Requirements Registry checker self-tests
3. current Requirements / Scenario registry conformance
4. current Contract fixture conformance
5. current Representation Profile fixture conformance
6. commit-pinned RFC 8785 JCS Go probe
7. semantic runtime / Provider Adapter / Verifier / Payload Source Go tests
8. V6 / V7 Projection evaluation
9. release candidate policy / required-path validation

個別workflowの古いgreen runを集計するだけでは、candidate gateの代替にしません。

## 6. Plan status policy

release candidateでは、次をblockerとします。

```text
Open
In Progress
Blocked
```

`Deferred`は無条件に許可しません。`release-candidate.json`の`allowed_deferred_issues`へversion固有に列挙したものだけ許可します。

v0.1.0では次だけを許可します。

```text
ISSUE-000021
```

ISSUE-000021は、historical chat export等が得られた場合のdesign-history provenance再監査であり、current semantic baselineの意味・実装・release再現性を止めるblockerではないためです。

このallow-listはUniversal Plan ontologyではなく、v0.1.0 candidate policyです。

## 7. required paths

candidate configurationは、release scopeを支える主要pathを列挙します。

checkerは設定ファイルに必要pathが存在することだけでなく、v0.1.0で外してはならない最低限のanchorがpolicyから削除されていないことも確認します。

これにより、gateを通すためにcandidate設定から重要な正本やruntimeを黙って外すことを防ぎます。

## 8. candidate report

candidate gateが最後まで成功した場合、machine-readable reportを生成します。

最低限:

- schema
- version
- repository
- source commit SHA
- source tree SHA
- executed gate names
- observed deferred issues
- candidate gate result
- `release_evidence = false`
- `operational_evidence = false`
- `adoption_outcome_evidence = false`

reportはCI artifactとして保存できますが、その存在自体はactual releaseを意味しません。

## 9. actual Release Evidenceへの昇格条件

Release Evidenceへ昇格するには、candidate gate PASSに加えて少なくとも次が必要です。

1. actual release tag / release identityが存在する。
2. tagがcandidate gateを通したsource commitへexactに結び付く。
3. 配布Artifactがそのtag / commitへ追跡できる。
4. custom配布Artifactがある場合、そのbytesをdigest等で識別できる。
5. release notesがv0.1.0 scopeと非主張範囲を明示する。
6. tag対象commitでRelease Candidate Gate相当の検査がsuccessしている。
7. release後のEvidence recordがtag、commit、artifact、gate resultを結び付ける。

GitHubがcommitから生成するsource archiveだけを配布する場合も、少なくともtagとcommitの対応をEvidenceとして残します。

## 10. main統合との関係

`develop/v0.1.0`でcandidate gateがPASSしただけではreleaseしません。

`main`へfast-forwardまたは同一commitを保つ方法で統合する場合、candidate commit identityを維持できます。

merge commit等によりrelease対象commitが変わる場合は、その新しいcommitについてRelease Candidate Gateを再実行します。

```text
candidate A tested
  + different release commit B
  != B tested
```

## 11. tag push

Release Candidate Gate workflowは`develop/**`、`main`に加え`v*` tag pushでも起動できる設計とします。

actual `v0.1.0` tag作成後は、tagが指すcommitで同じ統合gateがsuccessしたことをRelease Evidence記録へ含めます。

## 12. failure時の扱い

candidate gate failureは、release条件を弱める理由ではありません。

1. どのsub-gateが失敗したかを確認する。
2. Product / Contract / checker / runtime / policyのどの層が誤っているかを切り分ける。
3. 原因のある層を修正する。
4. 同一統合gateを再実行する。
5. success後にだけcandidate statusを更新する。

## 13. Release Evidence記録

actual release後に、たとえば次を`RELEASE_EVIDENCE.md`へ記録します。

```text
version
tag
release URL or identity
source commit SHA
source tree SHA
candidate gate run ID
candidate report artifact
custom artifact digest, if any
release scope
explicit non-claims
```

このEvidence文書はrelease後の記録であり、tag対象source treeへ自己参照的に事前埋め込みする必要はありません。

## 14. current state

このRelease Acceptanceとcandidate gateを整備した時点では、v0.1.0はまだactual releaseされていません。

したがって状態は次です。

- Release Candidate design: **Satisfied**
- Release Candidate executable gate: **gate success後に評価**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 15. 自然な日本語レビュー

SOZA_VALUE_ACCEPTANCE、ADR-0018、DEVELOPMENT_WORKFLOW、current Product / Requirements / Contract / Profile / runtime / evaluation、current Plan状態を照合しました。そのうえで、v0.1.0をsemantic development baselineのsource releaseとするscope、candidate identity、統合gate、actual releaseへの昇格条件、非主張範囲を整理しました。最後に、Evidence高さや技術的条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
