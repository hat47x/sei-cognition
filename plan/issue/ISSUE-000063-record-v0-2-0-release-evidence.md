# ISSUE-000063: v0.2.0 actual Release Evidenceを記録する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021, ADR-0029**  
Updated: 2026-09-02

## Goal

actual `v0.2.0` tag、GitHub Release、release asset、Release Candidate Gate、source commitの対応を実観測し、v0.2.0 Local Reference Product BaselineについてRelease Evidenceを評価する。

publication mechanismの設計やPR上のdry-runではなく、**actual releaseが存在し、その配布物を検査済みsource commitへ追跡できること**を対象とする。

あわせて、release成立後の`develop/v0.2.0`更新を同じ`v0.2.0`の再publicationとして扱わないよう、version固有のpublication lifecycleを完了状態へ閉じる。

## 背景

ISSUE-000062では、Release Candidate Gate成功後だけactual releaseをpublishできるworkflowを実装した。

PR #40のread-only検証では全9 gateとrelease preparationがsuccessし、PR上ではpublicationがskippedされることを確認した。その後PR #40を`develop/v0.2.0`へmergeし、actual merge commit `c3640bdfcc43652b63a5b9941fd6b472312ec28f`でRelease Candidate Gate Run `33574947445`を実行した。

同Runでは9 gate、release preparation、publicationがすべてsuccessし、actual `v0.2.0` tagとGitHub Releaseが作成された。

この時点で初めて、Release Acceptanceのactual Release Evidence条件を実在するtag / release / assetへ照合できる。

一方、publication workflowをそのままにすると、release後の新しい`develop/v0.2.0` commitでも同じ`v0.2.0` tagをpublishしようとし、既存tagのExact Bindingと新しいbranch HEADが不一致になる。releaseの不変性を保ったまま開発を継続するには、「candidate revalidation」と「同じversionのpublication request」を分離する必要がある。

## Resolution

`release/v0.2.0/RELEASE_EVIDENCE.md`を作成し、actual release identity、tag ref、source commit、candidate run、package digest、release asset ID / digestを一つのEvidence recordへ結び付けた。

確認した中心的な事実は次である。

- `v0.2.0` tagは`c3640bdfcc43652b63a5b9941fd6b472312ec28f`を直接指す。
- 同source commitでRelease Candidate Gate Run `33574947445`が9 gateすべてsuccessした。
- 同Runのrelease preparationがLocal Reference PackageについてSHA-256 `37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17`を算出した。
- GitHub Release上のpackage asset digestも同じSHA-256である。
- GitHub Release `v0.2.0`はdraftでもprereleaseでもなく、4つのexpected assetを持つ。
- Release Notesはv0.2.0のsupported scopeをE3aまでに限定し、E3b / E4やproduction領域を非主張として残している。
- actual release成立後、`release-request.json`を`publish: false / publication_state: completed`へ移し、後続candidate検査から同versionの再publicationを分離した。

これにより、v0.2.0 Local Reference Product BaselineについてRelease EvidenceをSatisfiedと評価する。

```text
Release Evidence Satisfied
  != production readiness
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## Actual release identity

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- GitHub Release ID: `380902898`
- GitHub Release URL: `https://github.com/hat47x/sei-cognition/releases/tag/v0.2.0`
- published: `2026-09-02T00:21:59Z`
- draft: `false`
- prerelease: `false`

## Candidate / publication Evidence

Release Candidate Gate Run `33574947445`:

- Gate 1〜9: **success**
- release preparation: **success**
- actual publication: **success**

同じsource commitについて次もsuccessした。

- Plan integrity Run `33574947407`
- External Integration E3a Run `33574947323`
- External Integration E3b Run `33574947359`

E3bのsuccessはv0.2.0 release scopeをE3bへ広げる根拠には用いない。

## Release assets

- package: asset ID `540358086`, digest `sha256:37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17`
- checksum: asset ID `540358088`, digest `sha256:271a9eb445af6edb3913e04a9cbf4d2407f551db3533d42958cc3eb927093d38`
- candidate report: asset ID `540358089`, digest `sha256:1362a70dae32f44b7c6d5972fa9272260fd816f451e5ddbc4b0f4e811147f15c`
- release metadata: asset ID `540358087`, digest `sha256:31e082e45100449e6c92bb9d0d797665007ce36577252787f3227f4f84149b59`

prepared publication bundle:

- GitHub Actions artifact ID: `9826285457`
- digest: `sha256:28555fd7f2664040363d65fa6350f599442077ef8e8fcb2c1d132e0611ab5162`

## Tag-triggered workflowの扱い

