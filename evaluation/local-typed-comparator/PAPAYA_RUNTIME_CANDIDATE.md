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



## P1b reference-side tokenizer identity

The original reference-side tokenizer can now be narrowed more strongly from an
independent conversion receipt, without claiming that Papaya's copied file has
the same bytes.

The published `aac6fef/laya-typed-decisions-coreml` release records, in one
`coreml_config.json`:

- source repository: `convaiinnovations/laya-typed-decisions`;
- source revision:
  `f9ab0b228f0fc0f14d873dbc99038f135c2da1b2`;
- source weights SHA-256:
  `4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e`;
- `tokenizer/tokenizer.json` bytes: **3,583,228**;
- `tokenizer/tokenizer.json` SHA-256:
  `6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30`.

This independently source-binds the same tokenizer hash already reported by
other Laya-family conversion manifests to SEI's exact pinned standalone
checkpoint revision.

The Papaya model acquisition path, however, reads its tokenizer from
`fr0stbit3/laya-typed-decisions-gguf`. That repository says it is a conversion
of `convaiinnovations/laya-typed-decisions`; its committed `tokenizer.json`
is also 3.58 MB and was added in a single verified upload commit. Public source
inspection shows matching tokenizer structure/config and sampled content, but
that repository does not publish a per-file SHA-256 receipt comparable to the
Core ML manifest.

Therefore split the P1b claim explicitly:

```text
reference tokenizer identity
  = independently source-bound to
    6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30

Papaya/fr0stbit3 tokenizer lineage
  = strongly consistent with the same source
  != byte-attested to the same SHA-256
```

Do not use equal byte size, matching sampled regions, or a base-model declaration
as a substitute for hashing the candidate-side file.

The reference side of P1c is now closed by retained exact-token Evidence below.
The Papaya/fr0stbit3 **candidate side** remains open until that tokenizer file is
independently byte-attested or replayed.

## P1c exact reference token / marker fixture

The reference tokenizer bytes are now available through an independent GitHub
retention path without relying on the current Hugging Face/Xet transport.

Pinned retained source:

- repository: `MatteoGauthier/laya-portable`;
- revision: `3dc028023929432b4a3d76b1a8ee050d0e5ccd7f`;
- path: `packages/laya-js/src/tokenizer/tokenizer.json`;
- Git blob: `2f4d8583e507b7466d2490e2d6c045647a822698`;
- UTF-8 bytes: **3,583,228**;
- independently recomputed SHA-256:
  `6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30`.

The recomputed digest exactly matches the reference tokenizer identity frozen in
P1b.

The same pinned repository retains a pure-JS ByteLevel BPE implementation and a
typed-decisions fuzz fixture:

- implementation:
  `packages/laya-js/src/laya-bpe.ts`,
  blob `58cabadbab133e162d4e4e7e792ec63932ab86c7`;
- fixture:
  `packages/test-vectors/vectors/bpe-fuzz.typed-decisions.json`,
  blob `be6c2982f2d088c5d249cd69d65e4695dc126040`.

Replaying that fixture against the exact tokenizer bytes produced **206 / 206
PASS** before generating SEI token Evidence.

The resulting reference-side token fixture is retained at:

`reference_token_fixture.v1.json`

with schema:

`sei.local-typed-comparator-reference-token-fixture/v1`.

For the exact frozen SEI fixture blob
`2bed0f232ea845e2bda43ffd113d5cd86a9f770e`:

| case | tokens | marker positions |
| --- | ---: | --- |
| `choice-route-a` | 72 | `[16, 21, 28]` |
| `choice-route-b` | 72 | `[16, 23, 30]` |
| `score-urgency` | 71 | `[14, 19, 25, 30]` |
| `noul-review` | 70 | `[16, 26]` |

The artifact retains the full `input_ids` arrays rather than only lengths or
hashes.

Special-token IDs observed from the exact tokenizer are:

- CLS = `50281`;
- SEP = `50282`;
- MASK = `50284`;
- PAD = `50283`.

