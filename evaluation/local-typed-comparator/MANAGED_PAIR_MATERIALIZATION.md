# Managed pair input materialization handoff

Status: execution handoff only. This document does not claim that the model
bytes have been materialized in the current ChatGPT execution environment.

Related: #597, #622, #623, #624, #627, #628, #629, #630, #631, #635, #636.

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

## 2.1 DNS-independent runtime dependency fallback

The managed reference runner records the dependency versions actually used; it
does not turn Laya's dependency ranges into an upstream runtime lock. On
2026-09-27, however, the current ChatGPT environment had no shell DNS for PyPI,
Hugging Face, or GitHub, while the connected GitHub Actions artifact path was
still able to materialize release artifacts.

A **host-assisted transport candidate** was therefore retained in
`runtime_dependency_wheelhouse.v1.json` for the observed Linux x86_64 /
Python 3.13.5 host. It is not a product/runtime pin and it is **not a
self-contained wheelhouse**.

The four retained wheels supply Laya plus three managed-reference
dependencies:

```text
wheelhouse supplies
  laya
  transformers
  tokenizers
  safetensors

still required from the execution host
  torch
  huggingface-hub
  numpy
  fastapi
  uvicorn
```

The managed reference capture checks those host distributions again and retains
the versions it actually uses.

The four materialized wheels are:

| distribution | version | wheel SHA-256 | GitHub workflow run | artifact id | artifact expires |
| --- | --- | --- | ---: | ---: | --- |
| Laya | 0.3.20 | `6039e802fa5effb8dd492061cd7ad39a43087beadc4a4fa4a649614e77eb83d4` | 35960902240 | 10792385664 | 2026-12-23T05:39:21Z |
| Transformers | 5.17.0 | `78ec1ce21579b38dfb83950a0658cd119f87212a2fcfdff478096ce9d6c03801` | 34367538606 | 10110585452 | 2026-12-08T15:01:53Z |
| tokenizers | 0.23.2 | `e8ccc55262e36550c54eafadf93df8ac449b454373727ef47c826adbeb733a1a` | 33735388484 | 9885597962 | 2026-12-02T08:48:51Z |
| safetensors | 0.9.0rc1 | `d5109939a6f11d502c1656c927e3b9413f8d48dba635204c2f21cdc465e5035a` | 35890001765 | 10764477075 | 2026-12-22T16:37:11Z |

The outer Actions artifact ZIP digests, successful workflow head revisions,
exact wheel filenames/tags, and artifact expiration timestamps are also
retained in the manifest. The GitHub API audit on 2026-09-27 found all four
artifacts unexpired and their workflow head SHAs equal to the retained source
revisions.

The Actions artifacts are a **time-bounded fallback**. After the recorded
expiration timestamps, `gh run download` may no longer work and must not be
treated as an immutable long-term package registry.

While they remain available, a host with GitHub CLI access can obtain the
recorded artifacts, for example:

```bash
gh run download 35960902240 -R NandhaKishorM/laya \
  -n dist -D <artifact-root>/laya

gh run download 34367538606 -R huggingface/transformers \
  -n python-dist -D <artifact-root>/transformers

gh run download 33735388484 -R huggingface/tokenizers \
  -n pypi_files-ubuntu-x86_64-auto-abi3 -D <artifact-root>/tokenizers

gh run download 35890001765 -R safetensors/safetensors \
  -n wheels-linux-x86_64-3.14 -D <artifact-root>/safetensors
```

Collect only the exact four retained wheel filenames into one directory, then
validate them before installation:

```bash
python3 verify_runtime_dependency_wheelhouse.py \
  runtime_dependency_wheelhouse.v1.json \
  <wheelhouse>
```

The validator fails closed on wheel-set drift, bytes/SHA-256 drift, package
name/version metadata drift, wheel-tag drift, artifact provenance shape drift,
or any attempt to promote the packet beyond transport-candidate scope.

If this wheelhouse is used for the actual managed pair, keep the same verified
directory available and pass it to the shared preflight:

```bash
--runtime-wheelhouse-dir <wheelhouse>
```

The preflight revalidates the manifest + wheel bytes and additionally requires
the currently observed `transformers`, `tokenizers`, and `safetensors`
versions to equal the retained transport candidate. The exact Laya wheel is
still checked independently by the existing Laya wheel SHA/size gate.

This binding intentionally does **not** require the execution host's
`torch`, `huggingface-hub`, `numpy`, `fastapi`, or `uvicorn`
versions to equal the host on which #635 was observed. Those distributions must
exist and their actual versions remain captured, but they are not promoted into
a product/runtime pin.

The wheelhouse check also does not prove installation origin for
Transformers/tokenizers/safetensors. It proves that the retained wheel bytes are
valid and that the currently observed package versions match those wheels. The
preflight receipt therefore keeps
`runtime_installation_origin_attested=false` unless a future, separately
designed provenance mechanism establishes more.

