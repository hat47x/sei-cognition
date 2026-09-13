# Personal Inquiry Continuity — Minimal Dogfood Surface

更新日: 2026-09-10  
状態: **Evaluation-only Executable Dogfood Surface / Not Supported Product CLI**  
関連: Issue #365 / PR #364 / `RESEARCH_DERIVED_VALIDATION_AMENDMENTS.md`

## 1. 目的

このsurfaceは、Personal Inquiry Continuity / Epistemic Resume Layer仮説を一人で実際に試すための最小local CLIである。

```text
Source Plane
  source reference
      ↓
Meaning Plane
  inquiry / record / decision
      ↓
Resume Plane
  orientation / baseline material / handoff
```

この実装はSEIのUniversal Contract、production storage format、supported CLI、固定workflowを定義しない。

## 2. 何を検証するか

first dogfoodで直接触る境界を次に限定する。

- queryなしでInquiryを開き、Orientationから現在地へ戻れるか
- Unknown / ConflictがDecision後も残るか
- RecommendationとDecisionを混同しないか
- Decision後に知った情報をhistorical basisへ遡及混入しないか
- subject / valid timeとcapture / knowledge-entry timeを区別できるか
- previous review以後のdeltaが再開に役立つか
- 元chatやLLMがなくてもread / write / review / handoffが成立するか
- Generic Summaryとの比較用に同一stateから中立なbaseline materialを作れるか

## 3. ファイル

- `dogfood_core.py` — evaluation-only state validation、mutation、Projection
- `dogfood_cli.py` — local JSONを操作するCLI
- `test_dogfood_surface.py` — focused semantic / temporal boundary tests

保存JSONのschema名は `sei.personal-inquiry-continuity-dogfood/v0` とする。この名前はevaluation artifact識別用であり、portable Universal Contractではない。

## 4. Source Plane

Sourceは原則として内容そのものではなく参照を保持する。

例:

```bash
python dogfood_cli.py source-add inquiry.json \
  --id src-chat-1 \
  --kind chat \
  --locator 'chat://external/thread-1' \
  --title '方式検討の会話' \
  --captured-at '2026-09-10T19:00:00+09:00'
```

locatorはdogfood用opaque referenceであり、CLI自身が外部sourceをfetchする機能は持たない。

```text
source reference
  != source truth
  != imported semantic meaning
```

SEIをgeneric document repositoryへ広げないことを優先する。

## 5. Meaning Plane

### Inquiryを開始

```bash
python dogfood_cli.py init inquiry.json \
  --question 'この方式を今後も採用するか' \
  --at '2026-09-10T19:00:00+09:00'
```

### Observation / Unknown等を追加

```bash
python dogfood_cli.py record-add inquiry.json \
  --kind observation \
  --id obs-1 \
  --summary '方式Aはローカルで完結する' \
  --captured-at '2026-09-10T19:05:00+09:00' \
  --source-ref src-chat-1

python dogfood_cli.py record-add inquiry.json \
  --kind unknown \
  --id unk-1 \
  --summary '長期的な保守負担はまだ分からない' \
  --captured-at '2026-09-10T19:10:00+09:00' \
  --status open
```

record kindはこのevaluation surface内の入力補助語彙であり、ここからUniversal ontologyを追加しない。

### subject timeとcapture time

過去から成立していた事実を後から知った場合は両方を記録できる。

```bash
python dogfood_cli.py record-add inquiry.json \
  --kind observation \
  --id obs-late \
  --summary '制約BはDecision以前から存在していた' \
  --subject-at '2026-09-01T09:00:00+09:00' \
  --captured-at '2026-09-10T19:20:00+09:00'
```

historical Decision basisの検査では`subject_at`ではなく、その意味を利用者 / SEIが知った時点としての`captured_at`を用いる。

```text
subject_at < decision time
  + captured_at > decision time
  => not historical basis
```

### Decisionを記録

```bash
python dogfood_cli.py decision-add inquiry.json \
  --id dec-1 \
  --statement '当面は方式Aを使う' \
  --decided-at '2026-09-10T19:15:00+09:00' \
  --basis-ref obs-1 \
  --unresolved-ref unk-1 \
  --revisit-when '保守負担が顕在化したとき'
```