`reference_token_fixture.py` validates the packet fail-closed against the
frozen protocol fixture, including canonical per-case request SHA-256
(state/instructions/criteria and authored order), case/question/option identity,
sequence bounds, token counts, strictly increasing marker positions, and each
marker pointing to MASK. It also rejects attempts to change either
`candidate_side_tokenizer_attested` or `numeric_model_parity` to true.

An independent Core ML validation artifact from
`mizorewww/laya-coreml@4619e0483f07adf39068532e85b42ec2347edb83`
also binds the same checkpoint revision / weights / tokenizer hash and reports
`tokens_equal=true` for 16 retained cases / 63 questions. That is useful
corroboration, but it does not substitute for this SEI fixture because it does
not retain these four SEI token arrays.

The claim boundary is therefore:

```text
exact reference tokenizer bytes
  + exact SHA-256 match
  + 206/206 tokenizer fuzz replay
  + exact #597 reference input IDs / markers
  = reference-side P1c Evidence

reference-side P1c Evidence
  != Papaya/fr0stbit3 candidate tokenizer byte attestation
  != candidate token-ID / marker parity
  != model tensor identity
  != numeric model parity
  != live L0 inference
```

The remaining P1 work is now candidate-side only.

## Deterministic `choice:11+` temperature incompatibility

The clamp-sensitive path can be classified before model bytes are available.

The shipped typed-decisions config contains:

```text
choice:11+ = 0.10058280825614929
```

Pinned Python Laya 0.3.20 keeps the raw value for inspection but applies
`clamp_temperature()` before inference. Its lower bound is:

```text
TEMP_MIN = 0.5
```

Therefore the Python reference uses `T = 0.5` for `choice:11+`.

Pinned Papaya instead formats answers with:

```python
z = logits / max(1e-3, temperature)
```

so it applies the raw `T = 0.10058280825614929`.

This is not merely an untested bucket. If the raw logits are the same, the two
probability vectors are deterministically related. Let `p` be the Python
0.3.20 probability vector after the 0.5 clamp and `q` the current Papaya
vector. Then:

```text
r = 0.5 / 0.10058280825614929
  = 4.971028435860277

q_i = p_i^r / sum_j(p_j^r)
```

For every non-uniform finite distribution, `r != 1` changes the reported
probabilities. A unique argmax is preserved by positive temperature scaling,
but calibrated probability / entropy-confidence parity is not.

Illustrative 12-option distributions with one top option and the remaining
probability spread equally show the scale of the deterministic difference:

| Python 0.3.20 top p | Papaya top p | Python entropy confidence | Papaya entropy confidence |
| ---: | ---: | ---: | ---: |
| 0.15 | 0.7108 | 0.0097 | 0.4789 |
| 0.20 | 0.9328 | 0.0266 | 0.8361 |
| 0.24 | 0.9779 | 0.0448 | 0.9361 |
| 0.30 | 0.9951 | 0.0787 | 0.9828 |
| 0.40 | 0.9995 | 0.1502 | 0.9976 |

These values are an analytic temperature transform, not observed model output.

Consequently:

```text
current Papaya code
  + identical tokenizer / logits / head weights
  != Python Laya 0.3.20 numeric parity on choice:11+
```

Exact full-runtime parity is therefore impossible on this bucket without a
Papaya-side behavior change (or an explicit decision to preserve the historical
unclamped semantics as a different runtime contract).

This narrows G2. A later live experiment should not ask whether the current
implementations happen to match on `choice:11+`; the static answer is already
no for ordinary non-uniform logits. Instead it should verify that a candidate
compatibility patch applies the same 0.5 clamp and then compare probabilities.

Do not modify the frozen four-case #597 L0 fixture solely to cover this
candidate-specific difference. Keep a separate >=11-option parity diagnostic so
the provider-neutral fixture remains stable.

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


## Candidate bundle artifact identity

The Papaya runtime source is pinned separately from the model bundle it
downloads. The current `fr0stbit3/laya-typed-decisions-gguf` bundle can now be
pinned more precisely even though its large files are still not materialized in
the current execution container.

Inspected Hugging Face repository state:

