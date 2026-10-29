# SOZA release管理

更新日: 2026-09-03  
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
- `release-request.json` — actual publicationのversion固有requestとpublication lifecycle
- `RELEASE_NOTES.md` — actual GitHub Releaseへ掲示した説明
- `RELEASE_EVIDENCE.md` — actual tag / commit / artifact / gate resultを結び付けるEvidence record

共通checkerを利用しても、versionごとのsupported scopeまで共通化しません。

```text
shared checker
  != shared release scope
```

## 3. current Release Candidate検証

GitHub Actionsは当面完全に停止しています。current `develop/v0.2.0`にはGitHub Actions workflowを置かず、過去runの再実行やrunner監視も行いません。

Release Candidateの意味上の条件は維持し、必要な再検証はrepository同梱のchecker、test、probeをローカルで個別に実行します。

中心となるcandidate policy checkerは次です。

```bash
python3 tools/check_release_candidate.py \
  --config release/v0.2.0/release-candidate.json
```

`--config`は必須です。versionごとにpolicyが異なるため既定値は置かず、検査対象のversionを明示します。v0.1.0のhistorical検査は`--config release/v0.1.0/release-candidate.json`で実行します。

`release-candidate.json`の`required_gates`は検査責務を示します。GitHub Actionsのjob名やworkflowの存在を要求するものではありません。各gateに対応するローカル検査を実際に実行し、確認できた範囲だけをEvidenceとして扱います。

```text
required gate
  = required verification responsibility
  != GitHub Actions job required
```

実行できなかった検査をPASSへ読み替えません。必要な検査が未実行なら、そのcandidateについては`Not Yet Verified`として扱います。

## 4. historical Release Candidate / publication Evidence

v0.2.0のactual release時にはGitHub Actionsを利用していました。この履歴はcurrent実行方式が変わっても削除しません。

actual release source commit `c3640bdfcc43652b63a5b9941fd6b472312ec28f`について、Release Candidate Gate Run `33574947445`で9 gateすべてがsuccessしています。

そのRunでは、同じ`GITHUB_SHA`へ`v0.2.0` tagを作成し、GitHub Releaseを公開しました。`GITHUB_TOKEN`によるtag作成ではGitHub Actionsの再帰抑制が働き、通常のtag-push workflowは別Runとして起動していません。

当時のEvidence chainは次です。

```text
same source commit
  → candidate gate 9/9 PASS
  → release preparation PASS
  → tagを同じGITHUB_SHAへ作成
  → GitHub Release作成
```

これは**historical Release Evidence**です。現在も同じworkflowが存在する、または再実行すべきだという意味ではありません。

## 5. v0.2.0 actual Release Evidence

`v0.2.0`は、Local Reference Product Baselineとしてactual GitHub Releaseになっています。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- historical Release Candidate Gate: Run `33574947445` — success
- GitHub Release ID: `380902898`
- Release Evidence: `release/v0.2.0/RELEASE_EVIDENCE.md`

Local Reference Packageのprepared SHA-256とactual Release asset digestは、次の値で一致しています。

```text
37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17
```

candidate gateで検査・準備したpackage bytesと、actual Releaseで配布しているpackage bytesを同一digestで追跡できます。

## 6. v0.2.0のsupported scope

v0.2.0は、semantic baselineに加えて、Product Interaction、Local Single-Node Packaging、Product Access責務分離、Realization / Provider交換、E3a version-pinned external artifact integrationまでを、開発者・評価者向けのLocal Reference Product Baselineとして固定します。

release source commitにはE3b-P1 public live Provider integrationやTEI executable injection boundaryのScoped Executable Evidenceも存在します。しかし、repositoryに後続Evidenceが存在することと、v0.2.0でsupportを主張することは分けます。

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

## 7. publication lifecycleの完了

actual `v0.2.0` release成立後は、後続の`develop/v0.2.0` commitを同じtagへ再publicationしません。

`release-request.json`では現在、次の状態を明示しています。

```text
publish = false
publication_state = completed
```

現在のローカル再検証は、既存`v0.2.0`を再publicationするためのものではありません。後続source treeについてrelease条件との整合を確認する場合も、既存tagを付け替えたり既存Releaseを再作成したりしません。

```text
future develop commit
  → local candidate revalidation when needed
  != v0.2.0 retag
  != v0.2.0 republish
```

historicalには、publication lifecycle導入後のRun `33585297218`で9 gateがsuccessし、release preparation / publicationが意図どおりskipされました。導入途中のcommit `f6477e3c89ec01a970c48cb6f3f55a0830744ff2`では旧release requestに`publication_state`がなくRun `33585287867`がfailureしましたが、requestを`completed`へ同期して同じ検査を通し直しています。

このfailure履歴も、条件を弱めず原因となったrelease stateを修正したEvidenceとして保持します。

## 8. Plan blockerのversion境界

Release Candidateを後続の`develop`で再検証するとき、現在存在するすべてのPlan Issueを過去versionのrelease blockerへしてはなりません。後から追加された実証課題がOpenであることと、既に成立したversionのcandidate条件は別だからです。

version固有の`release-candidate.json`に`plan_issue_scope_max`を持たせ、candidate policyが参照するPlan Issueの上限を固定します。

```text
v0.1.0 → ISSUE-000041 まで
v0.2.0 → ISSUE-000062 まで
```

v0.1.0の初回candidate commitにはISSUE-000041までが存在し、v0.2.0のactual release source commitにはISSUE-000062までが存在しました。これより後に追加されたIssueは、旧versionのcandidate blockerへ遡及させません。

一方、境界内のIssueが後から`Open`、`In Progress`、`Blocked`へ戻った場合は、現在のPlan registryとの不整合としてcandidate再検証をblockします。過去versionの条件を凍結することと、現在明示的に撤回された前提まで無視することは同じではありません。

```text
post-release Issue is Open
  != old release candidate blocked

in-scope historical Issue reopened
  → old candidate revalidation blocked
```

この境界はIssueを無理に`Resolved`へ変更して検査を通すための例外ではありません。各versionが実際にrelease判断へ含めたPlan snapshotを再現するためのpolicyです。

## 9. failureの扱い

ローカルchecker、test、probe、artifact build、release preparation等が失敗した場合は、条件を弱める理由にはしません。

failureが生じた場合は、Plan policy、checker、runtime、artifact build、release preparation、publication lifecycleのどこに原因があるかを切り分け、原因のある層を修正して同じ検査を再実行します。

`failed`を`not_verified`やPASSへ読み替えません。

GitHub Actions停止中は、Actions statusがないこと自体をfailureともPASSとも扱いません。

## 10. 自然な日本語レビュー

v0.1.0 / v0.2.0 Release Acceptance、各`release-candidate.json`、Release Notes、Release Evidence、release request、release preparation script、actual release sourceのPlan registry、historical tag / GitHub Release / Actions Runを照合しました。

過去のv0.2.0 publicationでGitHub Actionsを利用した事実はRelease Evidenceとして保持しつつ、現在の開発運用からは切り離しました。current candidate再検証はrepository-local checker、test、probeをローカルで個別に実行する方式とし、削除済みworkflowをrequired pathへ残さないよう整理しています。

候補の成立、actual releaseの成立、publication lifecycleの完了、後続のExecutable Evidence、Operational / Adoption Evidenceを分け、現在の運用とhistorical Evidenceを混同せず自然に読み通せることを最重要視して全文を再ドラフトしました。
