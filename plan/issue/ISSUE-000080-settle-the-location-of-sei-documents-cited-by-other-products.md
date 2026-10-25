# ISSUE-000080: 他製品が引用するSEI文書の所在を確定する

Status: **In Progress**  
Priority: **2**  
Related ADRs: **ADR-0014**  
Updated: 2026-10-09

## Goal

他製品がSEIの文書として引用しているのに、SEIのどのbranchにも履歴にも存在しない5件について、SEIが次のどれを選ぶかを決める。

1. 文書を再掲する。
2. 引用を撤回する。
3. 別の番号と名前で提案し直す。

あわせて、2026-09-12に同じ日に始まったSEIの`evaluation/distributed-execution-fabric`とEKI Fabricの関係を、SEI側の文書に書くかどうかを判断する。

完了時には、引用側の5製品が「引用を直す、残す、外す」のどれかを、SEIの決定にもとづいて選べる状態になる。

## Background

### 確認済みの事実

2026-10-06に、hat47xの7リポジトリを全てfetchしたうえで、`hat47x/<repo>:<path>`の形の明示的な引用35件を、引用先の`origin/main`と照合した。引用先は22種で、うち9種が取得できなかった。SEIに関わるものは、次の5件と1件である。

存在しない5件は次のとおり。

| 引用されている文書 | 引用元 |
| --- | --- |
| `product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md` | TEI 2、CSW 1、vs-bear 1 |
| `plan/adr/ADR-0032-family-integration-apex-and-control-meaning-boundary.md` | TEI 3、MMI 2、EKI 1 |
| `product/definition/SEI_FAMILY_SEMANTIC_MAP.md` | TEI 1、MMI 2、EKI 1、CSW 1、vs-bear 1 |
| `plan/issue/ISSUE-000081-test-commitment-gaps-by-composition.md` | TEI 1、vs-bear 2 |
| `plan/issue/ISSUE-000082-derive-family-afferent-profile-from-sibling-records.md` | TEI 1 |

引用側は5製品で、延べ20か所である。この表は文書名での一致を数えたもので、`hat47x/<repo>:<path>`の形に限ると、4製品の16か所になる（EKIは、リポジトリの接頭辞を付けずに引用している）。vs-bear-simulator-galleryにも、vs-bearと同じ引用がある。

この5件は、SEIのどのremote branchにも、どのcommitの履歴にも存在しない。この環境にある他のcloneにも見つからなかった。

SEIのIssue番号は、全refを通して79が最大である。ADR-0032の番号には、別の内容の`ADR-0032-learned-component-admission-boundary`（2026-10-02、Proposed）が入っている。引用されている`ADR-0032-family-integration-…`というfile名とは別の文書である。

TEI、MMI、EKIの文書は、これらを「SEIの未統合branch `docs/family-apex-backflow-20260927`にある」と説明している。このbranchは、2026-10-06時点でSEIのremoteにない。

残る1件は、`evaluation/local-typed-comparator/README.md`である。vs-bearが1か所で引用しており、`develop/v0.2.0`と`docs/product-family-boundary`にはあるが、`main`にはない。

### 他製品の側の対応

引用側は、SEIの提案「SEIを製品群の統合の頂点に置く」（2026-09-27）の本文を取得できないまま、それぞれの立場を書いている。TEIの`product/value/TEI_PRODUCT_VALUE.md`は、提案の採否に関係なく自分の線を維持すると述べる。EKIの`product/value.md`は、この提案でもSEIは他製品へ命令する頂点にならないと述べ、比喩からRequirementやfieldを導かないとする。MMIの`02_Architecture/sei-decision-semantics-mapping.md`は、参考情報であり依存を作らないと述べる。このため、各製品の立場は文書の欠落があっても成り立っている。一方、提案の本文は、どの製品からも取得できない。

### SEI側に現にある、家族の境界を述べた文書

`product/definition/SEI_PRODUCT_SHAPE.md`の§6.4が、SUI、SEI、TEI、EKIの四者の分担を述べている。同じ箇所は、製品の親和性は必須の依存でも共有Universal Coreでも共有Evidence claimでもないと明記する。同文書は、SUI、TEI、EKIをまたぐ共通の統合標準を「Not Established」としている。MMI、CSW、vs-bearは、この四者の表に入っていない。

### 同じ日に始まったEKIとの範囲

`evaluation/distributed-execution-fabric/README.md`は2026-09-12の文書で、状態は「Evaluation-only Shared Infrastructure Boundary」である。job配置、worker fan-out、共通Job Envelope候補、scheduler候補、安全境界を扱い、§11で共有OSSを新設する条件にも触れる。EKI Fabricのリポジトリは、同じ2026-09-12に最初のcommitを持つ。この文書にEKIへの言及はない。

一方、`SEI_PRODUCT_SHAPE.md`の§6.3は、EKI Fabricを分散実行基盤として位置づけ、SEIがresource placementを正本にしないと述べている。EKI側の`research/integration/sei-cognition-mapping.md`は、この評価文書の§3と§4を引用している。

### Unknown

- 存在しない5件が、別の環境にだけ存在するかどうか。
- 評価文書の§11が想定した共有OSSが、EKI Fabricであるかどうか。

## Questions

1. 5件を、SEIの外にある未公開の場所から再掲できるか。できるなら再掲するか。
2. 再掲しない場合、SEIは引用側へ何を示すか。撤回か、別の番号と名前での提案し直しか。
3. 家族の境界について、SEIが現在の基準にする文書は、`SEI_PRODUCT_SHAPE.md`§6.4でよいか。MMI、CSW、vs-bearを、その四者の表に加えるか。
4. `evaluation/distributed-execution-fabric/README.md`に、EKIとの関係を書くか。書く場合、EKIの前身として位置づけるか、SEIが保つ部分を切り分けるか。
5. `evaluation/local-typed-comparator/README.md`をmainへ統合するかどうか。引用側は、未統合のままでは取得できない。

