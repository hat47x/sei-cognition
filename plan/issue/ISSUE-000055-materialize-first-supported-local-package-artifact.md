# ISSUE-000055: first supported Local Package artifactを実体化する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0027, ADR-0029**  
Updated: 2026-09-01

## Goal

PMS-04で残っている、**build可能なprobe executableと、利用者へ渡せるsupported distributable artifactの差**を埋める。

Local Single-Node Packageについて、再現可能なbuild、artifact identity、version表示、明示的なdata root、配布物からの起動・保存・再開を、最小構成で検査する。

ここで扱うpackage lifecycle用の管理入口を、PMS-03で未決のhuman-facing / AI-facing Product Interaction Surfaceと混同しない。

```text
package lifecycle control surface
  != Product Interaction semantic surface
```

## 背景

ISSUE-000054では、`soza-package-probe`をtest内で実際にbuildし、独立したsave processを終了した後、別のinspect processがdurable data rootだけからbundleを再構成できることを確認した。

これによりliteral process restartのscoped Executable Evidenceは得られたが、次はまだ未成立である。

- repository testから独立して生成される配布artifact
- artifact自身のversion / build identity
- artifact layoutとdata rootの明示
- 配布artifactを使ったsave → exit → reloadの再現可能なacceptance
- artifact integrityを検査する最低限のmetadata

## Open Questions

- 最初のartifactを単一OS / architectureへ限定してよいか。
- archive形式をzip / tar.gz等のどれにするか。
- checksumをRelease Evidence以前のExecutable Evidenceとしてどこまで持つか。
- lifecycle command名をどこまで固定するか。
- `soza`本体名称をこの段階で使うか、reference package名を分離するか。
- version stringへsemantic contract versionを埋め込むべきか、product build versionと分離すべきか。

これらは現時点でUniversal Requirementへ昇格させない。

## 初期方針

### artifactの意味

artifactはfirst-party Go runtimeの一つの配布Realizationである。

```text
distribution artifact
  != canonical semantic data
  != Semantic Contract identity
  != Product Release itself
```

### lifecycle control

最初のartifactには、packaging acceptanceを検査するための最小管理操作だけを置く。

候補は次とする。

- portable Semantic Interchangeをdata rootへ取り込む。
- data rootからbundleを読み、semantic runtimeが再構成できることを確認する。
- build / version identityを表示する。

これらを利用者の判断仕事を行う正式CLIとして扱わない。

### artifact Evidence

CIでartifactをbuildし、別stepまたは別jobでそのartifact自体を使ってsave → exit → reloadを検査する。

source treeから`go run`するだけではsupported artifact Evidenceとはしない。

## Requirement / Scenario監査

現時点では新しいstable Requirement / Scenarioを追加しない。

主に次を利用する。

- REQ-0001 — 実装が変わっても意味を引き継ぐ。
- REQ-0018 — Storage実装から意味を独立させる。
- REQ-0020 — Evidenceを超える達成主張をしない。
- REQ-0021 — Realizationを交換可能にする。
- PMS-04 — 配布・保存・再開が可能な最小製品単位。

artifact化の過程で、既存Requirementでは表現できない独立したfailureが確認された場合だけCandidate Requirement / Scenarioを再検討する。

## Non-goals

- production Product Interaction UI / CLIの最終決定
- team / multi-user package
- container / Kubernetes標準化
- production RDB選定
- production installer
- auto-update
- code signingのproduction policy確定
- cross-platform support matrixの全面確定
- Release Evidenceの成立
- Operational / Adoption / Outcome Evidence

## 完了条件

- [ ] first distributable artifactのscopeを決める。
- [ ] artifactをCIで再現可能にbuildする。
- [ ] artifactへbuild / version identityを持たせる。
- [ ] artifactとdurable data rootを分離する。
- [ ] build済みartifactそのものを使ってsave → process exit → reloadを検査する。
- [ ] artifact再生成後も同じsupported semantic dataを読めることを検査する。
- [ ] artifact integrityに必要な最低限のmetadataを整理する。
- [ ] Product Interaction Surfaceとの境界を再監査する。
- [ ] Requirement / Scenario追加の要否を再監査する。
- [ ] Evidence文書へ結果を同期する。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Satisfied for work definition**
- Executable Evidence: **Not Yet Verified as a supported distribution artifact**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- artifactを成立させるためにProduct Interactionの特定Surfaceを先に固定する必要が生じた。
- artifact identityとSemantic Contract identityを分離できない設計上の問題が確認された。
- supported artifactからdurable semantic dataを再読できない。
- executable rebuild / version changeでsemantic continuityを保持できない。

## Natural Japanese review

PMS-04、Product Packaging baseline、ADR-0027 / 0029、ISSUE-000054のliteral process restart probeを照合し、次の未解決点を「test内でbuildできること」と「supportedな配布artifactとして成立すること」の差として切り出した。package lifecycle controlとProduct Interaction Surface、artifact identityとsemantic identity、Executable EvidenceとRelease Evidenceを混同しないよう境界を整理している。そのうえで、未決事項を先に固定せず、意味、要求強度、Evidence強度を保ったまま、自然な日本語となることを最重要視して全文をドラフトし、最終意味監査を実施済みである。