# Papaya / llama.cpp Q8 runtime candidate

Status: research runtime candidate only. No reference-provider or production promotion is implied.

Related: #543 / #597.

## Pinned upstream inspected

- Repository: `m0rphtail/papaya`
- Commit: `a76bc99bddafdac32863b2edc5319773e0cd3532`
- License: Apache-2.0
- Runtime shape:
  - llama.cpp `llama-server` for the ModernBERT encoder;
  - Q8_0 GGUF backbone;
  - PyTorch decision head loaded from safetensors;
  - Python tokenizer / request rendering;
  - local `POST /v1/systemone` HTTP facade.

Papaya is an independent runtime, not an official Laya release.

Its model acquisition path downloads from
`fr0stbit3/laya-typed-decisions-gguf`. The upstream model repository identifies
`convaiinnovations/laya-typed-decisions` as its base model and publishes the
ModernBERT backbone separately from the decision head.

This does **not** by itself prove byte identity with SEI's pinned reference:

- repository: `convaiinnovations/laya-typed-decisions`
- revision: `f9ab0b228f0fc0f14d873dbc99038f135c2da1b2`
- reference `model.safetensors` SHA-256:
  `4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e`.

The GGUF/head/tokenizer/config files therefore remain a **derived candidate
lineage** until their exact source revision and hashes are independently tied
back to the pinned reference.

## Why this candidate is interesting

Papaya targets the same broad local typed-decision problem as #597 but uses a
runtime shape that is materially different from both the pinned Python reference
and the pure-Rust Candle candidate:

```text
Python Laya reference
  = PyTorch encoder + PyTorch head

Papaya candidate
  = llama.cpp Q8 encoder
  + PyTorch head
  + Python request/tokenization layer

Rust candidate
  = Candle encoder + Candle head
```

For ARM CPUs, this split may be useful because llama.cpp already provides tuned
integer kernels while the relatively small decision head can remain outside the
encoder runtime.

This is an implementation hypothesis, not evidence that Q8 is an acceptable SEI
reference.

## Retained upstream benchmark Evidence

Papaya keeps raw **output** JSON artifacts in Git. The following blobs were
inspected directly at the pinned commit:

- Papaya Q8, 48 cases:
  `benchmarks/results/ours.json`
  blob `53fe8d4c7481d09d291dfc3914e730a5c36bbab0`;
- ONNX typed-decisions comparator, 48 cases:
  `benchmarks/results/navopw-on-typed-decisions.json`
  blob `ef9d27f18f2428d02e51e356cb2b4136a578deed`.

Recomputing the overlap from those retained JSON artifacts gives:

- common cases: 48;
- typed questions represented: 240;
- discrete Choice/Noul decisions compared: 144;
- discrete agreement: **144 / 144**;
- Score comparisons: 96;
- Score absolute-difference mean: approximately **0.00438**;
- Score maximum absolute difference: approximately **0.0189**;
- Noul probability comparisons: 72;
- Noul probability absolute-difference mean: approximately **0.00205**;
- Noul probability maximum absolute difference: approximately **0.0197**;
- Choice probability entries compared: 312;
- Choice probability absolute-difference mean: approximately **0.00142**;
- Choice probability maximum absolute difference: approximately **0.0125**.

Latency retained in the same artifacts:

- Papaya Q8: mean **11.8 s/case**, median **12.85 s/case**;
- ONNX typed-decisions comparator: mean **23.34 s/case**, median
  **24.17 s/case**.

These are upstream observations from the same Papaya repository, not SEI-local
measurements.

### Important benchmark-retention limit

The repository does **not** retain the `rows.json` benchmark input used by
`scripts/bench_compare.py`. The harness describes it as a subset of the
published typed-decisions test format, but exact input bytes / dataset revision /
selection hash are not committed beside the outputs.

The current tree also does not retain the raw result artifact behind the README's
"official PyTorch SDK = 55.5 s/case" row.

Therefore SEI may retain the Git-backed Q8-vs-ONNX output comparison above as
candidate evidence, but must not promote:

- the README's 4.8x-vs-official number; or
- task accuracy claims derived from the missing input rows

as independently reproducible SEI Evidence.

## The retained 48-case slice does not cover the current clamp difference

The Papaya output artifact contains:

- Choice questions with 4 or 5 options only;
- Score questions with 4 or 5 levels only;
- Noul questions with two outcomes.

It therefore never exercises the `choice:11+` temperature bucket.

This matters because the current SEI Python reference is Laya 0.3.20, which
clamps loaded temperatures into its accepted range before inference, whereas
Papaya reproduces Laya 0.3.4-era behavior and applies the configured temperature
with only a small numerical floor.

