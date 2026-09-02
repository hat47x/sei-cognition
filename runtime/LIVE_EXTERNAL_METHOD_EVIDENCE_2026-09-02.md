# Live External Cognitive Method Evidence — 2026-09-02

状態: **Scoped Executable Evidence**  
対象: **PMS-06 / E3b-M1a live KJ Atlas process + deterministic model stub**

## 1. この文書の役割

この文書は、ISSUE-000064で扱う最初のlive external Cognitive Method integrationについて、**実際に確認できたことと、まだ確認していないことを分けて記録するEvidence文書**です。

今回の実証では、SOZAとは別repositoryで開発されているKJ Atlasを固定commitから取得し、KJ AtlasのFastAPI backendとmodel processをSOZAとは別processとして実際に起動します。そのうえで、KJ Atlas自身が提供する`POST /ai/suggest-card-groups`をHTTP経由で呼び、返されたgrouping候補をSOZAの既存Cognitive Method Applicationへ結び付けます。

model processにはKJ Atlas repositoryに含まれる決定的model stubを使います。このため、今回の結果を実外部AI modelの接続、model品質、KJ法としての成果品質、E3b-M1全体、Operational portabilityへ拡張しません。

```text
E3b-M1a live KJ Atlas process + deterministic model stub
  != E3b-M1b live external model-backed KJ execution
```

また、v0.2.0 Local Reference Product BaselineのRelease Evidenceは別文書でSatisfiedとなっています。M1aはrelease後に追加されたScoped Executable Evidenceであり、v0.2.0のsupported scopeへ遡及的に含めません。

## 2. 実行対象

### KJ Atlas source identity

- repository: `hat47x/kj-atlas`
- commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- entry point: `POST /ai/suggest-card-groups`

source identityはprobe-localなProvenanceとして扱います。repository名やcommitをUniversalなMethod identityへ昇格させません。

### KJ Atlas側で実際に通す経路

専用workflowでは、固定commitをcheckoutした後に次を実行します。

1. backend packageをinstallする。
2. SQLite schemaへAlembic migrationを適用する。
3. KJ Atlas同梱のdeterministic model stubを起動する。
4. FastAPI backendを別processで起動する。
5. `/healthz`でbackend readinessを確認する。
6. `POST /ai/suggest-card-groups`へactual HTTP requestを送る。
7. grouping responseを取得する。

requestには通常cardと`holdState = held`のcardを含め、held cardがKJ Atlas側の処理によって`excludedCardIds`へ分離されることを確認します。

## 3. SOZAへ戻す境界

KJ Atlas responseはreference Adapterで最小限だけshapeを検査します。次のKJ Atlas固有fieldを新しいSOZA Universal Contractへ変換しません。

- `groups`
- `label`
- `cardIds`
- `rationale`
- `excludedCardIds`
- `truncated`

actual JSONの意味内容はopaqueな`not_verified` Method outputとして保持します。

```text
KJ Atlas response shape
  != SOZA Universal Cognitive Method Contract
```

source repository、commit、entry point、result SHA-256はopaqueなProvenanceとして保持し、existing Cognitive Method Applicationから次を参照します。

- `realization_ref`
- `output_refs`
- `provenance_refs`

## 4. Recommendation / Decisionとの境界

KJ Atlasが返すgrouping候補は、カードのまとまり方についての外部Method出力です。それだけを理由にSOZAのRecommendationやDecisionへ昇格させません。

```text
KJ Atlas grouping suggestion
  != Recommendation
  != Decision
```

reference testでは、Method Application、opaque output、Provenanceを追加した後にもDecision Memoryが自動生成されないことを確認します。

## 5. failure時の境界

### invalid response

必須`groups`の欠落、空のgroup label、空のcard ID等を拒否します。invalid responseではcanonical stateを変更しません。

### duplicate target

Method output等のtarget referenceがすでに存在する場合は、処理途中で一部だけ追加しません。reference probeでは事前検査と一時storeを用いて、single-threadの検査範囲で部分更新を防ぎます。

これはproduction transaction semanticsや並行更新制御を定義するものではありません。

### JSON byte identity

Semantic Interchangeから再読したopaque JSONについて、空白や改行まで元responseとbyte-for-byte同一であることは要求しません。ここで守るのはJSONとしての意味内容です。

source bytesそのものの完全同一性が必要になった場合は、artifact / Exact Bindingとして別に要求を定めます。

## 6. actual workflow Evidence

### 再基線化前

再基線化前のPR #41でも、KJ Atlasの固定commit取得、backend install、migration、model/backend process起動、actual grouping、SOZA mapping boundary test、actual result mappingまでを実際に通しています。

