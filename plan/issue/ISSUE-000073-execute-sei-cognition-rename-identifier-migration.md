# ISSUE-000073: SEI Cognitionへの改名とidentifier移行を実施する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0003, ADR-0021, ADR-0031**  
Updated: 2026-09-11

## Goal

ADR-0031で定めたclass別の規則に従って改名を実施し、完了時に次を判別可能な状態にします。

- current tree上のlive codeとlive文書に、Contract identity・repository path・環境変数・CLI flagとしての`sei`が残っていない。
- 記録済みEvidence（`evaluation/method-quality/historical/`、`runtime/evidence/`、`release/`、`contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md`）が、内容・digestともに改名前と一致する。
- 記録済みEvidenceを読むcheckerが、旧identity `sei.*`を受け付けたまま成功する。
- `sei.*/v1alpha1`をbasisとするv0.2.0時点のArtifactが、ADR-0031のmapping tableによって新identityへ解決できる。

「置換した」だけでは完了としません。上の4点が同時に成立して初めて完了です。

## Background

### 確認済みの事実

current tree上の実測値です。

```text
sei を含むfile                        428
sei. で始まるdistinct identifier      105
  うち portable Contract / Profile       7
  うち runtime verifier reference        2
  うち negative / boundary fixture       3
  うち 内部record schema (/v1)          80
      live codeからも参照               58
      記録済みEvidence内のみ            22
環境変数・CLI flag                    約50種
SEI_*.md 文書                          22
runtime/go/cmd/sei-*                    3
```

`fixtures/representation-profiles/*.json`の実digest 6件は合成payloadに対するもので`sei`文字列を含まないため、Representation Profile conformanceは改名の影響を受けません。

`sei`および`井`は、current tree上で衝突0件です。

`.github/workflows`は存在しません。`plan/DEVELOPMENT_WORKFLOW.md`のとおりGitHub Actionsは完全停止中であり、CI定義の追随作業は発生しません。検証はlocalでのcheckerとtest実行によります。

`evaluation/method-quality/historical/M1B-RUN-33596839607/review-manifest.json`は、`request.json`・`structure-report.json`を含む6fileのsha256を記録しています。これらのfileは`sei`文字列を含みます。

### 現時点の推論・仮説

- 環境変数とCLI flagは`runtime/integration/`のtestからも参照されているため、改名はtestと同時に行わなければ検出できないfailureが出ます。
- Go module pathの変更は`runtime/go/`配下のimport全件に及びます。`go build`と`go test`が同時に通ることを一つのPhaseの完了条件にします。

### Unknown / Conflict

- 記録済みEvidence文書の本文に書かれた旧repository URLを、注記付きで残すか、注記なしで残すかが未定です。ADR-0031は内容を変更しないと定めているため既定は「注記なしで残す」ですが、読者の混乱を避ける注記を別fileへ置く余地があります。
- Go toolchainがこのmachineのどこにあるかを未確認です。Phase 2の着手前に確認が必要です。Pythonについては、Windows側の`python`がStore stubであり、実体はWSL2側の`python3`のみであることを確認済みです。

## Questions

1. 内部record schemaのreader側で`sei.*`を受け付ける実装を、checkerごとに個別に書くか、共通のidentity正規化関数へ集約するか。
2. 記録済みEvidence文書中の旧repository URLについて、別fileの注記を置くか、ADR-0031への参照のみで足りるとするか。
3. `SEI_TEI_*`系の環境変数は、関連製品TEIとの境界に位置する。TEI側が同名の変数を読んでいないことを、改名前に確認する必要があるか。

1と2は意味上の未決事項です。3は事実確認であり、Phase 3の着手条件です。

## Constraints

- ADR-0031の4（記録済みEvidenceを改名しない）を、いかなる作業効率上の理由でも破らない。
- ADR-0021のlogical identityとversionの分離を維持する。identifier改名を理由にContract versionを進めない。
- 改名途中の混在状態でreleaseしない。Phase単位でcheckerを通す。
- readerの双方向受理を、期限付きの暫定措置として実装しない。記録済みEvidenceが存在する限り必要な恒久措置として書く。
- Non-goal: Contract意味境界の見直し、stable `v1`への移行、field / schema shapeの変更、新規Contractの追加。

## Required scenarios / experiments

### Phase 1 — Contract identity

対象は portable Contract 5、Representation Profile 2、verifier reference 2、JSON Schema `$id` host 5file、negative / boundary fixture identity 3件です。

- PASS: `tools/check_contract_conformance.py`と`tools/check_representation_profiles.py`が成功し、`fixtures/contracts/`と`fixtures/representation-profiles/`のすべてが新identityで検証を通る。`runtime/go/`のtestが成功する。
- FAIL: 上記のいずれかが失敗する。
- NOT_VERIFIED: checkerが対象identityへ到達していない。

