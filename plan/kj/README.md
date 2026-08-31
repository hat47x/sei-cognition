# SOZA KJ working documents

更新日: 2026-09-01  
状態: **Current guidance for KJ working records**

## 1. このディレクトリの役割

`plan/kj/`は、ADRやIssueへ判断を移す前の探索・束ね・核融合法・A型図解・B型文章化など、思考過程を保持するための作業領域です。

KJ文書は、Product Value、Accepted ADR、current Contract、current Runtimeの代わりになる規範文書ではありません。

```text
KJ working record
  → Issue / ADR preparation
  → Accepted ADR / resolved Issue
  → Architecture / Contract / Implementation / Evidence
```

後続の判断が成立した後も、KJ文書中の生カードや「ADR候補」という当時の記述を、現在の結論に合わせて後知恵で書き換えません。そうすると、何が観察され、どのように束ねられ、どの段階で判断へ移ったかという思考履歴が失われるためです。

## 2. current authorityとの関係

KJ文書とcurrent判断の関係は次のとおりです。

| KJ文書 | 主な検討 | current landing |
|---|---|---|
| `2026-08-31_TEI設計系列_ラウンドKJ統合.md` | SOZA / TEI境界、Capability / Provider、Inquiry、Authorization、Reference Model等の広域統合 | ADR-0014〜0017、ADR-0019、および後続のArchitecture / Contract / Runtimeへ分岐して反映 |
| `2026-08-31_RequirementInquiry_AuthorizationEvidence_ラウンドKJ.md` | Requirement Inquiry、Question identity、Decision Memory、Authorization Evidence | Requirement InquiryはADR-0015、Authorization EvidenceはADR-0016でAccepted |
| `2026-08-31_ReferenceModel_CapabilityObservation_ラウンドKJ.md` | Reference Model / Cognitive Method、TEI Capability Observation surface | Reference Model / Cognitive MethodはADR-0017、Provider-neutral Capability ObservationはADR-0019、実装上のAdapter境界はADR-0024でAccepted |

とくに、`ReferenceModel_CapabilityObservation`文書末尾の「ADR-0017 / ADR-0018候補」という記述は**当時のDecision preparation記録**です。currentのADR-0018はProduct Value authorityを扱う別判断であり、Capability Observationのcurrent landingはADR-0019、Provider Adapter実装境界はADR-0024です。

同様に、Requirement Inquiry / Authorization文書の「ADR-0015 / ADR-0016候補」は、その後それぞれADR-0015 / ADR-0016としてAcceptedされています。

## 3. 生カードを保全する理由

KJ文書では、結論だけでなく次を残します。

- その時点で観察された事実・違和感・問い
- 低確度でも探索上意味のあるカード
- 束ねる前の語感や具体性
- 統合時に弱まり、戻し照合で回復した残差
- 後続判断では採用されなかった分岐

これらは、現在の結論を正当化するための装飾ではありません。将来Product Valueや前提条件が変わったとき、当時の探索へ戻って別の束ね方を検討できるようにするための記録です。

したがって、KJ文書の監査では「現在と一致するよう全文を書き換える」ことよりも、**原記録を壊さず、current authorityとの読み分けを明確にすること**を優先します。

## 4. 自然な日本語レビューの扱い

新しいKJ文書を作る場合も、統合文・A型図解の説明・B型文章化・Decision preparationなど、人が読むために整理した部分は自然な日本語を最重要視して再ドラフトします。

一方、生カードの言葉に、その時点の感覚や具体性が残っている場合は、単なる文章美化のために均質化しません。意味や「土の匂い」が失われる修正は行いません。

既存の3文書は、2026-09-01の監査でcurrent ADR / Contract / Runtimeとの関係を再確認しました。本文は思考履歴として保全し、現在の着地点は本READMEで補足する方式を採用しています。

## 5. Evidence境界

KJである関係や仮説が見いだされたことは、Accepted DecisionやExecutable Evidenceを意味しません。

```text
KJ synthesis
  != Accepted ADR
  != Contract conformance
  != Runtime conformance
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

必要な判断はADR / Issueへ、実装上の確認はContract / Runtime / fixture / CIへ移して検証します。

## 6. Natural Japanese review

3つの既存KJ文書をcurrent Product Value、ADR-0014〜0019、ADR-0024、Capability Observation Contract、Decision Memory Contract、first semantic runtime、synthetic Provider Adapterへ戻って再監査しました。そのうえで、生カードや当時のDecision preparationを後知恵で改変せず、current authorityとの関係だけを本書で明確化しました。最後に、意味・履歴・Evidence強度を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
