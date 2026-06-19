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
