# Cinematic Hyperreal Simulation Render Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current LSFS 3D sparse/MR two-phase simulator into a reproducible pipeline that can produce a cinematic, inspectable, hyperrealistic water shot.

**Architecture:** Keep simulation, cache validation, render data conversion, and cinematic rendering as separate validated layers. Use the current C++ simulation runners for physics and metrics, JSONL/manifest render caches for interchange, Python tools for preview/validation/conversion, and an external renderer bridge before attempting any custom offline renderer. Every milestone must leave a runnable command, a measurable gate, and a committed artifact.

**Tech Stack:** C++17/MSVC, CMake, doctest, Python 3, JSONL cache manifests, Pillow/numpy preview tooling, optional OpenVDB/USD/Blender bridge after the cache schema is stable.

---

## Current State

The project has already landed the simulation and pre-render foundations needed for a first cinematic path:

- Sparse and multires 3D two-phase simulation exist and have validator/bench runners.
- SPEC-2 adaptivity scaffolds exist for narrow-band air, stochastic gas coarsening, liquid coarsening, liquid refill, and volume-weighted particle accounting.
- SPEC-3 solver work exists for high-density-ratio gates, coarse correction, coarse preconditioner, auto-disable, flexible CG, and relaxation diagnostics.
- Physical residuals exist for adaptive timestep, RK3 advection, c_div volume correction, escaped-particle classification, secondary particle lifecycle, and surface-tension diagnostics.
- SPEC-4 cache export exists for camera metadata, phase-field cells, primary particles, secondary particles, manifests, validation, and quick previews.

The missing work is not one feature. It is a pipeline:

1. Larger measured simulation runs.
2. Stable render-cache schema for cinematic data.
3. Mesh/volume/spray conversion.
4. External renderer bridge.
5. Shot orchestration and visual QA.
6. Final large-scale optimization and quality sweep.

## Completion Targets

**First cinematic preview target:** A 3-6 second 3D bubble or dam-break style shot rendered from validated cache frames with camera motion, water volume/mesh representation, visible secondary particles, and a GIF/MP4 preview artifact under `build/`.

**Hyperreal demo target:** A 6-12 second shot with large-scale sparse or MR simulation, validated cache manifest, water surface or volume representation, spray/foam/bubble render channels, cinematic camera/light/tone settings, and reproducible benchmark CSVs showing runtime, memory proxy, pressure convergence, and cache/render timing.

**Final research-quality target:** A repeatable end-to-end command sequence that can regenerate simulation caches, validate them, convert them to render assets, render frames, assemble a movie, and compare diagnostics against saved acceptance thresholds.

## Non-Goals

- Do not build a custom production renderer before proving the cache-to-render bridge.
- Do not optimize large scenes by intuition; every large-scene change must go through CSV metrics.
- Do not add slow cinematic runs to default `ctest`.
- Do not make photoreal claims from PPM slice demos or point-cloud previews.

## File Structure

- Modify `README.md`
  - Add status rows as each milestone lands.
  - Add quickstart commands only when they are validated.
- Modify `apps/bench_large_scale3d_tp.cpp`
  - Extend large-scale CSV metrics for simulation, cache export, preview/conversion timing, and memory proxy.
- Modify `apps/export_render_cache3d.cpp`
  - Add cinematic cache options, camera presets, frame cadence controls, and optional secondary/field channels.
- Modify `src/driver/render_cache3d.h`
  - Extend cache schema only with backwards-compatible versioned sections.
- Modify `tools/validate_render_cache.py`
  - Add stricter gates for cinematic sequences, frame continuity, phase volume drift, camera continuity, and secondary channel sanity.
- Modify `tools/render_cache_preview.py`
  - Keep fast inspection path current with every schema change.
- Create `tools/convert_render_cache.py`
  - Convert cache manifests into renderer-friendly intermediate assets.
- Create `tools/cinematic_render_stub.py`
  - Provide a reproducible local image-sequence render path before external renderer integration.
- Create `tools/assemble_frames.py`
  - Assemble PNG frame directories into GIF/MP4 preview artifacts when dependencies are available.
- Create milestone implementation plans as they begin:
  - `docs/superpowers/plans/2026-06-17-large-scale-benchmark-v2.md`
  - `docs/superpowers/plans/2026-06-17-cinematic-cache-schema-v2.md`
  - `docs/superpowers/plans/2026-06-17-render-cache-conversion.md`
  - `docs/superpowers/plans/2026-06-17-first-cinematic-preview.md`
  - `docs/superpowers/plans/2026-06-17-secondary-render-channels.md`
  - `docs/superpowers/plans/2026-06-17-water-reconstruction-export.md`
  - `docs/superpowers/plans/2026-06-17-external-render-bridge.md`
  - `docs/superpowers/plans/2026-06-17-cinematic-shot-pipeline.md`
  - `docs/superpowers/plans/2026-06-17-cinematic-render-presets.md`
  - `docs/superpowers/plans/2026-06-17-large-scale-cinematic-gate.md`

## Roadmap Overview

| Milestone | Name | Primary Outcome | Commit Boundary |
| --- | --- | --- | --- |
| S36 | Large-scale benchmark v2 | CSV evidence for sim/cache/preview timing and memory proxy | Done in `test: extend large scale render benchmarks` |
| S37 | Cinematic cache schema v2 | Stable cache fields for camera, water, secondary, and render metadata | Done in `feat: extend cinematic render cache schema` |
| S38 | Cache-to-render conversion | Renderer-neutral conversion tool and validation loop | Done in `feat: add render cache conversion tool` |
| S39 | First cinematic preview renderer | Local PNG/GIF shot preview from cache manifest | Done in `feat: add cinematic cache preview renderer` |
| S40 | Secondary spray/foam visual channels | Separate droplet/bubble/foam-like channels in cache and preview | Done in `feat: add secondary render channels` |
| S41 | Surface/volume reconstruction path | Mesh or volume asset output for water body | Done in `feat: add water reconstruction export` |
| S42 | External renderer bridge | Blender/USD/OpenVDB bridge selected by measured feasibility | Done in `feat: add external render bridge` |
| S43 | Shot orchestration runner | Single command emits cache, validation, render frames, and movie | Done in `feat: add cinematic shot pipeline` |
| S44 | Hyperreal material and lighting pass | Camera, lights, tone mapping, water/spray material presets | Done in `feat: add cinematic render presets` |
| S45 | Large-scale cinematic gate | End-to-end large shot with CSV, manifest, preview, and render artifacts | Done in `test: add large scale cinematic gate` |
| S46 | Smooth water surface pass | Reduce voxel-block look with mesh smoothing, normals, and reconstruction QA | Done in `feat: smooth cinematic water meshes` |
| S47 | Falling-water/dam-break cache preset | Produce a more visually dynamic water-motion shot than the current bubble tank | Done in `feat: add cinematic falling water preset` |
| S48 | Visible secondary particle pass | Ensure spray/foam/bubble channels can be seen in cinematic frames | Done in `feat: enhance secondary cinematic render` |
| S49 | Camera motion and shot grammar | Add camera path interpolation, framing presets, and shot continuity checks | Done in `feat: add cinematic camera motion` |
| S50 | Water material depth pass | Improve material response with depth tint, edge highlights, and preset sweeps | Done in `feat: improve water material presets` |
| S51 | Presentation artifact pack | Emit GIF/contact sheet/report bundle for fast visual review and sharing | Done in `feat: package cinematic review artifacts` |
| S52 | Visual gate v2 | Run a larger dynamic shot through the improved surface/render stack | Done in `test: add cinematic visual gate v2` |
| S53 | Implicit tetra water surface | Reduce voxel stair stepping with an opt-in implicit tetra OBJ reconstruction path | Done in `feat: add implicit tetra water surfaces` |
| S54 | High-detail surface gate | Run a higher-density tetra surface close-up and record timing/framing limits | Done in `test: add high detail cinematic surface gate` |
| S55 | Grid-aware cinematic framing | Scale preset camera target/distance from reference grid dims for high-detail gates | Done in `feat: add grid-aware cinematic framing` |
| S56 | Physically conditioned secondary seed | Replace demo secondary rings with liquid-candidate spray seeds in cinematic cache export | Done in `feat: add physical secondary spray seeds` |
| S57 | Sim-side secondary spray gate | Emit physical spray seeds inside sparse 3D TP sim steps with lifecycle volume accounting and shot acceptance thresholds | Done in `feat: add sim-side secondary spray gate` |
| S58 | Interface-conditioned secondary spray gate | Require measured interface diagnostics for physical sparse spray emission and record a larger visual gate | Done in `feat: add interface conditioned secondary gate` |
| S59 | Large water-event scene | Replace compact falling block with a wider falling sheet and impact pool cinematic scene | Done in `feat: add large water event scene` |
| S60 | Contact splash visibility gate | Start the large sheet lower/faster and include downward-impact spray candidates for stronger contact visuals | Done in `feat: add contact splash secondary gate` |
| S61 | Contact foam and surface detail gate | Split impact secondaries into spray/foam channels and add opt-in Blender water surface detail | Done in `feat: add contact foam surface detail gate` |
| S62 | Secondary render size pass | Add channel-specific secondary radii and spray/foam emission controls for stronger contact readability | Done in `feat: add secondary render size pass` |
| S63 | Contact close-up camera gate | Add `dam_break_contact_closeup` as a closer inspection preset with a 36-frame Blender visual gate | Done in `feat: add contact closeup camera gate` |
| S64 | Contact camera stability review | Report camera path stability gates and emit a wide/close review comparison sheet | Done in `feat: add contact camera stability review` |
| S65 | Cinematic visual QA metrics | Summarize frame luminance, contrast, bright-pixel ratios, and preset-driven visual QA gates | Done in `feat: add cinematic visual qa metrics` |
| S66 | Volumetric spray/foam render pass | Add a soft halo pass for spray/foam secondaries while preserving visual QA gates | Done in `feat: add volumetric spray foam render pass` |
| S67 | Secondary soft-pass performance | Batch spray/foam halo geometry into channel meshes to cut Blender render cost while preserving QA | Done in `perf: batch secondary soft pass geometry` |
| S68 | Secondary mist billboard quality | Use camera-facing billboard disks for spray/foam soft pass while preserving S67 cost and QA | Done in `feat: add secondary mist billboard pass` |
| S69 | Secondary mist alpha falloff | Add concentric radial alpha falloff materials for billboard mist disks while preserving render cost and QA | Done in `feat: add secondary mist alpha falloff` |
| S70 | Secondary mist falloff tuning | Tune outer alpha, radius, and inner emission for cleaner mist billboard edges while preserving QA | Done in `style: tune secondary mist falloff` |
| S71 | Secondary mist texture falloff | Add UV-driven radial shader alpha falloff for mist billboards while preserving QA and render cost | Done in `feat: add secondary mist texture falloff` |
| S72 | Secondary velocity streak pass | Add velocity-aligned spray/foam streak quads from secondary particle velocities for stronger motion readability | Done in `feat: add secondary velocity streak pass` |
| S73 | Secondary streak tuning | Tune spray streak length/width/intensity and report actual streak counts per frame | Done in `style: tune secondary velocity streaks` |
| S74 | Impact framing gate | Add inherited impact-framing preset and gate so the active secondary band stays visible longer | Done in `feat: add impact framing gate` |
| S75 | Active secondary framing QA | Project spray/foam particles into camera space and gate inside-frame ratio plus vertical placement | Done in `test: add active secondary framing qa` |
| S76 | Surface contact foam pass | Render flattened foam patches near the water surface to connect secondary foam back to the water body | Done in `feat: add surface contact foam pass` |
| S77 | Contact foam flow lines | Use an inherited preset with flow-aligned surface foam strokes for less static contact foam | Done in `feat: add contact foam flow lines` |
| S78 | Contact foam material fade | Add radial shader falloff to flow-aligned contact foam so strokes blend into the water surface | Done in `feat: add contact foam material fade` |
| S79 | Water-surface glint flow | Add subtle directional surface glint strokes so the main water body carries visible flow cues | Done in `feat: add water surface glint flow` |
| S80 | Water reflection continuity | Add longer camera-stable water reflection ribbons over S79 glints to reduce the flat-slab read of the main water body | Done in `feat: add water reflection continuity pass` |
| S81 | Water highlight temporal QA | Gate frame-to-frame luminance and highlight-mask deltas to catch flicker in glint/reflection layers | Done in `test: add water highlight temporal qa` |
| S82 | Water highlight temporal diff sheet | Emit frame-difference review artifacts so highlight movement can be visually inspected | Done in `test: add water highlight temporal diff sheet` |
| S83 | Water highlight motion tuning | Increase glint/reflection drift and coverage while preserving temporal highlight QA | Done in `style: tune water highlight motion` |
| S84 | Water impact ripple cues | Add foam/spray-driven impact-region ripple arcs so the splash contact area reads as broken water surface | Done in `feat: add water impact ripple cues` |
| S85 | Water impact ripple tuning | Lower ripple density and soften material strength so contact breakup remains readable without overpowering foam/spray | Done in `style: tune water impact ripple cues` |
| S86 | Water impact ripple material fade | Add UV edge-falloff material to impact ripple arcs so contact breakup blends into the water surface | Done in `feat: add water impact ripple material fade` |
| S87 | Water impact ripple focus QA | Add a focused contact-region review sheet and gate for ripple readability | Done in `test: add water impact ripple focus qa` |
| S88 | Water impact ripple focus comparison | Compare focus review sheets across nearby cinematic gates without replacing the full-frame contact sheet | Done in `test: add water impact ripple focus comparison` |
| S89 | Contact focus camera tuning | Narrow the contact camera and focus crop while preserving visual, temporal, camera, and secondary framing gates | Done in `style: tune contact focus camera` |
| S90 | Ripple placement focus tuning | Widen and slightly strengthen contact-region impact ripples while preserving all cinematic gates | Done in `style: tune ripple placement focus` |
| S91 | Ripple readability diagnostics | Add edge/highlight diagnostic sheets for contact-region ripple readability review | Done in `test: add ripple readability diagnostics` |
| S92 | Ripple diagnostic comparison | Compare ripple readability diagnostic sheets side by side across nearby cinematic gates | Done in `test: add ripple diagnostic comparison` |
| S93 | Contact foam/ripple integration | Soften and narrow contact foam so surface breakup reads less like separate overlay layers | Done in `style: tune contact foam ripple integration` |
| S94 | Water surface breakup/noise tuning | Increase water surface detail strength/depth for stronger contact-region breakup while preserving diagnostic and temporal gates | Done in `style: tune water surface breakup noise` |
| S95 | Spray/foam depth layering | Reduce spray/foam radius, soft-pass brightness, and foam streak intensity so secondaries sit more naturally in the contact volume | Done in `style: tune spray foam depth layering` |
| S96 | Secondary depth review metric | Add projected spray/foam contact-volume diagnostic sheet and gate for crop count, depth span, and normalized depth span | Done in `test: add secondary depth review metric` |
| S97 | Secondary volume-depth material tuning | Lower spray/foam emission and streak brightness while preserving secondary depth, visual, temporal, and ripple gates | Done in `style: tune secondary volume depth material` |
| S98 | Secondary depth comparison sheet | Compare secondary depth diagnostic sheets side by side across neighboring gates | Done in `test: add secondary depth comparison sheet` |
| S99 | Water volume/depth cue tuning | Strengthen water-body depth/rim cues while preserving visual, temporal, ripple, secondary depth, and comparison gates | Done in `style: tune water volume depth cues` |
| S100 | Water depth focus comparison | Move focus review to a lower water-body crop so water depth/rim cues can be compared against S99 without relying only on full-frame contact sheets | Done in `test: add water depth focus comparison` |
| S101 | Water depth diagnostic decision | Keep the S100 lower water-body crop as the water-depth diagnostic and move on to a real volume/scattering render pass | Done in `docs: record water depth diagnostic decision` |
| S102 | Water volume scattering pass | Add opt-in internal attenuation sheets so the main water body gains subtle volume/scattering cues while preserving the S100 diagnostic gates | Done in `feat: add water volume scattering pass` |
| S103 | Secondary render integration review | Extend the S102 water volume baseline with bubble-inclusive secondary depth review and comparison | Done in `test: add secondary render integration review` |
| S104 | Large-grid cinematic benchmark | Run the S103 render/review stack on a `32 x 40 x 26` grid with larger-grid camera and secondary acceptance gates | Done in `test: add large grid cinematic benchmark` |
| S105 | Cinematic benchmark summary | Generate a compact table for recent cinematic gates with runtime, grid size, and key QA metrics | Done in `tools: summarize cinematic gate metrics` |
| S106 | Large-grid render-quality followup | Reuse the S104 large-grid stack with a higher, wider camera to improve early secondary framing while preserving the render/review gates | Done in `test: tune large grid render quality` |
| S107 | Large-grid benchmark summary refresh | Include S106 in the compact benchmark table and expose framing-min plus validate/reconstruct/convert timing columns | Done in `tools: refresh large grid benchmark summary` |
| S108 | Cinematic stage profile | Turn the S107 benchmark table into render/non-render cost splits and rank large-grid stage bottlenecks | Done in `tools: profile cinematic stage costs` |
| S109 | Converted sequence reuse | Add opt-in SHA256 fingerprint reuse for converted sequence assets and expose reuse status in shot reports | Done in `perf: reuse fresh converted render cache` |
| S110 | Render-cache validation reuse | Add opt-in SHA256 validation stamps and expose validation reuse status in shot reports | Done in `perf: reuse fresh render cache validation` |
| S111 | Water reconstruction reuse | Add opt-in SHA256 water reconstruction reuse and expose water mesh reuse status in shot reports | Done in `perf: reuse fresh water reconstruction` |
| S112 | Export cache reuse | Add opt-in exporter-command cache reuse and preserve export metrics for downstream gates | Done in `perf: reuse fresh export cache` |
| S113 | Warm-cache stage summary | Summarize shot command timings and reuse flags from `shot_summary.json` | Done in `tools: summarize warm cache commands` |
| S114 | Render frame reuse | Add opt-in render-frame reuse for preview/Blender outputs and expose render reuse status in shot reports | Done in `perf: reuse fresh render frames` |
| S115 | Large-grid warm-cache preview benchmark | Measure the full opt-in warm-cache path on a larger-grid preview run | Done in `test: benchmark large grid warm cache preview` |
| S116 | Warm-cache fingerprint cost reduction | Move water reconstruction reuse detection before phase-cell loading and reduce large-grid warm-cache reconstruction check time | Done in `perf: reduce warm cache fingerprint overhead` |
| S117 | GIF assembly reuse | Add opt-in GIF assembly reuse and expose GIF reuse status in shot reports | Done in `perf: reuse fresh cinematic gif` |
| S118 | Blender quality warm-cache return | Re-run the large-grid Blender quality gate with full warm-cache controls enabled | Done in `test: return to blender quality warm cache` |
| S119 | Blender quality baseline comparison | Compare the current warm-cache Blender quality output against the S106 large-grid baseline | Done in `test: compare blender quality baseline` |
| S120 | Cinematic artifact inspection package | Validate and link the current GIF, contact sheet, and comparison sheets for quick visual inspection | Done in `tools: package cinematic artifacts` |
| S121 | Cinematic static gallery | Copy the current review assets into a self-contained browser gallery with manifest and report | Done in `tools: build cinematic gallery` |
| S122 | Cinematic gallery cftunnel publisher | Serve the static gallery locally, open an optional Cloudflare quick tunnel, and verify HTML/GIF assets over HTTP | Done in `tools: publish cinematic gallery` |
| S123 | Cinematic visual review triage | Record gallery/publish coverage, numeric gates, visual findings, and select the next look-dev adjustment | Done in `docs: triage cinematic visual review` |
| S124 | Contact-band composition pass | Lower the large-grid camera target toward the contact band while preserving S119 comparison and review gates | Done in `style: add contact band composition preset` |
| S125 | Contact-volume integration pass | Add lower contact-volume haze plus softer spray/foam/water scattering material settings while preserving S124 review gates | Done in `style: add contact volume integration preset` |
| S126 | Scene de-tank composition pass | Add a contact mist curtain pass and softer world/floor contrast while preserving S125 review gates | Done in `style: add scene detank composition pass` |
| S127 | Non-boxed falling-water scene pass | Change the falling-water scene/source shape so the top water silhouette no longer reads as a rectangular tank wall | Done in `feat: add nonboxed falling water scene` |
| S128 | S127 gallery refresh/publish | Package and publish the S127 review artifacts so the current non-boxed scene can be inspected externally | Done in `docs: publish s127 cinematic gallery` |
| S129 | Public gallery visual triage | Review the S127 public gallery and choose the next concrete scene/render improvement from visible evidence | Done in `docs: triage s127 public gallery` |
| S130 | Environment/depth-context pass | Reduce visible side-wall/enclosure bands and add stronger large-scale depth context around the non-boxed falling-water scene | Done in `style: add environment depth context preset` |
| S131 | S130 gallery refresh/publish | Package and publish the S130 review artifacts for external inspection before the next shot-shape adjustment | Done in `docs: publish s130 cinematic gallery` |
| S132 | S130 public gallery visual triage | Review the S130 public gallery and choose the next concrete visible shot-shape adjustment from current evidence | Done in `docs: triage s130 public gallery` |
| S133 | Falling-source silhouette breakup pass | Break the upper falling-water mass into staggered rounded lobes with less continuous vertical side-wall structure | Done in `feat: add falling source silhouette breakup` |
| S134 | S133 gallery refresh/publish | Package and publish the S133 review artifacts for external inspection | Done in `docs: publish s133 cinematic gallery` |
| S135 | S133 public gallery visual triage | Review the S133 public gallery and choose the next concrete visible shot adjustment from current evidence | Done in `docs: triage s133 public gallery` |
| S136 | Offscreen-source impact framing pass | Reframe the S133 scene so the source is mostly out of frame and attention stays on water entering frame and impacting the pool | Done in `style: add offscreen source impact framing` |
| S137 | S136 gallery refresh/publish | Package and publish the S136 review artifacts for external inspection before the next visual triage | Done in `docs: publish s136 cinematic gallery` |
| S138 | S136 public gallery visual triage | Review the S136 public gallery and choose the next concrete visible shot adjustment from current evidence | Done in `docs: triage s136 public gallery` |
| S139 | Low-angle impact close-up framing | Move the camera lower and closer to the contact band so the upper source is mostly cropped while spray/ripple readability remains gated | Done in `style: add low angle impact closeup framing` |
| S140 | S139 gallery refresh/publish | Package and publish the S139 review artifacts for external inspection before the next visual triage | Done in `docs: publish s139 cinematic gallery` |
| S141 | S139 public gallery visual triage | Review the S139 public gallery and choose the next concrete visible shot adjustment from current evidence | Done in `docs: triage s139 public gallery` |
| S142 | Impact-timed review window | Let the Blender bridge render a later cache window so the shot starts closer to visible impact without changing the simulation | Done in `feat: add impact timed render window` |
| S143 | S142 gallery refresh/publish | Package and publish the S142 review artifacts for external inspection before the next visual triage | Done in `docs: publish s142 cinematic gallery` |
| S144 | S142 public gallery visual triage | Review the S142 public gallery and choose the next concrete visible shot adjustment from current evidence | Done in `docs: triage s142 public gallery` |
| S145 | Foreground surface-detail/foam-breakup pass | Preserve S142 timing/framing while increasing close-up water detail, glint/ripple readability, and contact foam breakup | Done in `style: add foreground surface detail foam` |
| S146 | S145 gallery refresh/publish | Package and publish the S145 review artifacts for external inspection before the next visual triage | Done in `docs: publish s145 cinematic gallery` |
| S147 | S145 public gallery visual triage | Review the S145 public gallery and choose the next concrete visible shot adjustment from current evidence | Done in `docs: triage s145 public gallery` |
| S148 | Foreground water thickness/refraction pass | Add near-field water-body depth/refraction cues over S145 to reduce the thin-slab read while preserving current timing and gates | Done in `style: add foreground water thickness refraction` |
| S149 | S148 gallery refresh/publish | Package and publish the S148 review artifacts for external inspection before the next visual triage | Done in `docs: publish s148 cinematic gallery` |
| S150 | S148 public gallery visual triage | Review the S148 public gallery and choose the next concrete visible shot adjustment from current evidence | Done in `docs: triage s148 public gallery` |
| S151 | Source-edge cleanup framing pass | Crop or de-emphasize the upper source region over S148 while preserving close-up contact, water thickness, and review gates | Done in `style: add source edge cleanup framing` |
| S152 | S151 gallery refresh/publish | Package and publish the S151 review artifacts for external inspection before the next visual triage | Done in `docs: publish s151 cinematic gallery` |
| S153 | S151 public gallery visual triage | Review the S151 public gallery and choose the next concrete visible shot adjustment from current evidence | Done in `docs: triage s151 public gallery` |
| S154 | Secondary bead de-emphasis and mist integration | Reduce bead-like secondary particles over S151 while strengthening soft mist/streak integration for spray and foam | Done in `style: integrate secondary mist rendering` |
| S155 | S154 gallery refresh/publish | Package and publish the S154 review artifacts for external inspection before the next visual triage | Done in `docs: publish s154 cinematic gallery` |
| S156 | S154 public gallery visual triage | Review the S154 public gallery and choose the next concrete visible shot adjustment from current evidence | Done in `docs: triage s154 public gallery` |
| S157 | Contact foam sheet continuity pass | Broaden and connect surface contact foam strokes/wakes around the impact region over S154 while preserving gates | Done in `style: add contact foam sheet continuity` |
| S158 | S157 gallery refresh/publish | Package and publish the S157 review artifacts for external inspection before the next visual triage | Done in `docs: publish s157 cinematic gallery` |
| S159 | S157 public gallery visual triage | Review the S157 public gallery and choose the next concrete visible shot adjustment from current evidence | Done in `docs: triage s157 public gallery` |
| S160 | Large-event cinematic scale gate | Move beyond same-shot look-dev by piloting a larger physical event with the S157 render stack and measured gates | Done in `test: add large event cinematic scale gate` |
| S161 | S160 gallery refresh/publish | Package and publish the S160 large-event gate artifacts for public inspection before the next scale/composition adjustment | Done in `docs: publish s160 cinematic gallery` |
| S162 | Establishing scale composition pass | Use S160 as input evidence to widen the shot grammar so the larger physical event reads as a broader impact-pool scene, not only a foreground surface/mist close-up | Done in `style: add establishing scale composition` |
| S163 | S162 gallery refresh/publish | Package and publish the S162 establishing-scale artifacts for public inspection before the next visual triage | Done in `docs: publish s162 cinematic gallery` |
| S164 | S162 public gallery visual triage | Review the S162 public gallery and choose whether to attack source-slab silhouette, wider event shape, or render-detail readability next | Done in `docs: triage s162 public gallery` |
| S165 | Source-slab silhouette de-emphasis scene pass | Add a source-breakup scene/preset variant that reduces ceiling-like upper source mass while preserving the S162 impact-pool composition and gates | Done in `style: add source slab deemphasis scene` |
| S166 | S165 gallery refresh/publish | Package and publish the S165 source-slab de-emphasis artifacts for public inspection before the next visual triage | Done in `docs: publish s165 cinematic gallery` |
| S167 | S165 public gallery visual triage | Review the S165 public gallery and choose whether to tune remaining upper water band, depth readability, or advance to the next event-scale/render-data milestone | Done in `docs: triage s165 public gallery` |
| S168 | Water depth and foreground separation pass | Tune render-side depth cues over S165 so foreground, midground, and background water do not collapse into one flat blue sheet | Done in `style: add water depth separation preset` |
| S169 | S168 gallery refresh/publish | Package and publish the S168 depth-separation artifacts for public inspection before the next visual triage | Done in `docs: publish s168 cinematic gallery` |
| S170 | S168 public gallery visual triage | Review the S168 public gallery and choose whether to continue render-side polish or move to render-data/export depth for the next cinematic milestone | Done in `docs: triage s168 public gallery` |
| S171 | Render-data and depth export milestone | Add richer per-frame water volume/depth metadata for later cinematic render passes, preserving the current S168 visual baseline and gallery flow | Done in `tools: export cinematic render data summary` |
| S172 | Render-data consumer diagnostics | Consume the S171 sidecar in a depth/profile diagnostic artifact before wiring it into new render behavior | Done in `tools: add render data profile diagnostics` |
| S173 | Metadata-driven depth attenuation pass | Consume the S171/S172 render-data profile in the Blender bridge for a bounded depth/secondary attenuation render pass over S168 | Planned |

