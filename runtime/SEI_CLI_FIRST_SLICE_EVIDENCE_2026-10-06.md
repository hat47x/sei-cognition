# sei CLI 最小版 Evidence

更新日: 2026-10-08  
状態: **Scoped Executable Evidence。Go 1.25.14で`runtime/go`全体のtestがPASS。導入容易性のEvidenceではない**  
関連: **ISSUE-000084 / ADR-0033 / ADR-0034**

## 1. この文書の役割

利用者が直接使うGo製のCLI `sei` の最小版について、何を実装し、何を実行して確かめ、何をまだ確かめていないかを記録します。

2026-10-08に、並列のレビュー(正しさ、ガバナンスの不変条件、文書の主張の3観点)で見つかった指摘を、コードで裏付けて修正しました。修正の内容は§4に分けて記録します。

## 2. 実装したもの

- `runtime/go/seicli`: コマンドの実装。
- `runtime/go/cmd/sei`: 実行可能バイナリの入口と、利用者向けの`QUICKSTART.md`。
- `tools/build_sei.sh`: Linux、macOS、Windows向けの単体バイナリと`SHA256SUMS`を作る開発用script。
- `evaluation/adoption-first-contact/E84_1_OBSERVATION_PROTOCOL.md`: 導入の観測手順(観測は未実施)。

新しいContractは作っていません。記録は既存のDecision Memory Contractで書き、既存のSemantic Interchangeの封筒に入れます。

| コマンド | 内容 |
|---|---|
| `sei init` | 空の記録storeを作る。既存のstoreは上書きしない。storeのロックを取って作る |
| `sei add recommendation` | Recommendationを追記する。`--source`で出所を残せる(任意) |
| `sei add decision` | Decisionを追記する。`--recommendation`は、storeに記録済みのRecommendationだけを受け付ける。`--unresolved`で未解決を、`--responsible`で責任の参照を残す |
| `sei resume` | storeだけから、Decision、未解決、Recommendationの状況を示す。`--json`で機械可読にする。空の区間は`[]`で出す |
| `sei verify` | 書き出されたbundleを、storeなしで検証する |
| `sei export` | storeを可搬なbundleとして書き出す。既存のファイルは上書きしない |
| `sei gate check` | 記録済みのDecisionが方針を満たすかを、実行の前に確認する。判断の記録(bundle)は変更せず、実行もしない。確認のたびに運用ログ`gate-checks.jsonl`へ追記する |
| `sei mcp` | MCP(stdio)のserverとして、`resume`、`add_recommendation`、`check_decision`をAIツールへ渡す。`--allow-decision`を付けた場合だけ`add_decision`も渡す |
| `sei doctor` | 読み取り専用で自己診断する。バイナリの版とハッシュ、データ置き場への書き込み、記録の検証、残っているロック、ゲートログの書き込み、絶対パスのMCP設定を示す。`fail`があれば終了コード1。ロックは消さない |
| `sei version` | build情報を示す |

守っている性質は次のとおりです。

- 追記のみである。既存のrecordは書き換えず、同じIDの追加は失敗する。拒否されたコマンドがstoreを変えない。
- 同じstoreへの同時の`init`と`add`は、ロックファイル`store.lock`で直列化する。ロックが取れない場合は、待ったうえで失敗し、ロックを勝手に壊さない。
- Recommendationは、storeに記録済みのDecisionが依拠として名指したときだけ「依拠された」と報告する。Recommendationだけでは決定とみなさない。
- 未解決は、Decisionが残した時点のまま未解決として報告する。
- 未知のContractのrecordは、そのまま保持し、`not_verified`として報告する。
- MCPの引数は、型・空値・未知のキーをすべて検査し、合わなければエラーにする。黙って捨てない。
- MCPの記録の出所は、initializeで接続したクライアントの名前である。呼び出し側は別の名前を指定できない。

`sei mcp`は、Integration Surfaceのprofileであり、Contractでも、Stable Requirementでもありません。`sei gate check`は、新しい記録型や新しいContractを作らず、既存のDecision Memoryの読み取りとして実装しています。Action Intentそのものを記録する型は存在せず、確認の結果は判断の記録ではなく運用ログに残ります(ADR-0034)。

## 3. 確かめたこと

### 3.1 Go 1.25.14で`runtime/go`全体

WSL2のUbuntu上で、公式配布のGo 1.25.14(`go1.25.14.linux-amd64.tar.gz`、59,909,419 bytes、SHA-256 `a21ae563…e7712`)を用い、`go.mod`を変えずに次を`-count=1`で実行しました。

