# ISSUE-000074: actual TEI実行のEvidence採取プロトコルを実体化する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0020, ADR-0021, ADR-0024**  
Updated: 2026-09-11

## ID再採番の経緯

本Issueは当初ISSUE-000062として起票されたが、branch統合（commit `d993fb5`のintegrate/all-branches-20260908）の際に、別系統で採番されたISSUE-000062「v0.2.0 actual release publication workflowを実体化する」とID衝突を起こした。registryへ登録済みだったrelease publication側を既存のISSUE-000062として維持し、本Issueを未使用のISSUE-000074へ再採番した。

2026-09-11時点でISSUE-000073はSEI Cognition改名作業が使用中のため、`plan/scripts/next_plan_id.py`の提示値ではなくISSUE-000074を採った。

再採番はID衝突の解消だけを目的とする。本Issueの課題範囲、Evidence強度、未検証範囲は変更していない。

## Goal

E3b-P2「actual TEI process / service integration」を実際に評価できるよう、**外部から明示的に与えられたTEI binaryを実行し、そのbinary identity、sourceとのbinding状態、実行結果、current Capability Observationを一つのderived Evidence reportとして記録するプロトコル**を実体化する。

このIssueでは、private TEI repositoryの取得方法やcredential方式を固定しない。また、helper processやsynthetic binaryを実TEIとみなさない。目的は、実TEI binaryが供給された環境で同じ判定基準を再利用できるようにすることである。

```text
ISSUE-000061
  external executable injection boundary
        ↓
ISSUE-000074
  actual-binary Evidence collection protocol
        ↓
future actual TEI run
  E3b-P2 Scoped Executable Evidence
```

ISSUE-000074のPASSだけでは、E3b-P2のPASSにはならない。

## 背景

ISSUE-000061では、TEI source / binary acquisition、credential resolution、external process invocation、Provider固有JSON解釈、SEI Capability Observation mappingを分離した。

一方、actual E3b-P2を後から検証するには、「何を実行したか」を曖昧にしない必要がある。単に`tei`というfilenameやdeclared commitを記録するだけでは、実際に実行されたbytesとsource revisionの関係を追跡できない。

現時点の`hat47x/tei-platform`には、SEIがそのまま利用できるActions artifact uploadやGoReleaser等の既存binary配布経路は確認できていない。また、TEI repositoryはprivateであり、SEIの標準`GITHUB_TOKEN`が別private repositoryを取得できるとは仮定しない。

そのため、Evidence採取側では取得方式を問わず、供給されたbinaryについて観測可能なidentityを記録する。

```text
binary SHA-256
  = observed executable identity

declared repository / commit
  = source declaration

manifest match
  = declared source and binary digest are mutually consistent with the supplied manifest
  != manifest authenticity / signature verification
```

## Evidence reportの境界

新しいUniversal Contractは追加しない。

Evidence reportは`sei.e3b-tei-probe/v1`という**derived probe artifact**として扱う。SEIのsemantic authorityではなく、E3b-P2を評価するときの実行証跡である。

reportには少なくとも次を記録する。

- report schema
- probe result
- observed TEI binary SHA-256
- declared source repository
- declared source commit
- source-to-binary binding status
- bindingに使用したmanifestの有無
- `deployment-provider-plan`の実行対象solution / version
- 実行後に得られたcurrent Capability Observation

credential、token、secret、repository clone URLに埋め込まれた認証情報は記録しない。

## source-to-binary binding

build manifestは任意入力とする。

manifestを与えない場合:

```text
source_binding = not_verified
```

manifestを与えた場合は、次が一致する場合だけ:

- manifest schema
- declared repository
- declared commit
- observed binary SHA-256

```text
source_binding = manifest_matched
```

`manifest_matched`はmanifest自身の真正性、署名、build provenanceを検証したことを意味しない。将来TEI側で署名付きbuild provenance等が成立した場合は、別のEvidenceとして段階的に追加する。

## 実装方針

`runtime/go/teiprobe`にEvidence report生成を置き、`runtime/go/cmd/tei-e3b-probe`を薄い実行入口とする。

actual Evidence commandでは、`PrefixArgs`を使ったwrapperや`go run`ではなく、**直接実行するbinary file**を要求する。binary SHA-256が実際に呼ばれるexecutable bytesを指すようにするためである。

既存`runtime/go/teiintegration`を再利用し、Provider Planの意味mappingを二重実装しない。

## 必須検査

