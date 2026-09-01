# `plan/scripts/` — planning管理補助

更新日: 2026-09-01  
状態: **Current Planning Tooling Baseline**

## 1. 役割

このディレクトリには、SOZAのPlanning運用で起きやすい機械的な不整合を早く検出するための、小さな検査・採番ツールを置きます。

ツールはPlanning文書や開発文書の意味上の正本ではありません。判断理由は各ADR / Issue本文を正とし、`plan/registry.yaml`は状態と関連を管理する台帳です。自然な日本語監査の状態は`plan/document_review_registry.yaml`で管理します。

checkerは、これらの意味を評価するのではなく、actual treeと台帳の間に生じる機械的な取りこぼしを検出します。

## 2. ADR / Issue registry integrity

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

## 3. Document Review Registry coverage

```bash
python3 plan/scripts/check_document_review_registry.py
```

このcheckerは、ISSUE-000015で確立した自然な日本語監査の運用が、新しいMarkdown文書の追加後も台帳から抜け落ちないことを確認します。

主に次を確認します。

- actual tree上の`*.md`が、`plan/document_review_registry.yaml`のreviewed scopeまたは明示的なMarkdown exclusionに含まれること。
- `pending: []`であること。
- reviewed scopeのstatusが規定値であること。
- reviewed scopeがactual Markdownへ少なくとも1件一致すること。
- reviewed scopeの重複がないこと。

self-testは次で実行します。

```bash
python3 -m unittest plan/scripts/test_check_document_review_registry.py
```

self-testには、正常系に加えて少なくとも次のnegative caseを含めます。

- 未登録Markdownを追加するとFAILする。
- `pending`を残すとFAILする。
- actual treeへ一致しないstale reviewed scopeを残すとFAILする。

`reviewed-no-change`は正当な監査完了状態です。KJの生カードや原記録など、現在の結論へ合わせて書き換えるべきでない文書を、checkerが再ドラフトへ強制することはありません。

## 4. 次番号の候補

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

## 5. CIでの実行

`.github/workflows/plan-integrity.yml`では、ADR / Issue / registryの変更だけでなく、Markdown文書の変更でもPlanning integrityを実行します。

これにより、たとえば`product/`や`architecture/`へ新しいMarkdown文書を追加したにもかかわらず、Document Review Registryへ反映していない状態をPRで検出できます。

この仕組みは、新しい文書の内容が自然な日本語として十分かを機械判定するものではありません。機械的なcoverageを確認したうえで、文書作成者が`DOCUMENT_AUTHORING_STANDARD.md`に従って意味固定、自然な日本語全文再ドラフト、最終意味監査を実施したことを台帳へ反映する運用です。

## 6. Evidence境界

Planning checkerがPASSすることは、Planning metadataと文書監査台帳の構造整合を示すだけです。

```text
Plan integrity PASS
  != document meaning correct
  != Product Value satisfied
  != Architecture correct
  != Implementation conforms
  != Release ready
  != Operational effectiveness
  != Adoption / Outcome demonstrated
```

機械的整合を意味上の妥当性、実装Evidence、利用者価値へ昇格させません。

## 7. CI failure

Plan integrityが失敗した場合は、検出された不整合を解消してから後続作業へ進みます。

たとえば次を、単なるCIノイズとして無視しません。

- 本文を更新したのにregistryだけが旧Statusのまま残っている。
- 新しいADR / Issueを追加したのに`plan/registry.yaml`へ登録していない。
- 新しいMarkdown文書を追加したのにDocument Review Registryのscopeへ含まれていない。
- 文書監査を`pending`のまま残している。

一方、checkerの設計自体が誤って正当な文書を拒否している場合は、文書をcheckerへ無理に合わせるのではなく、checkerの責務を見直します。

## 8. Natural Japanese review

current Planning規約、ISSUE-000015の完了条件、`document_review_registry.yaml`、実際に発生した本文 / registry不整合、5段階Evidenceへ戻って説明を整理しました。その後、checkerの保証範囲を過大にせず、意味やEvidence強度を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
