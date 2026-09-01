# ISSUE-000034: historical M47 digestのRepresentation Profileを回収・対応付けする

Status: **Blocked**  
Recovery state: **semantic primary assets recovered; digest-producing source / binding anchor still unavailable**  
Priority: **2**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0023**  
Updated: 2026-09-01

## Goal

historical M47のCognitive Method Definition / Realization / Applicationで使われた`content_digest`について、**どのbytes、serialization、canonicalization、hash algorithmから生成されたかを推測せずに確認し**、適切なRepresentation Profileへ対応付ける。

このIssueはcurrent/future binding用のRepresentation Profile基線とは分離する。current JCS / raw-bytes ProfileはADR-0023、ISSUE-000038、ISSUE-000040により、Profile fixture、Verifier Registry、synthetic Payload Sourceまで限定Executable Evidenceが成立している。

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

## Evidence recovered before this review

Libraryから次を確認済みだった。

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

## Recovery update — 2026-09-01

LibraryをM47固有のファイル名、package名、digest語彙、Phase 1 bundle manifestから再探索した。

### 1. historical KJ Method Definition payloadを回収した

Libraryに`method.json`が残っており、少なくとも次を確認できる。

```text
schema = soza.cognitive-method-definition/v1
id = kj
version = 1
```

内容はM47 Implementation Reportに列挙された`methods/kj/method.json`と意味上整合する。

このpayloadは、将来actual historical binding digestを回収できた場合に、raw bytes / JSON serialization / canonicalization等の候補を再現するanchorとして使える。

ただし、**比較対象となるactual M47 digest値が現時点で回収できていないため、このpayloadを任意方式でhashしてhistorical Profileを推定しない。**

### 2. Phase 1の`method.go`はactual M47 sourceではないことを確認した

`BUNDLE_MANIFEST.json`には次が存在する。

```text
fixtures/integration/synthetic-m47-repo/runtime/go/cognitivemethod/method.go
```

manifest記録:

- size: `215 bytes`
- SHA-256: `aaca87204671c8f2299d13b9a6f964a0969b39d44bae0027f8305c47e333f056`

同bundleにはsynthetic `CURRENT_EVIDENCE_M47.yaml`、synthetic Contract、synthetic `go.mod`が置かれている。さらに`PHASE1_CANDIDATE_CLOSURE_REPORT.md`自身がpreflight結果を`PASS: synthetic M47 repository`と記録している。

したがって、この`method.go`をactual historical M47 implementationへ昇格させない。

```text
synthetic compatibility fixture
  != actual historical M47 source
```

### 3. M48側のdigest表記はactual binding anchorではない

M48 candidate fixtureには次のような値が残る。

```text
sha256:kj-app-001-v1
sha256:kj-v1
```

これらはcompatibility / semantic boundaryを検査するplaceholderであり、64桁hexのactual SHA-256出力ではない。

historical M47 digest Profileの識別anchorには使わない。

### 4. M47の実装ファイル一覧は再確認できた

`M47_IMPLEMENTATION_REPORT.md`から、historical M47に実在したと記録される主なsourceを再確認した。

```text
runtime/go/cognitivemethod/method.go
runtime/go/cognitivemethod/method_test.go
runtime/go/cmd/cognitivemethod/main.go
methods/kj/method.json
methods/kj/realizations/human-procedure-ja.json
methods/cultural-substrate-weaving/method.json
methods/cultural-substrate-weaving/realizations/openai-skill-ja.json
tools/run_m47_cognitive_method_conformance.py
CURRENT_EVIDENCE_M47.yaml
```

今回回収できたのはsemantic Contract、Implementation / Release資料、KJ Method Definition payloadまでであり、digest生成規則を直接示すactual Go source / conformance tool / binding値はまだない。

## Blocked reason — narrowed

2026-09-01の再探索後、未回収Evidenceは次へ絞られた。

### A. actual digest-producing implementation

最優先:

```text
runtime/go/cognitivemethod/method.go
runtime/go/cognitivemethod/method_test.go
runtime/go/cmd/cognitivemethod/main.go
```

とくにdigestを計算・比較・bindingへ格納する関数やhelperが必要である。

### B. actual stored binding anchor

少なくとも一つ、可能なら複数の次の組が必要である。

```text
historical payload bytes
+
historical content_digest
```

候補:

- `methods/kj/method.json` + KJ Definition binding digest
- `methods/kj/realizations/human-procedure-ja.json` + Realization binding digest
- cultural-substrate-weaving Method / Realization + binding digest
- Method Application fixture / record + its binding digest

### C. actual M47 conformance tool / Evidence manifest

```text
tools/run_m47_cognitive_method_conformance.py
CURRENT_EVIDENCE_M47.yaml
```

これらにdigest test vector、command invocation、生成手順が残っていれば、実装sourceが一部欠落していてもProfileを直接回収できる可能性がある。

## Recovery targets

優先順位を次へ更新する。

1. historical M47 working tree / release archive
2. actual `runtime/go/cognitivemethod/method.go`
3. actual `runtime/go/cognitivemethod/method_test.go`
4. `tools/run_m47_cognitive_method_conformance.py`
5. actual Definition / Realization / Applicationのpayload + digest pair
6. `methods/kj/realizations/human-procedure-ja.json`
7. `methods/cultural-substrate-weaving/method.json`
8. `methods/cultural-substrate-weaving/realizations/openai-skill-ja.json`
9. actual `CURRENT_EVIDENCE_M47.yaml`
10. generated M47 fixture / digest output

