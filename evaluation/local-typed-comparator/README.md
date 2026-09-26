# Local typed comparator — L0 protocol/schema fixture

Status: evaluation fixture only. No live model run or quality claim.

Related: #543 / #546 / #597.

## Purpose

Freeze the minimum Choice / Score / Noul request and response contract used to
compare a local Jev-compatible provider such as Laya without merging provider
identity or teacher lineage.

This directory is deliberately separate from
`evaluation/sparse-associative-cognition/jd-lgbm-teacher-dataset/`.
The latter remains the authenticated TypeSafe/Jev baseline path.

## Upstream reference inspected

The fixture was checked against:

- `NandhaKishorM/laya@970dc8c5f63d7b886a68409493f37d569424f933`;
- `laya/serve.py`, whose `POST /v1/systemone` returns
  `{model, answers, usage, ...}`;
- Laya's Choice / Score / Noul shapes, including provider-specific optional
  fields such as `routing`, `answer_confidence`, and `action`.

The upstream SHA is a compatibility reference, not dependency pinning or
endorsement. SEI owns this fixture contract.

Benchmark/result provenance is tracked separately in
[`UPSTREAM_BENCHMARK_PROVENANCE.md`](./UPSTREAM_BENCHMARK_PROVENANCE.md). In
particular, base zero-shot Laya results and the typed-decisions specialist
fine-tuned on the benchmark training split are not treated as one evidence
lineage.

Candidate local runtime audits are also kept provider/runtime-specific. See
[`RUST_RUNTIME_CANDIDATE.md`](./RUST_RUNTIME_CANDIDATE.md) and
[`PAPAYA_RUNTIME_CANDIDATE.md`](./PAPAYA_RUNTIME_CANDIDATE.md). Neither changes
the pinned Python reference or the model-byte admission gate.

At the inspection point, upstream also had open hardening work around malformed
or missing request state. SEI therefore requires an explicit non-null state in
the fixture rather than inheriting permissive behavior from a particular Laya
revision.

## Validate the frozen fixture

```bash
python3 protocol_contract.py fixture.v1.json
python3 -m unittest -v test_protocol_contract.py
```

Reference-side exact token/marker Evidence is retained separately in
[`reference_token_fixture.v1.json`](./reference_token_fixture.v1.json). Validate
its fixture binding and stop lines with:

```bash
python3 reference_token_fixture.py fixture.v1.json reference_token_fixture.v1.json
python3 -m unittest -v test_reference_token_fixture.py
```

That packet proves only the pinned **reference-side** tokenizer replay for these
four frozen cases. It deliberately records
`candidate_side_tokenizer_attested=false` and `numeric_model_parity=false`;
that flag describes the scope of the reference-only packet, not the current
candidate-byte state.

Papaya candidate tokenizer byte identity is retained separately in
[`papaya_candidate_tokenizer_attestation.v1.json`](./papaya_candidate_tokenizer_attestation.v1.json).
Validate that packet and its stop lines with:

```bash
python3 papaya_candidate_tokenizer_attestation.py papaya_candidate_tokenizer_attestation.v1.json
python3 -m unittest -v test_papaya_candidate_tokenizer_attestation.py
```

The candidate tokenizer packet proves byte identity only. Its own scope therefore
keeps token-ID / marker parity, numeric model parity, and live L0 inference
explicitly false.

Papaya's pinned source-equivalent sequence replay is retained separately in
[`papaya_sequence_replay.v1.json`](./papaya_sequence_replay.v1.json). Validate
its cross-binding to the frozen request fixture, reference token fixture, and
candidate tokenizer attestation with:

```bash
python3 papaya_sequence_replay.py \
  fixture.v1.json \
  reference_token_fixture.v1.json \
  papaya_candidate_tokenizer_attestation.v1.json \
  papaya_sequence_replay.v1.json
python3 -m unittest -v test_papaya_sequence_replay.py
```

That replay establishes exact full input-ID and marker-position equality for all
four frozen cases. It deliberately does **not** claim upstream Papaya Python or
Transformers execution, model loading, temperature-semantics parity, numeric
model parity, or live L0 inference.

For the known Papaya `choice:11+` temperature mismatch, prepare an
**evaluation-only compatibility overlay** with:

```bash
python3 prepare_papaya_compat_overlay.py \
  <candidate-bundle-directory> \
  <attested-tokenizer.json> \
  <output-directory>
```

Use `--verify-only` to validate the input hashes and print the planned receipt
without creating an output directory.

Because the staged Q8 backbone and decision head are symbolic links back to the
verified candidate directory, re-hash the **prepared overlay immediately before
each inference run**:

```bash
python3 prepare_papaya_compat_overlay.py --verify-staged <output-directory>
```