later-captured recordを過去Decisionのbasisに指定するとvalidation errorにする。

## 6. Review checkpoint

Review timeはこのsurfaceではProduct-local metadataとして扱う。

```bash
python dogfood_cli.py review inquiry.json \
  --id review-1 \
  --reviewed-at '2026-09-11T09:00:00+09:00' \
  --resume-anchor '次は保守負担の実測を見る'
```

`resume_anchor`は任意であり、mandatory semantic fieldではない。古くなって害がある場合はdogfood結果に基づき削除できる。

## 7. Resume Plane

### SEI Orientation

```bash
python dogfood_cli.py orient inquiry.json
```

出力には次を分けて含める。

- current observations / hypotheses
- current unresolved
- recommendations
- latest user Decisionと当時のbasis / unresolved
- since last review
- since latest Decision
- optional resume anchor

Orientationはcanonical authorityではなく再生成可能なProjectionである。

### Generic Summary baseline material

```bash
python dogfood_cli.py baseline-material inquiry.json
```

このcommandはGeneric Summaryそのものを生成しない。同じstateから、semantic roleやSEI固有のresume構造を外した時系列text materialを生成する。

これを人間または外部AIへ渡して通常のsummaryを作り、SEI Orientationと比較する。

```text
same underlying inquiry state
  → S0 generic summarizer receives flat material
  → S1 SEI receives semantic / temporal structure
```

S0を意図的に弱く実装してS1の優位を作らない。

### AI / tool handoff

```bash
python dogfood_cli.py handoff inquiry.json
```

handoffはObservation / Unknown / Recommendation / user Decision / later changeを役割分離して返すが、それ自体をcanonical authorityにしない。

## 8. dogfood時の最小手順

一件のreal Inquiryについて、次を推奨する。

1. `init`で問いだけを作る。
2. 作業中に重要なObservation / Unknownだけを追加する。
3. Decisionが自然に発生した場合だけ`decision-add`する。
4. 中断直前またはreview時に任意でResume Anchorを残す。
5. 数日以上空ける。
6. queryや元chatを開く前に`orient`だけを見る。
7. first useful actionまでに元sourceを何件開いたか記録する。
8. `baseline-material`から通常summaryを作り、別ケースまたは順序を入れ替えて比較する。
9. later Evidenceを追加し、`since_last_review` / `since_latest_decision`を確認する。

real Inquiry本文をrepositoryへcommitする必要はない。

## 9. focused validation

このsliceでは次の11境界をfocused unit testで検査する。

- queryless Orientationがsemantic roleを保持する
- since-review deltaがcapture timeを使う
- late-arriving Evidenceをhistorical basisへ入れられない
- subject timeがknowledge-entry timeを上書きしない
- Recommendation / Decision分離
- open UnknownがDecision後も残る
- baseline materialがflatでGeneric Summaryを僭称しない
- Handoffが主要stop lineを保持する
- local JSON round-trip
- LLM / source本文なしでもProjectionを読める
- Source / Meaning / Review / Decision間のID重複を拒否する

同一ソースをisolated temporary directoryへ置いた実行では、2026-09-10に`python -m unittest -v test_dogfood.py`相当の11件がPASSした。これはfull repository checkout上のtest、production Evidence、Adoption / Outcome Evidenceではない。

CLIについても同一ソースによるisolated smoke executionで、`init → record-add → decision-add → review → late record-add → orient`を通し、late recordが`since_last_review`へ現れることを確認した。

## 10. Evidence境界

```text
focused mechanics executable
  != queryless resume value proven
  != generic summary superiority disproven
  != capture burden acceptable
  != voluntary reuse observed
  != production CLI supported
```

このsurfaceの目的は要件を証明することではなく、次のdogfoodでRequirement候補を削る・強めるための観測可能な入口を作ることである。

## 11. 次に記録するもの

次段階ではUIを増やす前に、real dogfood metadataを記録する。

優先観測:

- First Useful Action
- Source Reopen Count
- False Continuity
- Unknown / Conflict preservation
- Generic Summary vs Orientation
- Resume Anchor utility / decay
- capture burden
- voluntary reuse

これらの結果を得るまでcurrent Stable Requirementは変更しない。