## Decision Gates

### Renderer Bridge Decision

Choose the external render bridge only after S38 proves cache conversion.

Accepted choices:

- **Blender first:** preferred if a Python-only bridge can produce water mesh/volume plus particles without complex native dependencies.
- **OpenVDB/USD first:** preferred if volumetric water/spray fidelity matters more than quick local setup.
- **Custom renderer later:** allowed only after external bridge limitations are documented in a checked-in report.

Decision artifact:

- Create `docs/render_bridge_decision.md`.
- Include command outputs, sample frame paths, dependency setup notes, and the selected first bridge.

### Water Representation Decision

Use one primary water representation for S41:

- **Mesh surface:** better for first cinematic water body with lighting and reflections.
- **Volume density:** better for spray-heavy or foamy water, but harder to make clean.

Decision rule:

- If cache phase-field resolution is sufficient to reconstruct a stable surface across at least 16 frames, choose mesh.
- If surface flicker is severe but volume preview is stable, choose volume first.
- Keep secondary droplets/bubbles as separate particle channels either way.

## Milestone Details

### S36: Large-Scale Benchmark v2

**Goal:** Stop guessing about the next bottleneck by measuring larger sparse/MR, adaptivity, cache export, validation, and preview timing in one CSV.

**Files:**
- Modify: `apps/bench_large_scale3d_tp.cpp`
- Modify: `README.md`
- Create: `docs/superpowers/plans/2026-06-17-large-scale-benchmark-v2.md`

**Required metrics:**
- grid dims, steps, solver mode, sim kind, adaptivity flags
- particle count start/end, liquid/gas count start/end
- active pressure cells or sparse block counts
- pressure iterations, final residual, convergence flag
- elapsed simulation milliseconds
- cache export milliseconds
- cache validate milliseconds
- preview render milliseconds
- cache byte size
- memory proxy for particles, grid blocks/cells, cache bytes

**Commands:**

```powershell
cmake --build build --config Release --target bench_large_scale3d_tp export_render_cache3d
.\build\Release\bench_large_scale3d_tp.exe --nx 24 --ny 36 --nz 24 --steps 8 --solver all --csv build\large_scale3d_tp_v2.csv
python tools\validate_render_cache.py build\large_scale3d_tp_v2_manifest.json
python tools\render_cache_preview.py build\large_scale3d_tp_v2_manifest.json build\large_scale3d_tp_v2_preview 6
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

**Acceptance gate:**
- CSV exists and has one row per requested solver/adaptivity mode.
- Every row has finite timings and non-negative memory proxy values.
- The runner does not require default `ctest` to run the large case.
- A README quickstart command exists after the runner is validated.

### S37: Cinematic Cache Schema v2

**Goal:** Make render caches carry enough information for a real shot without guessing at render time.

**Files:**
- Modify: `src/driver/render_cache3d.h`
- Modify: `apps/export_render_cache3d.cpp`
- Modify: `tools/validate_render_cache.py`
- Modify: `tools/render_cache_preview.py`
- Modify: `tests/test_render_cache3d.cpp`
- Create: `docs/superpowers/plans/2026-06-17-cinematic-cache-schema-v2.md`

**Schema additions:**
- `cache_schema_version: 2`
- camera shutter interval and frame time
- camera focal length or vertical FOV
- world units metadata
- per-frame bbox for water and secondary particles
- optional phase-field sampling stride
- secondary channel summary by type and age range

**Compatibility rule:**
- v1 manifests and JSONL frames must still validate and preview.
- v2-only fields must be optional in readers and required only when `--require-cinematic` is used.

**Acceptance gate:**
- doctest covers v2 writer output.
- validator accepts v1 by default.
- validator enforces v2 cinematic fields with `--require-cinematic`.
- preview renders both v1 and v2 manifests.

### S38: Cache-to-Render Conversion

**Goal:** Convert validated cache manifests into renderer-neutral assets without binding the simulator to a renderer.

**Files:**
- Create: `tools/convert_render_cache.py`
- Modify: `tools/validate_render_cache.py`
- Modify: `README.md`
- Create: `docs/superpowers/plans/2026-06-17-render-cache-conversion.md`

**Initial output format:**
- `frames/frame_000_particles.csv`
- `frames/frame_000_phase_cells.csv`
- `frames/frame_000_camera.json`
- `sequence.json`

**Command:**

```powershell
python tools\convert_render_cache.py build\large_scale3d_tp_v2_manifest.json build\cinematic_convert_smoke
python tools\validate_render_cache.py build\large_scale3d_tp_v2_manifest.json --require-cinematic
```

**Acceptance gate:**
- Converter rejects missing or invalid manifests with non-zero exit.
- Converter writes one output bundle per frame.
- Converted frame counts match manifest frame counts.
- `sequence.json` includes relative paths only, so the output directory is movable.

### S39: First Cinematic Preview Renderer

**Goal:** Produce a local PNG/GIF cinematic preview from a cache manifest without external DCC setup.

**Files:**
- Create: `tools/cinematic_render_stub.py`
- Create: `tools/assemble_frames.py`
- Modify: `README.md`
- Create: `docs/superpowers/plans/2026-06-17-first-cinematic-preview.md`

**Render behavior:**
- Load manifest or converted `sequence.json`.
- Project water phase cells as dense translucent depth layers.
- Draw secondary particles with size, color, and motion cue by type.
- Apply fixed cinematic camera framing from cache metadata.
- Output `frame_####.png`.
- Assemble `preview.gif` when Pillow is available.

**Command:**

```powershell
python tools\cinematic_render_stub.py build\large_scale3d_tp_v2_manifest.json build\cinematic_preview --frames 12 --width 1280 --height 720
python tools\assemble_frames.py build\cinematic_preview build\cinematic_preview.gif --fps 12
```

**Acceptance gate:**
- At least 12 nonblank PNG frames are produced.
- GIF exists or the tool prints a clear dependency message and leaves PNG frames.
- A simple pixel check confirms water or secondary pixels occupy more than 1 percent of each frame.

### S40: Secondary Spray/Foam Visual Channels

**Goal:** Move from generic secondary dots to inspectable spray, foam, and bubble render channels.

**Files:**
- Modify: `src/driver/secondary_particles3d.h`
- Modify: `src/driver/render_cache3d.h`
- Modify: `apps/export_render_cache3d.cpp`
- Modify: `tools/render_cache_preview.py`
- Modify: `tools/cinematic_render_stub.py`
- Modify: `tests/test_render_cache3d.cpp`
- Create: `docs/superpowers/plans/2026-06-17-secondary-render-channels.md`

**Channel rules:**
- Droplet: liquid escaped particle, gravity-driven, usually outside bulk water.
- Bubble: gas escaped particle, buoyancy-driven, usually inside or near liquid.
- Foam candidate: secondary or interface particle with age and speed criteria.

**Acceptance gate:**
- Cache stores channel counts per frame.
- Preview can isolate each channel.
- Validator catches negative counts, non-finite positions, and invalid channel names.

### S41: Water Surface or Volume Reconstruction

**Goal:** Export a water body representation that a renderer can shade as water, not as raw point dots.

**Files:**
- Create: `tools/reconstruct_water.py`
- Modify: `tools/convert_render_cache.py`
- Modify: `tools/cinematic_render_stub.py`
- Create: `docs/render_bridge_decision.md`
- Create: `docs/superpowers/plans/2026-06-17-water-reconstruction-export.md`

**First implementation path:**
- Build a coarse signed or density field from phase cells.
- Export either:
  - OBJ mesh per frame, or
  - dense volume slices per frame.
- Use the Water Representation Decision rule in this document.

**Acceptance gate:**
- Reconstruction command completes on at least 8 frames.
- Output asset count matches frame count.
- Preview shows a coherent water body, not only particles.
- A short decision note in `docs/render_bridge_decision.md` records mesh vs volume choice.

### S42: External Renderer Bridge

**Goal:** Produce the first renderer-backed cinematic frame sequence from converted cache assets.

**Files:**
- Create: `tools/render_bridge_blender.py` or `tools/render_bridge_usd.py`
- Modify: `tools/convert_render_cache.py`
- Modify: `README.md`
- Modify: `docs/render_bridge_decision.md`
- Create: `docs/superpowers/plans/2026-06-17-external-render-bridge.md`

**Bridge rule:**
- Prefer Blender if it can render a water mesh plus secondary particles from Python with documented setup.
- Prefer USD/OpenVDB only if Blender cannot represent the selected water asset cleanly.

**Acceptance gate:**
- One command creates at least 8 rendered PNG frames from a manifest or converted sequence.
- Frames are nonblank and camera framing is stable.
- The bridge has a documented dependency check command.
- The bridge can fail gracefully when the external renderer is not installed.

### S43: Cinematic Shot Pipeline Runner

**Goal:** Make a single orchestrated command generate sim cache, validate, convert, render, and assemble a preview movie.

**Files:**
- Create: `tools/run_cinematic_shot.py`
- Modify: `README.md`
- Create: `docs/superpowers/plans/2026-06-17-cinematic-shot-pipeline.md`

**Command:**

```powershell
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\shots\bubble_cinematic --frames 24 --width 1280 --height 720
```

**Acceptance gate:**
- Output directory contains `manifest.json`, validation report, converted assets, rendered frames, and preview GIF or MP4.
- The runner writes `shot_summary.json` with command lines, versions, elapsed times, and artifact paths.
- Re-running the command into a clean output directory produces the same frame count and schema.

### S44: Hyperreal Material and Lighting Pass

**Goal:** Add cinematic visual presets that separate simulation correctness from render look development.

**Files:**
- Modify: `tools/render_bridge_blender.py` or selected bridge
- Modify: `tools/run_cinematic_shot.py`
- Create: `configs/cinematic_presets.json`
- Create: `docs/superpowers/plans/2026-06-17-cinematic-render-presets.md`

**Preset fields:**
- camera path
- focal length or FOV
- shutter/motion blur setting
- sun or key light direction
- environment color
- water material parameters
- spray/foam material parameters
- tone mapping and exposure

**Acceptance gate:**
- At least two presets exist: `bubble_cinematic` and `dam_break_cinematic`.
- Renderer bridge can load a preset by name.
- Preview frames include water body, secondary particles, and stable exposure.

### S45: Large-Scale Cinematic Gate

**Goal:** Close the first end-to-end large-scale cinematic benchmark with evidence.

**Files:**
- Modify: `apps/bench_large_scale3d_tp.cpp`
- Modify: `tools/run_cinematic_shot.py`
- Modify: `README.md`
- Create: `docs/reports/cinematic_gate_s45.md`
- Create: `docs/superpowers/plans/2026-06-17-large-scale-cinematic-gate.md`

**Command:**

```powershell
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\shots\s45_bubble --frames 48 --width 1280 --height 720
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

**Acceptance gate:**
- Shot pipeline produces at least 48 rendered frames.
- `shot_summary.json` records simulation, cache, conversion, render, and assembly times.
- `docs/reports/cinematic_gate_s45.md` includes artifact paths, metrics summary, known limitations, and next recommended milestone.
- No slow cinematic render is added to default `ctest`.

## Verification Policy

Every milestone must run the smallest useful checks first:

1. Targeted unit tests or Python compile checks.
2. Release build of the touched executable or tool path.
3. A short smoke command that creates an inspectable artifact under `build/`.
4. `ctest --test-dir build -C Release --output-on-failure`.
5. `git diff --check`.

Use the existing `pwsh.exe` post-step warning policy: if MSBuild exit code is 0, the warning is not a failure.

## Commit Policy

Each milestone gets its own commit and push to `origin/main`.

Suggested commit sequence:

For this roadmap document:

```powershell
git add docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "docs: add cinematic hyperreal roadmap"
git push origin main
```

For S36:

```powershell
git add README.md apps\bench_large_scale3d_tp.cpp docs\superpowers\plans\2026-06-17-large-scale-benchmark-v2.md
git commit -m "test: extend large scale render benchmarks"
git push origin main
```

Do not combine renderer bridge decisions, simulation solver changes, and cache schema changes in one commit.

## Next Immediate Action

Continue with S194.

S183 is implemented and validated:

- S183 gate report:
  `docs/reports/cinematic_secondary_direct_visibility_gate_s183.md`
- S183 comparison report:
  `docs/reports/cinematic_secondary_direct_visibility_gate_comparison_s183.md`
- S183 plan:
  `docs/superpowers/plans/2026-06-19-secondary-direct-visibility-gate.md`
- S183 shot artifacts:
  `build/shots/s183_secondary_direct_visibility_gate`

S184 is published:

- Public gallery: `https://cove-grades-tba-tags.trycloudflare.com`
- S184 gallery report:
  `docs/reports/cinematic_secondary_direct_visibility_gate_gallery_s184.md`
- S184 publish report: `docs/reports/cinematic_gallery_publish_s184.md`
- S184 plan:
  `docs/superpowers/plans/2026-06-19-s183-gallery-publish.md`

S185 accepted S183:

- S185 triage report:
  `docs/reports/cinematic_public_gallery_triage_s185.md`
- S185 plan:
  `docs/superpowers/plans/2026-06-19-s183-public-gallery-triage.md`

S186 is implemented and validated:

- S186 gate report:
  `docs/reports/cinematic_water_surface_continuity_s186.md`
- S186 comparison report:
  `docs/reports/cinematic_water_surface_continuity_comparison_s186.md`
- S186 plan:
  `docs/superpowers/plans/2026-06-19-water-surface-continuity-stabilization.md`
- S186 shot artifacts:
  `build/shots/s186_water_surface_continuity_stabilized`

S187 is published:

- Public gallery:
  `https://prizes-inventory-plaintiff-violations.trycloudflare.com`
- S187 gallery report:
  `docs/reports/cinematic_water_surface_continuity_gallery_s187.md`
- S187 publish report: `docs/reports/cinematic_gallery_publish_s187.md`
- S187 plan:
  `docs/superpowers/plans/2026-06-19-s186-gallery-publish.md`

S188 accepted S186:

- S188 triage report:
  `docs/reports/cinematic_public_gallery_triage_s188.md`
- S188 plan:
  `docs/superpowers/plans/2026-06-19-s186-public-gallery-triage.md`

S189 is implemented and validated:

- S189 diagnostics report:
  `docs/reports/cinematic_surface_continuity_diagnostics_s189.md`
- S189 plan:
  `docs/superpowers/plans/2026-06-19-surface-reconstruction-continuity-diagnostics.md`
- S189 diagnostics outputs:
  `build/shots/s189_surface_continuity_diagnostics`

S190 is implemented and validated:

- S190 metric bridge report:
  `docs/reports/cinematic_surface_metric_bridge_s190.md`
- S190 plan:
  `docs/superpowers/plans/2026-06-19-surface-metric-bridge.md`
- S190 diagnostics outputs:
  `build/shots/s190_surface_metric_bridge_diagnostics`

S191 is implemented and validated:

- S191 gate report: `docs/reports/cinematic_water_mesh_smoothing_s191.md`
- S191 comparison report:
  `docs/reports/cinematic_water_mesh_smoothing_comparison_s191.md`
- S191 plan: `docs/superpowers/plans/2026-06-19-water-mesh-smoothing.md`
- S191 shot artifacts: `build/shots/s191_water_mesh_smoothing`

S192 is published:

- Public gallery: `https://emacs-bases-teens-health.trycloudflare.com`
- S192 gallery report:
  `docs/reports/cinematic_water_mesh_smoothing_gallery_s192.md`
- S192 publish report: `docs/reports/cinematic_gallery_publish_s192.md`
- S192 plan: `docs/superpowers/plans/2026-06-19-s191-gallery-publish.md`

S193 accepted S191:

- S193 triage report: `docs/reports/cinematic_public_gallery_triage_s193.md`
- S193 plan: `docs/superpowers/plans/2026-06-19-s191-public-gallery-triage.md`

S194 selected the stronger bounded smoothing probe:

- S194 report:
  `docs/reports/cinematic_smoothing_occlusion_probe_matrix_s194.md`
- S194 plan:
  `docs/superpowers/plans/2026-06-19-smoothing-occlusion-probe-matrix.md`
- Probe matrix:
  `build/shots/s194_smoothing_occlusion_probe_matrix/probe_matrix.png`

S195 should promote `dam_break_water_mesh_smoothing_strong_probe` into a
full-shot preset, render a 36-frame S191-vs-S195 comparison, and only publish it
if contrast/nonblank coverage stay inside the S194 gate.

S195 rendered the stronger smoothing full-shot candidate:

- S195 comparison report:
  `docs/reports/cinematic_water_mesh_smoothing_strong_comparison_s195.md`
- S195 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-smoothing-strong-fullshot.md`
- S195 artifacts:
  `build/shots/s195_water_mesh_smoothing_strong`

S196 should package and publish the S195 gallery for visual review. The numeric
gate is mixed: S195 preserves the S186 minimum contrast floor and nonblank
coverage, but it is 5 contrast points below S191, so replacement needs visual
confirmation.

S196 published the S195 gallery:

- Public gallery:
  `https://dicke-automotive-fitness-category.trycloudflare.com`
- S196 gallery report:
  `docs/reports/cinematic_water_mesh_smoothing_strong_gallery_s196.md`
- S196 publish report: `docs/reports/cinematic_gallery_publish_s196.md`
- S196 plan:
  `docs/superpowers/plans/2026-06-19-s195-gallery-publish.md`

S197 should triage the public S195 gallery against S191 and decide whether to
accept S195 or keep S191 while shifting the next pass toward
reconstruction/export smoothing.

S197 kept S191 as the accepted baseline:

- S197 triage report:
  `docs/reports/cinematic_public_gallery_triage_s197.md`
- S197 plan:
  `docs/superpowers/plans/2026-06-19-s195-public-gallery-triage.md`
- S197 review sheet:
  `build/shots/s197_s195_public_triage/review_comparison/comparison_sheet.png`

S198 should start a reconstruction/export smoothing pass. Renderer-side
smoothing now has diminishing returns; the next visible gain should come from
better water surface data or exported continuity/normal cues.

S198 added OBJ-level water mesh quality diagnostics:

- S198 report:
  `docs/reports/cinematic_water_mesh_quality_diagnostics_s198.md`
- S198 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-quality-diagnostics.md`
- S198 diagnostic outputs:
  `build/shots/s198_water_mesh_quality_diagnostics`

S199 should add reconstruction component metadata and an optional small-island
filter/labeling path. S198 shows the current exported OBJ topology is closed and
non-degenerate, but early frames split into two substantial components, so the
next useful work is component/island handling rather than stronger renderer
smoothing.

S199 added reconstruction component metadata and an opt-in island filter:

- S199 report:
  `docs/reports/cinematic_water_mesh_component_metadata_s199.md`
- S199 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-component-metadata.md`
- S199 probes:
  `build/shots/s199_component_metadata_probe`
  `build/shots/s199_component_filter_probe`

S200 should run a conservative visual island-filter probe and compare it
against S191. The S199 `0.3` filter proves the mechanism but is too aggressive
for production until visual review confirms the smaller component is an
artifact rather than meaningful separated water.

S200 ran a conservative island-filter visual probe:

- S200 mesh quality report:
  `docs/reports/cinematic_water_mesh_island_filter_quality_s200.md`
- S200 comparison report:
  `docs/reports/cinematic_water_mesh_island_filter_comparison_s200.md`
- S200 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-island-filter-probe.md`
- S200 artifacts:
  `build/shots/s200_island_filter_probe`

S200 should not replace S191. The filter removes 22656 faces and makes all
reconstruction frames single-component, but the 8-frame S191/S200 render probe
is pixel-identical. S201 should add component visibility or labeling diagnostics
before further filtering.

S201 explained the pixel-identical S200 probe:

- S201 report:
  `docs/reports/cinematic_water_mesh_component_visibility_s201.md`
- S201 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-component-visibility.md`
- S201 diagnostics:
  `build/shots/s201_component_visibility_diagnostics`

S201 shows the S200 render selected mesh frames `[13, 16, 19, 22, 26, 29, 32,
35]`, none of which contain components below the `0.24` filter threshold. S202
should build an earlier-window component-label probe targeting the frames where
the secondary component actually exists.

S202 rendered the early window where the filtered component is visible:

- S202 comparison report:
  `docs/reports/cinematic_water_mesh_island_filter_early_comparison_s202.md`
- S202 visibility report:
  `docs/reports/cinematic_water_mesh_component_visibility_s202.md`
- S202 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-island-filter-early-window.md`
- S202 artifacts:
  `build/shots/s202_island_filter_early_probe`

S202 should not promote island pruning. The removed component is visible and
large enough to look like part of the early water mass. S203 should add a
component label/overlay diagnostic so component 2 can be classified before any
pruning threshold becomes production behavior.

S203 added component overlay diagnostics:

- S203 report:
  `docs/reports/cinematic_water_mesh_component_overlay_s203.md`
- S203 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-component-overlay.md`
- S203 overlay sheet:
  `build/shots/s203_component_overlay/component_overlay_sheet.png`

S203 shows component 2 is a broad visible upper/back water mass, not a tiny
detached island. Do not promote face-ratio pruning. S204 should test
component-aware render treatment instead: preserve component 2, but tune its
depth/material contribution if it hurts readability.

S204 added an opt-in component-aware material treatment:

- S204 comparison report:
  `docs/reports/cinematic_water_mesh_component_material_comparison_s204.md`
- S204 overlay report:
  `docs/reports/cinematic_water_mesh_component_material_overlay_s204.md`
- S204 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-component-material-treatment.md`
- S204 artifacts:
  `build/shots/s204_component_material_probe`

S204 is safer than pruning because it preserves the visible secondary water
component, but it should not replace S191. The 8-frame early-window probe has a
very small mean changed ratio (`0.000341796875`), no strong changed pixels, and
a `-2` minimum-contrast delta. S205 should pivot toward exported surface-quality
data: water mesh continuity/normal metadata, depth/phase surface attributes, or
a no-regression gate proving component treatment is inactive on the accepted
S191 window before investing further in component-specific material tuning.

S205 added metadata-only water mesh surface-quality annotation:

- S205 report:
  `docs/reports/cinematic_water_mesh_surface_quality_annotation_s205.md`
- S205 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-surface-quality-annotation.md`
- S205 annotated reconstruction:
  `build/shots/s205_surface_quality_annotation/water_reconstruction.json`
- S205 converted sequence probe:
  `build/shots/s205_surface_quality_annotation/converted/sequence.json`

S205 labels the 36-frame reconstruction as `component_fragmented: 5`,
`normal_rough: 3`, and `stable: 28`, then verifies that all 56 converted render
frames carry `water_mesh_surface_quality`. S206 should use this metadata in a
renderer no-op/QA gate first: prove the accepted S191 source window is mostly
stable, then selectively attach normal/continuity shading or component material
treatment only on labeled frames.

S206 added the surface-quality render-window gate:

- S206 report:
  `docs/reports/cinematic_water_mesh_surface_quality_gate_s206.md`
- S206 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-surface-quality-gate.md`
- S206 gate artifacts:
  `build/shots/s206_surface_quality_gate`

S206 proves the accepted S191 window is stable-only: all 36 S191 render frames
map to `stable`, stable ratio is `1.0`, blocked labels are `0`, and component
treatment is a no-op. A dry-run with the S205 annotated sequence also confirms
`render_bridge_blender.py` now preserves `water_mesh_surface_quality` in both
scene specs and bridge summaries. S207 can add label-driven render treatment,
but it must keep the S206 no-op gate passing for the accepted S191 window.

S207 added label-gated component material treatment:

- S207 report:
  `docs/reports/cinematic_water_mesh_component_labeled_treatment_s207.md`
- S207 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-component-labeled-treatment.md`
- S207 artifacts:
  `build/shots/s207_component_material_labeled_probe`

S207 adds `quality_labels` to `water_mesh_component_material_pass` and the
`dam_break_water_component_material_labeled_probe` preset. The accepted S191
window remains no-op (`stable: 4`, gate passed), while the early window selects
`component_fragmented` frames for the softer component material. A 2-frame
Blender smoke render passed on the early fragmented window. S208 should add an
equally conservative label-gated path for `normal_rough` frames, keeping the
S206/S207 accepted-window gates passing.

S208 added label-gated normal-rough water material treatment:

- S208 report:
  `docs/reports/cinematic_water_mesh_normal_rough_labeled_treatment_s208.md`
- S208 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-normal-rough-labeled-treatment.md`
- S208 artifacts:
  `build/shots/s208_normal_rough_labeled_probe`

S208 introduces `water_mesh_quality_material_pass` and the
`dam_break_water_normal_rough_labeled_probe` preset. The accepted S191 window
still gates as `stable: 4`, while the targeted source index `8..11` window
selects `normal_rough: 4` in dry-run and `normal_rough: 2` in a Blender smoke
render. S209 should compare S208 against an untreated normal-rough window before
any baseline promotion.

S209 compared untreated vs S208-treated normal-rough frames:

- S209 report:
  `docs/reports/cinematic_water_mesh_normal_rough_comparison_s209.md`
- S209 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-normal-rough-comparison.md`
- S209 artifacts:
  `build/shots/s209_normal_rough_comparison`

S209 is mixed but safe: treated minimum contrast improves by `4`, mean
luminance rises by `0.18618055555555202`, and nonblank coverage is unchanged,
but bright/highlight ratios drop and the visual delta is small. Keep S208 as an
opt-in treatment for now. S210 should either run a wider normal-rough comparison
or tune a less highlight-suppressing variant.

S210 added and compared a softer-highlight normal-rough variant:

- S210 untreated comparison report:
  `docs/reports/cinematic_water_mesh_normal_rough_soft_highlight_comparison_s210.md`
- S210 S208 comparison report:
  `docs/reports/cinematic_water_mesh_normal_rough_s208_s210_comparison.md`
- S210 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-normal-rough-soft-highlight.md`
- S210 artifacts:
  `build/shots/s210_normal_rough_soft_highlight`

S210 keeps the accepted S191 window no-op (`stable: 4`, gate passed). Against
untreated normal-rough frames it improves minimum contrast by `5` with unchanged
nonblank coverage, but still suppresses bright/highlight ratios. Against S208 it
improves minimum contrast by `1` and slightly restores bright ratio while
leaving highlight ratio unchanged. Prefer S210 over S208 as the opt-in
normal-rough candidate, but keep baseline promotion blocked until a wider
keyframe or gallery review.

S211 ran the wider S210 normal-rough keyframe review:

- S211 report:
  `docs/reports/cinematic_water_mesh_normal_rough_keyframe_review_s211.md`
- S211 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-normal-rough-keyframe-review.md`
- S211 artifacts:
  `build/shots/s211_normal_rough_keyframe_review`

S211 rejects S210 for baseline promotion. The 4-frame 640x360 review preserves
nonblank coverage, but minimum contrast drops by `8` and bright/highlight ratios
drop. The next `normal_rough` pass should stop suppressing water material and
instead test label-gated mesh smoothing or normal-continuity treatment.

S212 added label-gated normal-rough mesh smoothing:

- S212 untreated comparison report:
  `docs/reports/cinematic_water_mesh_normal_rough_smoothing_comparison_s212.md`
- S212 S210 comparison report:
  `docs/reports/cinematic_water_mesh_normal_rough_s210_s212_comparison.md`
- S212 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-normal-rough-smoothing.md`
- S212 artifacts:
  `build/shots/s212_normal_rough_smoothing`

S212 is the preferred `normal_rough` route. It keeps the accepted S191 window
stable-only/no-op, then improves the 4-frame normal-rough review by `+45`
minimum contrast against untreated while preserving nonblank coverage and
bright/highlight energy much better than S210. S213 should package a small
visual review artifact and decide whether to fold the label-gated smoothing pass
into the main accepted render preset.

S213 packaged the normal-rough smoothing review and folded it into the accepted
water mesh smoothing preset:

- S213 gallery report:
  `docs/reports/cinematic_water_mesh_normal_rough_smoothing_gallery_s213.md`
- S213 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-normal-rough-review-gallery.md`
- S213 gallery:
  `build/shots/s213_normal_rough_review/gallery/index.html`

S213 adds `water_mesh_quality_smoothing_pass` to
`dam_break_water_mesh_smoothing`, gated to `normal_rough` labels with
`factor: 0.04` and `iterations: 1`. The accepted preset stable dry-run still
gates as `stable: 4` with stable ratio `1.0`, while the targeted normal-rough
dry-run selects `normal_rough: 4`. S214 should run a mixed-window accepted-preset
visual review so stable and normal-rough frames are checked together before the
next cinematic treatment.

S214 validated the accepted preset over a mixed `normal_rough`/`stable` window:

- S214 comparison report:
  `docs/reports/cinematic_water_mesh_mixed_window_accepted_preset_s214.md`
- S214 gallery report:
  `docs/reports/cinematic_water_mesh_mixed_window_gallery_s214.md`
- S214 plan:
  `docs/superpowers/plans/2026-06-19-water-mesh-mixed-window-accepted-preset.md`
- S214 gallery:
  `build/shots/s214_mixed_window_accepted_preset/gallery/index.html`

S214 uses source indices `8..55`, which route to `normal_rough: 1` and
`stable: 7` at 8 review frames. The mixed gate passed, the accepted render and
no-quality-smoothing baseline both completed, and the comparison preserves
nonblank coverage, minimum contrast, and highlight ratio with only tiny
luminance/bright-ratio deltas. The S213 fold can stay in the accepted preset.
Next work can leave mesh-quality gating and move back to broader cinematic
quality passes, or publish the S214 gallery if remote visual review is needed.

S216 added a depth/reflection probe on top of the accepted mixed-window preset:

- S216 comparison report:
  `docs/reports/cinematic_water_depth_reflection_probe_s216.md`
- S216 gallery report:
  `docs/reports/cinematic_water_depth_reflection_gallery_s216.md`
- S216 plan:
  `docs/superpowers/plans/2026-06-19-water-depth-reflection-probe.md`
- S216 gallery:
  `build/shots/s216_depth_reflection_probe/gallery/index.html`

S216 introduces `dam_break_water_mesh_depth_reflection_probe` as an opt-in
preset. It keeps accepted mesh smoothing and label-gated `normal_rough`
smoothing, while slightly deepening the water material, reducing reflection
ribbon density, and increasing volume/scatter depth. The mixed gate passed with
`normal_rough: 1` and `stable: 7`, and the render completed, but the comparison
against S214 drops minimum contrast by `-8.0` and mean luminance by
`-0.7349235026041754` despite higher bright/highlight ratios. Do not promote
S216 yet. S217 should tune this probe to recover contrast while preserving the
useful highlight increase.

S217 tested a contrast-preserving depth/reflection tune:

- S217 S214 comparison report:
  `docs/reports/cinematic_water_depth_reflection_contrast_probe_s217.md`
- S217 S216 comparison report:
  `docs/reports/cinematic_water_depth_reflection_s216_s217_comparison.md`
- S217 gallery report:
  `docs/reports/cinematic_water_depth_reflection_contrast_gallery_s217.md`
- S217 plan:
  `docs/superpowers/plans/2026-06-19-water-depth-reflection-contrast-probe.md`
- S217 gallery:
  `build/shots/s217_depth_reflection_contrast_probe/gallery/index.html`

S217 introduces `dam_break_water_mesh_depth_reflection_contrast_probe`, but it is
not a promotion candidate. It recovers some luminance compared with S216
(`+0.4082052951388988`) and preserves coverage, but against S214 the minimum
contrast delta is `-13.0`, worse than S216's `-8.0`. S218 should stop changing
the accepted water material and isolate reflection/glint overlay tuning only.

S218 isolated reflection/glint overlay tuning:

- S218 comparison report:
  `docs/reports/cinematic_water_overlay_highlight_probe_s218.md`
- S218 gallery report:
  `docs/reports/cinematic_water_overlay_highlight_gallery_s218.md`
- S218 plan:
  `docs/superpowers/plans/2026-06-19-water-overlay-highlight-probe.md`
- S218 gallery:
  `build/shots/s218_overlay_highlight_probe/gallery/index.html`

S218 introduces `dam_break_water_mesh_overlay_highlight_probe`. It keeps the
accepted water material, volume scattering, water surface detail, mesh smoothing,
and label-gated `normal_rough` smoothing unchanged, then tunes only glint and
reflection overlay controls. The mixed gate passed with `normal_rough: 1` and
`stable: 7`. Against S214 accepted, nonblank coverage, minimum contrast,
bright ratio, and highlight ratio are unchanged, while mean luminance improves
by `0.1124663628472149`. S218 is the current safe overlay-highlight promotion
candidate; S219 should either fold it into the accepted preset or A/B one
slightly stronger overlay-only variant first.

S219 A/B tested a stronger overlay-only candidate:

- S219 S214 comparison report:
  `docs/reports/cinematic_water_overlay_highlight_strong_probe_s219.md`
- S219 S218 comparison report:
  `docs/reports/cinematic_water_overlay_highlight_s218_s219_comparison.md`
- S219 gallery report:
  `docs/reports/cinematic_water_overlay_highlight_strong_gallery_s219.md`
- S219 plan:
  `docs/superpowers/plans/2026-06-19-water-overlay-highlight-strong-probe.md`
- S219 gallery:
  `build/shots/s219_overlay_highlight_strong_probe/gallery/index.html`

S219 introduces `dam_break_water_mesh_overlay_highlight_strong_probe`, still
changing only glint/reflection overlay controls. It improves mean luminance by
`0.43489746093749204` against S214 and by `0.32243109809027715` against S218,
while preserving nonblank coverage, minimum contrast, and mean highlight ratio.
S219 is the preferred overlay-only promotion candidate. S220 should fold these
overlay controls into `dam_break_water_mesh_smoothing` and rerun the accepted
mixed-window gate/render comparison.

S220 promoted the S219 overlay-only controls into the accepted water mesh
smoothing preset:

- S220 acceptance report:
  `docs/reports/cinematic_water_overlay_highlight_acceptance_s220.md`
- S220 S219 parity report:
  `docs/reports/cinematic_water_overlay_highlight_s219_s220_parity.md`
- S220 gallery report:
  `docs/reports/cinematic_water_overlay_highlight_acceptance_gallery_s220.md`
- S220 plan:
  `docs/superpowers/plans/2026-06-19-water-overlay-highlight-acceptance.md`
- S220 gallery:
  `build/shots/s220_accepted_overlay_highlight/gallery/index.html`

S220 adds the S219 `water_surface_glint_pass` and `water_reflection_pass`
overrides directly to `dam_break_water_mesh_smoothing`. The mixed gate passed
with `normal_rough: 1` and `stable: 7`. Against S214 accepted, S220 preserves
nonblank coverage, minimum contrast, and mean highlight ratio while improving
mean luminance by `0.43489312065972285`. Against S219, parity holds within render
noise (`-4.340277769188106e-06` mean luminance delta, all other aggregate deltas
`0.0`). Use S220 as the accepted baseline for the next visual pass. A practical
next target is secondary particle readability without increasing direct particle
clutter.

S221 tested secondary readability without increasing direct secondary particles:

- S221 comparison report:
  `docs/reports/cinematic_secondary_readability_probe_s221.md`
- S221 gallery report:
  `docs/reports/cinematic_secondary_readability_gallery_s221.md`
- S221 plan:
  `docs/superpowers/plans/2026-06-19-secondary-readability-probe.md`
- S221 gallery:
  `build/shots/s221_secondary_readability_probe/gallery/index.html`

S221 introduces `dam_break_secondary_readability_probe`, leaving
`secondary_direct_pass` unchanged while strengthening only `secondary_soft_pass`
and `secondary_streak_pass`. The mixed gate passed and direct secondary counts
match S220 on all 8 review frames. Against S220, contrast, coverage, bright
ratio, and highlight ratio remain unchanged while mean luminance rises by
`0.0604996744791606`. S221 is safe but visually subtle; keep it as opt-in and
run a stronger soft/streak-only A/B before promotion.

S222 A/B tested a stronger secondary readability candidate:

- S222 S220 comparison report:
  `docs/reports/cinematic_secondary_readability_strong_probe_s222.md`
- S222 S221 comparison report:
  `docs/reports/cinematic_secondary_readability_s221_s222_comparison.md`
- S222 gallery report:
  `docs/reports/cinematic_secondary_readability_strong_gallery_s222.md`
- S222 plan:
  `docs/superpowers/plans/2026-06-19-secondary-readability-strong-probe.md`
- S222 gallery:
  `build/shots/s222_secondary_readability_strong_probe/gallery/index.html`

S222 introduces `dam_break_secondary_readability_strong_probe`, still leaving
`secondary_direct_pass` unchanged and tuning only soft mist/streak rendering.
The mixed gate passed and direct secondary counts match S220/S221 on all review
frames. Against S220, S222 preserves coverage, minimum contrast, bright ratio,
and highlight ratio while improving mean luminance by `0.17864746093749773`.
Against S221, it adds another `0.11814778645833712` mean luminance with the same
bounded metrics. Prefer S222 as the secondary readability promotion candidate;
S223 should fold it into the accepted preset and revalidate.

S223 promoted the S222 secondary readability settings into the accepted water
mesh smoothing preset:

- S223 acceptance report:
  `docs/reports/cinematic_secondary_readability_acceptance_s223.md`
- S223 S222 parity report:
  `docs/reports/cinematic_secondary_readability_s222_s223_parity.md`
- S223 gallery report:
  `docs/reports/cinematic_secondary_readability_acceptance_gallery_s223.md`
- S223 plan:
  `docs/superpowers/plans/2026-06-19-secondary-readability-acceptance.md`
- S223 gallery:
  `build/shots/s223_accepted_secondary_readability/gallery/index.html`

S223 adds the S222 `secondary_soft_pass` and `secondary_streak_pass` overrides
directly to `dam_break_water_mesh_smoothing`, while leaving direct secondary
thinning unchanged. The mixed gate passed with `normal_rough: 1` and `stable: 7`.
Against S220, S223 preserves coverage, minimum contrast, bright ratio, and
highlight ratio while improving mean luminance by `0.17866536458332405`.
Against S222, parity holds within render noise (`1.7903645826322645e-05` mean
luminance delta, all other aggregate deltas `0.0`). Use S223 as the accepted
baseline for a wider-window review or external gallery publish.

S224 validated the accepted S223 preset over a wider mixed window:

- S224 comparison report:
  `docs/reports/cinematic_wide_accepted_review_s224.md`
- S224 gallery report:
  `docs/reports/cinematic_wide_accepted_review_gallery_s224.md`
- S224 plan:
  `docs/superpowers/plans/2026-06-19-wide-accepted-preset-review.md`
- S224 gallery:
  `build/shots/s224_wide_accepted_review/gallery/index.html`

S224 uses source indices `8..55` as a 16-frame accepted review, producing
`normal_rough: 2` and `stable: 14` with blocked labels `0` and stable ratio
`0.875`. Against the S220-wide baseline, S224 preserves nonblank coverage,
minimum contrast, and direct secondary counts on all 16 frames while improving
mean luminance by `0.19168701171875568`. Keep S223 as the accepted baseline.
The next practical choices are publishing the S224 gallery for remote review or
running the next visual pass against this wider accepted proof.

S225 published the S224 accepted wide-window gallery through a verified
Cloudflare quick tunnel:

- S225 publish report:
  `docs/reports/cinematic_gallery_publish_s225.md`
- Public URL:
  `https://acdbentity-greetings-reflects-win.trycloudflare.com`
- Publish manifest:
  `build/shots/s224_wide_accepted_review/gallery_publish_s225_manifest.json`

S225 verified HTTP `200` for the public `index.html`, `shot.gif`,
`comparison.png`, and `keyframe_00.png`. The published file sizes match the
S224 gallery assets, avoiding the stale-port collision that can occur when old
local gallery servers are still listening. Next visual work should use S224 as
the accepted baseline rather than opening another publish tunnel by default.

S226 hardened the gallery publisher after the S225 stale-port/stale-log issue:

- S226 report:
  `docs/reports/cinematic_gallery_publish_tool_hardening_s226.md`
- S226 plan:
  `docs/superpowers/plans/2026-06-19-gallery-publish-tool-hardening.md`

`tools/publish_cinematic_gallery.py` now truncates per-run process logs and
avoids `SO_REUSEADDR` on Windows during port probing, so stale trycloudflare
URLs and duplicate local listeners do not poison future publish checks. The
inline regression smoke passed, and an actual local publish smoke skipped the
occupied S225 port `18899` and selected `18900`. Continue visual work from the
S224 accepted baseline; do not open another tunnel unless a fresh share URL is
needed.

S227 validated the accepted preset over a longer 32-frame motion window:

- S227 comparison report:
  `docs/reports/cinematic_accepted_motion_window_s227.md`
- S227 gallery report:
  `docs/reports/cinematic_accepted_motion_window_gallery_s227.md`
- S227 plan:
  `docs/superpowers/plans/2026-06-19-accepted-motion-window-review.md`
- S227 gallery:
  `build/shots/s227_accepted_motion_window/gallery/index.html`

S227 uses the same source indices `8..55` but increases review density to
32 frames. The surface-quality gate passed with `normal_rough: 3`,
`stable: 29`, stable ratio `0.90625`, and blocked labels `0`. Against the
S220-motion baseline, S227 preserves nonblank coverage, minimum contrast, and
direct secondary counts on all 32 frames while improving mean luminance by
`0.20133558485242986`. Use S227 as the accepted motion proof before the next
actual visual improvement pass.

S228 added a foreground water-volume separation probe:

- S228 comparison report:
  `docs/reports/cinematic_foreground_volume_separation_probe_s228.md`
- S228 gallery report:
  `docs/reports/cinematic_foreground_volume_separation_gallery_s228.md`
- S228 plan:
  `docs/superpowers/plans/2026-06-19-foreground-volume-separation-probe.md`
- S228 gallery:
  `build/shots/s228_foreground_volume_separation_probe/gallery/index.html`

S228 introduces `dam_break_foreground_volume_separation_probe`, inheriting from
the accepted water mesh smoothing preset and changing only bounded rim,
metadata-emission, and water-volume scattering controls. Against S224 accepted,
S228 preserves coverage, minimum contrast, and direct secondary counts on all
16 frames while increasing mean luminance by `0.6793684895833394`. Bright and
highlight ratios drop slightly (`-6.510416666666654e-06` and
`-3.2552083333333407e-06`), so S228 should remain a promotion candidate until
S229 runs the same probe over the 32-frame motion window.

S229 validated the S228 foreground-volume probe over the 32-frame motion window:

- S229 comparison report:
  `docs/reports/cinematic_foreground_volume_motion_review_s229.md`
- S229 gallery report:
  `docs/reports/cinematic_foreground_volume_motion_gallery_s229.md`
- S229 plan:
  `docs/superpowers/plans/2026-06-19-foreground-volume-motion-review.md`
- S229 gallery:
  `build/shots/s229_foreground_volume_motion_review/gallery/index.html`

Against S227 accepted motion, S229 preserves nonblank coverage, minimum
contrast, and direct secondary counts on all 32 frames while increasing mean
luminance by `0.6768454318576431`. Bright and highlight ratios drop only
slightly (`-5.56098090277778e-06` and `-2.8483072916666647e-06`). Promote the
S228 foreground-volume settings in S230, then run accepted-preset parity against
S229.

S230 promoted the foreground-volume settings into the accepted preset:

- S230 acceptance report:
  `docs/reports/cinematic_foreground_volume_acceptance_s230.md`
- S230 gallery report:
  `docs/reports/cinematic_foreground_volume_acceptance_gallery_s230.md`
- S230 plan:
  `docs/superpowers/plans/2026-06-19-foreground-volume-acceptance.md`
- S230 gallery:
  `build/shots/s230_foreground_volume_acceptance/gallery/index.html`

S230 folds the S228/S229 rim, metadata-emission, and water-volume scattering
settings into `dam_break_water_mesh_smoothing`. The 32-frame accepted render
passes the surface-quality gate with `normal_rough: 3`, `stable: 29`, stable
ratio `0.90625`, and blocked labels `0`. Against S229, parity holds within
render noise: mean luminance delta is `-1.2207031261368684e-06`, all other
aggregate deltas are `0.0`, and direct secondary counts match on all 32 frames.
Use S230 as the accepted foreground-volume baseline.

S231 tested overlay-only highlight recovery after S230:

- S231 comparison report:
  `docs/reports/cinematic_highlight_energy_recovery_probe_s231.md`
