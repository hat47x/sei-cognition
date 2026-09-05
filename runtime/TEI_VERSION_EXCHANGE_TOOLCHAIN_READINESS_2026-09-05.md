# TEI Version Exchange Toolchain Readiness — 2026-09-05

## 1. この文書の位置づけ

PMS-06 / ISSUE-000072のactual revision B実行前レビューで、E2とE3が同じ`go` executableを前提にすると、一つの実行環境で連続実行できないtoolchain境界が見つかりました。

- E2 `run_tei_revision_b_prepositioned.py`はhistorical build条件としてGo `1.23.2`を要求します。
- E3 `run_tei_bundle_adapter_compatibility.py`はcurrent SOZA `runtime/go/go.mod`を使い、`GOTOOLCHAIN=local`でcurrent local toolchainを要求します。現在のmoduleはGo `1.25`です。

したがって、単一の`go` executableを両段階へそのまま使うことをexecution readinessの暗黙前提にしません。

```text
TEI historical build toolchain
  = Go 1.23.2

current SOZA live-test toolchain
  = Go 1.25系 / GOTOOLCHAIN=local

same command name "go"
  != same executable identity
```

この確認はactual revision B executionではありません。

## 2. toolchainを分離した連続実行入口

`runtime/integration/run_tei_version_exchange_evidence.py`を追加し、既存E2 / E3 runnerを順番に呼ぶ薄いorchestratorとしました。

必須引数は次です。

- `--source-repo`: exact revision B checkout
- `--reference-source-repo`: exact revision A checkout
- `--soza-repo-root`: current SOZA checkout
- `--output-dir`: Evidence出力先。revision B / revision A / SOZA checkoutと相互包含しない、新しいnon-symlink pathを使う。
- `--tei-go-executable`: E2用Go 1.23.2 executable
- `--soza-go-executable`: E3用current SOZA Go executable

両Go executableはLinux上の`go`というbasenameを持つfileとして明示します。symlink `.../bin/go`も、actual targetを解決したうえで利用できます。

orchestratorは各段階の間だけ指定Goのdirectoryを`PATH`先頭へ置き、段階終了後に元の`PATH`へ戻します。

```text
E2
  PATH -> TEI Go 1.23.2
  run_tei_revision_b_prepositioned.py

E3
  PATH -> SOZA Go 1.25系
  run_tei_bundle_adapter_compatibility.py
```

既存runnerのbuild条件、Provider Plan invocation、Adapter mapping semanticsは変更しません。

actual process開始前にはEvidence出力pathも検査します。combined runnerは`--output-dir`自身または既存ancestorのsymlinkを拒否し、revision B checkout、revision A checkout、SOZA checkoutの配下へEvidence directoryを置くことも、Evidence directoryがそれらを包含することも拒否します。`mkdir`はこの検査後にだけ行います。

standalone E2もfinal archive path / ancestor symlink、入力checkoutやSOZA repository配下への出力、既存archiveの暗黙上書きを拒否します。

```text
Evidence path configuration rejected
  = pre-stage configuration rejection
  != E2 process failure
  != E3 process failure
```

## 3. Evidence reportの段階性

出力は次の2 fileです。

```text
tei-e3b-p2-revision-b.tar.gz
tei-version-exchange-evidence.json
```

reportの`result`は、少なくとも次を区別します。

```text
e2_failed
  = B bundle生成まで成立していない

e2_bundle_verified_e3_not_run
  = E2成立後、E3開始前のinterim state

e2_verified_e3_failed
  = E2 bundleは成立したがcurrent Adapter live検査は不成立

fixed_scope_e2_e3_verified
  = exact-B executable + exact-A fixed input + 記録されたSOZA sourceについてE2/E3が成立
```

E3が失敗しても、成立済みE2 bundleを削除しません。E2 EvidenceとE3 compatibility failureを混同しないためです。

一方、E2が失敗した場合はE3を起動しません。