The current environment additionally demonstrated an offline install of these
four wheels together with its already-present host dependencies. That
observation is explicitly host-assisted rather than proof that the four-wheel
directory is self-contained. The resulting isolated runtime imported:

```text
laya          0.3.20
transformers  5.17.0
tokenizers    0.23.2
safetensors   0.9.0rc1
```

and successfully imported Transformers' ModernBERT implementation.

That observation means only that a runnable dependency set can be transported
without PyPI/Hugging Face shell access. In particular:

```text
runtime wheelhouse transport PASS
  != upstream product runtime pin
  != exact model bytes
  != model load
  != live inference
  != numeric parity
```

The `safetensors 0.9.0rc1` member is a prerelease selected only because the
stable 0.8.0 Actions artifacts had already expired while Transformers 5.17.0
requires `safetensors>=0.8.0`. An eligible execution host may use another
dependency set satisfying the declared package ranges; the managed capture
retains the versions it actually observes.

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

A second public transport candidate is retained in
`reference_model_transport.v1.json`. It binds the exact same five-file
contract to:

- the immutable Hugging Face revision above; and
- the public `truespar/paddock@610cd8f5...` mirror catalog
  (`crates/paddock-manager/models.toml`, blob
  `330a4ce13bd17fda07f6945123b3635bf548c95c`).

All five mirror rows match the existing reference attestation byte-for-byte,
including the 842,609,220-byte model weight SHA-256
`4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e`.

On an eligible host, either transport can be materialized atomically:

```bash
python3 materialize_reference_model.py \
  reference_model_transport.v1.json \
  --transport huggingface-immutable \
  --output-dir <new-reference-model-dir>
```

or:

```bash
python3 materialize_reference_model.py \
  reference_model_transport.v1.json \
  --transport truespar-paddock-mirror \
  --output-dir <new-reference-model-dir>
```

The materializer downloads into a sibling staging directory, verifies every
file's exact byte count and SHA-256, runs the existing
`verify_reference_model_directory.py` contract against the complete staged
directory, and only then atomically publishes the destination. Any download,
size, digest or directory-contract failure removes staging and leaves the
destination absent.

The TrueSpar URLs are deliberately **not** labelled content-addressed. Their
pinned catalog is provenance for the expected mirror mapping; the post-download
hash gate remains authoritative.

In the current ChatGPT shell, outbound DNS/HTTPS remains unavailable, so neither
transport succeeded here and no reference model bytes are claimed as
materialized. A separate public `chrisns/laya-mac-serve` Actions artifact was
also found to bundle the real checkpoint, but its 1,011,457,975-byte artifact
exceeds the connector's 536,870,912-byte download ceiling. These are transport
constraints, not model-validation failures.

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

### Rejected alternate reference transports

A public Kaggle model at
`ser8147/arc-laya/Transformers/typed-decisions` was inspected as a possible
independent transport on 2026-09-27. It is **not** the frozen Python-Laya
reference checkpoint.

The public operator record shows Kaggle versions 1 and 2. Version 2 contains a
`model.safetensors` with the same 842,609,220-byte length as the reference,
but its metadata identifies it as an ARC-specific fine-tune on 1,720 cases and
does not provide the frozen reference SHA-256. Equal byte length is therefore
not identity Evidence.

Version 1 is also a derived fine-tune: its retained metadata names
`ser8147/arc-laya-finetune-data` as training data and its
`rl_agent_config.json` has `fine_tuned=true`, 816 bytes, versus the frozen
reference contract's 847-byte config. Neither version is admitted as a
reference transport.

```text
same architecture / same weight-file byte length
  != same checkpoint bytes

derived ARC fine-tune
  != frozen convaiinnovations/laya-typed-decisions reference
```

The public macOS LayaServe releases were also inspected only as transport
leads. They publish a single approximately 1.1 GB disk image rather than a
standalone or split reference-weight artifact, and their release workflow does
not upload the model as a separate Actions artifact. That packaging route is
not an admitted exact-byte transport for this experiment.

## 4. Papaya Q8 candidate bytes

Papaya's evaluation candidate is intentionally a separate derived runtime
lineage.

The canonical transport contract is retained in
`papaya_candidate_transport.v1.json`. Unlike the Python-Laya reference,
no independent exact-byte mirror of the Q8 backbone/head has been identified;
the admitted transport therefore remains the immutable Hugging Face repository
revision only.

Materialize all candidate inputs atomically with:

```bash
python3 materialize_papaya_candidate.py \
  papaya_candidate_transport.v1.json \
  --output-dir <new-papaya-candidate-dir>
```

The materializer downloads into sibling staging, verifies every file while
streaming, runs the existing Papaya overlay-input verifier over the complete
staged set, and publishes the destination only after all checks pass. A size,
SHA-256, URL/revision, or overlay-input verification failure removes staging and
leaves the destination absent.

Four files are bound to:

```text
repository  fr0stbit3/laya-typed-decisions-gguf
revision    54ec2dbb58aad9e3c74782cb2feb5801f72b13d0
```

| path | bytes | SHA-256 |
| --- | ---: | --- |
| `laya-typed-decisions-Q8_0.gguf` | 421407968 | `84f16d7b0b0a07343e7a6f8d8bd7ae9633aa0372d55621e2242d0ed9a0aca28c` |
| `laya-typed-decisions-head.safetensors` | 106052952 | `f115a16370df62e24a88aded4ef10d6542d2cdec9439df86d3aea3689f13ca44` |
| `rl_agent_config.json` | 847 | `ebf0cd524d92342a6be5e48e9fca3d7c2babfb5a56ccd79d2171ef5d8c7f7be8` |
| `tokenizer_config.json` | 337 | `08d4cf3ac4dca381759441b85b91a6d40e688471dcd33d15d6649eb0a9a854d1` |

The exact `tokenizer.json` is intentionally bound to the separately attested
immutable tokenizer revision:

```text
revision 75300646cddbac2b47409fc1ca839c95bec004c8
bytes    3583228
sha256   6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30
Git blob 2f4d8583e507b7466d2490e2d6c045647a822698
```

The materialized directory therefore contains the four candidate-revision
files plus the attested tokenizer at its own revision. Materialization still
does **not** prepare the compatibility overlay.

Prepare the evaluation-only clamp overlay only after successful candidate
materialization:

```bash
python3 prepare_papaya_compat_overlay.py \
  <papaya-candidate-dir> \
  <papaya-candidate-dir>/tokenizer.json \
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

Model-free mechanics are retained in:

```bash
python3 -m unittest -v test_materialize_papaya_candidate.py
```

A successful materializer receipt proves only exact candidate input bytes and
the already-defined overlay-input preconditions. It does not claim overlay
publication, model load, inference, numeric parity, task quality, or shipping
readiness.

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

When using the #635 host-assisted wheelhouse, add:

```bash
--runtime-wheelhouse-dir <verified-wheelhouse>
```

A preflight PASS means only that the materialized input set satisfies the
already-merged byte/provenance/contracts. If the optional wheelhouse is
provided, its verification and the matched transported dependency versions are
also retained in the preflight receipt. It does not load model weights or claim
inference/parity.

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

When using the retained runtime wheelhouse, add the same optional
`--runtime-wheelhouse-dir <verified-wheelhouse>` argument. The paired runner
passes it only to preflight; the two provider captures keep their existing
runtime/provenance contracts unchanged.

The orchestrator runs:

```text
input preflight
  -> managed Python-Laya reference capture
  -> managed Papaya capture
  -> raw numeric-difference report
  -> preregistered #627/#628 parity decision
```

Do not change the preregistered thresholds after observing live output.

After the evidence directory has been copied back from the execution host,
verify the returned chain without re-running the models:

```bash
python3 verify_managed_pair_bundle.py \
  <returned-evidence-directory> \
  --source-git-sha <exact-clean-SEI-SHA>
```

This re-hashes the receipt, every completed artifact, and any retained
failed-stage partial output. It verifies internal transfer/integrity bindings;
it does not authenticate the host or recompute inference/parity.

## 8. Current ChatGPT-environment boundary

As of 2026-09-27, the current execution environment cannot materialize the
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
- the TrueSpar reference mirror is independently catalogued with the exact
  reference hashes, but even its 337-byte/847-byte files fail at DNS resolution
  in the current shell; this is a transport-environment failure, not a byte
  mismatch;
- the public Kaggle `ser8147/arc-laya` versions were rejected because both are
  derived fine-tunes rather than the frozen reference checkpoint;
- the public LayaServe macOS release exposes only an approximately 1.1 GB
  bundled disk image and no separate/split model artifact suitable for the
  current GitHub artifact handoff;
- the pinned b10964 llama runtime is already materialized Evidence and is not
  the remaining transport blocker.

On 2026-09-27 the GitHub Actions artifact path additionally materialized the
exact Laya wheel plus a compatible Transformers/tokenizers/safetensors runtime
candidate and verified the resulting imports offline. Therefore the Python
runtime dependency transport is no longer the limiting factor in this
environment.

Shell DNS remains unavailable for both Hugging Face and GitHub. Consequently,
this environment still does not contain:

- a clean exact SEI source checkout usable by the managed Git cleanliness gate;
- a clean exact Papaya source checkout;
- the exact reference F16 model directory;
- the exact Papaya Q8/head candidate bytes.

Therefore:

```text
runtime dependency transport demonstrated
  + materialization instructions frozen
  != exact source checkouts materialized here
  != model bytes materialized here
  != model load
  != live inference
  != numeric parity result
```

The remaining semantic external-input blockers for the actual paired experiment
are still the exact reference F16 model bytes and exact Papaya Q8/head bytes on
an eligible host; the current ChatGPT container additionally lacks the two
clean Git checkouts required by the managed runners.
