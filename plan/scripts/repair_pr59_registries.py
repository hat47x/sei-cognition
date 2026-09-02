from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected exactly one match")
    return text.replace(old, new, 1)


registry_path = Path("plan/registry.yaml")
text = registry_path.read_text(encoding="utf-8")

pairs = [
    (
        "    related_issues: [ISSUE-000019, ISSUE-000034, ISSUE-000043, ISSUE-000064, ISSUE-000066, ISSUE-000067, ISSUE-000068]\n",
        "    related_issues: [ISSUE-000019, ISSUE-000034, ISSUE-000043, ISSUE-000064, ISSUE-000066, ISSUE-000067, ISSUE-000068, ISSUE-000069]\n",
        "ADR-0017",
    ),
    (
        "    related_issues: [ISSUE-000023, ISSUE-000025, ISSUE-000026, ISSUE-000028, ISSUE-000029, ISSUE-000037, ISSUE-000039, ISSUE-000041, ISSUE-000044, ISSUE-000045, ISSUE-000048, ISSUE-000050, ISSUE-000051, ISSUE-000053, ISSUE-000062, ISSUE-000063]\n",
        "    related_issues: [ISSUE-000023, ISSUE-000025, ISSUE-000026, ISSUE-000028, ISSUE-000029, ISSUE-000037, ISSUE-000039, ISSUE-000041, ISSUE-000044, ISSUE-000045, ISSUE-000048, ISSUE-000050, ISSUE-000051, ISSUE-000053, ISSUE-000062, ISSUE-000063, ISSUE-000069]\n",
        "ADR-0018",
    ),
    (
        "    related_issues: [ISSUE-000025, ISSUE-000026, ISSUE-000027, ISSUE-000028, ISSUE-000029, ISSUE-000031, ISSUE-000037, ISSUE-000039, ISSUE-000041, ISSUE-000044, ISSUE-000045, ISSUE-000048, ISSUE-000050, ISSUE-000051, ISSUE-000053, ISSUE-000062, ISSUE-000063]\n",
        "    related_issues: [ISSUE-000025, ISSUE-000026, ISSUE-000027, ISSUE-000028, ISSUE-000029, ISSUE-000031, ISSUE-000037, ISSUE-000039, ISSUE-000041, ISSUE-000044, ISSUE-000045, ISSUE-000048, ISSUE-000050, ISSUE-000051, ISSUE-000053, ISSUE-000062, ISSUE-000063, ISSUE-000069]\n",
        "ADR-0020",
    ),
    (
        "    related_issues: [ISSUE-000022, ISSUE-000028, ISSUE-000029, ISSUE-000030, ISSUE-000031, ISSUE-000032, ISSUE-000033, ISSUE-000035, ISSUE-000038, ISSUE-000039, ISSUE-000041, ISSUE-000043, ISSUE-000044, ISSUE-000045, ISSUE-000046, ISSUE-000047, ISSUE-000048, ISSUE-000049, ISSUE-000050, ISSUE-000051, ISSUE-000053, ISSUE-000054, ISSUE-000056, ISSUE-000062, ISSUE-000063, ISSUE-000064, ISSUE-000065, ISSUE-000066, ISSUE-000067, ISSUE-000068]\n",
        "    related_issues: [ISSUE-000022, ISSUE-000028, ISSUE-000029, ISSUE-000030, ISSUE-000031, ISSUE-000032, ISSUE-000033, ISSUE-000035, ISSUE-000038, ISSUE-000039, ISSUE-000041, ISSUE-000043, ISSUE-000044, ISSUE-000045, ISSUE-000046, ISSUE-000047, ISSUE-000048, ISSUE-000049, ISSUE-000050, ISSUE-000051, ISSUE-000053, ISSUE-000054, ISSUE-000056, ISSUE-000062, ISSUE-000063, ISSUE-000064, ISSUE-000065, ISSUE-000066, ISSUE-000067, ISSUE-000068, ISSUE-000069]\n",
        "ADR-0021",
    ),
    (
        "    related_issues: [ISSUE-000043, ISSUE-000048, ISSUE-000049, ISSUE-000050, ISSUE-000064, ISSUE-000066, ISSUE-000067, ISSUE-000068]\n",
        "    related_issues: [ISSUE-000043, ISSUE-000048, ISSUE-000049, ISSUE-000050, ISSUE-000064, ISSUE-000066, ISSUE-000067, ISSUE-000068, ISSUE-000069]\n",
        "ADR-0025",
    ),
]
for old, new, label in pairs:
    text = replace_once(text, old, new, label)

issue68 = "  - {id: ISSUE-000068, file: plan/issue/ISSUE-000068-verify-actual-model-artifact-exchange-history.md, status: Resolved, priority: 1, related_adrs: [ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026]}"
issue69 = "  - {id: ISSUE-000069, file: plan/issue/ISSUE-000069-establish-cognitive-method-outcome-quality-evaluation-boundary.md, status: Open, priority: 1, related_adrs: [ADR-0017, ADR-0018, ADR-0020, ADR-0021, ADR-0025]}"
if issue69 not in text:
    if text.count(issue68) != 1:
        raise SystemExit("ISSUE-000068 Resolved row not found exactly once")
    text = text.replace(issue68, issue68 + "\n" + issue69, 1)
registry_path.write_text(text, encoding="utf-8")

review_path = Path("plan/document_review_registry.yaml")
review = review_path.read_text(encoding="utf-8")
review = replace_once(
    review,
    "    coverage: ISSUE-000001..ISSUE-000068\n",
    "    coverage: ISSUE-000001..ISSUE-000069\n",
    "Issue review coverage",
)

lines = review.splitlines()
prefix = "    note: E3a、E3b-P1、TEI executable注入境界、"
target = (
    "    note: E3a、E3b-P1、TEI executable注入境界、v0.2.0 publication / Release Evidence、"
    "E3b-P2 fixed-artifact actual TEI CLI execution、E3b-M1a、E3b-M1b、ISSUE-000067のhistorical reconstruction H1 / H2、"
    "ISSUE-000068のactual二モデル交換までをResolved Evidenceとして監査した。ISSUE-000069では、execution conformance、構造安全性、"
    "人間によるCognitive Method成果品質、Product Value / Adoption outcomeを分離する評価基線をOpen Issueとして追加した。"
    "評価基盤の実行可能性を成果品質そのもののSatisfiedへ昇格させない停止線を維持している。"
)
for index, line in enumerate(lines):
    if line.startswith(prefix):
        lines[index] = target
        break
else:
    if target not in lines:
        raise SystemExit("Issue review note not found")
review = "\n".join(lines) + "\n"

marker = "    note: current canonical fixtureから再生成可能な評価用Projection例として監査済み。\n"
block = """  - scope: evaluation/method-quality/*.md
    status: revised
    coverage:
      - evaluation/method-quality/README.md
      - evaluation/method-quality/HUMAN_REVIEW_TEMPLATE.md
    note: ISSUE-000069の評価基線として、execution conformance、機械的な構造安全性、人間によるCognitive Method成果品質、Product Value / Adoption outcomeを分離した。AI graderをcurrent正解にせず、単一総合点へ圧縮せず、カードの訴え・束ね・表札・残差を人間が記録できる自然な日本語として監査済み。
"""
if "  - scope: evaluation/method-quality/*.md\n" not in review:
    if review.count(marker) != 1:
        raise SystemExit("evaluation insertion marker not found exactly once")
    review = review.replace(marker, marker + block, 1)
review_path.write_text(review, encoding="utf-8")
