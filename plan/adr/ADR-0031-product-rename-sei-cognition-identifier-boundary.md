# ADR-0031: 製品名をSEI Cognitionへ改め、identifier改名の境界を定める

Status: **Accepted**  
Related Issue: **ISSUE-000075**  
Updated: 2026-09-11

## Context

本製品はこれまで`SOZA` / `綜座`という名前で開発してきました。今回、製品名を**SEI Cognition**へ、日本語名を**井**へ改めます。`SEI`は易経の卦「井」から採ります。井は、汲んでも尽きず、誰が汲みに来ても同じ水を返す共有の泉です。実行手段・人・組織が入れ替わっても、何を見て、何を問い、何を根拠とし、何を決め、何を未解決として残したかが失われないという本製品の中心主張と、この像が対応します。

改名の動機は表示名の変更ですが、影響は表示名に留まりません。current treeでは`soza`という語が識別子として広く使われています。実測すると次のとおりです。

```text
soza を含むfile                              428
soza. で始まるdistinct identifier            105
```

このidentifier群には、性質の異なる複数のclassが混ざっています。

- portable Semantic Contractのlogical identity 5件
- Representation Profile identity 2件
- runtime verifier reference 2件
- JSON Schemaの`$id` host 5file
- 未知versionや未知Contractを表すためのnegative / boundary fixture identity 3件
- 内部record schema identity 80件
- 環境変数・CLI flag 約50種
- 文書filename、Go package path、Python局所変数名

ADR-0021は、Contractがfilenameとは別のlogical identityとexplicit versionを持つこと、そしてpre-stable段階であっても、過去のDecisionやArtifactが特定versionをbasisとしている場合には当時のversionをhistoricalに特定できることを要求しています。本製品のContract familyは`v1alpha1`としてv0.2.0 Local Reference Product Baselineでrelease済みであり、この要求はすでに発効しています。

同時に、current treeには**書き換えてはならない記録済みEvidence**があります。

- `evaluation/method-quality/historical/M1B-RUN-33596839607/` — manifestが`request.json`や`structure-report.json`のsha256を記録しており、これらのfileは`soza`文字列を含みます。内容を書き換えるとdigestが一致しなくなり、Evidence自体が自壊します。
- `runtime/evidence/`配下の日付付きbundle 37file — 当時のrunで実際に出力されたrecordです。
- `release/v0.2.0/` — releaseのsource commitをpinしています。
- 日付を持つEvidence / audit / runbook / delta文書 30件 — 当時のrun ID、head SHA、対象Contract identity、実際に実行したcommandと環境変数を記述しています。

`architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`は、すでに「historical文書をcurrent正本へrenameしたものではない」という原則を持っています。今回の改名も同じ原則の下に置きます。

一方、確認できた幸運な事実もあります。`fixtures/representation-profiles/*.json`に記録された実digest 6件は、`{"z":1,"a":[true,null,"x"]}`のような合成payloadに対するものであり、`soza`文字列を含みません。Representation Profileのconformanceは改名によって壊れません。

今回判断するのは、**どのidentifier classをどの規則で改名し、どのclassを不変として残すか**です。改名作業そのものの手順と完了条件はISSUE-000075で扱います。

## Decision

製品名を**SEI Cognition**、日本語名を**井**とします。identifierの改名は、classごとに次の規則で行います。

### 1. portable Semantic Contractのlogical identityは、versionを進めずprefixのみ改める

`v1alpha1`のまま、prefixを`soza.`から`sei.`へ改めます。

| 旧identity | 新identity |
|---|---|
| `soza.semantic-reference/v1alpha1` | `sei.semantic-reference/v1alpha1` |
| `soza.decision-memory/v1alpha1` | `sei.decision-memory/v1alpha1` |
| `soza.cognitive-method/v1alpha1` | `sei.cognitive-method/v1alpha1` |
| `soza.capability-observation/v1alpha1` | `sei.capability-observation/v1alpha1` |
| `soza.semantic-interchange/v1alpha1` | `sei.semantic-interchange/v1alpha1` |
| `soza.jcs+sha256/v1alpha1` | `sei.jcs+sha256/v1alpha1` |
| `soza.raw-bytes+sha256/v1alpha1` | `sei.raw-bytes+sha256/v1alpha1` |
| `soza.runtime.verifier/jcs+sha256/v1alpha1` | `sei.runtime.verifier/jcs+sha256/v1alpha1` |
| `soza.runtime.verifier/raw-bytes+sha256/v1alpha1` | `sei.runtime.verifier/raw-bytes+sha256/v1alpha1` |

