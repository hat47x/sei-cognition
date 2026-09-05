# ISSUE-000070 actual Evidence 回収記録

更新日: 2026-09-05

## この記録の目的

長期間PR化されないまま残っていた `codex/issue-000070-actual-evidence` のactual runtime version交換Evidenceを、現在の `develop/v0.2.0` へ失わず回収するための記録です。

元branchは現在のdevelopより大きく遅れており、そのままtreeを採用すると、後から追加されたpreflight、progress observer、runner log identity、path safetyなどのfail-closed境界を巻き戻します。このため、回収mergeでは現在のdevelopを第一親・正本treeとし、元branchを第二親として履歴上統合したうえで、actual EvidenceそのものとEvidence要約だけを現在treeへ追加します。

## 回収するEvidence

元branch head:

- `codex/issue-000070-actual-evidence`
- `501110b0e6eaf26cf3fdf1b8cbb1b74b9a952007`

actual run:

- execution id: `local-20260904T193531Z-7855`
- raw Evidence: `runtime/evidence/runtime-version-exchange-local-20260904T193531Z/`
- narrative summary: `runtime/RUNTIME_VERSION_EXCHANGE_EVIDENCE_2026-09-05.md`

元branchの保存記録では、Ollama `0.32.13` / `0.32.14` のactual inference、固定model identity、同一prompt identity、historical Application保持、portable reconstruction、Evidence + Provenance verificationまで確認され、branch-local verifierは `107 ok / 0 blocked` を記録しています。

## 現行正本での扱い

この回収は、元branchのEvidenceを失わないための履歴・artifact統合です。元branch上の古いREADME、Issue本文、registry、runtime guard、integration helperを現在developへ戻しません。

また、branch-local verifierの成立を、後から強化された現在のcanonical verifier / progress observerを現在develop上で再実行したことへ読み替えません。したがって、この回収だけではISSUE-000070の現在の`Open`判定を`Resolved`へ変更しません。

次に行うべき確認は、回収したraw Evidenceを現在のcanonical verifierと補助的progress observerへ通し、現在のRequirement / Contract / reconstruction境界と再照合することです。

```text
historical actual Evidence recovered
  != current-contract revalidation PASS
  != ISSUE-000070 Resolved
  != model output quality satisfied
  != KJ-method outcome quality satisfied
```

raw Evidenceのbyte identityをcheckout時の改行変換から守るため、対象Evidence directoryには`.gitattributes`で`-text`を適用します。
