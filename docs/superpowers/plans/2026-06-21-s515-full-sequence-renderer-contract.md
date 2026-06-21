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
- S589 replaced the proof-only native stage with an external tonemap backend
  executable sample. The runner selected 8 representative S585 target frames,
  emitted backend scene descriptors, launched the backend script as a
  subprocess per frame, and reproduced the selected target frames with zero
  image diff.
- S590 moved the backend executable sample one step closer to the real renderer
  path by deriving source composites, magnitude masks, and depth/material
  controls directly from the S578 scene-cache handoff plus S580 render-data
  sidecar, using S585 only as the validation target.
- S591 extended the S590 scene-cache direct backend path from representative
  frames to full48 execution, preserving zero-diff parity against the S585
  target across all 48 frames.
- S592 re-ran the promotion gate on the S591 full48 backend output, confirming
  exact backend-target parity and the same bounded movement against the S577
  accepted visual gate.
- S593 published the S592 full48 backend-output promotion gate through a
  Cloudflare quick tunnel for direct external visual review.
- S594 converted the S591/S592 full48 scene-cache backend gate into a
  renderer-native material package with 48 frame-local Mitsuba roughdielectric
  snippets, localized mask texture bindings, material-parameter ranges, visual
  intent strips, and a gallery.
- S595 bound the S594 material package into an 8-frame Mitsuba XML sample by
  inserting frame-local scene-depth material snippets and redirecting the water
  surface BSDF references. The resulting XML export validated cleanly.
- S596 rendered that 8-frame native-material XML sample through Mitsuba at SPP4
  using the validated Python 3.11 + VS18 LLVM runtime, packaged a review
  gallery, and compared the result against the S573, S577, S585, and legacy
  S328 visual references.
- S597 fixed RGBA-alpha mask handling in the localized water-material split
  path, exported and rendered an 8-frame `MS1` face-split native-material
  sample, and compared it against S573/S577/S585/S596. The path is renderable
  but still too broad for promotion.
- S598 tightened the localized split path to high-confidence mask faces
  (`mask_threshold=128`, `face_limit=3000`) and rendered an 8-frame `MS2`
  sample. Legacy S328 target gap increased, but direct S577/S585 MAD dropped
  sharply, making S598 the current native-material tuning baseline.
- S599 reduced the split to a subtler `MS3` setting (`face_limit=2500` with
  weaker/rougher response bins), rendered and compared the same 8-frame sample,
  and slightly improved direct S577/S585 MAD over S598. This makes S599 the
  current native-material split tuning baseline.
- S600 regenerated the S572-style material/tone base on all 48 S322 frames,
  applied the S599 `MS3` localized split across the full sequence, validated all
  48 XML scenes, rendered all 48 frames through Mitsuba SPP4, and compared the
  result against S577/S585. This proves the S599 setting is full48-stable, but
  the late-frame water highlight remains a little stronger than the accepted
  targets.
- S601 reduced the selected response region and roughened/dimmed the localized
  split material into an `MS4` quiet full48 candidate. It preserves 48/48 render
  stability and improves full48 S577/S585 mean MAD over S600, with the known
  trade off that S577 max absolute diff rises by one pixel level.
- S602 tightened that quiet response again into a guarded `MS5` full48
  candidate. It reduces response faces to 67,200, preserves 48/48 render
  stability, improves full48 mean MAD and max-absolute error over S601, and
  becomes the current full48 native-material split baseline despite a small
  max-MAD increase.
- S603 tested a detail-recovery neighbor by increasing the selected response
  region to 76,800 faces. It preserved max absolute error and improved max MAD
  slightly, but worsened mean MAD and is not promoted.
- S604 tested a softer guarded neighbor with 57,600 response faces. It improves
  full48 mean MAD and max MAD against S577/S585 versus S602, while keeping
  S577 max absolute error below the earlier S601 outlier. S604 becomes the
  current full48 native-material split baseline, with peak error still tracked
  against S602.
- S605 tested a peak-balanced middle point between S602 and S604 with 62,400
  response faces. It regressed mean MAD and max MAD versus S604 and returned
  S577 max absolute error to `179`, so it is rejected.
- S606 published the S604 full48 comparison gallery locally for visual review.
  The gallery passed HTTP `200` checks for `index.html` and `assets/shot.gif`.
  Two Cloudflare quick-tunnel attempts failed during URL issuance with
  `trycloudflare.com` HTTP `500` / error code `1101`, so no public URL was
  issued in this milestone.
- S607 added frame-aware coverage attenuation to the localized water-material
  split path and rendered an `MS9` full48 candidate. It preserves 48/48 render
  stability, attenuates only 11 high-coverage frames, improves S604's full48
  mean MAD and max MAD against both S577 and S585, and becomes the current
  native-material split baseline. The remaining max-absolute outlier is still
  frame 14, which is below the coverage attenuation pivot and should be handled
  by a separate peak cleanup pass.
- S608/S609/S610 added and swept low-coverage highlight rescue. S608 proves the
  rescue can remove the frame-14 peak but is too strong and regresses mean MAD;
  S610 is too weak and leaves the peak unchanged. S609 is promoted: it keeps
  S607's max MAD unchanged, improves max abs from `176/175` to `175/174`, and
  keeps the mean-MAD movement small while remaining better than S604.
- S611/S612 added narrow coverage-band rescue for the frame-34/35 plateau.
  S611 lowers that plateau but leaves the global frame-14 peak. S612 combines
  the band rescue with a stronger bounded low-coverage rescue, keeps max MAD
  unchanged, improves global max abs to `173/172`, and becomes the current
  native-material split baseline.
- S613 tested a hand-bounded screen-region attenuation for late frames. It
  slightly improved mean direct S577/S585 MAD over S612/S614, but the box was
  manual and therefore not promoted as the durable control.
- S614 replaced that manual box with signed screen-error face attenuation
  driven by the S613-to-S585 gap summary. It preserved full48 render stability
  and lowered late-frame max-MAD with an automatic local-control path.
- S615 tried material-only attenuation of the signed-error-selected response
  faces. It preserved response faces but regressed mean/max MAD, so it is
  rejected as a direct material-scale direction.
- S616 split S614 into a full/base response delta buffer. A base-only render
  removed 96 response shapes and 55,526 response faces, reconstructed the full
  render with max diff `0`, and found response scale `0.75` as the best S585
  compositing probe (`mean MAD=2.982389550647291`,
  `max MAD=5.524723508230453`).
- S617 promoted that `0.75` response scale into a reusable
  `lsfs_mitsuba_secondary_composite` manifest with gallery assets and direct
  S577/S585 gate reports. It improves the S614 automatic baseline against both
  gates (`S577 mean/max MAD=2.9732022274734224/5.5108699845679014`,
  `S585 mean/max MAD=2.982389550647291/5.524723508230453`) and becomes the
  current AOV/export integration target.
