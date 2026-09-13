# TEI revision B後のrepair統合境界 — 2026-09-07

## 位置づけ

このEvidenceは、fixed revision B `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`で観測したsource-level compile矛盾が、その後のTEI Git履歴上でどこに統合されたかを記録する。

fixed-B自体のStatic Evidenceは次を正とする。

`runtime/evidence/tei-revision-b-static-cli-compile-contradiction-20260907/evidence.json`

本Evidenceはrevision Bを後続revisionへ差し替えない。また、後続revisionをISSUE-000072の新しい検証対象として選定するものでもない。

## 観測した境界

known repair commitは次である。

```text
3b928502a5f5d8519335fb3dabed9512ebd6005a
fix: restore build after reference feature integration
```

このrepair lineageの後続 `0f4164d31fb938f6ea2a219efb5fff492085f4e3` では、CLI sourceは次のrepair後blobになっている。

```text
cmd/tei/main.go
  ef2e10faac836959caf46a6a16cef5486e13ca0b

cmd/tei/validation_output.go
  5bdd0bef621efafc4e1154099c4b8b76e8228a91
```

一方、当時の`origin/main`側 `241c2c7d75a755678b4158f72f4d4e2826a3f29d` はfixed-Bのdescendantだがrepair commitとはdivergedしており、fixed-Bと同じ旧CLI blobを保持していた。

```text
cmd/tei/main.go
  6a27b98b7f6dbe4e66d1261edfc847402cd608a5

cmd/tei/validation_output.go
  2ca746592d325ec0f277cebc7c297e49d3022829
```

この状態では`main.go`側の別`validateWorkspace`が残り、`validation_output.go`も`workspace.DiagnosticFromLoadError`を参照している。

両lineageが直接合流する境界は次である。

```text
b371111b6103439a28acde4c8fbe3cb11b9c611c
2026-09-06T02:53:02Z
Merge remote-tracking branch 'origin/main'

parent 1 = 0f4164d31fb938f6ea2a219efb5fff492085f4e3
parent 2 = 241c2c7d75a755678b4158f72f4d4e2826a3f29d
```

Git compare上、`b371111b...`はfixed-Bと`3b928502...`の双方をancestorとして持つ。一方、merge直前ではrepair側parent `0f4164d...` とfixed-Bはdiverged、fixed-B側parent `241c2c7d...` とrepair commitもdivergedしている。

したがって、このmergeは今回観測した2 parent lineageについての**minimal common-descendant integration boundary**として扱える。

merge結果ではCLI sourceがrepair後blobへ揃う。

```text
cmd/tei/main.go
  ef2e10faac836959caf46a6a16cef5486e13ca0b
  -> main.go側の重複validateWorkspaceは存在しない

cmd/tei/validation_output.go
  5bdd0bef621efafc4e1154099c4b8b76e8228a91
  -> workspace.SourceDiagnosticFromErrorを参照
```

## 意味

この履歴観測から言えるのは、fixed-Bで観測したCLI source-level矛盾が後続履歴ではrepairされ、fixed-B lineageとrepair lineageが`b371111b...`で合流したことまでである。

言えないことは明確に分ける。

```text
post-B repair integration boundary observed
  != revision B replaced
  != successor revision selected
  != revision B actual build FAIL established
  != successor revision build PASS
  != Provider Plan compatibility verified
  != SOZA Adapter compatibility verified
  != ISSUE-000072 Resolved
```

特に、ISSUE-000072のcomparison axisは引き続きfixed revision Bへ束縛する。#317で同期した停止線どおり、まずfixed-Bをcanonical actual E2で検証する。

actual E2でfixed-B build failureが確認された場合も、そのfailure Evidenceとexact-B bindingを保持する。Adapter version-exchangeの問いを続けるため後続revisionを使う場合は、その時点で別revisionとして明示的に固定する必要がある。本Evidence単独では`b371111b...`をその候補へ昇格させない。

## Evidenceの高さ

```text
evidenceNature = static_git_history_observation
qualityJudgement = not_evaluated
ISSUE-000072 = Open
```

actual process execution、binary identity、Provider Plan output、current SOZA Adapter live compatibilityは本Evidenceでは観測していない。
