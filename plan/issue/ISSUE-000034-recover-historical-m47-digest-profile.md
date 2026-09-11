# ISSUE-000034: historical M47 digestのRepresentation Profileを回収・対応付けする

Status: **Resolved**  
Resolution: **Historical digest rule unrecoverable from currently retained direct evidence; keep affected bindings `not_verified`**  
Priority: **2**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0023**  
Updated: 2026-09-01

## Goal

historical M47のCognitive Method Definition / Realization / Applicationで使われた`content_digest`について、どのbytes、serialization、canonicalization、hash algorithmから生成されたかを推測せずに確認し、確認できる場合だけ適切なRepresentation Profileへ対応付ける。

このIssueはcurrent/future binding用のRepresentation Profile基線とは分離する。current JCS / raw-bytes ProfileはADR-0023、ISSUE-000038、ISSUE-000040により、Profile fixture、Verifier Registry、synthetic Payload Sourceまで限定Executable Evidenceが成立している。

```text
historical digest exists
  != historical Representation Profile is known

not_verified
  != failed
```

## Historical semantic boundary recovered

Library上の`COGNITIVE_METHOD_DEFINITION_REALIZATION_APPLICATION_v1.md`、`M47_IMPLEMENTATION_REPORT.md`、`M47_RELEASE_CLOSURE.md`から、少なくとも次の意味境界は回収できた。

```text
Method Definition
  ← exact-bound by Realization using ID / version / content digest

Method Application
  → exact-binds Definition and Realization
```

また、historical KJ Method Definition payloadも回収できた。

```text
schema = sei.cognitive-method-definition/v1
id = kj
version = 1
```

cultural-substrate-weavingのMethod Definition payloadもLibraryに残っている。

一方、これらの資料にはdigest生成時のcanonicalization、hash input bytes、serialization、hash algorithmを一意に特定できる記述がない。

## Recovery review — 2026-09-01

Resolution条件2を評価するため、単純なsemantic searchだけでなく、GitHub履歴、Actions、Libraryの個別ファイル、archive時系列まで探索範囲を広げた。

### 1. current GitHub reachable history

`hat47x/soza`について、`develop/v0.1.0`と`main`の到達可能履歴から次のpathを検索した。

```text
runtime/go/cognitivemethod/method.go
```

両方ともpath historyは空であり、現在到達可能なGit historyにはactual M47 `method.go`が残っていない。

現在列挙可能なbranchにもhistorical M47 branchは確認できなかった。

これはGit objectが世界のどこにも存在しないことの証明ではないが、**current GitHub repositoryから通常に回収可能なhistory / branchには存在しない**ことを確認した。

### 2. GitHub Actions history

M47が作業されていた時期に近い2026-08-30のGitHub Actions runを確認したが、current repositoryでは該当日のrunは0件だった。

したがって、Actions artifactやrun logを経由してM47 source / generated digest vectorを回収する経路も確認できなかった。

### 3. Library semantic / exact-name search

次を中心にLibrary全体を再探索した。

```text
package cognitivemethod
run_m47_cognitive_method_conformance.py
CURRENT_EVIDENCE_M47.yaml
human-procedure-ja.json
openai-skill-ja.json
cognitive-method-definition/v1
content_digest
sha256:
```

回収できたのは主に次だった。

- M47 semantic Contract
- M47 Implementation Report
- M47 Release Closure
- historical KJ `method.json`
- historical cultural-substrate-weaving `method.json`
- M47/M48 compatibility資料
- Phase 1 synthetic M47 fixture / manifest

actual M47 Go source、actual M47 conformance tool、actual `CURRENT_EVIDENCE_M47.yaml`、actual historical binding digest値は回収できなかった。

### 4. Library file-type inventory

semantic retrievalの取りこぼしを避けるため、Libraryに個別保存されたGo / Pythonファイルも拡張子単位で列挙した。

Goファイルとして確認できたのはPhase 1以降の`binding.go`であり、actual M47 `method.go` / `method_test.go`はなかった。

Pythonファイル一覧にも`run_m47_cognitive_method_conformance.py`はなかった。

### 5. archive timeline

2026-08-28〜2026-08-30のZIP archiveを時系列で確認した。

SOZA / Semantic Platform系では次が連続して残っている。

```text
semantic_platform_starter_m44_v1.zip
semantic_platform_starter_m45_v1.zip
semantic_platform_starter_m46_v1.zip
```

その後は、

```text
soza_architecture_transition_v1.zip
soza_architecture_delegation_2026-08-30.zip
soza_rebaseline_phase0_2026-08-30.zip
soza_rebaseline_phase0_final_2026-08-30.zip
soza_phase1_m48_integration_candidate_*.zip
```

へ移っている。

同じLibrary archive inventoryには、M47そのものを保持した`semantic_platform_starter_m47_*`または同等のM47 release/source archiveは確認できなかった。

### 6. Phase 1 synthetic M47 sourceはactual sourceではない

Phase 1 `BUNDLE_MANIFEST.json`には次が存在する。

```text
fixtures/integration/synthetic-m47-repo/runtime/go/cognitivemethod/method.go
```

manifest記録:

- size: `215 bytes`
- SHA-256: `aaca87204671c8f2299d13b9a6f964a0969b39d44bae0027f8305c47e333f056`

