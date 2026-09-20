# JD-LGBM-0 typed teacher dataset harness

This directory prepares the first Jev → local-student experiment without inventing teacher labels.

## Scope

- 12 low-risk synthetic structured-state cases.
- Three bounded tasks: `service_route` (Choice), `operational_urgency` (Score), and `human_review_gate` (Noul).
- Representative, boundary, perturbation, counterexample, and rare slices.
- Explicit train/valid/test and `split_group_identity` metadata.
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

The harness refuses to run without `TYPESAFE_API_KEY`. It stores raw responses separately from normalized `teacher_rows.jsonl`; it does not silently overwrite an existing row file.