`methods/kj/method.json`自体は回収済みのため、単独回収対象から「binding digestとのpair回収」へ位置づけを変更する。

## Required analysis after recovery

一次資料または同等の直接Evidenceを回収できた場合、次を確認する。

1. digest対象がraw file bytesか、JSON serializationか、semantic projectionか。
2. JSONの場合、key order / whitespace / number / Unicodeをどう扱っていたか。
3. hash algorithmとdigest text形式。
4. Definition / Realization / Applicationで同一規則か、別規則か。
5. digest対象へID / version metadataを含むか。
6. historical payloadからdigestを再現できるか。
7. 可能なら複数Artifact種で同じ規則が成立するか。
8. current Representation Profileとして再利用すべきか、historical-only Profileとして固定すべきか。

コードだけが見つかっても、historical bindingとの再現を行わずに`verified`とはしない。

## Allowed outcomes

### A. current JCS Profileと一意に一致する

actual historical ruleがRFC 8785 JCS + SHA-256と同一で、保存済みdigestを代表bindingで再現できた場合だけcurrent JCS Profileへ対応付ける。

### B. current raw-bytes Profileと一意に一致する

actual historical ruleが対象bytesへの直接SHA-256で、保存済みdigestを再現できた場合だけraw-bytes Profileへ対応付ける。

### C. historical独自Profileとして再現できる

独自serialization / canonicalizationで再現できる場合、必要ならhistorical-only Representation Profileとして記録する。

current Coreの既定Profileにはしない。

### D. 規則を確認できない

推測でJCSやraw-bytes Profileへ割り当てない。

historical bindingは「digest値は保存されているがRepresentation Profile不明」として扱い、`not_verified`を維持する。

```text
unrecoverable historical verification
  != failed binding
```

## Explicit non-goals

- historical M47 digestをJCSへ遡及変換すること。
- historical payloadをcurrent Profileで再hashして古いbindingを置換すること。
- synthetic M47 fixtureからactual algorithmを推定すること。
- M48 placeholder digestからactual M47 hash formatを推定すること。
- `sha256:` prefixの存在だけからraw SHA-256 / JCS / custom canonical JSONを決めること。
- M47のsemantic boundaryをcurrent implementation都合で変更すること。
- private chain-of-thoughtの回収。
- historical M47 local PASSをcurrent Executable Evidenceへ自動継承すること。

## Resolution condition

次のどちらかを満たしたときResolvedにできる。

1. 一次資料または同等の直接Evidenceからhistorical digest規則を特定し、Representation Profileへ対応付け、少なくとも1件のactual historical bindingで再現できた。
2. 十分な回収作業を行っても規則を特定できないことを明示Evidenceとともに確定し、`not_verified`として扱うcurrent方針をclosureした。

「規則を確認できないので永遠にBlocked」の状態を目的にはしない。回収不能性そのものも、十分に確認できれば最終的なEvidenceになり得る。

## Dependencies

- ADR-0008 — Exact Binding verification boundary
- ADR-0009 — verification outcome separation
- ADR-0017 — Cognitive Method boundary
- ADR-0023 — current Representation Profile baseline
- ISSUE-000009 — current/future Representation Profile stabilization（Resolved）
- ISSUE-000038 — current Runtime Verifier Registry（Resolved）
- ISSUE-000040 — current Payload Source boundary（Resolved）

## Evidence state

### Recovered

- M47 semantic Contract: **Recovered**
- M47 Implementation Report: **Recovered**
- M47 Release Closure: **Recovered**
- historical KJ Method Definition payload: **Recovered**
- Phase 1 synthetic M47 repository: **Identified as synthetic; excluded from actual-source inference**

### Not Yet Verified

- actual M47 digest-producing Go source
- actual historical Definition / Realization / Application binding digest value
- actual M47 conformance digest vectors
- mapping to JCS / raw-bytes / another historical Profile
- historical representative digest reproduction

### Current/future work remains independent

current JCS / raw-bytes Profile、Verifier Registry、synthetic Payload SourceのExecutable Evidenceをhistorical M47へ逆流させない。

## Revisit / unblock triggers

次のいずれかが得られた時点で再開する。

- historical SOZA repository snapshot / archive
- actual `runtime/go/cognitivemethod/` source
- actual M47 conformance tool
- actual `CURRENT_EVIDENCE_M47.yaml`
- Method Definition / Realization / Applicationのpayload + actual digest pair
- historical release artifactから抽出した上記source

## Natural Japanese review

2026-09-01にcurrent ADR-0008 / 0009 / 0023、ISSUE-000038 / 000040、Library上のM47 Contract、Implementation Report、Release Closure、KJ `method.json`、Phase 1 candidate manifest / closure reportを照合し直した。synthetic M47 fixtureやM48 placeholder digestをactual historical Evidenceへ混同しないよう回収済み情報とblockerを分離し、Resolution条件を「actual digest-producing sourceまたは同等の直接Evidence + historical binding再現」へ絞った。その後、意味、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
