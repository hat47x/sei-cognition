# ADR-0027: SEI production runtimeの標準実装言語をGoとする

Status: **Accepted**  
Related Issue: **ISSUE-000052**  
Updated: 2026-09-01

## Context

SEIでは、開発初期のchecker、評価、fixture処理等でPythonを利用してきた一方、current production-runtime候補はすでに`runtime/go/`へ集約されつつあります。actual repositoryにはGoで実装された`semanticruntime`、`provideradapter`、`journeyharness`があり、Semantic Contractの読み込み、検証、再構成、Provider Adapter、end-to-end semantic Product JourneyのExecutable Evidenceを担っています。

関連製品TEIもactual repository `hat47x/tei-platform`でGo moduleを持ち、CLI / core implementationをGoで構成しています。SEIとTEIはProduct Boundaryを分離しており、同一言語を使うこと自体を製品結合の理由にはしませんが、両製品の標準runtime言語を揃えることで、toolchain、CI、配布、observability、cross-product SDK等を共通化しやすくなります。

一方、SEIはCognitive MethodやCapability Providerの実現方式を自らへ囲い込まないことをProduct Valueとしています。AI / ML、探索的分析、評価、研究用prototypeではPython ecosystemの利点が大きい場合があります。そのため、Go採用をSEIに接続するすべての実装へ波及させるとProvider IndependenceやRealization交換可能性を不必要に狭めます。

今回判断するのは、**SEI自身がproduction productとして所有・配布する標準runtime realizationの主言語**です。Semantic Contractそのものや外部Method / Providerの実装言語は固定しません。

## Decision

SEI自身のproduction runtimeと標準reference implementationでは、**Goを標準実装言語とします。**

原則として次をGoで実装します。

- canonical Semantic Contractのloader / validator / reconstruction runtime
- persistence / interchangeのproduction側実装
- SEIが標準提供するProvider Adapter
- production service / daemon
- CLI
- first-party Product backend
- SEIとTEIの間で共有価値がある低レベルSDK / integration component

ただし、GoはSEIのSemantic ContractやUniversal Coreの意味要件ではありません。

```text
SEI semantic portability
  != Go dependency

standard production runtime language = Go
external Method / Provider language = unrestricted by this ADR
```

### Pythonを積極的に許容する領域

Pythonは廃止しません。特に次では、Pythonが最も自然であれば継続して使用できます。

- Cognitive Method Realizationの研究・prototype
- LLM / ML / embedding / NLP等の実験
- exploratory analysis
- evaluation harness / human-review支援
- fixture生成
- one-shot migration / maintenance script
- development-time checker
- 新しいProvider接続の短期probe

これらがproduction productの耐久的runtime境界へ昇格する場合は、Goへ移す価値とPythonのまま独立Provider / toolとして保つ価値を改めて比較します。Python実装であることだけを理由に移植しません。

### 言語境界

Cognitive Method、Capability Provider、外部service等は、JSON等のportable Contract、API、MCP、process boundaryその他の明示的なIntegration Surfaceを通じて接続できます。

```text
SEI Core / Runtime       Go
SEI first-party service  Go
TEI core/runtime          Go
Semantic Contract         language-neutral
Cognitive Method          language-neutral
Capability Provider       language-neutral
research / evaluation     best-fit language; Python allowed
```

## Alternatives considered

### PythonをSEI本体の標準言語とする

AI / ML ecosystem、prototype速度、動的なデータ処理では優位性があります。しかしcurrent SEIの中心はmodel trainingやLLM orchestrationではなく、長寿命のSemantic Contract、validation、interchange、persistence、Provider境界、Product Interactionを支えるruntimeです。

この責務では、単一binary配布、静的型による境界確認、依存の小ささ、service / CLI双方への展開、TEIとのtoolchain共通化を考えるとGoの方が標準runtimeとして適合します。

### Goだけを許可する

採用しません。AI / ML research、Cognitive Method prototype、評価・分析でPython ecosystemを捨てる合理性がなく、Provider / Method RealizationまでGoへ固定するとSEI自身のExecution Independenceを弱めます。

### 言語を一切標準化しない

採用しません。SEI自身が所有するproduction runtimeまで案件ごとに言語が分散すると、Packaging、deployment、CI、security update、observability、運用知識の負担が増えます。標準を一つ持ち、明確な外部境界では言語非依存とする方が責務分離が明瞭です。