The shipped typed-decisions configuration contains an out-of-range
`choice:11+` temperature in the historical lineage.

Thus:

```text
144 / 144 agreement on the retained Papaya slice
  != Python Laya 0.3.20 full numeric parity
```

The known clamp-sensitive path must be exercised explicitly in any SEI parity
experiment.

## Other protocol / semantic gaps

Papaya intentionally exposes a TypeSafe-shaped `POST /v1/systemone` surface, but
wire resemblance is not provider identity.

At the pinned source:

- aliases such as `jev-latest` resolve to Papaya's own model id;
- Noul custom `labels` from current Python Laya are not represented as the same
  independent request field;
- Choice/Score expose entropy-style `confidence`;
- current Python Laya's separate `answer_confidence=max(p)` field is not emitted;
- no `routing.model == typed-decisions` attestation equivalent to the existing
  #601 logical-checkpoint gate is present.

Accordingly:

```text
accepts Jev-like request
  != Jev provider
  != pinned Python Laya response semantics
  != exact checkpoint attestation
```

## Transport finding

Papaya does **not** bypass the current ChatGPT-container transport blocker.

Its GitHub repository and CI contain source/tests only. The inspected successful
CI run has no uploaded model artifact. First-run model acquisition still fetches
GGUF/head/config/tokenizer bytes from Hugging Face.

So this candidate improves the future runtime search space, not today's model-byte
materialization path.

## P0 frozen-fixture rendering audit

The model-independent rendering subset can be checked before any checkpoint bytes
are available.

Compared source lineages:

- Python reference:
  `NandhaKishorM/laya@23a17522aa4942da6cce53a995a275760320b691`;
- Papaya:
  `m0rphtail/papaya@a76bc99bddafdac32863b2edc5319773e0cd3532`;
- SEI fixture blob:
  `2bed0f232ea845e2bda43ffd113d5cd86a9f770e`.

For the current four #597 cases, both source lineages produce the same logical
pre-tokenization content for the common request subset:

- structured-state serialization;
- `"<type> question: <instructions>"` head text;
- authored Choice option order;
- Score level rendering;
- default Noul `false / true` option rendering.

For auditability, define the rendering packet as UTF-8 JSON with compact object
separators and keys `state`, `head`, `options`, where the `state` value is
itself the exact serialized state string.

Observed SHA-256 values:

| case | rendering packet SHA-256 |
| --- | --- |
| `choice-route-a` | `1f5e5482d8934c75ad21d762ceb7f14f2fadb17767486ae2ee0a878fdcb23358` |
| `choice-route-b` | `4b5d5f0f8a19144c272d25755fecadb8fb47a3adb5725a50eb2066134c64e09f` |
| `score-urgency` | `e5f3c3e110448de9d45148e1230b660e47b4f10da7483a4eebdf50ba0a0b43b3` |
| `noul-review` | `422380a515b93446dc58aaad8a7dcd89d334f5fade2e5248f591e424094623f2` |

This completes only the logical rendering portion of P0.

It does **not** establish:

- tokenizer file identity;
- token ID identity;
- option-token truncation parity;
- marker-position identity;
- checkpoint tensor identity;
- numeric output parity.

The Papaya sequence builder tokenizes full option text and slices to 48 tokens,
whereas the current Python reference requests tokenizer-side truncation to 48
tokens. The present option strings are short, but token-level equivalence remains
a P1 observation rather than a P0 assumption.

Custom Noul labels also remain outside this common subset.

Therefore the live boundary is now narrower:

```text
logical rendering parity on frozen #597 common subset
  -> tokenizer / token-id / marker parity still required
  -> numeric parity still blocked on model bytes
```

## SEI admission sequence

If exact candidate bytes later become available, use one bounded comparison unit:

```text
G0  verify candidate file hashes and source-checkpoint binding

G1  reproduce #597 state/question serialization and token IDs
    against pinned Python 0.3.20

G2  exercise both ordinary buckets and the clamp-sensitive choice:11+ case

G3  compare the exact #597 typed probability vectors / selected answers
    using the same candidate bytes and fixture

G4  compare CPU load time / RSS / p50-p95-p99 latency

G5  validate the HTTP response contract without treating model aliases
    as provider identity

G6  only after G0-G5, consider Papaya/llama.cpp as a shipping-runtime candidate
```

The official F16/pinned Python run remains the #597 reference event. A smaller Q8
artifact must not become the teacher/reference merely because it is easier to run.
