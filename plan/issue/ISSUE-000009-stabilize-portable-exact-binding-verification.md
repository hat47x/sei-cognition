# ISSUE-000009: Portable Exact Bindingの検証を安定化する

Status: **Blocked — local stabilization complete; historical M47 mapping / stable verifier integration pending**  
Priority: **1**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009**  
Updated: 2026-08-31

## Goal

Portable Exact Bindingを、Go固有の実装やSOZA独自canonicalizationだけに依存せず、複数言語・複数representationで検証可能な仕組みへ安定化する。

## Completed locally

- Go / Pythonの独立実装でcross-language digest一致を確認した。
- key order、whitespace、等価number表現等のadversarial fixtureを試した。
- semantic value差、duplicate key、payload tamperingを検出した。
- unknown Representation Contractを`verified`扱いしないことを確認した。
- representation-only changeをSemantic Lineageへ自動変換しないことを確認した。
- stable JSON ProfileはRFC 8785 JCSを第一候補とした。
- custom canonical JSON v1alpha1は実験Evidenceへ位置付け直した。
- non-JSON / large binary向けraw-bytes profile候補を整理した。
- Verification Outcomeを`verified / failed / not_verified`へ分離した。

## Remaining blockers

1. historical M47で用いられたdigest計算規則を、推測ではなく確認したうえでRepresentation Contractへmapする。
2. stable JCS Go verifier dependencyをlicense、maintenance、RFC test vector適合まで含めて選定・実証する。
3. historical bindingでpayloadやverifierが失われた場合の表示・Assurance運用をactual implementationで確認する。
4. high-precision semantic valueをJCS binary64へ暗黙丸めしないProfile境界を実装で検証する。

M47 historical digestをJCSへ遡及変換しない。判定不能なbindingを推測で再hashしない。

## Resolution condition

actual repository上でstable verifier adapterが成立し、historical M47 digestを正しいRepresentation Contractへ対応付けられること。

## Natural Japanese review

local hardening、ADR-0008/0009、現在のrepo状態を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
