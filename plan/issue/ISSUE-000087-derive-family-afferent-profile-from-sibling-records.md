# ISSUE-000087: 兄弟製品の実在の記録から、家族の求心プロファイルを導く

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0006, ADR-0014, ADR-0016, ADR-0035**  
Updated: 2026-09-27

## Goal

ADR-0035（Proposed）は、SEIを製品ファミリーの「統合の頂点（任意の合流）」とし、製品からSEIへ向かう求心のプロファイルを候補として持つことを提案しています。`product/definition/SEI_FAMILY_SEMANTIC_MAP.md`の対応は、現時点ではすべて候補です。

本Issueでは、プロファイルを机上で先に決めるのではなく、**兄弟製品に実在する記録をSEIの語で読み、どこで意味が失われるかを実際に観測してから**、必要な最小限のプロファイルを導きます。

最初の対象は次の二つです。

1. TEIの共有受理境界が残す`.tei/decisions/`の受理記録
2. SUIのADR-0086が定める`human_reviewed`への昇格の記録と、`artifactId`・`revisionId`・`contentDigest`

完了時には、次のどれに当たるかを判別できることを目指します。

```text
A. 対応表の読みで十分であり、プロファイルは不要
B. 失われる意味を明示した読み方の注記を加えれば十分
C. 最小限の求心プロファイル（Profileまたは参考の規約）が必要
D. SEIの既存契約では表せない独立の失敗があり、Candidate Requirementへ進む
E. 実在の記録がまだなく、判断できない（NOT_VERIFIED）
```

どの結論も正当な成果です。

## Background

### 確認済みの事実

- `SEI_PRODUCT_SHAPE.md` §8.5は、共通protocolやcross-product orchestrationを標準化する必要性はまだ確定しておらず、実際の統合の失敗から必要な境界だけを見つけるとしています。
- 評価記録（`product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md`）は、家族統合に最小限の求心プロファイルが要ると指摘し（W8）、製品ごとに認識が食い違う「分離脳」を新しい失敗の仮説として挙げています。
- TEIでは、共有受理境界を通った受理が`.tei/decisions/`に記録されます。記録には、意図、Evidence、基準のrevision、書き換えたfile、意味の差分、残った未解決が含まれ、`decisions`コマンドで現在のworkspaceと照合して`current` / `superseded`と`intact` / `diverged`を返します。TEI自身は、この記録を「authorityではない」としています（`hat47x/tei-platform:docs/status.md`）。
- SUIのADR-0086（Accepted）は、sensemaking artifactのlogical identity、revision、provenance、authority eventを分ける設計です。ただし、`human_reviewed`への昇格をReviewとみなすかAuthorityとみなすかは、ADR-0086とそのartifact contractでも開かれたままで、SUI側で未決です。payloadの正規化方式も、SUI側でまだ定まっていません。ADR-0086自体は「Runtime impact: None in this change」としています（`hat47x/sui-sensemaking:01_Plans/adr/ADR-0086-sensemaking-artifact-identity-provenance-authority-events.md`）。

### 最初に確かめる、観測された損失の候補

TEI側の検討で、`.tei/decisions/`の受理記録に**timestampのfieldがない**ことが見つかりました。この記録をSEIのdecision memoryへ投影すると、判断の時刻が失われます。判断の時刻は、当時の根拠と判断後の情報を分ける読み方（V1 / V3、`post-decision information != historical basis`）に関わります。

これは、実在の記録から見つかった**最初の損失の候補**です。SEIの要求の不足として確定したものではありません。Git commitの時刻で補える可能性も、TEI側で明示的なfieldを持つ可能性もあります。TEIはこの点を`hat47x/tei-platform:plan/issue/000070-sei-reference-adoption-change2-resumption.md`のTEI-4の付録に記録しており、この文書は未mergeブランチ`docs/family-apex-backflow-20260927`上にだけ存在します。

### 兄弟製品側の対応の提案（未mergeブランチ上）

