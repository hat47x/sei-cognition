# SEI External Standard Mapping

更新日: 2026-10-02  
状態: **Informative Mapping — non-normative / candidate correspondence / proposed via ADR-0032**

## 1. この文書の役割

この文書は、SEIのSemantic Contractの語が、外部の標準や草案のどの語に近いかを示す**参考の対応表**です。対象は、W3C PROV-O、Open Memory Protocol（v0.2草案）、C2PAの三つです。

次のいずれでもありません。

- Semantic Contract、Representation Profile、準拠の宣言
- 外部標準への依存や、外部標準が要求する出力の約束
- 外部標準との相互運用が実証されたという主張

```text
informative mapping != normative Contract
mapping candidate != interoperability proven
SEI export != compliance claim
```

対応は、意味が近い語を結ぶ候補です。意味が一致しない箇所は、一致しないと書きます。外部標準の側が正本であり、本書と食い違う場合は外部標準を正として本書を直します。

## 2. W3C PROV-O

PROV-Oは、Entity、Activity、Agentと、それらをつなぐ関係でProvenanceを表すW3Cの勧告です。

| SEIの語（Contract） | PROV-Oの語（候補） | 注記 |
|---|---|---|
| Observation、Artifact、Recommendationの内容 | `prov:Entity` | Artifactの当時内容を指すにはExact Bindingが要る。PROV側にはdigestの標準的な位置づけがない |
| Cognitive Method Application、Capability Providerの実行 | `prov:Activity` | Method ApplicationはAssuranceを意味しない。PROVはそれを区別しない |
| 人、AI、組織、Provider | `prov:Agent` | SEIはactor種別からAuthorityを推定しない。PROVのAgentの種別（Person等）も推定の根拠にしない |
| 出所の記録（Provenance） | `prov:wasAttributedTo`、`prov:wasGeneratedBy`、`prov:used` | Observationの帰属は`wasAttributedTo` |
| Semantic Lineage（`revises`、`supersedes`） | `prov:wasRevisionOf`、`prov:wasDerivedFrom` | `withdraws`に直接の対応はない。`supersedes`も、PROVの`wasRevisionOf`より強い意味を持ち得る |
| 委任（ISSUE-000081で試験中） | `prov:actedOnBehalfOf` | 委任の範囲、期限、撤回はPROVの基本の語では表せない。拡張や注記が要る |
| Decision | （対応する語なし） | 判断そのものは、ActivityとAgentの組合せとして書けるが、RecommendationとDecisionとAuthorityの区別は書けない |

PROV-Oへ写すと、SEIが区別している意味（Recommendation ≠ Decision ≠ Authority ≠ Execution、Unknown ≠ No、`not_verified` ≠ `failed`）が平らになります。したがってPROV-Oへの書き出しは、SEIの記録の**射影**であり、正本にはなりません。

## 3. Open Memory Protocol（v0.2草案）

Open Memory Protocolは、利用者が所有する記憶を、AIの間で持ち運ぶための草案です。2026-09時点のv0.2草案は「過去の決定」と来歴の制御を含み、SEIに最も近い外部の取り組みとされています（評価記録§10。草案のため、一次資料での確認が要ります）。

| SEIの語（候補） | Open Memory Protocolの語 | 注記 |
|---|---|---|
| Decision Memory | 「過去の決定」の記憶 | 草案の項目が、当時の根拠、未解決、見直しの条件まで持つかは要確認。持たなければ、書き出すときに失われる |
| Provenance | 来歴の制御 | 来歴の粒度と、SEIのExact Bindingとの対応は未確認 |
| 好み、事実（キャッシュ） | 記憶の項目 | SEIでは、ベンダーの記憶はキャッシュであり、判断の記録簿ではない（境界B2） |

B2の方針は次のとおりです。

- SEIからベンダーの記憶やOpen Memory Protocolへ渡すものは、**撤回できる投影**とする。
- ベンダーの記憶から取り込むものは、**出所つきのObservation**として受け、レビューを経る。判断の根拠にそのまま使わない。

この対応は、草案の変更に左右されます。確定した対応表は、草案が安定した後に、一次資料で確かめて作ります。