- repository: `fr0stbit3/laya-typed-decisions-gguf`;
- current bundle commit:
  `54ec2dbb58aad9e3c74782cb2feb5801f72b13d0`;
- tokenizer/config upload ancestor:
  `75300646cddbac2b47409fc1ca839c95bec004c8`.

Exact large-file pointer identities at the current bundle commit:

| artifact | bytes | SHA-256 |
| --- | ---: | --- |
| `laya-typed-decisions-Q8_0.gguf` | 421,407,968 | `84f16d7b0b0a07343e7a6f8d8bd7ae9633aa0372d55621e2242d0ed9a0aca28c` |
| `laya-typed-decisions-head.safetensors` | 106,052,952 | `f115a16370df62e24a88aded4ef10d6542d2cdec9439df86d3aea3689f13ca44` |

These values come from the repository's raw Xet/LFS pointer metadata, so they
identify the remote file bytes even though those bytes were not downloaded
locally.

Two small configuration files are also byte-identical to the pinned reference
lineage. Their complete public file contents and displayed byte sizes were
reconstructed exactly as UTF-8 JSON with no trailing newline; the recomputed
digests match the already independently attested reference hashes:

| artifact | bytes | SHA-256 | relation |
| --- | ---: | --- | --- |
| `rl_agent_config.json` | 847 | `ebf0cd524d92342a6be5e48e9fca3d7c2babfb5a56ccd79d2171ef5d8c7f7be8` | exact reference match |
| `tokenizer_config.json` | 337 | `08d4cf3ac4dca381759441b85b91a6d40e688471dcd33d15d6649eb0a9a854d1` | exact reference match |

The retained candidate `rl_agent_config.json` therefore carries the same raw
`choice:11+ = 0.10058280825614929` value as the reference checkpoint. The
numeric incompatibility described below remains a **runtime behavior** difference:
Python Laya 0.3.20 clamps that value before use while current Papaya does not.

The remaining tokenizer boundary is deliberately narrower:

- candidate `tokenizer.json` is publicly visible at 3,583,228 bytes;
- it was added at the verified `75300646...` upload;
- its structure, special-token IDs, line count and sampled contents match the
  independently attested reference tokenizer;
- but the candidate-side file still lacks an independently obtained full-file
  SHA-256 in SEI Evidence.

Therefore:

```text
Q8 backbone byte identity        ATTESTED by remote pointer
decision-head byte identity      ATTESTED by remote pointer
rl_agent_config byte identity    ATTESTED / exact reference match
tokenizer_config byte identity   ATTESTED / exact reference match
candidate tokenizer.json         NOT YET byte-attested
model numerical parity           NOT ESTABLISHED
```

This receipt improves future reproducibility but does not promote the Papaya
bundle to reference status. The Q8 encoder is quantized derived state and the
separate head file still requires source-lineage/numeric validation against the
pinned F16 Python reference.

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


## P1a retained sequence-length parity

The retained Papaya benchmark outputs expose one additional tokenization
observation even though they do not retain token IDs or marker positions.

At the pinned Papaya commit, the following Git-backed result artifacts were
compared by exact case id:

- `benchmarks/results/ours.json` — Papaya Q8;
- `benchmarks/results/navopw-on-typed-decisions.json` — the typed-decisions
  ONNX comparator.

Both contain 48 cases in the same case-id order. For every matched case,
`usage.input_tokens` is identical:

- exact input-token-count matches: **48 / 48**;
- mismatches: **0**;
- observed minimum: **784** tokens;
- observed maximum: **2041** tokens.

A second retained runtime check, `native-12.json` versus `docker-12.json`,
also has exact `usage.input_tokens` equality for **12 / 12** matched cases.

The retained `scripts/bench_compare.py` harness sends the same input row to
each TypeSafe-compatible endpoint and stores the endpoint-reported usage, so
this is positive **sequence-length parity** evidence across the retained runs.

It is deliberately weaker than token parity:

```text
same case identity
  + same logical rendering family
  + same reported input-token count
  = sequence-length parity evidence

  != tokenizer-file byte identity
  != token-ID identity
  != per-option token identity
  != marker-position identity
  != truncation-path identity
```

