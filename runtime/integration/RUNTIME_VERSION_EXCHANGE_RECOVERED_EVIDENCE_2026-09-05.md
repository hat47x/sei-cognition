# ISSUE-000070 actual Evidence 回収記録

更新日: 2026-09-05

## この記録の目的

長期間PR化されないまま残っていた `codex/issue-000070-actual-evidence` のactual runtime version交換Evidenceを、現在の `develop/v0.2.0` へ失わず回収するための記録です。

元branchは現在のdevelopより大きく遅れており、そのままtreeを採用すると、後から追加されたpreflight、progress observer、runner log identity、path safetyなどのfail-closed境界を巻き戻します。このため、回収mergeでは現在のdevelopを第一親・正本treeとし、元branchを第二親として履歴上統合したうえで、actual EvidenceそのものとEvidence要約だけを現在treeへ追加しました。

## 回収したEvidence

元branch head:

- `codex/issue-000070-actual-evidence`
- `501110b0e6eaf26cf3fdf1b8cbb1b74b9a952007`

actual run:

- execution id: `local-20260904T193531Z-7855`
- raw Evidence: `runtime/evidence/runtime-version-exchange-local-20260904T193531Z/`
- narrative summary: `runtime/RUNTIME_VERSION_EXCHANGE_EVIDENCE_2026-09-05.md`

元branchの保存記録では、Ollama `0.32.13` / `0.32.14` のactual inference、固定model identity、同一prompt identity、historical Application保持、portable reconstruction、Evidence + Provenance verificationまで確認され、verificationは `107 ok / 0 blocked`、`ready-to-review` を記録しています。

## current-contract再照合

回収直後は、元branch上のverificationを「後から強化された現在のcanonical verifier / Contractへ再照合した」とは扱わず、ISSUE-000070をOpenのまま保持しました。

その後、`runtime/RUNTIME_VERSION_EXCHANGE_CURRENT_CONTRACT_REVALIDATION_2026-09-05.md`でactual run commit `ae9f631b7d570a6c3853bb71b794d501761fdf63` とcurrent developをGit object identityで比較しました。

次はactual run時とcurrent developで同一objectです。

- ISSUE-000070 Resolution Criteria
- core Evidence verifier
- Evidence + Provenance verifier
- fixed artifact manifest
- Product Requirements
- Acceptance Scenarios
- Cognitive Method / Semantic Reference / Semantic Interchangeを含むrelevant Contract baseline

したがって、保存済みverificationが古い判定ロジックに対する結果でありcurrent Contractへ未照合、という保留理由は解消しました。Requirement / Contract再照合と自然な日本語最終監査もnarrative Evidenceに記録され、対象正本は現在まで漂流していません。

```text
historical actual Evidence recovered
  + current-contract object equivalence confirmed
  + Resolution Criteria 1-12 re-audited
  = ISSUE-000070 Resolution Criteria satisfied
```

これはactual A/Bを新たに再実行したという意味ではありません。repository内保存コピーをcurrent pathで再度canonical verifierへ通すことはreproducibility checkとして有用ですが、同一verifier / 同一manifest / 同一Contractへの保存済み`ready-to-review`結果を無効にする新しいResolution条件ではありません。

## 停止線

- model output quality: Not Evaluated
- KJ-method outcome quality: Not Evaluated
- Recommendation correctness: Not Evaluated
- Decision correctness: Not Evaluated
- E4 Operational portability: Not Established

```text
ISSUE-000070 Resolved
  != arbitrary runtime portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```

raw Evidenceのbyte identityをcheckout時の改行変換から守るため、対象Evidence directoryには`.gitattributes`で`-text`を適用しています。
