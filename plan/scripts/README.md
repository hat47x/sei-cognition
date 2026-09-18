# `plan/scripts/` — Planning管理補助

更新日: 2026-09-18  
状態: **Current Planning Tooling Baseline**

## 1. 役割

このディレクトリには、SEIのPlanning運用で起きやすい機械的な不整合を早く検出するための、小さな検査・採番ツールを置きます。

ツールはPlanning文書や開発文書の意味上の正本ではありません。判断理由は各ADR / Issue本文を正とし、`plan/registry.yaml`は状態と関連を管理する台帳です。自然な日本語監査の状態は`plan/document_review_registry.yaml`で管理します。

checkerは、これらの意味を評価するのではなく、actual treeと台帳・開発規約の間に生じる機械的な取りこぼしを検出します。

GitHub Actionsは当面完全に停止しているため、checkerは必要に応じて**ローカルで個別に実行**します。自動CIへ常設することをcurrent baselineの前提にはしません。

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

self-test:

```bash
python3 -m unittest plan/scripts/test_check_plan_registry.py
```

正常系に加え、ID重複、file binding重複、actual treeとのずれ、Status不一致、存在しない関連ADR、未登録の同一ID prefixファイル等を回帰検査します。

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

self-test:

```bash
python3 -m unittest plan/scripts/test_check_document_review_registry.py
```

正常系に加え、少なくとも次をnegative caseとして確認します。

- 未登録Markdownを追加するとFAILする。
- `pending`を残すとFAILする。
- actual treeへ一致しないstale reviewed scopeを残すとFAILする。

`reviewed-no-change`は正当な監査完了状態です。KJの生カードや原記録など、現在の結論へ合わせて書き換えるべきでない文書を、checkerが再ドラフトへ強制することはありません。

## 4. Requirement registry integrity

```bash
python3 plan/scripts/check_requirements_registry.py
```

Requirement / Acceptance ScenarioのID、本文、registry上の参照関係に機械的な不整合がないかを確認します。

self-test:

```bash
python3 -m unittest plan/scripts/test_check_requirements_registry.py
```

Requirementの意味上の妥当性や、新しいRequirementを追加すべきかどうかは、このcheckerでは判断しません。

## 5. GitHub Actions停止基線

```bash
python3 plan/scripts/check_github_actions_disabled.py
```

Accepted Development Conventionでは、current baselineに`.github/workflows`を置かず、必要な検証をローカルのtest / checker / probeとして個別実行します。このcheckerは、その停止基線がactual treeから逸脱していないかだけを確認します。

- `.github/workflows`以下にtracked fileが1件でも存在すればFAILする。
- workflowの内容やProduct semanticsを評価しない。
- GitHub-hosted runnerの可用性をProduct成立条件へ昇格させない。
- 将来Actionsを再採用する場合は、先にAccepted Development Conventionを明示的に変更する。

self-test:

```bash
python3 -m unittest plan/scripts/test_check_github_actions_disabled.py
python3 -m unittest plan/scripts/test_check_sei_operator_identity.py
```

このchecker自身をGitHub Actionsから実行して停止基線を守る、という循環した運用にはしません。

## 6. SEI operator identity regression guard

```bash
python3 plan/scripts/check_sei_operator_identity.py
```

SOZA→SEI Cognition改名後のcurrent operator surfaceについて、後続mergeで旧CLIや旧stage名が再流入して実行手順と実装がずれることを検出します。

対象はISSUE-000072のTEI version-exchangeに関するcurrent runtime文書に加え、`runtime/integration/*.py`のproduction script全体です。主に次のobsolete operational tokenを検査します。

- `SOZA_REPO / SOZA_GO / SOZA_HEAD`
- `--soza-repo-root / --soza-go-executable / --expected-soza-head`
- `soza_runtime_layout / soza_source_identity / soza_go_toolchain / soza_teiintegration_live_test`
- `sozaGoRequirement / sozaGoVersion / sozaSource / postLiveTestSozaSource`

これは旧名称一般を禁止するcheckerではありません。実在するhistorical workflow名、artifact / branch名、記録済みEvidenceの`soza.*` schema、ADR-0031に基づくreader側legacy identity受理は対象外です。`runtime/evidence/`とtest sourceもcurrent operator surfaceには数えません。

self-test:

```bash
python3 -m unittest plan/scripts/test_check_sei_operator_identity.py
```

2026-09-18にはchecker / testのGit blob SHA-1一致を確認した再構成環境で7/7 PASSを確認し、production integration 42 file + operator Markdown 13 fileの計55 fileをcurrent branchから実査してobsolete operational token 0件を確認しました。結果は`evaluation/identity-migration/sei_operator_identity_guard_execution_20260918.json`へ保存しています。これはoperator / production integration identityの限定的な回帰検査であり、改名作業全体の再証明やhistorical Evidence不変性検査の代替ではありません。

## 7. 次番号の候補

```bash
python3 plan/scripts/next_plan_id.py
python3 plan/scripts/next_plan_id.py adr
python3 plan/scripts/next_plan_id.py issue
```

actual treeの最大番号から次の候補IDを表示します。

