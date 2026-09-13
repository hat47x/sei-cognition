# Historical Contract Mapping

更新日: 2026-08-31  
状態: **Historical Design Provenance Mapping / current Evidenceではない**

## 1. 目的

この文書は、M48〜M50等のhistorical candidateで作成されたContract、schema、Representation Profile候補の意味核を、current Contract / Profile baselineへどのように再利用したかを記録します。

historical fileの存在、local PASS、`VERIFIED`等をcurrent Executable Evidenceへ自動継承しません。

## 2. Mapping

| Historical asset | Current treatment | Current destination / note |
|---|---|---|
| `INQUIRY_EPISTEMIC_ARTIFACTS_v1.md` | **Partially integrated** | Inquiry / Epistemicsの意味核を`sei.semantic-interchange`のtyped semantic recordとReference Architectureへ統合。M48 identityは継承しない。 |
| `M47_M48_COMPATIBILITY_PORT_v1.md` | **Historical bridge only / future method work input** | Method境界の再定義禁止、exact referenceの考え方をArchitectureへ統合。current Method Contractは未新設。 |
| `SEMANTIC_PORTABLE_BUNDLE_v1.md` | **Integrated and restructured** | portable bundleの意味を`sei.semantic-interchange`へ統合。旧bundle field setは継承しない。 |
| `PORTABLE_EXACT_BINDING_REPRESENTATION_v1alpha1.md` | **Split** | exact binding semanticsは`sei.semantic-reference`へ、representation規則はProfile境界へ分離。historical custom canonicalizationはcurrent authorityではない。 |
| `JCS_SHA256_REPRESENTATION_PROFILE_candidate.md` | **Historical candidate; current independently accepted** | historical候補を自動継承せず、ADR-0023で`sei.jcs+sha256/v1alpha1`をcurrent Profileとして再判断し、actual fixture / Go probeでEvidenceを取り直した。 |
| `RAW_BYTES_SHA256_REPRESENTATION_PROFILE_candidate.md` | **Historical candidate; current independently accepted** | historical候補を自動継承せず、ADR-0023で`sei.raw-bytes+sha256/v1alpha1`をcurrent Profileとして再判断し、actual fixtureでEvidenceを取り直した。 |
| `SEI_SEMANTIC_INTERCHANGE_v1alpha1.json` | **Historical schema only** | semantic vocabularyの参考にしたが、current Contract Definitionからcurrent schemaを再導出した。旧field set / enumは自動継承していない。 |
| M49 Decision Memory acceptance / architecture candidate | **Integrated semantically** | `sei.decision-memory`へMilestone名なしで再構成。historical fixture PASSは継承せず、current schema / fixture / runtimeでEvidenceを取り直した。 |
| M50 Capability Choice / Observation candidate | **Integrated semantically** | `sei.capability-observation`とArchitectureへ再構成。Matching / Choice / ProviderをObservationへ統合せず、current F1〜F7 / runtime / synthetic Adapterで一部境界を検証した。 |

## 3. 再利用した意味核

historical資産からcurrent baselineへ残した主な意味は次です。

- Observation != EvidenceUse != Assurance != Truth
- Unknown != No
- Conflict != latest-wins
- source provenance != discovery route
- logical identity != exact binding != semantic revision != storage revision
- Recommendation != Decision != Authority != Execution
- Decision creation != uncertainty resolution
- Capability Definition != Observation != Matching != Decision != Provider
- Provider execution mechanicsはCore外
- exact binding verificationは明示Representation Profileへ委譲
- `verified / failed / not_verified`の分離
- Projection / UI stateはcanonical semantic authorityではない
- private chain-of-thoughtをdurable semantic requirementにしない

## 4. 継承しなかったもの

次はcurrent baselineへ自動継承していません。

- M47 / M48 / M49 / M50等のMilestone identity
- historical package layout
- old field names
- old enum vocabulary
- old JSON Schema structure
- Go struct layout
- custom canonicalizationをstable defaultとする判断
- old local conformance PASS
- old Requirementの`direct / partial / design_only`
- release / operational coverage claim

currentでJCS、SHA-256、Go等を利用していても、それだけでhistorical選択を継承したことにはしません。current Product Value、Requirement、ADRから独立して採用理由を持たせます。

## 5. current Evidenceとの境界

historical candidateには、当時のlocal Design / Executable experimentとして価値があります。

一方、current repositoryには現在、historical PASSとは独立した次のEvidenceがあります。

- 4 Contract Definition / JSON Schema
- Contract 17 fixture conformance
- JCS / raw-bytes Profile fixture / Go probe conformance
- first semantic runtime slice
- synthetic Provider A / B Adapter slice

```text
historical PASS != current PASS
historical schema exists != current schema adopted
historical Profile candidate != current Profile accepted automatically
```

current Executable Evidenceは、current Contract / Profileへ再照合し、actual repositoryで取り直した範囲だけを主張します。

## 6. historical M47 digestの扱い

historical M47 bindingで使われたdigest規則が現在のJCS / raw-bytes Profileと同じかは、current Profile conformanceから推定しません。

```text
current Profile verified != historical digest profile identified
```

historical M47 digest recoveryはISSUE-000034で独立して追跡します。Profileを特定できない場合は`not_verified`として扱い、現在のProfileで再hashして過去bindingを作り直しません。

## 7. 再参照規則

historical資産を今後再利用するときは、次の順序で確認します。

1. current REQ / SCNで必要性を確認する。
2. current ADRと矛盾しないか確認する。
3. current Contract Definition / Representation Profileの意味を先に確定する。
4. historical schema / code / fixtureを差分材料として比較する。
5. 採用するfieldやalgorithmごとにcurrent理由を持たせる。
6. actual repositoryでExecutable Evidenceを取り直す。

## 8. Evidenceの高さ

```text
historical Design / local executable evidence
  != current Design Evidence
  != current Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

historical資料の価値を否定せず、同時にcurrentの達成主張へ自動変換しません。

## 9. Natural Japanese review

historical Contract / schema / Profile候補をcurrent 4 Contract family、2 Accepted Profile、17 fixture、first semantic runtime、synthetic Provider Adapterへ照合しました。historical Evidenceとcurrent Design / Executable Evidenceを分離し、historical M47 digestもISSUE-000034へ独立させています。その後、対応関係、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
