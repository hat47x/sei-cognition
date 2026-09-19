# Governed workload policy admission

状態: **Evaluation-only / fail-closed**

SAC-B6jは、SAC-B6i governanceをGoへ再実装するものではありません。

上流でgovernance validation済みのdeclaration snapshotについて、B6g `WorkloadPolicyEnvelope.Resolve` へ入れる直前に最低限のadmission条件だけを確認します。

## Admission条件

- state = `reviewed`
- `resolution_allowed=true`
- version >= 1
- `superseded_by_version=null`
- canonical governance provenance ref
- declaration policyがB6g envelopeのexact resolved policyと一致

candidate / expired / superseded / unreviewed / policy mismatchはfail-closedです。

## 責務分離

Python B6i governance contractが引き続き所有するもの:

- review metadata completeness
- validity / review-due / expiry ordering
- fixed logical `validation_as_of`
- bidirectional supersession
- latest-version判定
- Evidence / provenance completeness

Go admission adapterはそれらを再計算しません。既に検証されたsnapshotをresolverへ通してよいかだけを確認します。

## Current manifest

checked-in B6i declarationsは2件とも `candidate / resolution_allowed=false` です。

したがってcurrent manifestをそのままGo admissionへ渡すintegration testでは、両方ともresolver到達前に拒否されます。

## Runtime Evidence

`workload_governance_admission_evidence_2026-09-19.json`

Go 1.23.2 / `GO111MODULE=off` のfocused compatibility executionでは、existing B6g envelope testsを含む15 top-level testsがPASSしました。

canonical moduleはGo 1.25です。#512が未解消のため、これはGo 1.25 PASSとして扱いません。

## 停止線

```text
admitted declaration != correct declaration
reviewed snapshot != semantic truth
Go adapter PASS != production activation
Go 1.23 compatibility PASS != canonical Go 1.25 PASS
governance admission != workload class inference
```
