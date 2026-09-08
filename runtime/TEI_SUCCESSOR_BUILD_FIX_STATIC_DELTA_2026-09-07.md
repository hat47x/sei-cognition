# TEI Successor Build-Fix Static Delta — 2026-09-07

## 位置づけ

本書は、ISSUE-000072で固定したrevision Bを変更せず、後継TEI lineageについて得られた補助Static Evidenceだけを記録する。

固定比較軸は変更しない。

```text
revision B executable source
  = 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

revision A fixed reference input
  = 48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67
```

後継commitをrevision Bへ置き換えず、revision Cとしても固定しない。

## 1. fixed-Bで観測済みのsource-level contradiction

exact revision Bでは、同一`package main`内に次の2定義が存在する。

```text
cmd/tei/main.go
  func validateWorkspace(root string) bool

cmd/tei/validation_output.go
  func validateWorkspace(out io.Writer, root string) (int, error)
```

さらに`validation_output.go`は`workspace.DiagnosticFromLoadError`を参照する一方、fixed-B側のworkspace surfaceとは不整合がある。

これは既存ISSUE-000072で記録済みのStatic Evidenceであり、canonical Linux/amd64 + Go 1.23.2 actual checkout/buildの結果ではない。

```text
source-level contradiction observed
  != canonical actual revision B build FAIL
```

## 2. known build-fix lineageとfixed-Bは当初divergedしていた

既知のbuild-fix commitは次である。

```text
3b928502a5f5d8519335fb3dabed9512ebd6005a
fix: restore build after reference feature integration
```

このcommitはfixed revision Bのancestorではなく、当初はdivergedしたlineageに存在する。

したがって、このcommitをrevision Bへpatch適用したものとして扱わず、fixed-Bのactual Evidenceを後継sourceで代替しない。

## 3. 後継lineageのbounded convergenceを確認した

2026-09-05T14:05:58Zのmain-line commit `b1250fedce4f87515be25e225575b2fccec2152b` に対しては、known build-fix lineageとの関係はまだdivergedだった。

一方、2026-09-06T08:59:59Zのcommit

```text
564da346c0bc0dfe461d9c381354330624bf760e
Gate B same-run artifact独立監査toolを追加する
```

では、Git ancestry上で次を確認した。

```text
fixed revision B -> 564da346...
  status    = ahead
  mergeBase = fixed revision B
  aheadBy   = 274

known build-fix -> 564da346...
  status    = ahead
  mergeBase = known build-fix
  aheadBy   = 360
```

したがって、このcandidateはfixed-Bとknown build-fixの両方をancestorに持つ。

ただし「最初に両lineageが合流したcommit」までは特定しない。今回の目的はmerge-history archaeologyではなく、後継lineageで矛盾が解消可能であることを、Bのidentityを壊さず補助観測することである。

```text
latest observed non-converged boundary
  = 2026-09-05T14:05:58Z

observed converged candidate
  = 2026-09-06T08:59:59Z

exact earliest convergence
  = Not Determined / not required
```

## 4. convergence candidate自身でsource surfaceの修復を確認した

`564da346...`では、`cmd/tei/main.go`の観測範囲に旧`validateWorkspace(root string) bool`定義は存在せず、`cmd/tei/validation_output.go`に次の単一定義が存在する。

```text
func validateWorkspace(out io.Writer, root string) (int, error)
```

同fileではload error conversionも次へ揃っている。

```text
workspace.SourceDiagnosticFromError(root, err)
```

Git blob identity:

```text
candidate cmd/tei/main.go
  = ef2e10faac836959caf46a6a16cef5486e13ca0b

candidate cmd/tei/validation_output.go
  = 5bdd0bef621efafc4e1154099c4b8b76e8228a91
```

これら2 blobは2026-09-07 current main `19995a9304a6218c50ed8245ffd44a6403a4cc55`の同fileとも一致する。

よって、fixed-Bで観測した特定のsource-level contradictionは、少なくともこのbounded convergence candidateでは静的に解消されている。

これはcandidateのactual build PASSを意味しない。他のcompile error、runtime error、fixed-A input compatibility、Provider Plan surface、current SOZA Adapter compatibilityは未評価である。

## 5. ISSUE-000072での意味

今回の観測から、二つのことを分離できる。

```text
fixed revision B
  = original comparison target; actual E2 still required

later repaired lineage
  = supplemental evidence that the observed source defect is not necessarily a permanent Provider surface break
```

したがって、fixed-Bのactual executionを後継commitで代替しない。

同時に、将来actual environmentが得られた後、Bとは別に後継revisionを追加比較する価値は残る。その場合も、後継revisionを明示的に別identityとして固定し、A/B Evidenceを書き換えない。

## 6. 次の優先順位

Priority 1は変更しない。

1. canonical exact-B sourceを適切なLinux/amd64 execution environmentへ取得する。
2. exact Go 1.23.2 + exact-A fixed inputでactual E2 partialを実行する。
3. strict verifierでB/A identityを再確認する。
4. B actual binary / Provider Planを観測する。
5. current SOZA E3をresumeする。
6. その後、必要性が確認できた場合にのみ、後継revisionを別比較軸として追加する。

GitHub-hosted zero-step failureについても、cross-workflow runner-assignment boundaryが既にEvidence化されているため、同じworkflowの編集・反復rerunをProduct検証の代替にしない。

## 停止線

```text
successor convergence observed
  + fixed-B contradiction absent on candidate static surface
  != fixed revision B replacement
  != canonical actual revision B build PASS or FAIL
  != successor actual build PASS
  != successor Provider Plan PASS
  != current SOZA Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

Stable Requirement、Universal Contract、comparison axis、supported scope、quality judgement、Resolution条件は変更しない。

machine-readable Evidence:

`runtime/evidence/tei-successor-build-fix-convergence-20260907/observation.json`