- SUI: `hat47x/sui-sensemaking:02_Architecture/sensemaking_artifact_sei_mapping_candidate.md`（ADR-0086と`sei.semantic-reference`の対応、承認の記録の書き出し）
- TEI: `hat47x/tei-platform:plan/issue/000070-sei-reference-adoption-change2-resumption.md`（TEI-4の付録）
- EKI: `hat47x/eki-fabric:research/sei-cognition-mapping.md`、`research/contribution-accounting.md`
- MMI: `hat47x/markdown-matrix-injector:02_Architecture/sei-decision-semantics-mapping.md`
- CSW: `hat47x/cultural-substrate-weaving:docs/ja/maintainers/sibling-product-semantic-correspondence.md`（CSWのブランチは`research/family-apex-backflow-20260927`）
- vs-bear: `hat47x/vs-bear-simulator:docs/M5_ADOPTION_EVIDENCE_JOIN.md`

いずれも各製品の提案であり、SEIがこれらに依存することはありません。

### Unknown / Conflict

- SUIの昇格の記録が、実際のruntimeの記録として存在するか。存在しない場合は、ADR-0086の設計に対する読みに留まる。
- TEIの受理記録の時刻を、Git commitの時刻で補うことが、当時の根拠を分ける目的に十分か。
- 同じ判断がSUIとTEIの両方に現れたとき、食い違いを見つけられるか（分離脳の仮説）。

## Questions

1. TEIの受理記録を、SEIのDecisionの記録とTEIのAuthorityを指すevidence refとして読めるか。そのとき、SEIの記録がTEIのAuthorizationの代わりに見えないか。
2. TEIの受理記録に時刻がないことは、SEIでDecisionとして読むときに、どの程度の損失になるか。Git commitの時刻で補えるか。
3. SUIの`human_reviewed`への昇格は、SEIでReviewとして読むべきか、DecisionとAuthority evidence refとして読むべきか。SUI側の判断が定まるまで、SEIはどちらも決めずに読めるか。
4. SUIの`contentDigest`から、SEIのExact Bindingを作れるか。正規化方式が未決の間、どう扱うべきか。
5. 意味の差分、`current` / `superseded`、`intact` / `diverged`のような各製品に固有の情報は、SEIで読むときに失われるか。失われてよいか。
6. 読むために、兄弟製品の側が何かを変えたり、SEIを稼働させたりする必要があるか。必要があってはならない。

## Constraints

- 兄弟製品の記録は読み取るだけとし、兄弟製品の側に義務や変更を求めない。
- どの製品の局所のループも、SEIの稼働を必要としない状態を保つ。
- SEIのRecommendationをTEIのAuthorizationとして扱わない。SUIの昇格の判断はSUIの権限に残す。
- SUIで未決の事項（ReviewかAuthorityか、正規化方式）を、SEIの側で先に決めない。
- 記録に個人情報や秘密が含まれる場合は、SEIへ写さず、参照だけに留める。
- 実際の損失が観測されない限り、プロファイルやUniversal型を先に固定しない。
- 対応表への掲載を、特権や優先度の理由にしない。

## Required scenarios / experiments

### E82.1 — TEIの受理記録を読む

TEIの`reference/workspace/.tei/decisions/`にある実在の受理記録を、少なくとも一件選びます。候補は、2026-09-21に利用者の明示的なAcceptance decisionで受理された`repair_intake`のsourceの記録です。

1. 記録の各項目を、SEIのDecision Memory、Semantic Reference、Capability Observationのどの読みに当てられるかを書き出す。
2. 判断の時刻が失われることを確かめ、Git commitの時刻で補えるか、補った場合に当時の根拠を分ける目的に足りるかを確かめる。
3. 意味の差分、残った未解決、`current` / `superseded`、`intact` / `diverged`が、SEIの読みで保たれるか、失われるかを確かめる。

### E82.2 — SUIの昇格の記録を読む