Two different token sequences can have the same length. Also, the benchmark
`rows.json` input is not retained beside these outputs, so the 48-case result
cannot be independently regenerated from Git alone.

P1a remains useful as independent sequence-length evidence, but it is no longer
the strongest reference-side token evidence. The exact reference tokenizer and
four-case token/marker fixture in P1c supersede the earlier reference-side
blocker. What remains open is candidate-side Papaya/fr0stbit3 byte attestation
and replay against these retained IDs/markers.

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


## Candidate tokenizer transport recheck (2026-09-26)

The candidate-side tokenizer boundary was rechecked after the reference-side P1c
fixture was merged.

Current public Hugging Face metadata for
`fr0stbit3/laya-typed-decisions-gguf` still identifies the bundle as a
conversion of `convaiinnovations/laya-typed-decisions`. Its published
llama.cpp quickstart also constructs the typed-decision agent through the
original Laya package and explicitly tokenizes with the Hugging Face tokenizer
before sending token IDs to the converted backbone.

This strengthens **lineage and intended-tokenizer** evidence, but it does not
change the byte-attestation stop line:

```text
candidate model card names the exact base model
  + candidate runtime path uses the HF tokenizer contract
  + candidate tokenizer has the same observed byte size / structure
  != independent full-file SHA-256 of candidate tokenizer.json
```

A direct candidate-byte hashing attempt through available hosted compute was
also attempted during this checkpoint, but the compute service rejected the job
before execution. That transport/billing failure is not model evidence and is
not treated as a negative runtime result.

Accordingly, P1 remains fail-closed on the candidate side. The next admissible
event is still one of:

1. independently materialize the candidate `tokenizer.json` and hash all bytes;
2. obtain an authoritative immutable file digest tied to the candidate revision;
3. obtain a retained exact candidate token-ID fixture whose provenance can be
   independently bound to that revision.

Until then, `candidate_side_tokenizer_attested=false` remains required.


## Candidate tokenizer byte attestation (2026-09-26)

The candidate-side tokenizer byte gate is now closed by an immutable
Git-object identity rather than by size or sampled-content similarity.

Pinned candidate:

- repository: `fr0stbit3/laya-typed-decisions-gguf`;
- revision: `75300646cddbac2b47409fc1ca839c95bec004c8`;
- path: `tokenizer.json`;
- bytes: **3,583,228**.

The exact-revision Hugging Face download resolution exposes ETag
`2f4d8583e507b7466d2490e2d6c045647a822698`. Hugging Face documents that
for files tracked directly in Git, the Hub ETag is the file's Git SHA-1. The
candidate tokenizer is a regular Git-tracked file, so this is its immutable Git
blob identity.

That blob is exactly the independently retained reference tokenizer blob from
`MatteoGauthier/laya-portable@3dc028023929432b4a3d76b1a8ee050d0e5ccd7f`:

```text
candidate Git blob
  2f4d8583e507b7466d2490e2d6c045647a822698

reference Git blob
  2f4d8583e507b7466d2490e2d6c045647a822698
```

Git blob equality establishes byte equality. Because the reference bytes were
independently materialized and hashed, the candidate therefore has the same
SHA-256:

`6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30`.

This does **not** claim that the candidate SHA-256 was independently recomputed
from a second local download. Its SHA-256 equality is derived from exact byte
identity to the independently hashed reference.

Durable SEI Evidence is retained in:

- `papaya_candidate_tokenizer_attestation.v1.json`;
- `papaya_candidate_tokenizer_attestation.py`;
- `test_papaya_candidate_tokenizer_attestation.py`.

The validator fails closed if the candidate revision/blob/ETag/size/reference
identity drifts and rejects downstream overclaims.

Current boundary:

```text
candidate tokenizer byte identity     ATTESTED
candidate token-ID / marker parity    NOT YET REPLAYED
numeric model parity                  NOT ESTABLISHED
live L0 inference                     NOT RUN
```

