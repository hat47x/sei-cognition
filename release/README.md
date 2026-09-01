# SOZA release管理

更新日: 2026-09-02  
状態: **Release Candidate Evidence available — Release Evidence not yet claimed**

## 1. このディレクトリの役割

`release/`は、SOZAのrelease scope、Release Candidateの受入れ条件、actual release後のEvidenceを管理します。

ここに文書やcandidate設定が存在するだけではRelease Evidenceになりません。

```text
release planning
  != Release Candidate Gate PASS
  != actual release
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Product Value上のEvidence高さは`product/value/SOZA_VALUE_ACCEPTANCE.md`とADR-0018を正とします。

## 2. versionごとの配置

version固有のrelease資料は次へ置きます。

```text
release/vX.Y.Z/
```

現在、v0.1.0とv0.2.0で次を管理しています。

- `RELEASE_ACCEPTANCE.md` — そのversionのsupported scopeとcandidate / actual releaseの受入れ条件
- `release-candidate.json` — machine-readableなversion固有candidate policy

checkerやworkflowは共通化できますが、versionごとのrelease scopeまで共通化しません。

```text
shared checker
  != shared release scope
```

actual release後にEvidenceを記録する場合はcandidate設定を上書きせず、`RELEASE_EVIDENCE.md`等の別文書へactual tag / commit / artifact / gate resultを記録します。

## 3. candidate Evidence

Release Candidate Gateはsource treeへ固定値のcommit SHAを書き込まず、実行時のGit commit / tree SHAをmachine-readable reportへ記録します。

CIが生成するreportはderived Evidenceです。Product ValueやSemantic Contractのsource-of-truthではありません。

### v0.1.0

初回のactual Release Candidate Evidenceとして、commit `4ee3f75753972e56fff8ab9f88b977cfe3d7b67b`についてRun `33462821768`がsuccessしました。

- candidate report artifact ID: `9783773779`
- artifact digest: `sha256:3efef517ffdcc1c5588f9ab5893059ae1c4239354e58c79036b0e4c244697113`

### v0.2.0 — PR上の検査

PR #34では、closure後のtest mergeについてRelease Candidate Gateを複数回実行し、最終文書同期後のRun `33568925573`でも9 gateがすべてsuccessしました。これはmerge前にbaseとの組み合わせを検査したEvidenceです。

### v0.2.0 — actual `develop/v0.2.0` Evidence point

PR #34をmergeしたactual `develop/v0.2.0` commit `724cba2a744582252c6ccba8322fc34a55b76b1b`について、push-triggered Release Candidate Gate Run `33569004831`がsuccessしました。

同じcommitについて、次もsuccessしています。

- Plan integrity Run `33569004843`
- External Integration E3a Run `33569004842`

Release Candidate Gateでは9 gateに加え、Local Reference Packageとcandidate reportのartifact uploadも成功しました。

- candidate report artifact ID: `9824232506`
- candidate report artifact digest: `sha256:f6c9326e6af415654df80446893c5ba5c847fccd4e2d7192806b7056eb6c781d`
- Local Reference Package artifact ID: `9824232197`
- Local Reference Package artifact digest: `sha256:13bb5ed0ba8ab39e817a5dadc952e8bfb8934df9965474aa8435718136138ac7`

これを、v0.2.0における最初の**actual develop candidate Evidence point**として扱います。

この文書自身を更新するとbranch HEADは変わるため、「この文書に書かれているSHAが常に最新HEADでなければならない」とはしません。Evidenceは検査したcommitへ固定し、後続commitは後続CIで回帰を確認します。

```text
candidate Evidence point established
  != every later commit automatically verified
  != actual v0.2.0 release
```

## 4. v0.1.0とv0.2.0のrelease scope

v0.1.0は、semantic development baselineを再現可能なsource releaseとして固定するversionです。

v0.2.0は、そのsemantic baselineに加えて、Product Interaction、Local Single-Node Packaging、Product Access責務分離、Realization / Provider交換、E3a version-pinned external artifact integrationまでを、開発者・評価者向けの **Local Reference Product Baseline** として扱います。

どちらもproduction operational productの完成を意味しません。特にv0.2.0でも、次は別のEvidence高さとして後続で扱います。

- E3b live external process / service integration
- E4 Operational portability
- production Provider / Storage integration
- production identity / security
- formal platform support matrix
- Operational Evidence
- Adoption / Outcome Evidence

また、Release Candidate Gateがsuccessしてもactual tag / releaseが存在しない限り、Release Evidenceへは昇格しません。

## 5. Release Candidate failureの扱い

candidate gateのfailureは、release条件を弱める理由にはしません。

PR #34のclosure検証では、一度Plan Registryの既存`ISSUE-000013`ファイル名を誤って転記し、Run `33568527280`のGate 1がfailureしました。原因はrelease設計ではなくRegistryの転記ミスであり、実ファイル名へ戻した後、Plan integrityとRelease Candidate Gateを通し直してsuccessを確認しました。

この履歴は、`failed`を`not_verified`やPASSとして扱わず、原因を修正してから同じ検査を再実行する運用例として残します。

## 6. 自然な日本語レビュー

SOZA_VALUE_ACCEPTANCE、ADR-0018、v0.1.0 / v0.2.0 Release Acceptance、PMS-04〜07、Local Reference Package、E3a external artifact integration、PR #34、actual `develop/v0.2.0`のGitHub Actions Evidenceへ戻り、release planning、candidate、actual release、Operational / Adoption Outcomeの境界を整理しました。

とくに、PR上のtest merge、actual develop candidate Evidence point、後続の文書更新、actual tag / releaseを同一視しないよう整理しています。そのうえで、意味やEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
