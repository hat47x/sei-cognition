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

## Exact request bundle for trusted external capture

When the API key must stay outside the validation environment, first freeze the exact passive-baseline requests from the repository checkout:

```bash
python3 teacher_dataset.py tasks.v1.json --mode bundle \
  --source-git-sha "$(git rev-parse HEAD)" \
  --output-dir trusted-capture-bundle
```

Bundle mode sends **no network request** and stores no authorization header. It exclusive-creates:

- `capture_manifest.json` with the exact source Git SHA, `tasks.v1.json` SHA-256, API endpoint/method, and one descriptor per case;
- `requests/<case_id>.json` for all 12 canonical request bodies;
- both canonical request SHA-256 and exact request-file SHA-256.

The bundle is deterministic for the same source/manifest and refuses a non-empty output directory. Execute these exact request bodies in the trusted credentialed environment, then save one raw response per case as `raw/<case_id>.json` for the existing import path.

This first 12-case bundle remains the fixed passive JD-LGBM-0 baseline. Active-curriculum work such as #556 may add later acquisition, but must not replace or selectively filter this baseline.

## Credentialed direct-capture preflight

Before a direct authenticated run, validate the frozen bundle, the intended checkout identity, credential presence, and output collision state without sending a network request:

```bash
export TYPESAFE_API_KEY=...
python3 teacher_dataset.py tasks.v1.json --mode preflight \
  --capture-manifest trusted-capture-bundle/capture_manifest.json \
  --expected-source-git-sha "$(git rev-parse HEAD)" \
  --output-dir run-YYYYMMDD
```

A successful preflight reports `network_requests_sent: 0`, never prints the API key value, and requires the capture bundle's `source_git_sha` to match the explicitly supplied checkout SHA. It also refuses protected direct-capture artifacts already present under the output path.

This preflight is operational readiness only. It is not Jev Evidence, teacher correctness, or permission to train a student.

## Actual teacher collection

Direct authenticated collection uses the same frozen request bundle as external capture. Create the bundle first, then run:

```bash
python3 teacher_dataset.py tasks.v1.json --mode bundle \
  --source-git-sha "$(git rev-parse HEAD)" \
  --output-dir trusted-capture-bundle

export TYPESAFE_API_KEY=...
python3 teacher_dataset.py tasks.v1.json --mode run \
  --capture-manifest trusted-capture-bundle/capture_manifest.json \
  --output-dir run-YYYYMMDD
```

The harness refuses direct collection without both `TYPESAFE_API_KEY` and the exact capture manifest. It validates every frozen request before the first network request, preserves the exact HTTP response bytes under `raw/<case_id>.json`, and writes:

- normalized `teacher_rows.jsonl`;
- `raw_response_manifest.json` with request identity, exact raw-response SHA-256, canonical-response SHA-256, immutable Jev model version, and directly observed client latency.

HTTP 429 and 529 responses are retried with a bounded exponential backoff. Existing direct-capture artifacts are not overwritten unless `--force` is supplied. The raw-response manifest records `capture_mode: "direct-run"`; this is provenance metadata, not a correctness claim.

The response validator follows the current TypeSafe API response contract for this slice: exactly the requested answer is accepted, Score requires a complete `legend` matching the declared levels, and `usage.input_tokens` / `usage.output_tokens` must be present as non-negative integers. These checks protect capture integrity; they do not turn API conformance into teacher correctness.

## Import externally captured raw responses

An API key does not need to be copied into this execution environment. If the same case requests are executed in another trusted environment, save one raw TypeSafe response per case as `<case_id>.json`, then validate and normalize them here:

```bash
python3 teacher_dataset.py tasks.v1.json --mode import \
  --capture-manifest trusted-capture-bundle/capture_manifest.json \
  --raw-dir trusted-capture/raw \
  --output-dir normalized-run
```

Import mode requires the exact capture manifest and all 12 case files. Before normalization it revalidates the bundle against the current `tasks.v1.json`, checks every frozen request file byte-for-byte, rejects missing/duplicate/unexpected raw JSON files, and revalidates the returned Jev model version and typed probability/score shapes.

