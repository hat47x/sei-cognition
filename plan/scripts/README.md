# `plan/scripts/` — planning管理補助

更新日: 2026-08-31  
状態: **Current Planning Tooling Baseline**

## 1. 役割

このディレクトリには、ADR / Issue / `plan/registry.yaml`の管理を補助する小さな検査・採番ツールを置きます。

ここにあるツールはPlanning文書の意味上の正本ではありません。正本は各ADR / Issue本文と、台帳としての`plan/registry.yaml`です。ツールは、それらの間に起きやすい機械的な不整合を早く検出するために使います。

## 2. Registry integrity check

```bash
python3 plan/scripts/check_plan_registry.py
```

主に次を確認します。

- ADR IDが4桁、Issue IDが6桁であること。
- registry内でIDやfile pathが重複していないこと。
- actual `plan/adr` / `plan/issue`の全ファイルがregistryへ収載されていること。
- registryが存在しないファイルを参照していないこと。
- filename、本文見出し、registry IDが一致していること。
- 本文Statusとregistry Statusが一致していること。
- Statusが`plan/README.md`で定めた規定値であること。
- `related_issues` / `related_adrs`に記載したIDがactual registryに存在すること。

ADR側とIssue側の関連配列が完全に対称であることまでは要求しません。両者は関連を記録する観点が異なる場合があるためです。必要なのは、記載した参照が存在し、意味上の正本と矛盾していないことです。

## 3. 次番号の候補

```bash
python3 plan/scripts/next_plan_id.py
python3 plan/scripts/next_plan_id.py adr
python3 plan/scripts/next_plan_id.py issue
```

actual treeの最大番号から、次の候補IDを表示します。

重要な点として、このコマンドは**番号を予約しません**。複数branchや複数作業者が同時に実行すれば、同じ候補番号を得ることがあります。

そのため、新しいADR / Issueを作るときは次の順序を基本とします。

1. 最新の`develop/vX.Y.Z`を基準にする。
2. `next_plan_id.py`で候補番号を確認する。
3. 文書とregistryを同じ変更単位で作成する。
4. PR作成前に最新developとの比較を確認する。
5. `check_plan_registry.py`を通す。
6. merge直前にも、並行変更で同一IDが追加されていないことを確認する。

番号競合が起きた場合は、恒久IDの意味を後から入れ替えません。どちらを維持するかを成立順序と意味上の連続性から判断し、必要なら後発側を別IDへ移すか、内容が重複していれば統合します。

## 4. Evidence境界

このcheckerがPASSすることは、Planning metadataの構造整合を示すだけです。

```text
Plan integrity PASS
  != Product Value satisfied
  != Architecture correct
  != Implementation conforms
  != Release ready
  != Operational effectiveness
```

機械的整合を意味上の妥当性や実装Evidenceへ昇格させません。

## 5. 自然な日本語ドラフト

採番競合の実例と既存Planning規約へ戻って役割を整理した後、ツールの保証範囲を過大にしないよう留保を明示し、自然な日本語となることを最重要視して全文を再ドラフトしました。最終意味監査も実施済みです。