## Consequences

### Positive

- current `runtime/go/`を作り直さず、すでに得られたExecutable Evidenceを継続利用できる。
- TEIと開発toolchain、CI、logging / tracing、配布方式等を揃えやすい。
- production runtimeを単一binaryとして配布できる可能性が高まり、PMS-04 Packaging / Deployment検討と整合しやすい。
- staticな型境界を利用してSemantic Contractの意味差を実装上も維持しやすい。
- PythonのAI / ML ecosystemをMethod / Provider / research層で引き続き利用できる。
- 「SEI本体の言語」と「SEIに接続可能な実装言語」を分けることでProvider Independenceを保てる。

### Costs / Risks

- Pythonだけで高速に試せるAI機能をfirst-party runtimeへ組み込む場合、process / API boundaryを設けるかGo実装を用意する必要がある。
- GoとPythonの両toolchainがrepository内に残るため、補助toolまで完全な単一言語にはならない。
- Go向けAI / ML ecosystemが要件を満たさない領域をproduction Coreへ直接取り込みたくなった場合、言語標準との緊張が生じる可能性がある。
- TEIと同じGoを使うことを理由に、SEIとTEIのProduct BoundaryやContract Boundaryを暗黙に結合しない注意が必要である。

## Revisit conditions

次のEvidenceが得られた場合、このDecisionを再検討します。

- SEI production runtimeの中核要件として、Python ecosystemでなければ実用上成立しない機能が複数確認された。
- Goを標準とすることでPackaging / deployment / operabilityが継続的に悪化し、言語共通化の利点を上回るEvidenceが得られた。
- production Cognitive Methodをprocess / Provider boundaryへ分離できず、Goへの移植が意味・性能・保守性を大きく損なうことが実証された。
- TEIを含む周辺製品とのtoolchain共通化が実際には価値を生まず、SEI単独では別言語が明確に優位であると確認された。
- Go ecosystemまたは製品要件が大きく変わり、current判断の前提が成立しなくなった。

単にPythonの記述量が少ない、またはGoの記述量が多いといった局所的な比較だけでは再基線化しません。

## Evidence

### Design Evidence

- SEI Product Value / Principles: Provider Independence、Execution Independence、code shedding / prompt shedding
- ADR-0014: SEI / TEI Product Boundary
- ADR-0021 / ADR-0022: current Architecture / runtime boundary
- ADR-0025: Cognitive Method Definition / Realization / Application分離
- actual `runtime/go/`にsemanticruntime、provideradapter、journeyharnessが存在する。
- actual `runtime/go/go.mod`でGo moduleが成立している。
- actual `hat47x/tei-platform`に`go.mod`、`cmd/`、`internal/`が存在する。
- Pythonはcurrent SEIではV6 / V7評価checker等、主としてevaluation / development toolingに利用されている。

### Executable Evidence

current Go runtimeにはContract / runtime / Product Journeyについてfixture-scoped Executable Evidenceがあります。ただし、これは「Goがあらゆる将来要件で最良である」ことを実証するものではありません。

```text
current Go runtime PASS
  != language choice permanently optimal
  != packaged product proven
  != operational superiority proven
```

Release / Operational / Adoption・Outcome Evidenceは本ADR単独では`Not Yet Verified`です。

## Follow-up

- ISSUE-000046 Packaging / Deployment検討では、Go single-binary / service / CLIを標準候補として扱う。
- ISSUE-000045 Product Interactionでは、Interaction technologyの選択をGoそのものへ従属させず、backend / canonical runtimeとの境界を検討する。
- Python製Cognitive Method等をproduction利用する場合は、Provider / process / API等の明示的境界を優先して検討する。
- 新しいfirst-party production runtime componentでは、別言語を採用する場合に本ADRのRevisit条件または局所的な例外理由を明示する。

## Natural Japanese review

current Product Value、Product Principles、SEI / TEI Product Boundary、Cognitive Method境界、actual Go semantic runtime、Python評価tool、TEIのactual Go repositoryを照合した。Go統一をSemantic Contractや外部Providerへ波及させず、SEI自身が所有するproduction runtimeの標準Realizationに限定した。PythonのAI / ML・研究上の利点を正式に残し、意味、規範強度、例外、Evidenceの高さを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。