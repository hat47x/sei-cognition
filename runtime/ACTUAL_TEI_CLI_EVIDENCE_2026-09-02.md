# Actual TEI CLI Evidence — 2026-09-02

## 1. この文書の位置づけ

この文書は、PMS-06 / E3b-P2について、固定revisionの実TEI CLIを実際にbuild・起動し、その`deployment-provider-plan`出力をSOZAのcurrent Provider Adapter境界へ戻した後続Evidenceを記録するものです。

先行する`runtime/ACTUAL_TEI_INTEGRATION_PROBE_EVIDENCE_2026-09-02.md`では、SOZA Actionsからprivate TEI repositoryを取得する資格情報が利用できず、actual TEI stepがskipされました。その事実は変更しません。

今回のEvidenceは、先行probeを書き換えるのではなく、**別の取得・実行経路でactual TEI executionまで到達した後続記録**として扱います。

```text
先行credential-aware probe
  actual TEI step skipped
        +
後続fixed-artifact execution
  actual TEI CLI build / execution succeeded
        =
E3b-P2 fixed-artifact scopeのScoped Executable Evidence
```

ただし、この成立をcross-repository credential運用、任意TEI versionとの互換性、production integration、Operational Evidenceへ拡張しません。

## 2. 固定したTEI source

今回の実証ではTEI sourceを次へ固定しました。

- Repository: `hat47x/tei-platform`
- Source commit: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- CLI source: `cmd/tei`
- Command: `deployment-provider-plan`
- Reference Workspace: `reference/workspace`
- Durable Run: `reference/order_rollout.durable-run.m0.21.start.json`
- Solution: `order_rollout`
- Version: `2026.8.27`
- Plugin Lock: `reference/workspace/.tei/plugin-lock.json`

固定revisionは再現対象を特定するためのEvidence条件であり、TEIをSOZAの特別なProvider ontologyへ昇格させるものではありません。

## 3. TEI側actual execution

`hat47x/tei-platform`のEvidence branchで、固定source commitを改めてcheckoutし、actual `cmd/tei`をbuildして`deployment-provider-plan`を実行しました。

- Workflow: `SOZA E3b-P2 TEI Evidence`
- Workflow Run: `33589084290`
- Job: `actual-tei-cli`
- Result: **success**
- Evidence artifact ID: `9831112092`
- Artifact name: `tei-soza-e3b-p2-linux-amd64`
- Artifact digest: `sha256:1ee8bf4112d9ae97e1f66b3165f70278663951e9dd4bd6020b465471f563a287`

Runでは、少なくとも次がskipされずsuccessしました。

1. Evidence workflow sourceのcheckout
2. 固定TEI source commitのcheckout
3. source identityの確認
4. actual `cmd/tei` build
5. actual `deployment-provider-plan`実行
6. Provider Planの最小成立条件の確認
7. Evidence bundle生成
8. metadata確定
9. 再実行用archive生成
10. Evidence artifact保存

したがって、このRunはhelper subprocessではなく、固定revisionの実TEI CLIを起動したExecutable Evidenceです。

## 4. Evidence artifactのidentity

Evidence artifactのmetadataは次のidentityを記録しています。

```text
schema: tei.soza-e3b-p2-evidence/v1
source commit:
  48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67
entry point:
  cmd/tei deployment-provider-plan
binary SHA-256:
  31f0298b47f9caaa93cd4b2da538cda72e23e5b518f2d0ddad2cf98c46882154
Provider Plan SHA-256:
  39eafb26cf189681e0bd2ff46fcaf000cbe2f860cf698765bbadac6dfbd2a950
```

Evidence bundleには、actual `tei` binary、Reference Workspace、durable run、Provider Plan出力、metadataが含まれます。

このidentityは外部source / artifactを追跡するための情報です。

```text
repository / source commit / binary digest
  != Capability identity
  != semantic Authority
  != Decision identity
```

## 5. SOZA Adapter経由のactual execution

取得したactual TEI artifactを使い、SOZAのcurrent `teiintegration`境界から実TEI CLIを別OS processとして起動しました。

検査対象は、`develop/v0.2.0`に正本化済みの次の実装と同一Git blobです。

- `runtime/go/teiintegration/tei_cli.go`
  - Git blob: `62025ae7eeae388d29e9602957b6f3833251e671`
- `runtime/go/teiintegration/tei_live_test.go`
  - Git blob: `929de9ea1b5d7d1c529ab6124b079c35bd4bb669`

`TestLiveTEIProviderPlan`をskipさせずにactual artifactへ向けて実行し、次を確認しました。

- actual `tei` binaryを別OS processとして起動できる。
- actual `deployment-provider-plan`出力をcurrent Adapter-local DTOでstrictに読める。
- mapping後のCapability Observationがcurrent validatorを通る。
- `availability = true`を観測できる。
- `provider_plan_resolved = true`を観測できる。
- source state provenanceを保持できる。
- TEI固有のProvider Plan fieldをUniversal Capability Observationへ転写しない。

