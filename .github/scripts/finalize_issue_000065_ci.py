from pathlib import Path

path = Path("plan/issue/ISSUE-000065-materialize-actual-tei-cli-execution.md")
text = path.read_text()
old = "- [ ] Resolution反映後のPR headで対象CIをsuccessさせる。"
new = "- [x] Resolution反映後のPR headで対象CIをsuccessさせる。"
if old not in text:
    raise SystemExit("final CI checkbox anchor not found")
text = text.replace(old, new, 1)

anchor = "## Evidence state\n"
section = """## Resolution反映後のCI\n\nResolutionと台帳同期を含むPR head `afd34174ba17c8459c3546272ac8a37593b80b2d`では、次の9系統がすべてsuccessした。\n\n- Plan integrity Run `33597150206`\n- Semantic Runtime Conformance Run `33597150208`\n- External Integration E3a Run `33597150186`\n- External Integration E3b Run `33597150242`\n- External TEI Integration E3b P2 Run `33597150191`\n- External Method Integration E3b Run `33597150205`\n- V6 V7 Projection Evaluation Run `33597150252`\n- Local Package Artifact Run `33597150228`\n- Release Candidate Gate Run `33597150279`\n\nRelease Candidate GateはGate 1〜9がsuccessし、既に公開済みのv0.2.0に対するrelease preparation / publicationは意図どおりskipされた。\n\nExternal TEI Integration E3b P2のsuccessは、SOZA Actionsでprivate repository credential経路のactual stepが実行されたという意味ではない。fixed-artifact actual execution Evidenceは、TEI側Run `33589084290`と取得済みartifactを用いたSOZA Adapter実証として別に記録する。\n\n"""
if anchor not in text:
    raise SystemExit("Evidence state anchor not found")
text = text.replace(anchor, section + anchor, 1)
path.write_text(text)
print("ISSUE-000065 final CI evidence synchronized")