- S618 packaged the S617 target as a signed response-AOV contract:
  `base_rgb + response_positive_rgb - response_negative_rgb =
  selected_composite_rgb`. It preserves 48-frame reconstruction with max diff
  `0`, carries the S577/S585 gate metrics forward, and is now the portable
  handoff format for the next renderer/cache consumer.
- S619 consumed the S618 signed response-AOV contract back into a standard
  `lsfs_mitsuba_secondary_composite` summary. The import is exact
  (`max diff=0`, `mean diff=0.0`) and preserves the S617/S618 S577/S585 gate
  metrics, proving the response-AOV boundary can be exported and consumed
  without visual drift.
- S620 joined the S578/S580 renderer scene-cache handoff with the S618/S619
  signed response-AOV export/import boundary into a single scene/AOV handoff.
  The manifest keeps all 48 output frames ready, preserves exact AOV import
  parity (`max diff=0`), and records the expected 48-output-to-36-scene-frame
  normalized mapping from S578.
- S621 consumed the S620 scene/AOV handoff into a renderer/cache job manifest.
  It writes 48 per-frame descriptors that bind scene assets, render-data
  controls, signed response AOV layers, selected composites, output targets,
  and S577/S585 gate metrics without recomputing response layers.
- S622 dry-ran the S621 descriptors as a renderer/cache execution smoke gate.
  It filled the descriptor output image, metadata, and validation targets for
  all 48 frames, reconstructing the selected composite from signed response AOV
  layers with zero diff against both the selected and imported references.
- S623 moved that descriptor execution behind an external backend process
  boundary. The runner launched 48 subprocesses through
  `mitsuba_response_aov_scene_backend.py`, preserved selected/imported parity,
  and produced a backend gallery with zero process failures.

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
- Renderer scene depth/material tonemap backend sample:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_tonemap_backend_sample_s589.md`
- Renderer scene depth/material scene-cache backend sample:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_scene_cache_backend_sample_s590.md`
- Renderer scene depth/material scene-cache backend full48:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_scene_cache_backend_full48_s591.md`
- Renderer scene depth/material backend output compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_backend_output_compare_s592.md`
- Public S592 backend output compare review:
  `https://outputs-murray-phil-beads.trycloudflare.com`
