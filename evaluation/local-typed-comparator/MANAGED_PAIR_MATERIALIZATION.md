# Managed pair input materialization handoff

Status: execution handoff only. This document does not claim that the model
bytes have been materialized in the current ChatGPT execution environment.

Related: #597, #622, #623, #624, #627, #628, #629, #630.

The fail-closed validators already define the authoritative byte contract.
This page only collects the acquisition steps needed on an eligible host. Do
not relax a hash, size, revision, fixture, or parity-policy gate to make an
acquisition succeed.

## 1. Source checkout

Run the whole pair from one clean SEI checkout at the exact merged revision
chosen for the experiment.

The paired helper and preflight both require their own script checkout to be
the same directory passed as `--sei-source-dir`. The managed reference and
Papaya captures then revalidate the same full Git SHA independently.

Also prepare a clean checkout of:

```text
m0rphtail/papaya
revision a76bc99bddafdac32863b2edc5319773e0cd3532
```

`capture_papaya_l0.py` verifies the required source blobs and the actual
import binding before inference.

## 2. Python-Laya 0.3.20 runtime wheel

Acquire the wheel without dependencies, then let the preflight verify it:

```bash
python3 -m pip download \
  --only-binary=:all: \
  --no-deps \
  --dest <runtime-dir> \
  'laya==0.3.20'
```

Authoritative identity:

```text
file        laya-0.3.20-py3-none-any.whl
bytes       118520
sha256      6039e802fa5effb8dd492061cd7ad39a43087beadc4a4fa4a649614e77eb83d4
source      NandhaKishorM/laya@23a17522aa4942da6cce53a995a275760320b691
```

Do not substitute a locally rebuilt wheel.

## 3. Python-Laya reference model directory

Acquire the standalone checkpoint from the immutable Hub revision. The commands below use Hugging Face's current `hf` CLI (`huggingface-cli` was renamed to `hf` in 2025):

```text
repository  convaiinnovations/laya-typed-decisions
revision    f9ab0b228f0fc0f14d873dbc99038f135c2da1b2
```

One explicit form is:

```bash
hf download \
  convaiinnovations/laya-typed-decisions \
  model.safetensors \
  encoder/config.json \
  rl_agent_config.json \
  tokenizer/tokenizer.json \
  tokenizer/tokenizer_config.json \
  --revision f9ab0b228f0fc0f14d873dbc99038f135c2da1b2 \
  --local-dir <reference-model-dir>
```

The complete runtime-consumed contract is already frozen in
`reference_model_directory_attestation.v1.json`:

| path | bytes | SHA-256 |
| --- | ---: | --- |
| `model.safetensors` | 842609220 | `4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e` |
| `encoder/config.json` | 2084 | `5268d24ad3b77c8151de5dcb0762ba4391619aad9ab0bda33e36fb083cfeae6d` |
| `rl_agent_config.json` | 847 | `ebf0cd524d92342a6be5e48e9fca3d7c2babfb5a56ccd79d2171ef5d8c7f7be8` |
| `tokenizer/tokenizer.json` | 3583228 | `6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30` |
| `tokenizer/tokenizer_config.json` | 337 | `08d4cf3ac4dca381759441b85b91a6d40e688471dcd33d15d6649eb0a9a854d1` |

Verify before doing anything else:

```bash
python3 verify_reference_model_directory.py \
  reference_model_directory_attestation.v1.json \
  <reference-model-dir>
```

The weight digest is independently repeated in multiple public manifests,
including `mizorewww/laya-coreml@4619e048...`,
`OpenAgentsInc/openagents`, and the `ollaya-dev/ollaya` registry. Public
GitHub mirrors also expose Git-LFS pointers with the same SHA-256 and size.
Those pointers/manifests are provenance corroboration, not substitute model
bytes.

## 4. Papaya Q8 candidate bytes

Papaya's evaluation candidate is intentionally a separate derived runtime
lineage. Use the same current `hf download` CLI surface as the reference path.

Acquire these four files from:

```text
repository  fr0stbit3/laya-typed-decisions-gguf
revision    54ec2dbb58aad9e3c74782cb2feb5801f72b13d0
```

For example:

```bash
hf download \
  fr0stbit3/laya-typed-decisions-gguf \
  laya-typed-decisions-Q8_0.gguf \
  laya-typed-decisions-head.safetensors \
  rl_agent_config.json \
  tokenizer_config.json \
  --revision 54ec2dbb58aad9e3c74782cb2feb5801f72b13d0 \
  --local-dir <papaya-candidate-dir>
```

Required identities:

| path | bytes | SHA-256 |
| --- | ---: | --- |
| `laya-typed-decisions-Q8_0.gguf` | 421407968 | `84f16d7b0b0a07343e7a6f8d8bd7ae9633aa0372d55621e2242d0ed9a0aca28c` |
| `laya-typed-decisions-head.safetensors` | 106052952 | `f115a16370df62e24a88aded4ef10d6542d2cdec9439df86d3aea3689f13ca44` |
| `rl_agent_config.json` | 847 | `ebf0cd524d92342a6be5e48e9fca3d7c2babfb5a56ccd79d2171ef5d8c7f7be8` |
| `tokenizer_config.json` | 337 | `08d4cf3ac4dca381759441b85b91a6d40e688471dcd33d15d6649eb0a9a854d1` |

The exact tokenizer byte identity was closed separately. Acquire
`tokenizer.json` from the immutable candidate tokenizer revision:

