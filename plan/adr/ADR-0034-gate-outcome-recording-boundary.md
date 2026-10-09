# ADR-0034: 実行前の確認結果の記録は、まず運用ログに置き、Contract化は実証後に判断する

Status: **Proposed**  
Related Issue: **ISSUE-000084**  
Updated: 2026-10-06

## Context

ADR-0033は、Decision Gatewayが実行意図の発行前に、参照するDecisionとAuthority basisを確認し、結果を記録に残すとしました。`sei gate check`は、この確認を既存のDecision Memoryの読み取りとして実装しています。判断の記録は変えませんが、確認のたびに運用ログへ追記します。

確認の結果と、Action Intentそのものを、判断の記録(Semantic Interchangeのbundle)に入れるかどうかは、決まっていません。入れるなら、新しいContractで意味を固定する必要があります。

関係する既存の判断と事実は次のとおりです。

- Product Value: V1 Historical Reconstruction、V2 Semantic Separation、V8 Execution Independence。
- 既存のContractは五つあり、Action Intentと確認結果を表す型はありません。Contractを増やすのは、実装やProviderをまたいで意味を固定する必要がある場合に限る、という方針があります(`contracts/CONTRACT_CATALOG.md`)。
- REQ-0006は、提案、判断、権限、実行の分離を求めます。確認の結果は、そのどれでもありません。
- 現在のEvidenceは、`sei gate check`の実装とtestだけです。実際の利用者が、確認結果を後から読み返したいかどうかのEvidenceはありません。

このADRで固定しないものは次です。

- Action Intentの意味と構造。
- 確認結果をContractにする場合のfield。
- Authorityの確認方法(CR-84.1、CR-84.7)。

## Decision

二段階で進めます。

### 第一段階: 運用ログ(現在)

確認のたびに、時刻、決定ID、結果、理由、方針、確認していない事項を、`gate-checks.jsonl`へ追記します。このログは、判断の記録とは別の、運用のための記録です。

```text
gate-checks.jsonl(運用ログ)
  != Semantic Contractの記録
  != Decisionの根拠
  != Authorityの証明
```

- bundleには入れず、`sei export`にも含めない。
- 追記のみとし、ログに書けない場合は、許可を出さずに失敗する(fail-closed)。
- ログの存在や内容を、判断の根拠として他の記録から参照しない。

### 第二段階: Contract化の判断(実証の後)

次のいずれかが、実際の利用で確認された場合に、Contract化を別のADRで検討します。

- 確認結果を、別の組織、別の実装、別のProviderへ、意味を保って渡す必要が生じた。
- 監査人が、運用ログではなく判断の記録の一部として、確認の結果を検証したいという要求が確認された。
- 運用ログの形式が、実装ごとに分かれて、同じ確認が別の意味に読まれる事例が出た。

Contract化を検討するときは、Action Intentと確認結果を一つにまとめず、別の記録として扱えるかを先に確かめます。確認結果は、行為の許可でも、実行の事実でもありません。

## Alternatives considered

### A. 最初から確認結果のContractを作る

意味を早く固定できます。しかし、必要性のEvidenceがないまま、Contractを増やすことになります。Contractは作ると維持と互換性の費用が続き、削除も難しくなります。Action Intentの意味も未定のため、誤った型を先に固定する危険があります。採りません。

### B. 確認結果を記録しない

実装は最も単純です。しかし、ADR-0033が求める「確認の結果を記録に残す」を満たしません。また、拒否や確認不能の履歴が残らず、運用の事後確認ができません。採りません。

### C. 既存のContract(Capability ObservationやSemantic Reference)へ、確認結果を載せる

新しいContractは要りません。しかし、確認結果はCapabilityの観測でも、意味上の参照でもありません。性質の違うものを一つの記録へ潰すことになり、このプロダクトが最も避けたいことに反します。採りません。

### D. 運用ログをbundleの拡張領域(extensions)に入れる

bundleに含められ、書き出しにも載ります。しかし、運用ログが判断の記録の一部のように見え、Decisionの根拠として誤って参照される危険があります。第二段階の判断を先取りすることにもなります。採りません。

## Consequences

### Positive

- Contractを増やさずに、確認の履歴を残せる。
- 確認結果を判断の根拠と取り違えにくい。
- 実際の利用から、Contract化の必要性を確かめられる。

### Costs / Risks

- 運用ログは、`sei export`に含まれないため、別の環境へ持ち出すと失われる。第三者による検証には使えない。
- 運用ログは、単一のファイルへの追記であり、改ざんの検出は無い。署名と時刻の証明(CR-84.8)は未実装である。
- 複数のプロセスが同時に追記したときの順序は、保証しない。

## Revisit conditions

- 第二段階の三つの条件のいずれかが確認された。
- 運用ログの改ざんや欠落が、実際の問題になった。
- ADR-0033のDecision Gatewayの境界が変更された。
- Action Intentの意味が、別のIssueで定まった。

## Evidence

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

- Design Evidence: ISSUE-000084、ADR-0033、`contracts/CONTRACT_CATALOG.md`。
- Executable Evidence: `sei gate check`の運用ログについて、`runtime/go/seicli`のtestで、追記、bundleの不変、`export`への非混入、ログに書けない場合の失敗を確認した。範囲と留保は`runtime/SEI_CLI_FIRST_SLICE_EVIDENCE_2026-10-06.md`に記録する。
- Adoption / Outcome Evidence: なし。

このADRをAcceptedにする条件は、E-84.2とE-84.3の結果を踏まえて、プロダクト責任者が確認することです。