- Renderer scene depth/material backend output compare publish:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_backend_output_compare_publish_s593.md`
- Renderer scene depth/material native material package:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_renderer_scene_depth_material_native_material_package_s594.md`
- Renderer scene depth/material native material XML sample:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_xml_sample_s595.md`
- Renderer scene depth/material native material XML validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_xml_sample_validate_s595.md`
- Renderer scene depth/material native material XML SPP4 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_xml_sample_spp4_vs18_s596.md`
- Renderer scene depth/material native material XML SPP4 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_xml_sample_spp4_gallery_s596.md`
- Renderer scene depth/material native material XML target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_xml_sample_spp4_target_gap_s328_s596.md`
- Renderer scene depth/material native material XML sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_xml_sample_spp4_sequence_compare_s596.md`
- Renderer scene depth/material localized split material export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms1_soft_export_s597.md`
- Renderer scene depth/material localized split material validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms1_soft_validate_s597.md`
- Renderer scene depth/material localized split material render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms1_soft_render_s597.md`
- Renderer scene depth/material localized split material gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms1_soft_gallery_s597.md`
- Renderer scene depth/material localized split material target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms1_soft_target_gap_s328_s597.md`
- Renderer scene depth/material localized split material sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms1_soft_sequence_compare_s597.md`
- Renderer scene depth/material tight split material export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms2_tight_export_s598.md`
- Renderer scene depth/material tight split material validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms2_tight_validate_s598.md`
- Renderer scene depth/material tight split material render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms2_tight_render_s598.md`
- Renderer scene depth/material tight split material gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms2_tight_gallery_s598.md`
- Renderer scene depth/material tight split material target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms2_tight_target_gap_s328_s598.md`
- Renderer scene depth/material tight split material sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms2_tight_sequence_compare_s598.md`
- Renderer scene depth/material tight split direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms2_tight_direct_metrics_s598.md`
- Renderer scene depth/material subtle split material export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_export_s599.md`
- Renderer scene depth/material subtle split material validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_validate_s599.md`
- Renderer scene depth/material subtle split material render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_render_s599.md`
- Renderer scene depth/material subtle split material gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_gallery_s599.md`
- Renderer scene depth/material subtle split material target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_target_gap_s328_s599.md`
- Renderer scene depth/material subtle split material sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_sequence_compare_s599.md`
- Renderer scene depth/material subtle split direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_direct_metrics_s599.md`
- Renderer scene depth/material subtle split full48 base export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_full48_base_export_s600.md`
- Renderer scene depth/material subtle split full48 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_full48_export_s600.md`
- Renderer scene depth/material subtle split full48 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_full48_validate_s600.md`
- Renderer scene depth/material subtle split full48 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_full48_render_s600.md`
- Renderer scene depth/material subtle split full48 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_full48_gallery_s600.md`
- Renderer scene depth/material subtle split full48 target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_full48_target_gap_s328_s600.md`
- Renderer scene depth/material subtle split full48 sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_full48_sequence_compare_full48_s600.md`
- Renderer scene depth/material subtle split full48 direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms3_subtle_full48_direct_metrics_s600.md`
- Renderer scene depth/material quiet split full48 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms4_quiet_full48_export_s601.md`
- Renderer scene depth/material quiet split full48 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms4_quiet_full48_validate_s601.md`
- Renderer scene depth/material quiet split full48 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms4_quiet_full48_render_s601.md`
- Renderer scene depth/material quiet split full48 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms4_quiet_full48_gallery_s601.md`
- Renderer scene depth/material quiet split full48 target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms4_quiet_full48_target_gap_s328_s601.md`
- Renderer scene depth/material quiet split full48 sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms4_quiet_full48_sequence_compare_s601.md`
- Renderer scene depth/material quiet split full48 direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms4_quiet_full48_direct_metrics_s601.md`
- Renderer scene depth/material guarded split full48 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms5_guarded_full48_export_s602.md`
- Renderer scene depth/material guarded split full48 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms5_guarded_full48_validate_s602.md`
- Renderer scene depth/material guarded split full48 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms5_guarded_full48_render_s602.md`
- Renderer scene depth/material guarded split full48 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms5_guarded_full48_gallery_s602.md`
- Renderer scene depth/material guarded split full48 target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms5_guarded_full48_target_gap_s328_s602.md`
- Renderer scene depth/material guarded split full48 sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms5_guarded_full48_sequence_compare_s602.md`
- Renderer scene depth/material guarded split full48 direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms5_guarded_full48_direct_metrics_s602.md`
- Renderer scene depth/material detail-recovery split full48 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms6_detail_recovery_full48_export_s603.md`
- Renderer scene depth/material detail-recovery split full48 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms6_detail_recovery_full48_validate_s603.md`
- Renderer scene depth/material detail-recovery split full48 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms6_detail_recovery_full48_render_s603.md`
- Renderer scene depth/material detail-recovery split full48 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms6_detail_recovery_full48_gallery_s603.md`
- Renderer scene depth/material detail-recovery split full48 sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms6_detail_recovery_full48_sequence_compare_s603.md`
- Renderer scene depth/material soft-guard split full48 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms7_soft_guard_full48_export_s604.md`
- Renderer scene depth/material soft-guard split full48 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms7_soft_guard_full48_validate_s604.md`
- Renderer scene depth/material soft-guard split full48 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms7_soft_guard_full48_render_s604.md`
- Renderer scene depth/material soft-guard split full48 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms7_soft_guard_full48_gallery_s604.md`
- Renderer scene depth/material soft-guard split full48 target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms7_soft_guard_full48_target_gap_s328_s604.md`
- Renderer scene depth/material soft-guard split full48 sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms7_soft_guard_full48_sequence_compare_s604.md`
- Renderer scene depth/material soft-guard split full48 direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms7_soft_guard_full48_direct_metrics_s604.md`
- Renderer scene depth/material peak-balance split full48 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms8_peak_balance_full48_export_s605.md`
- Renderer scene depth/material peak-balance split full48 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms8_peak_balance_full48_validate_s605.md`
- Renderer scene depth/material peak-balance split full48 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms8_peak_balance_full48_render_s605.md`
- Renderer scene depth/material peak-balance split full48 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms8_peak_balance_full48_gallery_s605.md`
- Renderer scene depth/material peak-balance split full48 sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms8_peak_balance_full48_sequence_compare_s605.md`
- Renderer scene depth/material peak-balance split full48 direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms8_peak_balance_full48_direct_metrics_s605.md`
- Renderer scene depth/material soft-guard split full48 publish:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms7_soft_guard_full48_publish_s606.md`
- Renderer scene depth/material frame-peak-control split full48 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms9_frame_peak_control_full48_export_s607.md`
- Renderer scene depth/material frame-peak-control split full48 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms9_frame_peak_control_full48_validate_s607.md`
- Renderer scene depth/material frame-peak-control split full48 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms9_frame_peak_control_full48_render_s607.md`
- Renderer scene depth/material frame-peak-control split full48 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms9_frame_peak_control_full48_gallery_s607.md`
- Renderer scene depth/material frame-peak-control split full48 sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms9_frame_peak_control_full48_sequence_compare_s607.md`
- Renderer scene depth/material frame-peak-control split full48 direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms9_frame_peak_control_full48_direct_metrics_s607.md`
- Renderer scene depth/material gentle low-coverage rescue split full48 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms11_gentle_low_coverage_rescue_full48_export_s609.md`
- Renderer scene depth/material gentle low-coverage rescue split full48 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms11_gentle_low_coverage_rescue_full48_validate_s609.md`
- Renderer scene depth/material gentle low-coverage rescue split full48 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms11_gentle_low_coverage_rescue_full48_render_s609.md`
- Renderer scene depth/material gentle low-coverage rescue split full48 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms11_gentle_low_coverage_rescue_full48_gallery_s609.md`
- Renderer scene depth/material gentle low-coverage rescue split full48 sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms11_gentle_low_coverage_rescue_full48_sequence_compare_s609.md`
- Renderer scene depth/material gentle low-coverage rescue split full48 direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms11_gentle_low_coverage_rescue_full48_direct_metrics_s609.md`
- Renderer scene depth/material balanced dual-rescue split full48 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms14_balanced_dual_rescue_full48_export_s612.md`
- Renderer scene depth/material balanced dual-rescue split full48 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms14_balanced_dual_rescue_full48_validate_s612.md`
- Renderer scene depth/material balanced dual-rescue split full48 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms14_balanced_dual_rescue_full48_render_s612.md`
- Renderer scene depth/material balanced dual-rescue split full48 gallery:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms14_balanced_dual_rescue_full48_gallery_s612.md`
- Renderer scene depth/material balanced dual-rescue split full48 sequence compare:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms14_balanced_dual_rescue_full48_sequence_compare_s612.md`
- Renderer scene depth/material balanced dual-rescue split full48 direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms14_balanced_dual_rescue_full48_direct_metrics_s612.md`
- Renderer scene depth/material screen-region attenuation direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms15_screen_region_attenuation_full48_direct_metrics_s613.md`
- Renderer scene depth/material screen-error attenuation direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms16_screen_error_attenuation_full48_direct_metrics_s614.md`
- Renderer scene depth/material screen-error material attenuation direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_scene_depth_native_material_split_ms17_screen_error_material_attenuation_full48_direct_metrics_s615.md`
- Renderer scene depth/material response buffer base export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_delta_buffer_base_export_s616.md`
- Renderer scene depth/material response buffer base export validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_delta_buffer_base_export_validation_s616.md`
- Renderer scene depth/material response buffer base render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_delta_buffer_base_render_s616.md`
- Renderer scene depth/material response delta buffer:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_delta_buffer_s616.md`
- Renderer scene depth/material response scale composite:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_scale_composite_s075_s617.md`
- Renderer scene depth/material response scale S577 gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_scale_composite_s075_vs_s577_gap_s617.md`
- Renderer scene depth/material response scale S585 gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_scale_composite_s075_vs_s585_gap_s617.md`
- Renderer scene depth/material response scale direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_scale_composite_s075_direct_metrics_s617.md`
- Renderer scene depth/material signed response AOV contract:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_aov_contract_s075_s618.md`
- Renderer scene depth/material response AOV consumer:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_aov_consumer_s075_s619.md`
- Renderer scene depth/material response AOV consumer S577 gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_aov_consumer_s075_vs_s577_gap_s619.md`
- Renderer scene depth/material response AOV consumer S585 gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_aov_consumer_s075_vs_s585_gap_s619.md`
- Renderer scene depth/material response AOV consumer direct metrics:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_aov_consumer_s075_direct_metrics_s619.md`
- Renderer scene depth/material response AOV scene handoff:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_aov_scene_handoff_s075_s620.md`
- Renderer scene depth/material response AOV scene job manifest:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_aov_scene_job_manifest_s075_s621.md`
- Renderer scene depth/material response AOV scene job dry run:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_aov_scene_job_dry_run_s075_s622.md`
- Renderer scene depth/material response AOV scene backend adapter:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_response_aov_scene_backend_adapter_s075_s623.md`

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
- S589 renderer scene depth/material tonemap backend sample:
  - `status=passed`
  - frames: `8`
  - passed frames: `8`
  - failed frames: `0`
  - process failures: `0`
  - max abs diff vs S585 target: `0`
  - max mean diff vs S585 target: `0.0`
  - max backend delta from source: `5`
  - backend sample gallery:
    `build/shots/s589_mitsuba_renderer_scene_depth_material_tonemap_backend_sample/gallery/index.html`
  - backend sample GIF:
    `build/shots/s589_mitsuba_renderer_scene_depth_material_tonemap_backend_sample/gallery/assets/tonemap_backend_sample.gif`
- S590 renderer scene depth/material scene-cache backend sample:
  - `status=passed`
  - frames: `8`
  - passed frames: `8`
  - failed frames: `0`
  - process failures: `0`
  - input missing references: `0`
  - max abs diff vs S585 target: `0`
  - max mean diff vs S585 target: `0.0`
  - max backend delta from source: `5`
  - scene-cache backend sample gallery:
    `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/gallery/index.html`
  - scene-cache backend sample GIF:
    `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/gallery/assets/scene_cache_backend_sample.gif`
- S591 renderer scene depth/material scene-cache backend full48:
  - `status=passed`
  - frames: `48`
  - passed frames: `48`
  - failed frames: `0`
  - process failures: `0`
  - input missing references: `0`
  - max abs diff vs S585 target: `0`
  - max mean diff vs S585 target: `0.0`
  - max backend delta from source: `5`
  - full48 scene-cache backend gallery:
    `build/shots/s591_mitsuba_renderer_scene_depth_material_scene_cache_backend_full48/gallery/index.html`
  - full48 scene-cache backend GIF:
    `build/shots/s591_mitsuba_renderer_scene_depth_material_scene_cache_backend_full48/gallery/assets/scene_cache_backend_sample.gif`
- S592 renderer scene depth/material backend output compare:
  - `status=ready`
  - decision: `renderer_native_material_ready`
  - frames: `48`
  - missing references: `0`
  - max backend-vs-target abs diff: `0`
  - max backend-vs-target mean diff: `0.0`
  - max backend-vs-accepted abs diff: `5`
  - max backend-vs-accepted mean diff: `0.4139242541152263`
  - compare gallery:
    `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/gallery/index.html`
  - compare GIF:
    `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/gallery/assets/backend_compare_strips.gif`
- S593 public backend output compare review:
  - public URL:
    `https://outputs-murray-phil-beads.trycloudflare.com`
  - `GET /index.html`: `200`
  - `HEAD /assets/backend_compare_strips.gif`: `200`
  - GIF bytes: `30572999`
