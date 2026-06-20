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
- S564 replaced the process stub with
  `tools/mitsuba_low_frequency_post_tonemap_backend.py`, preserving the same
  descriptor/process CLI while emitting a non-stub backend result schema.
- S565 published the S564 post-tonemap backend proof gallery through Cloudflare
  quick tunnel.
- S566 compared S562 and S564 and confirmed identical GIF SHA256/byte size.
- S567 converted the S555 low-frequency correction masks into
  `lsfs_mitsuba_source_response_mask_source`, producing RGBA alpha layers and
  gallery strips that existing renderer-response tooling can consume.
- S568 built a renderer-neutral light-response contract from S567, turning the
  correction evidence into bounded per-frame response anchors.

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
- Post-tonemap backend script:
  `tools/mitsuba_low_frequency_post_tonemap_backend.py`
- Post-tonemap backend validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_post_tonemap_backend_process_validation_s564.md`
- Public S564/S565 backend proof:
  `https://providence-secrets-stats-last.trycloudflare.com`
- Stub/backend comparison:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_post_tonemap_backend_comparison_s566.md`
- Low-frequency response mask source:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_low_frequency_response_mask_source_s567.md`
- Low-frequency light response contract:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_low_frequency_light_response_contract_s568.md`

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
- S564 post-tonemap backend process validation:
  - `status=passed`
  - `total=1481`
  - `failed=0`
  - backend kind: `post_tonemap_texture_backend`
  - backend result schema:
    `lsfs_mitsuba_low_frequency_post_tonemap_backend_result`
  - process failures: `0`
  - max image diff: `0`
- S565 public checks:
  - `GET /index.html`: `200`
  - `HEAD /assets/shot.gif`: `200`
- S566 stub/backend parity:
  - S562 GIF SHA256:
    `8C6E621C4656B3F5D7AA85C44418CA3CFC455B4E03F5BD07892C62A14B544ACF`
  - S564 GIF SHA256:
    `8C6E621C4656B3F5D7AA85C44418CA3CFC455B4E03F5BD07892C62A14B544ACF`
  - result: `identical`
- S567 response mask source:
  - `status=ready`
  - `frames=48`
  - missing references: `0`
  - dimension mismatches: `0`
  - mean mask coverage: `0.10284999517746914`
  - max mask coverage: `0.18578510802469136`
- S568 light response contract:
  - `status=ready`
  - `frames=48`
  - anchors: `384`
  - max anchors per frame: `8`
  - mean mask coverage: `0.08506385834619341`
  - max mask coverage: `0.1625829475308642`

## Current Meaning

The current full48 visual result is no longer just a generated artifact. It is
now reproducible through:

1. a per-frame texture binding contract,
2. a renderer job manifest,
3. backend scene descriptors,
4. a process-level execution interface,
5. zero-diff validation against accepted references.

This gives the next renderer step a stable boundary. The first non-stub backend
is now in place and still produces the same accepted full48 visual output. The
low-frequency correction evidence has also been lifted into response-mask and
light-response contract formats, so the next step can drive renderer-native
parameters instead of only replaying accepted post-tonemap deltas.

## Next

Move the same descriptor/process boundary from renderer-neutral anchors into a
candidate renderer-native implementation:

1. Map the S568 response anchors onto candidate Mitsuba XML light, caustic, or
   volume-control parameters.
2. Generate a candidate Mitsuba XML export from that response descriptor.
3. Render a short sample through the real Mitsuba XML command adapter.
4. Compare the renderer-native sample against the S564 post-tonemap backend
   proof, and only promote it if it improves visual realism without breaking the
   current full48 contract gates.