This section supersedes the earlier chronological checkpoints that recorded
`candidate_side_tokenizer_attested=false`. Those entries remain useful as
history of the transport blocker, but are no longer the current state.

The reference-only `reference_token_fixture.v1.json` remains unchanged and
continues to record `candidate_side_tokenizer_attested=false` because that
packet itself does not attest the candidate. Candidate-side byte Evidence lives
in the separate attestation packet above.

The tokenizer-byte search is therefore closed. The next chronological P1 event
was Papaya's pinned sequence-builder replay against the four frozen #597
reference token-ID / marker rows; that replay is now retained below.


## P1d frozen #597 Papaya sequence replay

The pinned Papaya question normalization / rendering / sequence builder has now
been replayed against the exact four-case SEI reference token fixture without
loading model weights.

Pinned Papaya source:

- repository: `m0rphtail/papaya`;
- revision: `a76bc99bddafdac32863b2edc5319773e0cd3532`;
- `src/papaya/questions.py` blob
  `7b1fe73f23b225a04f4b2ac53fd0011a4fdf90bf`;
- `src/papaya/sequences.py` blob
  `f21139970d6d288114213db8f917f0cead9c082f`;
- `src/papaya/runtime.py` blob
  `b3999b7f1e02d4761ffba63b7f846b210f3e27dd`.

The replay uses the candidate tokenizer identity closed above:

`2f4d8583e507b7466d2490e2d6c045647a822698`

which is byte-identical to the independently hashed reference tokenizer. The
candidate config is also already attested at 847 bytes / SHA-256
`ebf0cd524d92342a6be5e48e9fca3d7c2babfb5a56ccd79d2171ef5d8c7f7be8`,
with `max_len=1024` and `head_max_len=256`.

The source-equivalent replay result is:

| case | Papaya tokens | reference tokens | input IDs | markers |
| --- | ---: | ---: | --- | --- |
| `choice-route-a` | 72 | 72 | exact | `[16, 21, 28]` exact |
| `choice-route-b` | 72 | 72 | exact | `[16, 23, 30]` exact |
| `score-urgency` | 71 | 71 | exact | `[14, 19, 25, 30]` exact |
| `noul-review` | 70 | 70 | exact | `[16, 26]` exact |

Thus the retained four-case common subset has **4 / 4 full input-ID equality**
and **4 / 4 marker-position equality**.

Durable Evidence:

- `papaya_sequence_replay.v1.json`;
- `papaya_sequence_replay.py`;
- `test_papaya_sequence_replay.py`.

The replay packet is intentionally narrower than a live Papaya run. It records:

```text
candidate tokenizer byte identity         ATTESTED
frozen #597 input-ID parity                PASS 4/4
frozen #597 marker-position parity         PASS 4/4

upstream Papaya Python executed            NO
Transformers AutoTokenizer executed        NO
model weights loaded                       NO
temperature-semantics parity               NO
numeric model parity                       NO
live L0 inference                          NO
```

The replay is called **source-equivalent** because the pinned Papaya source
semantics were reproduced with the byte-attested tokenizer and the independently
validated ByteLevel BPE implementation (206 / 206 retained typed-decisions fuzz
cases). It is not relabeled as an upstream runtime execution.

No frozen case exercises Papaya's option/head/state truncation boundary; the
observed rows are comfortably inside the configured budgets. The earlier
candidate-specific `choice:11+` temperature incompatibility is also unchanged:
token parity does not imply output-probability parity.

Current P1 boundary:

```text
P0  logical rendering parity             PASS
P1a retained sequence length             PASS
P1b candidate tokenizer bytes            ATTESTED
P1c reference exact IDs / markers        PASS
P1d candidate exact IDs / markers        PASS on frozen 4-case replay

P2  model numeric parity                 OPEN
G2  choice:11+ compatibility behavior    OPEN / current Papaya known incompatible
live L0 Papaya inference                 NOT RUN
```

The next useful Papaya comparison is therefore numeric rather than another
tokenizer search: preserve the frozen four-case input packet, separately cover
the known clamp-sensitive >=11-option diagnostic, and compare encoder/head
outputs only when executable candidate model bytes/runtime are available.


