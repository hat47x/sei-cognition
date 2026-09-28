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

## 2.2 Host-assisted exact-wheel evaluation runtime

When using the retained four-wheel transport candidate, materialize a dedicated
evaluation venv with:

```bash
python3 materialize_managed_runtime_env.py \
  <verified-runtime-wheelhouse> \
  --output-dir <new-managed-runtime-env>
```

The helper revalidates the wheelhouse and the retained Linux x86_64 /
Python 3.13.5 surface, creates the venv with
`system-site-packages=true`, then installs exactly the retained four wheels
offline with:

```text
pip install
  --no-index
  --no-deps
  --force-reinstall
  <Laya wheel>
  <Transformers wheel>
  <tokenizers wheel>
  <safetensors wheel>
```

The post-install probe requires all four transported modules to import from
inside the venv and verifies their PEP 610 `direct_url.json` local-file
origins against the retained wheel filenames and SHA-256 values. It also
requires an offline ModernBERT import.

The following packages remain host-assisted through
`system-site-packages` and are deliberately excluded from the exact-wheel
installation-origin claim:

```text
torch
huggingface-hub
numpy
fastapi
uvicorn
```

Therefore a successful environment records:

```text
transported_wheel_installation_origin_attested  true
runtime_installation_origin_attested            false
host_dependency_versions_pinned                 false
self_contained_runtime                           false
environment_relocatable                         false
model_weights_loaded                             false
live_inference                                   false
numeric_parity                                   false
shipping_decision                                false
```

The environment and its source wheelhouse are path-bound and should not be
moved after verification.

The managed-preflight integration is now enabled. Use the exact venv interpreter
and pass both the wheelhouse and environment paths:

```bash
<managed-runtime-env>/bin/python preflight_managed_pair.py \
  --source-git-sha <exact-clean-SEI-SHA> \
  --sei-source-dir <same-SEI-checkout-containing-this-script> \
  --reference-model-dir <reference-model-dir> \
  --laya-runtime-wheel <verified-runtime-wheelhouse>/laya-0.3.20-py3-none-any.whl \
  --papaya-source-dir <clean-papaya-a76bc99-checkout> \
  --papaya-overlay-dir <papaya-overlay-dir> \
  --llama-binary <pinned-b10964-llama-server> \
  --runtime-wheelhouse-dir <verified-runtime-wheelhouse> \
  --runtime-environment-dir <managed-runtime-env> \
  --output <external-preflight-receipt.json>
```

Preflight re-verifies the wheel bytes, PEP 610 origins, module locations,
host-assisted dependency availability, and exact current interpreter binding
before any model load. The broader
`runtime_installation_origin_attested=false` boundary remains unchanged.

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
directory, and only then atomically publishes the destination.

Transient remote transport/source-read failures use a bounded per-file retry
policy (default: 3 attempts). Each retry removes that file's partial staging
bytes and restarts the file from byte zero; HTTP Range/resume behavior is
deliberately not assumed. Local staging-directory/file open/write/close errors
are not transport retries: they fail immediately. Byte-size or SHA-256 mismatch
is also an integrity failure and is **not retried**. Successful file receipts
retain `download_attempts`.

Override the bound only when needed:

```bash
python3 materialize_reference_model.py \
  reference_model_transport.v1.json \
  --transport huggingface-immutable \
  --attempts <N> \
  --output-dir <new-reference-model-dir>
```

Any exhausted transport failure, integrity failure, or directory-contract
failure removes staging and leaves the destination absent.

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

A superficially similar public repository,
`fr0stbit3/laya-gguf`, was rechecked on 2026-09-28 and is **not** an admitted
mirror. Its current Hub metadata identifies the base lineage as
`convaiinnovations/laya`, while this experiment is fixed to the
`convaiinnovations/laya-typed-decisions` /
`fr0stbit3/laya-typed-decisions-gguf` lineage below. Public integrations such
as `llamadart` pin that separate `laya-gguf` repository and use similarly
sized Q8/head files, but approximate file size, architecture, naming, or task
surface is not byte identity Evidence.

Therefore:

```text
fr0stbit3/laya-gguf
  != independent mirror of fr0stbit3/laya-typed-decisions-gguf

approximately 421 MB Q8 + 106 MB head
  != retained SHA-256 pair

similar local typed-decision runtime
  != admissible Papaya candidate transport
```

Do not substitute that lineage unless every retained candidate file is first
shown to match the exact SHA-256/size contract below and the transport contract
is separately reviewed and updated. No such exact-byte equivalence is currently
established.

Materialize all candidate inputs atomically with:

```bash
python3 materialize_papaya_candidate.py \
  papaya_candidate_transport.v1.json \
  --output-dir <new-papaya-candidate-dir>
```

The materializer downloads into sibling staging, verifies every file while
streaming, runs the existing Papaya overlay-input verifier over the complete
staged set, and publishes the destination only after all checks pass.