### Phase 2 — repository / Go module path

- PASS: `go build ./...`と`go test ./...`が`runtime/go/`で成功し、module pathが`github.com/hat47x/sei-cognition/runtime/go`である。
- FAIL: build / testのいずれかが失敗する。

Go toolchainの所在確認をこのPhaseの前提とします。

### Phase 3 — 環境変数 / CLI flag

- PASS: `runtime/integration/`のtestが成功し、tree内に`SEI_`で始まる環境変数参照と`--sei-`で始まるflagがlive code上へ残っていない。
- FAIL: testが失敗する、または残存がある。

Question 3の事実確認をこのPhaseの着手条件とします。

### Phase 4 — 文書 / registry

- PASS: `plan/scripts/check_plan_registry.py`、`check_document_review_registry.py`、`check_requirements_registry.py`、`check_github_actions_disabled.py`がすべて成功する。
- FAIL: いずれかが失敗する。

### 全Phase共通 — 記録済みEvidenceの不変性

各Phaseの完了時に実行します。ADR-0031の4-aと4-bへ対応して、二つの検査を行います。

- PASS (4-a): `evaluation/method-quality/historical/`、`runtime/evidence/`、`release/`配下の全fileについて、改名前のsha256と一致する。さらに`review-manifest.json`が記録するdigestが、対応fileの実digestと一致する。
- PASS (4-b): ADR-0031の4-bが挙げる日付付き文書22件について、`sei`を含む行が改名前と一致する。
- FAIL: いずれかが不一致。

改名前のbaselineは、Phase 1着手前に取得して`plan/`配下の作業記録ではなく一時領域へ置き、各Phase完了時に照合します。

この検査は他のPASSに優先します。他がすべてPASSでもこれがFAILなら、そのPhaseはFAILです。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

本Issueで成立するのは、各PhaseのExecutable Evidenceまでです。改名の完了をRelease Evidenceへ自動昇格させません。

## Deliverables

- ADR-0031をAcceptedへ変更する。
- Phase 1〜4の実施。
- 内部record schema readerの双方向受理実装と、ADR-0031を参照するcode comment。
- `contracts/CONTRACT_CATALOG.md`、`architecture/TRACEABILITY.md`、`contracts/TRACEABILITY.md`の新identityへの同期。
- `README.md`見出しを「井 / SEI Cognition」へ変更。
- `evaluation/`配下の名称mapping注記。
- `plan/registry.yaml`と`plan/document_review_registry.yaml`への登録。
- 記録済みEvidence不変性の検査結果記録。

## Resolution

次がすべて成立したときResolvedにできます。

- Phase 1〜4がすべてPASSしている。
- 全Phaseで記録済みEvidence不変性検査がPASSしている。
- ADR-0031がAcceptedであり、mapping tableがcurrent treeの実装と一致している。
- Questions 1〜3に結論が出ており、その結論が成果物へ反映されている。

ResolvedはRelease / Operational / Adoption / Outcomeの成立を意味しません。

## Reopen conditions

- 外部実装が`sei.*` identityを参照している事例が確認され、双方向受理だけでは不足することが判明した。
- 記録済みEvidenceの不変性が、改名後のcommitで破られたことが判明した。
- ADR-0031のmapping tableでは解決できないhistorical reconstruction要求が確認された。
- `sei.` prefixが他のContract名前空間と衝突した。

## CI / verification

GitHub Actionsは停止中のため、すべてlocalで個別に実行します。このmachineではPythonの実体がWSL2側にのみ存在するため、Python製checkerは次の形で実行します。

```bash
wsl -e bash -lc "cd /mnt/d/GIT/sei && python3 plan/scripts/check_plan_registry.py"
```

実行対象:

- `tools/check_contract_conformance.py`
- `tools/check_representation_profiles.py`
- `plan/scripts/check_plan_registry.py`
- `plan/scripts/check_document_review_registry.py`
- `plan/scripts/check_requirements_registry.py`
- `plan/scripts/check_github_actions_disabled.py`
- `runtime/go/`の`go build ./...` / `go test ./...`
- `runtime/integration/`のtest

checker successをProduct Value達成やRelease readinessの証明にはしません。

## Natural Japanese review

内容・構造を確定した後、自然な日本語を最重要視して全文を再ドラフトした。再ドラフト前後で、Goalの4条件、Phase区分とPASS / FAILの読み方、記録済みEvidence不変性検査が他に優先すること、Non-goal、Reopen条件、Evidenceの高さが変わっていないことを確認した。
