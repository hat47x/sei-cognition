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

## 4. このEvidenceが意味しないこと

この結果は、親和図法で要求する深層意味近接の品質を証明しない。

また、次も未検証である。

- SUI Sensemaking実カードでのcandidate recall
- high lexical similarity / deep semantic mismatchの識別
- static semantic adapterを追加した場合の品質とmemory
- Model2Vec / fastText / local sentence encoderとの比較
- 10万〜100万件規模でANN indexが必要になる境界
- SUIへのin-process統合時のend-to-end latency
- production runtimeとしての採用可否
- Operational / Adoption / Outcome Evidence

SUI Sensemaking側のCOGNITIVE-ASSOC-01では、事前登録済みhuman adjudicationが完了するまでsemantic resultを生成しない。このprototypeの存在を理由に、そのgateを開かない。