As on the reference path, transient remote transport/source-read failures use
a bounded per-file retry policy (default: 3 attempts). Every retry removes the
partial staged file and restarts from byte zero; no Range/resume behavior is
assumed. Local staging-directory/file open/write/close errors fail immediately
rather than consuming the download retry budget. Byte-size or SHA-256 mismatch
is also an integrity failure and is **not retried**. Successful file receipts
retain `download_attempts`.

Optional override:

```bash
python3 materialize_papaya_candidate.py \
  papaya_candidate_transport.v1.json \
  --attempts <N> \
  --output-dir <new-papaya-candidate-dir>
```

An exhausted transport failure, integrity failure, URL/revision drift, or
overlay-input verification failure removes staging and leaves the destination
absent.

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

## 4.1 One-command managed model-input workspace

Once an eligible host can reach the admitted reference and Papaya transports,
the existing materializers can be composed without manually stitching their
outputs together:

```bash
python3 materialize_managed_pair_inputs.py \
  --source-git-sha <exact-clean-SEI-SHA> \
  --sei-source-dir <same-SEI-checkout-containing-this-script> \
  --reference-transport huggingface-immutable \
  --output-dir <new-managed-input-workspace>
```

Use `--reference-transport truespar-paddock-mirror` only when deliberately
selecting the separately retained exact-hash mirror mapping.

If the #635 host-assisted wheelhouse is available, add:

```bash
--runtime-wheelhouse-dir <verified-wheelhouse>
```

To create the #645 exact-wheel managed venv inside the same workspace, also
add:

```bash
--materialize-runtime-environment
```

The one-command workspace forwards one shared model-download attempt bound to
both reference and Papaya materializers. It defaults to 3; override it with:

```bash
--attempts <N>
```

The composite receipt retains the policy explicitly:

```text
attempts_per_file           N
restart_from_zero           true
retryable_failures          remote transport/source-read only
integrity_failures_retried  false
```

After any optional runtime-env has been created, the wrapper checks free disk
on the workspace filesystem **before the first model transfer**. The exact
retained model-input byte contract is currently:

```text
reference inputs   846,195,716 bytes
Papaya inputs      531,045,332 bytes
total            1,377,241,048 bytes
```

A configurable working reserve is added to that exact lower bound. The default
is 256 MiB (268,435,456 bytes), so the current default gate requires at least
1,645,676,504 free bytes after runtime materialization. Override only when the
execution host has a deliberate storage plan:

```bash
--disk-reserve-bytes <N>
```

The receipt retains the exact model-input total, configured reserve, required
free bytes, and observed free bytes immediately before model transfer. This is a
disk-capacity gate, not a RAM estimate or a claim that every filesystem quota is
observable through `disk_usage`.

That flag requires the wheelhouse. Runtime creation is deliberately placed
before the large model transfers, so platform/pip/PEP-610 failures do not occur
after downloading roughly 1.37 GB of model inputs.

The wrapper performs:

```text
validate exact clean SEI source SHA
  -> bind reference/Papaya manifest objects to the exact retained raw bytes
  -> optionally verify the retained runtime wheelhouse
  -> optionally materialize + verify runtime-env/
  -> materialize + verify reference model
  -> materialize + verify Papaya candidate
  -> prepare Papaya compatibility overlay
  -> re-hash overlay
  -> verify overlay Q8/head symlinks target the final candidate directory
  -> write managed-pair-input-materialization.json
```

The output layout is:

```text
<workspace>/
  runtime-env/            # only with --materialize-runtime-environment
  reference-model/
  papaya-candidate/
  papaya-overlay/
  managed-pair-input-materialization.json
```

The receipt keeps relative layout names and manifest digests rather than
host-local absolute paths.

This wrapper deliberately does **not** claim whole-workspace atomic publication.
The current overlay implementation creates absolute symlinks for the large
Q8/head pair. Moving a fully prepared parent staging tree would invalidate those
targets. Instead, each large sub-materializer keeps its own atomic publish
semantics, the final workspace path is used for overlay construction, and any
failure removes the entire new workspace so the requested destination is absent
after failure.

For the same reason, a successful workspace is **not relocatable**. Its overlay
must be used in place. The receipt fixes:

```text
workspace_relocatable                          false
runtime_environment_materialized                true/false
transported_wheel_installation_origin_attested  true/false
runtime_installation_origin_attested            false
model_weights_loaded                            false
live_reference_inference               false
live_papaya_inference                  false
numeric parity decision observed       false
```

When `runtime-env/` is included, keep both the workspace and source
wheelhouse at their verified paths. Launch subsequent preflight / paired
execution with `<workspace>/runtime-env/bin/python`,
`--runtime-wheelhouse-dir <verified-wheelhouse>`, and
`--runtime-environment-dir <workspace>/runtime-env`.

