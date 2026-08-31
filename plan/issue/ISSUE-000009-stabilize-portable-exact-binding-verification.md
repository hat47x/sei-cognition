# ISSUE-000009: Portable Exact BindingのRepresentation Profileを安定化する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009**  
Updated: 2026-08-31

## Goal

Portable Exact Bindingを、Go固有の実装やSOZA独自canonicalizationだけに依存せず、複数言語・複数representationで検証可能な仕組みへ安定化する。

本Issueでは、**current/future bindingに使用するRepresentation Profile**を対象とする。

historical M47 digestの規則回収はISSUE-000032へ分離した。historical Profileが未確認でも、ADR-0009に従って`not_verified`として保持できるため、current Profile安定化を停止しない。

## Already established

Phase 1 candidateとcurrent Contract baselineで、次はすでに確認・決定済みである。

- Exact Bindingはlogical identityと特定contentを結び付ける。
- canonicalization / digest algorithmはUniversal CoreではなくRepresentation Profileが所有する。
- `verified / failed / not_verified`を分離する。
- unknown Representation Profileを`verified`扱いしない。
- representation-only changeをSemantic Lineageへ自動変換しない。
- custom canonical JSON v1alpha1は実験Evidenceであり、stable defaultへ自動昇格しない。
- Go / Python独立実装によるcross-language pressure testはhistorical candidateで実施済みだが、current Executable Evidenceへは自動継承しない。

## 2026-08-31 current research

### RFC 8785 JCS

stable JSON Profileの第一候補はRFC 8785 JSON Canonicalization Schemeとする。

採用候補とする理由:

- canonical JSON規則をSOZA独自標準として所有しなくてよい。
- JSON primitive serialization、recursive object property sorting、UTF-8出力の相互運用規則が外部仕様として定義されている。
- cryptographic hash / signature用途を目的としている。
- 複数言語の公開実装・test vectorが存在する。

ただしRFC 8785はI-JSONを前提とし、JSON numberをIEEE 754 binary64で表現できることを要求する。

したがって、SOZA Profileでは次を重要な境界とする。

```text
high-precision semantic value
  != silently rounded JSON number
```

高精度整数・decimal等をbinary64へ暗黙丸めしてdigestを生成してはならない。必要な場合は型付き文字列等、値を失わないrepresentationへ明示的に投影する。

また、JCSはUnicode normalizationを行わないため、文字列のUnicode sequenceを「意味的に同じ」と推測して正規化しない。

### Go verifier candidates

#### `cyberphone/json-canonicalization`

- RFC作者側のreference repository。
- Apache License 2.0。
- Go実装とtestdataを含む。
- repository全体の最新確認commitは2024-12-13。
- Go版はhistorical GOPATH-styleの利用手順を持ち、現代的な直接module dependencyとしては扱いにくい。

#### `gowebpki/jcs`

- `github.com/gowebpki/jcs`としてGo module化されている。
- Apache License 2.0。
- RFC作者側Go実装を整理したforkであることをREADMEが明示している。
- `jcs.go`、number serialization test、testdataを持つ。
- 現在確認できる最新commitは2023-10-15。

更新頻度だけを見ると活発とは言いにくい。

しかしJCS自体は安定したRFCであり、SOZAでは「頻繁に更新されるlibrary」を必須条件にせず、次の組合せを優先する。

```text
RFC 8785をProfileの正本
  + dependency commitを固定
  + SOZA側でRFC / adversarial test vectorを保持
  + verifier adapterを交換可能にする
```

現時点では`gowebpki/jcs`を**Go probeの第一候補**とするが、Profile DefinitionをこのlibraryのAPIや制約へ従属させない。

## Scope split

### This Issue — current/future Profile

