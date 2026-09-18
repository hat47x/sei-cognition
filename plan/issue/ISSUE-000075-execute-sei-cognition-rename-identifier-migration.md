# ISSUE-000075: SEI Cognitionへの改名とidentifier移行を実施する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0003, ADR-0021, ADR-0031**  
Updated: 2026-09-13

## Goal

ADR-0031で定めたclass別の規則に従って改名を実施し、完了時に次を判別可能な状態にします。

- current tree上のlive codeとlive文書に、Contract identity・repository path・環境変数・CLI flagとしての`soza`が残っていない。
- 記録済みEvidence（`evaluation/method-quality/historical/`、`runtime/evidence/`、`release/`、`contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md`）が、内容・digestともに改名前と一致する。
- 記録済みEvidenceを読むcheckerが、旧identity `soza.*`を受け付けたまま成功する。
- `soza.*/v1alpha1`をbasisとするv0.2.0時点のArtifactが、ADR-0031のmapping tableによって新identityへ解決できる。

「置換した」だけでは完了としません。上の4点が同時に成立して初めて完了です。

## Background

### 確認済みの事実

current tree上の実測値です。

```text
soza を含むfile                        428
soza. で始まるdistinct identifier      105
  うち portable Contract / Profile       7
  うち runtime verifier reference        2
  うち negative / boundary fixture       3
  うち 内部record schema (/v1)          80
      live codeからも参照               58
      記録済みEvidence内のみ            22
環境変数・CLI flag                    約50種
SOZA_*.md 文書                          22
runtime/go/cmd/soza-*                    3
```

`fixtures/representation-profiles/*.json`の実digest 6件は合成payloadに対するもので`soza`文字列を含まないため、Representation Profile conformanceは改名の影響を受けません。

`sei`および`井`は、current tree上で衝突0件です。

`.github/workflows`は存在しません。`plan/DEVELOPMENT_WORKFLOW.md`のとおりGitHub Actionsは完全停止中であり、CI定義の追随作業は発生しません。検証はlocalでのcheckerとtest実行によります。

`evaluation/method-quality/historical/M1B-RUN-33596839607/review-manifest.json`は、`request.json`・`structure-report.json`を含む6fileのsha256を記録しています。これらのfileは`soza`文字列を含みます。

### 現時点の推論・仮説

- 環境変数とCLI flagは`runtime/integration/`のtestからも参照されているため、改名はtestと同時に行わなければ検出できないfailureが出ます。
- Go module pathの変更は`runtime/go/`配下のimport全件に及びます。`go build`と`go test`が同時に通ることを一つのPhaseの完了条件にします。

### Unknown / Conflict

- 記録済みEvidence文書の本文に書かれた旧repository URLを、注記付きで残すか、注記なしで残すかが未定です。ADR-0031は内容を変更しないと定めているため既定は「注記なしで残す」ですが、読者の混乱を避ける注記を別fileへ置く余地があります。
- Go toolchainがこのmachineのどこにあるかを未確認です。Phase 2の着手前に確認が必要です。Pythonについては、Windows側の`python`がStore stubであり、実体はWSL2側の`python3`のみであることを確認済みです。

## Questions

1. 内部record schemaのreader側で`soza.*`を受け付ける実装を、checkerごとに個別に書くか、共通のidentity正規化関数へ集約するか。
2. 記録済みEvidence文書中の旧repository URLについて、別fileの注記を置くか、ADR-0031への参照のみで足りるとするか。
3. `SOZA_TEI_*`系の環境変数は、関連製品TEIとの境界に位置する。TEI側が同名の変数を読んでいないことを、改名前に確認する必要があるか。

1と2は意味上の未決事項です。3は事実確認であり、Phase 3の着手条件です。

### 現時点の回答

**1: checkerごとに個別に書く。** 対象scriptは`tools/`、`evaluation/method-quality/`、`runtime/integration/`の三領域に分かれ、それぞれ独立して実行されます。共通moduleへ集約すると`sys.path`操作を伴う依存が生まれ、単体で実行できるという現在の性質を損ないます。各fileへ`legacy_schema()`を置き、docstringからADR-0031へ参照を張りました。`tools/check_release_candidate.py`と`tools/prepare_v0_2_0_release.py`は既存の`require_*`族に合わせ、`require_renamed_string` / `require_renamed_equal`として実装しています。

