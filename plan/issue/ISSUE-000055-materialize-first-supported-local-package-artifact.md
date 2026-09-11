# ISSUE-000055: first Local Reference Package artifactを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0027, ADR-0029**  
Updated: 2026-09-01

## Goal

PMS-04で残っていた、**test内でbuildできるexecutableと、明示的なdistribution artifactとして生成・展開・再利用できるpackageの差**を埋める。

Local Single-Node Packageについて、再生成可能なbuild、artifact identity、version表示、durable data rootとの分離、archiveからの起動・保存・再開を最小構成で検証する。

package lifecycle用の管理入口は、PMS-03で未決のhuman-facing / AI-facing Product Interaction Surfaceと混同しない。

```text
package lifecycle control surface
  != Product Interaction semantic surface
```

## Resolution

最初の配布実証を**Local Reference Package**として実体化した。

current reference distribution profileは次に限定する。

- target: `linux-amd64`
- artifact version: `0.2.0-reference`
- archive: `soza-local-reference-linux-amd64.tar.gz`
- checksum: `soza-local-reference-linux-amd64.tar.gz.sha256`
- executable name: `soza-local-reference`
- artifact format metadata: `soza.local-reference/v1`

これはPMS-04のMinimum Executable Evidenceを得るためのreference profileであり、Product Releaseや恒久的platform supportを意味しない。

```text
reference distribution artifact
  != canonical semantic data
  != Semantic Contract identity
  != Product Release
```

## build identity

probe executableへ`version`操作を追加し、build時に次を埋め込めるようにした。

- artifact version
- source commit
- target

artifact内の`build-metadata.json`にも同じidentityを記録する。

artifact identityはsemantic identityではない。archive名、build version、commit、targetをLogical ReferenceやSemantic Contract versionとして利用しない。

## reproducible build probe

Local Package Artifact workflowでは、同じsource checkout、Go version、target、ldflagsからbinaryを2回buildし、`cmp`でbyte-for-byte一致を検査する。

buildには`-buildvcs=false`と`-trimpath`を用いる。

このPASSが示すのは、current CI環境と同一input内での再生成性である。異なるtoolchainや将来時点を跨いだbit-for-bit reproducibilityまで主張しない。

## archive / integrity

archive作成ではfile順、mtime、owner / groupを固定し、gzip timestampを付与しない。

archiveにはSHA-256 checksum fileを付ける。さらにGitHub Actionsのworkflow artifactにもplatform側digestが付与される。

Run `33509521544`で保存されたartifactは次のとおり。

- name: `soza-local-reference-linux-amd64`
- artifact ID: `9801021136`
- size: `993955` bytes
- workflow artifact digest: `sha256:6282a2fe0b58dd023090d363e3323ce963a9f29c097f869ebab79b73aab2ba85`
- expires: 2026-09-15T12:46:44Z

retention期限はcurrent CI Evidenceの保存期間であり、正式Release retention policyではない。

## artifact acceptance

workflowではsource tree内のbinaryだけでacceptanceを完了させない。

生成したtar.gzを別directoryへ展開し、展開物に含まれる`soza-local-reference`を独立したprocessとして起動する。

```text
extracted artifact process A
  -> save portable Semantic Interchange
  -> exit

extracted artifact process B
  -> same durable data root
  -> inspect / reconstruct
```

`partial-knowledge-interchange.json`について、process Bが次を再構成することを確認した。

- `bundle_id = partial-knowledge-interchange`
- `record_count = 2`
- `validated_count = 2`
- `not_verified_count = 0`

これにより、archiveから展開したbuild済みartifactを使うsave → process exit → reloadにscoped Executable Evidenceが得られた。

## lifecycle controlとProduct Interaction

reference executableの`version` / `save` / `inspect`はPackaging acceptance用の管理入口である。

これらをInquiry、Observation、Recommendation、Decision等を扱う正式なSEI CLIへ昇格させない。

`runtime/package/reference/README.md`でもこの境界を明示した。

## Requirement / Scenario再監査

artifact化によって、新しいstable Product RequirementやAcceptance Scenarioを必要とする独立したfailureは確認されなかった。

引き続き主に次を利用する。

- REQ-0001 — 実装が変わっても意味を引き継ぐ。
- REQ-0018 — Storage実装から意味を独立させる。
- REQ-0020 — Evidenceを超える達成主張をしない。
- REQ-0021 — Realizationを交換可能にする。
- PMS-04 — 配布・保存・再開が可能な最小製品単位。

archive形式、target、checksum、lifecycle command等はreference distribution profileのRealizationであり、Universal Requirementではない。

## 完了条件

- [x] first reference distribution artifactのscopeを定める。
- [x] artifactをCIで再生成可能にbuildする。
- [x] artifactへbuild / version identityを持たせる。
- [x] artifactとdurable data rootを分離する。
- [x] build済みarchiveを展開し、そのartifact自身でsave → process exit → reloadを検査する。
- [x] 同一CI inputからbinaryを2回buildし、byte-for-byte一致を検査する。
- [x] archive checksumとworkflow artifact digestを取得する。
- [x] Product Interaction Surfaceとの境界を再監査する。
- [x] Requirement / Scenario追加の要否を再監査する。今回は追加しない。
- [x] Evidence文書へ結果を同期する。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [x] 対象CIをsuccessさせる。

## CI Evidence

head `36cf83d72ec5386df56193002eef4dce00536db4`で次が**success**した。

### Local Package Artifact Run `33509521544`

- Build reference binary twice
- Add reference package metadata
- Verify build identity
- Create deterministic archive and checksum
- Verify extracted artifact across independent processes
- Upload reference distribution artifact

すべてsuccess。

### 関連CI

- Plan integrity Run `33509521580` — success
- Semantic Runtime Conformance Run `33509521596` — success

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Scoped Evidence available for Local Reference Package**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

詳細は`runtime/LOCAL_PACKAGE_ARTIFACT_EVIDENCE_2026-09-01.md`を正とする。

## PMS-04への反映

Local Reference Packageによって、PMS-04のMinimum EvidenceであるPackaging / Deployment Designと最小packageのExecutable Evidenceが揃った。

したがってPMS-04は、**Design baseline established / Minimum scoped Executable Evidence available**と扱える。

これはPMS-07のRelease Evidenceや正式support matrixを意味しない。

## 未検証範囲

- Product Release artifact
- Windows / macOS等のdistribution
- cross-toolchain / cross-time reproducibility
- code signing
- installer / package manager / auto-update
- executable version upgrade後のresume
- production Product Interaction Surface
- production security / credential management
- actual production Storage migration
- Operational / Adoption / Outcome Evidence

## Reopen / escalation条件

- reference artifactからdurable semantic dataを再読できない変更が入る。
- artifact identityとSemantic Contract identityが混同される。
- Product Interactionを成立させるためにcurrent package lifecycle commandをsemantic authorityへ昇格させる必要が生じる。
- executable version upgradeでsupported semantic dataを引き継げない。
- Release artifactへ進む際にcurrent Packaging boundaryでは成立しない独立したfailureが確認される。

## Natural Japanese review

PMS-04、Product Packaging baseline、ADR-0027 / 0029、ISSUE-000054、Local Package Artifact workflow、reference package README、Run `33509521544`とartifact metadataを照合した。test内のbinaryと配布archive、package lifecycle controlとProduct Interaction、artifact identityとsemantic identity、Executable EvidenceとRelease Evidenceを分けている。Linux / amd64、tar.gz、checksum等はcurrent reference profileのRealizationとして扱い、恒久的support matrixへ昇格させていない。そのうえで、意味、要求強度、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。