- `go test ./...`: `runtime/go`の全14パッケージがPASS。`seicli`のパッケージは30件のtestで構成される(`doctor`の6件を含む)。
- `go vet ./...`: 指摘なし。
- `gofmt -l`(`seicli`、`cmd/sei`): 指摘なし。

`seicli`の30件の内訳は次のとおりです。`doctor_test.go`の6件は、後から追加したもので、§3.5の確認と対応します。

| ファイル | 件数 | 内容 |
|---|---|---|
| `seicli_test.go` | 5 | 最初の決定の記録と再開、追記のみ、未知のContractの保持、不正な入力の拒否、不正なbundleの拒否 |
| `gate_test.go` | 6 | 方針を満たす決定の許可と`not_verified`、拒否の終了コードと理由、未解決の既定の扱い、確認できない場合の終了コード1、運用ログへの追記とbundleの不変、ログに書けない場合の拒否 |
| `mcp_test.go` | 5 | 既定で渡す操作の範囲、Recommendationの出所、`responsible`の必須化、拒否を判定結果として返す、未知のmethodと不正なJSON |
| `doctor_test.go` | 6 | 未初期化のディレクトリは警告で、終了コードは0、ディレクトリを作らない。健全なstoreは`ok`で、MCP設定に絶対パスが入る。ロックは警告で、消さない。不正なstoreは失敗で終了コード1。データ置き場がファイルなら失敗。ゲートログに書けない場合は失敗 |
| `hardening_test.go` | 8 | 同時追記で記録が消えない、ロックの待ち時間切れで他人のロックを消さない、未記録のRecommendationへの依拠の拒否、ゲートが存在しない推薦を依拠と数えない、exportが既存ファイルを上書きしない、resume --jsonの空配列、MCPが扱えない引数を拒否する、MCPの出所がクライアント名である |

### 3.2 修正の確認(実プロセス)

修正版のLinuxバイナリで、20個の`sei add`を同時に走らせ、それを5回繰り返しました。

- 修正後: 5回とも20件すべてが残り、失敗は0、ロックファイルは残らなかった。
- 修正前: 同じ条件で、レビューの再現では5回中5回、残ったのは1件でした。コマンドは20件とも成功を返していました。

修正版のWindowsバイナリを公式のMCP Inspector(`@modelcontextprotocol/inspector` 2.9.0、CLI mode)に接続して確認しました。

- `add_recommendation`は、`source`を渡さなくても記録され、出所はクライアント名(`inspector-cli`)になった。
- `add_recommendation`に`source`を渡すと、「引数を受け付けない」というエラーで拒否された。
- `check_decision`は、存在しない決定に対して拒否の判定を返した。

### 3.3 Windows実機

修正版の`sei.exe`を、Windows 11上で、`sei`だけをPATHに置いた新しいディレクトリから順に実行しました(2026-10-08)。

- `init`、推薦2件、決定1件、`resume`、`verify`、`gate check`(終了コード0)が期待どおりに動き、`gate-checks.jsonl`に確認の記録が1行残った。
- 記録されていない推薦(`R-nope`)を依拠した決定は、拒否された(終了コード1)。
- `export`は、既存の`decisions.json`を上書きせず、二回目は拒否された(終了コード1)。

検証に使ったバイナリのSHA-256は次のとおりです。

- `sei.exe`(Windows、amd64): `3dd1e19da8242b6374d3a8ee5bde3f09e592ac0bbfbbf0d512954e54402e403c`
- `sei-linux`(WSL2、amd64): `08d6d6c5cee50c7973d589175cceeac3408c36aa1b22f9dc9b9fd51298b479e3`

注意: `sei version`の`commit`は、ビルド時のgit HEAD(`0a52e4f`)です。作業ツリーに未コミットの変更がある状態で作ったバイナリでは、この値は変更内容を表しません。バイナリの同一性は、このハッシュで確かめてください。

### 3.4 レビューと修正

並列のレビューは、3人の検査者と、指摘ごとの2人の反証者で行いました。反証で覆った指摘はありませんでした。ただし、検証は上位3件(重大度の高い順)に限られ、残りは作者がコードを読んで確かめました。