- S594 renderer scene depth/material native material package:
  - `status=ready`
  - frames: `48`
  - missing references: `0`
  - material snippets: `48`
  - texture bindings: `48`
  - max backend-vs-target abs diff: `0`
  - max backend-vs-target mean diff: `0.0`
  - max backend-vs-accepted abs diff: `5`
  - max backend-vs-accepted mean diff: `0.4139242541152263`
  - alpha range: `0.008699999999999998` .. `0.011999999999999999`
  - mask weight range: `0.625` .. `0.74875`
  - material package gallery:
    `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/gallery/index.html`
  - material intent GIF:
    `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/gallery/assets/native_material_intent.gif`
- S595 renderer scene depth/material native material XML sample:
  - export `status=ready`
  - frames exported: `8`
  - missing references: `0`
  - snippet insertions: `8`
  - water ref replacements: `8`
  - XML validation `status=ready`
  - XML parsed: `8`
  - validation failures: `0`
  - validation warnings: `0`
  - sample export:
    `build/shots/s595_mitsuba_scene_depth_native_material_xml_sample/mitsuba_export.json`
- S596 renderer scene depth/material native material XML SPP4 render:
  - render `status=ready`
  - frames rendered: `8`
  - failures: `0`
  - total elapsed ms: `2156`
  - image bytes: `24.60 MB`
  - preview bytes: `3.29 MB`
  - runtime:
    `C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\Llvm\x64\bin\LLVM-C.dll`
  - gallery:
    `build/shots/s596_mitsuba_scene_depth_native_material_xml_sample_spp4/gallery/index.html`
  - review GIF:
    `build/shots/s596_mitsuba_scene_depth_native_material_xml_sample_spp4/gallery/assets/shot.gif`
  - S328 target gap `status=ready`
  - S328 target gap max mean abs diff: `82.66423161008231`
  - S328 target gap max abs diff: `245`
  - S573/S577/S585 sequence compare `status=ready`
  - sequence compare candidates: `4`
  - sequence compare frames: `8`
  - sequence compare missing references: `0`
- S597 renderer scene depth/material localized split material MS1:
  - export `status=ready`
  - frames exported: `8`
  - response faces: `103565`
  - remainder faces: `53199`
  - water shape replacements: `8`
  - response BSDF insertions: `8`
  - XML validation `status=ready`
  - XML parsed: `8`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `8`
  - render failures: `0`
  - total elapsed ms: `1700`
  - image bytes: `24.86 MB`
  - preview bytes: `3.56 MB`
  - S328 target gap `status=ready`
  - S328 target gap max mean abs diff: `88.33843942901234`
  - S328 target gap max abs diff: `243`
  - S573/S577/S585/S596 sequence compare `status=ready`
  - sequence compare candidates: `5`
  - sequence compare frames: `8`
  - sequence compare missing references: `0`
- S598 renderer scene depth/material localized split material MS2:
  - export `status=ready`
  - frames exported: `8`
  - response faces: `24000`
  - remainder faces: `132764`
  - water shape replacements: `8`
  - response BSDF insertions: `8`
  - XML validation `status=ready`
  - XML parsed: `8`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `8`
  - render failures: `0`
  - total elapsed ms: `1667`
  - image bytes: `23.24 MB`
  - preview bytes: `2.91 MB`
  - S328 target gap `status=ready`
  - S328 target gap max mean abs diff: `100.68966885288066`
  - S328 target gap max abs diff: `219`
  - S573/S577/S585/S596/S597 sequence compare `status=ready`
  - sequence compare candidates: `6`
  - sequence compare frames: `8`
  - sequence compare missing references: `0`
  - direct S577 mean MAD: `3.87780647183642`
  - direct S585 mean MAD: `3.875843139146091`
