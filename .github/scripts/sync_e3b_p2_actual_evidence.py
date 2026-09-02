from pathlib import Path


def replace(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"anchor not found: {path}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1))


# Product README
replace(
    "product/README.md",
    "現在、PMS-06ではE2、E3a、E3b-P1、E3b-M1aにScoped Executable Evidenceがあります。E3b-P2ではactual TEI専用probe経路まで具体化しましたが、最初のrunではprivate TEI取得資格情報が利用できずactual executionがskipされたため、P2自体は未検証です。一方、PMS-07はv0.2.0 Local Reference Product Baselineの範囲でRelease EvidenceがSatisfiedです。PMS-08のOperational / Adoption・Outcome Evidenceは未検証のままです。",
    "現在、PMS-06ではE2、E3a、E3b-P1、E3b-P2のfixed-artifact actual TEI CLI execution、E3b-M1aにScoped Executable Evidenceがあります。E3b-P2では固定revisionの実TEIをbuild・起動し、SOZA Adapter経由でcurrent Capability Observationへ戻せることまで確認しました。一方、SOZA Actionsからprivate TEIを継続取得するcredential運用、任意version互換性、E3b-M1b、E4は未検証です。PMS-07はv0.2.0 Local Reference Product Baselineの範囲でRelease EvidenceがSatisfiedであり、PMS-08のOperational / Adoption・Outcome Evidenceは未検証のままです。",
)
replace(
    "product/README.md",
    "- E3b-P1 public live Provider service\n- E3b-M1a live KJ Atlas process + deterministic model stub\n\nE3b-P2ではactual TEI専用testとcredential-aware workflowまで用意しましたが、actual TEI checkout / build / executionはまだ成立していません。E3b-M1b external model-backed Method executionも未検証です。",
    "- E3b-P1 public live Provider service\n- E3b-P2 fixed-artifact actual TEI CLI execution\n- E3b-M1a live KJ Atlas process + deterministic model stub\n\nE3b-P2では、固定revisionの実TEI CLIをbuild・起動し、actual `deployment-provider-plan`をSOZA Adapterでstrictに読み、current Capability Observationへ戻す範囲までScoped Executable Evidenceがあります。SOZA Actionsからprivate TEIを継続取得するcredential運用、任意version互換性、E3b-M1b external model-backed Method executionは未検証です。",
)
replace(
    "product/README.md",
    "- Realization / Provider portability: **Partial — E2 / E3a / E3b-P1 / E3b-M1a Scoped Executable Evidence available**\n",
    "- Realization / Provider portability: **Partial — E2 / E3a / E3b-P1 / E3b-P2 fixed-artifact / E3b-M1a Scoped Executable Evidence available**\n",
)
replace(
    "product/README.md",
    "- E3b-P2 actual TEI process / service: **probe path available / actual execution Not Yet Verified**\n",
    "- E3b-P2 actual TEI process / service: **fixed-artifact Scoped Executable Evidence available / credential operation・arbitrary version pending**\n",
)
replace(
    "product/README.md",
    "repositoryには、release scope確定後に得られたE3b-P1、TEI executable injection boundary、E3b-P2 acquisition probe、E3b-M1aのEvidenceや実証準備も存在します。しかし、それらを理由にv0.2.0のsupported scopeを後から広げません。",
    "repositoryには、release scope確定後に得られたE3b-P1、TEI executable injection boundary、E3b-P2 fixed-artifact actual TEI CLI execution、E3b-M1aのScoped Executable Evidenceも存在します。しかし、それらを理由にv0.2.0のsupported scopeを後から広げません。",
)
replace(
    "product/README.md",
    "E3b-P2の最初のcredential-aware runはworkflow全体としてsuccessしましたが、actual TEI stepがskipされました。そのため、P2のScoped Executable Evidenceには数えていません。",
    "E3b-P2の最初のcredential-aware runではactual TEI stepがskipされましたが、その後、固定source commitからactual `cmd/tei`をbuild・実行したEvidence artifactを作成し、同artifactをcurrent SOZA Adapterから実processとして起動できることを確認しました。最初のskip記録は履歴として保持し、後続Evidenceによってfixed-artifact範囲だけを前進させています。",
)

# Product milestone
replace(
    "product/roadmap/SOZA_PRODUCT_MILESTONES.md",
    "**Partial / E2 + E3a + E3b-P1 + E3b-M1a Scoped Executable Evidence available / E3b-P2・E3b-M1b pending.**",
    "**Partial / E2 + E3a + E3b-P1 + E3b-P2 fixed-artifact + E3b-M1a Scoped Executable Evidence available / E3b-M1b・E4 pending.**",
)
replace(
    "product/roadmap/SOZA_PRODUCT_MILESTONES.md",
    "  │    ├─ preparation: external TEI executable injection boundary\n  │    └─ current probe: pinned private TEI acquisition path / actual execution pending",
    "  │    ├─ preparation: external TEI executable injection boundary\n  │    ├─ fixed-artifact actual TEI CLI execution [Scoped Evidence]\n  │    └─ private-repository credential operation / arbitrary version [pending]",
)
old_p2 = '''ISSUE-000061では、actual TEI CLI integrationの前段として次を分離しました。\n\n```text\nTEI source / binary acquisition\n  != credential resolution\n  != external process invocation\n  != Provider-specific JSON decoding\n  != SOZA Capability Observation mapping\n```\n\n`runtime/go/teiintegration`のhelper process testはexternal executable injection boundaryを検査するものであり、actual TEI executableを実行したEvidenceではありません。\n\nISSUE-000065では、この境界へ固定revisionの実TEIを渡す専用integration testとworkflowを追加しました。最初のRun `33589190828`ではdeterministic process-boundary testはsuccessしましたが、`TEI_REPOSITORY_TOKEN`を利用できなかったため、pinned TEI checkout、`cmd/tei` build、Reference Workspace validation、SOZA Adapter経由のactual `deployment-provider-plan`実行はすべてskipされています。\n\nしたがって、workflow全体がsuccessであってもE3b-P2のScoped Executable Evidenceとは数えません。\n\n```text\ncredential-aware probe success\n  != actual TEI checkout success\n  != actual TEI execution success\n  != E3b-P2 Satisfied\n```\n\n現在の実行結果は`runtime/ACTUAL_TEI_INTEGRATION_PROBE_EVIDENCE_2026-09-02.md`に記録しています。'''
new_p2 = '''ISSUE-000061では、actual TEI CLI integrationの前段として次を分離しました。\n\n```text\nTEI source / binary acquisition\n  != credential resolution\n  != external process invocation\n  != Provider-specific JSON decoding\n  != SOZA Capability Observation mapping\n```\n\n`runtime/go/teiintegration`のhelper process testはexternal executable injection boundaryを検査するものであり、それだけではactual TEI executableのEvidenceになりません。\n\nISSUE-000065の最初のcredential-aware Run `33589190828`では、`TEI_REPOSITORY_TOKEN`を利用できずactual TEI stepがskipされました。この記録は`runtime/ACTUAL_TEI_INTEGRATION_PROBE_EVIDENCE_2026-09-02.md`へそのまま保持しています。\n\nその後、TEI commit `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`を固定し、TEI側Workflow Run `33589084290`でactual `cmd/tei`をbuildして`deployment-provider-plan`を実行しました。生成したEvidence artifactについて、current SOZA Adapterからactual `tei` binaryを別OS processとして起動し、strict decode、Capability Observation mapping / validation、Provider固有情報の非漏出を確認しています。actual Provider Plan bytesはdigest付きfixtureとして通常CIでも継続検査します。\n\n```text\nfixed source / artifact\n  + actual TEI process execution\n  + current SOZA Adapter mapping\n  = E3b-P2 fixed-artifact Scoped Executable Evidence\n\n  != private-repository credential operation proven\n  != arbitrary TEI version compatibility\n  != E4 Operational portability\n```\n\n後続Evidenceは`runtime/ACTUAL_TEI_CLI_EVIDENCE_2026-09-02.md`を正とします。'''
replace("product/roadmap/SOZA_PRODUCT_MILESTONES.md", old_p2, new_p2)
replace(
    "product/roadmap/SOZA_PRODUCT_MILESTONES.md",
    "v0.2.0のsupported release scopeはE3aまでです。E3b-P1、TEI executable注入境界、E3b-P2 probe、E3b-M1aはrelease後に積み上がったEvidenceまたは実証準備であり、既に公開済みのv0.2.0 supported scopeやRelease Evidenceを遡及的に広げません。",
    "v0.2.0のsupported release scopeはE3aまでです。E3b-P1、TEI executable注入境界、E3b-P2 fixed-artifact actual TEI CLI execution、E3b-M1aはrelease後に積み上がったScoped Executable Evidenceであり、既に公開済みのv0.2.0 supported scopeやRelease Evidenceを遡及的に広げません。",
)
replace(
    "product/roadmap/SOZA_PRODUCT_MILESTONES.md",
    "- SOZA Actionsからprivate TEIの固定revisionを取得するrepository-scoped credentialを、どの運用境界で供給するか\n- TEI executableの正式な取得・配布方式をどの時点で決めるか",
    "- SOZA Actionsからprivate TEIを継続取得するrepository-scoped credentialを、どの運用境界で供給するか\n- TEI executableの正式な取得・配布方式をどの時点で決めるか\n- fixed revision以外のTEI versionへ交換したときにも同じ意味境界を保てるか",
)
replace(
    "product/roadmap/SOZA_PRODUCT_MILESTONES.md",
    "PMS-06では、M1aのIssue番号をcurrent正本のISSUE-000064へ修正し、マージ済みPR #41とマージ後回帰checkへ記述を同期しました。また、ISSUE-000065のE3b-P2専用probeを追加しましたが、最初のrunではprivate TEI取得資格情報が利用できずactual TEI stepがskipされたため、E3b-P2は未検証のままです。workflow successをactual TEI successへ読み替えていません。",
    "PMS-06では、ISSUE-000065の最初のcredential-aware probeでactual TEI stepがskipされた履歴を保ったまま、後続の固定artifact実証を追加しました。TEI側Run `33589084290`でactual `cmd/tei`をbuild・実行し、そのartifactをcurrent SOZA Adapterから実processとして起動できたため、E3b-P2はfixed-artifact範囲でScoped Executable Evidence availableへ進みました。一方、SOZA Actionsのprivate-repository credential運用、任意TEI version互換性、E4は未検証のままです。",
)
replace(
    "product/roadmap/SOZA_PRODUCT_MILESTONES.md",
    "actual TEI execution、E3b-M1b、E4 Operational portability、production security / Storage、PMS-08のOperational / Adoption・Outcome Evidenceは未検証のままです。",
    "private-repository credential運用、任意TEI version互換性、E3b-M1b、E4 Operational portability、production security / Storage、PMS-08のOperational / Adoption・Outcome Evidenceは未検証のままです。",
)

# Realization / Provider Exchange
old_def_p2 = '''`runtime/go/teiintegration`では、外部から明示的に与えられたexecutableを呼べるAdapter境界を実装しています。\n\nhelper subprocessによるdeterministic testにはScoped Executable Evidenceがありますが、**helper subprocessのPASSはactual TEI CLI executionのEvidenceではありません**。\n\nactual `hat47x/tei-platform` executable / serviceを実際に呼んだE3b-P2は、引き続き**Not Yet Verified**です。'''
new_def_p2 = '''`runtime/go/teiintegration`では、外部から明示的に与えられたexecutableを呼べるAdapter境界を実装しています。\n\nhelper subprocessによるdeterministic testにはScoped Executable Evidenceがありますが、**helper subprocessのPASSだけをactual TEI CLI executionのEvidenceとは扱いません**。\n\nISSUE-000065では、TEI commit `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`を固定し、TEI側Workflow Run `33589084290`でactual `cmd/tei`をbuildして`deployment-provider-plan`を実行しました。得られたactual artifactをcurrent SOZA Adapterから別OS processとして起動し、strict decode、Capability Observation mapping / validation、Provider固有情報の非漏出を確認しています。\n\nしたがって、E3b-P2は**fixed-artifact scopeでScoped Executable Evidence available**です。SOZA Actionsからprivate repositoryを継続取得するcredential運用、任意TEI version互換性、production integrationは別の未検証範囲として残します。'''
replace("product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md", old_def_p2, new_def_p2)
replace(
    "product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md",
    "| external TEI executable injection boundary | Scoped Executable Evidence | ISSUE-000061 | actual TEI execution |\n| E3b-P2 actual TEI | Not Yet Verified | — | — |",
    "| external TEI executable injection boundary | Scoped Executable Evidence | ISSUE-000061 | actual TEI / credential operation |\n| E3b-P2 actual TEI | Fixed-artifact Scoped Executable Evidence | ISSUE-000065 | credential operation / arbitrary version / Operational portability |",
)
replace(
    "product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md",
    "- actual TEI executable / serviceをどの環境からEvidence付きで渡すか\n- private repository credentialをacquisition / deployment policyへどう閉じ込めるか",
    "- fixed-artifact Evidenceを維持しながら、private repository credentialをacquisition / deployment policyへどう閉じ込めるか\n- TEI executableの配布・更新経路をどの段階で正式化するか",
)
replace(
    "product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md",
    "PMS-06、ADR-0017 / 0021 / 0025、ISSUE-000057〜000064、current Cognitive Method / Capability Observation Contract、E3a / E3b Provider Evidence、v0.2.0 Release Evidence、KJ Atlas固定commitのactual integration結果を照合しました。\n\nそのうえで、外部artifactを取得したEvidence、public Providerをliveに呼んだEvidence、TEI executable注入境界、KJ Atlasをlive実行したM1aを一つの段階へ潰さず、それぞれ何を確認したかが自然に読めるよう整理しました。",
    "PMS-06、ADR-0017 / 0021 / 0025、ISSUE-000057〜000065、current Cognitive Method / Capability Observation Contract、E3a / E3b Provider Evidence、v0.2.0 Release Evidence、KJ Atlas固定commitのactual integration結果、固定TEI artifactのactual execution結果を照合しました。\n\nそのうえで、外部artifactを取得したEvidence、public Providerをliveに呼んだEvidence、TEI executable注入境界、fixed-artifact actual TEI execution、KJ Atlasをlive実行したM1aを一つの段階へ潰さず、それぞれ何を確認したかが自然に読めるよう整理しました。",
)

# Value traceability
replace(
    "product/value/SOZA_VALUE_TRACEABILITY.md",
    "- actual TEI実行前のexternal executable injection boundary\n- E3b-M1a live KJ Atlas process integration",
    "- external TEI executable injection boundary\n- E3b-P2 fixed-artifact actual TEI CLI integration\n- E3b-M1a live KJ Atlas process integration",
)
replace(
    "product/value/SOZA_VALUE_TRACEABILITY.md",
    "- E3b-P2: actual TEI process / service — **Not Yet Verified**\n- external TEI executable injection boundary — **Scoped Executable Evidence with helper subprocess**",
    "- E3b-P2: actual TEI process / service — **fixed-artifact Scoped Executable Evidence available**\n- external TEI executable injection boundary — **Scoped Executable Evidence with helper subprocess**",
)
replace(
    "product/value/SOZA_VALUE_TRACEABILITY.md",
    "Plan / Requirements / Contract conformance、semantic runtime、Representation Profile / Verifier Registry、Payload Source / Provider Adapter、Cognitive Method、V6 / V7 evaluation、Product Journey、Interaction / Packaging / Persistence / Access / Realization exchange、E3a、E3b-P1、E3b-M1a等の限定Evidenceがあります。",
    "Plan / Requirements / Contract conformance、semantic runtime、Representation Profile / Verifier Registry、Payload Source / Provider Adapter、Cognitive Method、V6 / V7 evaluation、Product Journey、Interaction / Packaging / Persistence / Access / Realization exchange、E3a、E3b-P1、E3b-P2 fixed-artifact、E3b-M1a等の限定Evidenceがあります。",
)
replace(
    "product/value/SOZA_VALUE_TRACEABILITY.md",
    "synthetic Adapter、Provider replacement journey、out-of-process exchange、E3a、E3b-P1、M1aまでscopedに検査しています。actual TEI、実外部model、実Providerの交換・廃止・移行を伴うOperational / Outcome Evidenceはありません。",
    "synthetic Adapter、Provider replacement journey、out-of-process exchange、E3a、E3b-P1、fixed-artifact actual TEI、M1aまでscopedに検査しています。任意TEI versionへの交換、実外部model、実Providerの廃止・移行を伴うOperational / Outcome Evidenceはありません。",
)
replace(
    "product/value/SOZA_VALUE_TRACEABILITY.md",
    "Provider / Persistence / Realization交換とM1a external Method processのscoped probeは増えましたが、actual TEIや実外部modelを含むproduction環境で長期的に意味を維持したOperational Evidenceはありません。",
    "Provider / Persistence / Realization交換、fixed-artifact actual TEI、M1a external Method processまでscopedなExecutable Evidenceは増えましたが、実外部modelやversion交換を含むproduction環境で長期的に意味を維持したOperational Evidenceはありません。",
)
replace(
    "product/value/SOZA_VALUE_TRACEABILITY.md",
    "current registryはADR-0001〜ADR-0030、ISSUE-000001〜ISSUE-000064を管理します。",
    "current registryはADR-0001〜ADR-0030、ISSUE-000001〜ISSUE-000065を管理します。",
)
replace(
    "product/value/SOZA_VALUE_TRACEABILITY.md",
    "- ISSUE-000064: **Resolved** — E3b-M1a live KJ Atlas Cognitive Method execution\n- その他のcurrent Issue: repository registryに従う",
    "- ISSUE-000064: **Resolved** — E3b-M1a live KJ Atlas Cognitive Method execution\n- ISSUE-000065: **E3b-P2 fixed-artifact actual TEI CLI executionのEvidence確定中**\n- その他のcurrent Issue: repository registryに従う",
)
replace(
    "product/value/SOZA_VALUE_TRACEABILITY.md",
    "- actual TEI process / serviceを用いたE3b-P2\n- 実外部modelを用いたE3b-M1b",
    "- E3b-P2で残るprivate-repository credential運用とTEI version交換\n- 実外部modelを用いたE3b-M1b",
)
replace(
    "product/value/SOZA_VALUE_TRACEABILITY.md",
    "Product Value、Value Proposition、Product Shape、Product Milestone、REQ-0001〜0022、SCN-0001〜0018、ADR-0001〜0030、5 Semantic Contract family、2 Representation Profile、current runtime / probe、E3a / E3b-P1、E3b-M1a、v0.2.0 Release Acceptance / Release Evidence、ISSUE-000063 / 000064へ戻って全体を再監査しました。\n\nv0.2.0 Release Evidenceの成立範囲をLocal Reference Product Baselineへ限定したまま、release後に得られたM1aをV2 / V4 / V5 / V8へ関係するScoped Executable Evidenceとして追跡しています。E3b-P2、M1b、E4、production readiness、Operational Evidence、Adoption / Outcome Evidenceは未検証のままです。",
    "Product Value、Value Proposition、Product Shape、Product Milestone、REQ-0001〜0022、SCN-0001〜0018、ADR-0001〜0030、5 Semantic Contract family、2 Representation Profile、current runtime / probe、E3a / E3b-P1 / E3b-P2 fixed-artifact / E3b-M1a、v0.2.0 Release Acceptance / Release Evidence、ISSUE-000063〜000065へ戻って全体を再監査しました。\n\nv0.2.0 Release Evidenceの成立範囲をLocal Reference Product Baselineへ限定したまま、release後に得られたE3b-P2 fixed-artifact actual TEI executionとM1aをScoped Executable Evidenceとして追跡しています。private-repository credential運用、任意TEI version互換性、M1b、E4、production readiness、Operational Evidence、Adoption / Outcome Evidenceは未検証のままです。",
)

# Upstream plan
replace(
    "plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md",
    "状態: **Current Upstream Planning Baseline — v0.2.0 Release Evidence / E3b-M1a / E3b-P2 acquisition probe reflected**",
    "状態: **Current Upstream Planning Baseline — v0.2.0 Release Evidence / E3b-P2 fixed-artifact / E3b-M1a reflected**",
)
replace(
    "plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md",
    "Real Method / Provider Portabilityでは、E2、E3a、E3b-P1に加え、E3b-M1aとしてKJ Atlasのlive process + deterministic model stubまでScoped Executable Evidenceが得られました。E3b-P2については、実TEI専用integration testとcredential-aware workflowまで実装し、最初のprobeでprivate repository資格情報が利用できずactual TEI stepが実行されないことを確認しています。",
    "Real Method / Provider Portabilityでは、E2、E3a、E3b-P1、E3b-M1aに加え、E3b-P2でも固定revisionのactual TEI CLIをbuild・実行し、current SOZA Adapterへ戻す範囲までScoped Executable Evidenceが得られました。最初のcredential-aware probeでactual TEI stepがskipされた履歴は保持し、後続のfixed-artifact Evidenceと混同しません。",
)
replace(
    "plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md",
    "- E3b-P2: SOZA Actionsからprivate TEIの固定revisionを取得するrepository-scoped credentialを、どの運用境界で供給するか\n- E3b-P2: 資格情報を与えた実runでactual TEI CLIのbuild / validate / `deployment-provider-plan` / Capability Observation mappingが成立するか",
    "- E3b-P2: SOZA Actionsからprivate TEIを継続取得するrepository-scoped credentialを、どの運用境界で供給するか\n- E3b-P2: fixed revision以外のTEI versionへ交換してもcurrent Adapter境界とhistorical reconstructionを保てるか",
)
old_tree = '''       ├─ P2 actual TEI process / service                 [Not Yet Verified]\n       │    ├─ external executable injection boundary     [Scoped Evidence]\n       │    └─ credential-aware acquisition probe         [actual TEI skipped]'''
new_tree = '''       ├─ P2 actual TEI process / service\n       │    ├─ external executable injection boundary     [Scoped Evidence]\n       │    ├─ fixed-artifact actual TEI CLI execution    [Scoped Evidence]\n       │    └─ credential operation / arbitrary version   [Not Yet Verified]'''
replace("plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md", old_tree, new_tree)
old_up_p2 = '''ISSUE-000065では、TEI commit `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`を固定し、実TEI専用integration testとcredential-aware workflowを追加しました。最初のRun `33589190828`ではdeterministic process-boundary testはsuccessしましたが、`TEI_REPOSITORY_TOKEN`が利用できず、actual TEI checkout / build / validate / Adapter実行はskipされました。\n\nこのため、E3b-P2は**Not Yet Verified**のままです。run全体のsuccessをactual TEI executionへ読み替えません。\n\n次の実証では、repository-scoped credentialをacquisition / deployment policy側から与え、actual checkout、`cmd/tei` build、Reference Workspace validation、`deployment-provider-plan`実行、current Capability Observation mappingまでをskipなしで通します。\n\ncredentialを利用する場合も、GitHub PATや特定Secret製品をUniversal semanticsへ持ち込まず、acquisition / deployment policy側の問題として扱います。今回のprobeだけから「残る問題は資格情報だけである」とも断定せず、actual TEIを起動した後に初めて現れるCLI / JSON / lifecycle差を引き続き検証対象にします。'''
new_up_p2 = '''ISSUE-000065では、TEI commit `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`を固定しました。最初のcredential-aware Run `33589190828`では`TEI_REPOSITORY_TOKEN`が利用できずactual TEI stepがskipされましたが、後続のTEI側Run `33589084290`でactual `cmd/tei`をbuildし、`deployment-provider-plan`をskipなしで実行しました。\n\n生成したactual artifactをcurrent SOZA Adapterから別processとして起動し、strict decode、Capability Observation mapping / validation、Provider固有情報の非漏出まで確認しています。actual Provider Plan bytesはdigest付きfixtureとして通常CIで継続検査します。したがって、E3b-P2はfixed-artifact範囲で**Scoped Executable Evidence available**へ進みました。\n\n次の探索点は、SOZA Actionsからprivate TEIを継続取得するcredential運用、TEI executableの配布・更新、fixed revision以外のversion交換、E4 Operational portabilityです。credentialを利用する場合も、GitHub PATや特定Secret製品をUniversal semanticsへ持ち込まず、acquisition / deployment policy側の問題として扱います。'''
replace("plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md", old_up_p2, new_up_p2)
replace(
    "plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md",
    "post-releaseのE3b-P1、TEI executable注入境界、E3b-P2 acquisition probe、E3b-M1aは新しいScoped Executable Evidenceまたは実証準備です。",
    "post-releaseのE3b-P1、TEI executable注入境界、E3b-P2 fixed-artifact actual TEI CLI execution、E3b-M1aは新しいScoped Executable Evidenceです。",
)
replace(
    "plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md",
    "current Product Value、Product Shape、Product Milestone、v0.2.0 Release Evidence、ISSUE-000045〜000065、E2 / E3a / E3b-P1 / E3b-M1aのactual Evidence、ISSUE-000065のE3b-P2 probe、`hat47x/tei-platform`の実CLIとprivate repository条件、KJ Atlasの固定commitとactual process実証へ戻り、現在の上流探索順序を再監査しました。",
    "current Product Value、Product Shape、Product Milestone、v0.2.0 Release Evidence、ISSUE-000045〜000065、E2 / E3a / E3b-P1 / E3b-P2 fixed-artifact / E3b-M1aのactual Evidence、`hat47x/tei-platform`の固定CLI artifactとprivate repository条件、KJ Atlasの固定commitとactual process実証へ戻り、現在の上流探索順序を再監査しました。",
)
replace(
    "plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md",
    "Product Interaction、Packaging、Product Accessの既存scoped Evidenceを「未着手」のまま残さず、Real Method / Provider Portabilityを主探索系列として維持しています。そのうえで、M1aのcurrent Issue番号をISSUE-000064へ同期し、E3b-P2は実TEI専用testとworkflowまで具体化しました。最初のprobeではprivate repository資格情報が利用できずactual TEI stepがskipされたため、次の作業点を「接続方式を考える」から「資格情報をacquisition境界で供給し、固定revisionのactual executionをskipなしで検証する」へ狭めています。",
    "Product Interaction、Packaging、Product Accessの既存scoped Evidenceを「未着手」のまま残さず、Real Method / Provider Portabilityを主探索系列として維持しています。E3b-P2では最初のcredential-aware probeのskipを成功扱いせず、その後に固定revisionのactual `cmd/tei` build / executionとSOZA Adapter mappingを別経路で実証しました。これにより次の作業点は、fixed-artifact実行そのものから、private-repository credential運用、artifact配布・更新、TEI version交換、E4へ移ります。",
)
replace(
    "plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md",
    "v0.2.0 actual Release Evidenceは成立済みとして計画へ反映し、post-releaseのE3b Evidenceやprobeによってsupported scopeを遡及的に広げていません。また、helper processをactual TEI executionへ、credential-aware workflow successをskipされたactual executionへ、deterministic model stubを実外部model品質へ昇格させない停止線を維持しています。",
    "v0.2.0 actual Release Evidenceは成立済みとして計画へ反映し、post-releaseのE3b Evidenceによってsupported scopeを遡及的に広げていません。また、helper processをactual TEI executionへ、credential-aware workflow successをskipされたactual executionへ、fixed-artifact実行をcredential運用やOperational portabilityへ、deterministic model stubを実外部model品質へ昇格させない停止線を維持しています。",
)

# Document review registry: add coverage for the new Evidence document and refresh relevant notes.
replace(
    "plan/document_review_registry.yaml",
    "  - scope: runtime/ACTUAL_TEI_INTEGRATION_PROBE_EVIDENCE_2026-09-02.md\n    status: revised\n    note: E3b-P2の最初のcredential-aware probeを記録した。Run 33589190828ではdeterministic process境界はsuccessした一方、private TEI取得資格情報が利用できずactual checkout / build / validate / Adapter executionがskipされたため、P2をNot Yet Verifiedのまま保持している。",
    "  - scope: runtime/ACTUAL_TEI_INTEGRATION_PROBE_EVIDENCE_2026-09-02.md\n    status: revised\n    note: E3b-P2の最初のcredential-aware probeを記録した。Run 33589190828ではdeterministic process境界はsuccessした一方、private TEI取得資格情報が利用できずactual checkout / build / validate / Adapter executionがskipされた事実を履歴として保持している。\n  - scope: runtime/ACTUAL_TEI_CLI_EVIDENCE_2026-09-02.md\n    status: revised\n    note: E3b-P2の後続Evidenceとして、固定TEI sourceからactual `cmd/tei`をbuild・実行し、Evidence artifactをcurrent SOZA Adapterから別processとして起動してCapability Observationへ戻した範囲を記録した。fixed-artifact Executable Evidenceとcredential運用・任意version・Operational Evidenceを分離している。",
)
replace(
    "plan/document_review_registry.yaml",
    "note: Product Value、Milestone、Interaction、Packaging、Identity / Access、Realization / Provider Exchange、v0.2.0 Release Evidence、release後のE3b-M1aとE3b-P2 acquisition probeまでをcurrent Product入口として自然な日本語で再整理済み。P2はactual execution未検証のまま明示している。",
    "note: Product Value、Milestone、Interaction、Packaging、Identity / Access、Realization / Provider Exchange、v0.2.0 Release Evidence、release後のE3b-P2 fixed-artifact actual TEI executionとE3b-M1aまでをcurrent Product入口として自然な日本語で再整理済み。credential運用・任意version・E4を未検証として分離している。",
)
replace(
    "plan/document_review_registry.yaml",
    "note: calendar deadlineではなくOutcomeとEvidenceでPMS-00〜PMS-08およびMoving Rebaselineを定義。PMS-06はE2 / E3a / E3b-P1 / E3b-M1aまでをScoped Executable Evidenceとして維持し、M1aをcurrent正本のISSUE-000064へ修正した。E3b-P2はISSUE-000065のcredential-aware probeを反映したが、actual TEI stepがskipされたため未検証のまま分離している。PMS-07はv0.2.0 Local Reference Product BaselineのRelease Evidence成立を維持し、post-release Evidenceやprobeをsupported scopeへ遡及させていない。",
    "note: calendar deadlineではなくOutcomeとEvidenceでPMS-00〜PMS-08およびMoving Rebaselineを定義。PMS-06はE2 / E3a / E3b-P1 / E3b-P2 fixed-artifact / E3b-M1aまでをScoped Executable Evidenceとして整理し、credential運用・任意version・M1b・E4を未検証として分離している。PMS-07はv0.2.0 Local Reference Product BaselineのRelease Evidence成立を維持し、post-release Evidenceをsupported scopeへ遡及させていない。",
)

print("E3b-P2 actual Evidence document sync complete")
