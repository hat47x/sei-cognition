# SOZA v0.2.0 — Local Reference Product Baseline

SOZA v0.2.0は、production完成版ではありません。現在のProduct ValueとSemantic Contractに沿って、意味・操作・保存・配布・責務分離・交換可能性を、開発者や評価者が再現して確かめられる **Local Reference Product Baseline** として公開するreleaseです。

## このreleaseに含むもの

v0.2.0では、次の範囲をsupported scopeとして固定します。

- Product Value、Product Shape、期限を置かないProduct Milestone
- current Requirements / Acceptance Scenarios / Product Journey
- current Architecture、5つのSemantic Contract、Representation Profile
- Go semantic runtimeとcurrent Contract fixture baseline
- human-oriented / machine-orientedなProduct Interaction reference Surface
- Linux / amd64のLocal Reference Package
- deterministic build / archive、checksum、durable data rootからのresume
- Product access permissionとsemantic Responsibility / Authorityの責務分離
- Selective Disclosureにおける`withheld`の保持
- in-process synthetic exchange
- out-of-process reference Realization / Provider exchange
- E3a version-pinned external artifact integration

## v0.2.0のscopeと、その後に得られたEvidence

repositoryではRelease Candidate境界の確立後も検証を続けており、E3b-P1としてpublicな外部Provider serviceを実際に呼ぶScoped Executable Evidenceや、actual TEI実行の前段となるexternal executable injection boundaryも追加されています。

これらは後続開発のEvidenceとして保持しますが、**repositoryに実装やEvidenceが存在することだけを理由に、v0.2.0のsupported scopeをE3bへ広げません**。このreleaseでsupportを主張するRealization / Provider exchangeの範囲は、Release Acceptanceで定めたE3aまでです。

```text
later scoped Evidence exists
  != v0.2.0 supported scope expanded
```

## このreleaseで主張しないこと

v0.2.0をreleaseしても、次が成立したとは扱いません。

- production serviceとしての完成
- E3b live external AI / SaaS / TEI process・service integration全体の完了
- actual TEI CLI integrationの完了
- external Cognitive Methodのlive実行
- E4 Operational portability
- production Provider / Storage interoperability
- production IdP / IAM / credential / session lifecycle
- formal RBAC / ABAC
- production security assessment
- HA / backup / DR / SLA
- formal OS / architecture support matrix
- production installer / package manager / signing
- Operational Evidence
- Adoption / Outcome Evidence

```text
Local Reference Product Baseline released
  != production readiness
```

## 配布物

GitHub Releaseには、Release Candidate Gateと同じsource commitから生成・検査した次のartifactを添付します。

- `soza-local-reference-linux-amd64.tar.gz`
- `soza-local-reference-linux-amd64.tar.gz.sha256`
- `v0.2.0-candidate-report.json`
- `release-metadata.json`

Local Reference Packageのchecksumはrelease assetに含めます。candidate reportとrelease metadataを用いることで、version、source commit、candidate gate、artifact targetを追跡できます。

## Evidenceの読み方

Release Candidate GateのPASSだけでは、actual Releaseやproduction運用を証明したことにはなりません。

actual `v0.2.0` tag、GitHub Release、release asset、tag対象commitのgate resultがそろった後に、その実在をRelease Evidenceとして別途監査します。Operational EvidenceとAdoption / Outcome Evidenceは、さらに後続の実運用・利用実績に基づいて評価します。

## 自然な日本語レビュー

v0.2.0 Release Acceptance、Product Milestone、Product Interaction、Packaging、Product Access、Realization / Provider Exchange、E3a、E3b-P1、TEI executable injection boundary、5段階Evidenceを照合しました。

そのうえで、「現在repositoryに存在するもの」と「v0.2.0でsupportを主張するもの」を分け、利用者が何をこのreleaseから期待でき、何をまだ期待すべきでないかが自然に読み取れる構成へ整理しました。意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文をドラフトし、最終意味監査を実施済みです。
