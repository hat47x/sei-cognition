# Actual TEI Evidence 採取プロトコル

更新日: 2026-09-18  
状態: **Current Design / Implementation Baseline — actual TEI runは未検証**

## 1. この文書の役割

この文書は、ISSUE-000074で追加した `runtime/go/teiprobe` と `runtime/go/cmd/tei-e3b-probe` を使い、外部から与えられたTEI executableについて、**何を実行したか、declared sourceとbinaryの関係をどこまで確認したか、実行後にどのCapability Observationが得られたか**をderived Evidenceとして記録する方法を定めます。

ここで生成する `sei.e3b-tei-probe/v1` はSEIのUniversal Contractではありません。E3b-P2のactual TEI実行を監査するためのprobe artifactです。

```text
actual executable bytes
  + declared source repository / commit
  + optional build manifest
  + actual deployment-provider-plan execution
  + current Capability Observation validation
        ↓
derived Evidence report
```

reportが生成できたことだけでTEIの任意version互換性、manifest真正性、production integration、Operational Evidence、Product Valueを主張しません。

## 2. 既存境界との関係

Provider PlanのdecodeとSEI Capability Observationへのmappingは既存 `runtime/go/teiintegration` を正とします。

`teiprobe`は次を再実装しません。

- TEI Provider Plan fieldの意味解釈
- Capability Observation mapping
- current Capability Observation validation
- credential取得
- private repository clone
- TEI binary build / distribution

追加する責務は次だけです。

1. direct executable fileのidentityをSHA-256で観測する。
2. declared source repository / commitをEvidenceへ保持する。
3. optional manifestがある場合だけsource-to-binary bindingを照合する。
4. executableを既存`teiintegration`で実行する。
5. 実行後に同じfileを再hashし、probe中にbytesが変化していないことを確認する。
6. success時だけderived Evidence reportを生成する。

## 3. direct binary境界

`--binary`は、実際に起動するregular fileを直接指します。

symlinkは受理しません。wrapper commandやPrefixArgsをprobe側へ持ち込みません。

```text
direct executable file
  → hash
  → execute same path
  → hash again
  → pre/post digest equality required
```

これはadversarial filesystemに対する暗号学的なTOCTOU排除を意味しません。ただし、単にfilenameやdeclared digestだけを保存するより、probe開始時と終了時のactual file bytesが同一だったことをfail closedに確認します。

## 4. source declarationとmanifest

source repository / commitは必須の**declaration**です。

```text
declared repository / commit
  != observed Git checkout
  != signed provenance
```

manifestは任意です。current schemaは次です。

```json
{
  "schema": "sei.tei-binary-build-manifest/v1",
  "repository": "hat47x/tei-platform",
  "commit": "<declared source commit>",
  "binary_sha256": "<64 hex chars>"
}
```

manifestはstrict JSONとして読みます。unknown field、malformed JSON、複数JSON値は拒否します。

manifestを与えない場合:

```text
source_binding = not_verified
```

manifestを与え、repository / commit / observed binary SHA-256がすべて一致した場合だけ:

```text
source_binding = manifest_matched
```

`manifest_matched`はmanifest authenticity、署名、build provenance、reproducible buildを証明しません。

## 5. command

基本形は次です。

```bash
go run ./cmd/tei-e3b-probe \
  --binary /path/to/tei \
  --source-repository hat47x/tei-platform \
  --source-commit <commit> \
  --workspace /path/to/workspace \
  --run /path/to/run.json \
  --solution <solution-id> \
  --version <solution-version> \
  --plugin-lock /path/to/plugin-lock.json \
  --observation-id <observation-id> \
  --capability-id deployment-provider-routing \
  --observed-at <RFC3339 timestamp> \
  --source-state-ref <non-secret source state ref>
```

manifestを使う場合は `--manifest /path/to/manifest.json` を追加します。

`--timeout`はTEI processの上限時間です。timeout、process failure、Provider Plan decode failure、Capability Observation validation failure、manifest mismatch、実行中digest変化ではPASS reportを生成しません。

## 6. report

success時のreportには少なくとも次を含みます。

- schema = `sei.e3b-tei-probe/v1`
- result = `pass`
- observed binary SHA-256
- binary digest stability = `pre_post_matched`
- declared source repository / commit
- source binding
- manifest supplied / not supplied
- solution / version
- current Capability Observation

