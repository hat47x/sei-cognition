# ISSUE-000041: v0.1.0のRelease Evidence境界と再現可能なrelease candidateを定義する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-09-01

## Goal

SOZA v0.1.0について、現在蓄積されているDesign / Executable Evidenceを「release済み」「運用成立済み」と読み替えることなく、**exactなsource revisionへ結び付いたrelease candidateを再現・検査できる境界**を実体化する。

そのうえで、Release Evidenceが成立するために何が追加で必要かを明示する。

```text
Executable CI PASS
  != release candidate fixed
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

本Issueでは、release candidate gateの成功だけを理由にRelease Evidenceを`Satisfied`へ昇格させない。

## Background

current repositoryでは、Product Value、Requirements、ADR、Architecture、Contract、Representation Profile、semantic runtime、synthetic Provider Adapter、Payload Source、V6 / V7 Projection evaluationについて、限定されたExecutable Evidenceが存在する。

一方、2026-09-01時点では次が存在しない。

- repository全体のversion marker
- exact source revisionへ固定したrelease candidate manifest
- release candidate専用の統合gate
- release artifact / archiveのinventoryとchecksum
- tag / published releaseへcandidateを結び付ける規則
- Release Evidence report

したがって、個別CIがsuccessしていることだけからRelease Evidenceを成立させることはできない。

## Product Value trace

### 主なValue / Requirement

- **V1 Historical Reconstruction** — 後から「何をrelease candidateとして検査したか」をexactに再構成できる必要がある。
- **V6 Human / AI Readability** — release claimと未検証範囲を人間・AIの双方が読み違えない必要がある。
- **V8 Execution Independence** — release packageやCI方式をSOZA Universal semantic authorityへ昇格させない。
- **REQ-0001** — 耐久的な意味の連続性。
- **REQ-0020** — Evidenceを超える達成主張をしない。
- **REQ-0021** — Realization / Executionを交換可能にする。
- **SCN-0017** — Evidenceが低い段階で達成主張を監査する。

### 関連するAccepted Decision

- ADR-0018 — Product Valueの権威関係と評価境界。
- ADR-0020 — Requirements TraceabilityとEvidence境界。
- ADR-0021 — Architecture / Contractの権威関係とversioning。

## Release Evidenceの二段境界

### A. Release Candidate Evidence

release candidateは、少なくとも次へexactに結び付ける。

- candidate version / release line
- Git commit SHA
- Git tree SHA
- candidate作成時刻
- candidate gateのpolicy version
- 検査したcheck set
- 各checkの結果
- known blocked / deferred work
- Evidence上限

Release Candidate Evidenceは「このrevisionをrelease候補として再現可能に検査した」ことを示す。

### B. Published Release Evidence

Release Evidenceを成立させるには、候補検査に加えて、少なくとも次が必要である。

- version / tag等によりcandidate identityがimmutably固定される。
- 公開または配布対象がある場合、そのinventoryとchecksumをcandidateへ結び付けられる。
- release note / evidence reportがcandidate revisionと一致する。
- tag / published releaseが別revisionを指していないことを検査できる。
- Release Evidenceの成立をOperational / Adoption・Outcomeへ昇格させない。

```text
Release Candidate Evidence
  + immutable publication identity
  + released artifact identity where applicable
  → Release Evidence candidate