| 指摘 | 重大度 | 対応 |
|---|---|---|
| 同時の`add`と`init`で、記録が黙って消える | high | `store.lock`で直列化した。20並列の再現で修正を確認 |
| MCPの引数の型違いが黙って捨てられ、`check_decision`が拒否すべき判定を許可しうる | high | 型・空値・未知のキーを検査し、合わなければエラーにした |
| `add decision`が、存在しない推薦を依拠と記録できる | high | storeに記録済みの推薦だけを受け付けるようにした。`--require-recommendation`を付けたゲートは、記録された推薦を1件も依拠していない決定を拒否する |
| `export`が既存のファイルを上書きする | high | `O_EXCL`で、既存のファイルを上書きしないようにした |
| `build_sei.sh`の相対パスの出力先で、バイナリとSHA256SUMSの場所がずれる | high | 出力先を絶対パスに解決した(文書の修正と併せて、script自体の確認が必要) |
| MCPの出所を、呼び出し側が指定できる | medium | `source`引数を廃止し、クライアント名だけを出所にした |
| MCPの責任者の空値が、名指しされたものとして通る | medium | 空値を拒否した |
| `resume --json`の空の区間が`null`になる | low | `[]`にした |
| `gate check`を「読み取り専用」と書いていたが、ログに追記する | low | 文書を修正し、ログへの追記を明記した |
| QUICKSTARTの`claude mcp add`を、検証済みのように書いていた | medium | 未検証と明記した(文書の修正) |
| 「AIツールが書いたすべての記録に出所が残る」と書いていた | medium | MCP経由の記録だけだと限定した |

### 3.5 sei doctor(実バイナリでの4場面)

`tools/build_sei.sh`を経由せず、`CGO_ENABLED=0 go build -trimpath`で作ったLinuxバイナリ(版とcommitは注入していないので`dev`と`unknown`と表示される)で、次を確かめました(2026-10-08)。

- 空のディレクトリ: データ置き場が無いという警告だけで、終了コード0。ディレクトリは作られない。
- 初期化して推薦を1件記録した後: 全項目が`ok`で、終了コード0。storeは1件、検証済み1件。
- ロックファイルを手で置いた場合: `lock`が`warn`になり、終了コード0。ロックファイルは消されない。
- 不正なstoreの場合: `store`が`fail`になり、終了コード1。

この確認に使ったバイナリのSHA-256は`a4aedca6…d28a074`です。配布用のバイナリとは別のものです。

なお、この確認の途中で、WSL上の`go build`が240秒を超えて止まりました。`-x`を付けて時間制限を延ばすと、378秒で完了しました。原因の特定は行っていません。

## 4. まだ確かめていないこと

```text
runtime/go test PASS
  != 導入容易性(E-84.1)
  != Decision Gateway
  != Authorityの確認
  != Adoption / Outcome Evidence
```

- 空の端末で、作者の補助なしに導入できるか(E-84.1)は未観測です。このbuildと実行は作者の環境で行いました。
- Claude Code、Claude Desktop等の、実際のAIツールからの接続は未確認です。`claude mcp add`の構文は、この環境では実行していません。
- 確認の結果は、運用ログ`gate-checks.jsonl`に追記されるだけで、判断の記録の一部ではなく、`sei export`にも含まれません。ログは改ざんを検出できません。
- 確認が見るのは、決定が記録され、方針を満たすことだけです。責任を持つ人がAuthorityを持つこと、行為が決定の範囲に収まることは確認していません。
- `sei add decision`をシェルから直接実行すると、ゲートも`responsible`の必須化も掛かりません。既定の制限は、`sei mcp`が渡すツールにだけ働きます。
- 既定の方針では、未解決の問いが残った決定も許可されます(未解決は既定では拒否の理由にしない)。拒否するには`--deny-unresolved`を付けます。
- 記録の書き込みのたびに、bundle全体を書き直します。書き直しで、数値の表現が変わりうることを確認していません。手で編集するのは、`sei`を動かしていないときに限ります。
- ロックは、異常終了で残ることがあります。その場合は、ロックの説明に従い、`sei`が動いていないことを確かめてから手で消す必要があります。
- Linux(WSL2)とWindowsの実行は確認しました。macOS向けとlinux/arm64向けのバイナリは、ビルドできただけで、実行は確認していません。
- 並列の検証で、上位3件を超える指摘は、作者がコードを読んで確かめたもので、2人の反証者による検証を受けていません。

## 5. Natural Japanese review

修正の前後で、何を確かめ、何を確かめていないかを分けて書いた。Go 1.25.14の実行結果、実プロセスの同時書き込みの結果、Windowsでの実行結果、MCP Inspectorの結果を、それぞれの範囲のまま記した。導入容易性、Authorityの確認、実AIツールとの接続は、確認していないものとして残した。
