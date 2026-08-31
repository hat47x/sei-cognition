# ISSUE-000024: Capability Observation境界をschemaとfixtureで実体化する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0012, ADR-0013, ADR-0014, ADR-0019**  
Updated: 2026-08-31

## Goal

ADR-0019で確定したProvider-neutralなCapability Observation境界を、actual repositoryで検証できるContract、schema、fixture、semantic validatorへ落とす。

意味境界を先に固定した状態を保ち、TEI固有Schemaや一時的な実装都合からUniversal Coreを逆算しない。

## Resolution

### 1. Capability Observation Contractを実体化した

次をcurrent Contractとして追加した。

- `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
- `contracts/schemas/v1alpha1/capability-observation.schema.json`

Contractでは次を分離している。

```text
Capability Definition
  != Capability Observation
  != Matching
  != Choice Decision
  != Provider Selection
  != Authority
  != Execution
```

Provider internal stateをSOZA Universal Coreへ直接コピーせず、Provider-specific target referenceとmapping / adapter provenanceを保持できる。

### 2. F1〜F7をactual fixtureとして実体化した

`fixtures/contracts/v1alpha1/capability/`へ次を追加した。

- F1 — TEI partial degradation
- F2 — proposed state != actual state
- F3 — Release without Environment binding
- F4 — Observation gap
- F5 — TEI / SaaS cross-provider comparison
- F6 — historical reconstruction
- F7 — selective disclosure

Value Axisとの対応は`fixtures/contracts/v1alpha1/README.md`へ明示した。

### 3. Provider-neutralityを維持した

F5では、TEIとSaaSを同じ`document-summarization` Capabilityに対する異質なProviderとして同一Semantic Interchangeへ入れた。

一方、TEIのrelease情報やSaaSのservice plan等はProvider固有contextとして保持し、Universal Capability Observation fieldへ無理に平坦化していない。

Universal suitability scoreやProvider kindによる優先順位も要求していない。

### 4. Unknown / Conflict / Withheld境界を保持した

F3 / F4 / F7等で、次をnegative factへ変換しないことを確認した。

```text
not observed != unavailable
Unknown != incompatible
withheld != false
```

F7では、内部topologyの存在は示されているが内容が非開示という状態を`withheld`として保持した。

### 5. mapping provenanceとhistorical reconstructionを実体化した

F6では、Decision D1が利用したCapability Observationとadapter mappingをExact Artifact Bindingで特定した。

current releaseやcurrent mappingへ黙って追随せず、Decision時点のObservation / mappingを復元する構造になっている。

さらにContract checkerでは、bundle内にexact recordが存在する場合、Decision basisのdigest / Representation Profileが一致しないfixtureをsemantic violationとして検出する。

### 6. actual repository上でExecutable Evidenceを取得した

GitHub Actions `Contract Conformance` Run ID `33346472419`、Head SHA `9921c66f0803ddfe7810ea46c86b995f52895472`でCIがsuccessした。

17 fixtureのうちCapability F1〜F7はすべてexpected PASSとなり、negative / boundary fixtureも期待どおりに分類された。

詳細は`contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`を正本とする。

## Acceptance criteria

- [x] ADR-0019の意味境界をContract / schemaで表現できる。
- [x] TEI固有型がSOZA Universal Coreへ漏れていない。
- [x] F1〜F7のfixtureが存在する。
- [x] fixtureごとにV1〜V8のどの価値を検証するか明示した。
- [x] normalized / interpreted conditionからraw provenanceまたはProvider-specific referenceへ戻れる。
- [x] historical reconstructionが現在版への追随ではなく当時版の復元になっている。
- [x] actual repository上で再現可能なtest evidenceを得た。
- [x] 文書・fixture説明を自然な日本語で再ドラフトし、最終意味監査を行った。

## Evidence state at closure

- Capability Observation Design: **Satisfied**
- Capability Observation Fixture-scoped Executable Evidence: **Satisfied**
- Stable Representation Profile: **Not Yet Verified** — ISSUE-000009
- Actual multi-Provider production adapter interoperability: **Not Yet Verified**
- Release / Operational Evidence: **Not Yet Verified**

本IssueのResolvedはCapability Observation境界とF1〜F7のcurrent fixture conformanceを意味する。SOZA全体のExact Binding安定化やproduction Provider接続を意味しない。

## Follow-up

- ISSUE-000009 — stable Representation Profile / historical M47 digest mapping
- ISSUE-000031 — current Contract conformance全体
- ISSUE-000022 — repository baseline全体

## Natural Japanese review

F1〜F7、Capability Observation Contract / schema、CIログを戻り照合し、fixture-scoped Executable Evidenceと未検証のproduction / Representation Profileを分離した。その後、意味、条件、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
