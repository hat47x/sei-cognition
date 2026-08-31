# Historical Contract Mapping

更新日: 2026-08-31  
状態: **Historical mapping / current Evidenceではない**

## 1. 目的

この文書は、M48〜M50等のhistorical candidateで作成されたContract、schema、Representation Profileの意味核を、current Contract baselineへどのように再利用したかを記録します。

historical fileの存在、local PASS、`VERIFIED`等をcurrent Executable Evidenceへ自動継承しません。

## 2. Mapping

| Historical asset | Current treatment | Current destination / note |
|---|---|---|
| `INQUIRY_EPISTEMIC_ARTIFACTS_v1.md` | **Partially integrated** | Inquiry / Epistemicsの意味核を`soza.semantic-interchange`のtyped semantic recordとReference Architectureへ統合。M48 identityは継承しない。 |
| `M47_M48_COMPATIBILITY_PORT_v1.md` | **Historical bridge only / future method work input** | Method境界の再定義禁止、exact referenceの考え方をArchitectureへ統合。current Method Contractは未新設。 |
| `SEMANTIC_PORTABLE_BUNDLE_v1.md` | **Integrated and restructured** | portable bundleの意味を`soza.semantic-interchange`へ統合。旧bundle field setは継承しない。 |
| `PORTABLE_EXACT_BINDING_REPRESENTATION_v1alpha1.md` | **Split** | exact binding semanticsは`soza.semantic-reference`へ、custom canonicalizationはhistorical Representation Profile候補へ分離。 |
| `JCS_SHA256_REPRESENTATION_PROFILE_candidate.md` | **Candidate only** | current stable Profileには未採用。ISSUE-000009で再評価。 |
| `RAW_BYTES_SHA256_REPRESENTATION_PROFILE_candidate.md` | **Candidate only** | non-JSON / large binary向け候補。ISSUE-000009で再評価。 |
| `SOZA_SEMANTIC_INTERCHANGE_v1alpha1.json` | **Historical schema only** | semantic vocabularyの参考にするが、current Contract Definitionから新schemaを再導出する。旧field set / enumは自動継承しない。 |
| M49 Decision Memory acceptance / architecture candidate | **Integrated semantically** | `soza.decision-memory`へMilestone名なしで再構成。historical fixture PASSは継承しない。 |
| M50 Capability Choice / Observation candidate | **Integrated semantically** | `soza.capability-observation`とArchitectureへ再構成。Matching / Choice / ProviderをObservationへ統合しない。 |

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

## 5. Evidence境界

historical candidateには、当時のlocal design / executable experimentとして価値があります。

ただしcurrent repositoryで同じschema、fixture、runtime、toolが存在し、current Contractへ再照合されるまでは、current Executable Evidenceではありません。

```text
historical PASS != current PASS
historical schema exists != current schema adopted
```

## 6. 再参照規則

historical資産を今後再利用するときは、次の順序で確認します。

1. current REQ / SCNで必要性を確認する。
2. current ADRと矛盾しないか確認する。
3. current Contract Definitionの意味を先に確定する。
4. historical schema / code / fixtureを差分材料として比較する。
5. 採用するfieldやalgorithmごとにcurrent理由を持たせる。
6. actual repositoryでExecutable Evidenceを取り直す。

## 7. 自然な日本語レビュー

historical Evidenceとcurrent Design Evidenceを混同しないようmappingを整理した後、意味・Evidence強度・留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
