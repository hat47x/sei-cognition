# セキュリティポリシー

SEI Cognitionは初期開発中です。本番利用向けのサポート済みバージョンはまだありません。

## 脆弱性の報告

セキュリティ上の問題は、**公開Issueを作らず**、GitHubのPrivate vulnerability reportingから報告してください。

- リポジトリの「Security」タブ → 「Report a vulnerability」
- 対象のcommit、再現手順、影響、想定する攻撃条件を含めてください。
- 実在の顧客情報・個人情報・認証情報・非公開の判断記録を添付しないでください。合成fixtureで再現できる形に置き換えてください。

初期開発中のため、応答時間や修正期限は保証しません。

## 対象

- `runtime/`のGo実装、`contracts/`のSemantic Contract、`schemas/`の表現形式。
- Decision Memory、Provenance、Semantic Lineage、Capability Observationの境界。
- `evaluation/`の検証コードとfixture。

## 対象外

- 本リポジトリが提供していない本番運用環境。
- 第三者依存ライブラリの脆弱性。上流へ報告してください。
- 実在の組織・権限・業務判断の問題。

## 安全境界

- SEIは意味・来歴・未決を保持しますが、実在の決定・Authority・公開可否をこのリポジトリで保証しません。
- AIの提案を、人間の承認や実行許可として扱いません。
- 非公開リソースの内容は、このリポジトリへ複製しません。
