from pathlib import Path


def replace(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"anchor not found: {path}: {old!r}")
    p.write_text(text.replace(old, new, 1))

replace(
    "plan/registry.yaml",
    "- {id: ISSUE-000065, file: plan/issue/ISSUE-000065-materialize-actual-tei-cli-execution.md, status: Open, priority: 1, related_adrs: [ADR-0013, ADR-0019, ADR-0021, ADR-0024]}",
    "- {id: ISSUE-000065, file: plan/issue/ISSUE-000065-materialize-actual-tei-cli-execution.md, status: Resolved, priority: 1, related_adrs: [ADR-0013, ADR-0019, ADR-0021, ADR-0024]}",
)

replace(
    "plan/document_review_registry.yaml",
    "note: E3a、E3b-P1、TEI executable注入境界、v0.2.0 publication / Release Evidence、KJ Atlasをlive実行するE3b-M1aに加え、actual TEI実行を狙うE3b-P2のISSUE-000065まで監査した。ISSUE-000064をM1a、ISSUE-000065をP2としてcurrent番号体系へ同期し、資格情報不足でactual stepがskipされた最初のprobeをP2成功へ読み替えていない。",
    "note: E3a、E3b-P1、TEI executable注入境界、v0.2.0 publication / Release Evidence、KJ Atlasをlive実行するE3b-M1aに加え、E3b-P2のfixed-artifact actual TEI CLI executionまで監査した。ISSUE-000065はResolvedへ同期し、最初のcredential-aware probeでactual stepがskipされた履歴と、後続fixed-artifact Evidenceを分離している。",
)

replace(
    "plan/document_review_registry.yaml",
    "note: Product ShapeとRealization / Provider Exchangeを全文監査し、E2、E3a、E3b-P1、TEI executable注入境界、E3b-M1aを同じEvidence ladder上で分離した。KJ Atlas固有responseや実装方式をUniversal semanticsへ持ち込まない境界も明示済み。",
    "note: Product ShapeとRealization / Provider Exchangeを全文監査し、E2、E3a、E3b-P1、TEI executable注入境界、E3b-P2 fixed-artifact actual TEI CLI execution、E3b-M1aを同じEvidence ladder上で分離した。TEI / KJ Atlas固有responseや実装方式をUniversal semanticsへ持ち込まず、credential運用・任意version・E4を未検証として残している。",
)

replace(
    "plan/document_review_registry.yaml",
    "note: Local Reference Product Baselineのsupported scopeをE3aまでに保ったまま、9段階candidate gate、actual publication、actual tag・GitHub Release・4 asset・package digestの対応をRelease Evidenceとして正本化した。release後のE3b-P1 / M1aはこのsupported scopeへ遡及させない。",
    "note: Local Reference Product Baselineのsupported scopeをE3aまでに保ったまま、9段階candidate gate、actual publication、actual tag・GitHub Release・4 asset・package digestの対応をRelease Evidenceとして正本化した。release後のE3b-P1 / E3b-P2 fixed-artifact / M1aはこのsupported scopeへ遡及させない。",
)

print("ISSUE-000065 resolution registry sync complete")