path configuration rejectionはこれらのE2 / E3 resultへ昇格させません。checkoutやEvidenceへ副作用を出す前の入力拒否です。

## 4. 既存Evidenceの上書き境界

既定では、出力先にbundleまたはreportが既に存在すると実行を拒否します。

```text
existing Evidence
  != implicit overwrite target
```

再実行で同じ出力先を使う場合だけ`--overwrite`を明示します。

`--overwrite`時はcombined runnerが旧bundle / reportを実行開始前に削除します。したがって、新しいE2が失敗したときに旧bundleだけが残り、新しいrunで生成したEvidenceのように見える状態を作りません。

standalone E2は既存archiveを暗黙上書きしません。`--overwrite`はcombined runner側の明示契約であり、standalone E2へ既存archiveをそのまま渡して上書きさせるものではありません。

## 5. synthetic検査

path-safety追加前に、repository-local orchestrator synthetic検査で次の7件を確認済みです。

1. E2とE3で別々のGo executableがPATH先頭へ入る。
2. E2 failureではfailure reportを残し、E3を起動しない。
3. E3 failureでは成立済みE2 bundleと段階別reportを保持する。
4. 明示なしに既存Evidenceを上書きしない。
5. `--overwrite`後にE2が失敗しても旧bundleが残らない。
6. basenameが`go`ではないtoolchain指定を拒否する。
7. basenameが`go`のsymlinkをactual target identityへ解決して利用できる。

PR #223では、さらに次のnegative controlをbranch testへ追加しました。

- standalone E2: revision A/B checkout内出力を拒否する。
- standalone E2: SOZA repository内出力を拒否する。
- standalone E2: existing archiveを拒否する。
- standalone E2: symlink archiveを拒否する。
- combined runner: revision A/B/SOZA checkout内のoutput directoryを作成前に拒否する。
- combined runner: output directoryが入力checkoutを包含する配置を拒否する。
- combined runner: symlink output directoryをrunner開始前に拒否する。

これら追加testをcurrent ChatGPT execution environmentでfull suiteとして再実行したとは主張しません。HAT47Xがofflineであり、GitHub Actionsもcurrent baselineでは使用しません。

これはorchestration / Evidence境界のsynthetic検査であり、actual TEI revision BのbuildやSOZA Adapter互換性を示すものではありません。

## 6. actual実行例

### root権限なしのuser-local toolchain準備例

実行環境にGoがない場合、system packageや`sudo`を前提にせず、Go公式Linux / amd64 archiveをrepository外へ展開できます。

E2用Go 1.23.2はhistorical Evidence条件へ固定します。E3用のGo 1.25.0は、current `runtime/go/go.mod`のGo 1.25を満たす**再現可能なexecution candidate**としてここで例示するもので、Stable RequirementやUniversal Contractへ昇格させません。実行時にはactual `go version`がEvidence reportへ残ります。

Go公式配布ページで確認したLinux / amd64 archiveのSHA-256は次です。

```text
go1.23.2.linux-amd64.tar.gz
  542d3c1705f1c6a1c5a80d5dc62e2e45171af291e755d591c5e6531ef63b454e

go1.25.0.linux-amd64.tar.gz
  2852af0cb20a13139b3448992e69b868e50ed0f8a1e5940ee1de9e19a123b613
```

user-local配置例:

