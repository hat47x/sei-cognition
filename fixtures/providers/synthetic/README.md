# Synthetic Provider Adapter Fixtures

更新日: 2026-08-31  
状態: **Fixture-scoped Executable Evidence Baseline**

## 1. 目的

このfixture群は、異なるProvider固有stateを一つのUniversal `ProviderState`へ統合せず、Provider Adapterを通してcurrent `sei.capability-observation/v1alpha1`へ写像できることを検証するための固定入力です。

Provider AとProvider Bは、意図的に異なるfield名と単位を使います。

```text
Provider A
  health
  delay_ms
  service_ref

Provider B
  ready
  response_seconds
  endpoint
```

これらのfieldをSOZA Universal Coreのfieldとして採用する意図はありません。Provider固有stateの違いを保ったまま、Capability判断に必要なObservationだけを外在化する境界を検査します。

```text
Provider-specific input schema != Universal Contract
```

## 2. Fixtures

- `provider-a-green.json` — availability=true、latency=240msへmappingできるProvider A状態。
- `provider-a-missing.json` — healthとdelayが欠けており、falseや0ではなくUnknownとして扱う状態。
- `provider-b-ready.json` — availability=true、0.24秒を240msへ変換するProvider B状態。
- `provider-b-missing.json` — readyとresponse timeが欠けており、Unknownとして扱う状態。

fixtureはProvider実装の標準Schemaではありません。synthetic test inputとしてだけ利用します。

## 3. 検査する意味境界

1. Providerごとにinput schemaが異なってよい。
2. 同じCapabilityへ異なるProviderからObservationを作れる。
3. unit conversionやstatus interpretationをmappingとして扱う。
4. `mapping_provenance`と`source_state_ref`を失わない。
5. Provider-specific targetをSOZA Universal field setへ展開しない。
6. missing値をnegative / default値へ変換しない。
7. Adapter outputからRecommendation、Decision、Authority、Executionを生成しない。
8. 生成結果をcurrent Capability Observation runtime validationへ通す。
9. Provider A / B固有field名をCapability ObservationのUniversal field setへ直接漏らさない。

Provider-specific contextをReferenceやextensionとして保持すること自体は禁止しません。禁止しているのは、Provider固有SchemaをUniversal semantic authorityへ昇格させることです。

## 4. Executable Evidence

synthetic Provider Adapter sliceは`runtime/go/provideradapter/`で実装され、fixtureを使ったGo testがactual CIで再現されています。

代表run:

- Run ID: `33349604842`: **success** — synthetic Adapter slice初回closure
- Run ID: `33349801993`: **success** — Provider-specific field非漏洩hardening後

Contracts / Representation Profile文書の再基線化後もSemantic Runtime Conformanceはsuccessしています。

- Run ID: `33389771449`: **success**
- Run ID: `33389973787`: **success**

後続runは新しいProvider capabilityを増やしたEvidenceではなく、current semanticsに対する回帰確認です。

## 5. Evidence boundary

このfixtureのPASSはsynthetic Provider Adapter sliceのscoped Executable Evidenceです。

```text
synthetic fixture / Adapter PASS
  != TEI production integration
  != SaaS production interoperability
  != human Provider integration
  != Capability Choice decided
  != Authorization / Execution
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current Evidence state:

- Design: **Satisfied** — ADR-0024、Capability Observation Contract、Adapter boundaryを定義済み。
- Executable: **Partially Satisfied** — synthetic A / Bのtested scopeで再現可能。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

synthetic Providerの数やfixture件数をProvider Independenceの達成度スコアにはしません。

## 6. Natural Japanese review

fixture、Provider Adapter実装・test、Capability Observation Contract、ADR-0024、actual Semantic Runtime Conformanceへ戻って意味境界を再監査しました。Provider固有Schemaの標準化と誤読されないよう役割を整理し、current 5段階Evidenceと回帰runを反映しています。その後、検査対象・非対象とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
