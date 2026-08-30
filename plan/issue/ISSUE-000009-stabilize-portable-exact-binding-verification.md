# ISSUE-000009: Portable Exact Bindingの検証を安定化する

Status: **Blocked**  
Priority: **1**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009**  
Updated: 2026-08-31

## Goal

Portable Exact Bindingを、Go固有の実装やSOZA独自canonicalizationだけに依存せず、複数言語・複数representationで検証可能な仕組みへ安定化する。

## Current state

historical / local candidate上の安定化作業は進んでいるが、actual GitHub repositoryには検証実装・fixture・test toolの基線がまだ実体化していない。

したがって、このIssueは「local stabilizationが済んだ」という過去Evidenceと、「actual repositoryで再現可能なverificationがまだない」という現在状態を分けて扱う。

## Completed in historical / local candidate work

- Go / Pythonの独立実装でcross-language digest一致を確認した。
- key order、whitespace、等価number表現等のadversarial fixtureを試した。
- semantic value差、duplicate key、payload tamperingを検出した。
- unknown Representation Contractを`verified`扱いしないことを確認した。
- representation-only changeをSemantic Lineageへ自動変換しないことを確認した。
- stable JSON ProfileはRFC 8785 JCSを第一候補とした。
- custom canonical JSON v1alpha1は実験Evidenceへ位置付け直した。
- non-JSON / large binary向けraw-bytes profile候補を整理した。
- Verification Outcomeを`verified / failed / not_verified`へ分離した。

これらはhistorical / local candidate Evidenceであり、actual repository PASSへ自動継承しない。

## Blocked by

### ISSUE-000022 — actual repository baseline materialization

Representation Contract、fixture、verifier adapter、test toolをactual repositoryへ配置し、再実行可能な入口を作る必要がある。

この基線がない状態で、READMEやhistorical candidateの記録だけを根拠にactual PASSを主張しない。

## Remaining work after unblock

1. historical M47で用いられたdigest計算規則を、推測ではなく確認したうえでRepresentation Contractへmapする。
2. stable JCS Go verifier dependencyをlicense、maintenance、RFC test vector適合まで含めて選定・実証する。
3. historical bindingでpayloadやverifierが失われた場合の表示・Assurance運用をactual implementationで確認する。
4. high-precision semantic valueをJCS binary64へ暗黙丸めしないProfile境界を実装で検証する。
5. historical / local candidate fixtureをactual repositoryへ持ち込む場合、最新ADRとProduct Valueへ戻して再監査する。
6. actual repository上で得たPASSを、historical / local candidate Evidenceと別に記録する。

M47 historical digestをJCSへ遡及変換しない。判定不能なbindingを推測で再hashしない。

## Completion criteria

- actual repository上にRepresentation Contractと再実行可能なverifier入口が存在する。
- stable JCS verifier adapterがactual repositoryで検証されている。
- historical M47 digestを、確認できた範囲で正しいRepresentation Contractへ対応付けられる。
- `verified / failed / not_verified`がactual fixtureで区別できる。
- historical / local candidate PASSとactual repository PASSを別Evidenceとして報告できる。
- 未確認のhistorical bindingを検証済みとして表示しない。

## Reopen conditions

Resolved後も、複数representationでportable verificationが成立しない、選定したRepresentation Contractが意味再構成を妨げる、またはactual interoperabilityで重大な差異が出た場合は再開する。

## Natural Japanese review

ADR-0007〜0009、ISSUE-000022、actual repositoryの現在地へ戻して状態とEvidence強度を整理した後、意味、強度、Blocked条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