改名は名前の変更であり、意味の変更ではありません。

```text
identifier rename
  != semantic change
  != new Contract version
```

`v1alpha2`等へ進めないのは、意味境界、invariant、field、relationの役割が一切変わらないためです。versionを進めると、意味が変わっていないにもかかわらず「何が変わったのか」という問いを後世へ残します。

JSON Schemaの`$id` host `https://soza.example/contracts/v1alpha1/*.schema.json`も`https://sei-cognition.example/contracts/v1alpha1/*.schema.json`へ改めます。

未知version・未知Contractを表すfixture identity（`soza.future-semantic`、`soza.cognitive-method/v1alpha2`、`soza.jcs+sha256/v9`）も`sei.`へ改めます。これらは「自分の名前空間にある、まだ知らない何か」を表すためのものであり、prefixが旧名のままではfixtureの意図が読めなくなります。

### 2. 本ADRのmapping tableが、v0.2.0以前のArtifactを解決する唯一の橋である

v0.2.0時点で`soza.*/v1alpha1`をbasisとして記録されたArtifactは、今後も存在し続けます。それらを解決する手段は、本ADRのmapping tableだけです。

したがって本ADRは、実装が完了した後も削除・要約・統合の対象にしません。

```text
ADR-0031 mapping table
  = historical reconstruction上の必須資料
  != 移行完了後に不要になる作業memo
```

#### 文書filename mapping

`SOZA_`で始まる文書23件を`SEI_`へ改めました。prefix以降は変更していません。

| 旧 | 新 |
|---|---|
| `architecture/SOZA_*.md` | `architecture/SEI_*.md` (3件) |
| `contracts/**/SOZA_*_v1alpha1.md` | `contracts/**/SEI_*_v1alpha1.md` (7件) |
| `product/**/SOZA_*.md` | `product/**/SEI_*.md` (13件) |
| `plan/adr/ADR-0014-soza-tei-product-boundary.md` | `plan/adr/ADR-0014-sei-tei-product-boundary.md` |
| `plan/issue/ISSUE-000016-formalize-soza-tei-product-boundary.md` | `plan/issue/ISSUE-000016-formalize-sei-tei-product-boundary.md` |

4-aと4-bの凍結文書8件は、これらの旧filenameを参照したままです。`release/README.md`、`release/v0.1.0/RELEASE_ACCEPTANCE.md`、`release/v0.2.0/RELEASE_ACCEPTANCE.md`、両`release-candidate.json`、`runtime/ACCESS_COLLABORATION_PROBE_EVIDENCE_2026-09-01.md`、`runtime/INTERACTION_PROBE_EVIDENCE_2026-09-01.md`、`runtime/LIVE_EXTERNAL_PROVIDER_EVIDENCE_2026-09-02.md`が該当します。

これらのlinkはcurrent treeでは解決しません。当時のcommitでは解決しました。凍結文書のlinkを現在のpathへ書き換えるより、当時参照していたpathを残してこのtableで橋渡しするほうが、記録として正確です。

### 3. 内部record schema identityは、新規emit分のみ改める

`soza.tei-*`、`soza.runtime-version-exchange-*`、`soza.method-quality-*`、`soza.release-*`、`soza.plan-registry/v1`等の内部record schema identityは80件あります。これを二つに分けます。

| 区分 | 件数 | 規則 |
|---|---|---|
| live code / toolからも参照されるもの | 58 | emit側を`sei.*`へ改める。読み取り側は旧identityも受け付ける。 |
| 記録済みEvidence内にのみ存在するもの | 22 | **一切触れない。** |

読み取り側が旧identityを受け付けなければならないのは、記録済みEvidenceを検証するcheckerが、当時のrecordを読めなくなるためです。

```text
emitterが書くidentity      = sei.*
readerが受け付けるidentity  = sei.* および soza.*
```

この双方向受理は互換のための恒久措置であり、期限を切りません。記録済みEvidenceが存在する限り必要です。

### 4. 記録済みEvidenceは改名しない

記録済みEvidenceは、当時実際に何が観測されたかの記録です。当時のrecordへ現在の名前を書き込むことは、観測記録の改竄にあたります。

```text
記録の改名
  != 記録の更新
  = 記録の破壊
```

記録の性質が二種類あるため、規則も二つに分けます。

#### 4-a. byte単位で不変とするもの

