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
