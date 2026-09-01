# `plan/scripts/` — planning管理補助

更新日: 2026-09-01  
状態: **Current Planning Tooling Baseline**

## 1. 役割

このディレクトリには、ADR / Issue / `plan/registry.yaml`、Requirements registry、文書監査台帳の管理を補助する小さな検査・採番ツールを置きます。

ツールはPlanning文書の意味上の正本ではありません。判断理由は各ADR / Issue本文を正とし、各registryは状態・関連・監査範囲を管理する補助台帳です。checkerは、それらの間に起きやすい機械的な不整合を早く検出します。

## 2. Plan registry integrity check

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

## 3. Requirements registry check

```bash
python3 plan/scripts/test_check_requirements_registry.py
python3 plan/scripts/check_requirements_registry.py
```

self-testを先に実行し、その後current Requirements / Acceptance Scenario registryを検査します。

このPASSはRequirements registryの構造整合を示すものであり、Requirement内容やProduct Value達成の証明ではありません。

## 4. Document review registry check

```bash
cd plan/scripts
python3 test_check_document_review_registry.py
cd ../..
python3 plan/scripts/check_document_review_registry.py
```

`check_document_review_registry.py`は、`plan/document_review_registry.yaml`について次を構造的に検査します。

- schemaがcurrent versionであること。
- `pending: []`であること。
- reviewed / exclusion statusが許可語彙に収まること。
- reviewed scopeがactual Markdownへ解決できること。
- current Markdownがreviewed scopeから漏れていないこと。
- 同一scopeを重複登録していないこと。

`test_check_document_review_registry.py`では、positive caseに加え、次のnegative caseを固定します。

- 無効status
- stale scope
- 未収載Markdown
- duplicate scope
- pending review

このcheckerは文章の美しさや自然さを自動採点しません。

```text
Document review registry PASS
  != prose quality automatically proven
```

自然な日本語の品質そのものは、`plan/DOCUMENT_AUTHORING_STANDARD.md`と各文書の最終意味監査で担保します。このcheckerの役割は、監査工程から漏れたcurrent Markdownを機械的に見つけることです。

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
5. `check_plan_registry.py`を通す。
6. merge直前にも同一IDが追加されていないことを確認する。

番号競合が起きた場合は、恒久IDの意味を後から入れ替えません。成立順序と意味上の連続性からどちらを維持するか判断し、必要なら後発側を別IDへ移すか、重複内容を統合します。

## 6. v0.1.0 Release Readiness

`.github/workflows/release-readiness.yml`は、release candidate commitに対してcurrent checkerを同一commit上で再実行します。

主な対象は次です。

- Plan registry
- document review registry
- Requirements / Scenario registry
- Contract conformance
- Representation Profile conformance
- RFC 8785 JCS probe
- Go semantic runtime / Provider Adapter / Verifier / Payload Source tests
- V6 / V7 Projection evaluation

詳細は`plan/release/V0_1_0_RELEASE_READINESS.md`を参照します。

```text
Release Readiness Gate PASS
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

実際のtagや配布Artifactを検証して初めて、Product Value上のRelease Evidenceを別途評価します。

## 7. Evidence境界

各checkerのPASSは対象metadataやfixture、runtime sliceの限定されたExecutable Evidenceです。

```text
Plan / Requirements / Document registry PASS
  != Product Value satisfied
  != Architecture correct as a whole
  != Release Evidence
  != Operational effectiveness
  != Adoption / Outcome demonstrated
```

機械的整合を意味上の妥当性、production成立、利用者価値へ昇格させません。

## 8. CI failure

CIが失敗した場合は、どの不整合を検出したかを確認し、失敗を残したまま後続作業へ進みません。

checker defectとactual baseline defectを分け、actual defectは責任を持つ正本・fixture・implementation側で修正します。checker defectの場合も、検査強度を不当に下げてPASSさせません。

## 9. Natural Japanese review

current Planning規約、5段階Evidence、自然な日本語監査台帳、実際に発生したregistry不整合、v0.1.0 Release Readiness Gateへ戻って説明を整理しました。その後、各checkerの保証範囲を過大にせず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
