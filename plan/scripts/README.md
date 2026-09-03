# `plan/scripts/` — planning管理補助

更新日: 2026-09-03  
状態: **Current Planning Tooling Baseline**

## 1. 役割

このディレクトリには、SOZAのPlanning運用で起きやすい機械的な不整合を早く検出するための、小さな検査・採番ツールを置きます。

ツールはPlanning文書や開発文書の意味上の正本ではありません。判断理由は各ADR / Issue本文を正とし、`plan/registry.yaml`は状態と関連を管理する台帳です。自然な日本語監査の状態は`plan/document_review_registry.yaml`で管理します。

checkerは、これらの意味を評価するのではなく、actual treeと台帳の間に生じる機械的な取りこぼしを検出します。

GitHub Actionsは当面完全に停止しているため、これらのcheckerは必要に応じて**ローカルで個別に実行**します。自動CIへ常設することを現在の前提にはしません。

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

## 4. Requirement registry integrity

```bash
python3 plan/scripts/check_requirements_registry.py
```

Requirement / Acceptance ScenarioのID、本文、registry上の参照関係に機械的な不整合がないかを確認します。

self-testは次で実行します。

```bash
python3 -m unittest plan/scripts/test_check_requirements_registry.py
```

Requirementの意味上の妥当性や、新しいRequirementを追加すべきかどうかは、このcheckerでは判断しません。

## 5. 次番号の候補

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
5. `check_plan_registry.py`をローカルで実行する。
6. merge直前にも同一IDが追加されていないことを確認する。

番号競合が起きた場合は、恒久IDの意味を後から入れ替えません。成立順序と意味上の連続性からどちらを維持するか判断し、必要なら後発側を別IDへ移すか、重複内容を統合します。

## 6. ローカル検証の使い分け

GitHub Actions停止中は、変更内容に応じて必要なcheckerだけをローカルで個別実行します。

Planning文書やregistryを変更した場合の代表的な組み合わせは次です。

```bash
python3 plan/scripts/check_plan_registry.py
python3 plan/scripts/check_document_review_registry.py
```

Requirement / Acceptance Scenarioを変更した場合は、必要に応じて次も実行します。

```bash
python3 plan/scripts/check_requirements_registry.py
```

checker自身を変更した場合は、対応するself-testも実行します。

```bash
python3 -m unittest plan/scripts/test_check_document_review_registry.py
python3 -m unittest plan/scripts/test_check_requirements_registry.py
```

すべての変更で全checkerを機械的に実行する必要はありません。変更した責務と影響範囲に応じて、必要な検査を選びます。

```text
change scope
  → relevant local checker
  != monolithic CI required
```

ローカル環境の制約で検査を実行できなかった場合は、未実行範囲を明記します。実行していないcheckerをPASS扱いにはしません。

## 7. checker failureの扱い

Planning checkerが失敗した場合は、検出された不整合を確認し、該当する層を修正します。

たとえば次を、単なるノイズとして無視しません。

- 本文を更新したのにregistryだけが旧Statusのまま残っている。
- 新しいADR / Issueを追加したのに`plan/registry.yaml`へ登録していない。
- 新しいMarkdown文書を追加したのにDocument Review Registryのscopeへ含まれていない。
- 文書監査を`pending`のまま残している。

一方、checkerの設計自体が誤って正当な文書を拒否している場合は、文書をcheckerへ無理に合わせるのではなく、checkerの責務を見直します。

checker failureは修正対象ですが、GitHub Actions停止中の現在はCI statusやrequired checkとして扱いません。修正commitは通常どおりpushし、必要なローカル検証を再実行します。

## 8. Evidence境界

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

## 9. Natural Japanese review

current Planning規約、ISSUE-000015の完了条件、`document_review_registry.yaml`、実際に発生した本文 / registry不整合、5段階Evidenceへ戻って説明を整理しました。

以前の本文には、削除済みの`.github/workflows/plan-integrity.yml`をcurrent実行面として扱う記述が残っていました。GitHub Actionsを当面完全に停止する現在方針に合わせ、Planning checkerはローカルで変更範囲に応じて個別実行する形へ書き直しました。

checkerの保証範囲は従来どおり機械的整合に限定しています。ローカル実行へ切り替えたことを、文書の意味やEvidence強度を弱める理由にはしていません。また、実行できなかった検査をPASSへ読み替えない停止線も明示しました。

意味やEvidence強度を変えず、現在の運用として自然な日本語で読み通せることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
