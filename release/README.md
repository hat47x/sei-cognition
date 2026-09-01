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

## 3. candidate report

Release Candidate Gateはsource treeへ固定値のcommit SHAを書き込まず、実行時のGit commit / tree SHAをmachine-readable reportへ記録します。

CIが生成するreportはderived Evidenceです。Product ValueやSemantic Contractのsource-of-truthではありません。

### v0.1.0

初回のactual Release Candidate Evidenceとして、commit `4ee3f75753972e56fff8ab9f88b977cfe3d7b67b`についてRun `33462821768`がsuccessしました。

- candidate report artifact ID: `9783773779`
- artifact digest: `sha256:3efef517ffdcc1c5588f9ab5893059ae1c4239354e58c79036b0e4c244697113`

### v0.2.0

PR #34のclosure head `ffa3824908d2fa50c8363ffc68611b5b25d56344`に対するRelease Candidate Gate Run `33568653099`で、v0.2.0の9 gateがすべてsuccessしました。PR検査ではGitHubが生成したtest merge commit `cb88cc49d5d38293231b63db9d93e8e5804acd7b`をcheckoutしているため、candidate reportとLocal Reference Packageはそのtest merge commitへ結び付いています。

- candidate report artifact ID: `9824110337`
- candidate report artifact digest: `sha256:2d71979ec4f466bd679178bae88b2ba32584ec121d8618217b9b70d2c79a216a`
- Local Reference Package artifact ID: `9824109925`
- Local Reference Package artifact digest: `sha256:6b319c6ac2cd0aeb98a13d6234e6c1d9c06ae09a10927a3b54fa48878fc46fa6`
- External Integration E3a Run `33568653077`: **success**
- Plan integrity Run `33568653098`: **success**

この結果は、PR #34のtest merge状態に対するRelease Candidate Evidenceです。actual `develop/v0.2.0`へ統合したcommitが同一であるとは仮定しません。merge後は、actual branch headについてRelease Candidate Gateを改めて確認します。

```text
PR test merge PASS
  != actual branch head tested
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

PR #34のclosure検証では、一度Plan Registryの既存`ISSUE-000013`ファイル名を誤って転記し、Run `33568527280`のGate 1がfailureしました。原因はrelease設計ではなくRegistryの転記ミスであり、実ファイル名へ戻した後、Plan integrity Run `33568653098`とRelease Candidate Gate Run `33568653099`がsuccessしています。

この履歴は、`failed`を`not_verified`やPASSとして扱わず、原因を修正してから同じ検査を通し直す運用例として残します。

## 6. 自然な日本語レビュー

SOZA_VALUE_ACCEPTANCE、ADR-0018、v0.1.0 / v0.2.0 Release Acceptance、PMS-04〜07、Local Reference Package、E3a external artifact integration、actual GitHub Actions Evidenceへ戻り、release planning、candidate、actual release、Operational / Adoption Outcomeの境界を整理しました。

v0.2.0については、PR上のtest merge commitで得たcandidate Evidenceと、actual branch headのEvidenceを同一視しないことも明示しています。そのうえで、意味やEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