1. 実行対象binary fileのSHA-256を計算する。
2. source repository / commitを宣言としてreportへ保持する。
3. manifestなしではsource bindingを`not_verified`とする。
4. manifest一致時だけ`manifest_matched`とする。
5. manifestのrepository / commit / binary digest不一致を拒否する。
6. manifest unknown field / malformed JSON / multiple JSON valuesを拒否する。
7. Probe用commandではwrapper / PrefixArgsを許可しない。
8. TEI process failure / timeoutではPASS reportを生成しない。
9. success時のCapability Observationがcurrent validatorを通る。
10. credential / secretをreport fieldへ追加しない。
11. helper subprocessによるtestをactual TEI Evidenceへ昇格させない。
12. v0.2.0 supported release scopeをE3aから暗黙に拡張しない。

## Requirement / Scenario監査

新しいStable Requirement / Scenarioは追加しない。

主な既存正本は次で今回のEvidence採取境界を表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

binary digestやbuild manifestはEvidence / provenanceの実現手段であり、それだけを理由にUniversal Requirementへ昇格させない。

## Non-goals / 未検証範囲

- SEI CIからTEI private repositoryを自動cloneすること
- GitHub PAT等のcredential方式を標準化すること
- TEI binary distributionを新設すること
- build manifestの署名方式を決めること
- manifest authenticityを検証すること
- actual TEI binaryをこのIssueのhelper testだけで実行済みとみなすこと
- E3b-P2の成立をこのIssueだけで宣言すること
- E3b-M1 external Cognitive Method live execution
- E4 Operational portability
- Product Release / Release Evidence
- Adoption / Outcome Evidence

## 完了条件

- [ ] `runtime/go/teiprobe`を実装する。
- [ ] `tei-e3b-probe` commandを実装する。
- [ ] binary SHA-256とsource declarationをderived reportへ記録する。
- [ ] manifestなし / 一致 / 不一致をtestへ落とす。
- [ ] process failure / timeout時にPASS reportを生成しないことをtestする。
- [ ] reportにcredential fieldを持たせない。
- [ ] current runtime regressionを含むCIをsuccessさせる。
- [ ] Evidence protocol文書を自然な日本語で整備する。
- [ ] Product Milestone / Realization Provider Exchange / upstream planへ境界を同期する。
- [ ] plan registry / document review registryを同期する。
- [ ] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。

## Evidence state

起票時点（2026-09-02）の記載を、current `develop/v0.2.0`で成立している事実へ同期する。

- E3b-P1 public live Provider service: **Scoped Executable Evidence available**
- external TEI executable injection boundary: **Scoped Executable Evidence available with helper subprocess**
- actual TEI Evidence collection protocol: **Not Yet Verified**
- E3b-P2 actual TEI CLI execution: **Scoped Executable Evidence available（ISSUE-000065 / revision A fixed-artifact）**
- TEI executable version交換後のProvider Observation境界: **Not Yet Verified（ISSUE-000072 Open）**
- source-to-binary authenticity: **Not Yet Verified**
- E3b-M1a live external Cognitive Method execution: **Scoped Executable Evidence available（ISSUE-000064）**
- E3b-M1b actual model-backed Cognitive Method execution: **Scoped Executable Evidence available（ISSUE-000066）**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence: **available（ISSUE-000063 / v0.2.0、supported scopeはE3aまで）**
- Adoption / Outcome Evidence: **Not Yet Verified**

ISSUE-000065はrevision Aのfixed-artifactについてactual binary SHA-256とProvider Plan SHA-256を個別のEvidence文書へ記録したが、`runtime/go/teiprobe` / `tei-e3b-probe` / `sei.e3b-tei-probe/v1`として再利用可能なEvidence採取プロトコルと、build manifestによるsource-to-binary bindingは実装していない。本Issueが未完了として残るのはこの範囲である。

## Reopen / escalation条件

- actual TEI実行時にbinary SHA-256だけでは実行identityを十分に区別できない。
- TEI側のbuild provenanceが成立し、current manifest modelでは意味を失う。
- source declarationとbinary bindingをUniversal semanticsへ持ち込まないとProduct failureを防げないことが判明する。
- actual E3b-P2で、今回のEvidence reportでは再現・監査に必要な情報が不足する。

## Natural Japanese review

PMS-06、ISSUE-000060 / 000061、current Capability Observation Contract、Provider Adapter、`runtime/go/teiintegration`、`hat47x/tei-platform`のGo CLI・reference artifacts・CI構成を照合した。TEIには実行可能なCLI sourceがある一方、現時点ではSEIがそのまま利用できるbinary配布artifactがなく、private repositoryの取得方式をSEI側へ暗黙に持ち込むべきでもない。そのため、取得方式そのものを先に固定せず、実際に供給されたbinary bytesのSHA-256とsource declaration、任意manifestとの一致状態をderived Evidenceとして記録する境界を先に定めた。`manifest_matched`もmanifest真正性の検証とは区別し、Evidenceの高さを過大評価していない。意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。