**2: ADR-0031への参照で足りるとし、READMEからその参照を張る。** 旧repository URLはGitHubのrepository renameによるredirectで解決します。別fileの注記を置くとADR-0031のmapping tableと二重の正本ができます。ただし`evaluation/`については、`historical/`配下をbyte単位で不変とする境界を領域内で明示する価値があるため、`evaluation/HISTORICAL_SCHEMA_IDENTITY_MAPPING.md`を置きました。ADR-0031の適用範囲を具体化するものであり、権威はADR-0031にあります。

**3: 確認済み。前提は正しい。** 2026-09-13に`hat47x/tei-platform`をlocalで参照できるようになったため実測しました。TEI側のtreeには`SOZA_`で始まる環境変数の参照が1件もありません。`SOZA_TEI_*`はSEI側がTEIを呼ぶときに読む変数であり、TEI自身の設定面ではないという前提は成立しています。したがって`SEI_TEI_*`への改名でTEI側が壊れることはありません。

TEI側に残る`soza`は次の2件で、いずれも環境変数ではなくTEIが所有する記述です。SEI側の改名では扱いません。

- `.github/workflows/soza-e3b-p2-evidence.yml` — 当時のE3b-P2 Evidence採取workflow。`tei.soza-e3b-p2-evidence/v1`というTEI名前空間のschemaと、`evidence/soza-e3b-p2-version-exchange-2026-09-05`というhistorical tag triggerを持ちます。
- `plan/DERIVED_COGNITIVE_REQUIREMENT_DRAFT_2026-09.md` — 「SOZA系の認知・判断境界から取り込むもの」という散文。

これらの改名可否はTEI側のADR / Issueで判断します。ADR-0031のmapping tableは、TEI側がSEI Cognitionのidentityを参照するときの解決手段として利用できます。

### 本Issue自身の扱い

本IssueとADR-0031は、ADR-0031の4-cが定めるとおり改名の対象外です。どちらも改名そのものを主題とし、旧identityと新identityの両方を保持する必要があります。一括改名に含めると、「旧identity`soza.*`も受け付ける」という記述が「`sei.*`を受け付ける」という無意味な文へ変わります。

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

- PASS: `runtime/integration/`のtestが成功し、tree内に`SOZA_`で始まる環境変数参照と`--soza-`で始まるflagがlive code上へ残っていない。
- FAIL: testが失敗する、または残存がある。

Question 3の事実確認をこのPhaseの着手条件とします。

### Phase 4 — 文書 / registry

- PASS: `plan/scripts/check_plan_registry.py`、`check_document_review_registry.py`、`check_requirements_registry.py`、`check_github_actions_disabled.py`がすべて成功する。
- FAIL: いずれかが失敗する。

### 全Phase共通 — 記録済みEvidenceの不変性

各Phaseの完了時に実行します。ADR-0031の4-aと4-bへ対応して、二つの検査を行います。

- PASS (4-a): `evaluation/method-quality/historical/`、`runtime/evidence/`、`release/`配下の全fileについて、改名前のsha256と一致する。さらに`review-manifest.json`が記録するdigestが、対応fileの実digestと一致する。
- PASS (4-b): ADR-0031の4-bが挙げる日付付き文書22件について、`soza`を含む行が改名前と一致する。
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

### 成立した結論 (2026-09-13)

Phase 1〜4を完了しました。改名はcurrent tree全体へ適用され、記録済みEvidenceは不変のまま残っています。

実際に成立した内容:

- portable Semantic Contract 5件、Representation Profile 2件、runtime verifier reference 2件を`v1alpha1`のまま`sei.*`へ改めた。
- Go moduleを2つとも`github.com/hat47x/sei-cognition/...`へ改め、`runtime/go/cmd/sei-*`へ追随させた。
- 環境変数約52種とCLI flagを`SEI_*` / `--sei-*`へ一斉に切り替えた。互換aliasは設けていない。
- 製品名の散文表記、日本語名`井`、`SEI_`接頭辞の文書23件へ反映した。
- 記録済みEvidenceを読む側へ双方向受理を実装した。`tools/check_release_candidate.py`、`tools/prepare_v0_2_0_release.py`、`evaluation/method-quality/validate_case_catalog.py`、`evaluation/failure-behavior/test_actual_provider_missing_revision_observation.py`、`runtime/integration/`の5件が対象。
- 2026-09-12にmain branchから合流した`evaluation/failure-behavior/`、`evaluation/personal-inquiry-decision/`、`evaluation/sparse-associative-cognition/`、`evaluation/sei-cognition-orchestration/`等へも同じ規則を適用した。

確認できたEvidenceの高さ:

```text
Executable Evidence (fixture / test / checker scoped)
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

- `go build ./...`が2 moduleとも成功。`go test ./...`の失敗集合はdevelop/v0.2.0およびmainと一致し、改名由来の新規failureはない。
- python test 736件で改名前後の失敗集合を比較し、新規failureなし。
- `check_plan_registry` / `check_document_review_registry` / `check_requirements_registry` / `check_github_actions_disabled` / `check_contract_conformance` / `check_representation_profiles` / `check_release_candidate` (v0.1.0, v0.2.0) がすべてPASS。
- ADR-0031の4-a対象118 fileがdigest一致。4-b対象の`soza`記述も一致。

意図的に残した未完了事項:

- `runtime/go`の既存failure 3件（`externalintegration`のGit blob SHA-1 pin不一致2件、`teiintegration`のProvider Plan SHA-256不一致、`livemethodintegration`の`runtimeExchangeKJAtlasDirEnv`未定義によるtest build不能）は改名前から存在し、本Issueの範囲外です。
- TEI側の`.github/workflows/soza-e3b-p2-evidence.yml`と`plan/DERIVED_COGNITIVE_REQUIREMENT_DRAFT_2026-09.md`に残る`soza`は、TEIが所有する記述のためTEI側で判断します。

### Post-resolution regression guard (2026-09-18)

後続のISSUE-000072作業を再監査したところ、改名前に作成したcurrent operator文書の一部へ、旧`SOZA_REPO / SOZA_GO / SOZA_HEAD`、旧`--soza-*` CLI、旧`soza_* / sozaGo*` stage / result keyの説明が残っていることを確認した。current runtime codeはすでにSEI名へ移行済みであったため、これはhistorical Evidence互換ではなく、operator手順がcurrent CLIとずれるpost-resolution regressionとして扱った。

2026-09-18に次を実施した。

- ISSUE-000072のcurrent version-exchange runbook / readiness / failure-stage文書を、current `SEI_REPO / SEI_GO / SEI_HEAD`、`--sei-*`、`sei_* / seiGo*`へ同期した。
- 実在するhistorical workflow名 `SOZA E3b-P2 TEI Evidence`、historical artifact / branch名、記録済みEvidenceの`soza.*` schemaは観測事実として変更していない。
- reader側の`legacy_schema()`等、ADR-0031が要求するhistorical `soza.*`受理も変更していない。
- `plan/scripts/check_sei_operator_identity.py`を追加し、ISSUE-000072のcurrent operator surfaceへobsolete operational tokenが再流入した場合だけfailする境界を固定した。
- checker self-testはGit blob一致を確認した再構成環境で6/6 PASS。current `develop/v0.2.0`の対象operator surface 24 fileをGitHub treeから実査し、obsolete operational tokenは0件だった。

このguardは改名前の全記録を書き換えるcheckerではない。

```text
current operator identity guard PASS
  != historical Evidence rewritten
  != all uses of the word SOZA prohibited
  != rename migration re-executed from scratch
  != Release / Operational / Adoption Evidence
```

## Reopen conditions

- 外部実装が`soza.*` identityを参照している事例が確認され、双方向受理だけでは不足することが判明した。
- 記録済みEvidenceの不変性が、改名後のcommitで破られたことが判明した。
- ADR-0031のmapping tableでは解決できないhistorical reconstruction要求が確認された。
- `sei.` prefixが他のContract名前空間と衝突した。

## CI / verification

GitHub Actionsは停止中のため、すべてlocalで個別に実行します。このmachineではPythonの実体がWSL2側にのみ存在するため、Python製checkerは次の形で実行します。

```bash
wsl -e bash -lc "cd /mnt/d/GIT/sei-cognition && python3 plan/scripts/check_plan_registry.py"
```

実行対象:

- `tools/check_contract_conformance.py`
- `tools/check_representation_profiles.py`
- `plan/scripts/check_plan_registry.py`
- `plan/scripts/check_document_review_registry.py`
- `plan/scripts/check_requirements_registry.py`
- `plan/scripts/check_github_actions_disabled.py`
- `plan/scripts/check_sei_operator_identity.py`
- `python3 -m unittest plan/scripts/test_check_sei_operator_identity.py`
- `runtime/go/`の`go build ./...` / `go test ./...`
- `runtime/integration/`のtest

checker successをProduct Value達成やRelease readinessの証明にはしません。

## Natural Japanese review

内容・構造を確定した後、自然な日本語を最重要視して全文を再ドラフトした。再ドラフト前後で、Goalの4条件、Phase区分とPASS / FAILの読み方、記録済みEvidence不変性検査が他に優先すること、Non-goal、Reopen条件、Evidenceの高さが変わっていないことを確認した。