That staged verification follows the links and rejects any post-preparation
byte drift in the Q8/head files. It also rechecks the copied tokenizer,
tokenizer config, derived compatibility config, and receipt bindings. The
overlay does not inspect a local Papaya source checkout, so its receipt keeps
`runtime_source_verified=false`; the actual runtime revision/blobs must be
verified separately by the eventual execution harness.

The overlay requires the pinned Q8 backbone, decision head, raw config,
tokenizer config, and tokenizer bytes. It fails closed unless all exact byte
sizes / SHA-256 values match the retained candidate Evidence. It then derives a
config using Python Laya 0.3.20's `[0.5, 5.0]` clamp policy. For the currently
pinned candidate the **only** allowed semantic change is:

`temperature_by_options.choice:11+: 0.10058280825614929 -> 0.5`.

The derived config is pinned to 832 bytes / SHA-256
`279207d55fefd56b2c6738dd141a3e10ab1d3f46b755c43faee42364ce1cc892`.

This is not “Papaya as-is” and does not establish numeric parity. The generated
receipt keeps encoder/head/full numeric parity and live inference false, and
does not retain host-local file paths.

Validate the helper with:

```bash
python3 -m unittest -v test_prepare_papaya_compat_overlay.py
```

The current focused suite covers:

- fixture identity and option-order perturbation integrity;
- missing-state rejection;
- exact requested answer ids;
- Choice option/probability shape;
- Score ordered legend/probability shape;
- Noul probability range;
- non-negative integer usage counts;
- boolean-as-number rejection;
- provider-specific extra response fields.

## L0 interpretation

A response contract PASS means only that a returned payload is mechanically
usable by this bounded comparator surface.

```text
protocol/schema PASS
  != provider identity equivalence
  != Jev teacher Evidence
  != model correctness
  != calibration
  != Product Value
  != permission to train or activate a student
```

Provider/model/checkpoint identity remains outside this response-shape validator
and must be retained in run Evidence.

## Option-order pair

`choice-route-a` and `choice-route-b` contain the same state, question
semantics, and option set with only the Choice option order changed.

The fixture validator proves the pair is a valid metamorphic comparison. It does
not assert that a model must return the same distribution. A future live Laya
run should record both outputs and treat material order sensitivity as Evidence
for calibration/robustness review, not silently normalize it away.

## Papaya first-live-run capture

Papaya is captured through its own provider-specific runner rather than by
weakening the Python-Laya identity gates in `capture_l0.py`.

Prepare and revalidate the #620/#621 compatibility overlay first, then use:

```bash
python3 capture_papaya_l0.py \
  --source-git-sha <exact-clean-SEI-checkout-SHA> \
  --papaya-source-dir <clean-m0rphtail-papaya-a76bc99-checkout> \
  --overlay-dir <prepared-compat-overlay> \
  --llama-binary <pinned-b10964-llama-server> \
  --run-id <unique-run-id> \
  --output <new-run-artifact.json>
```

The run artifact path must be outside both verified source checkouts, so the
capture cannot make either working tree dirty after its cleanliness check.

The runner itself starts Papaya on an ephemeral loopback port and fails closed
unless all of the following bind correctly:

- the clean SEI source checkout at the requested full SHA;
- the clean `m0rphtail/papaya@a76bc99...` checkout and exact runtime/source
  Git blobs;
- the #621 prepared overlay, re-hashed once before launch and again after health
  but before first inference;
- the SEI first-run llama.cpp `b10964` binary, including executable SHA-256
  and `--version` output;
- the retained #617 four-case token-count replay.

The b10964 pin is an **SEI first-live-run runtime pin**, not a claim that Papaya
upstream requires that exact llama.cpp build.

The runner captures the frozen four cases and separately executes
[`papaya_choice11_diagnostic.v1.json`](./papaya_choice11_diagnostic.v1.json),
which contains one synthetic 12-option Choice question solely to exercise the
`choice:11+` compatibility-overlay path. The diagnostic has no expected answer
and no quality claim.

Papaya's pinned `pyproject.toml` uses dependency ranges rather than an exact
lock. The capture therefore requires the runtime dependencies to be present and
retains their **observed versions per run**; it does not relabel those versions
as upstream-pinned identities.

A complete Papaya run may establish live protocol/runtime Evidence, but still
keeps these claims false until a separate comparison exists:

```text
numeric parity with Python Laya   false
task quality                      false
calibration validity              false
Jev provider identity             false
reference-provider promotion      false
```

## Next step

The tokenizer/sequence/overlay preparation side is now closed sufficiently for
a first fail-closed Papaya execution handoff. The next admissible event is an
actual `capture_papaya_l0.py` run with the exact pinned model/runtime bytes.
After that run exists, compare its retained numeric outputs against the
independently captured Python-Laya reference without merging provider
provenance.

No new product/runtime branch is implied by this fixture.
