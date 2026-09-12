# ISSUE-000018: Authorization EvidenceとDecision Memoryの接続境界を定める

Status: **Resolved**  
Priority: **3**  
Related ADRs: **ADR-0004, ADR-0010, ADR-0011, ADR-0014, ADR-0016**  
Updated: 2026-08-31

## Goal

TEIや他Capability Providerが行う認証・認可評価を、SEIのDecision Memoryからどのように監査可能に参照するかを定める。

## Investigation

Entry Authorization / Resource Authorization、legacy auth、Provider固有policy、past / current authorization、Provider unavailable等を、SEIのDecision / Responsibility / Observation / Assurance境界へ戻してラウンドKJ法で検討した。

## Resolution

ADR-0016をAcceptedとし、本IssueをResolvedとする。

SEIはAuthorization engine / policy ontologyを所有しない。Provider側の評価は必要に応じてObservation、AssuranceRecord、EvidenceUse、Provider-specific reference等から参照する。

次を同一視しない。

```text
Decision != Responsibility != Authorization != Execution
Entry Authorization != Resource Authorization
past authorization != current authorization
not evaluated != denied
```

Universal `AuthorizationResult` Artifactは現時点では追加しない。複数Providerで独立Artifactが必要になる反復Evidenceが得られた場合に再検討する。

## Natural Japanese review

KJ統合とADR-0016へ戻して内容を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
