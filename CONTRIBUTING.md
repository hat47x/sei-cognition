# コントリビューション

SEI Cognitionは初期開発中です。変更は小さく、意味・来歴・未決の区別を保って送ってください。

## 進め方

1. 既存のIssue、Contract、Architecture、Decision Memoryを確認する。
2. 変更の目的、境界、未検証事項をIssueまたはPR本文へ書く。
3. 最新の`main`から短命ブランチを作る。
4. 変更に対応するtestを追加・更新する。
5. 変更範囲に応じた検査をローカルで実行し、結果をPR本文へ書いてから統合する。

## 禁止事項

- 実在の顧客情報、個人情報、認証情報、非公開の判断記録をコミットしない。
- 非公開リソースの内容を、この公開リポジトリへ複製しない。
- AIの提案を、人間の承認・公開権限・Authorityとして扱わない。
- 合成fixtureの成功を、実運用での意味の受理として主張しない。

## 検証

GitHub Actionsは当面停止しており、`.github/workflows`はありません。検査は変更範囲に応じてローカルで実行します。方針は[開発ワークフロー](plan/DEVELOPMENT_WORKFLOW.md)の「GitHub Actionsの当面停止方針」にあります。

- Go: `runtime/go`で`go test ./... -count=1`を実行する。
- Python: 変更した対象の`unittest`を実行する（例: `python -m unittest discover -s tools -p "test_*.py"`）。
- Contract変更は、`contracts/`・`schemas/`・fixture・testを同時に更新し、次の2つの検査を実行する。
  - `python tools/check_contract_conformance.py`: Contractのschemaとfixtureの整合を検査する。`jsonschema`と`referencing`が必要で、未導入なら「jsonschema and referencing are required」と表示して終了する。仮想環境を作り、`pip install -r tools/contract-check-requirements.txt`で入れる。
  - `python tools/check_representation_profiles.py`: Representation ProfileのDefinitionと固定fixtureを検査する。追加の依存はない。
  - どちらも、PASSが示すのはリポジトリ内のschemaとfixtureの整合までである。出力の`claims`のとおり、`release`・`operational`・`adoption_outcome`は`false`で、実運用での意味の受理やリリース可否は示さない。
- 文書: 変更した現行Markdownについて`plan/scripts/check_document_review_registry.py`を確認する。

実行した検査、実行できなかった検査、その理由をPR本文に分けて書いてください。GitHub Actionsのstatusがないことは、PASSでもfailureでもありません。

## 文書

- 日本語を基本とし、Contract ID・API名・コマンドは原表記を保つ。
- 意味、規範強度、Evidence強度を混ぜない。
- 実データを使わず、合成fixtureで再現できる形にする。

## ライセンス

貢献はMITライセンスの下で受け入れます。詳細は[LICENSE](LICENSE)を参照してください。
