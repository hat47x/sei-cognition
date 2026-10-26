# コントリビューション

SEI Cognitionは初期開発中です。変更は小さく、意味・来歴・未決の区別を保って送ってください。

## 進め方

1. 既存のIssue、Contract、Architecture、Decision Memoryを確認する。
2. 変更の目的、境界、未検証事項をIssueまたはPR本文へ書く。
3. 最新の`main`から短命ブランチを作る。
4. 変更に対応するtestを追加・更新する。
5. CIを確認してからPRを統合する。

## 禁止事項

- 実在の顧客情報、個人情報、認証情報、非公開の判断記録をコミットしない。
- 非公開リソースの内容を、この公開リポジトリへ複製しない。
- AIの提案を、人間の承認・公開権限・Authorityとして扱わない。
- 合成fixtureの成功を、実運用での意味の受理として主張しない。

## 検証

- Go: `go test ./... -count=1`
- Python: 対象の`unittest`を実行する。
- Contract変更は、`contracts/`・`schemas/`・fixture・testを同時に更新する。
- CI: `.github/workflows/`の対象workflow。

## 文書

- 日本語を基本とし、Contract ID・API名・コマンドは原表記を保つ。
- 意味、規範強度、Evidence強度を混ぜない。
- 実データを使わず、合成fixtureで再現できる形にする。

## ライセンス

貢献はMITライセンスの下で受け入れます。詳細は[LICENSE](LICENSE)を参照してください。
