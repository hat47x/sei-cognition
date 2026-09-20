# JD-LGBM-0 typed teacher dataset harness

This directory prepares the first Jev → local-student experiment without inventing teacher labels.

## Scope

- 12 low-risk synthetic structured-state cases.
- Three bounded tasks: `service_route` (Choice), `operational_urgency` (Score), and `human_review_gate` (Noul).
- Representative, boundary, perturbation, counterexample, and rare slices.
- Explicit train/valid/test and `split_group_identity` metadata; one group is never allowed to cross splits.
- Canonical SHA-256 request identity before any teacher call.
- Exact returned Jev model version, raw response hash, probability/score payload, usage, and observed client latency in every derived row.

The public TypeSafe API contract used by the harness is `POST https://api.typesafe.ai/v1/systemone` with `model: "jev-latest"`; `state` may be a JSON object/array. Choice returns a selected option plus a distribution and confidence, Score returns a weighted score plus level probabilities and confidence, and Noul returns a 0–1 value.

References:
- https://docs.typesafe.ai/api
- https://docs.typesafe.ai/introduction/quickstart

## Non-claims

A passing harness test is not a Jev run. Synthetic case design is not teacher output or ground truth. Teacher fidelity is not task correctness. Jev probability/confidence is not semantic truth or SEI confidence. No student is trained, activated, or made a production default by this harness.

## Plan only

```bash
python3 teacher_dataset.py tasks.v1.json --mode plan
```

This validates the manifest and prints deterministic request identities. It sends no network request.

## Actual teacher collection

```bash
export TYPESAFE_API_KEY=...
python3 teacher_dataset.py tasks.v1.json --mode run --output-dir run-YYYYMMDD
```

The harness refuses to run without `TYPESAFE_API_KEY`. It stores raw responses separately from normalized `teacher_rows.jsonl`; it does not silently overwrite an existing row file. HTTP 429 and 529 responses are retried with a bounded exponential backoff.

## Import externally captured raw responses

An API key does not need to be copied into this execution environment. If the same case requests are executed in another trusted environment, save one raw TypeSafe response per case as `<case_id>.json`, then validate and normalize them here:

```bash
python3 teacher_dataset.py tasks.v1.json --mode import \
  --raw-dir trusted-capture/raw \
  --output-dir normalized-run
```

Import mode requires all 12 case files, revalidates the returned Jev model version and typed probability/score shapes, and writes normalized rows with `teacher_latency_ms: null` because external capture latency was not observed by this harness.

## Student-dataset readiness gate

After authenticated teacher rows exist, join them back to the exact structured inputs before any model training:

```bash
python3 student_dataset.py tasks.v1.json normalized-run/teacher_rows.jsonl \
  --output-dir student-ready
```

The gate requires exactly one validated teacher row for every manifest case, exact request/split/schema/provenance identity, one immutable Jev model version across the first JD-LGBM-0 slice, and valid typed target distributions. It writes structured `features` joined from the manifest plus teacher targets; it does **not** train LightGBM. Missing, duplicated, mixed-version, or identity-mismatched rows are rejected.