この実行はChatGPT作業セッション内で行ったactual artifact実証であり、SOZA GitHub Actionsの`TEI_REPOSITORY_TOKEN`経路が成功したという意味ではありません。

## 6. actual Provider Planの回帰fixture

actual TEIが生成したProvider Plan bytesを、次のfixtureとしてSOZA repositoryへ保持します。

- `runtime/go/teiintegration/testdata/tei-provider-plan-48a7ca1f.json`
- SHA-256: `39eafb26cf189681e0bd2ff46fcaf000cbe2f860cf698765bbadac6dfbd2a950`

`runtime/go/teiintegration/actual_provider_plan_fixture_test.go`では、次を通常CIで継続検査します。

- fixture digestが固定値と一致する。
- current strict decoderでactual Provider Planを読める。
- current Capability Observationを生成できる。
- current validatorを通る。
- `migration.atlas`、`pluginRuntime`、`resourceBindings`、`TEI_DATABASE_CREDENTIAL`等のTEI固有情報をCapability Observationへ漏らさない。

このfixture testはactual processを毎回起動するEvidenceではありません。

```text
actual process execution Evidence
  != actual-output compatibility regression test
```

両者を分けて記録することで、外部artifact取得経路を通常CIへ暗黙に要求せず、actual outputとの互換性だけは継続して検査できます。

## 7. E3b-P2で今回成立した範囲

今回、次の範囲にはScoped Executable Evidenceがあります。

- 固定TEI source revisionのidentity確認
- actual `cmd/tei` build
- actual `deployment-provider-plan`実行
- actual binary / Provider Plan digestの固定
- actual TEI CLIをSOZA Adapterから別processとして起動
- current strict decoding
- current Capability Observation mapping / validation
- Provider固有情報の非漏出
- actual Provider Plan bytesに対する通常CI回帰検査

したがって、**E3b-P2のfixed-artifact actual TEI CLI execution scopeはScoped Executable Evidence available**とします。

## 8. 今回も成立させないもの

次は引き続き未検証です。

- SOZA Actionsからprivate TEI repositoryを継続取得するcredential運用
- `TEI_REPOSITORY_TOKEN`を含む特定Secret方式の標準化
- arbitrary / future TEI versionとの互換性
- TEI binaryの正式な配布、署名、更新方式
- long-running serviceとしてのTEI integration
- network / credential失効 / artifact store障害を含むOperational portability
- production execution authorization
- E3b-M1b external model-backed Cognitive Method
- E4 Operational portability
- v0.2.0 supported scopeの遡及的拡張
- この変更に対する新しいRelease Evidence
- Adoption / Outcome Evidence

とくに、今回TEI側の固定artifact生成経路で成功したことを、SOZA Actionsのprivate repository acquisitionが解決済みであるとは扱いません。

## 9. Requirement / Scenario監査

新しいStable Requirement / Scenarioは追加しません。

今回の実証で確認した意味境界は、既存の次のRequirement / Scenarioで表現できます。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

実TEIを接続できたこと自体を、新しいUniversal TEI ContractやStable Requirementの根拠にはしません。

## 10. Evidence state

- Design Evidence for the current E3b-P2 boundary: **Satisfied**
- ISSUE-000061 external executable injection boundary: **Scoped Executable Evidence available**
- E3b-P2 fixed-artifact actual TEI CLI execution: **Scoped Executable Evidence available**
- SOZA Actions private-repository acquisition / credential operation: **Not Yet Verified**
- arbitrary TEI version compatibility: **Not Yet Verified**
- E3b-M1a live KJ Atlas + deterministic model stub: **Scoped Executable Evidence available**
- E3b-M1b external model-backed Cognitive Method: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence for this change: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 11. 自然な日本語レビュー

ISSUE-000061 / 000065、PMS-06、current Capability Observation Contract、`runtime/go/teiintegration`、TEI固定source commit、TEI側Workflow Run `33589084290`、Evidence artifact、actual Provider Plan、SOZAのcurrent live integration testを照合しました。

先行probeで資格情報が利用できずactual TEI stepがskipされた事実はそのまま残し、後続のfixed-artifact実証によって初めて成立した範囲を別Evidenceとして積み上げています。また、TEI側でactual binaryを作れたこと、SOZA Adapterからそのbinaryを実行できたこと、actual outputを通常CIで継続検査できることをそれぞれ区別しました。

今回成立したのは固定revision・固定artifactに対するScoped Executable Evidenceです。cross-repository credential運用、任意version互換性、production integration、Operational / Release / Adoption・Outcome Evidenceへは広げていません。

意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
