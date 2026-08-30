# `plan/scripts/` 管理補助

更新日: 2026-08-31

`plan/scripts/`には、ADR / Issueの採番やregistry整合を再現可能にするための小さな管理補助を置きます。

これらのスクリプトはProduct ValueやADR本文の意味を決定しません。人間が行った判断を、番号・Status・台帳不整合によって壊さないための機械的な検査に限定します。

## `check_plan_registry.py`

次を検査します。

- ADRが4桁、Issueが6桁で採番されているか。
- `plan/adr` / `plan/issue`のactual fileがregistryへ全件登録されているか。
- registryが存在しないファイルを参照していないか。
- 本文H1のIDとregistry IDが一致しているか。
- 本文Statusとregistry Statusが一致しているか。
- Statusが`plan/README.md`の規定値に収まっているか。
- related Issue / ADRが実在するか。
- registry上のADR↔Issue関連が双方向に一致しているか。

実行:

```bash
python3 plan/scripts/check_plan_registry.py
```

PASSはplanning metadataの整合だけを示します。ADR Decisionの妥当性、Product Value coverage、実装完成、operational evidenceを証明しません。

## `next_plan_id.py`

actual treeから現在の最大番号を読み、次のIDを表示します。

```bash
python3 plan/scripts/next_plan_id.py adr
python3 plan/scripts/next_plan_id.py issue
```

現在の採番規則:

```text
ADR-0001 ... ADR-9999
ISSUE-000001 ... ISSUE-999999
```

採番補助は並行branch間の競合を完全には防ぎません。merge前に`check_plan_registry.py`を再実行し、必要なら後発側を採番し直します。

## 依存関係

Python標準ライブラリだけで動作することを原則とします。

`registry.yaml`も現在の制約された書式を外部YAML libraryなしで読みます。registryの構造を変更する場合は、管理スクリプトとCIを同じ変更単位で更新します。

## 非責務

管理スクリプトへProduct ontologyや設計判断を埋め込みません。

たとえば、Priority、Resolved件数、ADR件数等からProduct Valueの達成度やrelease可否を自動推定する規則は追加しません。

```text
Planning metadata consistency != Product Value realization
```

## 自然な日本語ドラフト

管理スクリプトの責務と非責務を整理した後、技術的意味を変えず、自然な日本語となることを最重要視して全文をドラフトし、最終意味監査を実施しています。