- S231 gallery report:
  `docs/reports/cinematic_highlight_energy_recovery_gallery_s231.md`
- S231 plan:
  `docs/superpowers/plans/2026-06-19-highlight-energy-recovery-probe.md`
- S231 gallery:
  `build/shots/s231_highlight_energy_recovery_probe/gallery/index.html`

S231 introduces `dam_break_highlight_energy_recovery_probe`, changing only
glint/reflection overlay controls. It is safe but insufficient: the 16-frame
gate passes with `normal_rough: 2`, `stable: 14`, direct secondary counts match
on all frames, nonblank coverage and minimum contrast are preserved, and mean
luminance rises by `0.1705642361111046`, but bright/highlight ratio deltas are
both `0.0`. Keep S231 opt-in and run a stronger S232 overlay-only candidate
before any promotion.

S232 tested a stronger overlay-only highlight recovery candidate:

- S232 comparison report:
  `docs/reports/cinematic_highlight_energy_recovery_strong_probe_s232.md`
- S232 gallery report:
  `docs/reports/cinematic_highlight_energy_recovery_strong_gallery_s232.md`
- S232 plan:
  `docs/superpowers/plans/2026-06-19-highlight-energy-recovery-strong-probe.md`
- S232 gallery:
  `build/shots/s232_highlight_energy_recovery_strong_probe/gallery/index.html`

S232 introduces `dam_break_highlight_energy_recovery_strong_probe`, still
changing only glint/reflection overlay controls. Against the S230-equivalent
accepted 16-frame baseline, the surface-quality gate passes with
`normal_rough: 2`, `stable: 14`, stable ratio `0.875`, and blocked labels `0`.
Direct secondary counts match on all 16 frames, nonblank coverage and minimum
contrast are preserved, mean luminance rises by `0.6406933593749926`, and
bright ratio improves by `7.324218749999979e-06`. Highlight ratio remains
unchanged at `0.0` delta, so keep S232 opt-in and use S233 for a 32-frame motion
review only if the stronger overlay looks acceptable in the gallery.

S233 validated S232 over the 32-frame accepted motion window:

- S233 comparison report:
  `docs/reports/cinematic_highlight_energy_motion_review_s233.md`
- S233 gallery report:
  `docs/reports/cinematic_highlight_energy_motion_gallery_s233.md`
- S233 plan:
  `docs/superpowers/plans/2026-06-19-highlight-energy-motion-review.md`
- S233 gallery:
  `build/shots/s233_highlight_energy_motion_review/gallery/index.html`

Against S230 accepted foreground-volume, S233 passes the surface-quality gate
with `normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. Direct secondary counts match on all 32 frames, nonblank coverage is
preserved, minimum contrast rises by `9.0`, mean luminance rises by
`0.656890869140625`, and bright ratio improves by
`4.475911458333328e-06`. Highlight ratio still slips slightly by
`-4.069010416666625e-07`, so keep the strong highlight probe opt-in. S234 should
target highlight shape/threshold behavior instead of adding more broad overlay
energy.

S234 tested tighter overlay highlight shape/threshold behavior:

- S234 comparison report:
  `docs/reports/cinematic_highlight_shape_threshold_probe_s234.md`
- S234 gallery report:
  `docs/reports/cinematic_highlight_shape_threshold_gallery_s234.md`
- S234 plan:
  `docs/superpowers/plans/2026-06-19-highlight-shape-threshold-probe.md`
- S234 gallery:
  `build/shots/s234_highlight_shape_threshold_probe/gallery/index.html`

S234 adds `dam_break_highlight_shape_threshold_probe`, changing only
glint/reflection overlay shape controls. It passes the 16-frame gate with
`normal_rough: 2`, `stable: 14`, stable ratio `0.875`, and blocked labels `0`.
Direct secondary counts match on all frames, nonblank coverage and minimum
contrast are preserved, mean luminance rises by `0.20324544270832234`, and
bright ratio improves by `2.441406249999975e-06`. Highlight ratio is still
unchanged at `0.0` delta. Do not promote S234 to motion review; overlay-only
strip tuning has likely reached the current aggregate metric ceiling, so the
next useful step is render-metric calibration or a real material/specular pass.

S235 added render-metric calibration for highlight tuning:

- S235 report:
  `docs/reports/cinematic_highlight_metric_calibration_s235.md`
- S235 plan:
  `docs/superpowers/plans/2026-06-19-highlight-metric-calibration.md`
- S235 calibration artifacts:
  `build/shots/s235_highlight_metric_calibration/`

S235 extends `tools/compare_cinematic_frames.py` with additive
`calibration_deltas` computed from rendered PNG pairs: `luma_p95`, `luma_p99`,
`luma_p995`, `upper_mid_ratio`, `near_highlight_ratio`, `specular_ratio`, and
pair-derived mean `contrast`. The new metrics show why the previous probes were
visually meaningful despite flat legacy `highlight_ratio`: S232 has `luma_p99`
delta `+8.375` and `luma_p995` delta `+9.8125`, and S233 has `luma_p99` delta
`+8.53125` and `luma_p995` delta `+9.875`. Hard near-highlight/specular ratios
remain flat or slightly negative, so the next useful step is S236
material/specular tuning or a water/glint contribution mask rather than more
overlay-only strip density.

S236 tested material/specular highlight response:

- S236 comparison report:
  `docs/reports/cinematic_highlight_material_response_probe_s236.md`
- S236 gallery report:
  `docs/reports/cinematic_highlight_material_response_gallery_s236.md`
- S236 plan:
  `docs/superpowers/plans/2026-06-19-highlight-material-response-probe.md`
- S236 gallery:
  `build/shots/s236_highlight_material_response_probe/gallery/index.html`

S236 adds `dam_break_highlight_material_response_probe`, keeping accepted overlay
density while raising `water_glint` and `water_reflection` material response. It
passes the 16-frame gate with `normal_rough: 2`, `stable: 14`, stable ratio
`0.875`, and blocked labels `0`. Direct secondary counts match on all frames,
nonblank coverage is preserved, mean luminance rises by `0.5723060438368037`,
minimum contrast rises by `6.0`, bright ratio improves by
`3.580729166666665e-05`, hard highlight ratio is non-negative at `0.0` delta,
and calibration deltas are strong (`luma_p99 +9.4375`, `luma_p995 +11.5`).
Promote S236 to S237 32-frame motion review before any accepted-preset change.

S237 validated S236 over the 32-frame accepted motion window:

- S237 comparison report:
  `docs/reports/cinematic_highlight_material_motion_review_s237.md`
- S237 gallery report:
  `docs/reports/cinematic_highlight_material_motion_gallery_s237.md`
- S237 plan:
  `docs/superpowers/plans/2026-06-19-highlight-material-motion-review.md`
- S237 gallery:
  `build/shots/s237_highlight_material_motion_review/gallery/index.html`

Against S230 accepted foreground-volume, S237 passes the surface-quality gate
with `normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. Direct secondary counts match on all 32 frames, nonblank coverage is
preserved, minimum contrast rises by `16.0`, mean luminance rises by
`0.571984456380207`, bright ratio improves by `2.943250868055555e-05`, hard
highlight ratio is non-negative at `0.0` delta, and calibration deltas remain
strong (`luma_p99 +9.40625`, `luma_p995 +11.4375`). Promote the S236 material
response into `dam_break_water_mesh_smoothing` in S238 and run accepted-preset
parity against S237.

S238 accepted the material highlight response:

- S238 acceptance report:
  `docs/reports/cinematic_highlight_material_acceptance_s238.md`
- S238 gallery report:
  `docs/reports/cinematic_highlight_material_acceptance_gallery_s238.md`
- S238 plan:
  `docs/superpowers/plans/2026-06-19-highlight-material-acceptance.md`
- S238 gallery:
  `build/shots/s238_highlight_material_acceptance/gallery/index.html`

S238 folds the S236/S237 `water_glint` and `water_reflection` material response
plus bounded pass scale updates into `dam_break_water_mesh_smoothing`. The
32-frame accepted render passes the surface-quality gate with `normal_rough: 3`,
`stable: 29`, stable ratio `0.90625`, and blocked labels `0`. Against S237,
parity holds within render noise: mean luminance delta is
`-5.018446174176461e-06`, and bright ratio, highlight ratio, nonblank ratio,
minimum contrast, calibration deltas, and direct secondary counts are unchanged.
Against S230 accepted foreground-volume, S238 preserves coverage and hard
highlight ratio while improving mean luminance by `0.5719794379340328`, minimum
contrast by `16.0`, bright ratio by `2.943250868055555e-05`, `luma_p99` by
`9.40625`, and `luma_p995` by `11.4375`. Use S238 as the current accepted
cinematic water baseline.

S239 added highlight contribution diagnostics:

- S239 report:
  `docs/reports/cinematic_highlight_contribution_diagnostics_s239.md`
- S239 plan:
  `docs/superpowers/plans/2026-06-19-highlight-contribution-diagnostics.md`
- S239 diagnostic sheet:
  `build/shots/s239_highlight_contribution_diagnostics/diagnostic_sheet.png`
- S239 masks:
  `build/shots/s239_highlight_contribution_diagnostics/masks/`

S239 adds `tools/highlight_contribution_diagnostics.py`, an image-space
upper-tail gain/loss mask tool. Comparing S230 accepted foreground-volume
against S238 accepted highlight-material over 32 frames gives aggregate gain
ratio `0.031143391927083333`, loss ratio `0.0`, net gain ratio
`0.031143391927083333`, mean gain luma delta `12.647490145835157`, and strongest
gain luma delta `25`. The diagnostic sheet shows the accepted highlight change
adds upper-tail energy in the intended glint/reflection regions without
measurable upper-tail loss. S240 should move to a non-highlight visual pass,
such as water/foam readability or contribution-mask rendering, rather than more
broad highlight recovery.

S240 tested foam/readability tuning on top of S238:

- S240 comparison report:
  `docs/reports/cinematic_foam_readability_probe_s240.md`
- S240 gallery report:
  `docs/reports/cinematic_foam_readability_gallery_s240.md`
- S240 plan:
  `docs/superpowers/plans/2026-06-19-foam-readability-probe.md`
- S240 gallery:
  `build/shots/s240_foam_readability_probe/gallery/index.html`

S240 adds `dam_break_foam_readability_probe`, changing bounded contact foam,
impact ripple, secondary soft, and secondary streak render controls while
leaving direct secondary particles unchanged. Against a matched S238 accepted
16-frame baseline, the surface-quality gate passes with `normal_rough: 2`,
`stable: 14`, stable ratio `0.875`, and blocked labels `0`. Direct secondary
counts match on all frames. Contact foam mean count rises from `42.75` to
`52.4375`, impact ripple mean count rises from `62.0` to `73.0`, mean luminance
rises by `0.15290771484374943`, bright ratio improves by
`2.170138888888903e-06`, coverage/minimum contrast/hard highlight ratio are
preserved, and calibration `luma_p99` rises by `0.3125`. Promote S240 to S241
32-frame motion review before any accepted-preset change.

S241 validated S240 over the 32-frame accepted motion window:

- S241 comparison report:
  `docs/reports/cinematic_foam_readability_motion_review_s241.md`
- S241 gallery report:
  `docs/reports/cinematic_foam_readability_motion_gallery_s241.md`
- S241 plan:
  `docs/superpowers/plans/2026-06-19-foam-readability-motion-review.md`
- S241 gallery:
  `build/shots/s241_foam_readability_motion_review/gallery/index.html`

Against S238 accepted highlight-material, S241 passes the surface-quality gate
with `normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. Direct secondary counts match on all 32 frames. Contact foam mean count
rises from `43.1875` to `54.5625`, impact ripple mean count rises from `62.0`
to `73.0`, mean luminance rises by `0.16201470269096774`, bright ratio improves
by `2.3057725694444525e-06`, coverage/minimum contrast/hard highlight ratio are
preserved, and calibration `luma_p99` rises by `0.1875`. The tiny negative
upper-mid/specular deltas are below practical significance for this foam-focused
pass. Promote S240 into `dam_break_water_mesh_smoothing` in S242 and run parity
against S241.

S242 accepted the foam/readability tuning:

- S242 acceptance report:
  `docs/reports/cinematic_foam_readability_acceptance_s242.md`
- S242 baseline delta report:
  `docs/reports/cinematic_foam_readability_acceptance_baseline_delta_s242.md`
- S242 gallery report:
  `docs/reports/cinematic_foam_readability_acceptance_gallery_s242.md`
- S242 plan:
  `docs/superpowers/plans/2026-06-19-foam-readability-acceptance.md`
- S242 gallery:
  `build/shots/s242_foam_readability_acceptance/gallery/index.html`

S242 folds the S240/S241 contact foam, impact ripple, secondary soft, and
secondary streak readability settings into `dam_break_water_mesh_smoothing`.
The 32-frame accepted render passes the surface-quality gate with
`normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels `0`.
Against S241, parity holds within render noise: max changed ratio `0`, max
strong changed ratio `0`, max mean abs luma `0.00014756944444444445`, bright
ratio delta `0`, highlight ratio delta `0`, `luma_p99` delta `0`, and contact
foam/ripple/streak count deltas `0`. Against S238, the accepted baseline gains
the intended foam/ripple readability: contact foam mean count rises from
`43.1875` to `54.5625`, impact ripple mean count rises from `62.0` to `73.0`,
mean luminance rises by `0.16201321072048813`, bright ratio improves by
`2.3057725694444525e-06`, and coverage/minimum contrast/hard highlight ratio
remain unchanged. Use S242 as the current accepted cinematic water baseline.

S243 added foam/readability contribution diagnostics:

- S243 report:
  `docs/reports/cinematic_foam_readability_contribution_diagnostics_s243.md`
- S243 plan:
  `docs/superpowers/plans/2026-06-19-foam-readability-contribution-diagnostics.md`
- S243 diagnostic sheet:
  `build/shots/s243_foam_readability_contribution_diagnostics/diagnostic_sheet.png`
- S243 masks:
  `build/shots/s243_foam_readability_contribution_diagnostics/masks/`

S243 compares S238 accepted highlight-material against S242 accepted
foam/readability with upper-tail gain/loss masks. The diagnostic reports gain
ratio `0.00255615234375`, loss ratio `0.0001691351996527778`, net gain ratio
`0.0023870171440972224`, mean gain luma delta `12.237818422405875`, and
strongest gain luma delta `55`. The sheet shows the S242 gain clustered around
contact foam and ripple speckles, especially in the middle of the motion window,
while loss is smaller and scattered. With foam/readability accepted and
localized, move next to water-body thickness/refraction.

S244 added a water-body thickness/refraction probe:

- S244 report:
  `docs/reports/cinematic_water_body_thickness_probe_s244.md`
- S244 gallery report:
  `docs/reports/cinematic_water_body_thickness_gallery_s244.md`
- S244 plan:
  `docs/superpowers/plans/2026-06-19-water-body-thickness-probe.md`
- S244 gallery:
  `build/shots/s244_water_body_thickness_probe/gallery/index.html`

S244 adds `dam_break_water_body_thickness_probe`, a bounded probe that keeps
accepted foam/ripple/glint/reflection overlays unchanged while tuning water
material depth/alpha/transmission and slightly increasing water-volume
scattering. The matched 16-frame gate passes with `normal_rough: 2`,
`stable: 14`, stable ratio `0.875`, and blocked labels `0`. Against S242
accepted 16-frame baseline, contact foam, impact ripple, and secondary streak
mean counts are unchanged; mean luminance rises by `0.3961309136284683`, bright
ratio by `3.065321180555552e-05`, highlight ratio by
`1.6818576388888902e-05`, and `luma_p99` by `0.125`, with nonblank coverage
unchanged. Remaining watch items are minimum contrast `-1.0` and `luma_p99.5`
`-0.125`, so S244 should go to S245 32-frame motion review before acceptance.

S245 validated S244 over the 32-frame accepted motion window:

- S245 motion review report:
  `docs/reports/cinematic_water_body_thickness_motion_review_s245.md`
- S245 gallery report:
  `docs/reports/cinematic_water_body_thickness_motion_gallery_s245.md`
- S245 plan:
  `docs/superpowers/plans/2026-06-19-water-body-thickness-motion-review.md`
- S245 gallery:
  `build/shots/s245_water_body_thickness_motion_review/gallery/index.html`

Against S242 accepted foam/readability, S245 passes the surface-quality gate
with `normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. Contact foam, impact ripple, and secondary streak mean counts remain
unchanged. Mean luminance rises by `0.37631863064235915`, minimum contrast by
`1.0`, bright ratio by `5.018446180555557e-05`, highlight ratio by
`2.8754340277777787e-05`, `luma_p95` by `0.5`, and `luma_p99` by `0.09375`;
coverage and `luma_p99.5` are unchanged. Promote S244 into
`dam_break_water_mesh_smoothing` in S246 and run accepted-preset parity against
S245.

S246 accepted the water-body thickness/refraction tuning:

- S246 acceptance report:
  `docs/reports/cinematic_water_body_thickness_acceptance_s246.md`
- S246 baseline delta report:
  `docs/reports/cinematic_water_body_thickness_acceptance_baseline_delta_s246.md`
- S246 gallery report:
  `docs/reports/cinematic_water_body_thickness_acceptance_gallery_s246.md`
- S246 plan:
  `docs/superpowers/plans/2026-06-19-water-body-thickness-acceptance.md`
- S246 gallery:
  `build/shots/s246_water_body_thickness_acceptance/gallery/index.html`

S246 folds the S244/S245 water material depth/alpha/transmission, water volume
scatter material, 20-layer scattering pass, and surface detail tuning into
`dam_break_water_mesh_smoothing`, while leaving occlusion disabled and accepted
foam/ripple/highlight behavior unchanged. The 32-frame accepted render passes
the surface-quality gate with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`. Against S245, parity holds within render
noise: max changed ratio `0`, max strong changed ratio `0`, bright/highlight/
contrast/nonblank/luma percentile deltas `0`, and scatter/foam/ripple/streak
count deltas `0`. Against S242, mean luminance rises by `0.3763206651475599`,
minimum contrast by `1.0`, bright ratio by `5.018446180555557e-05`, highlight
ratio by `2.8754340277777787e-05`, `luma_p95` by `0.5`, and `luma_p99` by
`0.09375`, with coverage and `luma_p99.5` unchanged. Use S246 as the current
accepted cinematic water baseline.

S247 added water-body contribution diagnostics:

- S247 report:
  `docs/reports/cinematic_water_body_contribution_diagnostics_s247.md`
- S247 plan:
  `docs/superpowers/plans/2026-06-19-water-body-contribution-diagnostics.md`
- S247 diagnostic sheet:
  `build/shots/s247_water_body_contribution_diagnostics/diagnostic_sheet.png`
- S247 masks:
  `build/shots/s247_water_body_contribution_diagnostics/masks/`

S247 compares S242 accepted foam/readability against S246 accepted water-body
thickness with upper-tail gain/loss masks. The diagnostic reports gain ratio
`0.0022139485677083333`, loss ratio `0.0017569986979166666`, net gain ratio
`0.00045694986979166665`, mean gain luma delta `10.267281407078043`, and mean
loss luma delta `9.951799090238987`. The sheet shows a mixed upper-tail
redistribution rather than a purely localized overlay gain, which is expected
for material/scattering tuning. Keep S246 accepted, but prioritize the
render-export/review schema before more subtle secondary mist tuning.

S248 added an accepted bridge-render review package:

- S248 report:
  `docs/reports/cinematic_accepted_review_package_s248.md`
- S248 plan:
  `docs/superpowers/plans/2026-06-19-accepted-review-package.md`
- S248 package JSON:
  `build/shots/s248_accepted_review_package/review_package.json`
- S248 tool:
  `tools/build_bridge_review_package.py`

S248 introduces the `lsfs_bridge_cinematic_review_package` schema and packages
the current S246 accepted baseline into one review manifest. The package indexes
the S246 gallery assets, bridge summary, SHA-256 hashes, render metadata,
comparison deltas, the S246 surface-quality gate, and S247 contribution
diagnostics. The generated package contains `12` artifacts and `4` summary
sources. Use this as the bridge-render review/export baseline before returning
to secondary mist readability.

S249 added a secondary mist readability probe:

- S249 report:
  `docs/reports/cinematic_secondary_mist_readability_probe_s249.md`
- S249 gallery report:
  `docs/reports/cinematic_secondary_mist_readability_gallery_s249.md`
- S249 plan:
  `docs/superpowers/plans/2026-06-20-secondary-mist-readability-probe.md`
- S249 gallery:
  `build/shots/s249_secondary_mist_readability_probe/gallery/index.html`

S249 adds `dam_break_secondary_mist_readability_probe`, a bounded soft mist,
streak, and contact haze probe that leaves direct secondary particles unchanged.
The stronger first trial in this step was too hazy, so the committed probe uses
a smaller contact curtain and softer secondary increases. The matched 16-frame
gate passes with `normal_rough: 2`, `stable: 14`, stable ratio `0.875`, and
blocked labels `0`. Against S246 accepted 16-frame baseline, contact foam,
impact ripple, and secondary streak mean counts are unchanged; mean luminance
rises by `0.4338905164930651`, minimum contrast and nonblank coverage are
unchanged, `luma_p95` rises by `0.25`, `luma_p99` by `0.0625`, and `luma_p99.5`
by `0.125`. Bright and highlight ratios have tiny negative deltas near the
comparison noise floor, so S249 should go to S250 32-frame motion review before
acceptance.

S250 reviewed S249 over the 32-frame accepted motion window:

- S250 motion review report:
  `docs/reports/cinematic_secondary_mist_motion_review_s250.md`
- S250 gallery report:
  `docs/reports/cinematic_secondary_mist_motion_gallery_s250.md`
- S250 plan:
  `docs/superpowers/plans/2026-06-20-secondary-mist-motion-review.md`
- S250 gallery:
  `build/shots/s250_secondary_mist_motion_review/gallery/index.html`

Against S246 accepted water-body thickness, S250 passes the surface-quality gate
with `normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. Contact foam, impact ripple, and secondary streak mean counts remain
unchanged. Mean luminance rises by `0.4362015787760498`, `luma_p95` by
`0.34375`, `luma_p99` by `0.1875`, and `luma_p99.5` by `0.09375`, with nonblank
coverage unchanged. However, minimum contrast drops by `3.0` and mean frame
contrast by `1.78125`, so S249 should not be accepted as-is. Run S251 with a
softer mist-only probe.

S251 added a softer secondary mist probe:

- S251 report:
  `docs/reports/cinematic_secondary_mist_soft_probe_s251.md`
- S251 gallery report:
  `docs/reports/cinematic_secondary_mist_soft_gallery_s251.md`
- S251 plan:
  `docs/superpowers/plans/2026-06-20-secondary-mist-soft-probe.md`
- S251 gallery:
  `build/shots/s251_secondary_mist_soft_probe/gallery/index.html`

S251 adds `dam_break_secondary_mist_readability_soft_probe`, a conservative
retry that leaves contact mist curtain and direct secondary particles unchanged
while applying a small soft mist/streak lift. The matched 16-frame gate passes
with `normal_rough: 2`, `stable: 14`, stable ratio `0.875`, and blocked labels
`0`. Against S246 accepted 16-frame baseline, contact foam, impact ripple, and
secondary streak mean counts are unchanged; minimum contrast, mean frame
contrast, nonblank coverage, and highlight ratio are unchanged; `luma_p95`,
`luma_p99`, and `luma_p99.5` each rise by `0.0625`. Promote S251 to S252
32-frame motion review.

S252 reviewed S251 over the 32-frame accepted motion window:

- S252 motion review report:
  `docs/reports/cinematic_secondary_mist_soft_motion_review_s252.md`
- S252 gallery report:
  `docs/reports/cinematic_secondary_mist_soft_motion_gallery_s252.md`
- S252 plan:
  `docs/superpowers/plans/2026-06-20-secondary-mist-soft-motion-review.md`
- S252 gallery:
  `build/shots/s252_secondary_mist_soft_motion_review/gallery/index.html`

Against S246 accepted water-body thickness, S252 passes the surface-quality gate
with `normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. Contact foam, impact ripple, and secondary streak mean counts remain
unchanged. Minimum contrast, mean frame contrast, nonblank coverage, and
highlight ratio are unchanged; `luma_p95` rises by `0.125` and `luma_p99` by
`0.03125`. However, mean luminance only rises by `0.020624593098958144`, and
`luma_p99.5` has a tiny `-0.03125` delta. Do not promote S251. Return to the
S246 accepted baseline and move to a more visible presentation or
shot-composition pass.

