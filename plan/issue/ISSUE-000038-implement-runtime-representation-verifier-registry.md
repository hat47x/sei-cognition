# ISSUE-000038: RuntimeへRepresentation Verifier Registryを実装する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0021, ADR-0022, ADR-0023**  
Updated: 2026-09-01

## Goal

Accepted済みのRepresentation Profileをfirst Semantic Runtimeへ接続し、Exact Bindingのcontent digestをruntime上で再検証できる最小のVerifier Registryを実装する。

対象Profileは次の2つとする。

```text
soza.jcs+sha256/v1alpha1
soza.raw-bytes+sha256/v1alpha1
```

このIssueでは新しいSemantic ContractやUniversal Core型を作らず、ADR-0008 / ADR-0009 / ADR-0023で既に決定済みの検証境界をExecutable Evidenceへ落とす。

## Background

current repositoryでは、次がすでに成立している。

- Exact BindingとRepresentation Profile mechanicsの分離 — ADR-0008
- Exact BindingとVerification Outcomeの分離 — ADR-0009
- JCS + SHA-256 / raw-bytes + SHA-256 ProfileのAccepted baseline — ADR-0023
- Profile fixture / JCS Go probeのfixture-scoped Executable Evidence
- first Semantic Runtimeのread / validate / reconstruct slice — ADR-0022

一方、current `semanticruntime`はRepresentation Profile identityとdigest文字列の存在を検査するが、payloadからdigestを再計算するVerifier Registryをまだ持たない。

```text
Exact Binding metadata valid
  != Exact Binding content verified
```

`contracts/TRACEABILITY.md`でも、Production-grade Runtime Verifier Registry / Adapter integrationはNot Yet Verifiedとして残っている。

## Questions

1. runtimeでProfile ID / versionからVerifierをどのように解決すれば、Profile Definitionと実装を分離したままにできるか。
2. `verified / failed / not_verified`を、未知Profile、payload不足、digest mismatch、Profile入力制約違反でどう再現するか。
3. JCS Profileのsafe-integer / Unicode non-normalization等を、既存probeと意味差を生じさせずruntimeへ実装できるか。
4. raw-bytes Profileを、暗黙の改行変換・再encode・normalizationなしに検証できるか。
5. Verifier結果をExact Binding本体へ書き戻さず、独立したVerification Outcomeとして返せるか。

## Constraints

- Profile authorityはProfile DefinitionとRFC 8785であり、Go library APIではない。
- runtime独自のcanonicalization規則を新設しない。
- `Exact Binding != Verification Outcome`を維持する。
- unknown Profile、verifier不足、payload不足をdigest mismatchへ変換しない。
- `not_verified != failed`を維持する。
- SHA-256をUniversal Core唯一のhash algorithmへ昇格しない。
- JCSへ投入できない高精度semantic integerをbinary64へ暗黙丸めしない。
- Unicode normalizationを暗黙実行しない。
- raw-bytes入力へ改行変換、再encode、decompression等を暗黙適用しない。
- historical M47 digest規則をcurrent Profileから推測しない。ISSUE-000034は独立Blocked事項のままとする。
- Action execution、Authorization enforcement、production Provider / TEI integrationはNon-goalとする。
- Verifier Registryの導入を理由にSemantic Runtimeのread / validate / reconstruct境界をexecution側へ拡張しない。

## Required scenarios / experiments

### JCS Profile

1. known Profile + canonical digest一致 → `verified`
2. known Profile + digest mismatch → `failed`
3. object property order / insignificant whitespace差でも同一digestになる。
4. duplicate key等、JCSとして不正なrepresentation → `failed`
5. `9007199254740993`等のunsafe integerを暗黙丸めせず → `failed`
6. NFC / NFDを勝手にnormalizeせず、Profile fixtureと同じdigest差を保持する。

### Raw bytes Profile

7. known Profile + raw bytes digest一致 → `verified`
8. known Profile + digest mismatch → `failed`
9. text / binary双方で入力bytesそのものを検証する。

### Registry / outcome boundary

10. unknown Profile ID / version → `not_verified`
11. payloadを取得できない → `not_verified`
12. Verifier Registryに実装がないProfile → `not_verified`
13. verificationでExact Binding自体をmutateしない。
14. `VerificationOutcome`にbinding、status、必要なreason / verifier referenceを返せる。
15. current semantic loader / Provider Adapter testsが回帰しない。

## Deliverables

- runtime用Representation Verifier interface / Registry
- JCS + SHA-256 verifier
- raw-bytes + SHA-256 verifier
- Profile fixtureを再利用するGo tests
- `verified / failed / not_verified`の境界test
- `runtime/go/go.mod` / `go.sum`の再現可能なdependency固定
- Semantic Runtime Conformanceへの統合
- runtime / Contract traceability / Evidence文書のcurrent状態更新

## Resolution

次をすべて満たしたときResolvedにする。

- [ ] current 2 Profileをruntime Registryから解決できる。
- [ ] JCS Profile fixtureのpositive / negative境界をGo runtime testで再現できる。
- [ ] raw-bytes fixtureをGo runtime testで再現できる。
- [ ] `verified / failed / not_verified`をruntime testで区別できる。
- [ ] unknown Profileとpayload不足を`failed`へ誤変換しない。
- [ ] Exact Bindingを検証結果でmutateしない。
- [ ] current Contract / runtime / Provider Adapter testsが回帰しない。
- [ ] Representation Profile ConformanceとSemantic Runtime Conformanceがsuccessする。
- [ ] Release / Operational / Adoption・Outcome Evidenceへ過大昇格していない。
- [ ] 実装・文書を自然な日本語となることを最重要視して再監査した。

## Reopen conditions

Resolved後、次の場合は再開または後続Issueを検討する。

- 同じProfile ID / versionで別実装間のdigest差が確認された。
- current verifier libraryに重大なsecurity / maintenance / interoperability問題が見つかった。
- streamingやexternal object source等、現在の`[]byte`入力では扱えない主要use caseが具体化した。
- 新しいRepresentation Profileをruntimeへ登録する際、current Registry abstractionでは意味を保てないことが分かった。

production Provider / TEI interoperability、Release、Operational、Adoption / Outcomeは本Issueの再開理由ではなく、それぞれ別Evidence sliceとして扱う。

## CI / verification

最低限、次を確認する。

- `Semantic Runtime Conformance`
- `Representation Profile Conformance`
- `Contract Conformance`
- `Plan integrity`

CI failureを検出した場合は、その場で原因を解消してsuccessを確認してから後続作業へ進む。

## Natural Japanese review

ADR-0008、ADR-0009、ADR-0022、ADR-0023、current Profile Definition、Profile fixture、JCS Go probe、first Semantic Runtime実装、Contract Traceabilityへ戻って境界を整理した。その後、Goal、Constraints、Required scenarios、Resolution条件、Evidence強度を固定し、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