## Constraints

- 各製品の意味は、各製品が正本である。引用側の文書を直すのは、SEIではなく各製品である。
- 存在しない文書の内容を、他製品の引用から再構成して復元しない。引用は二次情報であり、本文ではない。
- 提案「統合の頂点」の採否は、このIssueでは決めない。
- 製品の親和性を、依存、共有Core、共有Evidence claimへ読み替えない（`SEI_PRODUCT_SHAPE.md`§6.4）。

## Required scenarios / experiments

1. 引用の抽出と照合を、同じ手順で再実行できること。手順は、各リポジトリの文書とコードから`hat47x/<repo>:<path>`と、上の5件の文書名を抽出し、引用先の`origin/main`に対して`git cat-file -e`で存在を確かめる、というものである。決定後に再実行し、SEIに関わる欠落が0件、または全件が取得不能と明記された状態になったことを記録する。
2. 決定の内容を、引用側の5製品が知る手段があること。SEIは他製品の文書を直さないため、このIssueの結果（再掲する、撤回する、提案し直す）を、各製品が参照できる場所に残す。

## Acceptance criteria

- 5件のそれぞれについて、再掲、撤回、提案し直しのどれかが決まっている。
- 決定が、`SEI_PRODUCT_SHAPE.md`か該当するADRに記録され、引用側が参照できる。
- 家族の境界を述べる基準の文書が、SEI内で一つに定まっている。
- `distributed-execution-fabric`とEKIの関係が、評価文書に書かれているか、書かない理由が残っている。
- `local-typed-comparator`のmain統合の可否が決まっている。

## Deliverables

- 5件の決定の記録
- 家族の境界の基準となる文書の指定
- `evaluation/distributed-execution-fabric/README.md`の状態表記の更新、または更新しない理由

## Resolution

一部が成立した。受け入れ基準のうち、文書の所在に関する2つが成立し、残る3つは未決である。

### 成立したこと（2026-10-09）

SEIは、branch `docs/family-apex-backflow-20260927`を`develop/v0.2.0`へmergeした（`041c3fa`）。このbranchは、それまでSEIのremoteになかった。mergeの際に、衝突した番号を振り直している。

| 引用されていた文書 | 現在の所在 |
| --- | --- |
| `product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md` | 同名で`develop/v0.2.0`にある |
| `product/definition/SEI_FAMILY_SEMANTIC_MAP.md` | 同名で`develop/v0.2.0`にある |
| `plan/adr/ADR-0032-family-integration-apex-and-control-meaning-boundary.md` | `ADR-0035-…`として`develop/v0.2.0`にある。状態はProposed |
| `plan/issue/ISSUE-000081-test-commitment-gaps-by-composition.md` | `ISSUE-000086-…`として`develop/v0.2.0`にある |
| `plan/issue/ISSUE-000082-derive-family-afferent-profile-from-sibling-records.md` | `ISSUE-000087-…`として`develop/v0.2.0`にある |

5件は、いずれも`main`には統合されていない。このIssueの背景に書いた「別の環境にだけ存在する可能性」は、実際にそうだった。

引用側の対応状況を、同じ照合手順で2026-10-09に測り直した（git管理下のファイルだけを対象に、SEIは`develop/v0.2.0`を統合の線として扱った）。

- TEIは、8か所の引用を新しい名前に直し、版（`@041c3fa`）を固定した。8か所とも取得できる。
- MMIは、旧名`ADR-0032-…`を1か所で引用している。取得できない。
- vs-bearは、旧名`ISSUE-000081-…`を2か所で引用している。取得できない。
- CSWとEKIの、SEIへの引用は取得できる。

### 未決のこと

- 家族の境界を述べる基準の文書を一つに定め、MMI、CSW、vs-bearを対象に加えるか。`SEI_PRODUCT_SHAPE.md`§6.4は四者のままである。ADR-0035は提案中で、採否は決まっていない。
- `evaluation/distributed-execution-fabric/README.md`と、EKIの関係を書くか。
- `evaluation/local-typed-comparator/README.md`を`main`へ統合するか。2026-10-09時点で、`develop/v0.2.0`にだけある。

引用側のMMIとvs-bearが旧名を直すのは、各製品の判断である。SEIは、上の対応表を示すにとどめる。

## Reopen conditions

- 存在しない5件が、別の環境から見つかった。
- 提案「統合の頂点」の本文が、決定の前提を変える形で再提示された。
- 引用側が、SEIの決定と食い違う形で文書を更新した。

## CI / verification

文書の変更のみを想定する。`plan/scripts/check_plan_registry.py`と`plan/scripts/check_document_review_registry.py`を、ローカルで実行する。

## Natural Japanese review

本文は、最初から自然な日本語で起こし、yomiyasuの静的検査（リンター）にかけた。続いて、事実の記述を一次資料と突き合わせた。突き合わせた対象は、引用の件数と所在、SEIのIssue番号とADR番号、`SEI_PRODUCT_SHAPE.md`の§6.3と§6.4、評価文書とEKIの日付、TEI、MMI、EKIが書いた立場である。引用の数え方が下限だったことは、この過程で見つかり、本文を直した。

この確認は、起票した作成者（Claude）が自分で行ったもので、SEIの別の担当による監査ではない。そのため、`document_review_registry.yaml`には`reviewed-no-change`として登録しつつ、作成者以外の確認が必要だと判断する場合は、この文書を`pending`へ戻して構わない。
