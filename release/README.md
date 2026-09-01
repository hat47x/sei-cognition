# SOZA release管理

更新日: 2026-09-01  
状態: **Release Candidate Evidence available — Release Evidence not yet claimed**

## 1. このディレクトリの役割

`release/`は、SOZAのrelease scope、release candidateの受入れ条件、actual release後のEvidenceを管理します。

ここに文書やcandidate設定が存在するだけではRelease Evidenceになりません。

```text
release planning
  != release candidate gate PASS
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

v0.1.0では次を管理します。

- `RELEASE_ACCEPTANCE.md` — release scopeとcandidate / actual releaseの受入れ条件
- `release-candidate.json` — machine-readableなcandidate policy

actual release後にEvidenceを記録する場合は、candidate設定を上書きせず、`RELEASE_EVIDENCE.md`等の別文書へactual tag / commit / artifact / gate resultを記録します。

## 3. candidate report

Release Candidate Gateはsource treeへ固定値のcommit SHAを書き込まず、実行時のGit commit / tree SHAをmachine-readable reportへ記録します。

CIが生成するreportはderived evidenceです。source-of-truthのProduct ValueやSemantic Contractではありません。

初回のactual Release Candidate Evidenceとして、commit `4ee3f75753972e56fff8ab9f88b977cfe3d7b67b`についてRun `33462821768`がsuccessしました。candidate report artifactはID `9783773779`、artifact digestは`sha256:3efef517ffdcc1c5588f9ab5893059ae1c4239354e58c79036b0e4c244697113`です。

この記録は当該commitに対するcandidate Evidenceであり、以後source treeが変われば新しいcommitでgateを再実行します。

## 4. releaseの意味

v0.1.0では、source releaseとして配布するsemantic development baselineを対象とします。

これはproduction operational productの完成を意味しません。

production Provider、production Storage、live authorization、Operational Evidence、Adoption / Outcome Evidenceは、別のEvidence高さとして後続で扱います。

また、Release Candidate Gateがsuccessしてもactual tag / releaseが存在しない限り、Release Evidenceへは昇格しません。

## 5. 自然な日本語レビュー

SOZA_VALUE_ACCEPTANCE、ADR-0018、DEVELOPMENT_WORKFLOW、v0.1.0 release acceptance、actual Release Candidate Gate Runへ戻り、release planning、candidate、actual release、Operational / Outcomeの境界を整理しました。その後、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
