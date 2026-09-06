# TEI Version Exchange Post-run Resolution Audit — 2026-09-06

## 1. この文書の役割

本書は、ISSUE-000072のactual revision B E2→E3を実行した**後**に、得られたEvidenceをIssueのResolution条件へ戻して監査する標準手順を固定します。

actual実行前の準備は次を正とします。

- `runtime/TEI_VERSION_EXCHANGE_CURRENT_READINESS_2026-09-06.md`
- `runtime/integration/preflight_tei_version_exchange_from_github.py`

actual結果を見る前のRequirement / Scenario判定基準は次を正とします。

- `runtime/TEI_VERSION_EXCHANGE_REQUIREMENT_PREAUDIT_2026-09-05.md`

post-runのmachine-readable入口は、revision B取得経路に応じて次を使います。

- GitHub Git Data API one-shot経路: `runtime/integration/audit_tei_version_exchange_resolution.py`
- local prepositioned checkout経路: `runtime/integration/audit_tei_version_exchange_resolution_local.py`

local wrapperは既存Resolution auditを正本として再利用し、criterion 6のacquisition境界だけをlocal checkout向けに差し替えます。Requirement判定やResolution条件そのものを複製しません。

どちらのauditもIssueを自動closeしません。Stable RequirementやUniversal Contractも変更しません。

```text
resolution audit candidate
  != ISSUE-000072 automatically Resolved
  != revision B compatibility necessarily PASS
  != Stable Requirement change
  != Universal Contract change
```

## 2. post-run auditが見るもの

ISSUE-000072のResolution条件1〜8を、次の二層へ分けます。

### 2.1 machine-readableに確認する条件

条件1〜6は、actual reportと保存済みEvidenceから確認します。

1. historical revision A artifactをcurrent verifierで再検証できる。
2. revision B actual bundleのsource / binary / Provider Plan identityを記録できる。
3. E2が成立したか、不成立ならrepository-local E2 stageを判別できる。
4. E3が成立したか、不成立ならrepository-local E3 stageを判別できる。
5. revision B追加後もhistorical revision A Evidenceが固定identityへ一致する。
6. acquisition / credential provenance / artifact identity / fixed input identity / Provider compatibilityを分離して追跡できる。

結果は各条件について次のいずれかです。

```text
satisfied
blocked
manual_review
```

### 2.2 必ず人が意味を確認する条件

条件7〜8は自動完了させません。

7. REQ-0001 / REQ-0007 / REQ-0021 / SCN-0014 / SCN-0018へ再照合する。
8. 自然な日本語を最重要視した最終意味監査を行う。

adjacent RequirementとしてREQ-0022も確認します。ただしactual Product failureから独立した意味上の必要性がない限り、IssueのResolution条件やUniversal Contractへ追加しません。

## 3. GitHub one-shot経路での標準手順

GitHub Git Data APIからrevision Bを取得してone-shot runnerを使った場合、Evidence directoryには少なくとも次が残ります。

```text
tei-e3b-p2-revision-b.tar.gz
tei-version-exchange-evidence.json
tei-version-exchange-github-acquisition.json
```

historical revision A Evidence bundleをfixed inputとして使った例では、post-run auditを次のように実行します。

```bash
SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"

python3 "$SOZA_REPO/runtime/integration/audit_tei_version_exchange_resolution.py" \
  --canonical-report "$EVIDENCE_DIR/tei-version-exchange-evidence.json" \
  --github-wrapper-report "$EVIDENCE_DIR/tei-version-exchange-github-acquisition.json" \
  --historical-a-bundle "$TEI_A_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --expected-soza-head "$SOZA_HEAD" \
  --output "$AUDIT_DIR/tei-version-exchange-resolution-audit.json"
```

`AUDIT_DIR`はSOZA repository外の新規pathを使います。audit outputをSOZA checkoutへ直接書き込んでsource baselineを汚しません。