S253 added a presentation lift probe:

- S253 report:
  `docs/reports/cinematic_presentation_lift_probe_s253.md`
- S253 gallery report:
  `docs/reports/cinematic_presentation_lift_gallery_s253.md`
- S253 plan:
  `docs/superpowers/plans/2026-06-20-presentation-lift-probe.md`
- S253 gallery:
  `build/shots/s253_presentation_lift_probe/gallery/index.html`

S253 adds `dam_break_presentation_lift_probe`, a presentation-only tone and
lighting variant that inherits the accepted S246 simulation, material,
secondary, foam, ripple, and metadata overlay behavior. The matched 16-frame
gate passes with `normal_rough: 2`, `stable: 14`, stable ratio `0.875`, and
blocked labels `0`. Against S246 accepted 16-frame baseline, mean luminance
rises by `2.5741634114583434`, minimum contrast by `1.0`, `luma_p95` by
`2.9375`, `luma_p99` by `2.5625`, and `luma_p99.5` by `2.5`, with nonblank
coverage unchanged. Bright and highlight deltas remain tiny, upper-mid ratio
is effectively unchanged, and specular ratio decreases slightly. Promote S253
to S254 32-frame motion review before any accepted-preset promotion.

S254 reviewed the presentation lift over the 32-frame accepted motion window:

- S254 motion review report:
  `docs/reports/cinematic_presentation_lift_motion_review_s254.md`
- S254 gallery report:
  `docs/reports/cinematic_presentation_lift_motion_gallery_s254.md`
- S254 plan:
  `docs/superpowers/plans/2026-06-20-presentation-lift-motion-review.md`
- S254 gallery:
  `build/shots/s254_presentation_lift_motion_review/gallery/index.html`

Against S246 accepted, S254 passes the surface-quality gate with
`normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. Mean luminance rises by `2.5770274522569423`, minimum contrast by `1.0`,
`luma_p95` by `2.96875`, `luma_p99` by `2.53125`, and `luma_p99.5` by
`2.53125`, with nonblank coverage unchanged. Mean frame contrast decreases by
`1.6875`, but hard highlight/specular deltas remain tiny and visual comparison
does not show broad washout. Promote the S253 tone/lighting lift to S255
accepted-preset parity.

S255 promoted the presentation lift into the accepted preset:

- S255 parity report:
  `docs/reports/cinematic_presentation_lift_acceptance_parity_s255.md`
- S255 accepted delta report:
  `docs/reports/cinematic_presentation_lift_acceptance_delta_s255.md`
- S255 gallery report:
  `docs/reports/cinematic_presentation_lift_acceptance_gallery_s255.md`
- S255 plan:
  `docs/superpowers/plans/2026-06-20-presentation-lift-acceptance.md`
- S255 gallery:
  `build/shots/s255_presentation_lift_acceptance/gallery/index.html`

S255 moves the S253 tone mapping and lighting values into
`dam_break_water_mesh_smoothing` and keeps `dam_break_presentation_lift_probe`
as a historical alias. The 32-frame gate passes with `normal_rough: 3`,
`stable: 29`, stable ratio `0.90625`, and blocked labels `0`. Against S254,
bright ratio, highlight ratio, minimum contrast, nonblank coverage, luma
percentiles, upper-mid ratio, near-highlight ratio, specular ratio, and frame
contrast all have `0.0` delta; mean luminance differs only by
`-3.390842010730921e-06`. Against the previous S246 accepted baseline, S255
keeps the intended presentation lift with mean luminance `+2.5770240614149316`,
minimum contrast `+1.0`, `luma_p95 +2.96875`, `luma_p99 +2.53125`, and
`luma_p99.5 +2.53125`, while nonblank coverage is unchanged. S255 is now the
current accepted bridge-render visual baseline. Refresh the accepted review
package/gallery next.

S256 refreshed the accepted review package for S255:

- S256 report:
  `docs/reports/cinematic_accepted_review_package_s256.md`
- S256 plan:
  `docs/superpowers/plans/2026-06-20-accepted-review-package-refresh.md`
- S256 package JSON:
  `build/shots/s256_accepted_review_package/review_package.json`
- S255 accepted gallery:
  `build/shots/s255_presentation_lift_acceptance/gallery/index.html`

S256 packages the new S255 accepted visual baseline using the existing
`lsfs_bridge_cinematic_review_package` schema. The package contains `12`
artifacts and `4` summary sources: `s255_parity`, `s255_baseline_delta`,
`s255_surface_gate`, and `s254_motion_review`. This supersedes S248 for current
external review and publish handoff while preserving S248 as historical S246
evidence. Publish the S255 gallery/package next, then continue with either
shot-composition/camera polish or the next renderer-data/export milestone.

S257 published the S255 accepted gallery through a Cloudflare quick tunnel:

- S257 publish report:
  `docs/reports/cinematic_s255_gallery_publish_s257.md`
- S257 plan:
  `docs/superpowers/plans/2026-06-20-s255-gallery-publish.md`
- S257 manifest:
  `build/shots/s257_s255_gallery_publish/publish_manifest.json`
- S257 public URL:
  `https://kinds-dealers-cookie-athletics.trycloudflare.com`

The publisher verified local and public `index.html` plus `assets/shot.gif`
with HTTP `200`. The tunnel is session-scoped; refresh it if the process exits
or the machine restarts. After review, either start a shot-composition/camera
polish pass or move back to renderer-data/export schema work for larger-scale
handoff.

S258 added a camera-only presentation composition probe:

- S258 report:
  `docs/reports/cinematic_presentation_composition_probe_s258.md`
- S258 gallery report:
  `docs/reports/cinematic_presentation_composition_gallery_s258.md`
- S258 plan:
  `docs/superpowers/plans/2026-06-20-presentation-composition-probe.md`
- S258 gallery:
  `build/shots/s258_presentation_composition_probe/gallery/index.html`

S258 adds `dam_break_presentation_composition_probe`, extending S255 accepted
`dam_break_water_mesh_smoothing` while changing only camera motion/stability.
The 16-frame gate passes with `normal_rough: 2`, `stable: 14`, stable ratio
`0.875`, and blocked labels `0`. Secondary framing remains safe with mean
inside ratio `0.934460364976418` and min inside ratio `0.762962962962963`.
Against the accepted 16-frame camera reference, mean luminance is effectively
unchanged at `-0.032495117187508527`, minimum contrast rises by `57.0`, mean
frame contrast by `10.9375`, nonblank coverage is unchanged, and bright/
highlight ratios decrease. Promote S258 to S259 32-frame motion review before
accepting or rejecting the camera path.

S259 reviewed the camera composition over the 32-frame accepted motion window:

- S259 motion review report:
  `docs/reports/cinematic_presentation_composition_motion_review_s259.md`
- S259 gallery report:
  `docs/reports/cinematic_presentation_composition_motion_gallery_s259.md`
- S259 plan:
  `docs/superpowers/plans/2026-06-20-presentation-composition-motion-review.md`
- S259 gallery:
  `build/shots/s259_presentation_composition_motion_review/gallery/index.html`

Against S255 accepted, S259 passes the surface-quality gate with
`normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. Secondary framing remains inside QA with mean inside ratio
`0.9373630705958788` and min inside ratio `0.7239057239057239`. S259 preserves
nonblank coverage, raises minimum contrast by `5.0`, raises mean frame
contrast by `7.34375`, lowers mean luminance by only `0.07692477756076244`,
and reduces bright, highlight, near-highlight, and specular ratios. Promote
the S258/S259 camera motion to S260 accepted-camera parity.

S260 promoted the presentation composition camera into the accepted preset:

- S260 parity report:
  `docs/reports/cinematic_presentation_composition_acceptance_parity_s260.md`
- S260 accepted delta report:
  `docs/reports/cinematic_presentation_composition_acceptance_delta_s260.md`
- S260 gallery report:
  `docs/reports/cinematic_presentation_composition_acceptance_gallery_s260.md`
- S260 plan:
  `docs/superpowers/plans/2026-06-20-presentation-composition-acceptance.md`
- S260 gallery:
  `build/shots/s260_presentation_composition_acceptance/gallery/index.html`

S260 moves the S258 camera motion/stability values into
`dam_break_water_mesh_smoothing` and keeps
`dam_break_presentation_composition_probe` as a historical alias. Against S259,
all comparison metrics and calibration deltas are exactly `0.0`, confirming
accepted-preset parity. Against S255, S260 preserves nonblank coverage, raises
minimum contrast by `5.0`, raises mean frame contrast by `7.34375`, and reduces
bright, highlight, near-highlight, and specular ratios. S260 is now the current
accepted bridge-render visual baseline. Refresh the accepted review package
and public gallery from S260 next.

S261 refreshed and published the S260 accepted review package:

- S261 package report:
  `docs/reports/cinematic_accepted_review_package_s261.md`
- S261 publish report:
  `docs/reports/cinematic_s260_gallery_publish_s261.md`
- S261 plan:
  `docs/superpowers/plans/2026-06-20-s260-review-package-publish.md`
- S261 package JSON:
  `build/shots/s261_accepted_review_package/review_package.json`
- S261 public URL:
  `https://permits-cat-tall-certainly.trycloudflare.com`

S261 packages S260 with `12` artifacts and `4` summary sources:
`s260_parity`, `s260_baseline_delta`, `s260_surface_gate`, and
`s259_motion_review`. It also stops the previous S257/S255 tunnel and publishes
the S260 gallery through a new Cloudflare quick tunnel. Local and public
`index.html` plus `assets/shot.gif` return HTTP `200`. This supersedes S256/S257
as the current external review package and public gallery endpoint. Continue
with the next visible pass only after review, or move back to renderer-data/
export schema work if the S260 shot is acceptable for now.

S262 added a subject-clarity probe:

- S262 report:
  `docs/reports/cinematic_subject_clarity_probe_s262.md`
- S262 gallery report:
  `docs/reports/cinematic_subject_clarity_gallery_s262.md`
- S262 plan:
  `docs/superpowers/plans/2026-06-20-subject-clarity-probe.md`
- S262 gallery:
  `build/shots/s262_subject_clarity_probe/gallery/index.html`

S262 adds `dam_break_subject_clarity_probe`, extending S260 accepted
`dam_break_water_mesh_smoothing` while reducing surface glint/reflection
clutter and slightly strengthening water body volume/detail. The 16-frame gate
passes with `normal_rough: 2`, `stable: 14`, stable ratio `0.875`, and blocked
labels `0`. Effective glint count drops from `166` to `137`, reflection count
from `56` to `46`, and volume scatter alpha rises from `0.3456` to `0.3672`.
Against the S260 16-frame reference, nonblank coverage is unchanged, minimum
contrast rises by `24.0`, mean frame contrast by `1.3125`, and bright/highlight
ratios decrease. The upper luma tail drops (`luma_p99.5 -6.25`), so promote
S262 to S263 32-frame motion review before any accepted-preset promotion.

S263 reviewed subject clarity over the 32-frame accepted motion window:

- S263 motion review report:
  `docs/reports/cinematic_subject_clarity_motion_review_s263.md`
- S263 gallery report:
  `docs/reports/cinematic_subject_clarity_motion_gallery_s263.md`
- S263 plan:
  `docs/superpowers/plans/2026-06-20-subject-clarity-motion-review.md`
- S263 gallery:
  `build/shots/s263_subject_clarity_motion_review/gallery/index.html`

Against S260 accepted, S263 passes the surface-quality gate with
`normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. S263 preserves nonblank coverage, raises minimum contrast by `47.0`,
raises mean frame contrast by `2.4375`, reduces mean bright ratio by
`1.925998263888889e-05`, and visibly lowers surface-line clutter. The luma
tail drops and highlight/specular deltas rise slightly, but remain small enough
to promote S262/S263 subject-clarity settings to S264 accepted-preset parity.

S264 promoted the subject-clarity settings into the accepted preset:

- S264 parity report:
  `docs/reports/cinematic_subject_clarity_acceptance_parity_s264.md`
- S264 accepted delta report:
  `docs/reports/cinematic_subject_clarity_acceptance_delta_s264.md`
- S264 gallery report:
  `docs/reports/cinematic_subject_clarity_acceptance_gallery_s264.md`
- S264 plan:
  `docs/superpowers/plans/2026-06-20-subject-clarity-acceptance.md`
- S264 gallery:
  `build/shots/s264_subject_clarity_acceptance/gallery/index.html`

S264 moves S262 glint, reflection, water volume scattering, and water surface
detail settings into `dam_break_water_mesh_smoothing` and keeps
`dam_break_subject_clarity_probe` as a historical alias. Against S263, minimum
contrast, bright ratio, highlight ratio, nonblank coverage, luma percentiles,
upper-mid ratio, near-highlight ratio, specular ratio, and frame contrast all
have `0.0` delta; mean luminance differs only by `-1.3563367957658556e-06`.
Against S260, S264 preserves coverage, raises minimum contrast by `47.0`,
raises mean frame contrast by `2.4375`, and reduces mean bright ratio while
slightly increasing bounded highlight/specular ratios. S264 is now the current
accepted bridge-render visual baseline. Refresh the accepted review package
and public gallery from S264 next.

S265 refreshed and published the S264 accepted review package:

- S265 package report:
  `docs/reports/cinematic_accepted_review_package_s265.md`
- S265 publish report:
  `docs/reports/cinematic_s264_gallery_publish_s265.md`
- S265 plan:
  `docs/superpowers/plans/2026-06-20-s264-review-package-publish.md`
- S265 package JSON:
  `build/shots/s265_accepted_review_package/review_package.json`
- S265 public URL:
  `https://course-graduation-flags-longer.trycloudflare.com`

S265 packages S264 with `12` artifacts and `4` summary sources:
`s264_parity`, `s264_baseline_delta`, `s264_surface_gate`, and
`s263_motion_review`. It stops the previous S261/S260 tunnel and publishes the
S264 gallery through a new Cloudflare quick tunnel. Local and public
`index.html` plus `assets/shot.gif` return HTTP `200`. This supersedes S261 as
the current external review package and public gallery endpoint. Continue with
another visible pass only if review shows a concrete issue; otherwise shift
back to renderer-data/export schema or larger-scale handoff work.

S266 added a material-only secondary color cooling probe:

- S266 report:
  `docs/reports/cinematic_secondary_color_cooling_probe_s266.md`
- S266 gallery report:
  `docs/reports/cinematic_secondary_color_cooling_gallery_s266.md`
- S266 plan:
  `docs/superpowers/plans/2026-06-20-secondary-color-cooling-probe.md`
- S266 gallery:
  `build/shots/s266_secondary_color_cooling_probe/gallery/index.html`

S266 adds `dam_break_secondary_color_cooling_probe`, extending S264 accepted
`dam_break_water_mesh_smoothing` while changing only spray, foam, and bubble
material color/emission/alpha. The 16-frame gate passes with `normal_rough: 2`,
`stable: 14`, stable ratio `0.875`, and blocked labels `0`. Against S264,
nonblank, contrast, bright ratio, and highlight ratio are unchanged; mean
luminance changes only by `-0.05237711588542027`. Do not promote S266 as-is:
material-only cooling is safe but too subtle. Run S267 with stronger secondary
bead de-warming that also reduces direct bead retention/alpha and secondary
emission.

S267 added a stronger secondary de-warm probe:

- S267 report:
  `docs/reports/cinematic_secondary_dewarm_probe_s267.md`
- S267 gallery report:
  `docs/reports/cinematic_secondary_dewarm_gallery_s267.md`
- S267 plan:
  `docs/superpowers/plans/2026-06-20-secondary-dewarm-probe.md`
- S267 gallery:
  `build/shots/s267_secondary_dewarm_probe/gallery/index.html`

S267 adds `dam_break_secondary_dewarm_probe`, extending S264 accepted
`dam_break_water_mesh_smoothing` while cooling spray/foam/bubble materials,
reducing direct secondary bead retention/radius, and softening secondary
soft/streak alpha and emission. The 16-frame gate passes with `normal_rough: 2`,
`stable: 14`, stable ratio `0.875`, and blocked labels `0`. Against S264,
nonblank coverage and contrast are stable, mean luminance drops by
`0.24353271484375227`, upper luma tail drops, and bright/highlight increases
are only around `1e-7`. Promote S267 to S268 32-frame motion review.

S268 validated the secondary de-warm probe over the accepted motion window:

- S268 report:
  `docs/reports/cinematic_secondary_dewarm_motion_review_s268.md`
- S268 gallery report:
  `docs/reports/cinematic_secondary_dewarm_motion_gallery_s268.md`
- S268 plan:
  `docs/superpowers/plans/2026-06-20-secondary-dewarm-motion-review.md`
- S268 gallery:
  `build/shots/s268_secondary_dewarm_motion_review/gallery/index.html`

S268 keeps `dam_break_secondary_dewarm_probe` unchanged and compares it against
S264 over `32` frames. The surface-quality gate passes with `normal_rough: 3`,
`stable: 29`, stable ratio `0.90625`, and blocked labels `0`. Against S264,
nonblank coverage, minimum contrast, and mean frame contrast are unchanged.
Mean luminance drops by `0.24766113281251023`, upper luma tail drops
(`p95 -0.71875`, `p99 -1.0625`, `p99.5 -1.25`), and bright/highlight/specular
increases remain around `1e-7` to `5e-7`. The comparison sheet confirms the
secondary particles remain visible while reading less like warm beads. Promote
S267/S268 settings to S269 accepted-preset parity.

S269 promoted the secondary de-warm settings into the accepted preset:

- S269 parity report:
  `docs/reports/cinematic_secondary_dewarm_acceptance_parity_s269.md`
- S269 accepted delta report:
  `docs/reports/cinematic_secondary_dewarm_acceptance_delta_s269.md`
- S269 gallery report:
  `docs/reports/cinematic_secondary_dewarm_acceptance_gallery_s269.md`
- S269 plan:
  `docs/superpowers/plans/2026-06-20-secondary-dewarm-acceptance.md`
- S269 gallery:
  `build/shots/s269_secondary_dewarm_acceptance/gallery/index.html`

S269 folds the S267/S268 secondary channel radius, direct-pass, soft-pass,
streak-pass, and spray/foam/bubble material overrides into
`dam_break_water_mesh_smoothing`. `dam_break_secondary_dewarm_probe` is now a
historical alias extending the accepted preset. The 32-frame gate passes with
`normal_rough: 3`, `stable: 29`, stable ratio `0.90625`, and blocked labels
`0`. Against S268, parity is exact except for mean luminance floating-point
noise at `-5.425347211485132e-07`; all coverage, contrast, highlight, luma-tail,
and specular deltas are `0`. Against S264, the reviewed secondary de-warm delta
is preserved: coverage and contrast stay unchanged, mean luminance drops by
`0.24766167534723138`, upper luma tail drops, and bright/highlight/specular
increases remain negligible. S269 is the current accepted bridge-render visual
baseline. Refresh the accepted review package and public gallery from S269.

S270 refreshed and published the S269 accepted review package:

- S270 package report:
  `docs/reports/cinematic_accepted_review_package_s270.md`
- S270 publish report:
  `docs/reports/cinematic_s269_gallery_publish_s270.md`
- S270 plan:
  `docs/superpowers/plans/2026-06-20-s269-review-package-publish.md`
- S270 package JSON:
  `build/shots/s270_accepted_review_package/review_package.json`
- S270 public URL:
  `https://rfc-empirical-match-outstanding.trycloudflare.com`

S270 packages S269 with `12` artifacts and `4` summary sources:
`s269_parity`, `s269_baseline_delta`, `s269_surface_gate`, and
`s268_motion_review`. It stops the previous S265/S264 quick tunnel and publishes
the S269 gallery through a new Cloudflare quick tunnel. Local and public
`index.html` plus `assets/shot.gif` checks all returned HTTP `200`. S270 is now
the current external review package and public gallery endpoint.

S271 added a machine-readable accepted bridge handoff manifest:

- S271 tool:
  `tools/build_bridge_handoff_manifest.py`
- S271 report:
  `docs/reports/cinematic_accepted_handoff_manifest_s271.md`
- S271 plan:
  `docs/superpowers/plans/2026-06-20-accepted-handoff-manifest.md`
- S271 manifest:
  `build/shots/s271_accepted_handoff/handoff_manifest.json`

S271 consumes the S270 review package and publish manifest, plus the converted
sequence, render-data summary, and `configs/cinematic_presets.json`. The output
schema is `lsfs_bridge_cinematic_handoff_manifest` version `1`, with accepted
preset `dam_break_water_mesh_smoothing`, git commit
`b53576c548a45406757f6b3f2740bc528f8278ef`, public URL
`https://rfc-empirical-match-outstanding.trycloudflare.com`, `12` artifacts,
`4` summary digests, and `5` source fingerprints. Use S271 as the current
machine-readable baseline pointer for external renderer schema work,
larger-shot reruns, or large-scale benchmark gates.

S272 added and ran a handoff manifest validator:

- S272 tool:
  `tools/validate_bridge_handoff_manifest.py`
- S272 report:
  `docs/reports/cinematic_accepted_handoff_validation_s272.md`
- S272 plan:
  `docs/superpowers/plans/2026-06-20-accepted-handoff-validation.md`
- S272 validation JSON:
  `build/shots/s272_handoff_validation/validation.json`

S272 validates the `lsfs_bridge_cinematic_handoff_manifest` schema/version,
accepted preset, `5` source fingerprints, `12` gallery artifact fingerprints,
publish status, and public `index.html`/`assets/shot.gif` checks. The S271
manifest passed `23` checks with `0` failures and `0` warnings, and both public
URL checks returned HTTP `200`. Use the S271/S272 pair as the current
machine-readable accepted baseline gate before external-render experiments,
larger-shot reruns, or large-scale benchmark jobs consume S269.

S273 added a frame-level external render bundle manifest:

- S273 tool:
  `tools/build_bridge_external_render_bundle.py`
- S273 report:
  `docs/reports/cinematic_external_render_bundle_s273.md`
- S273 plan:
  `docs/superpowers/plans/2026-06-20-external-render-bundle.md`
- S273 bundle:
  `build/shots/s273_external_render_bundle/external_render_bundle.json`

S273 consumes the S271 handoff manifest and emits
`lsfs_bridge_external_render_bundle` version `1`. It reuses the bridge
renderer's source-window resampling rule, producing `32` accepted output frames
from source window `8..55` with camera JSON, particle CSV, phase-cell CSV,
water-mesh OBJ, surface-quality, and render-data references. The generated
bundle has `0` missing assets and records the accepted input footprint:
`1.28 GB` particle CSV, `33.66 MB` phase-cell CSV, and `53.39 MB` water OBJ.
Use S273 as the frame-level input list for external renderer prototypes,
larger-shot reruns, or large-scale benchmark input-size gates.

S274 made the external render bundle directly previewable:

- S274 report:
  `docs/reports/cinematic_external_bundle_preview_s274.md`
- S274 plan:
  `docs/superpowers/plans/2026-06-20-external-bundle-preview-gate.md`
- S274 preview GIF:
  `build/shots/s274_external_bundle_preview/preview.gif`
- S274 preview summary:
  `build/shots/s274_external_bundle_preview/preview/render_summary.json`

S274 extends `tools/cinematic_render_stub.py` to accept
`lsfs_bridge_external_render_bundle` inputs. Bundle mode samples only the
requested preview frames before reading large particle/phase CSV assets, and it
uses the bundle water-mesh assets for mesh overlay. The S273 bundle rendered an
8-frame `640 x 360` preview with minimum occupancy `0.0608984375` against the
`0.01` gate, then assembled a GIF. Use S274 as the fast visual smoke gate for
S273 before heavier external-render, larger-shot, or Blender work.

S275 packaged the S274 preview as a lightweight static gallery:

- S275 tool:
  `tools/build_preview_gallery.py`
- S275 report:
  `docs/reports/cinematic_external_bundle_preview_gallery_s275.md`
- S275 plan:
  `docs/superpowers/plans/2026-06-20-preview-gallery-builder.md`
- S275 gallery:
  `build/shots/s275_external_bundle_preview_gallery/gallery/index.html`