credential、password、API key、access tokenをreport schemaへ追加しません。

ただし、呼び出し側が `source-state-ref` 等の自由入力へsecretを埋め込まない責任までprobeが自動的に代替するわけではありません。Evidenceへ渡すProvenance文字列は非secretである必要があります。

## 7. failure boundary

次を区別します。

```text
binary acquisition failure
  != binary identity mismatch
  != manifest mismatch
  != TEI process failure
  != TEI timeout
  != Provider Plan decode failure
  != Capability Observation validation failure
```

current `Probe` APIはfailure時にPASS reportを返しません。途中まで得られたObservationやpartial reportを成功Evidenceとして残しません。

`teiintegration`はprocess failureの診断性を保つため、上限付きで取得したTEI subprocessのstderrを返却errorへ含める場合があります。このerror textは**local diagnostic**であり、`sei.e3b-tei-probe/v1`のderived Evidence reportではありません。失敗時のstderrをそのまま通常Evidenceやrepository保存artifactへ転記しません。failure observationを保存する必要がある場合は、ISSUE-000076のsecret-safe Evidence boundaryで、credential・token・secret等を含まない最小限の分類と事実へ落としてから記録します。

```text
successful derived report
  != local failure diagnostic

bounded subprocess stderr
  = local diagnosis input
  != repository-safe Evidence by itself
```

failureの詳細な分類・retry設計はISSUE-000076のfailure-behavior Evidenceと混同しません。ISSUE-000074の主眼は、actual TEI success Evidenceのidentity / binding / mappingを監査可能にすることです。

## 8. test Evidenceの高さ

`runtime/go/teiprobe/probe_test.go`では、POSIX shell fixtureをdirect executableとして使用し、次を検査する設計です。

- manifestなし → `not_verified`
- manifest一致 → `manifest_matched`
- repository / commit / digest不一致 → reject
- unknown manifest field / multiple JSON → reject
- symlink executable → reject
- process failure → PASS reportなし
- timeout → PASS reportなし
- probe中のexecutable digest変化 → reject
- report schemaへcredential fieldを追加しない
- success時のCapability Observationがcurrent validatorを通る

これらのfixtureはactual TEIではありません。

```text
helper / shell fixture test PASS
  != actual TEI execution Evidence
```

また、2026-09-18時点ではrepositoryのGo moduleはGo 1.25を要求し、この作業環境ではcurrent testをactual実行できていません。したがってtest sourceの追加をExecutable Evidence PASSとは扱いません。

## 9. actual Evidenceとして受理する条件

actual TEI Evidenceとして扱うには、少なくとも次を満たします。

1. actual TEI binaryをdirect fileとして供給する。
2. binary SHA-256をprobe自身が観測する。
3. declared source repository / commitを明示する。
4. manifestを使う場合はstrict matchする。
5. actual `deployment-provider-plan`が成功する。
6. current `teiintegration` mappingが成功する。
7. current Capability Observation validatorが成功する。
8. executable pre/post digestが一致する。
9. reportをactual runのEvidence artifactとして保存する。
10. fixtureやhelper subprocessの結果をactual runへ流用しない。

## 10. Evidence停止線

```text
teiprobe implementation available
  != teiprobe tests executed

teiprobe tests PASS
  != actual TEI binary executed

actual TEI report PASS
  != arbitrary TEI version compatibility
  != manifest authenticity
  != source reproducibility
  != Operational portability
  != Product Value / Adoption outcome
```

ISSUE-000072のrevision B version exchangeでは、このprotocolを利用できても、exact-B actual executionとcurrent Adapter compatibilityを別途確認する必要があります。

## 11. Natural Japanese review

本protocolは、取得方式やcredential方式をTEI / SEIの恒久的な意味へ昇格させず、実際に与えられたbinary bytes、declared source、任意manifest、actual Provider Plan実行、current Capability Observationを一つの監査可能なEvidenceへ束ねるためのものです。

特に、`manifest_matched`を署名付きprovenanceと誤読しないこと、helper fixtureをactual TEI Evidenceへ昇格させないこと、failure時にpartial PASS reportを作らないこと、Provider Planの意味mappingを`teiintegration`と二重実装しないことを停止線として維持します。