```bash
hf download \
  fr0stbit3/laya-typed-decisions-gguf \
  tokenizer.json \
  --revision 75300646cddbac2b47409fc1ca839c95bec004c8 \
  --local-dir <papaya-tokenizer-dir>
```

Required tokenizer identity:

```text
bytes   3583228
sha256  6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30
Git blob 2f4d8583e507b7466d2490e2d6c045647a822698
```

Prepare the evaluation-only clamp overlay:

```bash
python3 prepare_papaya_compat_overlay.py \
  <papaya-candidate-dir> \
  <papaya-tokenizer-dir>/tokenizer.json \
  <new-papaya-overlay-dir>
```

Immediately before the managed run, re-hash the staged overlay:

```bash
python3 prepare_papaya_compat_overlay.py \
  --verify-staged <papaya-overlay-dir>
```

The only admitted semantic config change remains:

```text
temperature_by_options.choice:11+
  raw      0.10058280825614929
  applied  0.5
```

Derived compatibility config:

```text
bytes   832
sha256  279207d55fefd56b2c6738dd141a3e10ab1d3f46b755c43faee42364ce1cc892
```

## 5. Pinned llama.cpp runtime

The first Papaya managed run uses SEI's existing b10964 runtime pin.

Unlike the model files above, this runtime has already been actually
materialized through the official llama.cpp Release workflow artifact in the
SEI evidence lineage:

```text
repository       ggml-org/llama.cpp
release tag      b10964
source commit    b29c606e28a01b1bc8c1351026a0fa6e616bf6c4
workflow run     34852868138
artifact id      10354692768
artifact name    llama-bin-ubuntu-x64.tar.gz
artifact ZIP sha 4b7bfdc8857ea001e602c8c330982bdcb50c28ea08c2f17705b9a728d7033805
inner archive    llama-b10964-bin-ubuntu-x64.tar.gz
inner sha256     9abf88aea48a55d0f80edb1ee20220b186848cca0b4e919d71518cfd7ca67443
llama-server sha 79e312188dc1d75c28201771f106e91de470b5cebdd838d31bb4db25eecf5d39
version          0.4.1-dev (build 10964, commit b29c606e2)
```

The durable receipt is:

`evaluation/local-model-probe/first_actual_runtime_materialization_evidence_2026-09-23.json`.

On a host with GitHub CLI access, the official workflow artifact can be
retrieved again with the run/artifact identity above. Regardless of acquisition
method, `preflight_managed_pair.py` and `capture_papaya_l0.py` require the
exact executable SHA and version before inference.

## 6. Preflight before model load

Once all bytes are present, run the shared preflight before either provider
loads model weights:

```bash
python3 preflight_managed_pair.py \
  --source-git-sha <exact-clean-SEI-SHA> \
  --sei-source-dir <same-SEI-checkout-containing-this-script> \
  --reference-model-dir <reference-model-dir> \
  --laya-runtime-wheel <laya-0.3.20-py3-none-any.whl> \
  --papaya-source-dir <clean-papaya-a76bc99-checkout> \
  --papaya-overlay-dir <papaya-overlay-dir> \
  --llama-binary <pinned-b10964-llama-server> \
  --output <new-path-outside-both-source-checkouts>/pair-preflight.json
```

A preflight PASS means only that the materialized input set satisfies the
already-merged byte/provenance/contracts. It does not load model weights or
claim inference/parity.

## 7. One-shot paired execution

After preflight is capable of passing, use the paired orchestrator rather than
running the providers from unrelated revisions:

```bash
python3 run_managed_pair.py \
  --source-git-sha <exact-clean-SEI-SHA> \
  --sei-source-dir <same-SEI-checkout-containing-this-script> \
  --reference-model-dir <reference-model-dir> \
  --laya-runtime-wheel <laya-0.3.20-py3-none-any.whl> \
  --papaya-source-dir <clean-papaya-a76bc99-checkout> \
  --papaya-overlay-dir <papaya-overlay-dir> \
  --llama-binary <pinned-b10964-llama-server> \
  --run-id <unique-run-id> \
  --output-dir <new-directory-outside-both-source-checkouts>
```

The orchestrator runs:

```text
input preflight
  -> managed Python-Laya reference capture
  -> managed Papaya capture
  -> raw numeric-difference report
  -> preregistered #627/#628 parity decision
```

Do not change the preregistered thresholds after observing live output.

## 8. Current ChatGPT-environment boundary

As of 2026-09-26, the current execution environment cannot materialize the
large Hugging Face/Xet model objects through its available download path.

Observed public transport evidence is narrower:

- the exact 842,609,220-byte reference digest appears in several independent
  public manifests and Git-LFS pointers;
- no GitHub Release or Actions artifact containing that exact reference model
  object was found;
- the large `ollaya` CUDA release archives were inspected and are CUDA
  library packs, not bundled Laya model weights;
- no GitHub mirror/Release/Actions artifact for the exact Papaya Q8/head
  SHA-256 values was found;
- the pinned b10964 llama runtime is already materialized Evidence and is not
  the remaining transport blocker.

Therefore:

```text
materialization instructions frozen
  != model bytes materialized here
  != model load
  != live inference
  != numeric parity result
```

The remaining external-input blocker is specifically the exact reference F16
model directory plus the exact Papaya Q8/head candidate bytes on an eligible
host.