The normalized output contains:

- `teacher_rows.jsonl`;
- `raw_response_manifest.json`, which binds each case to its request SHA-256, exact raw-response file SHA-256, canonical response SHA-256, and returned immutable Jev model version;
- a deterministic `raw_response_set_sha256` over the ordered response descriptors.

External capture latency remains `null`; import does not invent latency that this harness did not observe. Raw-response completeness also does not prove that all rows use one teacher model version; the student-dataset readiness gate checks that separately.

## Student-dataset readiness gate

After authenticated teacher rows exist, join them back to the exact structured inputs before any model training:

```bash
python3 student_dataset.py tasks.v1.json normalized-run/teacher_rows.jsonl \
  --output-dir student-ready
```

The gate requires exactly one validated teacher row for every manifest case, exact request/split/schema/provenance identity, one immutable Jev model version across the first JD-LGBM-0 slice, and valid typed target distributions. It writes structured `features` joined from the manifest plus teacher targets; it does **not** train LightGBM. Missing, duplicated, mixed-version, or identity-mismatched rows are rejected.

## Evidence-chain integrity gate

After the authenticated 12-case capture has been normalized and the student-ready dataset has been produced, verify the entire retained chain before any training step:

```bash
python3 evidence_gate.py \
  tasks.v1.json \
  trusted-capture-bundle/capture_manifest.json \
  trusted-capture/raw \
  normalized-run/raw_response_manifest.json \
  normalized-run/teacher_rows.jsonl \
  student-ready/student_records.jsonl \
  student-ready/dataset_manifest.json \
  --output normalized-run/evidence_chain_verification.json
```

For a direct authenticated run, point the raw directory and raw-response manifest at the direct-run output instead.

The gate independently checks the fixed 12-case manifest order/set, frozen request bytes and hashes, raw response bytes and canonical hashes, capture mode/latency semantics, one immutable Jev model version, teacher-row provenance, typed target/distribution shape, student record joins, and dataset manifest hashes. It also requires `lightgbm_training_performed` to be the boolean value `false`.

```text
evidence-chain integrity PASS
  != authenticated-origin attestation by the verifier itself
  != teacher correctness / ground truth
  != model quality / Product Value
  != automatic permission to train or activate a student
```

Synthetic fixtures may satisfy this integrity gate, so a PASS is meaningful only together with the separately retained authenticated capture provenance. The first passive 12-case baseline still precedes #556 active curriculum acquisition.

## Atomic post-capture finalization

After either direct capture or external import has produced validated `teacher_rows.jsonl` and `raw_response_manifest.json`, finalize the fixed baseline in one network-free command:

```bash
python3 finalize_capture.py \
  tasks.v1.json \
  trusted-capture-bundle/capture_manifest.json \
  trusted-capture/raw \
  normalized-run/raw_response_manifest.json \
  normalized-run/teacher_rows.jsonl \
  --expected-source-git-sha "$(git rev-parse HEAD)" \
  --output-dir verified-capture
```

For a direct run, replace the last three capture inputs with `run-YYYYMMDD/raw`, `run-YYYYMMDD/raw_response_manifest.json`, and `run-YYYYMMDD/teacher_rows.jsonl`.

The finalizer:

- revalidates the frozen bundle and requires its `source_git_sha` to equal the explicitly supplied checkout SHA;
- builds the student-ready dataset without training a model;
- runs the full retained evidence-chain integrity check;
- writes `evidence_chain_verification.json` and `capture_verification_receipt.json`;
- records `network_requests_sent: 0` and `lightgbm_training_performed: false`;
- prepares all derived artifacts in a temporary directory and publishes the final output directory only after every gate passes.

If any gate fails, no final `verified-capture` directory is published. An existing output directory is never overwritten by this command.

```text
post-capture finalization PASS
  != authenticated-origin attestation by the finalizer itself
  != teacher correctness / ground truth
  != permission to activate a student
```

JD-LGBM-1 training remains a separate later stage and is not invoked by this command.

