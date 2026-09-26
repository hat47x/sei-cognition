# Upstream Laya benchmark provenance

Status: research provenance guard only. No SEI model-quality claim.

Related: #543 / #597.

## Why this guard exists

Laya publishes several typed-decision benchmark numbers that belong to different
model/training lineages. SEI must not collapse them into one "Laya" result or
treat a specialist result as a zero-shot head-to-head against a general provider.

The upstream source inspected for this checkpoint is:

- repository: `NandhaKishorM/laya`
- Git commit: `970dc8c5f63d7b886a68409493f37d569424f933`

## Retained zero-shot result artifacts

Two upstream JSON artifacts are retained in Git and were inspected directly.

### T4 artifact

`research/results/t4_colab_benchmark.json`

- Git blob: `ddc400a430834abc30c4bd028b6238153a968eee`
- device: Tesla T4
- seed: 13
- typed-decisions test size: 2,000 decisions
- `convaiinnovations/laya` calibrated accuracy: `0.362`
- `convaiinnovations/laya-multilingual` calibrated accuracy: `0.3515`
- dropped typed-decision questions: 0 for both
- the artifact caveat explicitly says neither checkpoint trained on
  typed-decisions.

### CPU sweep artifact

`research/results/cpu_51_language_sweep.json`

- Git blob: `1cb7d5ed5c498a6919797181d0f9ecb205e05b3d`
- device: CPU
- Laya package: 0.2.0
- threads: 4
- typed-decisions test size: 2,000 decisions
- base English checkpoint accuracy: `0.3615`
- Jev values in this artifact are explicitly copied published reference points;
  Jev was not run by this experiment.

These retained artifacts support a reproducible statement about the **base**
checkpoints only.

## The 0.766 typed-decisions number is a different lineage

At the same upstream commit, `BENCHMARKS.md`, `README.md`, and
`research/README.md` report approximately `0.766` accuracy for
`laya-typed-decisions`.

That checkpoint is not the zero-shot base checkpoint measured above. Upstream
documents it as a specialist fine-tuned on the typed-decisions benchmark's own
training split:

- 1,200 training cases / 6,000 typed decisions;
- evaluation on the separate 400-case / 2,000-decision test split;
- checkpoint: `convaiinnovations/laya-typed-decisions`.

The upstream fine-tuning notebook is the generation/training path for that
specialist result. The two zero-shot retained result JSON files above do not
contain an independently replayable `laya-typed-decisions = 0.766` run record.

Therefore SEI records the 0.766 value as an **upstream specialist claim whose
training lineage is known**, not as SEI-reproduced Evidence.

## Specialist vs generalist boundary

The typed-decisions dataset itself distinguishes these regimes:

```text
specialist
  = fitted on these workflow/question spaces
  -> measures task-specific architecture / compression value

generalist
  = trained on other workflows
  -> evaluates unseen question-schema behavior
```

Accordingly:

```text
fine-tuned laya-typed-decisions result
  != zero-shot base Laya result

specialist laya-typed-decisions accuracy
  != direct generalist Jev superiority claim

published Jev reference copied into an upstream artifact
  != Jev measured in the same run
```

SEI may compare both kinds of systems, but must label the regime and provenance
separately.

## SEI #597 admission rule

For the local comparator lane:

1. the first actual L0/L1 run keeps the already pinned
   `convaiinnovations/laya-typed-decisions` checkpoint identity;
2. local latency/RSS/protocol Evidence must come from SEI's own capture, not
   upstream headline numbers;
3. any task-quality score must state whether the tested checkpoint is specialist
   or generalist relative to the evaluation cases;
4. #543 authenticated Jev Evidence remains a separate lineage;
5. Jev/Laya disagreement or quality comparison is not promoted until the same
   eligible fixture/dataset and scoring contract are used;
6. upstream README/model-card rankings are context only until locally reproduced.

This provenance guard does not change the current execution blocker: exact model
bytes still have to be materialized before the first live local Laya capture.


## Papaya Q8 vs ONNX same-checkpoint retained outputs

Papaya also retains a narrower **same-checkpoint runtime comparison** at
`m0rphtail/papaya@a76bc99bddafdac32863b2edc5319773e0cd3532`.

Exact result blobs:

- Papaya Q8: `benchmarks/results/ours.json`
  - Git blob: `53fe8d4c7481d09d291dfc3914e730a5c36bbab0`;
  - retained label: `laya-cpp`;
- comparison run: `benchmarks/results/navopw-on-typed-decisions.json`
  - Git blob: `ef9d27f18f2428d02e51e356cb2b4136a578deed`;
  - retained label: `navopw-typed`;
- upstream README Git blob:
  `ab6ca374dda4b61c38824c95d18d703327c64293`.

SEI independently recomputed the retained 48-case outputs:

- cases: 48 / input-token counts equal on 48/48;
- typed questions: 240 = Choice 72 + Noul 72 + Score 96;
- Choice selected label: **72/72 equal**;
- Noul boolean at threshold 0.5: **72/72 equal**;
- therefore upstream's **144/144 discrete agreement** means
  **Choice + Noul only**;
- Score expected-value absolute delta:
  mean **0.0043833333**, max **0.0189**;
- if Score distributions are additionally reduced to probability argmax,
  agreement is **95/96**, with one near-boundary difference at
  `security_incidents_000003 / urgency`;
- mean absolute answer-probability delta across 708 retained probability cells:
  **0.0014935**, max **0.0125**.

The retained environment reports mean latency 11.8 s for Papaya and 23.34 s for
the comparison run, a ratio of about **1.978x**. That number is upstream-host
context only, not SEI shipping performance Evidence.

Durable SEI material:

- `papaya_upstream_same_checkpoint.v1.json`;
- `compare_papaya_upstream_same_checkpoint.py`;
- `test_compare_papaya_upstream_same_checkpoint.py`.

The comparator validates the exact upstream Git blobs before recomputing the
summary. Its model-free unit tests were run locally before merge: **5/5 PASS**.

Important stop line:

```text
retained Papaya Q8 output
  vs upstream-labeled ONNX comparison output
  = useful quantization/runtime tolerance context

same-checkpoint wording in upstream README
  != independently attested ONNX model/runtime bytes

upstream Q8-vs-ONNX delta
  != Python-Laya reference parity threshold
  != SEI live-capture acceptance threshold
```

The packet therefore keeps `numeric_acceptance_threshold=false` and
`tolerance_context_only=true`. Actual #597 parity still requires the managed
Python-Laya and Papaya live artifacts introduced by #622/#624.
