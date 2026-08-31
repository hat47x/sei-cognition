# Synthetic Provider Adapter fixtures

更新日: 2026-08-31  
状態: **Executable test fixture**

## 目的

このfixture群は、異なるProvider固有stateを一つのUniversal `ProviderState`へ統合せず、Provider Adapterを通してcurrent `soza.capability-observation/v1alpha1`へ変換できることを検証します。

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

これらのfieldをSOZA Universal Coreのfieldとして採用する意図はありません。Provider固有stateの違いを保ったまま、必要な観測結果だけをCapability Observationへ外在化する境界を検査するための入力です。

## fixture

- `provider-a-green.json`: availability=true、latency=240msへmappingできるProvider A状態。
- `provider-a-missing.json`: healthとdelayが欠けており、falseや0ではなくUnknownとして扱う状態。
- `provider-b-ready.json`: availability=true、0.24秒を240msへ変換するProvider B状態。
- `provider-b-missing.json`: readyとresponse timeが欠けており、Unknownとして扱う状態。

## 検査する意味境界

1. Providerごとにinput schemaが異なってよい。
2. 同じCapabilityへ異なるProviderからObservationを作れる。
3. unit conversionやstatus interpretationをmappingとして扱う。
4. `mapping_provenance`と`source_state_ref`を失わない。
5. Provider-specific targetをSOZA Universal field setへ展開しない。
6. missing値をnegative/default値へ変換しない。
7. Adapter outputからRecommendation、Decision、Authority、Executionを生成しない。
8. 生成結果をcurrent Capability Observation runtime validationへ通す。

## Evidence境界

このfixtureのPASSはsynthetic Provider Adapter sliceのExecutable Evidenceです。

```text
synthetic fixture PASS
  != TEI production integration
  != SaaS production interoperability
  != Provider operational evidence
  != release readiness
```

## 自然な日本語レビュー

fixtureの役割をProvider固有Schemaの標準化と誤読しないように整理したうえで、検査対象と非対象を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