SUIに、ADR-0086に沿った実在の昇格の記録があるかを確かめます。

1. 実在の記録がある場合は、E82.1と同じ手順で読む。
2. 実在の記録がない場合は、ADR-0086の設計に対する読みとして記録し、実在の記録での確認は`NOT_VERIFIED`とする。
3. ReviewとAuthorityのどちらで読むかは、SUI側の判断を待ち、SEIの側では両方の読みを並べておく。

### E82.3 — 同じ判断が二つの製品に現れる場合（任意）

同じ判断が、SUIとTEIの両方に記録される場面を探します。たとえば、SUIがTEIへの移管について行った判断（`hat47x/sui-sensemaking:01_Plans/issues/issue-ARCH-TEI-MIGRATION-01-tei-reference-adoption-and-development-load-validation.md`で任意のdogfoodとして提案）です。二つの記録をSEIの語で並べたとき、食い違いを見つけられるかを確かめます。

読み方:

- **PASS** — 意味の損失がない、または損失を具体的に名指しでき、読み方の注記で扱える。
- **FAIL** — 損失を名指しできない、または損失のために当時の根拠や判断の主体を取り違える。
- **NOT_VERIFIED** — 実在の記録がない、または確かめていない。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

実在の記録を読んで対応を書き出すことは、Design上の観測です。変換を実装してtestで確かめた場合に限り、その範囲のExecutable Evidenceになります。

## Deliverables

- 実在の記録を読んだ対応の記録（本Issueへ追記するか、`evaluation/`へ評価資料として置く）
- 観測した損失の一覧と、A〜Eのどれに当たるかの判断
- `SEI_FAMILY_SEMANTIC_MAP.md`の該当する行の更新。Evidenceが得られた行だけ、状態を「候補」から改める
- Cに当たる場合の、最小限の求心プロファイルの草案

## Resolution

次をすべて満たしたとき、Resolved候補とします。

1. TEIの受理記録を少なくとも一件、実際に読み、判断の時刻の損失を含めて損失を記録した。
2. SUIの昇格の記録について、実在の記録を読んだか、実在の記録がないことを`NOT_VERIFIED`として記録した。
3. 結果をA〜Eのどれかに分類した。
4. 兄弟製品の側に義務や依存を作っていないことを再確認した。

Resolvedになることは、家族統合が利用者に価値を届けたことを意味しません。

## Reopen conditions

- 兄弟製品の記録の形式が変わり、読み方が成り立たなくなった。
- SUIで、昇格の記録をReviewとみなすかAuthorityとみなすかが定まった。
- SUIでpayloadの正規化方式が定まった。
- TEIで、受理記録に時刻のfieldが加わった、またはGit commitの時刻で補う方針が定まった。
- 分離脳にあたる食い違いが、実際の利用で観測された。

## CI / verification

実在の記録を読むだけの段階では、repositoryのtestは必要ありません。変換をcodeとして実装する場合は、Goのsemantic runtimeのtestとContractのconformance checkerを、変更範囲に応じてローカルで個別に実行します。

2026-09-27の起票時点では、PythonとGoがない環境で作業したため、どのcheckerも実行していません。手作業での確認はISSUE-000085の「2026-09-27の検証（手作業）」に記録しています。

## Natural Japanese review

ADR-0035、家族の対応表、Product Shape §8.5、TEIの`docs/status.md`、SUIのADR-0086、各製品の未mergeブランチ上の対応の提案を照合し、求心プロファイルを実在の記録と実際の損失から導く手順を定めました。TEIの受理記録に時刻がないという最初の損失の候補を、要求の不足と断定せずに確かめる項目として置き、SUIで未決の事項をSEIの側で先に決めないことをConstraintsに入れています。

内容、Constraints、読み方、完了条件を固定した後、**自然な日本語となることを最重要視して全文を再ドラフトしました。** 最後に、Goal、Questions、Constraints、Resolution条件、Evidenceの高さが変わっていないことを再監査しました。
