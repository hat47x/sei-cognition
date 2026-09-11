# SEI Implementation Language Policy

更新日: 2026-09-01  
状態: **Current Architecture Policy**

## 1. この文書の役割

この文書は、ADR-0027で決定したSEIの実装言語方針を、current Architectureから読める形に整理します。

言語選択はSEIのUniversal Semantic Contractではありません。Product Value、Requirement、Contractの意味はGoへ依存せず、外部のCognitive MethodやCapability Providerへ同じ言語を要求しません。

## 2. 標準production runtime

SEI自身が所有・配布するproduction runtimeとfirst-party reference implementationでは、Goを標準実装言語とします。

主な対象は次です。

- Semantic Contract loader / validator / reconstruction runtime
- canonical persistence / interchangeのproduction側実装
- first-party Provider Adapter
- service / daemon
- CLI
- Product backend
- SEI / TEI間で必要となるfirst-party integration component

current repositoryでも、`runtime/go/`の`semanticruntime`、`provideradapter`、`journeyharness`がこの方向を先行して実体化しています。

## 3. Goをsemantic requirementにしない

SEIが持ち運びたいのは実装言語ではなく、判断・不確実性・責任・来歴等の意味です。

```text
Semantic Contract
  != Go type definition
  != Go package
  != Go process
```

Go runtimeがcurrent reference implementationであっても、Contractのmachine-readable representationやIntegration Surfaceは、他言語から実装・利用できる形を維持します。

## 4. Pythonを残す領域

Pythonは補助的な「過渡期言語」として廃止する対象ではありません。次のような領域では、Pythonが最も自然であれば積極的に利用できます。

- AI / ML / embedding / NLPの研究
- Cognitive Method prototype
- exploratory analysis
- evaluation harness
- human review支援
- fixture生成
- one-shot migration / maintenance
- development checker
- Provider接続の短期probe

currentのV6 / V7 Projection Evaluation checkerは、この種の開発・評価用途に該当します。

## 5. production化するときの境界

Python等で作成したprototypeがproduction利用へ進む場合、直ちにGoへ書き直すことも、直ちにSEI Coreへ埋め込むこともしません。

次の順序で検討します。

1. Cognitive Method / Capability Providerとして独立したまま接続できるか。
2. process / API / MCP等の明示的境界で分離できるか。
3. first-party production runtimeへ同居させる必要が本当にあるか。
4. 同居が必要なら、Go移植と多言語runtime維持の運用コストを比較する。
5. ADR-0027のRevisit条件に該当するほど前提が変わる場合は、言語方針そのものを再審査する。

この順序により、Python ecosystemの強みを利用しつつ、production Coreの依存を無制限に増やさないようにします。

## 6. TEIとの関係

TEIのactual repositoryもGoで実装されています。両製品でGoを標準runtime言語とすることには、toolchain、CI、配布、observability、SDK等を共通化しやすい利点があります。

ただし、同じ言語を使うことは次を意味しません。

```text
same implementation language
  != same product
  != same runtime process
  != same deployment unit
  != privileged Provider relationship
```

SEIはTEIをCapability Providerの一つとして扱うというADR-0014の境界を維持します。

## 7. Packaging / Interactionへの含意

ISSUE-000046では、Goのsingle binary、CLI、long-running service等をsupported Packaging候補として評価できます。

ISSUE-000045のProduct Interactionでは、backend / canonical runtimeをGoとすることからfrontend technologyを自動決定しません。Web UI、desktop UI、MCP、API等はProduct Interactionの要件から別途選びます。

```text
Go backend
  != frontend technology fixed
```

## 8. 言語追加の判断

新しいfirst-party production runtime componentへGo以外を採用する場合は、少なくとも次を記録します。

- Goでは満たしにくい具体的要件
- process / Provider境界で分離できない理由
- Packaging / deployment / security updateへの影響
- dependency lifecycle
- observability / operationsへの影響
- 将来削除または再統合できる境界

単にprototypeがその言語で書かれていることだけでは、production runtimeへの追加理由にしません。

## 9. Evidence

current Go runtimeにはfixture-scoped Executable Evidenceがあります。一方、この文書とADR-0027が確立するのは言語配置のDesign Evidenceです。

```text
Go runtime exists
  != Go operational superiority proven
  != every Method should be Go
  != Release Evidence
```

言語方針のOperationalな妥当性はPackaging、deployment、実運用を通して後から検証します。

## 10. 関連文書

- `../plan/adr/ADR-0027-go-as-standard-production-runtime-language.md`
- `../plan/issue/ISSUE-000052-formalize-production-runtime-language-policy.md`
- `SEI_REFERENCE_ARCHITECTURE.md`
- `../product/principles/SEI_PRODUCT_PRINCIPLES.md`
- `../plan/adr/ADR-0014-sei-tei-product-boundary.md`
- `../plan/adr/ADR-0025-cognitive-method-portable-contract-boundary.md`
- `../plan/issue/ISSUE-000045-define-first-usable-product-interaction-boundary.md`
- `../plan/issue/ISSUE-000046-define-v0-2-0-product-packaging-and-deployment-boundary.md`

## 11. Natural Japanese review

ADR-0027、current Go runtime、Python evaluation tooling、SEI / TEI Product Boundary、Cognitive Method Realization分離を照合した。Goをproduction runtimeの標準Realizationとしつつ、Semantic Contract、外部Method / Provider、研究・評価へ言語制約を広げない構造を維持した。そのうえで、意味、例外、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。