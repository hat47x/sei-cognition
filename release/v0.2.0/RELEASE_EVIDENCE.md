# SOZA v0.2.0 Release Evidence

更新日: 2026-09-02  
状態: **Release Evidence Satisfied for the Local Reference Product Baseline**

## 1. この文書の役割

この文書は、SOZA v0.2.0について、Release Acceptanceで定めた条件に対して**actual tag、GitHub Release、配布artifact、検査済みsource commitが実在し、相互に追跡できること**を記録します。

このEvidenceは、v0.2.0のsupported scopeであるLocal Reference Product Baselineに限ってRelease Evidenceを成立させるものです。

```text
Release Evidence Satisfied
  != production readiness
  != Operational Evidence
  != Adoption / Outcome Evidence
```

E3b全体、E4 Operational portability、production IAM / Storage / security等を、このreleaseによってSatisfiedへ上げません。

## 2. Release identity

actual releaseは次で特定します。

- Repository: `hat47x/soza`
- Version / tag: `v0.2.0`
- Release name: `SOZA v0.2.0 — Local Reference Product Baseline`
- Release ID: `380902898`
- Published at: `2026-09-02T00:21:59Z`
- Draft: `false`
- Prerelease: `false`
- Release URL: `https://github.com/hat47x/soza/releases/tag/v0.2.0`

`v0.2.0` tagは、次のsource commitを直接指しています。

```text
c3640bdfcc43652b63a5b9941fd6b472312ec28f
```

Git ref APIで、tag objectのSHAとsource commitが完全一致することを確認しました。

## 3. candidate gateとpublicationの結び付き

source commit `c3640bdfcc43652b63a5b9941fd6b472312ec28f`について、push-triggered Release Candidate Gate Run `33574947445`がsuccessしました。

同Runでは、次が順に成立しています。

1. Release Candidate Gateの9 gateすべてがsuccessした。
2. Local Reference Packageとcandidate reportが同じsource commitから生成された。
3. `prepare-v0-2-0-release`がcandidate report、package、checksum、Release Notes、release requestを照合した。
4. `publish-v0-2-0`が同じ`GITHUB_SHA`をsourceとして`v0.2.0` tagを作成した。
5. 同じprepared publication bundleからGitHub Releaseと4つのrelease assetを作成した。

publication jobのlogには、次が記録されています。

```text
created tag v0.2.0 -> c3640bdfcc43652b63a5b9941fd6b472312ec28f
```

したがって、release tagとcandidate gateを別々の曖昧な時点へ結び付けていません。

## 4. Local Reference Package byte identity

release preparationでは、Local Reference Packageについて次のSHA-256を実bytesから算出しました。

```text
37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17
```

GitHub Release上の`soza-local-reference-linux-amd64.tar.gz` assetが持つdigestも、同じ値です。

```text
prepared package SHA-256
  == release asset digest
```

これにより、candidate検査に用いたpackage bytesと、actual Releaseで配布しているpackage bytesを同一digestで追跡できます。

## 5. Release assets

GitHub Releaseには次の4 assetが存在します。

| Asset | Release asset ID | GitHub asset digest |
| --- | ---: | --- |
| `soza-local-reference-linux-amd64.tar.gz` | `540358086` | `sha256:37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17` |
| `soza-local-reference-linux-amd64.tar.gz.sha256` | `540358088` | `sha256:271a9eb445af6edb3913e04a9cbf4d2407f551db3533d42958cc3eb927093d38` |
| `v0.2.0-candidate-report.json` | `540358089` | `sha256:1362a70dae32f44b7c6d5972fa9272260fd816f451e5ddbc4b0f4e811147f15c` |
| `release-metadata.json` | `540358087` | `sha256:31e082e45100449e6c92bb9d0d797665007ce36577252787f3227f4f84149b59` |

ここでGitHub asset digestは各release assetそのもののdigestです。GitHub Actionsのartifact zip digestとは別物として扱います。