1. JCS + SHA-256 Profile Definitionを作る。
2. RFC test vectorとSOZA固有adversarial fixtureをcurrent repositoryへ置く。
3. Go verifier candidateをcommit固定でprobeする。
4. high-precision boundaryをnegative fixtureで確認する。
5. Unicode non-normalization、duplicate key、number serialization境界を確認する。
6. `verified / failed / not_verified`をcurrent Contract checkerへ接続する。
7. non-JSON向けraw-bytes + SHA-256 Profileの必要最小限を定義する。

### ISSUE-000032 — historical mapping

- historical M47 digest bytes / canonicalization / hash規則の回収
- historical bindingのProfile対応付け
- 回収不能時のclosure

historical M47をJCSへ遡及変換しない。

## Candidate stable JSON Profile

Profile identity候補:

```text
soza.jcs+sha256/v1alpha1
```

Profile Definitionが所有する予定の規則:

1. inputはRFC 8785 / I-JSON制約を満たすJSON representationである。
2. RFC 8785に従ってcanonical UTF-8 bytesを生成する。
3. canonical bytesへSHA-256を適用する。
4. digest textは`sha256:<64 lowercase hex>`とする。
5. duplicate property nameはinvalid inputとする。
6. non-finite numberはinvalid inputとする。
7. binary64で値を保持できないsemantic numberを暗黙丸めしてはならない。
8. Unicode normalizationを行わない。
9. Profile ID / versionがunknownな場合は検証済みと扱わない。

この一覧はProfile DefinitionとExecutable probeの照合後に確定する。

## Candidate raw-bytes Profile

non-JSON / large binary向けには、次を別Profileとする方向で検討する。

```text
soza.raw-bytes+sha256/v1alpha1
```

このProfileは「semantic valueをJSONへ変換してhashする」ものではなく、明示されたbytesそのものを対象にする。

```text
raw bytes identity != semantic JSON identity
```

content-type、bytes acquisition、external source retention等の条件をProfileまたは上位Policyで明示する。

## Acceptance

### Design Acceptance

- [ ] JCS Profile Definitionがactual repositoryに存在する。
- [ ] Profileの正本がRFC / Profile Definitionであり、特定Go libraryではない。
- [ ] high-precision valueの暗黙丸め禁止が明示されている。
- [ ] Unicode normalizationを行わないことが明示されている。
- [ ] raw-bytes Profileとの意味差が明示されている。

### Executable Acceptance

- [ ] RFC 8785 representative vectorがPASSする。
- [ ] key order / whitespace差で同じcanonical resultになる。
- [ ] RFC number serialization representative vectorがPASSする。
- [ ] duplicate keyを拒否する。
- [ ] high-precision valueを暗黙丸めする入力を安全に拒否・分離できる。
- [ ] Unicode normalizationを勝手に行わない。
- [ ] Go verifier candidateをcommit固定でactual GitHub Actionsから実行できる。
- [ ] dependencyを差し替えてもProfile identity / Contract意味が変わらないadapter境界を維持する。
- [ ] raw-bytes Profileの代表fixtureが再現できる。

### Evidence boundary

本IssueをResolvedにしても、次を意味しない。

- historical M47 digest mapping完了 — ISSUE-000032
- Production Runtime integration完了
- Release Evidence成立
- Operational Evidence成立

## Resolution condition

current/future Exact Bindingについて、少なくともJCS + SHA-256とraw-bytes + SHA-256のProfile Definition、test vector、independent verifier pathがactual repositoryで再現できること。

historical M47 mappingはResolution条件から外し、ISSUE-000032で独立してclosureする。

## Dependencies / Follow-up

- ADR-0007 — storage-neutral persistence
- ADR-0008 — Exact Binding verification boundary
- ADR-0009 — verification outcome separation
- ISSUE-000031 — Contract fixture-scoped conformance（Resolved）
- ISSUE-000032 — historical M47 digest recovery

## Natural Japanese review

historical M47 mappingとcurrent/future Profile安定化を分離し、RFC 8785、Go verifier候補、high-precision境界、raw-bytes境界を再整理した。その後、まだprobe前の事項を確定済みと誤読させないようEvidence強度を調整し、意味と留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
