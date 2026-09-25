# Rust runtime candidate for local Laya typed decisions

Status: research candidate only. No runtime promotion is implied.

## Pinned upstream

- Repository: `aovestdipaperino/laya-rust`
- Commit: `5104bf2a42287382cb867edfe74732f6d823795a`
- Crate package: `laya 0.1.1`
- Rust floor: `1.75`
- License: Apache-2.0
- `Cargo.lock` blob: `a567b6deab7f216d8a6a48d833504169bc0a454a`
- Core dependencies at the pinned source:
  - `candle-core = 0.9`
  - `candle-nn = 0.9`
  - `tokenizers = 0.21`
  - `serde / serde_json`
- Optional local web server:
  - `axum = 0.8`
  - `tokio = 1`

The implementation loads the same Laya checkpoint directory shape
(`model.safetensors`, `encoder/config.json`, `tokenizer/tokenizer.json`,
`rl_agent_config.json`) and exposes CPU / Metal / CUDA execution through Candle.

## Why this candidate matters

The Python reference lane currently needs Python + PyTorch + Transformers/Tokenizers for
checkpoint execution. A validated Rust path could reduce the shipping/runtime dependency
surface while keeping the same typed-decision checkpoint family.

This is an implementation/runtime hypothesis only:

```text
same checkpoint family
  != same numerical implementation
  != same rendered prompt
  != same calibrated probabilities
  != same Jev wire contract
```

Do not promote this candidate from source inspection alone.

## Current protocol gap

The pinned Rust web server is **not** a drop-in replacement for Laya 0.3.20
`POST /v1/systemone`.

Pinned Rust server surface:

- endpoint: `POST /api/predict`
- questions: ordered array of `{id, ...question}`
- optional prompt inspection
- response adds local `latency_ms`
- no Python-Laya `routing.model` metadata

The Rust library response also differs from the Python/Jev-compatible response details:

- answer metadata is named `rl_agent.act_probability`
- the pinned Rust `noul` answer does not expose the Python-side confidence fields
- no HTTP-side logical checkpoint attestation equivalent to
  `/health.loaded == typed-decisions` + `routing.model == typed-decisions`

Therefore:

```text
Rust Agent::system_one compatibility candidate
  != Jev-compatible HTTP provider
```

A thin adapter may be possible later, but it must not be added before numerical/runtime
parity is established.

## Upstream test evidence and its limit

At the pinned source:

- model-free rendering tests cover:
  - Choice option order;
  - Score level rendering;
  - Noul false/true ordering;
  - temperature buckets;
  - question-type embedding indices.
- checkpoint-dependent inference tests cover:
  - well-formed typed answers;
  - batched-vs-single equality;
  - probability normalization / argmax;
  - score range;
  - fail-loudly behavior for excessive options.

Those checkpoint-dependent tests skip when model weights are absent.

They are useful upstream regression tests, but they are **not** SEI cross-runtime parity
Evidence against the pinned Python Laya 0.3.20 reference.

## SEI admission gate

Only evaluate the Rust runtime after exact typed-decisions checkpoint bytes are available.

Use the already frozen #597 L0 fixture and preserve the same checkpoint identity:

- repository: `convaiinnovations/laya-typed-decisions`
- revision: `f9ab0b228f0fc0f14d873dbc99038f135c2da1b2`
- `model.safetensors` SHA-256:
  `4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e`

Required order:

1. run the pinned Python Laya reference on the frozen fixture;
2. run pinned Rust `5104bf2...` against the **same checkpoint directory bytes**;
3. compare rendered token IDs, marker positions and option ordering before comparing outputs;
4. compare typed answers and probability vectors;
5. record per-case numeric deltas rather than requiring accidental bit identity;
6. compare CPU load time, p50/p95 latency and RSS;
7. only if parity is acceptable, implement/test a Jev-wire adapter;
8. only after that may Rust be considered a local runtime candidate for the cascade.

## Numeric parity policy

Do not predeclare a permissive tolerance before seeing which operations differ.

First record raw deltas for:

- choice probabilities;
- score distributions / expectation;
- noul probability;
- confidence calculation where both runtimes expose a comparable quantity.

Any acceptance tolerance must then be justified from:

- dtype/backend differences;
- classification stability near decision boundaries;
- calibration impact;
- downstream threshold sensitivity.

A top-1 match alone is insufficient.

## Current local execution boundary

The current ChatGPT execution container does not provide `rustc` or `cargo`, and its
Cargo registry/cache is absent. Exact typed-decisions model bytes are also not materialized
in this environment.

Therefore this checkpoint records source/runtime feasibility only:

```text
pinned Rust source inspected
  + locked dependency graph present upstream
  + same checkpoint directory format supported
  != Rust binary built here
  != model loaded here
  != Python/Rust parity measured
  != Jev-wire compatibility
```

Do not add a Rust adapter branch until the model-byte gate opens and the parity experiment can
be executed as one bounded work unit.
