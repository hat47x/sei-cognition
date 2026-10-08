# ISSUE #660 Epistemic Routing Evaluation

このディレクトリは、TEI #958 / PR #961で検討している文脈付きepistemic projectionを、SEI Cognitionが**意味を複製せずにconsumerとして利用できるか**を確認するevaluation-only Referenceです。

## 境界

SEIはTEIの確認状態、文脈判定、target binding、Health計算を再実装しません。入力はTEI Projectionであり、SEIは認知処理へ渡す直前のroutingだけを担当します。

Projectionの意味契約 `tei.epistemic-projection/v0` とJSON表現 `tei.reference.epistemic-assessment/v0` は別に確認します。意味契約が未知ならschemaが同じでも拒否し、意味契約が既知でもschemaが未対応ならdecoder未対応として拒否します。

出力laneは次の4種類です。

```text
premise
candidate
review
blocked
```

TEIが`premise`と返しても、consumer境界で次が見つかればfail closedします。

- metadataがpartial / absent
- targetがambiguous / detached
- contextがunknown / incompatible
- lifecycleがactiveではない
- confirmationがrejected
- assertion freshnessがstale / not-yet-valid
- Conflictがpresent

`reanchored`はpremiseとして利用できる場合がありますが、semantic identityを証明したことにはせず、別signalとして残します。

## Health / coverage

TEI Healthの`viewMetadataState`がpartialなら、SEIはproject-wide Healthとして扱いません。

coverage gapはretrieval missとは別のUnknownです。「検索で見つからなかった」のではなく、「状態を把握すべき領域に十分なepistemic mappingが無い」可能性を表します。high / critical gapはreview escalationへ渡します。

consumer-specific freshnessもassertion本体のconfirmationとは分けます。あるassertionが通常premiseでも、高い鮮度を要求するconsumerでstaleなら、そのconsumer向けのescalationを返します。assertion自体をfalse / rejectedへ変更しません。

## Fixture

`epistemic_projection_fixture_v0.json`はTEI PR #961のProjection field shapeを固定したevaluation fixtureです。TEIのCanonical authorityではありません。Source snapshotとschemaを明示し、contract driftを検出できるようにしています。

## 実行

```bash
python -m unittest evaluation/tei-reference-adoption/test_epistemic_routing.py
python evaluation/tei-reference-adoption/epistemic_routing.py \
  evaluation/tei-reference-adoption/epistemic_projection_fixture_v0.json
```

CLIはraw TEI Projectionと、このevaluation fixtureのような`{"projection": ...}` wrapperの両方を受け取ります。

## Authority stop line

このReferenceは次を行いません。

- TEI Projectionを客観的Truthへ昇格する
- semantic similarity / retrieval confidenceからconfirmationを作る
- reanchored targetを意味同一と断定する
- partial Healthをproject全体へ一般化する
- reviewer候補をDecision / Authorityへ昇格する
- TEIのepistemic modelをSEI固有正本として複製する

Issue: #660
Cross-repo parent: hat47x/tei-platform#958
