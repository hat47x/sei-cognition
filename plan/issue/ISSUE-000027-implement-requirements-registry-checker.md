# ISSUE-000027: Requirements / Scenario registryの整合性検査をactual repositoryへ実装する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0020**  
Updated: 2026-08-31

## Goal

current `requirements/PRODUCT_REQUIREMENTS.md`と`requirements/ACCEPTANCE_SCENARIOS.md`について、stable ID、参照、Value Axis、状態語彙の基本整合性をactual repository上で再現可能に検査する。

このIssueはRequirementsの意味内容を決めるものではない。ADR-0020とISSUE-000026で確定したDesign baselineに対するExecutable Acceptanceを担当する。

## Resolution

### 1. checkerをactual repositoryへ実装した

次を追加した。

```text
plan/scripts/check_requirements_registry.py
plan/scripts/test_check_requirements_registry.py
.github/workflows/requirements-registry.yml
```

checkerはPython標準ライブラリだけで動作し、Markdownを新しいsemantic authorityへ昇格させない。

将来Requirement registryをmachine-readable sourceへ移した場合は置換可能な軽量checkerとしている。

### 2. current registryの基本整合を検査できるようにした

少なくとも次を検査する。

1. `REQ-\d{4}`のID重複
2. `SCN-\d{4}`のID重複
3. Requirement → Scenario参照切れ
4. Scenario → Requirement参照切れ
5. V1〜V8以外のValue Axis
6. Requirement status
7. Acceptance state
8. historical `SOZA-PR-*` / `SOZA-NFR-*` / `SOZA-AS-*`のcurrent table混入
9. Milestone接頭辞付きID等によるcanonical table/body不整合
10. summary tableと本文registryの不一致

### 3. negative self-testを追加した

self-testでは少なくとも次を期待どおり検出する。

- REQ ID重複
- SCN ID重複
- 存在しないREQ参照
- 存在しないSCN参照
- 不正Requirement Value Axis
- 不正Scenario Value Axis
- 不正Requirement status
- 不正Acceptance state
- historical `SOZA-PR-*`のcurrent table混入
- `M49-REQ-0001`のようなMilestone接頭辞付きIDによるcanonical registry不整合

negative caseは、Requirementsの内容が「悪い」と自動判定するものではなく、ADR-0020で固定したregistry規約への不適合を検出する。

### 4. GitHub Actionsでactual branchを検証した

専用workflow `Requirements Registry Conformance`を追加し、actual `develop/v0.1.0`をcheckoutして次を実行した。

```text
python3 -m py_compile \
  plan/scripts/check_requirements_registry.py \
  plan/scripts/test_check_requirements_registry.py

python3 plan/scripts/test_check_requirements_registry.py
python3 plan/scripts/check_requirements_registry.py
```

negative coverage追加後のGitHub Actions:

- Run ID: `33346697016`
- Head SHA: `bcf707ed49b87fe03f217b67cce1da4e8788550d`
- Job: `requirements-registry`
- Conclusion: **success**

実行結果:

```text
PASS: requirements registry checker self-tests
PASS: 22 requirements / 17 scenarios
```

同じHead SHAで`plan-integrity`もsuccessしている。

## Evidence boundary

今回確認したのはcurrent registryの構造整合と規約適合である。

```text
registry checker PASS
  != Requirement semantic truth
  != implementation completeness
  != release readiness
```

REQ-0001〜REQ-0022やSCN-0001〜SCN-0017の意味内容自体が正しいことをcheckerが証明するものではない。

また、Executable Evidenceはcurrent Markdown registryとcheckerに対するものであり、Release / Operational Evidenceへ昇格させない。

## Acceptance criteria

- [x] actual repositoryにcheckerが存在する。
- [x] current REQ / SCNの相互参照を検査できる。
- [x] negative self-testで不整合を検出できる。
- [x] actual current baselineに対するPASSをGitHub Actionsで再現できる。
- [x] historical ID / Milestone付きIDのcanonical混入を検出できる。
- [x] 検査結果をDesign / Executable / Release / Operational Evidenceと混同していない。
- [x] checker説明文と本Issueを自然な日本語で再ドラフトし、最終意味監査を行った。

## Evidence state at closure

- Requirements Design Baseline: **Satisfied**
- Requirements Registry Structural Executable Evidence: **Satisfied**
- Requirement implementation coverage: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

## Dependencies / Follow-up

- ADR-0020
- ISSUE-000026 — Requirements Design baseline
- ISSUE-000022 — repository baseline全体

## Natural Japanese review

checker実装、negative self-test、actual GitHub Actionsのsuccess、current 22 Requirements / 17 ScenariosのPASSへ戻ってAcceptanceを一件ずつ照合した。その後、registry構造のExecutable EvidenceをRequirement内容そのものの正当性へ広げないよう境界を整理し、意味、条件、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
