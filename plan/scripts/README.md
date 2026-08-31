# `plan/scripts/` — planning管理補助

更新日: 2026-08-31  
状態: **Current Planning Tooling Baseline**

## 1. 役割

このディレクトリには、ADR / Issue / `plan/registry.yaml`の管理を補助する小さな検査・採番ツールを置きます。

ツールはPlanning文書の意味上の正本ではありません。判断理由は各ADR / Issue本文を正とし、`plan/registry.yaml`は状態と関連を管理する台帳です。checkerは、それらの間に起きやすい機械的な不整合を早く検出します。

文書の自然な日本語監査は`plan/document_review_registry.yaml`で管理します。現時点ではこの文書監査台帳そのものを`check_plan_registry.py`の検査対象へ混ぜず、ADR / Issue registry integrityとは別責務として扱います。

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

ADR側とIssue側の関連配列が完全に対称であることまでは要求しません。両者は関連を記録する観点が異なる場合があるためです。

## 3. 次番号の候補

```bash
python3 plan/scripts/next_plan_id.py
python3 plan/scripts/next_plan_id.py adr
python3 plan/scripts/next_plan_id.py issue
```

actual treeの最大番号から次の候補IDを表示します。

このコマンドは**番号を予約しません**。複数branchや複数作業者が同時に実行すれば、同じ候補番号を得ることがあります。

新しいADR / Issueを作るときは次を基本とします。

1. 最新の`develop/vX.Y.Z`を基準にする。
2. `next_plan_id.py`で候補番号を確認する。
3. 文書とregistryを同じ変更単位で作成する。
4. 最新developとの競合を確認する。
5. `check_plan_registry.py`を通す。
6. merge直前にも同一IDが追加されていないことを確認する。

番号競合が起きた場合は、恒久IDの意味を後から入れ替えません。成立順序と意味上の連続性からどちらを維持するか判断し、必要なら後発側を別IDへ移すか、重複内容を統合します。

## 4. Evidence境界

このcheckerがPASSすることはPlanning metadataの構造整合を示すだけです。

```text
Plan integrity PASS
  != Product Value satisfied
  != Architecture correct
  != Implementation conforms
  != Release ready
  != Operational effectiveness
  != Adoption / Outcome demonstrated
```

機械的整合を意味上の妥当性、実装Evidence、利用者価値へ昇格させません。

## 5. CI failure

Plan integrityが失敗した場合は、Status、registry、file path、関連ID等のどの不整合を検出したかを確認し、失敗を残したまま後続作業へ進みません。

本文を正しく更新した直後にregistryだけが旧Statusのまま残った場合も、単なるCIノイズとして無視せず同じ作業単位で同期します。

## 6. Natural Japanese review

current Planning規約、5段階Evidence、実際に発生した本文 / registry一時不整合、document review registryの責務へ戻って説明を整理した。その後、checkerの保証範囲を過大にせず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
