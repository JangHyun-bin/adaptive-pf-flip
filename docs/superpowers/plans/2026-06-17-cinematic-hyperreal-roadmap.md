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

Continue with S60.

The next implementation plan should be:

`docs/superpowers/plans/2026-06-18-contact-splash-secondary-visibility.md`

The next command target should start from:

```powershell
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s60_contact_splash --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s60.md --timeout-seconds 1500
```

The next success condition is a large water-event shot where contact with the pool produces more visible spray/splash breakup instead of only smooth sheet and pool surfaces.
