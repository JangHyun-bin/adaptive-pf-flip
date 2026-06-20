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
- S569 consumed the S568 contract into an 8-frame Mitsuba XML sample export,
  inserting localized area emitters on the water mesh and validating the XML
  bundle.
- S570 rendered the S569 XML sample through the real Mitsuba backend command
  adapter at SPP4 and passed backend validation.
- S571 compared S515 raw, S555 accepted correction, and S570 native-light
  previews. The light-only path was technically valid but did not move the
  sample toward the accepted tone.
- S572 used the S567 low-frequency mask source as both channel and highlight
  evidence for material/tone XML modulation, producing a no-key dark-water
  8-frame sample export.
- S573 rendered the S572 sample at SPP4 and passed backend validation.
- S574 compared S515 raw, S555 accepted correction, S570 native-light, and S573
  material/tone previews. The S567-driven material/tone path moved farther away
  from the accepted correction, so local light/material consumers are not enough
  for this T4 field.

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
- Native light-response sample export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_low_frequency_light_response_sample_export_s569.md`
- Native light-response sample validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_low_frequency_light_response_sample_validate_s569.md`
- Native light-response sample render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_low_frequency_light_response_sample_spp4_s570.md`
- Native light-response sample render validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_low_frequency_light_response_sample_spp4_validation_s570.md`
- Native light-response compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_light_response_vs_accepted_compare_s571.md`
- Native light-response visual triage:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_light_response_visual_triage_s571.md`
- LFMask material/tone sample export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water_export_s572.md`
- LFMask material/tone sample validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water_validate_s572.md`
- LFMask material/tone sample render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water_spp4_s573.md`
- LFMask material/tone sample render validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water_spp4_validation_s573.md`
- LFMask material/tone compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_lfmask_material_tone_compare_s574.md`
- LFMask material/tone visual triage:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_lfmask_material_tone_visual_triage_s574.md`

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
- S569 native-light XML sample:
  - `status=ready`
  - frames exported: `8`
  - lights inserted: `64`
  - localized anchors: `64`
  - XML validation failures: `0`
- S570 native-light render:
  - `status=ready`
  - frames rendered: `8/8`
  - process failures: `0`
  - validation: `66/66` checks passed
- S571 visual comparison:
  - `status=ready`
  - candidates: `3`
  - selected frames: `8`
  - missing frame references: `0`
  - mean raw-vs-accepted MAD: `1.878133`
  - mean native-light-vs-accepted MAD: `1.915123`
- S572/S573 LFMask material/tone sample:
  - XML export: `ready`
  - XML validation failures: `0`
  - render: `ready`
  - frames rendered: `8/8`
  - process failures: `0`
  - backend validation: `66/66` checks passed
- S574 material/tone comparison:
  - `status=ready`
  - candidates: `4`
  - selected frames: `8`
  - mean raw-vs-accepted MAD: `1.878133`
  - mean native-light-vs-accepted MAD: `1.915123`
  - mean LFMask-material-vs-accepted MAD: `2.395302`

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
light-response contract formats, and two real renderer-native/local XML samples
have been rendered. These samples prove the contract and material/tone paths are
executable, but neither local light anchors nor direct material/tone modulation
reproduce the accepted S555 tone.

## Next

Move the same descriptor/process boundary toward an explicit low-frequency
texture/cache input instead of another local light/material tweak:

1. Package the S555/S564 low-frequency field as explicit per-frame renderer
   texture/cache data.
2. Keep the current post-tonemap backend as the accepted full48 proof until a
   real renderer-side texture consumer exists.
3. Shift new photoreal work toward real geometry, surface detail, secondary
   particles, and export/cache formats rather than local XML anchor tweaks.
4. Promote a native renderer sample only if it reduces the accepted-reference
   gap before attempting full48.