prepared publication bundle自体もGitHub Actions artifactとして残っています。

- Artifact ID: `9826285457`
- Artifact digest: `sha256:28555fd7f2664040363d65fa6350f599442077ef8e8fcb2c1d132e0611ab5162`

## 6. 同じsource commitの回帰Evidence

release source commit `c3640bdf...`では、Release Candidate Gateだけでなく次もsuccessしています。

- Plan integrity Run `33574947407`
- External Integration E3a Run `33574947323`
- External Integration E3b Run `33574947359`

E3b Runのsuccessは後続のScoped Executable Evidenceとして有用ですが、v0.2.0のsupported release scopeをE3bへ広げる根拠には使いません。

```text
E3b scoped Evidence on release commit
  != E3b included in v0.2.0 supported scope
```

## 7. tag作成とGitHub Actionsの再帰抑制

`v0.2.0` tagは、publication jobの`GITHUB_TOKEN`を用いて作成しました。GitHub Actionsでは、`GITHUB_TOKEN`によって生じた通常のpush eventは、workflowの再帰起動を抑制する扱いになります。そのため、この自動生成tagについてtag-push event由来の別Release Candidate Gate Runは発生していません。

これは「tag対象commitが未検査」という意味ではありません。今回のpublicationは次の順序で行っています。

```text
source commit c3640bdf...
  → Release Candidate Gate 9/9 PASS
  → release preparation PASS
  → tag v0.2.0 を同じGITHUB_SHAへ作成
  → GitHub Releaseを作成
```

Release Acceptanceが要求する「tag対象commitでRelease Candidate Gateがsuccessしている」という条件は、Run `33574947445`によって満たしています。

一方、手動または外部credentialでtagを作成した場合に備え、workflowのtag trigger自体は維持します。**自動publicationのpre-publication gate**と**外部から作られたtagに対するtag-triggered gate**は、別の検査経路として扱います。

## 8. Release Acceptanceとの照合

Release Acceptanceのactual Release Evidence条件を次のように評価します。

1. actual `v0.2.0` tag / release identity: **Satisfied**
2. tagとcandidate gate済みsource commitのExactな結び付き: **Satisfied**
3. 配布Artifactからtag / source commitへの追跡: **Satisfied**
4. Local Reference Package bytesのdigest識別: **Satisfied**
5. supported scopeと非主張範囲を明示するRelease Notes: **Satisfied**
6. tag対象commitのRelease Candidate Gate success: **Satisfied** — Run `33574947445`
7. tag / commit / artifact / gate resultを結び付けるrelease後Evidence record: **Satisfied by this document**

したがって、**v0.2.0 Local Reference Product BaselineのRelease EvidenceはSatisfied**と判断します。

## 9. このEvidenceから主張しないこと

このreleaseによって次を証明したことにはしません。

- production serviceとしての完成
- E3b live external integration全体の完了
- actual TEI CLI integrationの完了
- external Cognitive Methodのlive実行
- E4 Operational portability
- production Provider / Storage interoperability
- production identity / security
- formal platform support matrix
- production installer / signing
- Operational Evidence
- Adoption / Outcome Evidence

Releaseは「配布可能なsupported scopeをactual artifactとして固定できた」ことを示します。実運用で安全・安定・有用であることは、別のEvidenceを必要とします。

## 10. 自然な日本語レビュー

v0.2.0 Release Acceptance、Release Notes、ISSUE-000059〜000062、Release Candidate Gate Run `33574947445`、publication job log、actual tag ref、GitHub Releaseと各asset digestを照合しました。

そのうえで、candidateの成立、actual releaseの成立、E3b等の後続Executable Evidence、Operational / Adoption Evidenceを混同しないよう整理しました。とくに、`GITHUB_TOKEN`で作成したtagがtag-push workflowを再帰起動しない点について、未検証と誤読されないよう、pre-publication gateとtag SHAのExactな結び付きを明示しています。

意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文をドラフトし、最終意味監査を実施済みです。
