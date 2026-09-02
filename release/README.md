# SOZA release管理

更新日: 2026-09-02  
状態: **v0.2.0 Release Evidence available for the Local Reference Product Baseline**

## 1. このディレクトリの役割

`release/`は、SOZAのversion固有のrelease scope、Release Candidateの受入れ条件、actual release、release後のEvidenceを管理します。

release planning、candidate、actual release、実運用は同じものではありません。

```text
release planning
  != Release Candidate Gate PASS
  != actual release
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Product Value上のEvidence高さは`product/value/SOZA_VALUE_ACCEPTANCE.md`とADR-0018を正とします。

## 2. versionごとの配置

version固有資料は次へ置きます。

```text
release/vX.Y.Z/
```

v0.2.0では、少なくとも次を管理しています。

- `RELEASE_ACCEPTANCE.md` — supported scopeとcandidate / actual releaseの受入れ条件
- `release-candidate.json` — machine-readableなcandidate policy
- `release-request.json` — actual publicationのversion固有request
- `RELEASE_NOTES.md` — actual GitHub Releaseへ掲示する説明
- `RELEASE_EVIDENCE.md` — actual tag / commit / artifact / gate resultを結び付けるEvidence record

checkerやworkflowを共通化しても、versionごとのsupported scopeまで共通化しません。

```text
shared checker
  != shared release scope
```

## 3. Release Candidate Evidence

Release Candidate Gateは、source treeへ固定SHAを書き込まず、実行時のcommit / tree SHAをcandidate reportへ記録します。

CI reportやworkflow artifactはderived Evidenceです。Product ValueやSemantic Contractのsource-of-truthではありません。

v0.2.0では、PR #34でRelease Candidate boundaryを確立した後、actual `develop/v0.2.0`でも継続して回帰検査を行いました。actual release source commit `c3640bdfcc43652b63a5b9941fd6b472312ec28f`については、Release Candidate Gate Run `33574947445`で9 gateすべてがsuccessしています。

## 4. v0.2.0 actual Release Evidence

`v0.2.0`は、**Local Reference Product Baseline**としてactual GitHub Releaseになりました。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- GitHub Release ID: `380902898`
- Release Candidate Gate: Run `33574947445` — success
- Release Evidence: `release/v0.2.0/RELEASE_EVIDENCE.md`

Local Reference Packageのprepared SHA-256とactual Release asset digestは、次の値で一致しています。

```text
37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17
```

これにより、candidate gateで検査・準備したpackage bytesと、actual Releaseで配布しているpackage bytesを同一digestで追跡できます。

## 5. v0.2.0のsupported scope

v0.2.0は、semantic baselineに加えて、Product Interaction、Local Single-Node Packaging、Product Access責務分離、Realization / Provider交換、E3a version-pinned external artifact integrationまでを、開発者・評価者向けのLocal Reference Product Baselineとして固定します。

release source commitにはE3b-P1 public live Provider integrationやTEI executable injection boundaryのScoped Executable Evidenceも存在します。しかし、**repositoryに後続Evidenceが存在することと、v0.2.0でsupportを主張することは分けます**。

v0.2.0のsupported scopeはE3aまでです。

次はこのreleaseから主張しません。

- E3b live external integration全体
- actual TEI CLI integrationの完了
- E4 Operational portability
- production Provider / Storage integration
- production identity / security
- formal platform support matrix
- Operational Evidence
- Adoption / Outcome Evidence

```text
v0.2.0 released
  != production readiness
```

## 6. tag作成とcandidate gate

v0.2.0 publicationでは、Release Candidate Gate Run `33574947445`がsource commit `c3640bdf...`を検査した後、同じRunのpublish jobがその`GITHUB_SHA`へ`v0.2.0` tagを作成しました。

`GITHUB_TOKEN`で作成したtagはGitHub Actionsの再帰抑制により、通常のtag-push workflowを別Runとして起動していません。このため、今回の自動publicationでは次をEvidence chainとします。

```text
same source commit
  → candidate gate 9/9 PASS
  → release preparation PASS
  → tagを同じGITHUB_SHAへ作成
  → GitHub Release作成
```

手動・外部credential等からtagを作成する場合に備え、tag trigger自体はcandidate workflowに残しています。

## 7. failureの扱い

candidate / publicationのfailureは、条件を弱める理由にはしません。

failureが生じた場合は、Plan policy、checker、runtime、artifact build、release preparation、publicationのどこに原因があるかを切り分け、修正後に同じ検査を通し直します。

`failed`を`not_verified`やPASSへ読み替えません。

## 8. 自然な日本語レビュー

v0.2.0 Release Acceptance、Release Notes、Release Evidence、ISSUE-000059〜000063、actual tag ref、GitHub Release、Run `33574947445`、各release asset digestを照合しました。

候補の成立、actual releaseの成立、後続のE3b等のExecutable Evidence、Operational / Adoption Evidenceを分け、現在の状態をrelease入口から自然にたどれる構成へ整理しています。意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
