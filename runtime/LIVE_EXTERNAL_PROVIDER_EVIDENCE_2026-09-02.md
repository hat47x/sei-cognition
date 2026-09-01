# Live External Provider Evidence — 2026-09-02

状態: **Scoped Executable Evidence**  
対象: **PMS-06 / E3b-P1 public live Provider service**

## 1. この文書の役割

この文書は、ISSUE-000060で実施した最初のlive external Provider integrationについて、**実際に確認できたことと、まだ確認していないことを分けて記録するEvidence文書**です。

今回の実証では、SOZAとは独立したpublic serviceをネットワーク越しに実際に呼び出し、その応答をProvider固有の表現のままUniversal Contractへ持ち込まず、current Capability Observationへ戻せることを確認しました。

一方、この結果をE3b全体、TEI live integration、external Cognitive Method execution、Operational portability、Product Releaseへ拡張しません。

## 2. 実証した経路

```text
SOZA liveintegration reference client
        │
        │ HTTPS
        ▼
public GitHub REST API
        │
        │ fixed commit response
        ▼
Provider-local response validation
        │
        ▼
reference mapping
        │
        ▼
current Capability Observation validator
```

live serviceにはGitHub REST APIのcommit取得面を使いました。

- repository: `hat47x/cultural-substrate-weaving`
- expected commit: `aa3651f3460a6db7dc70bd848f93b600f149ffe8`

GitHubをSOZAの標準Providerとしたわけではありません。追加credentialを要求せず、固定revisionをlive network越しに問い合わせられるため、最初のreference serviceとして利用しています。

## 3. 実装した境界

`runtime/go/liveintegration`に、live serviceへのHTTP呼び出しとProvider-local responseの検査を置きました。

成功時にcurrent Capability Observationへ移すのは、対象Capabilityについて今回観測できた最小限の意味だけです。

- 外部serviceへ到達し、正常応答を得られたこと
- 期待した固定revisionを応答上で確認できたこと
- どのProvider / mappingから得たObservationかを区別できること

GitHub固有の`node_id`、HTML URL、API response shape等はCapability Observationへ転写しません。repository / commit / HTTP protocolもUniversal semantic identityへ昇格させません。

```text
GitHub response shape
  != SOZA Universal Provider State

HTTP success
  != semantic authority

Provider identity
  != Capability identity
```

## 4. Negative case

通常のGo testでは`httptest`を使い、外部networkへ依存せず次を再現しています。

1. 正常応答からcurrent Capability Observationを生成できる。
2. responseのrevisionが期待値と異なる場合、Observationを生成しない。
3. HTTP 5xxの場合、Observationを生成しない。
4. timeout / cancellationの場合、Observationを生成しない。
5. Provider固有response fieldがCapability Observationへ漏れない。
6. 不正なrepository指定をProvider requestへ進めない。

失敗時に返すのはerrorとzero-value documentであり、失敗したProvider responseをcanonicalな観測として確定しません。

## 5. 初回current-baseline CI Evidence

PR #37の初回head `977773dc3071c8a4d6f33bf4f29e3ffc0c1fec23`では、次がsuccessしました。

- External Integration E3b Run `33569912285`
  - deterministic live integration boundary test: success
  - public GitHub REST APIへのactual live call: success
  - fixed commit responseのidentity確認: success
  - current Capability Observationへのmapping / validation: success
- Semantic Runtime Conformance Run `33569912339`: success
- Plan integrity Run `33569912230`: success
- External Integration E3a Run `33569912086`: success
- Local Package Artifact Run `33569912317`: success

同じheadのRelease Candidate Gate Run `33569912273`ではGate 1〜8がsuccessし、Gate 9がOpenなISSUE-000060を意図どおりblockしました。これはE3b-P1の失敗ではなく、v0.2.0 candidate policyが未解決Issueを検出した結果です。

IssueをResolvedへ移し、Evidence文書と上流文書を同期した最終headでは、Gate 9を含めてRelease Candidate Gateを再検査します。

## 6. Evidenceの読み方

今回成立したEvidenceは、E3bのうち最初のpublic live Provider serviceに限られます。

```text
E3b-P1 PASS
  != E3b全体 PASS
  != live TEI process / service PASS
  != external Cognitive Method live execution PASS
  != private credential integration PASS
  != rate-limit / retry / circuit-breaker design PASS
  != E4 Operational portability
  != Product Release / Release Evidence
  != Adoption / Outcome Evidence
```

また、固定commitを問い合わせたことでlive network invocationとresponse identityを確認しましたが、これはGitHubというProviderのproduction suitabilityやSLAを評価したものではありません。

v0.2.0 Release Candidateのsupported scopeはE3aまでです。E3b-P1を追加で実証したことを理由に、既存candidateのsupported scopeを暗黙に拡張しません。

## 7. Requirement / Scenario再監査

今回の実証から、新しいStable Requirement / Scenarioは追加しません。

既存の次で、今回観測したProduct failure boundaryを表現できます。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

HTTP、GitHub、固定commitという実装方式だけを理由に、新しいProduct Requirementを作りません。

## 8. 次に残るE3b

E3b全体には、少なくとも次が残っています。

- E3b-P2: live TEI process / service integration
- E3b-M1: external Cognitive Methodのlive execution
- private credentialの扱い
- timeout以外のnetwork degradationやrate limit
- version change時のProvenance / historical reconstruction
- formal integration protocolを本当に必要とするかの再判断

これらは、最初のP1の実証結果をそのまま一般化せず、対象ごとに必要な意味差を確認して進めます。

## 9. Natural Japanese review

PMS-06、`product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`、v0.2.0 Release Acceptance、ISSUE-000057 / 000058 / 000060、current Capability Observation Contract、Provider Adapter、PR #37初回headのExternal Integration E3b / Semantic Runtime / Plan integrity / E3a / Local Package / Release Candidate Gateを照合した。live network invocationが成立した事実と、TEI・Cognitive Method・production credential・Operational portability・Product Releaseが未検証である事実を分離し、GitHub固有のresponse shapeやprotocolをUniversal semantic modelへ持ち込まない境界を確認した。そのうえで、実証内容、negative case、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。