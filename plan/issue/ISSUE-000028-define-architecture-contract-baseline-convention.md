# ISSUE-000028: current Architecture / Contracts基線の正本・責務・版管理規約を定める

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

current `requirements/`の次段として、`architecture/`と`contracts/`をactual repositoryへ実体化する前に、それぞれが何を正本とし、ADR / Requirement / Implementationとどう責務を分けるかを定める。

historical candidateのArchitecture / Contractを無検査で復元せず、current REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、ADR-0001〜ADR-0020から再導出できる規約を作る。

## Historical inputs

Library上のhistorical candidateには、Architecture、Contract、schema、representation profile、Milestone固有の設計・実装報告が混在している。

これらにはcurrent Product Valueと整合する意味核が多くある一方、Milestone名、当時の型候補、JCS / Go等の実装選択、旧Evidence stateも含まれる。

## Questions reviewed

1. Architecture文書は何を正本とし、ADRとどう分けるか。
2. Architectureにstable IDを付けるか、名前付きcurrent viewとして扱うか。
3. Contractはどの条件で新設するか。
4. Contractのlogical identityとversionをどう管理するか。
5. Markdown Contract Definitionとmachine-readable schemaの権威関係をどうするか。
6. representation-only changeとsemantic breaking changeをどう分けるか。
7. historical Milestone文書をcurrent architectureへどう移すか。
8. Core / Profile / Provider / Adapter / Projectionの配置をどこまでArchitectureで固定するか。
9. Product Value V1〜V8 → REQ → ADR → Architecture / Contractの追跡をどう残すか。
10. Design EvidenceとExecutable Contract conformanceをどう分けるか。

## Resolution

ADR-0021で、Architecture / Contractの権威関係、current view、Contract versioning、human-readable Contract Definitionとmachine-readable schemaの関係、historical candidateの再評価規則をAccepted Decisionとして確定した。

主な境界は次である。

```text
Architecture description != Architecture Decision Record
Architecture concern != runtime component
Semantic Contract != Representation Profile
Contract exists != Implementation conforms
Schema validates example != Operational interoperability
```

current Architectureのcanonical entry pointは次とする。

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

current Contractは、Architectureから相互運用・historical reconstruction・verification上の必要性が確認された境界だけを規範化する。

## Acceptance

### Semantic / Design Acceptance

- [x] ArchitectureとADRの責務境界が決まっている。
- [x] ArchitectureとContractの責務境界が決まっている。
- [x] Contract identity / version ruleが決まっている。
- [x] machine-readable schemaの権威関係が決まっている。
- [x] historical candidateの再利用規則が決まっている。
- [x] Milestone identityをcurrent正本へ持ち込まない規則が決まっている。
- [x] V1〜V8からArchitecture / Contractまで追跡できる規則が決まっている。
- [x] Evidence階層を混同しない規則が決まっている。
- [x] 自然な日本語全文再ドラフトと最終意味監査が完了している。

### Executable Acceptance

本Issueでは要求しない。current Architecture / Contractsの実体化とconformanceは後続Issueへ分離する。

## Follow-up

- ISSUE-000029 — current Reference Architectureの実体化
- ISSUE-000030 — current Contract baselineの実体化

## Reopen conditions

次の場合に再検討する。

- Architecture current viewにstable document identityが必要な外部利用が反復する。
- Contract Definitionとmachine-readable schemaの二層管理が重大な同期不良を繰り返す。
- federation等でContract versioningへより強い互換性規則が必要になる。

## Natural Japanese review

ADR-0021、current Requirements、actual Architectureの構成へ戻してResolutionを確定した後、意味、規範強度、Evidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
