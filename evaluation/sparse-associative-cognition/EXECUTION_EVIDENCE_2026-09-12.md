# Sparse Associative Cognitive Substrate — Execution Evidence 2026-09-12

状態: **Executable evaluation prototype evidence**

## 1. 何を確認したか

依存ゼロのGo prototypeについて、synthetic fixtureだけを用いて次を確認した。

- fixed seedで同一feature入力から同一signatureを再生成できる
- 共通featureを持つ入力が、非共通入力より高いbinary cosine similarityを持つ
- 2入力のbundleで共有activationが優先される
- compact signature indexからtop-k候補を取得できる
- upsert / deleteがindex件数を壊さない
- novelty signalが近い候補と遠い候補を逆転させない

実装は `prototype-go/sparseassoc/` に置く。

## 2. synthetic microbenchmark

実行環境:

- OS: Linux
- arch: amd64
- CPU: AMD EPYC 9V74 80-Core Processor
- Go toolchain: container current Go toolchain
- Config: dimensions=4096, fanout=8, active=64

`go test -bench=. -benchmem -count=3` の観測範囲:

| Benchmark | 観測値 | allocation |
|---|---:|---:|
| Encode 20 features | 5.58–5.65 µs/op | 240 B/op, 5 allocs/op |
| Query 10,000 signatures, top-8 | 0.844–0.858 ms/op | 192 B/op, 1 alloc/op |

`uint16` dimension IDを用いるため、active=64のsignature active payloadは128 byteである。これはGoのslice header、entry、string、map等のruntime overheadを含まない。

## 3. 最適化で行ったこと

初期prototypeから次を変更した。

- dimension IDを`uint32`から`uint16`へ縮小
- Encoderへscore / mark / touched scratchを保持し、毎回の大きなmap構築を廃止
- indexをmap iteration主体からcontiguous slice scanへ変更
- Queryは全candidate listを作らずtop-kだけを保持

同じsynthetic benchmarkでは、変更前の20-feature Encode約17 µs/opから約5.6 µs/op、10,000件Query約1.0 ms/opから約0.85 ms/opへ低下した。ただし異なる実装revision間の参考比較であり、製品性能保証ではない。

## 4. SUI Associative Cognition Provider adapter

SUI Sensemaking側で確定した `sui.associative-recall-request/v1alpha1` / `sui.associative-recall-response/v1alpha1` 境界へ、current Go `sparseassoc`を接続するevaluation adapterを `prototype-go/suiassocprovider/` に追加した。

adapterは次を行う。

- SUIが渡したboundedな `text / graph / provenance / grouping` channelをcaller-owned sparse featureへ変換する
- anchor群をbundleし、anchor以外のitemだけを候補indexへ入れる
- `sparseassoc.Candidate.Similarity`をProvider内部の候補絞り込みにだけ使う
- SUI responseではcandidate refをstable ref順へ戻し、内部rankingを外へ出さない
- `activation / similarity / confidence / importance / rank / score / novelty_signal`をresponse schemaへ持ち込まない
- 十分な候補がない場合は数値noveltyではなく `outcome=abstain`, `noveltyCue=abstain` へ縮退する
- 外在化できる説明は、双方に実在する入力channel provenanceだけに限定する
- requestの未知field、上限超過、重複ref、scope外anchorをfail-closedする

v1alpha1の境界上限はSUI側と合わせ、次を固定した。

- items: 512以下
- anchorRefs: 32以下
- candidateLimit: 64以下

### 4.1 ローカル検証

SOZAのAccepted Development Conventionに従い、GitHub Actionsは使用していない。

一方、この作業環境から `github.com` を直接cloneする経路はDNS解決できなかったため、full repository checkout上のtestは実行できなかった。

代わりに、GitHub connectorから取得したcurrent `main` の `prototype-go/sparseassoc/sparseassoc.go` と、branch上のadapterが持つ**同じ型・validation・candidate narrowing・response縮退の契約ロジックを再現したローカル検証版**を一時moduleへ配置し、接続境界を独立に確認した。これはbranch上のファイルをbyte-for-byte checkoutして実行したものではない。

ローカル環境はGo 1.23.2であったため、一時moduleの`go` directiveだけを1.23とした。repositoryの`prototype-go/go.mod` (`go 1.25`) は変更していない。今回のadapterが利用する言語機能はこのローカルtoolchainで実行可能な範囲にある。

実行:

```text
gofmt -w sparseassoc/sparseassoc.go suiassocprovider/provider.go suiassocprovider/provider_test.go
go test ./...
```

結果:

```text
?    github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/sparseassoc         [no test files]
ok   github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/suiassocprovider   0.004s
```

ローカル再現版で確認したadapter境界:

- formal responseから内部similarity等が漏れない
- candidateはanchorを含まない
- Provider内部順位ではなくstable ref順で返す
- explainableなchannel provenanceだけを返す
- high thresholdでは空candidate + abstainになる
- JSON requestはclosed-world
- items / anchors / candidateLimitの上限をfail-closedする
- duplicate item / scope外anchorを拒否する
- requestを変更しない
- unsupported schema / intentを拒否する
- provider/version traceを明示する

この結果は**full checkout testでも、branch上のexact source testでもない**。current-mainから取得したSACS sourceと、今回adapterの契約ロジックを同じ境界で再現したコードが手元のGo環境で実行可能だったことを示す限定的なExecutable Evidenceである。branch上のexact sourceによる検証は、repository checkoutが可能な環境で改めて行う余地を残す。

## 5. このEvidenceが意味しないこと

この結果は、親和図法で要求する深層意味近接の品質を証明しない。

また、次も未検証である。

- SUI Sensemaking実カードでのcandidate recall
- high lexical similarity / deep semantic mismatchの識別
- static semantic adapterを追加した場合の品質とmemory
- Model2Vec / fastText / local sentence encoderとの比較
- 10万〜100万件規模でANN indexが必要になる境界
- SUIへの実transportを含むend-to-end latency
- full repository checkout上での今回adapter test
- branch上のexact adapter sourceの実行
- production runtimeとしての採用可否
- Operational / Adoption / Outcome Evidence

SUI Sensemaking側のCOGNITIVE-ASSOC-01では、事前登録済みhuman adjudicationが完了するまでsemantic resultを生成しない。このadapterの存在を理由に、そのgateを開かない。