publication jobは`GITHUB_TOKEN`でtagを作成する。GitHub Actionsの再帰抑制により、このtag作成から通常のtag-push workflowは別Runとして起動しなかった。

ただしRelease Acceptanceが要求するのは「tag対象commitでcandidate gateがsuccessしていること」であり、tag作成前の同一publication Run `33574947445`で、tag対象commit`c3640bdf...`が9 gateを通過している。さらにpublish jobはtagを当該`GITHUB_SHA`へだけ作成し、異なる既存tagは上書きしない。

したがって、今回のreleaseについてtag対象commitの検査はSatisfiedとする。

一方、workflowに残しているtag triggerは、手動または外部credential等からtagが作成された場合の独立検査経路として維持する。

## Publication lifecycle closure

actual release成立後は、`v0.2.0` tagを後続develop commitへ付け替えない。

`release-request.json`の状態を次へ移した。

```text
publish = false
publication_state = completed
```

Release Candidate Gateはversion固有requestを読み、publication requestが完了している場合も9 gateのcandidate revalidation自体は継続する。一方、release preparationとpublication jobはskipする。

```text
future develop commit
  → candidate revalidation
  != v0.2.0 retag
  != v0.2.0 republish
```

この境界の導入途中では、workflow更新commit `f6477e3c89ec01a970c48cb6f3f55a0830744ff2`に対するRun `33585287867`が`Resolve release publication lifecycle`でfailureした。原因はworkflowを先に更新した時点で、旧release requestに`publication_state`がまだ無かったためである。

直後のcommit `55403445907cd465031f63e09f2a7f77bc47995c`でrelease requestを`completed`へ同期し、Release Candidate Gate Run `33585297218`を再実行した。結果は9 gateすべてsuccessで、`prepare-v0-2-0-release`と`publish-v0-2-0`は意図どおりskippedとなった。

このfailureは条件を弱めず、version固有release stateの不整合を修正して同じ検査を通し直すことで解消した。

## Acceptance criteria

- [x] actual `v0.2.0` tagが存在する。
- [x] tagがcandidate gate済みsource commitをexactに指す。
- [x] actual GitHub Releaseが存在し、draft / prereleaseではない。
- [x] expected 4 assetが存在する。
- [x] Local Reference Packageのprepared SHA-256とrelease asset digestが一致する。
- [x] tag対象commitのRelease Candidate Gateがsuccessしている。
- [x] Release Notesがsupported scopeと非主張範囲を明示する。
- [x] actual releaseのtag / commit / artifact / gate resultを`RELEASE_EVIDENCE.md`へ正本化する。
- [x] actual release後にpublication requestを`completed`へ閉じ、後続develop commitで同じtagを再publicationしない。
- [x] publication完了後もcandidate gateを継続し、release preparation / publicationのみをskipできることをactual CIで確認する。
- [x] Release EvidenceをOperational / Adoption・Outcome Evidenceへ昇格させない。
- [x] 全文を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行う。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Satisfied for the scoped candidate/publication mechanism**
- Release Evidence: **Satisfied for v0.2.0 Local Reference Product Baseline**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Non-goals

- E3b全体をv0.2.0 supported scopeへ追加すること
- actual TEI CLI integrationの完了を主張すること
- E4 Operational portabilityの証明
- production IAM / Storage / securityの証明
- formal platform support matrixの確定
- Operational / Adoption KPIの評価

## Reopen条件

- `v0.2.0` tagがrelease source commit以外を指していることが判明する。
- release assetが記録したdigestと一致しないことが判明する。
- candidate report / release metadataからsource commitを追跡できないことが判明する。
- Release Notesがsupported scopeを誤ってE3b / production領域へ拡張していることが判明する。
- release完了後のdevelop pushが`v0.2.0`再publicationを試行する。
- Release EvidenceをOperational / Adoption Evidenceとして誤って利用していることが判明する。

## Natural Japanese review

Release Acceptance、Release Notes、Release Evidence、release request、ISSUE-000059〜000062、actual tag ref、GitHub Release API、Run `33574947445`のcandidate / preparation / publication各job、package digest、release後のRun `33585297218`を照合した。

publication mechanismの成功とactual releaseの実在を分けたうえで、後者に必要なtag、commit、asset、digest、gate resultが揃ったことをRelease Evidenceとして記録している。さらに、release成立後はversion固有publication requestを完了状態へ閉じ、後続develop commitのcandidate revalidationと同じversionの再publicationを分離した。

`GITHUB_TOKEN`によるtag作成がtag-push Runを再帰起動しない点も、未検証や失敗と混同しないよう整理した。一方、E3b / E4やproduction領域はこのreleaseから切り離したままとした。意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