`--output`を省略した場合はJSONを標準出力へ返します。

## 4. audit resultの読み方

### 4.1 `resolutionCandidate=true`

次を意味します。

```text
Resolution条件1〜6
  = machine-readable Evidence上はsatisfied

Resolution条件7〜8
  = manual_reviewのまま
```

したがって、この時点でIssueをcloseしません。

次に条件7のRequirement / Scenario再照合を行い、その後に条件8の自然な日本語による最終意味監査を行います。

### 4.2 `resolutionCandidate=false`

`criteria`と`automatedCriteria.blockedOrManual`を確認します。

actual実行そのものが失敗したことと、Resolution auditがblockedであることは同じ意味ではありません。

例として、E2がrepository-local stage付きで失敗した場合、条件3は「停止stageを判別できた」として`satisfied`になり得ます。しかしrevision B actual bundleを得ていなければ条件2は`blocked`なので、Resolution candidateにはなりません。

## 5. E3 failureでもResolution候補になり得る理由

ISSUE-000072はrevision Bが必ずcurrent AdapterでPASSすることをResolution条件にしていません。

E2でactual revision B bundleまで成立し、その後E3がrepository-local stage付きで不成立になった場合、次を観測できています。

```text
revision B actual artifact identity
exact-A fixed input identity
E2成立
E3不成立
E3停止stage
```

この場合、条件1〜6がすべて満たされていれば`resolutionCandidate=true`になり得ます。

ただし、E3 failureをそのままUniversal Contract failureへ昇格させません。pre-auditへ戻り、まず次を確認します。

```text
Provider surface compatibility
Adapter-local DTO compatibility
mapping / validator boundary
```

Stable Requirementの変更は、actual failureとは別に、Durable Semantic Coreの意味変更が本当に必要だと確認できた場合だけ検討します。

## 6. Requirement / Scenario最終再照合

条件7では、audit reportの`criteria["7"].detail.hint`を出発点にします。

### E2 + E3 PASS

原則として次を確認します。

```text
REQ-0001  No Change または Evidence strengthened
REQ-0007  No Change または Evidence strengthened
REQ-0021  No Change または Evidence strengthened
REQ-0022  Provider-neutral Observation Evidenceの強化を確認
SCN-0014  この実験だけでSatisfiedへ上げない
SCN-0018  fixture-scoped Evidenceの強化範囲だけを確認
```

### E2 failure

build / toolchain / Provider Plan process failureだけからsemantic incompatibilityを推定しません。

```text
E2 failure
  != Stable Requirement不足
  != Universal Contract不足
```

### E2 PASS + E3 failure

まずProvider / Adapter-local compatibilityとして評価します。

strict decode、mapping、validator等の内部原因は、machine-readable Evidenceがある場合だけその高さまで特定します。stderr / stdoutの自然言語から内部stageを作りません。

## 7. natural Japanese final audit

条件8では、最終記録を自然な日本語として読み直します。

特に次を確認します。

- 「取得できた」と「互換性が成立した」を混同していないか。
- 「buildできた」と「Provider Planが成立した」を混同していないか。
- 「Provider Planが成立した」と「SOZA Adapter mappingが成立した」を混同していないか。
- `resolutionCandidate`を`Resolved`と書いていないか。
- E3 failureを直ちにProduct Requirement failureと書いていないか。
- byte driftをsemantic incompatibilityと書いていないか。
- acquisition pathやcredential方式をCapability identityへ取り込んでいないか。
- SCN-0014をTEI executable version交換だけでSatisfiedへ上げていないか。
- Evidenceの高さをExecutable / Release / Operational / Adoption・Outcomeで混同していないか。

## 8. local prepositioned checkout経路

`prepare_tei_revision_b_checkout.py`でlocal Git object databaseからexact-B checkoutを準備し、canonical `run_tei_version_exchange_evidence.py`を直接実行する経路も有効です。