S275 emits `lsfs_preview_gallery` version `1`, copies the preview GIF to
`assets/shot.gif` for compatibility with `tools/publish_cinematic_gallery.py`,
copies `8` preview keyframes, and includes the S274 render summary. The gallery
has `9` visual assets, `1` metadata file, and preserves the S274 minimum
occupancy `0.0608984375`. Use S275 as the lightweight shareable visual page for
the external-render handoff path.

S276 published the S275 lightweight external-bundle preview gallery:

- S276 publish report:
  `docs/reports/cinematic_external_bundle_preview_publish_s276.md`
- S276 plan:
  `docs/superpowers/plans/2026-06-20-external-bundle-preview-publish.md`
- S276 manifest:
  `build/shots/s276_external_bundle_preview_publish/publish_manifest.json`
- S276 public URL:
  `https://broken-textile-compared-rebound.trycloudflare.com`

S276 serves the S275 gallery on local port `8901` and starts a separate
Cloudflare quick tunnel, leaving the S270/S269 accepted gallery endpoint active.
Local and public `index.html` plus `assets/shot.gif` checks all returned HTTP
`200`. Use S276 as the lightweight external-bundle visual handoff endpoint.

S277 upgraded the external-bundle preview to a 16-frame motion review:

- S277 report:
  `docs/reports/cinematic_external_bundle_motion_preview_s277.md`
- S277 gallery report:
  `docs/reports/cinematic_external_bundle_motion_preview_gallery_s277.md`
- S277 plan:
  `docs/superpowers/plans/2026-06-20-external-bundle-motion-preview.md`
- S277 gallery:
  `build/shots/s277_external_bundle_motion_preview/gallery/index.html`

S277 updates `tools/cinematic_render_stub.py` so external-bundle inputs are
loaded lazily one selected frame at a time, avoiding retention of all selected
particle/phase CSV payloads. The S273 bundle rendered a `16` frame `960 x 540`
preview with minimum occupancy `0.05804398148148148` against the `0.01` gate,
assembled a GIF, and built a preview gallery with `9` visual assets. Use S277
as the preferred lightweight external-render handoff preview before heavier
larger-shot or Blender work.

S278 published the S277 external-bundle motion preview gallery:

- S278 publish report:
  `docs/reports/cinematic_external_bundle_motion_preview_publish_s278.md`
- S278 plan:
  `docs/superpowers/plans/2026-06-20-external-bundle-motion-preview-publish.md`
- S278 manifest:
  `build/shots/s278_external_bundle_motion_preview_publish/publish_manifest.json`
- S278 public URL:
  `https://concord-extensions-dial-conduct.trycloudflare.com`

S278 stops the S276/S275 preview endpoint, serves the S277 gallery on local port
`8901`, and starts a new Cloudflare quick tunnel. Local and public `index.html`
plus `assets/shot.gif` checks all returned HTTP `200`. S278 is now the current
lightweight external-render handoff preview endpoint; the S270/S269 accepted
gallery endpoint remains active separately.

S279 added the external-bundle benchmark readiness gate:

- S279 tool:
  `tools/validate_external_bundle_benchmark_gate.py`
- S279 report:
  `docs/reports/cinematic_external_bundle_benchmark_gate_s279.md`
- S279 plan:
  `docs/superpowers/plans/2026-06-20-external-bundle-benchmark-gate.md`
- S279 gate JSON:
  `build/shots/s279_external_bundle_benchmark_gate/benchmark_gate.json`

S279 validates the S273 bundle, S277 preview summary, and S278 publish manifest
before larger-shot or benchmark work consumes the external-bundle path. The gate
passed `13` checks with `0` failures: bundle schema/frame count, missing assets,
monotonic source sampling, minimum water mesh faces, preview frame count,
preview resolution, preview occupancy, publish status, recorded publish checks,
and live public `index.html`/`assets/shot.gif`. It records the current input
footprint as `1.37 GB`, projected `64`-frame input as `2.74 GB`, and projected
`24`-frame preview sample input as `1.03 GB`. Use S279 as the preflight gate
before bounded larger-shot dry-runs or benchmark jobs.

S280 ran a bounded larger preview benchmark through the external-bundle path:

- S280 tool:
  `tools/run_external_bundle_preview_benchmark.py`
- S280 report:
  `docs/reports/cinematic_external_bundle_preview_benchmark_s280.md`
- S280 plan:
  `docs/superpowers/plans/2026-06-20-external-bundle-preview-benchmark.md`
- S280 summary:
  `build/shots/s280_external_bundle_preview_benchmark/benchmark_summary.json`
- S280 gallery:
  `build/shots/s280_external_bundle_preview_benchmark/gallery/index.html`

S280 requires the S279 preflight gate, renders the S273 bundle as a `24` frame
`1280 x 720` preview, assembles a GIF, and builds a preview gallery. The run
passed with minimum occupancy `0.056202256944444445` against the `0.01` gate,
`9` gallery assets, `903.32 KB` GIF size, and total elapsed time `70.72s`
(`69.25s` preview render, `1.28s` GIF assembly, `0.20s` gallery build). Use S280
as the bounded larger preview benchmark before replacing the public preview
endpoint or scaling further.

S281 published the S280 external-bundle preview benchmark gallery:

- S281 publish report:
  `docs/reports/cinematic_external_bundle_preview_benchmark_publish_s281.md`
- S281 plan:
  `docs/superpowers/plans/2026-06-20-external-bundle-preview-benchmark-publish.md`
- S281 manifest:
  `build/shots/s281_external_bundle_benchmark_publish/publish_manifest.json`
- S281 public URL:
  `https://roman-semester-highlighted-formatting.trycloudflare.com`

S281 stops the S278/S277 preview endpoint, serves the S280 gallery on local port
`8901`, and starts a new Cloudflare quick tunnel. Local and public `index.html`
plus `assets/shot.gif` checks all returned HTTP `200`. S281 is now the current
lightweight external-render benchmark preview endpoint; the S270/S269 accepted
gallery endpoint remains active separately.

S282 validated the accepted bridge render at higher presentation resolution:

- S282 review report:
  `docs/reports/cinematic_accepted_bridge_hires_review_s282.md`
- S282 gallery report:
  `docs/reports/cinematic_accepted_bridge_hires_gallery_s282.md`
- S282 plan:
  `docs/superpowers/plans/2026-06-20-accepted-bridge-hires-review.md`
- S282 gallery:
  `build/shots/s282_accepted_bridge_hires_review/gallery/index.html`

S282 renders the accepted `dam_break_water_mesh_smoothing` preset at `32`
frames, source window `8..55`, `960 x 540`, and `12` samples. The dry-run and
surface-quality gate pass with `normal_rough: 3`, `stable: 29`. Against S269
`640 x 360`, S282 preserves nonblank coverage, reduces broad bright/highlight
ratios by about `2e-5`, raises mean frame contrast by `1.65625`, and is visibly
sharper. The local minimum contrast delta is `-9.0`, recorded as a resolution
review note rather than an accepted-preset regression. Use S282 as the
high-resolution bridge review artifact while keeping S269 as the accepted preset
baseline.

S283 published the S282 high-resolution bridge review gallery:

- S283 publish report:
  `docs/reports/cinematic_accepted_bridge_hires_publish_s283.md`
- S283 plan:
  `docs/superpowers/plans/2026-06-20-accepted-bridge-hires-publish.md`
- S283 manifest:
  `build/shots/s283_s282_bridge_hires_publish/publish_manifest.json`
- S283 public URL:
  `https://staff-held-cheese-organized.trycloudflare.com`

S283 stops the previous S270/S269 accepted-gallery endpoint, serves the S282
gallery on local port `8900`, and starts a new Cloudflare quick tunnel. Local
and public `index.html` plus `assets/shot.gif` checks all returned HTTP `200`.
The new HTTP server PID is `138664`, and the Cloudflared PID is `38632`. S283 is
now the current high-resolution bridge-review endpoint; S281 remains active
separately as the lightweight external-bundle benchmark preview endpoint.

S284 packaged the S282/S283 high-resolution bridge review state:

- S284 package report:
  `docs/reports/cinematic_accepted_bridge_hires_review_package_s284.md`
- S284 plan:
  `docs/superpowers/plans/2026-06-20-accepted-bridge-hires-review-package.md`
- S284 package JSON:
  `build/shots/s284_accepted_hires_review_package/review_package.json`

S284 collects `12` visual/metadata artifacts from the S282 gallery and `4`
summary sources: S282-vs-S269 frame deltas, S282 surface-gate output, the S283
publish manifest, and the S280 external-bundle preview benchmark summary. Use
S284 as the current high-resolution bridge-review handoff package while keeping
S269 as the accepted preset baseline.

S285 added a renderer-facing job manifest:

- S285 tool:
  `tools/build_external_renderer_job.py`
- S285 report:
  `docs/reports/cinematic_external_renderer_job_s285.md`
- S285 plan:
  `docs/superpowers/plans/2026-06-20-external-renderer-job-manifest.md`
- S285 job JSON:
  `build/shots/s285_external_renderer_job/external_renderer_job.json`

S285 emits `lsfs_external_renderer_job` version `1` from the S273 external
bundle and attaches S282 bridge-look settings, S284 review package evidence,
the S283 accepted publish manifest, and the S280 external-bundle benchmark
summary. It records a channel contract for camera JSON, water-surface OBJ,
phase-volume CSV, and particle-stream CSV without loading the large CSV
payloads. The generated job is `ready` with `32` frames, `960 x 540`, `8` FPS,
`12` samples, `0` missing assets, `0` camera failures, minimum water mesh faces
`17720`, and a `1.37 GB` input footprint. Use S285 as the renderer handoff
contract before writing a renderer-specific adapter or larger-shot job variant.

S286 made S285 renderer jobs previewable:

- S286 preview report:
  `docs/reports/cinematic_external_renderer_job_preview_s286.md`
- S286 gallery report:
  `docs/reports/cinematic_external_renderer_job_preview_gallery_s286.md`
- S286 plan:
  `docs/superpowers/plans/2026-06-20-external-renderer-job-preview.md`
- S286 gallery:
  `build/shots/s286_external_renderer_job_preview/gallery/index.html`

S286 extends `tools/cinematic_render_stub.py` so `lsfs_external_renderer_job`
inputs can drive the existing preview renderer directly. The S285 job rendered
a `16` frame `960 x 540` preview with minimum occupancy
`0.05804398148148148`, assembled a GIF, and built a `9` asset gallery. Use S286
as the visual smoke test for the renderer job schema before publishing the
gallery or writing a renderer-specific adapter.

S287 published the S286 external renderer job preview gallery:

- S287 publish report:
  `docs/reports/cinematic_external_renderer_job_preview_publish_s287.md`
- S287 plan:
  `docs/superpowers/plans/2026-06-20-external-renderer-job-preview-publish.md`
- S287 manifest:
  `build/shots/s287_external_renderer_job_preview_publish/publish_manifest.json`
- S287 public URL:
  `https://installations-uni-tiger-nov.trycloudflare.com`

S287 serves the S286 gallery on local port `8902` and starts a separate
Cloudflare quick tunnel. Local and public `index.html` plus `assets/shot.gif`
checks all returned HTTP `200`. The HTTP server PID is `61388`, and the
Cloudflared PID is `153412`. S287 is the public smoke-test endpoint for the
external renderer job schema path; S283 and S281 remain active separately for
accepted bridge review and external-bundle benchmark preview.

S288 connected external renderer jobs to the Blender bridge dry-run path:

- S288 report:
  `docs/reports/cinematic_external_renderer_job_blender_adapter_s288.md`
- S288 plan:
  `docs/superpowers/plans/2026-06-20-external-renderer-job-blender-adapter.md`
- S288 dry-run summary:
  `build/shots/s288_external_renderer_job_blender_adapter/dry/bridge_summary.json`
- S288 scene spec:
  `build/shots/s288_external_renderer_job_blender_adapter/dry/blender_scene_spec.json`

S288 extends `tools/render_bridge_blender.py` so `src` can be either the older
S38 converted `sequence.json` or a `lsfs_external_renderer_job`. The S285 job
dry-run produced an `8` frame Blender scene spec at `960 x 540`, `12` samples,
using source window `0..31` and the accepted
`dam_break_water_mesh_smoothing` preset. First/last water mesh face counts are
`20000` and `22300`, and secondary totals are `256` and `964`. Use S288 as the
renderer-specific adapter gate before running a bounded Blender render through
the job path.

S289 rendered the first actual Blender sequence from the external renderer job
schema:

- S289 render report:
  `docs/reports/cinematic_external_renderer_job_blender_render_s289.md`
- S289 comparison report:
  `docs/reports/cinematic_external_renderer_job_blender_render_compare_s289.md`
- S289 gallery report:
  `docs/reports/cinematic_external_renderer_job_blender_render_gallery_s289.md`
- S289 plan:
  `docs/superpowers/plans/2026-06-20-external-renderer-job-blender-render.md`
- S289 gallery:
  `build/shots/s289_external_renderer_job_blender_render/gallery/index.html`

S289 renders the S285 job path through Blender for `8` frames at `960 x 540`,
`12` samples, using source window `0..31` and the accepted
`dam_break_water_mesh_smoothing` preset. Blender elapsed time is `42895.83` ms,
minimum nonblank ratio is `1.0`, minimum contrast is `207.0`, first/last water
mesh face counts are `20000` and `22300`, and first/last secondary totals are
`256` and `964`. Against an aligned S282 8-frame sample, nonblank delta is
`0.0`, mean luma p99 delta is `0.375`, mean specular ratio delta is
`4.099151234567901e-06`, and aligned mean frame contrast delta is `-0.125`. Use
S289 as the first actual Blender render proof from the external renderer job
schema.

S290 published the S289 job-path Blender render gallery:

- S290 publish report:
  `docs/reports/cinematic_external_renderer_job_blender_render_publish_s290.md`
- S290 plan:
  `docs/superpowers/plans/2026-06-20-external-renderer-job-blender-render-publish.md`
- S290 manifest:
  `build/shots/s290_external_renderer_job_blender_render_publish/publish_manifest.json`
- S290 public URL:
  `https://mathematics-insert-hybrid-dozens.trycloudflare.com`

S290 stops the S287 preview-smoke endpoint, serves the S289 actual Blender
render gallery on local port `8902`, and starts a new Cloudflare quick tunnel.
Local and public `index.html` plus `assets/shot.gif` checks all returned HTTP
`200`. The HTTP server PID is `154780`, and the Cloudflared PID is `90764`.
S290 is the current public job-path Blender render endpoint; S283 and S281
remain active separately for accepted high-resolution bridge review and
external-bundle benchmark preview.

S291 scaled the job-path Blender render to the full 32-frame accepted window:

- S291 render report:
  `docs/reports/cinematic_external_renderer_job_blender_full32_s291.md`
- S291 comparison report:
  `docs/reports/cinematic_external_renderer_job_blender_full32_compare_s291.md`
- S291 gallery report:
  `docs/reports/cinematic_external_renderer_job_blender_full32_gallery_s291.md`
- S291 plan:
  `docs/superpowers/plans/2026-06-20-external-renderer-job-blender-full32.md`
- S291 gallery:
  `build/shots/s291_external_renderer_job_blender_full32/gallery/index.html`

S291 renders all `32` frames from the S285 job path at `960 x 540`, `12`
samples, using source window `0..31` and the accepted
`dam_break_water_mesh_smoothing` preset. Blender elapsed time is `160355.97`
ms, minimum nonblank ratio is `1.0`, minimum contrast is `188.0`, first/last
water mesh face counts are `20000` and `22300`, and first/last secondary totals
are `256` and `964`. Against S282, nonblank delta is `0.0`, mean frame contrast
delta is `0.125`, mean luma p99 delta is `0.25`, and mean specular ratio delta
is `3.6168981481481466e-06`. Use S291 as the full-length job-path Blender proof
before publishing, packaging, larger-shot jobs, or external renderer adapters.

S292 published the S291 full-length job-path Blender render gallery:

- S292 publish report:
  `docs/reports/cinematic_external_renderer_job_blender_full32_publish_s292.md`
- S292 plan:
  `docs/superpowers/plans/2026-06-20-external-renderer-job-blender-full32-publish.md`
- S292 manifest:
  `build/shots/s292_external_renderer_job_blender_full32_publish/publish_manifest.json`
- S292 public URL:
  `https://shall-warnings-critical-quite.trycloudflare.com`

S292 stops the S290 8-frame job-path render endpoint, serves the S291 full32
gallery on local port `8902`, and starts a new Cloudflare quick tunnel. Local
and public `index.html` plus `assets/shot.gif` checks all returned HTTP `200`.
The HTTP server PID is `66504`, and the Cloudflared PID is `129180`. S292 is
the current public full-length job-path Blender render endpoint; S283 and S281
remain active separately for accepted high-resolution bridge review and
external-bundle benchmark preview.

S293 packaged the full-length external-renderer job proof:

- S293 package report:
  `docs/reports/cinematic_full_renderer_job_proof_package_s293.md`
- S293 plan:
  `docs/superpowers/plans/2026-06-20-full-renderer-job-proof-package.md`
- S293 package JSON:
  `build/shots/s293_full_renderer_job_proof_package/review_package.json`

S293 collects `12` visual/metadata artifacts from the S291 gallery and `4`
summary sources: the S285 renderer job, S291-vs-S282 comparison, S292 publish
manifest, and S280 external-bundle benchmark summary. Use S293 as the current
handoff package for the full-length external-renderer job proof before moving
to larger-shot job generation or a non-Blender external renderer adapter.

S294 created a larger 48-frame external render bundle:

- S294 tool update:
  `tools/build_bridge_external_render_bundle.py`
- S294 report:
  `docs/reports/cinematic_larger_external_render_bundle_s294.md`
- S294 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-render-bundle.md`
- S294 bundle:
  `build/shots/s294_larger_external_render_bundle_48/external_render_bundle.json`

S294 adds `--public-review-manifest` so new bundles can override stale public
review metadata from older handoff manifests. The generated
`lsfs_bridge_external_render_bundle` has `48` frames over source window `8..55`,
`0` missing assets, and points at the current S292 public URL
`https://shall-warnings-critical-quite.trycloudflare.com`. Its input footprint
is `1.92 GB` particle CSV, `50.49 MB` phase-cell CSV, and `80.07 MB` water mesh
OBJ. Use S294 as the larger-shot input bundle before building the next renderer
job.

S295 built the larger 48-frame renderer job contract:

- S295 report:
  `docs/reports/cinematic_larger_external_renderer_job_s295.md`
- S295 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job.md`
- S295 job JSON:
  `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`

S295 emits `lsfs_external_renderer_job` version `1` from S294 and attaches S291
bridge-look settings, S293 proof package evidence, S292 publish evidence, and
S280 benchmark context. The job is `ready` with `48` frames, source sequence
range `8..55`, `0` missing assets, `0` camera failures, monotonic frame order,
minimum water mesh faces `17720`, quality labels `normal_rough: 4` and
`stable: 44`, and a `2.05 GB` input footprint. Use S295 as the larger renderer
job contract before preview or Blender gates.

S296 previewed the larger 48-frame renderer job:

- S296 preview report:
  `docs/reports/cinematic_larger_external_renderer_job_preview_s296.md`
- S296 gallery report:
  `docs/reports/cinematic_larger_external_renderer_job_preview_gallery_s296.md`
- S296 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job-preview.md`
- S296 gallery:
  `build/shots/s296_larger_external_renderer_job_preview/gallery/index.html`

S296 renders the S295 job through the preview renderer as `24` frames at
`1280 x 720`, with minimum occupancy `0.056203342013888886` against the `0.01`
gate. The generated GIF is `931895` bytes, and the gallery has `9` visual
assets. A representative keyframe is nonblank and shows water, secondary
particles, and mesh overlay. Use S296 as the larger-job visual smoke test before
publishing or running a Blender adapter dry-run.

S297 published the larger-job preview gallery:

- S297 publish report:
  `docs/reports/cinematic_larger_external_renderer_job_preview_publish_s297.md`
- S297 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job-preview-publish.md`
- S297 manifest:
  `build/shots/s297_larger_external_renderer_job_preview_publish/publish_manifest.json`
- S297 public URL:
  `https://arch-walk-informational-corporate.trycloudflare.com`

S297 serves the S296 gallery on local port `8903` and starts a Cloudflare quick
tunnel. Local and public `index.html` plus `assets/shot.gif` checks all returned
HTTP `200`. The HTTP server PID is `167784`, and the Cloudflared PID is
`49980`. Use S297 as the public larger-job preview endpoint while S292 remains
active separately as the full32 Blender render proof endpoint.

S298 connected the larger 48-frame job to the Blender adapter dry-run path:

- S298 report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_adapter_s298.md`
- S298 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job-blender-adapter.md`
- S298 dry-run summary:
  `build/shots/s298_larger_external_renderer_job_blender_adapter/dry/bridge_summary.json`
- S298 scene spec:
  `build/shots/s298_larger_external_renderer_job_blender_adapter/dry/blender_scene_spec.json`

S298 runs `tools/render_bridge_blender.py` in dry-run mode from the S295 job,
using source window `0..47`, `12` output frames, `960 x 540`, `12` samples, and
the accepted `dam_break_water_mesh_smoothing` preset. The generated scene spec
covers render-data source frames `20..55`, first/middle/last water mesh faces
`20000`, `18576`, and `22300`, and first/last secondary totals `256` and `964`.
Use S298 as the Blender adapter gate before rendering a bounded larger-job
sample.

S299 rendered a bounded Blender sample from the larger 48-frame job path:

- S299 render report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample12_s299.md`
- S299 comparison report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample12_compare_s299.md`
- S299 gallery report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample12_gallery_s299.md`
- S299 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job-blender-sample12.md`
- S299 gallery:
  `build/shots/s299_larger_external_renderer_job_blender_sample12/gallery/index.html`

S299 renders the S295 larger job through Blender for `12` frames at `960 x
540`, `12` samples, using source window `0..47` and the accepted
`dam_break_water_mesh_smoothing` preset. Blender elapsed time is `66438.96` ms,
minimum nonblank ratio is `1.0`, minimum contrast is `159.0`, first/last water
mesh face counts are `20000` and `22300`, and first/last secondary totals are
`256` and `964`. Against a matched S291 sample, nonblank delta is `0.0`, mean
luma p99 delta is `-0.1666666666666714`, mean specular ratio delta is
`-1.1252572016460965e-06`, and mean frame contrast delta is
`-4.166666666666657`. Use S299 as the bounded larger-job Blender render proof
before public publish, package, or longer larger-job render attempts.

S300 published the S299 larger-job Blender sample gallery:

- S300 publish report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample12_publish_s300.md`
- S300 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job-blender-sample12-publish.md`
- S300 manifest:
  `build/shots/s300_larger_external_renderer_job_blender_sample12_publish/publish_manifest.json`
- S300 public URL:
  `https://vatican-ranking-laden-slip.trycloudflare.com`

S300 stops the S297 larger-job preview endpoint, serves the S299 actual Blender
sample gallery on local port `8903`, and starts a new Cloudflare quick tunnel.
Local and public `index.html` plus `assets/shot.gif` checks all returned HTTP
`200`. The HTTP server PID is `60752`, and the Cloudflared PID is `60408`. Use
S300 as the current public larger-job Blender sample endpoint while S292 remains
active separately as the full32 job-path proof endpoint.

S301 packaged the larger-job Blender sample proof:

- S301 package report:
  `docs/reports/cinematic_larger_renderer_job_sample_proof_package_s301.md`
- S301 plan:
  `docs/superpowers/plans/2026-06-20-larger-renderer-job-sample-proof-package.md`
- S301 package JSON:
  `build/shots/s301_larger_renderer_job_sample_proof_package/review_package.json`

S301 collects `12` visual/metadata artifacts from the S299 gallery and `4`
summary sources: the S295 larger renderer job, S299-vs-S291 comparison, S300
publish manifest, and S297 preview publish manifest. Use S301 as the current
handoff package for the larger-job Blender sample proof before longer
larger-job renders or non-Blender external renderer adapters.

S302 scaled the larger-job Blender proof to 24 sampled frames:

- S302 render report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample24_s302.md`
- S302 comparison report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample24_compare_s302.md`
- S302 gallery report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample24_gallery_s302.md`
- S302 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job-blender-sample24.md`
- S302 gallery:
  `build/shots/s302_larger_external_renderer_job_blender_sample24/gallery/index.html`

