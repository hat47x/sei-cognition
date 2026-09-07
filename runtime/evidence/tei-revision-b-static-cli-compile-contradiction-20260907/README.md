# TEI revision B static CLI compile contradiction — 2026-09-07

## 位置づけ

このEvidenceは、fixed revision B
`1a7028d444fcae60a1c4f2f2d247456f4c7c35be`
のGit object identityへ固定したsource bytesから観測できる、CLI source-levelの静的矛盾を記録する。

これはcanonical exact-B checkoutでのactual E2 build結果ではない。

## 観測1: `validateWorkspace` の二重定義

fixed-Bでは次の2ファイルが同じ`package main`に属し、同じtop-level function名を定義している。

```text
cmd/tei/main.go:939
  func validateWorkspace(root string) bool
  blob = 6a27b98b7f6dbe4e66d1261edfc847402cd608a5

cmd/tei/validation_output.go:11
  func validateWorkspace(out io.Writer, root string) (int, error)
  blob = 2ca746592d325ec0f277cebc7c297e49d3022829
```

Goではtop-level functionをsignature違いでoverloadしないため、これはsource-levelのdeterministic compile contradictionとして扱う。

## 観測2: workspace API世代の不一致

fixed-B `cmd/tei/validation_output.go`は次を参照する。

```text
workspace.DiagnosticFromLoadError
```

一方、fixed-B workspace sourceでは`internal/workspace/source_diagnostic.go`が次を定義している。

```text
workspace.SourceDiagnosticFromError
blob = 59fd57685e44edba62e538c31b6db51b62d4e651
```

`ProjectedDiagnostic` / `ProjectDiagnostics`は`internal/workspace/diagnostic_projection.go`
（blob `137d139fc7e51c10af3b5cb3082a12a2c37e7410`）に存在する。

したがって、`validation_output.go`は少なくとも`DiagnosticFromLoadError`についてfixed-B workspace APIと一致していない。

## 履歴上の関係

`validation_output.go`は`e619ef58ffcc7c17645e3e24e8974f56f6cf18b7`で追加された。

その後、fixed-B祖先の`c804931c2480bd45ee5831455f123f5bf8a3bd71`では`main.go`へ別の`validateWorkspace`と`SourceDiagnosticFromError`側の経路が追加された。

`3b928502a5f5d8519335fb3dabed9512ebd6005a`（`fix: restore build after reference feature integration`）にはこの衝突を解消する方向の変更があるが、GitHub compare上このcommitはfixed-Bのancestorではなくdivergedしている。したがって、そのfixをfixed-Bへ含まれているものとして扱わない。

## 停止線

```text
fixed-B exact source bytesでstatic contradiction observed
  != canonical exact-B checkout actual build FAIL
  != revision B Provider Plan failure
  != current SOZA Adapter incompatibility
  != quality judgement
  != ISSUE-000072 Resolved
```

canonical exact-B checkoutが利用可能になった時点では、既存E2 partial runnerでactual buildを実行し、この静的観測を実行結果と独立に照合する。

machine-readable recordは`evidence.json`を正とする。