代表的な成功Runは次です。

- External Method Integration E3b Run `33584876930`
- External Method Integration E3b Run `33585078576`

### current developへの再基線化後

v0.2.0 Release Evidenceを含むcurrent `develop/v0.2.0` commit `5abc9abdd16456b60ebb1f006d65377c1ca51d29`からPR #41を作り直しました。

behavior-complete head `0313f707a352dec7bec0eb40f8e3a980e74c9eae`では、次の8系統がすべてsuccessしました。

- External Method Integration E3b Run `33587455439`
- Plan integrity Run `33587455472`
- Semantic Runtime Conformance Run `33587455445`
- External Integration E3a Run `33587455452`
- External Integration E3b Run `33587455442`
- Local Package Artifact Run `33587455447`
- V6 V7 Projection Evaluation Run `33587455441`
- Release Candidate Gate Run `33587455459`

専用Run `33587455439`では、次のM1a経路がすべてsuccessしています。

- pinned KJ Atlas checkout
- backend install
- SQLite / Alembic migration
- deterministic model stub起動
- FastAPI backend起動
- actual `POST /ai/suggest-card-groups`
- SOZA method mapping boundary test
- actual external resultのSOZA semantic recordsへのmapping

Release Candidate Gate Run `33587455459`ではGate 1〜9がsuccessし、公開済みv0.2.0に対するrelease preparationとpublicationはともにskipされました。したがって、このM1a PRの検査によって既存v0.2.0をretag / republishしていません。

このEvidence記録後のdoc-only headについてはPRの最終CIで再検査します。Run IDを文書へ書き込むたびにさらに新しいRun IDが生じる再帰を避けるため、上記Run群を**behavior-complete headに対する実行Evidence**として固定し、最終doc-only headの結果はPR merge判定で確認します。

## 7. v0.2.0 Release Evidenceとの関係

`release/v0.2.0/RELEASE_EVIDENCE.md`では、Local Reference Product Baselineについてactual tag、GitHub Release、release assets、asset digest、candidate gateとの結び付きが確認され、Release EvidenceがSatisfiedとなっています。

一方、v0.2.0のsupported Realization / Provider exchange scopeはE3aまでです。

```text
v0.2.0 Release Evidence Satisfied
  != E3b-M1a included in v0.2.0

post-release E3b-M1a Evidence
  != released supported scope rewritten
```

## 8. Evidenceとして成立すること

今回のM1a実証から主張できるのは次です。

- SOZAとは別repositoryのKJ Atlasを固定revisionで取得できる。
- KJ Atlas backendとmodel stubをSOZAとは別processとして起動できる。
- KJ Atlas自身のHTTP endpointからactual grouping responseを取得できる。
- KJ Atlas固有responseをUniversal Contractへ昇格させずに保持できる。
- actual responseをexisting Cognitive Method Applicationへ結び付けられる。
- source identityとresult digestをopaque Provenanceとして保持できる。
- grouping候補をRecommendation / Decisionへ自動昇格させない。
- invalid responseやduplicate targetでreference canonical stateを部分更新しない。

## 9. このEvidenceから主張しないこと

```text
E3b-M1a PASS
  != external model quality proven
  != Cognitive Method output quality proven
  != E3b-M1b PASS
  != actual E3b-P2 TEI PASS
  != formal integration protocol finalized
  != production credential portability
  != E4 Operational portability
  != Operational Evidence
  != Adoption / Outcome Evidence
```

KJ Atlas同梱model stubの出力品質を、KJ法の妥当性や生成AI品質のEvidenceとして扱いません。

## 10. 次の未検証領域

### E3b-M1b

実外部modelを用いてKJ Atlasのlive Method pathを通した場合にも、同じ意味境界で扱えるかを確認する必要があります。

### E3b-P2

actual TEI executable / serviceを実際に接続したEvidenceは別系列です。helper subprocessによるTEI executable injection boundaryのPASSを、actual TEI executionへ昇格させません。

### E4

実運用でMethod / Providerを交換した際に、利用者が判断記憶を継続利用できることはまだ確認していません。

## 11. 自然な日本語レビュー

最新`develop/v0.2.0`のPMS-06、Realization / Provider Exchange、ISSUE-000057〜000064、v0.2.0 Release Evidence、current Cognitive Method Contract、KJ Atlas固定commit、再基線化後PR #41のactual CIを照合しました。

実外部Methodを呼べたという技術的事実を過大評価せず、KJ Atlas固有response、SOZAのMethod Application、Recommendation / Decision、Release Evidence、Operational Evidenceを別々の意味として読めるよう構成しています。

意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文をドラフトし、最終意味監査を実施しました。