```bash
export TOOLCHAIN_ROOT="$HOME/.local/opt/soza-tei-go"
mkdir -p "$TOOLCHAIN_ROOT"
cd "$TOOLCHAIN_ROOT"

test ! -e "$TOOLCHAIN_ROOT/go1.23.2"
curl -fL --retry 3 \
  -o go1.23.2.linux-amd64.tar.gz \
  https://go.dev/dl/go1.23.2.linux-amd64.tar.gz
printf '%s  %s\n' \
  542d3c1705f1c6a1c5a80d5dc62e2e45171af291e755d591c5e6531ef63b454e \
  go1.23.2.linux-amd64.tar.gz | sha256sum -c -
mkdir "$TOOLCHAIN_ROOT/go1.23.2"
tar -C "$TOOLCHAIN_ROOT/go1.23.2" --strip-components=1 \
  -xzf go1.23.2.linux-amd64.tar.gz

test ! -e "$TOOLCHAIN_ROOT/go1.25.0"
curl -fL --retry 3 \
  -o go1.25.0.linux-amd64.tar.gz \
  https://go.dev/dl/go1.25.0.linux-amd64.tar.gz
printf '%s  %s\n' \
  2852af0cb20a13139b3448992e69b868e50ed0f8a1e5940ee1de9e19a123b613 \
  go1.25.0.linux-amd64.tar.gz | sha256sum -c -
mkdir "$TOOLCHAIN_ROOT/go1.25.0"
tar -C "$TOOLCHAIN_ROOT/go1.25.0" --strip-components=1 \
  -xzf go1.25.0.linux-amd64.tar.gz

test "$("$TOOLCHAIN_ROOT/go1.23.2/bin/go" version)" = \
  "go version go1.23.2 linux/amd64"
test "$("$TOOLCHAIN_ROOT/go1.25.0/bin/go" version)" = \
  "go version go1.25.0 linux/amd64"
```

archive bytesのSHA-256確認前に展開しません。既存toolchain directoryも暗黙に上書きしません。

```text
official archive SHA-256 verified
  != TEI revision B build PASS
  != current SOZA Adapter live compatibility PASS
```

actual実行では、2つのGo installationを別々に指定します。`EVIDENCE_DIR`は3つのcheckoutと相互包含しない別directoryを指定します。

```bash
export TEI_B_REPO=/path/to/tei-revision-b
export TEI_A_REPO=/path/to/tei-revision-a
export SOZA_REPO=/path/to/soza
export EVIDENCE_DIR=/path/outside/checkouts/tei-version-exchange-evidence
export TEI_GO="$HOME/.local/opt/soza-tei-go/go1.23.2/bin/go"
export SOZA_GO="$HOME/.local/opt/soza-tei-go/go1.25.0/bin/go"

SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"

python3 "$SOZA_REPO/runtime/integration/run_tei_version_exchange_evidence.py" \
  --source-repo "$TEI_B_REPO" \
  --reference-source-repo "$TEI_A_REPO" \
  --soza-repo-root "$SOZA_REPO" \
  --output-dir "$EVIDENCE_DIR" \
  --tei-go-executable "$TEI_GO" \
  --soza-go-executable "$SOZA_GO" \
  --expected-soza-head "$SOZA_HEAD" \
  --json
```

同じdirectoryへ意図的に再実行するときだけ`--overwrite`を追加します。

## 7. 現在のEvidence状態

```text
separate E2/E3 toolchain requirement
  = identified

toolchain-split E2->E3 orchestrator
  = implemented

orchestrator synthetic tests before later path-safety additions
  = 7 passed

Evidence output / checkout separation guard
  = implemented

path-safety negative controls
  = committed; full suite not re-run in current environment

revision B actual CLI build / execution
  = Not Yet Verified

revision B Provider Plan
  = Not Yet Observed

revision B current SOZA Adapter live compatibility
  = Not Yet Verified
```

停止線は次です。

```text
toolchain split resolved in execution path
  + Evidence output path safety implemented
  != revision B build PASS
  != Provider Plan observed
  != current SOZA Adapter live compatibility PASS
  != arbitrary TEI version compatibility
  != Release Evidence
  != Operational Evidence
  != ISSUE-000072 Resolved
```

このtoolchain差やEvidence配置規則はStable RequirementやUniversal Contractへ昇格させません。historical TEI build再現とcurrent SOZA test executionを安全に観測するためのEvidence環境として保持します。