- S599 renderer scene depth/material localized split material MS3:
  - export `status=ready`
  - frames exported: `8`
  - response faces: `20000`
  - remainder faces: `136764`
  - water shape replacements: `8`
  - response BSDF insertions: `8`
  - XML validation `status=ready`
  - XML parsed: `8`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `8`
  - render failures: `0`
  - total elapsed ms: `1740`
  - image bytes: `23.19 MB`
  - preview bytes: `2.88 MB`
  - S328 target gap `status=ready`
  - S328 target gap max mean abs diff: `100.98423739711934`
  - S328 target gap max abs diff: `226`
  - S573/S577/S585/S596/S597/S598 sequence compare `status=ready`
  - sequence compare candidates: `7`
  - sequence compare frames: `8`
  - sequence compare missing references: `0`
  - direct S577 mean MAD: `3.833308577674897`
  - direct S585 mean MAD: `3.8382736143261313`
- S600 renderer scene depth/material localized split material MS3 full48:
  - base export `status=ready`
  - base frames exported: `48`
  - split export `status=ready`
  - split frames exported: `48`
  - response faces: `120000`
  - remainder faces: `806364`
  - water shape replacements: `48`
  - response BSDF insertions: `48`
  - XML validation `status=ready`
  - XML parsed: `48`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `48`
  - render failures: `0`
  - total elapsed ms: `10307`
  - image bytes: `137.83 MB`
  - preview bytes: `17.13 MB`
  - S328 target gap `status=ready`
  - S328 target gap max mean abs diff: `100.98423739711934`
  - S328 target gap max abs diff: `226`
  - S577/S585/S600 full48 sequence compare `status=ready`
  - sequence compare common frames: `48`
  - sequence compare selected frames: `13`
  - sequence compare missing references: `0`
  - direct S577 mean MAD: `3.9167686096107683`
  - direct S585 mean MAD: `3.921020661865569`
- S601 renderer scene depth/material localized split material MS4 quiet full48:
  - export `status=ready`
  - frames exported: `48`
  - response faces: `86400`
  - remainder faces: `839964`
  - water shape replacements: `48`
  - response BSDF insertions: `48`
  - XML validation `status=ready`
  - XML parsed: `48`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `48`
  - render failures: `0`
  - total elapsed ms: `10318`
  - image bytes: `136.16 MB`
  - preview bytes: `16.51 MB`
  - S328 target gap `status=ready`
  - S328 target gap max mean abs diff: `101.8383661265432`
  - S328 target gap max abs diff: `217`
  - S577/S585/S600/S601 full48 sequence compare `status=ready`
  - sequence compare common frames: `48`
  - sequence compare selected frames: `13`
  - sequence compare missing references: `0`
  - direct S577 mean MAD: `3.5123040578918037`
  - direct S577 max abs: `179`
  - direct S585 mean MAD: `3.520047702867798`
  - direct S585 max abs: `175`
- S602 renderer scene depth/material localized split material MS5 guarded full48:
  - export `status=ready`
  - frames exported: `48`
  - response faces: `67200`
  - remainder faces: `859164`
  - water shape replacements: `48`
  - response BSDF insertions: `48`
  - XML validation `status=ready`
  - XML parsed: `48`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `48`
  - render failures: `0`
  - total elapsed ms: `10460`
  - image bytes: `135.00 MB`
  - preview bytes: `16.04 MB`
  - S328 target gap `status=ready`
  - S328 target gap max mean abs diff: `102.57438400205761`
  - S328 target gap max abs diff: `210`
  - S577/S585/S601/S602 full48 sequence compare `status=ready`
  - sequence compare common frames: `48`
  - sequence compare selected frames: `13`
  - sequence compare missing references: `0`
  - direct S577 mean MAD: `3.205035231267147`
  - direct S577 max MAD: `5.944519032921811`
  - direct S577 max abs: `171`
  - direct S585 mean MAD: `3.2147581232853226`
  - direct S585 max MAD: `5.954301054526749`
  - direct S585 max abs: `167`
- S603 renderer scene depth/material localized split material MS6 detail recovery full48:
  - export `status=ready`
  - frames exported: `48`
  - response faces: `76800`
  - remainder faces: `849564`
  - XML validation `status=ready`
  - XML parsed: `48`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `48`
  - render failures: `0`
  - total elapsed ms: `10007`
  - image bytes: `135.58 MB`
  - preview bytes: `16.28 MB`
  - S577/S585/S602/S603 full48 sequence compare `status=ready`
  - sequence compare common frames: `48`
  - sequence compare selected frames: `13`
  - sequence compare missing references: `0`
  - direct S577 mean MAD: `3.365041460369513`
  - direct S577 max MAD: `5.936041023662551`
  - direct S577 max abs: `171`
  - direct S585 mean MAD: `3.374113069594479`
  - direct S585 max MAD: `5.94494212962963`
  - direct S585 max abs: `167`
  - decision: `not promoted; mean MAD regressed versus S602`
- S604 renderer scene depth/material localized split material MS7 soft guard full48:
  - export `status=ready`
  - frames exported: `48`
  - response faces: `57600`
  - remainder faces: `868764`
  - XML validation `status=ready`
  - XML parsed: `48`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `48`
  - render failures: `0`
  - total elapsed ms: `10452`
  - image bytes: `134.47 MB`
  - preview bytes: `15.79 MB`
  - S328 target gap `status=ready`
  - S328 target gap max mean abs diff: `102.81458140432099`
  - S328 target gap max abs diff: `216`
  - S577/S585/S602/S603/S604 full48 sequence compare `status=ready`
  - sequence compare common frames: `48`
  - sequence compare selected frames: `13`
  - sequence compare missing references: `0`
  - direct S577 mean MAD: `3.0665762442129627`
  - direct S577 max MAD: `5.926882716049382`
  - direct S577 max abs: `176`
  - direct S585 mean MAD: `3.0774464431155693`
  - direct S585 max MAD: `5.939676568930041`
  - direct S585 max abs: `175`
- S605 renderer scene depth/material localized split material MS8 peak balance full48:
  - export `status=ready`
  - frames exported: `48`
  - response faces: `62400`
  - remainder faces: `863964`
  - XML validation `status=ready`
  - XML parsed: `48`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `48`
  - render failures: `0`
  - total elapsed ms: `9936`
  - image bytes: `134.74 MB`
  - preview bytes: `15.92 MB`
  - S577/S585/S602/S604/S605 full48 sequence compare `status=ready`
  - sequence compare common frames: `48`
  - sequence compare selected frames: `13`
  - sequence compare missing references: `0`
  - direct S577 mean MAD: `3.139332534936557`
  - direct S577 max MAD: `5.992344393004116`
  - direct S577 max abs: `179`
  - direct S585 mean MAD: `3.149561873070988`
  - direct S585 max MAD: `6.003236239711934`
  - direct S585 max abs: `175`
  - decision: `not promoted; S604 remains baseline`
