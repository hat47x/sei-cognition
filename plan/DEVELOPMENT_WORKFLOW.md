# SOZA 開発ワークフロー

更新日: 2026-09-03  
状態: **Accepted Development Convention**

## 1. 目的

この文書は、SOZAの開発をどのbranchで進め、Product Value、探索、Requirement、設計、実装、検証をどの順序で扱うかを定めます。

実装を早く積み上げること自体を目的にはしません。まず「何を価値として守るか」を確認し、まだ要求が定まっていない領域は、議論や実証を通して必要性を確かめてからRequirementへ進めます。

検証手段も意味上の正本とは分けます。GitHub Actions、ローカルtest、repository同梱checker、外部runner、手動実証は、いずれも検証のための手段です。Product Value、Requirement、Contract、Evidenceの意味を、特定の実行基盤へ依存させません。

## 2. Branch運用

安定した基線は`main`で管理します。通常の開発は次の形式のbranchで進めます。

```text
develop/vX.Y.Z
```

原則として、開発中の変更を`main`へ直接積み上げません。まとまりのよい単位まで`develop/vX.Y.Z`で整備し、必要な文書・検査・Evidenceが揃った段階で`main`へ統合します。

個別作業では、Product、Plan、Requirement、runtime等の責務が分かるtopic branchを利用できます。branch名をProduct ontologyや恒久的なMilestone IDとして扱いません。

## 3. 優先順位

開発では、原則として次の順序を優先します。

1. `product/value`、`product/definition`、`product/vision`、`product/principles`
2. `product/roadmap/SOZA_PRODUCT_MILESTONES.md`
3. `plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`、`plan/issue`、`plan/adr`
4. discussion / research / experimentによる未定領域の探索
5. `requirements`
6. `architecture`、`contracts`
7. runtime、Provider Adapter、fixture、test、tool
8. Release Evidence
9. Operational Evidence
10. Adoption / Outcome Evidence

上位文書を毎回大量に書くという意味ではありません。実装へ進む前に、上位の意味と判断が十分に定まっているかを確認するための順序です。

## 4. 未定領域の標準フロー

Requirementとして十分に定まっていない領域では、次の流れを基本とします。

```text
Open Question
  → Discussion / Research
  → Experiment / Prototype / Fixture / Human Review
  → Evidence
  → Candidate Requirement
  → Requirement audit
  → Stable Requirement / existing Requirement integration / No Change
```

Open Questionを直接Stable Requirementへ変換しません。

チャット上の議論は探索や統合に利用できますが、current正本はrepository上のProduct / Plan / Requirement / ADRへ戻します。

Requirement化の詳細なgateは`plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`を正とします。

## 5. Product Milestoneの扱い

`product/roadmap/SOZA_PRODUCT_MILESTONES.md`は、期限ではなくOutcomeとEvidenceで製品成立段階を示します。

Milestoneは次の作業の優先順位を考える入力にはなりますが、その内容をそのままRequirementやworkflowへ変換しません。

```text
Product Milestone
  != Universal ontology
  != fixed workflow
  != calendar deadline
```

historicalなM48 / M49等の実装順序とも区別します。

## 6. Production runtimeの実装言語

ADR-0027に従い、SOZA自身が所有・配布するproduction runtimeとfirst-party reference implementationはGoを標準とします。

一方、次にはGoを一律に強制しません。

- Semantic Contractそのもの
- Cognitive Method Realization
- Capability Provider
- AI / ML研究
- evaluation / analysis
- fixture生成やone-shot tooling

Python等で作ったprototypeをproductionへ進める場合は、次の順序で扱います。

1. 外部Method / Providerとして明示的な境界に残せるか確認する。
2. SOZA first-party runtimeへ含める必要性を確認する。
3. 含める必要がある場合は、Go移植と多言語runtime維持のコストを比較する。
4. Go以外をfirst-party production runtimeへ採用する場合は、ADR-0027との整合またはRevisit理由を明示する。

```text
standard runtime language = Go
connected implementation language != Go required
```

詳細は`architecture/IMPLEMENTATION_LANGUAGE_POLICY.md`とADR-0027を正とします。

## 7. 一つの開発単位で行うこと

一つの課題を進めるときは、必要な範囲で次を行います。

1. Product Value / Product Milestoneとの関係を確認する。
2. 何を要求すべきか未定なら、Open QuestionとしてIssueまたは上流計画へ置く。
3. 必要に応じて議論、資料調査、prototype、fixture、human review等で実証する。
4. 新Requirementが必要そうな場合はCandidateとして既存REQ / SCNとの重複を監査する。
5. Stable Requirement / Acceptance Scenarioへ影響する場合はArchitectureより先に反映する。
6. 設計判断が必要であればADRを作成・更新する。
7. Architecture / Contractを整える。
8. 実装する。
9. fixture / test / conformance / checker等で確認する。
10. 実際に得られた高さまでEvidenceと未完了事項を更新する。
11. 文書を自然な日本語へ全文再ドラフトする。
12. 意味・仕様・留保・Evidence強度が変わっていないか最終監査する。
13. current Markdown文書を追加・更新した場合は、`plan/document_review_registry.yaml`へ監査状態を反映する。
14. 利用可能な検証手段を確認し、実行できた検査と実行できなかった検査を分けて記録する。

