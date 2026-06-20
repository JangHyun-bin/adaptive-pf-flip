# S515 Full-Sequence Renderer Contract Handoff

## Goal

Promote the current S515/S552 visual candidate from a corrected GIF into a
reproducible renderer/backend contract that can be consumed frame-by-frame.

This is still a post-tonemap low-frequency correction path. It is not yet a
renderer-native volumetric water or material model. Its purpose is to make the
current best full48 visual candidate deterministic, inspectable, and executable
through the same contract boundary that a real backend renderer can later
replace.

## Completed Chain

- S552 selected the bounded raw-contrast T4 correction as the current full48
  visual candidate.
- S555 regenerated the same 48 corrected frames while writing per-frame runtime
  bindings:
  - `base_rgb`
  - `positive_delta_rgb`
  - `negative_delta_rgb`
  - `correction_mask`
- S556 published the S555 gallery through Cloudflare quick tunnel for live
  review.
- S557 converted the S555 sequence summary into
  `lsfs_mitsuba_low_frequency_renderer_acceptance_package`.
- S558 built and validated a full48 renderer job manifest.
- S559 executed the renderer job dry-run and reproduced all accepted references
  with zero image diff.
- S560 built backend scene descriptors from the renderer job manifest.
- S561 executed the descriptor-level backend dry-run with zero image diff.
- S562 executed the same descriptors through an external process stub with zero
  image diff and no process failures.
- S563 published the S562 backend process proof gallery through Cloudflare quick
  tunnel.

## Key Artifacts

- Sequence bindings report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings_s555.md`
- Public S555 binding gallery:
  `https://operating-intended-analyses-individually.trycloudflare.com`
- Sequence acceptance package report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_sequence_acceptance_package_s557.md`
- Renderer job manifest validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_job_manifest_validation_s558.md`
- Renderer job dry-run validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_job_dry_run_validation_s559.md`
- Backend adapter validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_backend_adapter_validation_s560.md`
- Backend adapter dry-run validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_backend_adapter_dry_run_validation_s561.md`
- Backend process stub validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_backend_process_stub_validation_s562.md`
- Public S562 backend process proof:
  `https://passport-ground-excerpt-equipped.trycloudflare.com`

## Verification

- S555 sequence adapter:
  - `status=ready`
  - `frames=48`
  - `interpolated=40`
  - binding files missing: `0`
  - corrected frame hashes match S552: `48/48`
- S557 acceptance package:
  - `status=ready`
  - `frames=48`
  - required bindings: `144/144`
- S558 renderer job validation:
  - `status=passed`
  - `total=606`
  - `failed=0`
- S559 renderer job dry-run validation:
  - `status=passed`
  - `total=465`
  - `failed=0`
  - max image diff: `0`
- S560 backend adapter validation:
  - `status=passed`
  - `total=985`
  - `failed=0`
- S561 backend adapter dry-run validation:
  - `status=passed`
  - `total=1378`
  - `failed=0`
  - max image diff: `0`
- S562 backend process stub validation:
  - `status=passed`
  - `total=1481`
  - `failed=0`
  - process failures: `0`
  - max image diff: `0`
- S563 public checks:
  - `GET /index.html`: `200`
  - `HEAD /assets/shot.gif`: `200`

## Current Meaning

The current full48 visual result is no longer just a generated artifact. It is
now reproducible through:

1. a per-frame texture binding contract,
2. a renderer job manifest,
3. backend scene descriptors,
4. a process-level execution interface,
5. zero-diff validation against accepted references.

This gives the next renderer step a stable boundary: replace the process stub
with a real backend implementation while preserving the descriptor schema and
validation gates.

## Next

Build the real backend bridge for this contract. The practical next slice is:

1. Add a backend executable/script that consumes one
   `lsfs_mitsuba_low_frequency_backend_scene_descriptor` and writes the declared
   output image, metadata, validation, and strip artifacts.
2. Keep the current process-stub CLI shape so `run_mitsuba_low_frequency_backend_process_stub.py`
   can call either the stub or the real backend script.
3. First target can still be a post-tonemap image backend; after that, move the
   correction into renderer-native material/light/volume response instead of
   using accepted-reference deltas.
4. Publish the first real-backend gallery and compare it against S563.
