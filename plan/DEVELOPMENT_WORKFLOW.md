# SOZA 開発ワークフロー

更新日: 2026-09-01  
状態: **Accepted Development Convention**

## 1. 目的

この文書は、SOZAの開発をどのbranchで進め、どの順序で価値定義・探索・要件化・設計・実装・検証するかを定めます。

開発速度だけを優先して実装を先行させるのではなく、Product Valueと製品として成立させたい状態を先に明確にします。まだ何を要求すべきか分からない領域では、議論や実証を通して必要性を確認してからRequirementへ進みます。

## 2. Branch運用

安定した基線は`main`で管理します。通常の開発は次の形式のbranchで進めます。

```text
develop/vX.Y.Z
```

原則として開発中の変更を`main`へ直接積み上げません。まとまりのよい単位まで`develop/vX.Y.Z`で整備し、文書・検査・Evidenceが揃った段階で`main`へ統合します。

個別作業では、Product、Plan、Requirement、runtime等の責務が分かるtopic branchを使えます。branch名をProduct ontologyや恒久的なMilestone IDとして扱いません。

## 3. 優先順位

開発作業は原則として次の順序を優先します。

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

上位文書を毎回大量に書くという意味ではありません。実装へ進む前に、上位の意味と判断が十分に定まっているかを確認するための優先順位です。

## 4. 未定領域の標準フロー

まだRequirementとして十分に定まっていない領域では、次の流れを基本とします。

```text
Open Question
  → Discussion / Research
  → Experiment / Prototype / Fixture / Human Review
  → Evidence
  → Candidate Requirement
  → Requirement audit
  → Stable Requirement / existing Requirement integration / No Change
```

Open Questionを直接stable REQへ変換しません。

チャット上の議論は探索・統合に利用できますが、current正本はrepository上のProduct / Plan / Requirement / ADR等へ戻します。

Requirement化の詳細なgateは`plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`を正とします。

## 5. Product Milestoneの扱い

`product/roadmap/SOZA_PRODUCT_MILESTONES.md`は、期限ではなくOutcomeとEvidenceで製品成立段階を示します。

Milestoneは次の作業の優先順位を決める入力になりますが、その内容をそのままRequirementやworkflowへ変換しません。

```text
Product Milestone
  != Universal ontology
  != fixed workflow
  != calendar deadline
```

historicalなM48 / M49等の実装順序とも区別します。

## 6. Production runtimeの実装言語

ADR-0027に従い、SOZA自身が所有・配布するproduction runtimeとfirst-party reference implementationはGoを標準とします。

一方、次へGoを一律に強制しません。

- Semantic Contractそのもの
- Cognitive Method Realization
- Capability Provider
- AI / ML研究
- evaluation / analysis
- fixture生成やone-shot tooling

Python等で作ったprototypeをproductionへ進める場合は、次の順序で扱います。

1. 外部Method / Providerとして明示的境界に残せるか確認する。
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
5. stable Requirement / Acceptance Scenarioへ影響する場合は、Architectureより先に反映する。
6. 設計判断が必要であればADRを作成・更新する。
7. Architecture / Contractを整える。
8. 実装する。
9. fixture / test / conformanceで確認する。
10. 実際に得られた高さまでEvidenceと未完了事項を更新する。
11. 文書を自然な日本語へ全文再ドラフトする。
12. 意味・仕様・留保・Evidence強度が変わっていないか最終監査する。
13. current Markdown文書を追加・更新した場合は、`plan/document_review_registry.yaml`へ監査状態を反映する。
14. 対象CIがsuccessしていることを確認する。

CI failureが出た場合は、最後まで先送りしません。**失敗を検出した時点で原因を解消し、successを確認してから後続作業へ進みます。**

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

`Plan integrity`はMarkdown変更でも起動し、Document Review Registryのcoverageと`pending`の有無を検査します。

ただし、このCIは自然な日本語の品質や文書の意味を自動判定しません。機械的なcoverage検査と、全文再ドラフト・最終意味監査は別の責務です。

## 10. Evidenceを超える状態更新をしない

Product Value Acceptanceでは次の5段階を分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

設計が完了したこと、actual repositoryでCIが通ったこと、release Artifactが成立したこと、本番で安定して動作したこと、利用者・組織へ価値が届いたことは、それぞれ別の主張です。

Issue、Requirement、Milestone、README等の状態は、実際に確認できた高さまでだけ更新します。

## 11. 実装順序を製品ontologyにしない

`M48`、`M49`、`M50`等はhistoricalな開発Milestoneです。

その順序を利用者の業務workflowやSOZAのUniversal ontologyとして固定しません。Product Milestoneも、製品成熟を確認するための上位計画であり、利用者の必須操作順序ではありません。

意味上の前提が変わった場合は、旧実装を守ることよりProduct Value / Requirement / ADRへ戻って再検討することを優先します。

## 12. Planning変更は可能な範囲でatomicにする

ADR / Issue本文のStatus、`plan/registry.yaml`、関連文書を同時に変更する必要がある場合は、可能な範囲で一つの変更単位へまとめます。

同様に、新しいcurrent Markdown文書を追加した場合は、可能な範囲で`plan/document_review_registry.yaml`への監査状態反映も同じ作業単位へ含めます。

分割commitが必要な場合は、最終branch状態でPlan integrityが成立し、途中状態を達成Evidenceとして扱わないようにします。

## 13. CI failureの扱い

CI failureは次の設計入力でもあります。

1. 失敗したworkflow / step / fixtureを確認する。
2. Product / Plan / Requirement / Contract / runtime / 文書台帳のどの層の問題かを切り分ける。
3. current Product Value / Contractを安易に弱めず、誤っている層を修正する。
4. 同じCIを再実行し、successを確認する。
5. 必要ならIssue / Evidence文書へ原因と修正内容を残す。
6. その後に次の作業へ進む。

## 14. Natural Japanese review

current Product Value、Product Shape、Product Journey、期限を持たないProduct Milestone、5段階Evidence、Document Review Registry、ADR-0027のproduction runtime言語方針へ戻ってworkflowを再構成した。未定領域では議論・実証をRequirementより先に置き、production runtimeではGoを標準としながら、外部Method / Provider、AI / ML研究、評価へ言語制約を広げない境界を追加した。既存のbranch方針、Evidence境界、CI即時解消方針を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。