- S606 S604 full48 comparison gallery publish:
  - gallery: `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/sequence_compare_s577_s585_s602_s603/gallery/index.html`
  - local URL: `http://127.0.0.1:8991`
  - local `index.html` check: `200`
  - local `assets/shot.gif` check: `200`
  - GIF bytes: `13701804`
  - HTTP server PID: `44732`
  - public URL: `n/a`
  - cftunnel attempts: `2`
  - cftunnel result: `trycloudflare.com HTTP 500 / error code 1101`
- S607 renderer scene depth/material localized split material MS9 frame peak control full48:
  - export `status=ready`
  - frames exported: `48`
  - response faces: `55768`
  - remainder faces: `870596`
  - coverage-control attenuated frames: `11`
  - coverage-control max attenuation: `0.2302478780864198`
  - XML validation `status=ready`
  - XML parsed: `48`
  - validation failures: `0`
  - validation warnings: `0`
  - render `status=ready`
  - frames rendered: `48`
  - render failures: `0`
  - total elapsed ms: `10305`
  - image bytes: `134.38 MB`
  - preview bytes: `15.73 MB`
  - S577/S585/S602/S604/S605/S607 full48 sequence compare `status=ready`
  - sequence compare common frames: `48`
  - sequence compare selected frames: `17`
  - sequence compare missing references: `0`
  - direct S577 mean MAD: `3.0432079609267837`
  - direct S577 max MAD: `5.651857638888889`
  - direct S577 max abs: `176`
  - direct S585 mean MAD: `3.054593420460391`
  - direct S585 max MAD: `5.6697800925925925`
  - direct S585 max abs: `175`
  - decision: `promoted over S604 for mean/max-MAD; frame-14 max abs remains for S608`
- S608/S609/S610 low-coverage rescue sweep:
  - S608 render `status=ready`, frames rendered `48`, failures `0`
  - S608 response faces: `56828`
  - S608 max rescue: `1.0`
  - S608 direct S577 mean/max/maxabs: `3.0633944723079565` / `5.651857638888889` / `175`
  - S608 direct S585 mean/max/maxabs: `3.074621967163923` / `5.6697800925925925` / `174`
  - S608 decision: `not promoted; rescue is too strong and mean MAD moves back toward S604`
  - S609 export `status=ready`
  - S609 frames exported: `48`
  - S609 response faces: `55898`
  - S609 remainder faces: `870466`
  - S609 coverage-control attenuated frames: `11`
  - S609 low-coverage rescue frames: `11`
  - S609 low-coverage max rescue: `0.12`
  - S609 XML validation `status=ready`
  - S609 XML parsed: `48`
  - S609 validation failures: `0`
  - S609 validation warnings: `0`
  - S609 render `status=ready`
  - S609 frames rendered: `48`
  - S609 render failures: `0`
  - S609 total elapsed ms: `10101`
  - S609 image bytes: `134.40 MB`
  - S609 preview bytes: `15.73 MB`
  - S609 sequence compare `status=ready`
  - S609 sequence compare common frames: `48`
  - S609 sequence compare selected frames: `19`
  - S609 sequence compare missing references: `0`
  - S609 direct S577 mean MAD: `3.0457930919924556`
  - S609 direct S577 max MAD: `5.651857638888889`
  - S609 direct S577 max abs: `175`
  - S609 direct S585 mean MAD: `3.0571595561128255`
  - S609 direct S585 max MAD: `5.6697800925925925`
  - S609 direct S585 max abs: `174`
  - S609 decision: `promoted; best tested max-abs rescue without losing S607 max-MAD`
  - S610 render `status=ready`, frames rendered `48`, failures `0`
  - S610 response faces: `55850`
  - S610 max rescue: `0.08`
  - S610 direct S577 mean/max/maxabs: `3.045021071780693` / `5.651857638888889` / `176`
  - S610 direct S585 mean/max/maxabs: `3.056393108603395` / `5.6697800925925925` / `175`
  - S610 decision: `not promoted; rescue is too weak and leaves S607 max-abs peak unchanged`
- S611/S612 mid-coverage band rescue sweep:
  - S611 render `status=ready`, frames rendered `48`, failures `0`
  - S611 response faces: `55976`
  - S611 low-coverage max rescue: `0.12`
  - S611 coverage-band rescue frames: `4`
  - S611 coverage-band max rescue: `0.1189232804232805`
  - S611 direct S577 mean/max/maxabs: `3.0469056096750684` / `5.651857638888889` / `175`
  - S611 direct S585 mean/max/maxabs: `3.0582672244727367` / `5.6697800925925925` / `174`
  - S611 decision: `not promoted; frame-34/35 plateau improves but global frame-14 peak remains`
  - S612 export `status=ready`
  - S612 frames exported: `48`
  - S612 response faces: `56058`
  - S612 remainder faces: `870306`
  - S612 coverage-control attenuated frames: `11`
  - S612 low-coverage rescue frames: `11`
  - S612 low-coverage max rescue: `0.2`
  - S612 coverage-band rescue frames: `4`
  - S612 coverage-band max rescue: `0.1189232804232805`
  - S612 XML validation `status=ready`
  - S612 XML parsed: `48`
  - S612 validation failures: `0`
  - S612 validation warnings: `0`
  - S612 render `status=ready`
  - S612 frames rendered: `48`
  - S612 render failures: `0`
  - S612 total elapsed ms: `10116`
  - S612 image bytes: `134.41 MB`
  - S612 preview bytes: `15.74 MB`
  - S612 sequence compare `status=ready`
  - S612 sequence compare common frames: `48`
  - S612 sequence compare selected frames: `20`
  - S612 sequence compare missing references: `0`
  - S612 direct S577 mean MAD: `3.048554499957133`
  - S612 direct S577 max MAD: `5.651857638888889`
  - S612 direct S577 max abs: `173`
  - S612 direct S585 mean MAD: `3.0598990483539095`
  - S612 direct S585 max MAD: `5.6697800925925925`
  - S612 direct S585 max abs: `172`
  - S612 decision: `promoted; best tested peak-error recovery while preserving S607/S609 max-MAD`
- S613/S614/S615 localized screen-error experiments:
  - S613 direct S577 mean/max/maxabs: `3.0386621897505144` / `5.580354295267489` / `173`
  - S613 direct S585 mean/max/maxabs: `3.050184823495371` / `5.599894547325103` / `172`
  - S613 decision: `not promoted as final; best mean MAD but uses a manual screen box`
  - S614 direct S577 mean/max/maxabs: `3.038890683942044` / `5.5758995627572014` / `173`
  - S614 direct S585 mean/max/maxabs: `3.050464838391632` / `5.595675154320989` / `172`
  - S614 decision: `kept as automatic local-control baseline`
  - S615 direct S577 mean/max/maxabs: `3.049201630015432` / `5.654789737654322` / `173`
  - S615 direct S585 mean/max/maxabs: `3.0605547785922496` / `5.672728909465021` / `172`
  - S615 decision: `rejected; material-only attenuation regresses the direct gap`
