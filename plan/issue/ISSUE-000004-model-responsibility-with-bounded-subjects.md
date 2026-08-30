# ISSUE-000004: Bounded SubjectでResponsibilityを表現する

Status: **Resolved**  
Priority: **5**  
Related ADRs: **ADR-0004**  
Updated: 2026-08-31

## Goal

人間、AI、service、organization、committee、external provider等を参照しつつ、Global Principal ontologyや固定role hierarchyをCoreへ持ち込まずにResponsibilityを表現する。

## Investigation

一人が複数責任を持つ場合、組織Decisionと実務担当者が異なる場合、AIがRecommendationを作る場合、committee共同Decision、外部contractor、Selective Disclosure等を比較した。

## Resolution

主体参照には`BoundedSubjectRef { scope_ref, subject_id }`を用い、外部identityは別Bindingとする。Responsibilityは文脈付き`ResponsibilityStatement`として表し、role vocabularyはopenに保つ。

Responsibility、Authorization、Credential、Trust ranking、Capability eligibilityを同一視しない。

判断はADR-0004へ確定したため、本IssueはResolvedとする。

## Natural Japanese review

Bounded Subject architectureへ戻して内容を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