This command does not materialize the clean Papaya source checkout or the
pinned llama.cpp runtime; those remain separate preflight inputs.

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

When also using the #645 exact-wheel managed venv, run the command with
`<managed-runtime-env>/bin/python` and additionally add:

```bash
--runtime-environment-dir <managed-runtime-env>
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
`--runtime-wheelhouse-dir <verified-wheelhouse>` argument. When using the
managed venv, invoke `run_managed_pair.py` with that venv's `bin/python` and
also pass `--runtime-environment-dir <managed-runtime-env>`. Both optional
paths are forwarded only to preflight, which verifies the environment and exact
interpreter before either provider loads weights. All subsequent stages are then
spawned with the same `sys.executable`.

The two provider captures keep their existing provider/model/runtime provenance
contracts unchanged.

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

On 2026-09-27 the GitHub transport audit was extended with exact public
repository evidence so later runs do not repeat the same dead ends:

- `he-jev/laya@c5d78730f3493e4fe16d61507ef4b78eef7318cf`
  retains `typed-decisions/model.safetensors` as Git blob
  `3fb9c9678050815e76d0c847115919d7871ace3e`. The tracked file is the
  standard 134-byte Git-LFS pointer whose object id is exactly
  `sha256:4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e`
  and whose declared object size is exactly 842,609,220 bytes. The repository
  tree also retains the four small typed-decisions files at the expected Git
  blobs. However, both the GitHub `raw` and connector file paths return the
  134-byte pointer, not the LFS object; the repository has no Releases or
  Actions runs carrying the weights. This is strong independent provenance,
  but not current-environment materialization.
- `danielmeppiel/apm-laya-triage` successfully ran the genuine frozen
  checkpoint in public Actions. Full-run `36122098981` retained eight
  `laya-shard-*` artifacts, `full-laya-report`, and `experiment-source`.
  Their published artifact sizes are all only a few megabytes or less and the
  workflow uploads results after each runner downloads the checkpoint itself;
  it does not upload the model cache. Therefore those successful live runs are
  independent execution corroboration, not a weight transport.
- the exact Papaya filenames and SHA-256 values were searched across public
  GitHub code/workflow surfaces. `m0rphtail/papaya` downloads the files from
  Hugging Face at runtime and does not publish a model-bearing Actions artifact,
  Release asset, or GHCR build path in the pinned source. No independent
  GitHub artifact for the exact 421,407,968-byte Q8 backbone or
  106,052,952-byte decision head was found.
- public split-artifact searches for the exact 842,609,220-byte reference
  object found no workflow that publishes sub-512-MB chunks. The known
  model-bearing LayaServe artifact remains larger than the connector download
  ceiling, so it does not create a usable current-environment bypass.

These findings deliberately do not add another admitted transport. A Git-LFS
pointer, successful third-party inference run, or model-bearing oversized bundle
must not be relabelled as materialized exact bytes.

### OCI/container transport audit

A separate 2026-09-28 audit checked whether a public container image could carry
the exact 842,609,220-byte reference object around the current Hugging Face/Xet
transport failure. The durable packet is:

`oci_reference_transport_audit_2026-09-28.json`

Four concrete OCI leads were inspected at exact Git revisions:

- `beremaran/laya-docker@90535d3...` publishes
  `ghcr.io/beremaran/laya-docker`, but its Dockerfile keeps `/models` as a
  volume and downloads checkpoints on first inference. The image does not
  transport the reference bytes.
- `ZulfiFazhar/system-one@f908c07...` publishes
  `ghcr.io/zulfifazhar/system-one`, but model files live in an externally
  mounted `models/` directory and are downloaded when absent. The documented
  default is the multilingual checkpoint, not the frozen typed-decisions
  reference.
- `cloudn1ne/system1@7a1d89e...` publishes
  `ghcr.io/cloudn1ne/system1`, and its Dockerfile explicitly states that
  checkpoint weights are never baked into the image.
- `wescodess/budds@820fef8...` has the useful opposite build recipe: its
  Laya evaluator Dockerfile downloads the immutable
  `f9ab0b228f...` typed-decisions revision, verifies the exact
  `4fa56de7...a24e` weights SHA-256, and copies the checkpoint into the final
  offline image. However, the inspected repository workflow tests that evaluator
  without Docker/model weights and exposes no model-bearing image publish
  workflow or public image reference.

Therefore the OCI audit found one exact **recipe**, but no public exact
model-bearing OCI **artifact**:

```text
public GHCR runtime image
  != model-bearing image

exact model-bearing Dockerfile recipe
  != published OCI artifact

published OCI artifact
  + independently verified layer/model bytes
  = potential transport candidate
```

No OCI manifest or layer was pulled by this audit, and no new reference
transport is admitted.


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