このコマンドは**番号を予約しません**。複数branchや複数作業者が同時に実行すれば、同じ候補番号を得ることがあります。また欠番を再利用せず、actual treeで観測した最大番号の次を候補とします。

self-test:

```bash
python3 -m unittest plan/scripts/test_next_plan_id.py
```

空tree、最大値+1、gap非再利用、templateや無関係fileの除外、ADR / Issueの独立算出、ID空間枯渇を回帰検査します。

新しいADR / Issueを作るときは次を基本とします。

1. 最新の`develop/vX.Y.Z`を基準にする。
2. `next_plan_id.py`で候補番号を確認する。
3. 文書とregistryを同じ変更単位で作成する。
4. 最新developとの競合を確認する。
5. `check_plan_registry.py`をローカルで実行する。
6. merge直前にも同一IDが追加されていないことを確認する。

番号競合が起きた場合は、恒久IDの意味を後から入れ替えません。成立順序と意味上の連続性からどちらを維持するか判断し、必要なら後発側を別IDへ移すか、重複内容を統合します。

## 8. ローカル検証の使い分け

GitHub Actions停止中は、変更内容に応じて必要なcheckerだけをローカルで個別実行します。

Planning文書やregistryを変更した場合の代表例:

```bash
python3 plan/scripts/check_plan_registry.py
python3 plan/scripts/check_document_review_registry.py
```

Requirement / Acceptance Scenarioを変更した場合:

```bash
python3 plan/scripts/check_requirements_registry.py
```

repository baselineやworkflow配置に触れた場合:

```bash
python3 plan/scripts/check_github_actions_disabled.py
```

TEI version-exchangeのoperator手順、CLI名、stage / result keyを変更した場合:

```bash
python3 plan/scripts/check_sei_operator_identity.py
```

checkerや採番helper自身を変更した場合は、対応するself-testも実行します。

```bash
python3 -m unittest plan/scripts/test_check_plan_registry.py
python3 -m unittest plan/scripts/test_check_document_review_registry.py
python3 -m unittest plan/scripts/test_check_requirements_registry.py
python3 -m unittest plan/scripts/test_check_github_actions_disabled.py
python3 -m unittest plan/scripts/test_next_plan_id.py
```

すべての変更で全checkerを機械的に実行する必要はありません。変更した責務と影響範囲に応じて必要な検査を選びます。

```text
change scope
  → relevant local checker / test / probe
  != monolithic CI required
```

ローカル環境の制約で検査を実行できなかった場合は未実行範囲を明記します。実行していないcheckerやself-testをPASS扱いにはしません。

## 9. checker failureの扱い

Planning checkerが失敗した場合は、検出された不整合を確認し、該当する層を修正します。

たとえば次を単なるノイズとして無視しません。

- 本文を更新したのにregistryだけが旧Statusのまま残っている。
- 新しいADR / Issueを追加したのに`plan/registry.yaml`へ登録していない。
- 新しいMarkdown文書を追加したのにDocument Review Registryのscopeへ含まれていない。
- 文書監査を`pending`のまま残している。
- current conventionがActions停止中なのに`.github/workflows`へtracked workflowが戻っている。
- current codeがSEI名へ移行済みなのに、TEI version-exchangeのoperator文書やproduction scriptへ旧 `--soza-*` / `SOZA_*` / `soza_*` tokenが戻っている。

一方、checkerの設計自体が誤って正当な文書やtreeを拒否している場合は、対象をcheckerへ無理に合わせるのではなく、checkerの責務またはAccepted Conventionを見直します。

checker failureは修正対象ですが、GitHub Actions停止中の現在はCI statusやrequired checkとして扱いません。修正commitは通常どおりpushし、必要なローカル検証を再実行します。

## 10. Evidence境界

Planning checkerがPASSすることは、Planning metadata、文書監査台帳、またはcurrent開発規約との構造整合を示すだけです。

```text
Plan / repository integrity PASS
  != document meaning correct
  != Product Value satisfied
  != Architecture correct
  != Implementation conforms
  != Release ready
  != Operational effectiveness
  != Adoption / Outcome demonstrated
```

機械的整合を意味上の妥当性、実装Evidence、利用者価値へ昇格させません。

## 11. Natural Japanese review

current Planning規約、ISSUE-000015の完了条件、`document_review_registry.yaml`、実際に発生した本文 / registry不整合、5段階Evidenceへ戻って説明を整理しました。

GitHub Actionsを当面完全に停止する現在方針に合わせ、Planning checkerはローカルで変更範囲に応じて個別実行する形を維持しています。2026-09-18時点のactual toolingへ同期し、ADR / Issue registry、Document Review Registry、Requirements Registry、Actions停止基線、SEI operator identity regression guard、次ID候補算出の各責務とself-testを一つのrunbookから追えるようにしました。

checkerの保証範囲は機械的整合に限定しています。ローカル実行へ切り替えたことを、文書の意味やEvidence強度を弱める理由にはしていません。また、実行できなかった検査をPASSへ読み替えない停止線も維持します。

意味やEvidence強度を変えず、current運用として自然な日本語で読み通せることを最重要視して最終意味監査を実施しました。