次の配下は、file内容をbyte単位で変更しません。

```text
evaluation/method-quality/historical/
runtime/evidence/
release/
```

これらは、過去のrunが実際に出力したmachine-readable recordか、その内容をdigestで拘束したmanifestです。`evaluation/method-quality/historical/M1B-RUN-33596839607/review-manifest.json`は、`soza`文字列を含むfileのsha256を記録しているため、内容を書き換えた瞬間にEvidenceが自壊します。

#### 4-b. 過去の観測記述として`soza`を残すもの

日付を持つEvidence / audit / runbook / delta文書 **30件**では、`soza`を含む記述を変更しません。

```text
contracts/CONFORMANCE_EVIDENCE_2026-08-31.md
contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md
runtime/*_2026-*.md
runtime/integration/RUNTIME_VERSION_EXCHANGE_RECOVERED_EVIDENCE_2026-09-05.md
```

これらの文書に現れる`soza`は二種類あり、いずれも過去の事実です。

- 当時のconformance runが対象としたContract identity（例: `soza.semantic-reference/v1alpha1`）
- 当時実際に実行したcommandと環境変数（例: `SOZA_REPO=/path/to/soza`）

当時のrunは`soza.*`を対象として実行され、`SOZA_REPO`を読んで動きました。これを`sei.*`へ書き換えると、実行されなかったcommandを実行したことにし、検証されなかったidentityを検証したことにします。

4-aと異なり、これらの文書はcurrent維持対象から外れるわけではありません。禁じるのは、過去の観測記述としての`soza`を現在の名前へ置き換えることだけです。

#### 4-c. ADRとIssueは凍結しない

`plan/adr/`と`plan/issue/`は改名対象です。

ADRは過去に判断した記録であると同時に、ADR-0021が定めるとおりcurrent Contractの権威そのものです。たとえばADR-0023は「current Representation Profile baseline」を定義しています。この文書が現行と異なるidentityを示したままでは、ADRが現在の状態について誤った記述をすることになります。Issueも、Resolvedであっても参照しているのは現行のContractです。

```text
過去のrunが何を実行し何を観測したかの記録   → 凍結する (4-a, 4-b)
設計判断・要求・Contract定義を述べる文書     → 改名する (4-c)
```

本ADR自身とISSUE-000075は例外です。どちらも改名そのものを主題とし、旧identityと新identityの両方を保持する必要があります。この二つで`soza`を一律に置換すると、mapping tableが片側を失い、Issueの「旧identityも受け付ける」という記述が「新identityを受け付ける」という無意味な文へ変わります。実際、最初の一括改名でISSUE-000075の本文がこの形で壊れ、改名前の内容へ戻しました。

### 5. repositoryとGo module pathを改める

```text
github.com/hat47x/soza            → github.com/hat47x/sei-cognition
github.com/hat47x/soza/runtime/go → github.com/hat47x/sei-cognition/runtime/go
```

`runtime/go/cmd/soza-package-probe`、`soza-reference-method`、`soza-reference-provider`も追随します。

記録済みEvidence文書に書かれた旧repository URLは、上記4の規則により変更しません。GitHubのrepository renameによるredirectと、本ADRのmapping tableで解決します。

### 6. 環境変数・CLI flagは互換期間を設けない

`SOZA_ROOT`、`SOZA_REPO`、`SOZA_HEAD`、`SOZA_GO_*`、`SOZA_TEI_*`、`SOZA_RUNTIME_EXCHANGE_*`等の約50種と、`--soza-repo-root`、`--expected-soza-head`等のflagは、`SEI_*` / `--sei-*`へ一斉に改めます。

これらはoperator向けの操作面であり、記録済みEvidenceの意味を担っていません。互換aliasを残すと二つの名前が長期に並存し、どちらが正かが不明瞭になります。current baselineは単一開発者によるlocal referenceであり、外部operatorへの配布実績がないため、一斉切り替えの費用が互換維持の費用を下回ります。

## Alternatives considered

### 新しいContract versionへ進める

`sei.*/v1alpha2`として新設し、`soza.*/v1alpha1`をsupersededとして定義ごと残す案です。ADR-0003のrevision / supersession模型に素直に乗り、互換性の観点では最も安全でした。

採用しませんでした。supersessionは意味の変化を伴う場合の道具です。意味が変わっていないのにversionを進めると、Contractの意味変遷史へ実体のない一段を挿入することになり、後からこのContract familyを読む者に「v1alpha1とv1alpha2で何が変わったのか」という答えのない問いを残します。identifierの綴りが変わったことは、mapping tableで表現するほうが正確です。