- S616 response delta buffer:
  - base export `status=ready`, frames exported `48`
  - base export removed response shapes: `96`
  - base export removed response faces: `55526`
  - base XML validation `status=ready`, failures `0`, warnings `0`
  - base render `status=ready`, frames rendered `48`, failures `0`
  - response buffer `status=ready`, missing references `0`
  - response buffer mean abs delta: `2.78263054323131`
  - response buffer max abs delta: `184`
  - response buffer changed channel fraction: `0.16185079357424553`
  - response buffer reconstruction max abs diff: `0`
  - best S585 response scale: `0.75`
  - best S585 response scale mean/max/maxabs: `2.982389550647291` / `5.524723508230453` / `148`
- S617 response scale composite:
  - composite `status=ready`, frames `48`, missing references `0`
  - response scale: `0.75`
  - composite bytes: `14.77 MB`
  - gallery GIF bytes: `33.87 MB`
  - S577 gap `status=ready`, frames `48`, missing references `0`
  - S577 mean/max/maxabs: `2.9732022274734224` / `5.5108699845679014` / `151`
  - S585 gap `status=ready`, frames `48`, missing references `0`
  - S585 mean/max/maxabs: `2.982389550647291` / `5.524723508230453` / `148`
  - S617 decision: `promoted as the current response-scale AOV/export integration target`
- S618 signed response AOV contract:
  - contract `status=ready`, frames `48`, missing references `0`
  - response scale: `0.75`
  - reconstruction max abs diff: `0`
  - reconstruction max mean abs diff: `0.0`
  - mean abs signed delta: `2.092316449116941`
  - max abs signed delta: `138`
  - AOV bytes: `40.45 MB`
  - composite bytes: `14.77 MB`
  - selected-full max mean/maxabs: `0.9312789351851852` / `46`
  - S618 decision: `promoted as the portable signed response-AOV handoff`
- S619 response AOV consumer:
  - consumer `status=ready`, frames `48`, missing references `0`
  - response scale: `0.75`
  - max import absolute diff: `0`
  - max import mean absolute diff: `0.0`
  - max import mismatched coverage: `0.0`
  - S577 mean/max/maxabs: `2.9732022274734224` / `5.5108699845679014` / `151`
  - S585 mean/max/maxabs: `2.982389550647291` / `5.524723508230453` / `148`
  - S619 decision: `promoted as the response-AOV import proof`
- S620 response AOV scene handoff:
  - handoff `status=ready`, frames `48`, missing references `0`
  - response scale: `0.75`
  - max import absolute diff: `0`
  - max import mean absolute diff: `0.0`
  - S577 mean/max/maxabs: `2.9732022274734224` / `5.5108699845679014` / `151`
  - S585 mean/max/maxabs: `2.982389550647291` / `5.524723508230453` / `148`
  - unique scene frames: `36`
  - scene frame count mismatch: `true` as expected from S578 normalized mapping
  - S620 decision: `promoted as the current scene-cache plus response-AOV handoff`
- S621 response AOV scene job manifest:
  - manifest `status=ready`, frames `48`, descriptors `48`
  - missing inputs: `0`
  - SHA mismatches: `0`
  - size mismatches: `0`
  - max import absolute diff: `0`
  - max import mean absolute diff: `0.0`
  - scene asset refs: `192/192`
  - AOV refs: `240/240`
  - unique scene frames: `36`
  - S621 decision: `promoted as the current renderer/cache job descriptor input`
- S622 response AOV scene job dry run:
  - dry run `status=passed`, frames `48`
  - passed frames: `48`
  - failed frames: `0`
  - missing frames: `0`
  - max selected absolute diff: `0`
  - max selected mean absolute diff: `0.0`
  - max imported absolute diff: `0`
  - max imported mean absolute diff: `0.0`
  - output bytes: `14.77 MB`
  - GIF bytes: `7.91 MB`
  - S622 decision: `promoted as the descriptor execution smoke gate`
- S623 response AOV scene backend adapter:
  - adapter `status=passed`, frames `48`
  - passed frames: `48`
  - failed frames: `0`
  - process failures: `0`
  - stderr bytes: `0`
  - max selected absolute diff: `0`
  - max selected mean absolute diff: `0.0`
  - max imported absolute diff: `0`
  - max imported mean absolute diff: `0.0`
  - output bytes: `14.77 MB`
  - GIF bytes: `7.91 MB`
  - S623 decision: `promoted as the external backend process boundary`

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
13. a public visual review URL for the S587 compare gallery,
14. an external tonemap backend executable sample that consumes S585-derived
   scene descriptors and reproduces representative target frames through a
   subprocess boundary,
15. a scene-cache direct backend sample that derives the same controls from
   S578/S580 scene data before validating against S585 target references,
16. a full48 scene-cache direct backend run with exact S585 target parity
   through the same external backend process boundary,
17. a full48 backend promotion gate that compares the S591 output against both
   the S585 target and S577 accepted visual gate,
18. a public visual review URL for that full48 backend promotion gate,
19. a full48 renderer-native material package with per-frame Mitsuba material
   snippets and localized texture bindings derived from the validated S591/S592
   contract,
20. a validated 8-frame Mitsuba XML sample that binds those material snippets
   into real water-surface BSDF references,
21. an actual SPP4 Mitsuba render of that native-material XML sample plus
   S573/S577/S585 visual comparison artifacts,
22. a renderable localized water-face material split path that consumes the
   low-frequency response mask through alpha-aware mesh partitioning,
23. a tighter localized split baseline that is much closer to S577/S585 than
   the previous native-material renders on direct 8-frame MAD,
24. a full48 stability render of that localized split path through the real
   Mitsuba SPP4 backend,
25. a quieter full48 localized split baseline that reduces mean S577/S585
   error while preserving backend stability,
26. a guarded full48 localized split baseline that improves both mean and max
   absolute S577/S585 error over the previous quiet baseline,
27. a soft-guard full48 baseline that improves mean/max-MAD error while keeping
   the S577 peak error below the earlier quiet-baseline outlier,
28. a rejected peak-balance neighbor proving the current scalar split family is
   near a tradeoff boundary,
29. a locally published S604 review gallery with verified HTML/GIF checks,
30. an automatic signed screen-error attenuation baseline that replaces manual
   late-frame screen boxes,
31. a rejected material-only response attenuation probe,
32. a base-only Mitsuba render that removes the response water bins while
   preserving the same scene/camera/secondary context,
33. a full/base response delta buffer and compositing sweep that improves S585
   direct mean/max MAD before renderer-native AOV integration,