## G2 evaluation-only clamp compatibility overlay

The known `choice:11+` incompatibility can now be isolated without modifying
the pinned Papaya source or pretending that current Papaya already matches
Python Laya 0.3.20.

The helper:

`prepare_papaya_compat_overlay.py`

takes:

1. a local directory containing the exact pinned candidate Q8 backbone, decision
   head, raw `rl_agent_config.json`, and `tokenizer_config.json`;
2. any local copy of the tokenizer bytes that verifies to the attested
   3,583,228-byte / SHA-256
   `6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30`;
3. a fresh output directory.

It first verifies the exact retained candidate identities:

| role | bytes | SHA-256 |
| --- | ---: | --- |
| Q8 backbone | 421,407,968 | `84f16d7b0b0a07343e7a6f8d8bd7ae9633aa0372d55621e2242d0ed9a0aca28c` |
| decision head | 106,052,952 | `f115a16370df62e24a88aded4ef10d6542d2cdec9439df86d3aea3689f13ca44` |
| raw config | 847 | `ebf0cd524d92342a6be5e48e9fca3d7c2babfb5a56ccd79d2171ef5d8c7f7be8` |
| tokenizer config | 337 | `08d4cf3ac4dca381759441b85b91a6d40e688471dcd33d15d6649eb0a9a854d1` |
| tokenizer bytes | 3,583,228 | `6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30` |

It then applies the pinned reference `clamp_temperature()` policy from
`NandhaKishorM/laya@23a17522...`, `laya/common.py` blob
`6c4c426e64eb9660c97d40bc64c227e8c7e71361`.

For the currently pinned candidate, the helper fails closed unless the complete
temperature transformation contains exactly one delta:

```text
temperature_by_options.choice:11+
  raw     = 0.10058280825614929
  applied = 0.5
```

All other temperature values must remain numerically unchanged.

The resulting deterministic compatibility config is pinned to:

- bytes: **832**;
- SHA-256:
  `279207d55fefd56b2c6738dd141a3e10ab1d3f46b755c43faee42364ce1cc892`.

The staged directory keeps the candidate Q8/head artifacts, the byte-attested
tokenizer identity, and the candidate tokenizer config, but replaces the raw
temperature config with this derived compatibility config. It also writes
`sei_compat_overlay_receipt.json`.

The receipt intentionally contains no host-local input paths. It records
artifact byte/hash identities, the **required** Papaya source revision/blobs,
tokenizer identity, the #617 frozen sequence-parity precondition, reference
clamp provenance, the exact config delta, and the derived config hash.

The helper does not inspect a local Papaya source checkout. Accordingly the
receipt explicitly records `source_verified_by_overlay=false` and
`runtime_source_verified=false`; those pinned source identities are execution
requirements, not observations about whichever runtime later consumes the
overlay.

The Q8 backbone and decision head are staged as symbolic links to avoid copying
roughly 527 MB of model data. That makes a second fail-closed check mandatory
immediately before inference:

```bash
python3 prepare_papaya_compat_overlay.py --verify-staged <output-directory>
```

This command re-hashes the current link targets plus all copied/derived overlay
files and rejects post-staging drift. Overlay creation performs the same staged
verification once before publishing the output directory.

The claim boundary is:

```text
current Papaya as-is temperature semantics       INCOMPATIBLE on choice:11+
SEI compatibility-overlay temperature semantics ALIGNED BY CONSTRUCTION
tokenizer byte identity                          PRESERVED
frozen four-case token/marker parity             PRECONDITION PRESERVED

encoder numeric parity                           NOT ESTABLISHED
decision-head numeric parity                     NOT ESTABLISHED
full numeric parity                              NOT ESTABLISHED
live inference                                   NOT RUN
reference-provider promotion                     NO
```

This means G2 has an executable compatibility **preparation** path, not an
observed runtime parity result. The next live candidate event should run the
pinned model through this overlay and retain both the ordinary frozen four-case
numeric outputs and a separate >=11-option clamp-sensitive diagnostic.
