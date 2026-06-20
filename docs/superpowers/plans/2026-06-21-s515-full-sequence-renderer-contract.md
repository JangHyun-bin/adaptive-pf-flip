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
- S575 bridged the S555 full48 runtime sequence adapter into the existing
  `lsfs_mitsuba_low_frequency_parity` schema.
- S576 built a full48 renderer texture/cache package from S575, writing 12
  texture layers per frame with zero reconstruction error.
- S577 consumed the S576 package and reconstructed the accepted full48 frames
  with max expected diff `0`.
- S578 mapped the current large-grid converted scene cache, water meshes,
  camera metadata, phase cells, particles, secondary channel counts, and S576
  low-frequency textures into a renderer scene-cache handoff manifest.
- S579 validated the S578 handoff across all mapped scene, texture, water mesh,
  and consumer composite references.
- S580 exported the S578 handoff into an `lsfs_render_data_summary` sidecar so
  renderer depth/material controls can consume water bounds, phase volume,
  mesh complexity, secondary counts, and visual-contract frame links without
  re-reading raw cache JSONL.
- S581 consumed the S580 sidecar into CSV/SVG profile diagnostics and verified
  monotonic source/output frame mappings plus depth, mesh, and secondary trend
  coverage.
- S582 used S580/S581 controls to apply a bounded scene-depth material preview
  over the accepted S577 composite frames, producing a GIF and per-frame
  original/mask/preview/diff strips without exceeding the configured image-diff
  tolerance.
- S583 triaged S582 against S577 and kept S577 as the accepted visual gate
  while preserving S582 as a safe metadata-driven depth/material control proof.
- S584 swept bounded depth/material strengths over the S578/S580 contract and
  selected `strength_1_0` as the strongest feasible image-space target for a
  native renderer-side implementation.
- S585 packaged the selected S584 `strength_1_0` candidate as a native
  renderer-side depth/material target manifest with per-frame controls,
  expected image deltas, source composite links, magnitude masks, target
  previews, strips, and a review gallery.
- S586 consumed the S585 target through a renderer-stage process adapter and
  reproduced all 48 selected target previews with zero image diff, proving the
  selected control contract is executable outside the sweep/preview generator.
- S587 compared the S586 native-stage output against both the S585 target and
  the current S577 accepted composite gate, confirming exact native-target
  parity while bounding the accepted-gate movement.
- S588 published the S587 native-stage compare gallery through a Cloudflare
  quick tunnel for external visual review.

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
- Low-frequency parity bridge:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_low_frequency_parity_from_sequence_s575.md`
- Low-frequency texture/cache package:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_low_frequency_texture_package_s576.md`
- Low-frequency texture/cache consumer:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_low_frequency_texture_consumer_s577.md`
- Renderer scene-cache handoff:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_cache_handoff_s578.md`
- Renderer scene-cache handoff validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_cache_handoff_validation_s579.md`
- Renderer scene render-data sidecar:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_render_data_s580.md`
- Renderer scene render-data profile:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_render_data_profile_s581.md`
- Renderer scene depth/material preview:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_preview_s582.md`
- Renderer scene depth/material preview triage:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_preview_triage_s583.md`
- Renderer scene depth/material sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_sweep_s584.md`
- Renderer scene depth/material target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_target_s585.md`
- Renderer scene depth/material native-stage proof:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_native_stage_s586.md`
- Renderer scene depth/material native-stage compare gate:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_native_stage_compare_s587.md`
- Public S587 native-stage compare review:
  `https://basics-classes-searched-mortgages.trycloudflare.com`
