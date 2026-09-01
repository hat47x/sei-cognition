# Local Reference Package Artifact Evidence

更新日: 2026-09-01  
状態: **Scoped Executable Evidence**

## 1. この文書の役割

この文書は、ISSUE-000055で作成したSOZA Local Reference Packageについて、**source tree内でbuildできることではなく、CIが明示的な配布archiveを生成し、そのarchiveから実際に起動・保存・再開できること**を記録します。

これはProduct ReleaseのEvidenceではありません。

```text
reference distribution artifact PASS
  != Product Release
  != production support matrix
  != production installer
  != Operational / Adoption Evidence
```

## 2. artifact scope

current reference artifactは次に限定します。

- target: `linux-amd64`
- artifact version: `0.2.0-reference`
- archive: `soza-local-reference-linux-amd64.tar.gz`
- checksum file: `soza-local-reference-linux-amd64.tar.gz.sha256`
- executable: `soza-local-reference`
- artifact format metadata: `soza.local-reference/v1`

このscopeはExecutable Evidenceを得るためのreference distribution profileです。SOZAの恒久的なplatform supportや正式Release formatを決めるものではありません。

## 3. artifactとsemantic identityの分離

binaryにはbuild version、commit、targetを埋め込み、`version`操作からJSONで取得できます。

一方、artifact versionやarchive名をSemantic Contract identity、Logical Reference、Decision identity等へ転用しません。

```text
artifact identity
  != semantic identity
  != Semantic Contract version
```

artifactを再buildしても、canonical semantic dataはdurable data root側に残る構造を維持します。

## 4. package lifecycle control

reference executableが持つ`version` / `save` / `inspect`はPackaging acceptance用の管理入口です。

これらを、利用者がInquiry、Recommendation、Decision等の判断仕事を行う正式なProduct Interaction CLIとは扱いません。

```text
package lifecycle control
  != Product Interaction Surface
```

正式なhuman-facing / AI-facing SurfaceはPMS-03側のOpen Questionのままです。

## 5. build reproducibility probe

Local Package Artifact workflowでは、同じcheckout、Go version、target、ldflagsを用いてbinaryを2回buildし、byte-for-byte一致を`cmp`で検査します。

buildでは`-buildvcs=false`、`-trimpath`を利用し、current reference profileに必要なbuild identityだけを明示的に埋め込みます。

このPASSは、**同一CI環境・同一inputでのbinary再生成性**についてのEvidenceです。異なるGo toolchain、OS、将来時点を跨いだbit-for-bit reproducibilityまで証明するものではありません。

## 6. archiveとintegrity metadata

archiveはfile順、mtime、owner / groupを固定して作成し、gzip timestampも付与しない形で生成します。

archiveとあわせてSHA-256 checksum fileを生成します。

GitHub Actionsへuploadされたworkflow artifactにもplatform側のdigestが付与されています。

Run `33509521544`で保存されたartifact:

- artifact name: `soza-local-reference-linux-amd64`
- artifact ID: `9801021136`
- size: `993955` bytes
- workflow artifact digest: `sha256:6282a2fe0b58dd023090d363e3323ce963a9f29c097f869ebab79b73aab2ba85`
- expires: 2026-09-15T12:46:44Z

workflow artifactのretentionはEvidence保存期間の一つであり、正式Release retention policyではありません。

## 7. extracted artifactからの再開

workflowではsource tree上のbinaryを直接実行してacceptanceを済ませません。

生成したtar.gzを別directoryへ展開し、展開物に含まれる`soza-local-reference`を使って次を実行します。

```text
extracted artifact process A
  -> save Semantic Interchange
  -> exit

extracted artifact process B
  -> same durable data root
  -> inspect / reconstruct
```

`partial-knowledge-interchange.json`について、process Bが次を再構成することを確認しました。

- `bundle_id = partial-knowledge-interchange`
- `record_count = 2`
- `validated_count = 2`
- `not_verified_count = 0`

これにより、**配布archiveから展開したbuild済みartifactを用いたsave → process exit → reload**にscoped Executable Evidenceがあります。

## 8. build identity verification

archiveへ入れる前のbinaryについて、`version`出力がworkflowで指定したversion、commit、targetと一致することを検査しています。

`build-metadata.json`にも同じartifact identityを記録します。

binary内identityとmetadataが存在することは、semantic dataがそのbuildへ従属することを意味しません。

## 9. CI Evidence

head `36cf83d72ec5386df56193002eef4dce00536db4`で次が**success**しました。

### Local Package Artifact Run `33509521544`

- Build reference binary twice — success
- Add reference package metadata — success
- Verify build identity — success
- Create deterministic archive and checksum — success
- Verify extracted artifact across independent processes — success
- Upload reference distribution artifact — success

### 同一headの関連CI

- Plan integrity Run `33509521580` — success
- Semantic Runtime Conformance Run `33509521596` — success

## 10. PMS-04への意味

PMS-04が要求する「配布・保存・再開が可能な最小製品単位」について、reference distribution profileに限ればMinimum Evidenceを満たすscoped Executable Evidenceが得られました。

```text
Packaging Design: established
literal process restart: scoped Executable Evidence available
reference distribution archive: scoped Executable Evidence available
archive extraction -> save -> exit -> reload: scoped Executable Evidence available
Product Release: not yet verified
production support matrix: not yet verified
```

したがってPMS-04は、**Design baseline established / Minimum scoped Executable Evidence available**と扱えます。

これはPMS-07のRelease Evidenceを先取りしません。

## 11. Requirement / Scenario再監査

artifact化によって、新しいstable Product RequirementまたはAcceptance Scenarioを必要とする独立したfailureは確認されませんでした。

引き続きREQ-0001 / 0018 / 0020 / 0021とPMS-04を主な検査軸とします。archive形式、target、checksum、lifecycle command等はcurrent reference distribution profileのRealizationです。

## 12. 未検証範囲

- production Release artifact
- Windows / macOS等のreference distribution
- cross-toolchain reproducibility
- code signing
- installer / package manager
- auto-update
- executable version upgrade後のresume
- production Product Interaction Surface
- production security / credential management
- actual production Storage migration
- Operational / Adoption / Outcome Evidence

## 13. Natural Japanese review

PMS-04、Product Packaging baseline、ADR-0027 / 0029、ISSUE-000054 / 000055、Packaging probe、Local Package Artifact workflow、Run `33509521544`とworkflow artifact metadataを照合しました。source tree内のbuildと配布archive、package lifecycle controlとProduct Interaction、artifact identityとsemantic identity、Executable EvidenceとRelease Evidenceを分離しています。reference artifactの成功を正式support matrix、version upgrade互換性、production security、Operational / Adoption Evidenceへ広げないまま、意味、Evidence強度、未検証範囲を保ち、自然な日本語となることを最重要視して全文をドラフトし、最終意味監査を実施済みです。