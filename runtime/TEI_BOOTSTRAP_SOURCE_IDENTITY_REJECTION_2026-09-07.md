# TEI bootstrap source identity rejection — 2026-09-07

## 位置づけ

current execution containerにはprivate GitHub credentialを渡せず、container自身のGitHub network accessも利用できないため、fixed revision B `1a7028d444fcae60a1c4f2f2d247456f4c7c35be` に存在する `bootstrap/final-source` をGitHub connector経由でbyte transportできるかを追加確認しました。

これはcanonical Git Data API acquisition (`prepare_tei_revision_b_source.py`) の代替をUniversal Contractへ昇格させる作業ではありません。actual E2を始める前にsource identityへ戻る補助的な取得実験です。

## 観測

`bootstrap/final-source` tree `36270e38c6f6256ec9fc3ad4bffedb8deee20b22` の `0000`〜`0061`、62 blobを取得し、各chunkをlocal `git hash-object`でGitHub connectorが返したblob SHAへ再照合しました。

```text
chunk count       = 62
chunk mismatch    = 0
concatenated size = 176908 bytes
```

連結payloadはstrict Base64 decodeに成功し、XZ magic `fd377a585a00` を持つ132680-byte streamになりました。XZ展開にも成功し、993280-byte tarを得ました。tarにはabsolute / `..` traversal path、symlink / hardlink、device entryはありませんでした。

したがって、ここまでで言えるのは **bootstrap payloadのbyte transport integrityが成立した** ことです。

## fixed revision B source identityとの照合

しかし、展開sourceをfixed revision B execution boundaryへ戻すと一致しませんでした。

| 対象 | bootstrap payload | fixed revision B | 結果 |
|---|---|---|---|
| `go.mod` blob | `8a50045ffbefd897fddf9b729bbda3b9c16ffadb` | `f8763f8fb2d64d73f1b40b905f62b5e09c44493b` | mismatch |
| `cmd/tei/main.go` blob | `233be1fdb0b4ff6118cb5501ed23ee832e603cff` | `6a27b98b7f6dbe4e66d1261edfc847402cd608a5` | mismatch |
| `cmd` tree | `696368eb0e57abbd575a6c7031924d0131878f26` | `ac4d4406dfa590a2078cf91217c4fe30797e7f8e` | mismatch |
| `internal` tree | `837d498e98f85918319bfdcc48108331edf2ca30` | `10d2bfea4932c308fa6537e3b081bc6ea5501205` | mismatch |
| `reference` tree | `25470d5b68b9e274b71a4cabc85e031f72cd3ad8` | `57fafb742988ecb936b9ab261fa8a991e37ed5c7` | mismatch |
| `go.sum` | absent | required blob `c7cd1478…` | mismatch |
| `cmd/tei/source_index.go` | absent | required blob `19ac0589…` | mismatch |
| `cmd/tei/validation_output.go` | absent | required blob `2ca74659…` | mismatch |

展開された`go.mod`も次のhistorical formでした。

```text
module tei

go 1.23.2
```

revision B repository内の `bootstrap/direct-tree-method.txt` には、source normalizationをdirect Git tree content constructionへ切り替える旨が残っています。このため`bootstrap/final-source`をcurrent exact-B execution sourceとして扱う根拠はありません。

## 判定

このpayloadは **actual revision B inputとしてreject** します。

```text
bootstrap byte transport PASS
  != bootstrap payload is revision B
  != exact revision B source acquired
  != revision B build PASS
  != Provider Plan execution PASS
  != SOZA Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

canonical Git Data API acquisition、self-contained local Git object databaseからのexact-B checkout、およびそれらからcanonical source verifierへ戻る既存経路の位置づけは変更しません。

machine-readable observation:

`runtime/evidence/tei-bootstrap-source-identity-rejection-20260907/observation.json`
