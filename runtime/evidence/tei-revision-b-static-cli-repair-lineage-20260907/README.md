# TEI revision B static CLI repair lineage — 2026-09-07

## 位置づけ

このEvidenceは、`runtime/evidence/tei-revision-b-static-cli-compile-contradiction-20260907/`で観測したfixed revision Bの静的compile矛盾が、その後のTEI履歴でどこに収束したかを記録する。

比較軸のrevision Bは変更しない。

```text
fixed revision B
  = 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

known repair commit
  = 3b928502a5f5d8519335fb3dabed9512ebd6005a
```

## 観測結果

fixed revision Bとknown repairは当初divergedしていた。

B側の系譜では、`241c2c7d75a755678b4158f72f4d4e2826a3f29d`まで次のbroken CLI blobを保持していた。

```text
cmd/tei/main.go
  = 6a27b98b7f6dbe4e66d1261edfc847402cd608a5

cmd/tei/validation_output.go
  = 2ca746592d325ec0f277cebc7c297e49d3022829
```

一方、repair側の`0f4164d31fb938f6ea2a219efb5fff492085f4e3`はknown repairのdescendantであり、CLIは次の修正版blobを持つ。

```text
cmd/tei/main.go
  = ef2e10faac836959caf46a6a16cef5486e13ca0b

cmd/tei/validation_output.go
  = 5bdd0bef621efafc4e1154099c4b8b76e8228a91
```

この二系譜を最初にcurrent mainlineへ収束したmergeとして、次を確認した。

```text
commit
  = b371111b6103439a28acde4c8fbe3cb11b9c611c

committed at
  = 2026-09-06T11:53:02+09:00

message
  = Merge remote-tracking branch 'origin/main'

parents
  = 0f4164d31fb938f6ea2a219efb5fff492085f4e3
  + 241c2c7d75a755678b4158f72f4d4e2826a3f29d
```

`b371111b...`ではfixed revision Bとknown repairの両方がancestorであり、CLI blobもrepair側の修正版へ一致する。

また、current mainのcommit listingでこのmerge直前に観測した`9976e743de614191173db96cd344ef21f09836bf`はknown repairのancestorではなく、broken B CLI blobを保持していた。

したがって今回の観測範囲では、`b371111b...`を**broken B lineageとrepair lineageの最初のmainline convergence boundary**として扱える。

## Evidence境界

このlineageは、fixed revision Bを後続revisionへ置き換える根拠ではない。

```text
repair lineage observed
  != revision B replaced
  != canonical actual revision B build result
  != Provider Plan result
  != SOZA Adapter compatibility result
  != ISSUE-000072 Resolved
```

ISSUE-000072の比較軸は引き続きfixed revision Bである。`b371111b...`は、Bの静的矛盾が後続履歴で修復されたことを示すinformative follow-up revision boundaryとしてのみ保持する。

canonical exact-B actual buildは依然としてNot Yet Verifiedであり、Provider PlanはNot Yet Observed、current SOZA Adapter compatibilityはNot Yet Verified、`qualityJudgement = not_evaluated`、ISSUE-000072はOpenのままである。

machine-readable Evidenceは`evidence.json`を参照する。