S302 renders the S295 larger job through Blender for `24` frames at `960 x
540`, `12` samples, using source window `0..47` and the accepted
`dam_break_water_mesh_smoothing` preset. Blender elapsed time is `120208.43`
ms, minimum nonblank ratio is `1.0`, minimum contrast is `128.0`, first/last
water mesh face counts are `20000` and `22300`, and first/last secondary totals
are `256` and `964`. Against a matched S291 sample, nonblank delta is `0.0`,
mean luma p99 delta is `0.0833333333333286`, mean specular ratio delta is
`-3.215020576131689e-06`, and mean frame contrast delta is `-0.25`. Use S302 as
the stronger larger-job Blender proof before publish, package, or full
48-frame render attempts.

S303 published the S302 larger-job 24-frame Blender sample gallery:

- S303 publish report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample24_publish_s303.md`
- S303 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job-blender-sample24-publish.md`
- S303 manifest:
  `build/shots/s303_larger_external_renderer_job_blender_sample24_publish/publish_manifest.json`
- S303 public URL:
  `https://animals-zealand-fcc-thursday.trycloudflare.com`

S303 stops the S300 12-frame larger-job endpoint, serves the S302 24-frame
gallery on local port `8903`, and starts a new Cloudflare quick tunnel. Local
and public `index.html` plus `assets/shot.gif` checks all returned HTTP `200`.
The HTTP server PID is `17836`, and the Cloudflared PID is `160000`. Use S303
as the current public larger-job 24-frame Blender sample endpoint while S292
remains active separately as the full32 job-path proof endpoint.

S304 packaged the S302/S303 larger-job 24-frame Blender proof:

- S304 package report:
  `docs/reports/cinematic_larger_renderer_job_sample24_proof_package_s304.md`
- S304 plan:
  `docs/superpowers/plans/2026-06-20-larger-renderer-job-sample24-proof-package.md`
- S304 package JSON:
  `build/shots/s304_larger_renderer_job_sample24_proof_package/review_package.json`

S304 collects `12` visual/metadata artifacts from the S302 gallery and `4`
summary sources: the S295 larger renderer job, the S302-vs-S291 comparison,
the S303 publish manifest, and the S301 12-frame proof package. Use S304 as
the current larger-job 24-frame proof package before full 48-frame renders or
non-Blender external renderer adapters.

S305 rendered the full 48-frame larger-job Blender proof:

- S305 render report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_full48_s305.md`
- S305 comparison report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_full48_compare_s305.md`
- S305 gallery report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_full48_gallery_s305.md`
- S305 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job-blender-full48.md`
- S305 gallery:
  `build/shots/s305_larger_external_renderer_job_blender_full48/gallery/index.html`

S305 renders all `48` frames from the S295 larger job at `960 x 540`, `12`
samples, using the accepted `dam_break_water_mesh_smoothing` preset. Blender
elapsed time is `238031.96` ms, minimum nonblank ratio is `1.0`, minimum
contrast is `106`, first/last secondary totals are `256` and `964`, and the
GIF is `17138447` bytes. Against S302 using `24` sampled frame pairs, nonblank
delta is `0.0`, mean luminance delta is `0.021145431455749986`, and mean frame
contrast delta is `-4.125`. Use S305 as the strongest local larger-job Blender
visual proof before public publish, packaging, or non-Blender external renderer
adapter work.

S306 published the S305 full48 Blender gallery:

- S306 publish report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_full48_publish_s306.md`
- S306 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-job-blender-full48-publish.md`
- S306 manifest:
  `build/shots/s306_larger_external_renderer_job_blender_full48_publish/publish_manifest.json`
- S306 public URL:
  `https://combined-ion-bowl-ted.trycloudflare.com`

S306 stops the S303 24-frame larger-job endpoint, serves the S305 full48
gallery on local port `8903`, and starts a new Cloudflare quick tunnel. Local
and public `index.html` plus `assets/shot.gif` checks all returned HTTP `200`.
The HTTP server PID is `59524`, and the Cloudflared PID is `44484`. Use S306
as the current public larger-job full48 Blender proof endpoint while S292
remains active separately as the full32 job-path proof endpoint.

S307 packaged the S305/S306 full48 larger-job Blender proof:

- S307 package report:
  `docs/reports/cinematic_larger_renderer_job_full48_proof_package_s307.md`
- S307 plan:
  `docs/superpowers/plans/2026-06-20-larger-renderer-job-full48-proof-package.md`
- S307 package JSON:
  `build/shots/s307_larger_renderer_job_full48_proof_package/review_package.json`

S307 collects `12` visual/metadata artifacts from the S305 gallery and `4`
summary sources: the S295 larger renderer job, the S305-vs-S302 sampled
comparison, the S306 publish manifest, and the S304 sample24 proof package. Use
S307 as the current full48 larger-job Blender proof package before non-Blender
external renderer adapters or larger simulation-scale jobs.

S308 added a renderer-neutral adapter manifest path for non-Blender renderers:

- S308 tool:
  `tools/build_external_renderer_adapter_manifest.py`
- S308 report:
  `docs/reports/cinematic_larger_external_renderer_generic_adapter_s308.md`
- S308 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-generic-adapter.md`
- S308 manifest:
  `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- S308 command list:
  `build/shots/s308_larger_external_renderer_generic_adapter/render_commands.txt`

S308 consumes the S295 `lsfs_external_renderer_job`, uses S305 as the look
reference, and links S307/S306 as proof package and public manifest context. It
emits `48` renderer-neutral scene descriptor JSON files for
`generic_path_tracer`, with `0` missing assets, monotonic frame order, minimum
water mesh faces `17720`, and a referenced asset footprint of `2.05 GB`. Use
S308 as the non-Blender adapter contract before writing a renderer-specific
backend or invoking a real offline renderer.

S309 added a dry-run backend validator for the S308 adapter manifest:

- S309 tool:
  `tools/validate_external_renderer_adapter_manifest.py`
- S309 report:
  `docs/reports/cinematic_larger_external_renderer_generic_backend_validation_s309.md`
- S309 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-generic-backend-validation.md`
- S309 validation JSON:
  `build/shots/s309_larger_external_renderer_generic_backend_validation/backend_validation.json`

S309 reads all `48` S308 scene descriptors, verifies required `json_camera`,
`obj`, and `csv` inputs, checks command-list count and path matching, and
confirms sequential output frames. It reports `0` failures, `1` expected
warning for the missing placeholder `generic_path_tracer` executable, `0`
command mismatches, and a referenced asset footprint of `2.05 GB`. Use S309 as
the backend dry-run gate before implementing a renderer-specific adapter.

S310 added a concrete Mitsuba XML export backend:

- S310 tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- S310 report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_s310.md`
- S310 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-xml.md`
- S310 export JSON:
  `build/shots/s310_larger_external_renderer_mitsuba_xml/mitsuba_export.json`
- S310 command list:
  `build/shots/s310_larger_external_renderer_mitsuba_xml/mitsuba_render_commands.txt`

S310 consumes the S308 adapter manifest and emits `48` Mitsuba XML scene files.
Each scene connects the accepted camera and water OBJ mesh, while preserving
phase-cell CSV and particle CSV paths as sidecar contracts. The export reports
`0` failures, `80.07 MB` of referenced water meshes, and `74.38 KB` of XML
scene files. Use S310 as the first concrete non-Blender scene format before
Mitsuba executable validation, particle proxy expansion, or volume conversion.

S311 added secondary particle proxy expansion to the Mitsuba XML exporter:

- S311 updated tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- S311 report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_proxy_s311.md`
- S311 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-proxy.md`
- S311 export JSON:
  `build/shots/s311_larger_external_renderer_mitsuba_secondary_proxy/mitsuba_export.json`
- S311 command list:
  `build/shots/s311_larger_external_renderer_mitsuba_secondary_proxy/mitsuba_render_commands.txt`

S311 keeps secondary proxy export opt-in via `--secondary-proxy-limit`, reads the
particle CSV secondary channels, samples proxy spheres while preserving
`spray`, `foam`, `bubble`, and `droplet` channel distribution, and emits
per-channel diffuse BSDFs plus Mitsuba sphere shapes. The S311 full48 export
emits `4608` secondary proxies from `15413` available secondary particles, with
`0` failures, `80.07 MB` of water meshes, and `995.47 KB` of XML scene files.
Sample frames `0000`, `0024`, and `0047` each parse as XML and contain `1`
water OBJ shape plus `96` secondary sphere shapes. Use S311 as the first
non-Blender scene export where secondary particles are actual renderer scene
geometry rather than sidecar-only data.

S312 added sparse phase-volume proxy expansion to the Mitsuba XML exporter:

- S312 updated tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- S312 report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_phase_proxy_s312.md`
- S312 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-phase-proxy.md`
- S312 export JSON:
  `build/shots/s312_larger_external_renderer_mitsuba_phase_proxy/mitsuba_export.json`
- S312 command list:
  `build/shots/s312_larger_external_renderer_mitsuba_phase_proxy/mitsuba_render_commands.txt`

S312 keeps phase proxy export opt-in via `--phase-volume-proxy-limit`, reads
phase-cell CSV rows with positive `liquid_volume`, samples sparse phase-volume
proxy spheres, and emits a phase-volume diffuse BSDF. The S312 full48 export
emits `4608` secondary proxies and `3072` phase-volume proxies from `15413`
available secondary particles and `261158` available phase-volume cells, with
`0` failures, `80.07 MB` of water meshes, and `1.52 MB` of XML scene files.
Sample frames `0000`, `0024`, and `0047` each parse as XML and contain `1`
water OBJ shape plus `160` proxy sphere shapes. Use S312 as the first
non-Blender scene export where water mesh, secondary particles, and sparse phase
volume are all represented as renderer scene geometry.

S313 added a Mitsuba XML export validation gate:

- S313 tool:
  `tools/validate_mitsuba_xml_export.py`
- S313 report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_validation_s313.md`
- S313 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-validation.md`
- S313 validation JSON:
  `build/shots/s313_larger_external_renderer_mitsuba_xml_validation/mitsuba_validation.json`

S313 parses all `48` S312 XML scenes, verifies `48` Mitsuba command lines,
counts `48` water OBJ shapes, `7680` proxy sphere shapes, and `288` BSDFs, and
reports `0` failures. It records `1` expected warning:
`mitsuba_executable_missing`, because `mitsuba` is not installed or not on PATH.
Use S313 to distinguish the now-valid XML scene contract from the remaining
external renderer executable dependency.

S314 added a visual preview path for Mitsuba XML geometry before Mitsuba is
installed:

- S314 tool:
  `tools/preview_mitsuba_xml_export.py`
- S314 preview report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_s314.md`
- S314 gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_gallery_s314.md`
- S314 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-xml-preview.md`
- S314 preview summary:
  `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/frames/render_summary.json`
- S314 gallery:
  `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/gallery/index.html`

S314 parses the S312 XML scenes, projects water OBJ vertices plus phase/secondary
proxy sphere geometry into `48` `960 x 540` top-down PNG frames, assembles a
`1254704` byte GIF, and builds a static gallery. The preview reports minimum
occupancy `0.07859760802469136`, `7680` total sphere shapes, and up to `7000`
water vertices drawn per frame. This is not a physically rendered image, but it
is the first inspectable visual artifact generated from the non-Blender XML
scene bundle itself.

S315 published the S314 Mitsuba XML geometry preview gallery:

- S315 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_publish_s315.md`
- S315 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-xml-preview-publish.md`
- S315 manifest:
  `build/shots/s315_larger_external_renderer_mitsuba_xml_preview_publish/publish_manifest.json`
- S315 public URL:
  `https://assign-pig-beauty-lots.trycloudflare.com`

S315 serves the S314 preview gallery on local port `8904` and starts a new
Cloudflare quick tunnel. Local and public `index.html` plus `assets/shot.gif`
checks all returned HTTP `200`. The HTTP server PID is `112016`, and the
Cloudflared PID is `156892`. Use S315 as the public non-Blender XML geometry
preview while S306 remains active separately as the public full48 Blender render
proof endpoint.

S316 tuned the Mitsuba XML geometry preview for clearer channel review:

- S316 updated tool:
  `tools/preview_mitsuba_xml_export.py`
- S316 preview report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_tuned_s316.md`
- S316 gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_tuned_gallery_s316.md`
- S316 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-xml-preview-tuned.md`
- S316 preview summary:
  `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/frames/render_summary.json`
- S316 gallery:
  `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/gallery/index.html`

S316 adds opt-in review look controls to the XML preview renderer: water alpha,
water point scale, phase proxy scale, secondary proxy scale, material counts,
and an optional frame legend. The tuned full48 preview uses `3600` water
vertices per frame, keeps `7680` proxy sphere shapes, reports minimum occupancy
`0.03595293209876543`, and produces a `1241823` byte GIF. The sphere material
counts are `3072` phase-volume, `2937` spray, `1187` foam, `484` bubble, and
`0` droplet proxies. Use S316 as the preferred non-Blender XML geometry review
view before actual Mitsuba rendering.

S317 published the S316 tuned Mitsuba XML geometry preview gallery:

- S317 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_tuned_publish_s317.md`
- S317 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-xml-preview-tuned-publish.md`
- S317 manifest:
  `build/shots/s317_larger_external_renderer_mitsuba_xml_preview_tuned_publish/publish_manifest.json`
- S317 public URL:
  `https://became-dodge-personal-thoroughly.trycloudflare.com`

S317 stops the S315 preview endpoint, serves the S316 tuned preview gallery on
local port `8904`, and starts a new Cloudflare quick tunnel. Local and public
`index.html` plus `assets/shot.gif` checks all returned HTTP `200`. The HTTP
server PID is `157712`, and the Cloudflared PID is `130076`. Use S317 as the
current public non-Blender XML geometry preview while S306 remains active
separately as the public full48 Blender render proof endpoint.

S318 packaged the tuned non-Blender XML preview proof chain:

- S318 package report:
  `docs/reports/cinematic_mitsuba_xml_preview_tuned_proof_package_s318.md`
- S318 plan:
  `docs/superpowers/plans/2026-06-20-mitsuba-xml-preview-tuned-proof-package.md`
- S318 package JSON:
  `build/shots/s318_mitsuba_xml_preview_tuned_proof_package/review_package.json`

S318 collects `10` visual/metadata artifacts from the S316 tuned gallery and
`5` summary sources: the S312 Mitsuba phase-proxy XML export, S313 XML
validation, S316 tuned preview summary, S317 tuned preview publish manifest,
and S306 Blender full48 publish manifest. Use S318 as the durable handoff
package tying the non-Blender XML scene contract, validation gate, public
preview endpoint, and Blender proof endpoint together before Mitsuba
installation or another renderer backend integration.

S319 added the first actual Mitsuba runtime render probe:

- S319 updated tools:
  `tools/export_external_renderer_mitsuba_xml.py`,
  `tools/validate_mitsuba_xml_export.py`
- S319 new tool:
  `tools/render_mitsuba_xml_export.py`
- S319 export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_command_fix_s319.md`
- S319 validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_command_validation_s319.md`
- S319 render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_render_probe_s319.md`
- S319 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-render-probe.md`
- S319 export JSON:
  `build/shots/s319_larger_external_renderer_mitsuba_render_probe/mitsuba_export.json`
- S319 render JSON:
  `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/mitsuba_render.json`

S319 fixes generated command lists from the invalid legacy
`mitsuba render ...` shape to `mitsuba -m scalar_rgb scene.xml -o frame.exr`,
adds command syntax validation for that regression, and introduces an opt-in
Mitsuba Python API runner. On this machine the runner uses Mitsuba `3.8.0` from
a build-local Python `3.11` venv and Visual Studio LLVM-C.dll through
`DRJIT_LIBLLVM_PATH`. The actual probe renders `3` selected XML frames to EXR
and PNG preview with `0` manifest failures, after validating all `48` XML
frames with `48` water OBJ shapes and `7680` proxy sphere shapes. The supervised
worker records Windows exit code `3221226505` after valid artifact writes, so
the ready manifest is the gate. Use S319 as the first proof that the external
Mitsuba path can produce real rendered frames, not only XML or software preview
geometry.

S320 packaged and published the actual Mitsuba renderer probe:

- S320 new tool:
  `tools/build_mitsuba_render_gallery.py`
- S320 gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_render_gallery_s320.md`
- S320 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_render_gallery_publish_s320.md`
- S320 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-render-gallery-publish.md`
- S320 gallery manifest:
  `build/shots/s320_larger_external_renderer_mitsuba_render_gallery/gallery/gallery_manifest.json`
- S320 publish manifest:
  `build/shots/s320_larger_external_renderer_mitsuba_render_gallery_publish/publish_manifest.json`
- S320 public URL:
  `https://ordinary-millions-analytical-lib.trycloudflare.com`

S320 reads the S319 `lsfs_mitsuba_xml_render` manifest, copies the `3` actual
Mitsuba PNG preview frames into a static gallery, assembles a `165682` byte
`assets/shot.gif`, and exposes the render/export JSON metadata. The Cloudflare
publish gate verified public `index.html` with HTTP `200` and `3165` bytes plus
public `assets/shot.gif` with HTTP `200` and `165682` bytes. Use S320 as the
first externally shareable proof of actual Mitsuba renderer output. It is still
a runtime proof (`spp=1`, `3` frames), not final cinematic look development.

S321 added a closer actual Mitsuba visual proof:

- S321 updated tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- S321 export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_export_s321.md`
- S321 validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_validation_s321.md`
- S321 render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_render_s321.md`
- S321 gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_gallery_s321.md`
- S321 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_publish_s321.md`
- S321 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-closeup-proof.md`
- S321 public URL:
  `https://cooling-pts-cups-skating.trycloudflare.com`

S321 extends the Mitsuba XML exporter with opt-in camera, sample, background
radiance, and water roughness overrides. The S321 close-up XML bundle keeps all
`48` source frames valid, disables phase-volume diagnostic proxies, retains
secondary proxy spheres, and renders `8` selected frames at `spp=4` with `0`
manifest failures. The published gallery assembles a `1261101` byte actual
Mitsuba GIF and verifies public `index.html` plus `assets/shot.gif` with HTTP
`200`. Use S321 as the current actual-Mitsuba visual proof. It is materially
more readable than S319/S320, but still needs renderer-side material, lighting,
and secondary representation work before it can be judged as cinematic look
development.

S322 added masked secondary-proxy material control:

- S322 updated tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- S322 export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_export_s322.md`
- S322 validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_validation_s322.md`
- S322 render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_render_s322.md`
- S322 gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_gallery_s322.md`
- S322 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_publish_s322.md`
- S322 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-mask.md`
- S322 public URL:
  `https://evaluate-inns-suppliers-wright.trycloudflare.com`

S322 adds `--secondary-opacity` to the Mitsuba XML exporter. When set, the
secondary channel diffuse BSDFs are wrapped in Mitsuba `mask` BSDFs so spray,
foam, bubble, and droplet proxies are no longer forced to render as fully
opaque spheres. A rejected large-radius experiment made secondary particles read
as large blue dots, so the committed proof uses the S321 close-up setup with
`192` secondary proxies per frame, `0.14` base radius, and `0.22` secondary
opacity. The resulting actual Mitsuba render keeps all `48` XML frames valid,
renders `8` selected frames at `spp=4` with `0` manifest failures, and publishes
a `1289627` byte GIF with public HTTP `200` checks. Use S322 as the current
secondary-material knob proof, while noting that real cinematic mist/foam still
needs a non-sphere or volumetric representation.

S323 added a screen-space secondary composite path:

- S323 new tool:
  `tools/composite_mitsuba_secondary_layer.py`
- S323 composite report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_composite_subtle_s323.md`
- S323 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_composite_publish_s323.md`
- S323 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-composite.md`
- S323 composite summary:
  `build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/secondary_composite_summary.json`
- S323 public URL:
  `https://fixes-achieve-pledge-cells.trycloudflare.com`

S323 reads the S322 actual Mitsuba render manifest, matches each rendered frame
back to its XML/export frame, parses the Mitsuba camera, projects secondary
particle CSV rows into screen space, builds blurred RGBA mist/foam layers, and
composites those layers over the actual Mitsuba PNG previews. The subtle proof
projects `2877 / 2877` selected secondary particles across `8` frames, reaches
maximum layer coverage `0.13125578703703702`, publishes a `1360178` byte GIF,
and verifies public `index.html` plus `assets/shot.gif` with HTTP `200`. Use
S323 as the first non-sphere secondary representation proof. It is currently a
post-composite approximation, not yet a renderer contract or volumetric model.

S324 added a restrained cinematic review grade for the actual Mitsuba composite:

- S324 new tool:
  `tools/grade_mitsuba_composite.py`
- S324 grade report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_composite_grade_soft_s324.md`
- S324 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_composite_grade_publish_s324.md`
- S324 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-composite-grade.md`
- S324 grade summary:
  `build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/grade_summary.json`
- S324 public URL:
  `https://hydrocodone-becomes-attempted-unified.trycloudflare.com`

S324 reads the S323 secondary composite frames and applies a post-render review
grade with exposure `1.02`, contrast `1.12`, saturation `1.08`, mild highlight
bloom, cool tone, and vignette. A harsher first grade was rejected because it
crushed water detail. The committed soft grade publishes an `8` frame,
`3010803` byte GIF and verifies public `index.html` plus `assets/shot.gif` with
HTTP `200`. Use S324 as the current most readable public proof, while noting
that it is a review-grade post-process rather than physically based renderer
look development.

S325 added a renderer-review contract for the current public Mitsuba proof:

- S325 new tool:
  `tools/build_mitsuba_renderer_review_contract.py`
- S325 contract report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_review_contract_s325.md`
- S325 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-review-contract.md`
- S325 contract JSON:
  `build/shots/s325_mitsuba_renderer_review_contract/renderer_review_contract.json`
- Current public proof URL:
  `https://hydrocodone-becomes-attempted-unified.trycloudflare.com`

S325 follows the S324 grade summary back through the S323 secondary composite,
the S322 actual Mitsuba render manifest, and the S322 Mitsuba XML export
manifest. It emits a `ready` `lsfs_mitsuba_renderer_review_contract` with `8`
matched grade/composite/render frames, `0` missing frame assets, source hashes,
artifact hashes, public review metadata, and renderer-facing expectations for
promoting the secondary layer and grade settings out of ad hoc post-processing.
Use S325 as the handoff contract for the next rendering stage.

S326 added a validator for the S325 renderer-review contract:

- S326 new tool:
  `tools/validate_mitsuba_renderer_review_contract.py`
- S326 validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_review_contract_validation_s326.md`
- S326 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-review-contract-validation.md`
- S326 validation JSON:
  `build/shots/s326_mitsuba_renderer_review_contract_validation/validation.json`

S326 checks the contract schema/version/status, source JSON hashes and schemas,
gallery artifact hashes/sizes, frame count consistency, per-frame base preview,
secondary layer, composite, and graded frame paths, graded frame hashes,
projected particle counts, and layer coverage bounds. The committed validation
run also enabled public URL probing and passed `77` checks with `0` failures and
`0` skipped checks. Use S326 as the regression gate before changing the
external-renderer handoff, secondary representation, or review-grade path.

S327 added a portable renderer handoff bundle:

- S327 new tool:
  `tools/build_mitsuba_renderer_handoff_bundle.py`
- S327 handoff bundle report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_handoff_bundle_s327.md`
- S327 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-handoff-bundle.md`
- S327 handoff manifest:
  `build/shots/s327_mitsuba_renderer_handoff_bundle/handoff_manifest.json`
- S327 bundle root:
  `build/shots/s327_mitsuba_renderer_handoff_bundle`

S327 reads the S325 contract and S326 validation, copies the contract,
validation, source metadata, gallery artifacts, and all selected per-frame base
preview, secondary layer, composite, and graded reference images into a portable
bundle. The generated `lsfs_mitsuba_renderer_handoff_bundle` is `ready`, covers
`8` frames, copies `41` files totaling `12.39 MB`, and has `0` missing
references. Use S327 as the renderer-facing reference package before replacing
the post-composite secondary layer and review grade with renderer-side
implementations.

S328 added a renderer target preview from the S327 handoff bundle:

- S328 new tool:
  `tools/build_mitsuba_renderer_target_preview.py`