同bundleにはsynthetic Contract、synthetic `CURRENT_EVIDENCE_M47.yaml`、synthetic `go.mod`があり、`PHASE1_CANDIDATE_CLOSURE_REPORT.md`も`PASS: synthetic M47 repository`と明記している。

したがって、これをactual historical implementationへ昇格させない。

```text
synthetic compatibility fixture
  != actual historical M47 source
```

### 7. M48 placeholder digestはactual binding anchorではない

M48 candidate fixtureに残る、

```text
sha256:kj-app-001-v1
sha256:kj-v1
```

等はsemantic boundary用のplaceholderであり、actual SHA-256出力ではない。

historical Profile識別には利用しない。

## Recovery matrix

| Recovery target | Result | Closure interpretation |
|---|---|---|
| M47 semantic Contract | Recovered | exact-binding意味は確認可能 |
| M47 Implementation Report | Recovered | historical file setは確認可能 |
| M47 Release Closure | Recovered | M47 executable closureの存在は確認可能 |
| KJ Method Definition payload | Recovered | 将来digest anchorが出た場合の比較payloadとして利用可能 |
| cultural-substrate-weaving Method Definition payload | Recovered | 同上 |
| actual `runtime/go/cognitivemethod/method.go` | Not recovered | digest-producing codeを確認不能 |
| actual `method_test.go` | Not recovered | digest test vectorを確認不能 |
| actual M47 conformance tool | Not recovered | digest生成・比較手順を確認不能 |
| actual `CURRENT_EVIDENCE_M47.yaml` | Not recovered | actual binding anchorを確認不能 |
| actual Definition / Realization / Application digest | Not recovered | recovered payloadとの再現比較不能 |
| current Git reachable history | Checked; no M47 source path | 通常のGit history recovery routeなし |
| GitHub Actions around M47 transition | Checked; no 2026-08-30 run | Actions artifact recovery routeなし |
| Library individual Go/Python inventory | Checked; no M47 source/tool | semantic search取りこぼしの可能性を縮小 |
| Library archive timeline | Checked; M44/M45/M46あり、M47 archiveなし | retained archiveからの直接回収不能 |
| Phase 1 synthetic M47 repo | Recovered, explicitly synthetic | actual algorithm inferenceから除外 |

## Resolution decision

このIssueのResolution条件2を採用する。

```text
十分な回収作業を行っても
historical digest ruleを一意に特定できない
        ↓
Profileを推測で割り当てない
        ↓
historical bindingは not_verified のまま保持
```

current JCS Profile、raw-bytes Profile、Phase 1 custom canonical JSONのいずれにもM47 digestを遡及対応付けしない。

`sha256:`というprefixだけから、raw SHA-256、JCS + SHA-256、独自canonical JSON + SHA-256のどれかを推定しない。

historical verificationの回収不能性は、binding内容が誤っていることを意味しない。

```text
unrecoverable historical verification
  != failed binding
```

## Evidence state at closure

- current/future Representation Profile baseline: **Satisfied**
- current Verifier Registry: **Fixture-scoped Executable Evidence — Satisfied**
- current Payload Source boundary: **Synthetic-source Executable Evidence — Satisfied**
- historical M47 semantic boundary: **Recovered**
- historical M47 digest algorithm / Representation Profile: **Not Verified / currently unrecoverable**
- historical representative digest reproduction: **Not Verified / currently unrecoverable**
- Release / Operational / Adoption・Outcomeへの追加主張: **None**

## Reopen conditions

Resolved後も、次のいずれかが新たに発見された場合はこのIssueを再開してよい。

- historical SOZA M47 repository snapshot / archive
- actual `runtime/go/cognitivemethod/` source
- actual `tools/run_m47_cognitive_method_conformance.py`
- actual `CURRENT_EVIDENCE_M47.yaml`
- Method Definition / Realization / Applicationのpayload + actual digest pair
- historical release artifactから抽出した同等の一次資料

再開時も、保存済みactual digestとの再現比較なしにhistorical Profileを`verified`へ昇格させない。

## Explicit non-goals retained

- historical M47 digestをJCSへ遡及変換すること。
- historical payloadをcurrent Profileで再hashして古いbindingを置換すること。
- synthetic M47 fixtureからactual algorithmを推定すること。
- M48 placeholder digestからactual M47 hash formatを推定すること。
- M47のsemantic boundaryをcurrent implementation都合で変更すること。
- historical M47 local PASSをcurrent Executable Evidenceへ自動継承すること。

## Natural Japanese review

2026-09-01にcurrent ADR-0008 / 0009 / 0023、ISSUE-000038 / 000040、current GitHub reachable history、GitHub Actions、Library上のM47 Contract / Implementation Report / Release Closure、historical KJ / cultural-substrate-weaving Method Definition、個別Go / Pythonファイル、2026-08-28〜30のarchive時系列、Phase 1 synthetic M47 fixtureを照合した。actual sourceが見つからないという一つの検索結果だけではなく、複数の独立した回収経路を確認したうえで、historical digest ruleを現在保持されたEvidenceからは一意に回収できないと結論づけた。その後、推測Profileを付与せず`not_verified`を維持する意味、Evidence強度、再開条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
