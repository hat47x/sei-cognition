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
`candidate_side_tokenizer_attested=false` and `numeric_model_parity=false`.

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

## Next step

#597 L0 can proceed with an actual local Laya endpoint only after the runtime and
checkpoint identity are fixed. The live runner should:

1. load this exact fixture;
2. submit one case at a time;
3. retain exact request/response bytes and latency;
4. validate each response with `validate_response`;
5. record provider/model/checkpoint/runtime hashes separately;
6. make no task-quality claim from protocol conformance alone.

No new product/runtime branch is implied by this fixture.