## 4. C2PA

C2PAは、コンテンツの出所と編集の履歴を、署名されたmanifestで示す標準です。C2PA 2.4は、AIによる生成や編集の開示のassertionを加えました（2026-04）。

| SEIの語（候補） | C2PAの語 | 注記 |
|---|---|---|
| Observationの出所の区分（AIの生成、AIの要約、外部資料） | AI開示のassertion、manifest | 区分の候補はISSUE-000083（E83.5）で既存のProvenanceの参照で表せるかを試す |
| 外部資料のExact Binding | manifestへの参照 | manifestの存在は、内容の真実性を意味しない |

C2PAのmanifestが付いた外部資料を扱うときは、manifestへの参照を出所の一部として保持できます。manifestの検証はC2PAの側の責務であり、SEIは検証の結果を保持するだけです。manifestが検証できないことは、資料が偽であることを意味しません（`not_verified` ≠ `failed`）。

## 5. 兄弟製品が採用しているdigestの規則との関係

外部標準ではありませんが、同じ観点で、兄弟製品の識別子とdigestの規則も整理します。収束には、正規化方式の明示的な対応が要ります。

- **MMI** — 出所ファイルのdigestは、SEIの`sei.raw-bytes+sha256/v1alpha1`と同じ規則で計算されており、整合します。一方、`hat47x.structured-artifact-observation/v0`はJCS（RFC 8785）ではなく、keyを並べ替えてJSONを書き、末尾に改行を加える方式です。そのため、digestの値はSEIの`sei.jcs+sha256/v1alpha1`と異なります。別紙マニフェスト（仕様§8.1）はdigestを持たず、出所の同一性とdigestはMMIのSource Identity Contract v1が扱います。
- **SUI** — payloadの正規化方式は、SUI側で未決です。JCSと互換にすることは選択肢の一つです。

## 6. この対応表で決めないこと

- 外部標準への書き出しの義務や、準拠の宣言
- 規制（EU AI Act、ISO/IEC 42001、日本のAI事業者ガイドライン）への適合の判定。SEIは、記録と監督のEvidenceを出せる形を持つだけです（境界B5）
- 新しいContract、Universal型、field
- 外部標準の側の変更への追従の約束

## 7. 更新の条件

- 外部標準の改訂があった、またはOpen Memory Protocolの草案が安定した。
- ISSUE-000081で、委任や消去の読み方が定まった。
- ISSUE-000083で、出所の区分や外部への束縛の再検証の手順が定まった。

## 8. Evidence状態

```text
External standard mapping: informative Design record
Interoperability with PROV-O / Open Memory Protocol / C2PA: Not Yet Verified
Executable Evidence: none added
```

## 9. 関連文書

- `CONTRACT_CATALOG.md`
- `README.md`
- `semantic-reference/SEI_SEMANTIC_REFERENCE_v1alpha1.md`
- `decision-memory/SEI_DECISION_MEMORY_v1alpha1.md`
- `profiles/README.md`
- `../product/definition/SEI_FAMILY_SEMANTIC_MAP.md`
- `../product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md`
- `../plan/adr/ADR-0032-family-integration-apex-and-control-meaning-boundary.md`
- `../plan/issue/ISSUE-000081-test-commitment-gaps-by-composition.md`
- `../plan/issue/ISSUE-000083-maintain-model-progress-robustness-register.md`

## 10. Natural Japanese review

PROV-O、Open Memory Protocol、C2PAの語を、SEIのContractの語と一つずつ対応させました。意味が近い語を結ぶ候補であり、準拠の宣言でも相互運用の実証でもないことを最初に置いています。PROV-Oへ写すと意味の区別が平らになること、Open Memory Protocolが草案であること、C2PAのmanifestが真実性を意味しないことを、各節に書きました。MMIのdigestについては、出所ファイルのdigestはraw-bytes Profileと整合し、観測契約はJCSではないためJCS Profileと異なること、SUIの正規化方式は未決であることを、確認済みの事実に合わせて書いています。

内容と留保を固定した後、**自然な日本語となることを最重要視して全文を再ドラフトし、非規範性とEvidenceの高さが変わっていないことを最終監査しました。**