```

実際にPublished Release Evidenceを成立させるかは、candidate gateを実体化した後に別のrelease decisionとして扱ってよい。

## Candidate gateで必須とするcurrent checks

少なくとも、同一checkout / source revisionから次を再検査する。

1. Plan integrity
2. Requirements Registry Conformance
3. Contract Conformance
4. Representation Profile Conformance
5. Semantic Runtime Conformance
6. V6 / V7 Projection Evaluation

既存workflowの過去Run IDだけを列挙してrelease candidateにしない。candidate gate自身が対象revisionから必要な検査を再実行するか、同じrevisionに対する検証結果を機械的に確認できなければならない。

## Candidate manifest

候補manifestは、少なくとも次をmachine-readableに持つ。

```text
schema
release_line
candidate_commit_sha
candidate_tree_sha
policy_version
checks[]
known_limitations[]
evidence_ceiling
```

manifestはSOZA Universal Contractではない。release engineering用のEvidence artifactとして扱う。

### evidence_ceiling

candidate gateがsuccessしても、manifestの上限は少なくとも次とする。

```text
release_candidate
```

`operational`や`adoption_outcome`をcandidate gateから生成しない。

## Known limitationsの扱い

release candidateは未解決事項を隠さない。

current baselineでは少なくとも次を区別して記録する。

- ISSUE-000021 — Deferred: design history provenance。原資料不足。
- ISSUE-000034 — Blocked: historical M47 digest/profile recovery。historical source不足。
- production Provider / Storage / Authorization / Action executionは未検証。
- Release / Operational / Adoption・Outcomeは現時点で未成立。

Blocked / Deferredがあること自体をcandidate failureとするかは、現在のrelease scopeとの関係で判断する。candidate gateはそれらを黙ってPASSへ変換しない。

## Required experiments

1. candidate manifestがexact commit SHAとtree SHAを記録する。
2. 同じrevisionからcandidate gateを再実行すると、source identityとcheck setを再構成できる。
3. required checkの一つが失敗した場合、candidate gate全体がsuccessしない。
4. required checkが欠落している場合、candidate manifestをcompleteとして扱わない。
5. candidate revision変更後はcommit / tree identityが変わる。
6. known Blocked / Deferred Issueをmanifestから黙って除外しない。
7. candidate gateのsuccessからOperational / Adoption・Outcomeを生成しない。
8. manifestのcandidate identityが空、または不正なら検査失敗とする。
9. published releaseを将来検査する場合、tag / release targetがcandidate commitと異なればRelease Evidenceを成立させない。
10. archive / packageをrelease対象にする場合、inventoryとchecksumなしでreleased artifact identityを成立させない。

## Deliverables

### 本Issueで実体化する

- `release/README.md` — Release Evidence / candidate boundary。
- `release/release-candidate-policy.json` — candidate gateのmachine-readable policy。
- `tools/check_release_candidate.py` — current revisionのrelease candidate gateとmanifest生成。
- `.github/workflows/release-candidate.yml` — 同一checkoutでcandidate gateを実行しEvidence artifactを保存するCI。
- generated candidate manifestをGitHub Actions artifactとして保存する。
- actual CI結果に基づく本Issue / Product Value Traceabilityの更新。

### candidate gate後に判断する

- repository-wide `VERSION`を導入するか。
- Git tag / GitHub ReleaseをRelease Evidenceのpublication identityとして採用するか。
- source archive以外のpackage / binary artifactをv0.1.0で配布対象にするか。
- published releaseを実際に作るタイミング。

これらをcandidate gate実装前に固定しない。

## Completion criteria

- [ ] Release Candidate EvidenceとPublished Release Evidenceを区別する。
- [ ] exact commit / tree identityをmachine-readable manifestへ記録できる。
- [ ] 6つのcurrent required checkを同一candidate revisionから再実行できる。
- [ ] required check failure / missing checkをcandidate successへ変換しない。
- [ ] known Blocked / Deferredをcandidate evidenceへ明示できる。
- [ ] candidate manifestをCI artifactとして保存できる。
- [ ] candidate gate successをRelease / Operational / Adoption・Outcomeへ過大昇格させない。
- [ ] Release Evidence成立に必要なpublication identity / artifact identityの残件を明示する。
- [ ] current conformance workflow群が回帰しない。
- [ ] 文書を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行う。

## Non-goals

- production deploymentを行うこと。
- Operational Evidenceを作ること。
- Adoption / Outcome Evidenceを作ること。
- historical M47不足を推測で埋めること。
- release工程をSOZA Universal semantic contractへ昇格させること。
- package managerや配布形式を今の段階で固定すること。
- CI成功だけを理由にv0.1.0を公開済みと宣言すること。

## Reopen / follow-up conditions

candidate gate完成後、publication方式を選ぶ場合は後続Issueへ分ける。

特に次は別Decisionになり得る。

- immutable publication identityの具体方式。
- signed tag / provenance attestation。
- reproducible source archive / binary artifact。
- SBOM / dependency provenance。
- release rollback / revocation。
- production deployment verification。

## Natural Japanese review

Product Value Traceability、Value Acceptance、REQ-0020、SCN-0017、ADR-0018 / 0020 / 0021、current CI workflow群、actual repository treeへ戻って、現在存在するEvidenceと存在しないrelease machineryを分けて整理した。その後、Executable Evidence、Release Candidate Evidence、Published Release Evidence、Operational / Adoption・Outcomeの境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最後に、candidate gate実装前の状態をRelease Evidenceとして過大評価していないことを再監査済みである。
