# SEI Local Reference Package

このpackageは、SEIのLocal Single-Node Packaging / Deployment境界を実行可能に検証するための**reference distribution artifact**です。

現時点ではLinux / amd64を対象とし、Product Releaseや恒久的なplatform supportを意味しません。人間やAIが判断仕事を行うための正式なProduct Interaction CLIでもありません。

## 含まれるもの

- `soza-local-reference` — package lifecycleの検証用binary
- `build-metadata.json` — artifactのbuild identity
- このREADME

binaryには次の管理操作があります。

- `version` — build version、commit、targetをJSONで表示します。
- `save --data-root <dir> --input <file>` — Semantic Interchangeを検証し、local durable data rootへ保存します。
- `inspect --data-root <dir>` — 保存済みbundleを読み直し、current runtimeで再構成できたrecord数をJSONで表示します。

`save`と`inspect`はPackaging acceptanceのための管理入口です。これらをSEIの正式なhuman-facing / AI-facing Product Interaction Surfaceとして扱いません。

## semantic dataとの境界

実行binary、archive名、filesystem pathはcanonical semantic identityではありません。

```text
distribution artifact
  != canonical semantic data
  != Semantic Contract identity
```

耐久的意味のportable境界にはcurrent Semantic Interchangeを用います。runtimeが理解していないnested Contractを保持できても、その意味をvalidatedしたとはみなしません。

## Evidence境界

このreference artifactをCIでbuild・展開・起動し、save process終了後に別processからreloadできた場合でも、確認できるのは限定されたExecutable Evidenceです。

```text
reference artifact PASS
  != Product Release
  != production support matrix
  != version upgrade compatibility proven
  != crash durability proven
  != Operational / Adoption Evidence
```

正式な配布範囲、security、code signing、installer、auto-update、Product Interaction Surface等は後続の設計・実証で扱います。

## 文書品質

Product Packaging baseline、ADR-0029、ISSUE-000055のEvidence境界を照合し、reference artifactとProduct Release、package lifecycle controlとProduct Interaction、artifact identityとsemantic identityを混同しない形で整理しました。そのうえで、意味と未検証範囲を変えず、自然な日本語となることを最重要視して全文をドラフトし、最終意味監査を実施済みです。