- Renderer scene depth/material native-stage compare publish:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_native_stage_compare_publish_s588.md`

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
- S575 low-frequency parity bridge:
  - `status=ready`
  - frames: `48`
  - missing references: `0`
  - dimension mismatches: `0`
  - max target abs diff: `43`
- S576 low-frequency texture/cache package:
  - `status=ready`
  - frames: `48`
  - textures per frame: `12`
  - texture bytes: `73.92 MB`
  - max reconstruction abs diff: `0`
- S577 low-frequency texture/cache consumer:
  - `status=ready`
  - frames: `48`
  - max expected abs diff: `0`
  - max expected mean diff: `0.0`
- S578 renderer scene-cache handoff:
  - `status=ready`
  - scene frames: `36`
  - visual frames: `48`
  - handoff frames: `48`
  - unique scene frames mapped: `36`
  - mapping mode: `nearest_normalized_scene_frame`
  - missing references: `0`
  - camera assets: `36`
  - particle assets: `36`
  - phase-cell assets: `36`
  - water mesh assets: `36`
  - texture bytes: `73.92 MB`
  - max texture reconstruction abs diff: `0`
  - max visual expected abs diff: `0`
- S579 renderer scene-cache handoff validation:
  - `status=passed`
  - total checks: `579`
  - failed checks: `0`
  - frames: `48`
  - scene frames: `36`
  - visual frames: `48`
  - unique scene frames mapped: `36`
- S580 renderer scene render-data sidecar:
  - `status=ok`
  - scene/cache frames: `36`
  - visual frames: `48`
  - render-data frames: `48`
  - mapping mode: `nearest_normalized_scene_frame`
  - water Y-depth span: min `21.0`, mean `26.375`, max `31.0`
  - water Z-depth span: min `19.0`, mean `21.416666666666668`, max `25.0`
  - water mesh face count: min `23424`, mean `27165.75`, max `29664`
  - secondary total count: `192` across mapped frames
- S581 renderer scene render-data profile:
  - `status=ok`
  - frames: `48`
  - row count, water depth spans, mesh faces, secondary counts, source mapping,
    and output mapping checks all passed
  - SVG profile:
    `build/shots/s581_mitsuba_renderer_scene_render_data_profile/render_data_profile.svg`
- S582 renderer scene depth/material preview:
  - `status=ready`
  - frames: `48`
  - missing references: `0`
  - max absolute delta: `3`
  - max mean absolute delta: `0.2585140174897119`
  - max changed coverage: `0.2705073302469136`
  - GIF:
    `build/shots/s582_mitsuba_renderer_scene_depth_material_preview/depth_material_preview.gif`
  - representative strip:
    `build/shots/s582_mitsuba_renderer_scene_depth_material_preview/strips/frame_0024_depth_material_preview.png`
- S583 renderer scene depth/material preview triage:
  - `status=recorded`
  - decision: keep S577 as accepted full48 visual gate
  - use S582 as a safe metadata-driven depth/material control proof
  - next: run a bounded strength/material sweep before promotion
- S584 renderer scene depth/material sweep:
  - `status=ready`
  - candidates: `4`
  - feasible candidates: `4`
  - selected candidate: `strength_1_0`
  - selected max absolute delta: `5`
  - selected max mean absolute delta: `0.4139242541152263`
  - selected max changed coverage: `0.3287885802469136`
  - selected GIF:
    `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_1_0/depth_material_sweep.gif`
  - representative strip:
    `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/gallery/assets/strength_1_0_strip_02.png`
- S585 renderer scene depth/material target:
  - `status=ready`
  - selected target: `strength_1_0`
  - frames: `48`
  - missing references: `0`
  - ready target previews: `48`
  - selected max absolute delta: `5`
  - selected max mean absolute delta: `0.4139242541152263`
  - selected max changed coverage: `0.3287885802469136`
  - target gallery:
    `build/shots/s585_mitsuba_renderer_scene_depth_material_target/gallery/index.html`
  - target GIF:
    `build/shots/s585_mitsuba_renderer_scene_depth_material_target/gallery/assets/selected_depth_material_target.gif`
- S586 renderer scene depth/material native stage:
  - `status=passed`
  - frames: `48`
  - passed frames: `48`
  - failed frames: `0`
  - missing references: `0`
  - max absolute diff vs S585 target: `0`
  - max mean diff vs S585 target: `0.0`
  - max native delta from source: `5`
  - native-stage GIF:
    `build/shots/s586_mitsuba_renderer_scene_depth_material_native_stage/gallery/assets/native_stage.gif`
  - native-stage gallery:
    `build/shots/s586_mitsuba_renderer_scene_depth_material_native_stage/gallery/index.html`
- S587 renderer scene depth/material native-stage compare:
  - `status=ready`
  - decision: `backend_sample_ready`
  - frames: `48`
  - missing references: `0`
  - max native-vs-target abs diff: `0`
  - max native-vs-target mean diff: `0.0`
  - max native-vs-accepted abs diff: `5`
  - max native-vs-accepted mean diff: `0.4139242541152263`
  - compare gallery:
    `build/shots/s587_mitsuba_renderer_scene_depth_material_native_stage_compare/gallery/index.html`
- S588 public native-stage compare review:
  - public URL:
    `https://basics-classes-searched-mortgages.trycloudflare.com`
  - `GET /index.html`: `200`
  - `HEAD /assets/native_compare_strips.gif`: `200`
  - GIF bytes: `30560993`

