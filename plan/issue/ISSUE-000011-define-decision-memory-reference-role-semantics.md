# ISSUE-000011: Decision Memoryの参照役割を定義する

Status: **Resolved**  
Priority: **3**  
Related ADRs: **ADR-0010, ADR-0011**  
Updated: 2026-08-31

## Goal

Decision周辺の参照を単一`refs[]`へ潰さず、後から「何が文脈で、何が根拠で、何が採否対象で、何が未解決だったか」を再構成できる意味役割を定める。

## Resolution

少なくとも次を意味上分離する。

- `context`
- `basis`
- `recommendation`
- `unresolved`

同じArtifactが複数役割を持ってよい。`basis != EvidenceUse`を維持し、Recommendation参照だけから採用を推定しない。

歴史再構成を主張する場合、当時参照した可変Artifactの内容をExactArtifactBinding等で特定できなければならない。

判断はADR-0011へ確定したため、本IssueはResolvedとする。

## Deferred representation

専用DecisionReference型、field配置、wire enum等のrepresentation shapeはactual implementationまでDeferredとする。

このDeferred事項はIssue自体をOpenへ戻す理由ではない。Resolvedなのは**参照役割の意味境界**であり、具体表現や実装は別のEvidence段階として扱う。

## Natural Japanese review

StatusとDeferred representationを分離したうえで、M49 Reference Roles architectureとADR-0011へ戻して内容を照合し、意味、条件、未実装範囲を変えず、自然な日本語となることを最重要視して全文を再確認した。最終意味監査も実施済み。