- S328 target preview report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_preview_s328.md`
- S328 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_preview_publish_s328.md`
- S328 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-target-preview.md`
- S328 target preview summary:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- S328 public URL:
  `https://partnerships-cleaners-animals-gallery.trycloudflare.com`

S328 recomposes each S327 frame from the copied base preview plus secondary
layer, applies the accepted S324 grade settings from the handoff look intent,
and compares the generated renderer target against the accepted graded
reference. The generated `lsfs_mitsuba_renderer_target_preview` is `ready` for
`8` frames with `0` missing references, max composite mean absolute diff `0.0`,
and max target mean absolute diff `0.0`. The published gallery verifies public
`index.html` and `assets/shot.gif` with HTTP `200`. Use S328 as the visual target
reference for moving secondary and grade work into the actual renderer.

S329 added a validator for the S328 renderer target preview:

- S329 new tool:
  `tools/validate_mitsuba_renderer_target_preview.py`
- S329 validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_preview_validation_s329.md`
- S329 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-target-preview-validation.md`
- S329 validation JSON:
  `build/shots/s329_mitsuba_renderer_target_preview_validation/validation.json`

S329 checks the S328 summary schema/version/status, frame count, missing
reference count, composite and target diff thresholds, per-frame renderer
secondary, target, diff, and strip image paths, target image hashes, and the
published public URL when requested. The committed validation run passed `62`
checks with `0` failures and `0` skipped checks, including public HTTP `200`
checks for `index.html` and `assets/shot.gif`. Use S329 as the gate before
changing the renderer target preview or replacing it with a renderer-native
secondary/grade implementation.

S330 added an actual-Mitsuba versus target gap baseline:

- S330 new tool:
  `tools/compare_mitsuba_renderer_target_gap.py`
- S330 gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_gap_s330.md`
- S330 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_gap_publish_s330.md`
- S330 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-target-gap.md`
- S330 gap summary:
  `build/shots/s330_mitsuba_renderer_target_gap/renderer_target_gap_summary.json`
- S330 public URL:
  `https://dealt-sudden-mustang-grove.trycloudflare.com`

S330 compares the current actual Mitsuba baseline frames from the S327 handoff
bundle against the accepted S328 target preview, emits per-frame diff/strip
images, and publishes a gap gallery. The generated
`lsfs_mitsuba_renderer_target_gap` is `ready` for `8` frames with `0` missing
references, mean gap mean absolute diff `74.16963405028292`, max gap mean
absolute diff `104.48981417181069`, and max gap max absolute diff `153`. The
published gallery verifies public `index.html` and `assets/shot.gif` with HTTP
`200`. Use S330 to judge whether renderer-native material, secondary, and grade
changes actually move the Mitsuba output toward the accepted target.

S331 added the first renderer-native Mitsuba gap-reduction pass:

- S331 updated tool:
  `tools/compare_mitsuba_renderer_target_gap.py`
- S331 export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_export_s331.md`
- S331 render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_render_s331.md`
- S331 gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_target_gap_s331.md`
- S331 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_target_gap_publish_s331.md`
- S331 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-native-gap-pass.md`
- S331 public URL:
  `https://tan-afford-direct-wanting.trycloudflare.com`

S331 extends the target-gap comparison tool with `--actual-render-manifest`,
then exports and renders a calibrated actual Mitsuba pass with lower background
radiance, lower water alpha, more secondary proxies, and masked secondary
opacity. The new actual render is `ready` for `8` frames with `0` failures. The
new gap gallery is `ready` for `8` frames with `0` missing references, mean gap
mean absolute diff `55.544113136574076`, and max gap mean absolute diff
`85.7207773919753`, improving over S330's `74.16963405028292` mean and
`104.48981417181069` max. The published gallery verifies public `index.html`
and `assets/shot.gif` with HTTP `200`. Use S331 as the first measured
renderer-native improvement, while noting that the remaining gap still requires
a non-sphere secondary representation and renderer-side grade/material work.

S332 added a small Mitsuba native material/secondary sweep:

- S332 new tool:
  `tools/summarize_mitsuba_native_gap_sweep.py`
- S332 sweep summary report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_sweep_summary_s332.md`
- S332 best candidate gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_sweep_b_gap_s332.md`
- S332 best candidate publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_sweep_b_publish_s332.md`
- S332 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-native-gap-sweep.md`
- S332 public URL:
  `https://also-ringtone-compilation-only.trycloudflare.com`

S332 renders two additional actual Mitsuba candidates and ranks them against
S330 and S331. Candidate B is the new best renderer-native baseline with mean
gap mean absolute diff `37.73105774176955`, max gap mean absolute diff
`67.67647762345679`, and max gap max absolute diff `171`. Candidate C is worse
than B with max gap mean absolute diff `70.31346450617283`. Candidate B improves
over S331's `85.7207773919753` max gap and S330's `104.48981417181069` max gap.
The published B gallery verifies public `index.html` and `assets/shot.gif` with
HTTP `200`. Use S332-B as the next actual Mitsuba baseline, then spend the next
pass on replacing sphere secondary proxies with a softer or volumetric
renderer-side secondary representation.

S333 added opt-in Mitsuba secondary halo proxies:

- S333 updated tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- S333 sweep summary report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_sweep_summary_s333.md`
- S333 best candidate gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_h2_gap_s333.md`
- S333 best candidate publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_h2_publish_s333.md`
- S333 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-halo.md`
- S333 public URL:
  `https://timer-symbol-referrals-competent.trycloudflare.com`

S333 extends the Mitsuba XML exporter with `--secondary-halo-opacity` and
`--secondary-halo-radius-scale`. When enabled, each secondary proxy also emits a
larger low-opacity halo sphere with a dedicated halo BSDF. H1 and H2 both render
successfully, and H2 becomes the best ranked actual Mitsuba candidate with mean
gap mean absolute diff `37.58172702867798`, max gap mean absolute diff
`67.40660365226337`, and max gap max absolute diff `171`. This is only a small
improvement over S332-B's max gap `67.67647762345679`, so S333 confirms that
halo sphere proxies are useful as a temporary renderer-side baseline but are
not enough to replace the accepted screen-space secondary target. The next
renderer step should use a true screen-space or volumetric secondary
representation instead of only more sphere tuning.

S334 added a Mitsuba secondary overlay hybrid:

- S334 new tool:
  `tools/build_mitsuba_render_secondary_overlay.py`
- S334 overlay report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_overlay_hybrid_s334.md`
- S334 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_overlay_hybrid_publish_s334.md`
- S334 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-overlay-hybrid.md`
- S334 public URL:
  `https://laundry-tanks-prot-until.trycloudflare.com`

S334 reads the S333 H2 actual Mitsuba render, applies the accepted S327
secondary layer over each rendered preview, applies the accepted S328 grade
settings, and compares the result against the S328 target. The generated
`lsfs_mitsuba_render_secondary_overlay` is `ready` for `8` frames with `0`
missing references, mean overlay mean absolute diff `12.566030735596708`, max
overlay mean absolute diff `18.040229552469135`, and max overlay max absolute
diff `214`. This is the closest current visual bridge to the accepted target,
but it remains a hybrid post-render overlay. The next step should turn this
screen-space layer into a renderer-native screen-space pass or volumetric
secondary representation rather than stopping at the overlay.

S335 added a renderer-facing secondary pass contract:

- S335 new tool:
  `tools/build_mitsuba_secondary_pass_contract.py`
- S335 contract report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_pass_contract_s335.md`
- S335 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-pass-contract.md`
- S335 contract JSON:
  `build/shots/s335_mitsuba_secondary_pass_contract/secondary_pass_contract.json`
- S335 public URL:
  `https://laundry-tanks-prot-until.trycloudflare.com`

S335 reads the S334 overlay summary, follows the source chain to the S333 H2
actual Mitsuba render, S327 handoff bundle, and S328 target preview, and emits a
`ready` `lsfs_mitsuba_secondary_pass_contract`. The contract covers `8` frames,
has `0` missing frame assets, preserves source/artifact hashes, stores
per-frame overlay/target/diff mappings, and records mean overlay mean absolute
diff `12.566030735596708` plus max overlay mean absolute diff
`18.040229552469135`. Use S335 as the bridge contract for replacing the hybrid
screen-space overlay with a renderer-native secondary pass without losing the
current visual target gates.

S336 added a validation gate for the Mitsuba secondary pass contract:

- S336 new tool:
  `tools/validate_mitsuba_secondary_pass_contract.py`
- S336 validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_pass_contract_validation_s336.md`
- S336 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-pass-contract-validation.md`
- S336 validation JSON:
  `build/shots/s336_mitsuba_secondary_pass_contract_validation/validation.json`

S336 validates the S335 `lsfs_mitsuba_secondary_pass_contract` without
regenerating render assets. It checks schema/version/status, source JSON hashes
and schemas, review artifacts, required per-frame asset roles, per-frame asset
hashes, overlay diff metrics, output-frame ordering, and renderer-pass
semantics. The default run passed `187` checks with `0` failures and `2`
skipped optional public HTTP checks. A `--check-public` mode is available when a
Cloudflare quick tunnel is active, but the default gate treats quick tunnel
lifetime as external to the contract. Use S336 as the regression gate for the
next step: replacing the S334 screen-space secondary overlay with a
renderer-native Mitsuba secondary pass while preserving the S335 target-diff
contract.

S337 added a native Mitsuba secondary candidate gap gate:

- S337 new tool:
  `tools/compare_mitsuba_secondary_native_candidate.py`
- S337 candidate gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_native_candidate_gap_s337.md`
- S337 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-native-candidate-gap.md`
- S337 candidate gap summary:
  `build/shots/s337_mitsuba_secondary_native_candidate_gap/secondary_native_candidate_gap_summary.json`
- S337 gallery:
  `build/shots/s337_mitsuba_secondary_native_candidate_gap/gallery/index.html`

S337 compares the current best native Mitsuba candidate, S333 H2, against the
S335 secondary-pass contract. It matches frames by `output_frame` and compares
the candidate preview against both the contract `overlay_graded` frame and the
accepted target frame. The run is `ready` for `8` frames with `0` missing
references, but the verdict is `candidate_needs_work`: S333 H2 has mean
candidate-to-target MAD `37.58172702867798` and max candidate-to-target MAD
`67.40660365226337`, while the S335 overlay contract is much tighter at mean
MAD `12.566030735596708` and max MAD `18.040229552469135`. Use S337 as the
replacement gate: a renderer-native secondary pass should not replace the
screen-space overlay contract until it beats both the mean and max target MAD.
The next renderer pass should focus on a screen-facing or soft-density
secondary representation instead of more opaque sphere/halo proxy tuning.

S338 added and measured opt-in Mitsuba secondary mist shell proxies:

- S338 updated tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- S338 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-mist-shells.md`
- S338 M1 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m1_export_s338.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m1_render_s338.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m1_candidate_gap_s338.md`
- S338 M2 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m2_export_s338.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m2_render_s338.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m2_candidate_gap_s338.md`

S338 extends the Mitsuba XML exporter with `--secondary-mist-opacity`,
`--secondary-mist-radius-scale`, `--secondary-mist-shells`, and
`--secondary-mist-shell-spacing`. These options are off by default and emit
larger low-opacity native sphere shells around selected secondary proxies.
After pinning the background radiance to the S333 H2 baseline
`0.16,0.23,0.32`, both tested candidates rendered successfully and produced a
small native improvement over H2 while still failing the S335 replacement gate.
M1 is the current best native Mitsuba candidate with mean candidate-to-target
MAD `37.286685796039094` and max `66.5063766718107`; M2 records mean
`37.38058802726338` and max `66.78048096707819`. Both improve over S333 H2's
max `67.40660365226337`, but both remain far from the S335 contract max
`18.040229552469135`. Keep S338 M1 as the current native baseline and keep the
background radiance pinned in later candidate exports.

S339 added and measured opt-in camera-facing Mitsuba secondary billboards:

- S339 updated tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- S339 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-billboards.md`
- S339 H2 rerender control reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_runtime_h2_rerender_control_s339.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_runtime_h2_rerender_control_candidate_gap_s339.md`
- S339 B4 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_billboard_b4_export_s339.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_billboard_b4_render_s339.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_billboard_b4_candidate_gap_s339.md`

S339 extends the Mitsuba XML exporter with `--secondary-billboard-opacity`,
`--secondary-billboard-radius-scale`, and `--secondary-billboard-aspect`. These
options are off by default and emit camera-facing `disk` shapes for selected
secondary proxies. A current-runtime H2 rerender reproduced the S337 baseline
with max candidate-to-target MAD `67.40660365226337`, confirming the measured
changes are not Mitsuba runtime drift. B4, an H2-plus-billboard candidate under
the same background, rendered successfully and records mean candidate-to-target
MAD `37.57644900977366` and max `67.3997678755144`. This is a tiny improvement
over H2 but worse than S338 M1. Keep billboard support as an experimental
native geometry path, but prefer S338 M1 as the current native Mitsuba
secondary baseline. The next concrete step should be a depth-aware
post-render/renderer-composite secondary pass because pure native geometry is
still far from the S335 screen-space contract.

S340 summarized the native Mitsuba secondary candidate sweep:

- S340 new tool:
  `tools/summarize_mitsuba_secondary_candidate_sweep.py`
- S340 sweep report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_native_candidate_sweep_s340.md`
- S340 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-native-candidate-sweep.md`
- S340 sweep summary:
  `build/shots/s340_mitsuba_secondary_native_candidate_sweep/candidate_sweep_summary.json`

S340 ranks H2, corrected S338 M1/M2, and S339 B4 using the same
`lsfs_mitsuba_secondary_native_candidate_gap` schema. The ranking is:
`mist_m1` max target MAD `66.5063766718107`, `mist_m2`
`66.78048096707819`, `billboard_b4` `67.3997678755144`, and H2
`67.40660365226337`. This makes S338 M1 the current best native Mitsuba
secondary baseline, but it is still far from the S335 overlay contract max
target MAD `18.040229552469135`. The next renderer step should use S340 as the
native baseline and move to a depth-aware renderer-composite or post-render
secondary pass.

S341 added a depth-aware post-render secondary composite bridge:

- S341 new tool:
  `tools/build_mitsuba_depth_aware_secondary_composite.py`
- S341 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-depth-aware-secondary-composite.md`
- S341 naive overlay baseline report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_mist_m1_overlay_baseline_s341.md`
- S341 C1-C4 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c1_s341.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c2_s341.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c3_s341.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c4_s341.md`

S341 uses S338 M1 as the native render input and the S335 secondary-pass
contract as the visual anchor. The tool builds a secondary alpha/depth proxy
from the contract secondary layer, keeps lower native contribution near
secondary pixels, and blends more native graded detail away from the secondary
mask. The naive M1 overlay baseline has mean target MAD
`29.154523855452673` and max `60.98076067386831`, so simply stacking the layer
over M1 is not enough. The depth-aware sweep improves sharply: C1 max target MAD
`16.35688014403292`, C2 `15.450580632716049`, C3 `14.571005658436214`, and C4
`19.998582175925925`. C3 is the best bridge candidate: it beats the S335
contract max target MAD `18.040229552469135` while retaining measured native
contribution from the S338 M1 render. Use C3 as the current post-render bridge
baseline. The next step should add a validator for the
`lsfs_mitsuba_depth_aware_secondary_composite` schema and publish/package the
C3 gallery for visual review.

S342 added a validation gate for the Mitsuba depth-aware secondary composite:

- S342 updated tool:
  `tools/build_mitsuba_depth_aware_secondary_composite.py`
- S342 new tool:
  `tools/validate_mitsuba_depth_aware_secondary_composite.py`
- S342 validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_validation_s342.md`
- S342 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-depth-aware-secondary-composite-validation.md`
- S342 validation JSON:
  `build/shots/s342_mitsuba_depth_aware_composite_validation/validation.json`

S342 validates the S341 C3
`lsfs_mitsuba_depth_aware_secondary_composite` without changing the bridge
metrics. It checks schema/version/status, source manifests and schemas, gallery
files, required per-frame assets, composite hashes, target/contract MAD gates,
output-frame ordering, and native-weight bounds. The run passed `129` checks
with `0` failures and `0` skipped checks. C3 remains ready with mean target MAD
`11.423722591949588`, max target MAD `14.571005658436214`, max contract MAD
`8.268018904320988`, and mean native weight `0.13702558967259743`. The builder
now marks the gallery copy of its own summary JSON as
`hash_policy: self_referential_json`, while the validator still records the
top-level composite summary SHA and validates all non-self-referential gallery
metadata hashes. The next step should package or publish the C3 gallery for
visual review, then continue toward a renderer-native depth/secondary pass that
can replace the post-render bridge.

S343 published the validated Mitsuba depth-aware composite C3 gallery:

- S343 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c3_publish_s343.md`
- S343 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-depth-aware-secondary-composite-publish.md`
- S343 publish manifest:
  `build/shots/s343_mitsuba_depth_aware_composite_c3_publish/publish_manifest.json`
- S343 public URL:
  `https://itself-auburn-steering-collectables.trycloudflare.com`

S343 serves `build/shots/s341_mitsuba_depth_aware_composite_c3/gallery`
through `tools/publish_cinematic_gallery.py --cftunnel`. The publish manifest
is `running` with local URL `http://127.0.0.1:8943`, HTTP server PID `153272`,
and cloudflared PID `37812`. The local and public checks passed for both
`index.html` and `assets/shot.gif`; the public GIF check returned HTTP `200`
with `2881913` bytes. Use this endpoint as the current external visual review
page for the depth-aware composite baseline. The quick-tunnel URL is
session-scoped, so refresh S343 if either recorded process exits. The next step
should start a renderer-native depth/secondary pass that tries to reproduce or
beat the C3 post-render bridge without relying on the screen-space contract
layer as the final composite source.

S344 added a renderer-native replacement gap gate against the C3 bridge:

- S344 new tool:
  `tools/compare_mitsuba_native_to_depth_aware_composite.py`
- S344 gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_s344.md`
- S344 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-depth-aware-native-replacement-gap.md`
- S344 gap summary:
  `build/shots/s344_mitsuba_depth_aware_native_replacement_gap_m1/depth_aware_native_replacement_gap_summary.json`
- S344 gap gallery:
  `build/shots/s344_mitsuba_depth_aware_native_replacement_gap_m1/gallery/index.html`

S344 compares the current best native Mitsuba secondary baseline, S338 M1,
against the validated S341 C3 depth-aware composite. The tool measures both
native-to-bridge error and native-to-accepted-target error. M1 remains far from
replacement quality: native mean target MAD is `37.286685796039094` versus C3
bridge `11.423722591949588`, and native max target MAD is
`66.5063766718107` versus C3 bridge `14.571005658436214`. Native-to-bridge
mean MAD is `40.380344087577164`, max `62.06783050411523`, with `8` frames and
`0` missing references. Use S344 as the native replacement gate: a future
renderer-native secondary pass should not replace the C3 bridge until it beats
both the C3 mean target MAD and C3 max target MAD.

S345 tested mist-plus-billboard native Mitsuba proxy candidates against the
S344 gate:

- S345 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-mist-billboard-sweep.md`
- S345 MB1 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb1_export_s345.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb1_render_s345.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb1_candidate_gap_s345.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_mb1_s345.md`
- S345 MB2 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb2_export_s345.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb2_render_s345.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb2_candidate_gap_s345.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_mb2_s345.md`

S345 keeps the S338 M1 camera/background/water/mist settings pinned and adds
two billboard stress candidates. MB1 uses billboard opacity `0.09`, radius
scale `2.5`, and aspect `1.25`; MB2 uses opacity `0.18`, radius scale `4.0`,
and aspect `1.4`. MB2 is the best measured native proxy candidate so far:
mean target MAD `37.13389178240741`, max target MAD `66.33950488683128`,
native-to-C3 mean MAD `40.225236062885806`, and native-to-C3 max MAD
`61.84939814814815`. This improves slightly over S338 M1 max target MAD
`66.5063766718107`, but it is still far from the C3 bridge max
`14.571005658436214`. Treat this as evidence that more sphere/mist/billboard
proxy strength alone is not enough. The next renderer-native pass should use a
more direct depth/secondary representation guided by C3/S335 masks.

S346 added a renderer-side secondary screen-card insertion path:

- S346 new tool:
  `tools/add_mitsuba_secondary_screen_cards.py`
- S346 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-screen-card.md`
- S346 SC1 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc1_export_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc1_render_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc1_candidate_gap_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_sc1_s346.md`
- S346 SC2 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc2_export_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc2_render_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc2_candidate_gap_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_sc2_s346.md`

S346 takes the S345 MB2 native export as a base and inserts per-frame
camera-facing rectangle cards using bitmap opacity masks generated from the
S341 C3 secondary layers. The output remains a valid
`lsfs_mitsuba_xml_export`, so the existing Mitsuba render tool can render it.
SC1 uses weak mask gain `0.6`; SC2 uses stronger mask gain `8.0` and emits `8`
screen cards plus `73.76 KB` of mask textures with `0` missing references.
Neither improves the S344 gate: SC2 mean target MAD is `37.13389475630144` and
max target MAD is `66.33952031893004`, effectively tied with MB2 and still far
from C3 bridge max `14.571005658436214`. Keep the screen-card tool as the next
renderer-native representation path, but tune depth placement, material
response, facing/orientation, and possibly multi-card placement before another
native replacement attempt.

S347 extended the secondary screen-card path with sprite mode:

- S347 updated tool:
  `tools/add_mitsuba_secondary_screen_cards.py`
- S347 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-secondary-screen-sprites.md`
- S347 SC3 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc3_export_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc3_render_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc3_candidate_gap_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_sc3_s347.md`
- S347 SC4 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc4_export_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc4_render_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc4_candidate_gap_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_sc4_s347.md`

S347 samples bright pixels from the secondary mask and projects them as small
camera-facing Mitsuba `disk` area emitters instead of relying on a single
textured rectangle. SC3 emits `4096` sprites across `8` frames; SC4 emits
`8192` sprites and is the current best native Mitsuba candidate by max target
MAD. SC4 records mean target MAD `37.13381309477881`, max target MAD
`66.33893840020576`, native-to-C3 mean MAD `40.2254558899177`, and
native-to-C3 max MAD `61.848001543209875`. This is a measurable but tiny
improvement over S345 MB2 max `66.33950488683128`, still far from the C3 bridge
max `14.571005658436214`. Treat sprite mode as useful renderer-native
infrastructure, but shift the next pass to native tone/background calibration
because the remaining gap is no longer explained by secondary mask placement
alone.

S348 calibrated native Mitsuba background/tone around the MB2 secondary setup:

- S348 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-tone-background-sweep.md`
- S348 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_tb*_export_s348.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_tb*_render_s348.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_tb*_candidate_gap_s348.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_tb*_s348.md`

S348 keeps camera, water alpha, secondary proxy, halo, mist, and billboard
settings pinned, then sweeps background radiance from TB1 to TB7. This is the
largest native-render improvement so far. S347 SC4 had mean target MAD
`37.13381309477881` and max target MAD `66.33893840020576`; TB6 lowers that to
mean target MAD `19.411650913065845` and max target MAD
`24.390221193415638`. TB1 has the best mean target MAD at
`16.39866785622428`, but TB6 has the best max target MAD and should be treated
as the current native replacement baseline. It still does not beat the S335
contract max `18.040229552469135` or S341 C3 bridge max
`14.571005658436214`. Continue from TB6 rather than the brighter S345/S347
baseline.

S349 tested TB6 plus the S347 screen-sprite secondary path:

- S349 plan:
  `docs/superpowers/plans/2026-06-20-larger-external-renderer-mitsuba-tone-sprite-combination.md`
- S349 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_screen_sprites_ts1_export_s349.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_screen_sprites_ts1_render_s349.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_screen_sprites_ts1_candidate_gap_s349.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_ts1_s349.md`

S349 uses S348 TB6 as the base export and adds SC4-style screen sprites from
the C3 secondary mask. TS1 is slightly worse than TB6: mean target MAD
`19.41354994534465` versus TB6 `19.411650913065845`, and max target MAD
`24.39063721707819` versus TB6 `24.390221193415638`. Do not keep the current
screen-sprite path on top of the calibrated TB6 baseline. Continue from TB6 and
move to native material/water/secondary tuning or a TB6-based post-render bridge
refresh.
