# ISSUE-000034: historical M47 digestのRepresentation Profileを回収・対応付けする

Status: **Blocked**  
Priority: **2**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0023**  
Updated: 2026-08-31

## Goal

historical M47のCognitive Method Definition / Realization / Applicationで使われた`content digest`について、**どのbytes、serialization、canonicalization、hash algorithmから生成されたかを推測せずに確認し**、適切なRepresentation Profileへ対応付ける。

このIssueは、current/future binding用のRepresentation Profile基線とは分離する。current JCS / raw-bytes ProfileはADR-0023とISSUE-000009でfixture-scoped Executable Evidenceまで成立している。

historical Profileが不明でも、ADR-0009に従い`not_verified`として保持できるため、current Profileの利用を停止しない。

## Why this is separate

M47の公開意味契約からは、次までは確認できる。

```text
Method Definition
  ← exact-bound by Realization using ID / version / content digest

Method Application
  → exact-binds Definition and Realization
```

一方、現在回収できているM47 Contract、Implementation Report、Release Closureには、digest生成時のcanonicalization / hash input bytesを特定できる記述がない。

したがって、historical digestを現在のJCS Profileへ遡及的に割り当てることはできない。

```text
historical digest exists
  != historical Representation Profile is known
```

ADR-0009により、Profileやverifierを特定できないbindingは`failed`ではなく`not_verified`として保持できる。ADR-0023では、このhistorical mapping未完了をcurrent/future ProfileのAcceptance条件から分離した。

## Evidence already recovered

Libraryから次を確認済み。

- `COGNITIVE_METHOD_DEFINITION_REALIZATION_APPLICATION_v1.md`
  - RealizationはMethod DefinitionをID / version / content digestでexact-bindする。
  - Method ApplicationはDefinitionとRealizationをexact-bindする。
- `M47_IMPLEMENTATION_REPORT.md`
  - historical sourceとして`runtime/go/cognitivemethod/method.go`等が存在したことは確認できる。
  - digest生成規則そのものは記録されていない。
- `M47_RELEASE_CLOSURE.md`
  - M47 boundary / regression evidenceは確認できる。
  - digest canonicalization規則は記録されていない。
- Phase 1 hardening資料
  - historical M47を壊さないため、Representation ContractをUniversal必須へしなかった。
  - unknown historical Profileを推測して再hashしない方針が明示されている。
- current ADR-0023 / Representation Profile conformance
  - current/future JSON bindingはRFC 8785 JCS + SHA-256、raw contentはraw bytes + SHA-256へ分離した。
  - unknown Profileは`not_verified`として扱えることをactual fixtureで確認した。
  - historical M47 digestをcurrent JCSへ遡及変換しないことをAcceptedした。

## Blocked reason

現在のactual `hat47x/soza` repositoryにはhistorical M47 Go source / method assetsが存在しない。

Library検索でも、次の**実ファイル本文**は回収できていない。

- historical `runtime/go/cognitivemethod/method.go`
- historical digest生成helper
- historical `methods/*/method.json`とdigest生成時の入力規則
- M47 conformance tool内のdigest計算コード

これらのいずれか、または同等の一次資料が必要である。

## Recovery targets

優先順位:

1. historical M47 working tree / archive
2. `runtime/go/cognitivemethod/method.go`
3. `tools/run_m47_cognitive_method_conformance.py`
4. `methods/kj/method.json`
5. `methods/kj/realizations/human-procedure-ja.json`
6. `methods/cultural-substrate-weaving/method.json`
7. `methods/cultural-substrate-weaving/realizations/openai-skill-ja.json`
8. `CURRENT_EVIDENCE_M47.yaml`
9. generated M47 fixture / digest output

## Required analysis after recovery

一次資料を回収できた場合、次を確認する。

1. digest対象がraw file bytesか、JSON serializationか、semantic projectionか。
2. JSONの場合、key order / whitespace / number / Unicodeをどう扱っていたか。
3. hash algorithmとdigest text形式。
4. Definition / Realization / Applicationで同一規則か、別規則か。
5. digest対象へID / version metadataを含むか。
6. historical payloadからdigestを再現できるか。
7. current Representation Profileとして再利用すべきか、historical-only Profileとして固定すべきか。

## Allowed outcomes

### A. 規則を一意に確認できる

historical-onlyまたは再利用可能なRepresentation Profile Definitionを作成し、Profile ID / versionを固定する。

既存bindingをそのProfileへ対応付ける。

### B. 一部だけ確認できる

確認できた範囲だけ記録し、再検証不能なbindingは`not_verified`のまま保持する。

### C. 規則を確認できない

推測でJCSやraw-bytes Profileへ割り当てない。

historical bindingは「digest値は保存されているがRepresentation Profile不明」として扱い、current/future bindingとは分離する。

## Explicit non-goals

- historical M47 digestをJCSへ遡及変換すること
- digest値が似ていることからalgorithmを推定すること
- M47のsemantic boundaryをcurrent implementation都合で変更すること
- private chain-of-thoughtの回収
- historical M47 local PASSをcurrent Executable Evidenceへ自動継承すること

## Resolution condition

次のどちらかを満たしたときResolvedにできる。

1. 一次資料からhistorical digest規則を特定し、Representation Profileへ対応付け、代表bindingで再現できた。
2. 十分な回収作業を行っても規則を特定できないことを明示Evidenceとともに確定し、`not_verified`として扱うcurrent方針をclosureした。

「規則を確認できないので永遠にBlocked」の状態を目的にはしない。回収不能性そのものも、十分に確認できれば最終的なEvidenceになり得る。

## Dependencies

- ADR-0008 — Exact Binding verification boundary
- ADR-0009 — verification outcome separation
- ADR-0017 — Cognitive Method boundary
- ADR-0023 — current Representation Profile baseline
- ISSUE-000009 — current/future Representation Profile stabilization（Resolved）

## Evidence state

- current/future Profile baseline: **Satisfied — ADR-0023 / ISSUE-000009**
- historical M47 Profile identification: **Not Yet Verified**
- historical representative digest reproduction: **Not Yet Verified**
- Production Runtime integration: **Not Yet Verified**

## Natural Japanese review

current Profile安定化の完了、ADR-0023、Libraryで確認できた意味契約と確認できていない一次実装を整理した。その後、推測を避ける条件、回収対象、許容するclosure、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