### Contract identityを`soza.*`のまま据え置く

製品名だけ改め、wire上のidentifierはstable `v1`へ上げるときまで触れない案です。schema、fixture、runtimeへの変更が一切不要で、作業量は最小でした。

採用しませんでした。本製品はSemantic Lineageと名前の一貫性そのものを価値として主張しています。製品名とwire identityが恒久的に食い違う状態は、その主張と正面から矛盾します。また据え置きは判断の回避であり、stable `v1`の時点で同じ判断がより高い費用で再来します。

### tree全体を一括text置換する

`soza`を`sei`へ機械的に置換する案です。

採用しませんでした。記録済みEvidenceを破壊します。特に`evaluation/method-quality/historical/M1B-RUN-33596839607/`は、`soza`文字列を含むfileのsha256をmanifestへ記録しているため、置換した瞬間にdigestが一致しなくなります。identifier classごとに規則が異なることが、本ADRの中心です。

## Consequences

### Positive

- 製品名、日本語名、wire identity、repository、module pathが一つの名前で揃う。
- 名前が変わっても意味と根拠が失われないことを、本製品自身の改名で実証する機会になる。本ADRのmapping tableは、その最初の実例である。
- 記録済みEvidenceを不変として扱う原則が、Architecture領域からEvidence領域へ明示的に拡張される。

### Costs / Risks

- 読み取り側が`sei.*`と`soza.*`の双方を受け付ける状態が恒久化する。実装の分岐が一つ増え、その理由を知らない者が後から片方を削除する危険がある。code comment側にも本ADRへの参照を残して緩和する。
- v0.2.0以前を参照する外部資料は、本ADRを読まないと解決できない。
- 改名途中のcommitでは、tree内へ新旧identityが混在する。Phase単位でcheckerを通し、混在状態でreleaseしない。
- `sei`という短いprefixは、他領域の語と衝突する可能性が旧prefixより高い。ただしcurrent tree上の衝突は0件である。

## Revisit conditions

- stable `v1`へ進める際、identifier体系そのものを再設計する必要が生じた。
- 外部実装が`soza.*` identityを実際に参照している事例が確認され、双方向受理だけでは不足することが判明した。
- `sei.` prefixが他のContract名前空間と実際に衝突した。
- 記録済みEvidenceを不変とする規則が、historical reconstructionの要求を満たせない事例が見つかった。

## Evidence

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

本ADRを支えるのは、現時点では**Design Evidenceのみ**です。

確認済みの事実として、current tree上のidentifier実測値（`soza`を含むfile 428、distinct identifier 105、内部record schema 80のうちlive参照58 / 記録済みEvidence内のみ22、4-b対象の日付付き文書30）、`fixtures/representation-profiles/*.json`の実digestが`soza`文字列を含まないこと、`sei`および`井`がcurrent tree上で衝突0件であること、`.github/workflows`が存在せずCI追随作業が発生しないことを記録します。

なお`evaluation/method-quality/historical/`と`runtime/evidence/`に加えて日付付きEvidence文書22件を4-bとして分離したのは、本ADR起草後にtreeを再走査して判明した範囲です。当初の凍結範囲は`runtime/`配下のdated documentを取りこぼしていました。

Executable Evidenceは、ISSUE-000075の各Phaseでchecker・test・fixtureを実行した時点で成立します。本ADRをAcceptedにすることは、改名作業の完了を意味しません。

## Follow-up

- ISSUE-000075で改名作業をPhase 1〜4に分けて実施する。
- `plan/registry.yaml`、`plan/document_review_registry.yaml`へ本ADRとISSUE-000075を登録する。
- `architecture/TRACEABILITY.md`、`contracts/TRACEABILITY.md`、`contracts/CONTRACT_CATALOG.md`を新identityへ同期する。
- `evaluation/`配下へ、Architecture領域の`HISTORICAL_ARCHITECTURE_MAPPING.md`と同趣旨の名称mapping注記を置く。

## Natural Japanese review

内容・構造を確定した後、自然な日本語を最重要視して全文を再ドラフトした。再ドラフト前後で、改名するclassとしないclassの区分、versionを進めない理由、記録済みEvidenceを不変とする規則、双方向受理の恒久性、Evidenceの高さがDesign Evidenceに留まることが変わっていないことを確認した。