この経路では、post-runに`audit_tei_version_exchange_resolution_local.py`を使います。local wrapperは既存`audit_tei_version_exchange_resolution.py`を実行した後、criterion 6だけを次の境界で再評価します。

```text
source acquisition mode
  = prepositioned_local_checkout

credential requirement
  = not_applicable

artifact identity
  = current checkoutをcanonical source verifierでexact revision Bへ再検証

fixed input acquisition
  = canonical reportのexact-A acquisition modeを保持
```

つまりlocal acquisitionにGitHub credentialが存在しないことを不足とは扱いません。

```text
credential not used
  != credential verification failure
  != semantic identity difference
```

historical revision A Evidence bundleをfixed inputとして使った例では、次のように実行します。

```bash
SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"

python3 "$SOZA_REPO/runtime/integration/audit_tei_version_exchange_resolution_local.py" \
  --canonical-report "$EVIDENCE_DIR/tei-version-exchange-evidence.json" \
  --revision-b-source-repo "$TEI_B_REPO" \
  --historical-a-bundle "$TEI_A_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --expected-soza-head "$SOZA_HEAD" \
  --output "$AUDIT_DIR/tei-version-exchange-local-resolution-audit.json"
```

`--checkout-preparation-report`は任意です。`prepare_tei_revision_b_checkout.py --report-output`で保存したJSONを指定すると、current source identityに加えて次も照合します。

- preparation schema / result
- exact revision B
- detached HEAD
- source clone HEAD / status不変
- source / output object databaseのself-contained性
- pre-publish identity verification
- reportの`outputRepository`とcurrent `--revision-b-source-repo`の一致

例:

```bash
python3 "$SOZA_REPO/runtime/integration/prepare_tei_revision_b_checkout.py" \
  --source-repo "$TEI_SOURCE_CLONE" \
  --output-repo "$TEI_B_REPO" \
  --report-output "$CHECKOUT_PREPARATION_REPORT" \
  --json

python3 "$SOZA_REPO/runtime/integration/audit_tei_version_exchange_resolution_local.py" \
  --canonical-report "$EVIDENCE_DIR/tei-version-exchange-evidence.json" \
  --revision-b-source-repo "$TEI_B_REPO" \
  --checkout-preparation-report "$CHECKOUT_PREPARATION_REPORT" \
  --historical-a-bundle "$TEI_A_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --expected-soza-head "$SOZA_HEAD" \
  --output "$AUDIT_DIR/tei-version-exchange-local-resolution-audit.json"
```

`--report-output`はsource/output checkout外の新規non-symlink pathへno-overwriteでpublishします。report publishに失敗した場合、その呼び出しで作成したexact-B checkoutも撤去します。

preparation reportを指定しなくてもcurrent exact-B checkoutは独立再検証します。ただしその場合、checkoutがどの過去操作で生成されたかという履歴までは主張せず、`checkoutPreparationProvenance.observed=false`として明示します。

```text
current exact-B source identity verified
  != checkout creation history reconstructed
```

GitHub one-shotとlocal prepositionedのどちらでも、Resolution条件1〜6の意味は同じです。acquisition mechanism固有の情報はcriterion 6内部のProvenanceへ閉じ、Capability identityやUniversal Contractへ昇格させません。

## 9. IssueをResolvedへ進める直前

次をすべて確認します。

```text
criteria 1〜6 = satisfied
criterion 7    = manual review completed
criterion 8    = manual review completed
```

そのうえで、Issue本文のResolution 1〜8を一つずつ最終照合します。

正式なRelease asset、特定credential方式、特定CI provider、特定execution host、binary byte同一性、Provider Plan byte同一性はResolution条件へ追加しません。

actual結果がPASSでもFAILでも、観測したEvidenceより高い意味を主張しません。

```text
actual Evidence
  -> resolution audit
  -> Requirement / Scenario review
  -> natural Japanese semantic audit
  -> Issue Resolution decision
```