## Current Meaning

The current full48 visual result is no longer just a generated artifact. It is
now reproducible through:

1. a per-frame texture binding contract,
2. a renderer job manifest,
3. backend scene descriptors,
4. a process-level execution interface,
5. zero-diff validation against accepted references,
6. a renderer scene-cache handoff that links the accepted full48 visual
   texture contract to real camera, phase-field, water mesh, primary particle,
   and secondary particle data,
7. a renderer-data sidecar/profile that turns the handoff into reusable
   depth/material control metrics,
8. a bounded depth/material visual preview that proves those controls can drive
   an inspectable image-space renderer probe without broad exposure drift,
9. a bounded strength sweep that selects a more readable but still safe
   renderer-side depth/material target,
10. a selected target manifest that translates the chosen sweep result into
   per-frame renderer controls and concrete preview references for native
   implementation,
11. a process-level renderer-stage adapter that consumes the selected target
   contract and reproduces its full48 references with zero image diff,
12. a promotion gate showing exact S586/S585 parity and the bounded delta
   against the current S577 accepted visual gate,
13. a public visual review URL for the S587 compare gallery.

This gives the next renderer step a stable boundary. The first non-stub backend
is now in place and still produces the same accepted full48 visual output. The
low-frequency correction evidence has also been lifted into response-mask and
light-response contract formats, and two real renderer-native/local XML samples
have been rendered. These samples prove the contract and material/tone paths are
executable, but neither local light anchors nor direct material/tone modulation
reproduce the accepted S555 tone. The accepted T4 field is now packaged as a
full48 texture/cache boundary with lossless reconstruction and has a validated
handoff into the current large-grid scene-data cache. The handoff now also has
an `lsfs_render_data_summary` sidecar and trend profile, so the next pass can
drive renderer-side depth/material behavior from measured scene metadata rather
than by hand-tuning only the final image. S582 shows that this metadata can
produce a bounded visual probe. S583 keeps S577 as the accepted look, and S584
selects `strength_1_0` as a stronger but still bounded target. S585 packages
that target as the current implementation contract for the next native
renderer-side depth/material pass. S586 proves the contract can now be consumed
through an independent renderer-stage process boundary with exact parity
against the selected target previews. S587 records the promotion gate for the
next backend sample: native-target parity is exact, and the accepted-gate move
is bounded to max abs diff `5` and max mean diff `0.4139242541152263`. S588
publishes that gate for direct visual inspection.

## Next

Use the texture/cache boundary as the accepted visual handoff while moving the
photoreal renderer work back toward real scene data:

1. Keep S577 as the current accepted full48 texture/cache import gate.
2. Use S578/S579 as the renderer-side scene-data input contract.
3. Use S580/S581 as the reusable depth/material control sidecar and profile.
4. Replace the S586 process-proof stage with a real renderer material or
   tonemap backend sample while preserving the same S585 control contract.
5. Use S587 as the promotion gate for that backend sample, then promote only if
   it preserves S585 target parity and improves or justifies the S577 accepted
   gate movement before attempting full48.