GitHub Actionsがcurrent baselineに存在しない期間は、Actionsのsuccessを開発完了の一般条件にはしません。repository同梱test、checker、fixture、保存Evidence、必要に応じた外部実行を使い、確認できた範囲だけをEvidenceとして記録します。

## 8. Requirementを増やす前の停止線

新しいREQ IDを付ける前に、少なくとも次を確認します。

1. Product Valueのどの価値を守るために必要か。
2. Product Milestoneの単なる実装候補ではなく、独立した規範上の必要性か。
3. 具体Scenarioまたは失敗例で必要性を説明できるか。
4. 既存REQ / SCNで既に表現できないか。
5. UI / Provider / Storage / AI model等の現在制約を補うだけではないか。
6. Profile / Projection / Adapter / deployment policyへ置く方が自然ではないか。
7. 評価時点から10〜50倍程度先を見ても意味差が残るか。
8. Acceptanceを観測可能な形で定義できるか。

この監査の結果、新Requirementを作らないことも正当な完了です。

実装言語も原則としてRequirementへ持ち込みません。Goはcurrent standard realizationであり、Goであること自体が利用者世界のsemantic obligationではありません。

## 9. 文書品質を後処理にしない

自然な日本語への再ドラフトは、release直前にまとめて行う後処理ではありません。

新しく作成・更新した開発文書は、その作業単位を閉じる前に`plan/DOCUMENT_AUTHORING_STANDARD.md`の工程を通します。

Document Review Registryのcoverage確認と、全文の自然な日本語レビューは別の責務です。checkerが存在する場合も、機械的なcoverage検査だけで日本語の自然さや文書の意味が保証されたとは扱いません。

## 10. Evidenceを超える状態更新をしない

Product Value Acceptanceでは次の5段階を分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

設計が完了したこと、repository上のtestが通ったこと、release Artifactが成立したこと、本番で安定して動いたこと、利用者・組織へ価値が届いたことは、それぞれ別の主張です。

Issue、Requirement、Milestone、README等の状態は、実際に確認できた高さまでだけ更新します。

## 11. 実装順序を製品ontologyにしない

`M48`、`M49`、`M50`等はhistoricalな開発Milestoneです。

その順序を利用者の業務workflowやSOZAのUniversal ontologyとして固定しません。Product Milestoneも、製品成熟を確認するための上位計画であり、利用者の必須操作順序ではありません。

意味上の前提が変わった場合は、旧実装を守ることよりProduct Value / Requirement / ADRへ戻って再検討することを優先します。

## 12. Planning変更は可能な範囲でatomicにする

ADR / Issue本文のStatus、`plan/registry.yaml`、関連する上流文書を同時に変更する必要がある場合は、可能な範囲で一つの変更単位へまとめます。

同様に、新しいcurrent Markdown文書を追加した場合は、`plan/document_review_registry.yaml`への監査状態反映も同じ作業単位へ含めます。

分割commitが必要な場合も、最終branch状態でPlan Registryと文書台帳が一致するようにします。途中状態を達成Evidenceとして扱いません。

## 13. pushと検証を分ける

検証のfailureや外部実行基盤の利用不能は、原因調査や修正commitのpushを止めるためのロックではありません。

```text
commit
  → push
  → 利用可能な手段で観測
  → 必要なら修正
  → 再push
```

GitHub Actions等の自動検証を将来再導入した場合も、次を分けます。

- workflowが定義・選択されたか。
- runnerが割り当てられたか。
- stepが開始されたか。
- 検査本文がPASS / FAILしたか。
- その結果がどのEvidence段階を支えるか。

`runner_id = 0`、`steps = []`のように検査本文へ到達していないfailureをrepository test failureとして扱いません。

一方、実際に検査本文が開始されて失敗した場合は、Product / Plan / Requirement / Contract / runtime / fixture / 文書台帳のどの層に問題があるかを切り分け、Product ValueやContractを安易に弱めず誤っている層を修正します。

## 14. merge / release / Evidence gate

push、merge、release、Evidence確定は同じgateではありません。

```text
push allowed
  != merge allowed
  != release allowed
  != Evidence claim established
```

特定の検査成功をmergeやreleaseに要求する場合は、その対象と理由を個別に定義します。通常の開発pushをrequired status checkで塞ぐ方針は、別途明示的に決めない限り採用しません。

current baselineではGitHub Actions workflow群を常設していません。将来自動検証を再導入するときは、ISSUE-000069のReopen条件に従い、実証責務、共有依存、外部runner availabilityを改めて監査します。

## 15. Natural Japanese review

Product Value、Product Shape、Product Journey、期限を持たないProduct Milestone、5段階Evidence、Document Review Registry、ADR-0027のproduction runtime言語方針へ戻り、開発の流れを再構成しました。

以前の文書には、GitHub Actionsが常に存在し、Plan integrity等が自動起動することを前提に読める箇所が残っていました。PR #70でActionsをcurrent baselineから外したため、「何を検証すべきか」と「どの実行基盤で検証するか」を分けて書き直しました。

CI failureをpush停止条件にしない原則は維持しています。同時に、検証を省略してよいという意味にも読めないよう、利用可能なtest、checker、fixture、保存Evidence、外部実行で確認できた範囲を記録し、merge / release / Evidence gateは別に扱うことを明示しました。

意味、要求強度、Evidence強度を変えず、現在のrepository方針として自然な日本語で一続きに読めることを最重要視して全文を再ドラフトしました。