34. a promoted response-scale composite manifest that packages the selected
   `0.75` response strength as a reusable S577/S585-gated visual candidate,
35. a signed response-AOV contract that reconstructs the selected composite
   exactly from base, positive response, and negative response layers,
36. a response-AOV consumer proving that the portable contract can reconstruct
   the promoted visual gate with exact parity,
37. a scene-cache plus response-AOV handoff that carries scene data, render-data
   controls, signed AOV layers, selected composites, and S577/S585 gate metrics
   together for larger renderer-cache jobs,
38. a renderer/cache job manifest that expands that handoff into 48 per-frame
   descriptors with concrete input refs, future output targets, and gate
   expectations,
39. a descriptor-level renderer/cache dry run that fills those output targets
   and proves exact selected/imported composite parity across all 48 frames,
40. an external backend process adapter that executes the same descriptors
   through subprocess calls with zero process failures and zero selected/imported
   visual drift.

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
publishes that gate for direct visual inspection. S589 moves the same contract
out of the proof-only stage and into an executable backend sample with
descriptor, process, metadata, validation, strip, GIF, and report artifacts.
S590 removes the S585 manifest as the source of backend inputs: it consumes the
scene-cache handoff and render-data sidecar directly, while preserving exact
S585 target parity on the representative sample. S591 proves the same
scene-cache direct backend path holds across all 48 frames. S592 confirms that
the full48 backend result is ready to feed the next renderer-native material
implementation step: backend-target parity is exact, and accepted-gate movement
is still bounded to max abs diff `5` and max mean diff `0.4139242541152263`.
S593 publishes the full48 backend gate for direct inspection. S594 turns the
validated backend/gate contract into renderer-native material inputs, so the
next step can patch or generate Mitsuba XML scenes instead of hand-translating
image-space controls. S595 performs that first binding into real XML scenes and
passes XML validation. S596 proves the bound XML sample is renderable in the
native Mitsuba path and produces a much more refractive/renderer-native water
look; the sequence compare also shows this is a major visual move from the
S577/S585 accepted gate, so it should be tuned before any full48 promotion.
S597 fixes a concrete mask-ingestion bug in the face-split path and proves a
localized native-material split can render, but the selected response region is
still broad enough to increase the legacy S328 target gap relative to S596.
S598 reduces the selected region to 24k response faces and, despite a worse
legacy S328 gap, directly matches the current S577/S585 gates much more closely
than S596 or S597. This makes S598 the current tuning baseline, not yet a full48
promotion. S599 narrows and weakens that split again to 20k response faces and
slightly improves direct S577/S585 metrics over S598, so S599 replaces S598 as
the current localized native-material tuning baseline. It is still an 8-frame
sample and not a full48 promotion. S600 scales the same setting through all 48
frames without XML/render failures. The full48 direct metrics are still close
to S577/S585, but the mean MAD rises slightly versus the 8-frame sample and
late-frame strips show a stronger water highlight. S600 is therefore the
full48 stability baseline, not the final accepted visual promotion. S601
quietens that full48 response and lowers direct S577/S585 mean MAD
substantially while preserving 48/48 render stability. It becomes the current
full48 native-material split baseline, with S577 max absolute diff `179` as the
main tracked risk. S602 removes that risk by guarding the response further:
mean S577/S585 MAD and max absolute error both improve over S601, while max
MAD rises slightly. S603 shows that simple face-count recovery is not enough:
it improves max MAD slightly but worsens mean MAD. S604 softens the response
instead and improves mean/max-MAD over S602 while keeping S577 max abs below
the S601 outlier. S604 is the current full48 native-material split baseline,
with peak error versus S602 still tracked. S605 tries a middle point, but it
loses S604's mean/max-MAD gains and returns S577 peak error to `179`. This
suggests the next improvement should not be another simple scalar midpoint.
S606 packages the S604 review evidence locally and verifies the page/GIF over
HTTP. Public quick-tunnel publishing is blocked by Cloudflare quick-tunnel
issuance returning HTTP `500`, not by the gallery artifacts. S607 adds
coverage-aware per-frame attenuation, reduces high-coverage late-frame response
faces, and improves S604's mean/max-MAD scores without changing the remaining
frame-14 max-absolute outlier. S608/S609/S610 add a second, opposite control:
low-coverage rescue for under-bright localized highlights. S609 is the best
tested setting because it reduces the frame-14 max-abs peak by one level while
preserving S607's max-MAD win and staying much closer to S607 mean MAD than
S608. S611 adds a narrow coverage-band rescue that fixes the frame-34/35
plateau but not the global peak. S612 combines both rescue bands and becomes
the current baseline for scalar split tuning: max MAD remains unchanged, global
max abs improves to `173/172`, and the late-frame high-coverage attenuation
stays intact. S613 and S614 show that localized screen-error controls are the
right next direction, with S614 preferred because it removes the manual screen
box. S615 rejects material-only attenuation as a direct promotion path. S616
then separates S614 into a reusable full/base response buffer and proves that
response scale `0.75` can improve the direct S585 probe before moving that
control into renderer-native AOV/export plumbing. S617 promotes that scale into
a standard composite manifest and verifies it against both S577 and S585. This
is now the concrete visual target for the next portable response-AOV export
contract. S618 completes that export boundary by storing the selected response
as signed positive/negative AOV layers with exact reconstruction. S619 consumes
that contract back into a standard composite summary with zero import diff,
which closes the response-AOV export/import loop. S620 wires that proven AOV
boundary into the S578/S580 scene-cache handoff so scene data and signed
response layers can travel through the same renderer-cache job contract. S621
turns that contract into concrete frame descriptors, which is the execution
boundary a renderer/cache backend can consume next. S622 executes that boundary
with the current dry-run compositor and proves the descriptor IO path has zero
visual drift before swapping in a heavier external renderer/cache backend.
S623 performs that swap at the process boundary: the image math is still the
parity backend, but the execution contract is now the same shape a native
renderer/cache backend can replace.

## Next

Use the texture/cache boundary as the accepted visual handoff while moving the
photoreal renderer work back toward real scene data:

1. Keep S577 as the current accepted full48 texture/cache import gate.
2. Use S578/S579 as the renderer-side scene-data input contract.
3. Use S580/S581 as the reusable depth/material control sidecar and profile.
4. Use S623 as the current external backend process contract. The next step
   should replace the parity backend internals with native renderer/cache work
   while preserving descriptor IO, selected/imported parity, and carried
   S577/S585 gate reporting.
5. Retry public publishing only after quick-tunnel issuance is healthy, or use
   a named tunnel for stable review URLs.
6. Keep S592 as the pass/fail gate: preserve S585 target parity and only
   promote renderer-native changes that improve or justify the S577 accepted
   gate movement.
