# SEIの実装言語の方針

更新日: 2026-09-01  
状態: **現行の全体構成に適用する方針**

## 1. この文書の役割

本書は、ADR-0027で決定したSEIの実装言語方針を、現行の全体構成と関連付けて説明します。

実装言語の選択は、SEIの汎用的な意味の契約（Universal Semantic Contract）には含めません。製品価値、要求、契約で定める意味はGoに依存させず、外部の認知方式（Cognitive Method）や能力の提供元（Capability Provider）に同じ言語の使用を求めません。

## 2. 本番向け実行環境の標準言語

SEI自身が管理・配布する本番向け実行環境と、SEIが提供する参照実装には、Goを標準言語として採用します。

主な対象は次です。

- 意味の契約を読み込み、検証し、再構成する実行環境
- 正本となる意味の永続化と受け渡しの本番向け実装
- SEIが提供する外部接続部（Provider Adapter）
- サービスや常駐プログラム
- CLI
- 製品のサーバー側の処理
- SEIとTEIの連携に必要な、SEI側の構成要素

現行のリポジトリでも、`runtime/go/`内の`semanticruntime`、`provideradapter`、`journeyharness`が、この方針に沿う実装として先行しています。

## 3. 意味の契約にGoの使用を求めない

SEIが持ち運びたいのは実装言語ではなく、判断・不確実性・責任・来歴等の意味です。

```text
Semantic Contract
  != Go type definition
  != Go package
  != Go process
```

Goによる実行環境が現行の参照実装であっても、契約の機械可読な表現や外部との接続面は、他の言語でも実装・利用できるようにします。

## 4. Pythonを残す領域

Pythonを、一時的な補助言語として将来的に廃止するわけではありません。次のような領域では、Pythonが最も自然であれば積極的に利用できます。

- AI、機械学習、埋め込み表現、自然言語処理の研究
- 認知方式の試作
- 探索的な分析
- 評価を実行するための仕組み
- 人による確認の支援
- 試験用データの生成
- 一度限りの移行や保守
- 開発時の検査ツール
- 外部提供元との接続を試す短期的な検証

現行のV6・V7の用途別表現を評価する検査ツールは、こうした開発・評価用途に当たります。

## 5. 本番向けに採用する場合の判断

Pythonなどで作った試作品を本番向けに採用する場合も、直ちにGoへ書き直したり、SEIの中核へ取り込んだりはしません。

次の順序で検討します。

1. 認知方式や能力の提供元として、独立したまま接続できるか。
2. 別プロセス、API、MCPなどの明示的な境界で分離できるか。
3. SEIが提供する本番向け実行環境へ組み込む必要が本当にあるか。
4. 組み込みが必要なら、Goへの移植と複数言語の実行環境を維持する場合の運用負担を比較する。
5. ADR-0027のRevisit条件に該当するほど前提が変わる場合は、言語方針そのものを再審査する。

この順序で判断することで、Pythonの豊富なライブラリや関連ツールを活用しつつ、本番向けの中核に依存関係を無制限に増やさないようにします。

## 6. TEIとの関係

TEIの現在のリポジトリでも、実装言語にはGoを使用しています。両製品でGoを標準的な実行環境の言語とすることで、開発ツール、継続的な検証（CI）、配布、稼働状況の把握、SDKなどを共通化しやすくなります。

ただし、同じ言語を使うことは次を意味しません。

```text
same implementation language
  != same product
  != same runtime process
  != same deployment unit
  != privileged Provider relationship
```

SEIはTEIを能力の提供元の一つとして扱うという、ADR-0014で定めた境界を維持します。

## 7. 配布形態と操作方式への影響

ISSUE-000046では、Goの単一実行ファイル、CLI、常駐サービスなどを、対応する配布形態の候補として評価できます。

ISSUE-000045で扱う利用者とのやり取りでは、サーバー側の処理や正本の意味を扱う実行環境がGoであっても、画面を作る技術までは自動的に決めません。Web画面、デスクトップ画面、MCP、APIなどは、利用者とのやり取りに関する要求から別途選びます。

```text
Go backend
  != frontend technology fixed
```

## 8. 言語追加の判断

SEIが提供する本番向け実行環境の新しい構成要素にGo以外の言語を採用する場合は、少なくとも次の点を記録します。

- Goでは満たしにくい具体的要件
- 別プロセスや外部の提供元として分離できない理由
- 配布、配備、安全上の更新への影響
- 依存する技術の保守周期
- 稼働状況の把握と運用への影響
- 将来削除または再統合できる境界

試作品がその言語で書かれているというだけでは、本番向け実行環境へ追加する理由にはしません。

## 9. 検証根拠

現行のGo実行環境には、試験用データの範囲に限った実行検証根拠（Executable Evidence）があります。一方、本書とADR-0027が示すのは、言語の配置に関する設計上の根拠（Design Evidence）です。

```text
Go runtime exists
  != Go operational superiority proven
  != every Method should be Go
  != Release Evidence
```

言語方針が運用上も妥当かどうかは、配布・配備と実際の運用を通して検証します。

## 10. 関連文書

- `../plan/adr/ADR-0027-go-as-standard-production-runtime-language.md`
- `../plan/issue/ISSUE-000052-formalize-production-runtime-language-policy.md`
- `SEI_REFERENCE_ARCHITECTURE.md`
- `../product/principles/SEI_PRODUCT_PRINCIPLES.md`
- `../plan/adr/ADR-0014-sei-tei-product-boundary.md`
- `../plan/adr/ADR-0025-cognitive-method-portable-contract-boundary.md`
- `../plan/issue/ISSUE-000045-define-first-usable-product-interaction-boundary.md`
- `../plan/issue/ISSUE-000046-define-v0-2-0-product-packaging-and-deployment-boundary.md`

## 11. 日本語の推敲に関する記録

ADR-0027、current Go runtime、Python evaluation tooling、SEI / TEI Product Boundary、Cognitive Method Realization分離を照合した。Goをproduction runtimeの標準Realizationとしつつ、Semantic Contract、外部Method / Provider、研究・評価へ言語制約を広げない構造を維持した。そのうえで、意味、例外、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。