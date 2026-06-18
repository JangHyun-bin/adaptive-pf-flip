# lsfs — Adaptive Phase-Field-FLIP, from scratch

A faithful, test-driven, **incremental reimplementation** of the hybrid Eulerian/Lagrangian fluid solver from:

> Bernhard Braun, Jan Bender, Nils Thuerey.
> **"Adaptive Phase-Field-FLIP for Very Large Scale Two-Phase Fluid Simulation."**
> *ACM Transactions on Graphics 44(4), Article 42 (SIGGRAPH 2025).* [doi:10.1145/3730854](https://doi.org/10.1145/3730854)

The goal is to rebuild the method **algorithmically identical** to the paper — same equations, same algorithms, same data structures (MSBG) — growing it one validated phase at a time. Everything is C++17, built with CMake, and covered by [doctest](https://github.com/doctest/doctest) unit + integration tests.

> ⚠️ This reproduces the paper's *method*; it does not aim for bit-identical reproduction of the paper's tables/figures (the original adaptive-Poisson solver and exact constants are not public, and the reference hardware has 2× the RAM). See `docs/superpowers/specs/` for the explicit fidelity contract.

---

## Results so far

| 2D core (Phase 0) | 3D (Phase 1) |
|---|---|
| ![2D dam-break](assets/dambreak-2d.gif) | ![3D dam-break](assets/dambreak-3d.gif) |
| 64² grid, 4,128 particles | 48³ grid, 211,968 particles (mid-z slice) |

Both show a classic dam-break: gravity-driven collapse → floor surge → wall run-up → sloshing.

**Phase 2 — two-phase phase field (the paper's core).** Below: a Rayleigh-Taylor instability (heavy water over light air) resolved with **no surface reconstruction** — the phase field is a by-product of the particle-to-grid splat (Eq. 7), and buoyancy emerges from the variable-coefficient β=1/ρ pressure solve (Eq. 8).

![Rayleigh-Taylor two-phase](assets/rayleigh-taylor-2phase.gif)

*(blue = water, dark = air; 64×96 grid — classic RT mushroom fingering)*

**Rough rendering (Phase R).** The same two-phase RT, exported and shaded as a smooth volumetric water body with a surface highlight (`apps/dump_render.cpp` → `tools/rough_render.py`) — a rough stand-in for the paper's ray tracer.

![Rough volumetric render](assets/water-rough-render.gif)

**Sparse FLIP (Phase A).** The single-phase dam-break running entirely on the Phase 3 sparse block grid — blue = particles, dark green = the **only blocks actually allocated** (max 64/192 across the whole 128×96 run). Storage follows the fluid; the rest of the domain never exists in memory.

![Sparse dam-break](assets/sparse-dambreak-2d.gif)

**Sparse two-phase (Phase B).** The paper's core solver running on the paper's storage: a gas bubble (amber) rising through water (blue) by buoyancy that **emerges purely from the β=1/ρ variable-coefficient pressure solve** — no explicit buoyancy force — on sparse block storage. The bubble deforms into a cap and splits into a vortex pair (classic 2D behavior without surface tension); the free surface bulges; and the empty headspace **never allocates** (max 78/144 cell blocks across the 96² run).

![Sparse two-phase bubble](assets/sparse-bubble-2phase.gif)

---

## Roadmap

This is **SPEC-1** (the faithful core), decomposed into phases. Each phase produces working, tested software on its own.

| Phase | Adds | Status |
|---|---|---|
| **0** | 2D MAC FLIP/PIC, pressure CG, RK2 advect, dam-break | ✅ done |
| **1** | **3D** extension, viscosity (Eq. 13), velocity extrapolation | ✅ done |
| **2** ★ | **Two-phase phase field** (Eq. 7), variable-coefficient β=1/ρ Poisson (Eq. 8), cubic kernel (Eq. 6) — validated by Rayleigh-Taylor | ✅ done — *the paper's identity* |
| **2c** | **3D** two-phase (3D air-water): 3D normalized-cubic P2G, 3D variable-coefficient Poisson, 3D Rayleigh-Taylor | ✅ done |
| **R** | **Rough rendering** — particle export + density-splat shading (volumetric-ish water look), *not* the paper's exact ray tracer | ✅ done |
| **3** | **Sparse block grid** — our own clean-MSVC reimplementation of MSBG's concepts (treeless, large blocks, dense block-pointer array, block pool, 4/8-color). The real [MSBG](https://github.com/tum-pbs/MSBG) is GCC/Make/POSIX-only and won't build/link on MSVC, so we rebuilt the ideas. Validated: **same result as the uniform grid, sparse storage** (only active blocks allocated). *Single-resolution; multiresolution → Phase 3b.* | ✅ done |
| **A** | **Sparse FLIP** — the Phase 3 grid wired into a real solver: 2D single-phase FLIP (MAC fields as sparse block fields, P2G activates only touched blocks, pressure CG enumerates fluid cells) with the dam-break matching the uniform solver's behavior. **Payoff demonstrated: max 64/192 blocks allocated** in the 128×96 run. *Two-phase/3D/multiresolution on sparse → later.* | ✅ done |
| **B** | **Sparse two-phase** — Phase 2's phase-field FLIP (Eq. 6 cubic kernel, Eq. 7 φ, Eq. 8 β=1/ρ Poisson with Neumann pin) ported onto the sparse grid, with β computed on the fly from face raw densities (no extra storage). Validated two ways: sparse Rayleigh-Taylor overturns like the dense solver (equivalence), and a free-surface bubble tank where the **empty headspace never allocates — max 78/144 cell blocks** (sparsity). *Narrow-band air for full-domain two-phase → SPEC-2.* | ✅ done |
| **C** | **Multires sparse-grid path** - 2D multires layout, scalar/MAC grids, transfer, pressure projection, bubble simulation, and visualization runner. | done |
| **D1** | **Sparse 3D FLIP** - 3D sparse block/MAC grids, 8-color transfer, sparse 3D pressure projection, and a single-phase sparse 3D simulation step. | done |
| **D2** | **Sparse 3D two-phase** - 3D sparse phase-field FLIP, variable-coefficient pressure, RT/bubble validation, and demo runners. | done |
| **E1** | **3D multires foundation** - 3D multires layout, scalar grid, and MAC face-patch enumeration for the later 3D multires pressure/transfer path. | done |
| **E2** | **3D multires transfer** - 3D two-phase P2G/G2P/advect on multires MAC face patches, with mass-normalized u/v/w transfer tests. | done |
| **E3** | **3D multires pressure system** - 3D finite-volume cell volumes, face-area conductance, and coarse-fine pressure graph tests. | done |
| **E4** | **3D multires projection** - 3D marker-aware variable-coefficient pressure projection with solid-face zeroing. | done |
| **E5** | **3D multires two-phase validation** - 3D multires bubble scene, sim step loop, and metrics-only validation runner. | done |
| **E8** | **3D multires visual demo** - 3D multires bubble slice writer and `mrb3_###.ppm` demo runner. | done |
| **E9** | **Sparse vs 3D multires benchmark** - paired sparse/MR bubble metrics for particles, rise, pressure cells, face counts, and elapsed time. | done |
| **E10** | **3D multires performance cleanup** - cached 3D face enumeration and local-radius multires transfer for the P2G hot path. | done |
| **E11** | **3D multires dynamic refinement** - per-step particle/gas occupancy driven 3D layout refresh with coarse headspace preserved. | done |
| **E12** | **3D multires refinement stability** - retained-box hysteresis and optional fine-leaf budget controls for dynamic refinement. | done |
| **F1** | **SPEC-3 solver prep** - 3D multires pressure solve stats for iterations, residuals, convergence, breakdown, and high-density-ratio smoke coverage. | done |
| **F2** | **SPEC-3 adaptive PCG baseline** - explicit 3D multires solve config with relative residual stopping and Jacobi preconditioner toggle/metrics. | done |
| **F3** | **SPEC-3 solver comparison harness** - 3D multires bubble workload runner comparing Jacobi abs/relative stopping and no-Jacobi relative stopping. | done |
| **F4** | **SPEC-3 adaptive PCG restart** - residual-growth restart guard, non-finite breakdown checks, and runner metrics/CLI toggles for 3D multires pressure solves. | done |
| **F5** | **SPEC-3 solver diagnostics** - optional residual-history sampling plus min/max residual metrics in 3D multires validation and benchmark runners. | done |
| **F6** | **SPEC-3 adaptive relaxation prep** - optional damped-Jacobi pre-relaxation with backoff, stats, and runner sweep controls before PCG. | done |
| **F7** | **SPEC-3 flexible CG prep** - selectable flexible-CG beta recurrence with beta-reset stats and a solver harness comparison variant. | done |
| **F8** | **SPEC-3 high-density validation gate** - 1000:1 density-ratio runner options with convergence, residual, and diagonal sanity checks. | done |
| **F9** | **SPEC-3 Galerkin MG prep** - volume-weighted residual norms, restriction/prolongation helpers, and Galerkin coarse pressure graph energy tests. | done |
| **F10** | **SPEC-3 coarse-correction scaffold** - one-shot Galerkin coarse correction helper with pinned weighted-CG solve and restricted-residual reduction tests. | done |
| **F11** | **SPEC-3 geometry aggregation** - level-1 pressure-cell aggregation from 3D multires grid geometry for Galerkin coarse correction. | done |
| **F12** | **SPEC-3 coarse-correction solver hook** - optional level-1 Galerkin coarse correction as a 3D multires projection initial guess with runner diagnostics. | done |
| **F13** | **SPEC-3 damped coarse correction** - multi-sweep damped coarse correction diagnostics for accepted/rejected sweeps and applied scale. | done |
| **F14** | **SPEC-3 coarse preconditioner probe** - optional additive level-1 coarse solve inside the 3D multires CG preconditioner with runner diagnostics. | done |
| **F15** | **SPEC-3 coarse preconditioner sweep** - solver bench sweep variants for coarse-preconditioner inner iterations and additive scale. | done |
| **F16** | **SPEC-3 solver bench summary** - baseline-relative iteration, elapsed, and coarse-work summaries for coarse-preconditioner sweeps. | done |
| **F17** | **SPEC-3 coarse preconditioner guard** - min-rz-gain acceptance guard and runner diagnostics for rejecting weak additive coarse solves. | done |
| **F18** | **SPEC-3 coarse preconditioner work cap** - max-work-ratio budget guard, skip diagnostics, and sweep variants for bounded coarse-pre work. | done |
| **F19** | **SPEC-3 coarse preconditioner auto-disable** - rejected/skip streak auto-disable plus solver-bench auto-selection diagnostics for coarse-pre variants. | done |
| **S1** | **SPEC-2 narrow-band air scaffold** - opt-in sparse 3D TP gas-particle pruning around liquid cells, compact particle erase, validator metrics, and pruning regression coverage. | done |
| **S2** | **SPEC-2 gas particle coarsening scaffold** - opt-in sparse 3D TP per-cell gas particle cap with adaptivity metrics and regression coverage. | done |
| **S3** | **SPEC-2 stochastic gas coarsening selection** - seed-based hash selection for reproducible per-cell gas particle coarsening. | done |
| **S4** | **SPEC-2 sparse adaptivity bench hook** - sparse-vs-MR bubble bench now reports an optional adaptive sparse run with narrow-band/coarsening metrics. | done |
| **S5** | **SPEC-2 multires particle adaptivity hook** - 3D multires TP sim and validator expose the same opt-in narrow-band and gas coarsening controls. | done |
| **S6** | **SPEC-2 paired adaptivity bench hook** - sparse-vs-MR bubble bench can now run optional adaptive sparse and adaptive MR variants side by side. | done |
| **S7** | **SPEC-2 shared 3D adaptivity helpers** - sparse and multires 3D TP sims now share the same narrow-band and stochastic gas-coarsening implementation. | done |
| **S8** | **SPEC-2 liquid particle coarsening scaffold** - sparse and multires 3D TP sims expose opt-in deterministic liquid particle caps through the shared adaptivity helper. | done |
| **S9** | **SPEC-2 liquid coarsening runner metrics** - sparse/MR validators and paired bench expose opt-in liquid coarsening CLI controls and metrics. | done |
| **S10** | **SPEC-2 per-phase particle metrics** - sparse/MR validators and paired bench report liquid/gas particle start/end counts for adaptivity audits. | done |
| **S11** | **SPEC-2 per-phase adaptivity gates** - validators and paired bench now enforce liquid/gas preserve-or-nonincrease rules based on enabled adaptivity options. | done |
| **S12** | **SPEC-2 liquid particle refill scaffold** - sparse and multires 3D TP sims can deterministically refill underfilled liquid cells up to an opt-in target. | done |
| **S13** | **SPEC-2 liquid refill runner metrics** - sparse/MR validators and paired bench expose opt-in liquid refill CLI controls, metrics, and bounded count gates. | done |
| **S14** | **SPEC-2 interface-only liquid refill** - optional refill policy now restores only liquid cells near gas, with sparse/MR tests and runner metrics. | done |
| **S15** | **SPEC-2 liquid refill add budget** - optional per-step refill budget caps particle creation and is enforced by sparse/MR validators and paired bench. | done |
| **S16** | **SPEC-2 liquid refill mass accounting** - runner gates now require run-time liquid refill additions to stay within liquid coarsening removals when both are enabled. | done |
| **S17** | **SPEC-2 volume-weighted particle adaptivity** - 3D TP particles carry volume multipliers, coarsen/refill redistributes volume, and runners gate phase volume/mass drift. | done |
| **S18** | **Physical residual particle boundary accounting** - sparse/MR 3D TP advect reports phase and axis boundary clamps as the scaffold for escaped-particle droplet/bubble handling. | done |
| **S19** | **Physical residual adaptive timestep** - sparse/MR 3D TP sims can opt into CFL-limited effective dt with validator and paired-bench diagnostics. | done |
| **S20** | **Physical residual RK3 advection option** - sparse/MR 3D TP advect can switch from midpoint RK2 to RK3, with validator and paired-bench controls. | done |
| **S21** | **Physical residual c_div volume correction** - sparse/MR 3D TP projections accept an opt-in divergence correction derived from liquid volume target error. | done |
| **S22** | **Physical residual escaped-particle classification** - sparse/MR 3D TP sims now classify boundary-clamped liquid as droplet candidates and gas as bubble candidates for later secondary-particle handling. | done |
| **S23** | **Physical residual escaped-particle branching scaffold** - opt-in sparse/MR 3D TP sims store boundary-clamped liquid/gas escape events into secondary droplet/bubble particle containers. | done |
| **S24** | **Physical residual interface diagnostics** - sparse/MR 3D TP sims report phase-interface gradient and curvature metrics so surface-tension work can be gated by measured interface behavior. | done |
| **S25** | **Physical residual surface tension scaffold** - sparse/MR 3D TP sims expose opt-in bounded CSF-style interface force with validator and paired-bench diagnostics. | done |
| **S26** | **Integrated physical validation preset** - sparse/MR 3D TP validators and paired bench expose short/long presets that combine adaptive timestep, RK3, c_div, escaped-particle branching, surface tension, and particle adaptivity gates. | done |
| **S27** | **Secondary particle lifecycle scaffold** - escaped droplet/bubble containers now support opt-in advection, lifetime expiry, reabsorption removal, age tracking, and count/volume accounting in sparse/MR validators and paired bench. | done |
| **S28** | **Surface tension validation hardening** - sparse/MR 3D TP surface tension now reports smoothed curvature, capillary stability limits, and strength-sweep gates for bounded bubble-shape validation. | done |
| **S29** | **SPEC-4 pre-render cache format** - sparse/MR 3D TP sims can export JSONL render caches containing camera metadata, water volume summaries, phase-field cells, primary particles, and secondary droplet/bubble particles. | done |
| **S30** | **Large-scale benchmark gate** - CSV runner records sparse vs MR, adaptivity on/off, solver option, memory-proxy, time, and pressure convergence metrics for larger 3D bubble workloads. | done |
| **S31** | **SPEC-4 cache preview tool** - JSONL render cache frames can be projected into quick PNG/GIF previews for schema and motion inspection before the full renderer exists. | done |
| **S32** | **SPEC-4 render cache manifest** - export runs now write a JSON sequence manifest and the preview tool can consume the manifest directly. | done |
| **S33** | **SPEC-4 render cache QA validator** - manifests and JSONL frames can be checked for schema, finite values, frame ordering, count consistency, and water-volume drift before rendering. | done |
| **S34** | **SPEC-4 secondary preview controls** - render-cache previews can color secondary droplet/bubble particles by type, age, or speed and isolate them from primary water. | done |
| **S35** | **Secondary particle physics upgrade** - sparse/MR 3D TP secondary droplets and bubbles expose dt-based drag, droplet gravity scale, buoyancy, and opt-in reabsorb-to-primary accounting. | done |
| **S36** | **Large-scale benchmark v2** - large-scale CSV runner now records per-phase counts, render-cache export bytes/time, cache validation time, preview time, and total memory proxy. | done |
| **S37** | **Cinematic cache schema v2** - render cache frames and manifests now carry v2 camera timing, world units, frame bounds, focal metadata, and secondary-channel summaries while preserving v1 compatibility markers. | done |
| **S38** | **Cache-to-render conversion** - validated render cache manifests can be converted into movable renderer-neutral bundles with per-frame camera JSON, particle CSV, phase-cell CSV, and `sequence.json`. | done |
| **S39** | **First cinematic preview renderer** - render cache manifests or converted sequences can now produce local `frame_####.png` previews, `preview.gif`, and occupancy QA summaries before external renderer integration. | done |
| **S40** | **Secondary render channels** - secondary particles now export droplet, spray, foam, and bubble render channels with validator cross-checks and preview isolation controls. | done |
| **S41** | **Water reconstruction export** - phase-cell render caches can now export dependency-free OBJ water mesh sequences with reconstruction indexes, converter attachment, and cinematic preview mesh overlays. | done |
| **S42** | **External renderer bridge** - converted cache bundles with OBJ water meshes can now generate Blender scene specs, dependency reports, and background-rendered PNG frame sequences through a documented bridge. | done |
| **S43** | **Cinematic shot pipeline** - a single runner can now export cache frames, validate, reconstruct water meshes, convert assets, render preview/Blender frames, assemble a GIF, and write `shot_summary.json`. | done |
| **S44** | **Cinematic render presets** - named presets now drive shot dimensions, renderer choice, camera, lighting, material, and tone-mapping values for the S43 runner and Blender bridge. | done |
| **S45** | **Large-scale cinematic gate** - the preset-driven shot runner now produces a 48-frame 1280x720 Blender gate, `shot_summary.json`, GIF, and checked-in report with metrics and limitations. | done |
| **S46** | **Smooth cinematic water meshes** - water reconstruction can now export opt-in smoothed OBJ vertices and vertex normals, with cinematic presets enabling smoother Blender shading by default. | done |
| **S47** | **Dynamic falling-water cinematic preset** - the render-cache exporter and shot runner now accept scene selection, and `dam_break_cinematic` drives a sparse 3D two-phase falling-water scene instead of the bubble tank. | done |
| **S48** | **Visible cinematic secondary particles** - the render-cache exporter can seed opt-in demo secondary droplets/bubbles per frame, and Blender rendering can scale those channels so spray, foam, droplets, and bubbles are visible in cinematic gates. | done |
| **S49** | **Cinematic camera motion** - Blender scene specs now precompute preset camera paths with smooth interpolation, dry-run summaries report motion status, and `dam_break_cinematic` uses a moving camera path. | done |
| **S50** | **Water material depth/rim pass** - Blender water materials now consume preset depth tint, rim highlight, specular, and coat controls, with shot reports recording the active water-material response. | done |
| **S51** | **Presentation artifact pack** - cinematic shot runs now emit a review contact sheet, keyframe thumbnails, and `review_manifest.json` alongside GIFs, reports, and `shot_summary.json`. | done |
| **S52** | **Visual gate v2** - `dam_break_cinematic` has a larger 36-frame 960x540 Blender gate with GIF, review pack, timings, material metrics, and a checked-in report. | done |
| **S53** | **Implicit tetra water surface** - water reconstruction can now export an opt-in implicit tetra OBJ surface, and `dam_break_cinematic` uses it to reduce voxel stair stepping in review gates. | done |
| **S54** | **High-detail surface gate** - a 20x24x17 falling-water close-up gate exercises tetra reconstruction at higher mesh density, with timing and framing limits recorded. | done |
| **S55** | **Grid-aware cinematic framing** - Blender scene specs can auto-scale preset camera targets/distances from reference grid dimensions, fixing high-detail gate crop while preserving camera motion. | done |
| **S56** | **Physically conditioned secondary seed** - `dam_break_cinematic` now uses liquid-particle candidate secondary emission instead of demo rings, with first/last channel counts recorded in shot reports. | done |
| **S57** | **Sim-side secondary spray gate** - sparse cinematic physical secondary emission now runs inside the sparse 3D two-phase sim step, with lifecycle volume accounting and shot-report acceptance thresholds. | done |
| **S58** | **Interface-conditioned secondary spray gate** - physical sparse secondary emission now requires measured interface diagnostics, reports gate pass/cells/gradient/curvature, and has a larger 30-frame Blender gate. | done |
| **S59** | **Large water-event scene** - `dam_break_cinematic` now uses a wider falling sheet over a shallow impact pool, with a 36-frame 1280x720 Blender gate and larger interface/volume metrics. | done |
| **S60** | **Contact splash visibility gate** - large water-event timing now produces earlier pool contact, impact-driven spray candidates, 192 physical secondaries, and a 36-frame Blender contact/splash report. | done |
| **S61** | **Contact foam and surface detail gate** - impact-driven droplets now split into spray and foam channels, shot reports enforce foam acceptance, and Blender water meshes get opt-in surface detail displacement. | done |
| **S62** | **Secondary render size pass** - Blender rendering now supports channel-specific secondary radii and spray/foam emission so contact particles are more legible in the large water-event gate. | done |
| **S63** | **Contact close-up camera gate** - `dam_break_contact_closeup` provides a closer inspection preset for foam, spray, and contact-region surface breakup. | done |
| **S64** | **Contact camera stability review** - close-up shots now report camera path stability and can emit a wide/close review comparison sheet. | done |
| **S65** | **Cinematic visual QA metrics** - Blender gates now summarize frame luminance, contrast, bright-pixel ratios, and preset-driven visual QA pass/fail checks. | done |
| **S66** | **Volumetric spray/foam render pass** - Blender rendering can add a soft halo pass for spray/foam channels while preserving visual QA gates. | done |
| **S67** | **Secondary soft-pass performance** - spray/foam halos are batched into channel meshes, reducing Blender soft-pass render cost while preserving QA. | done |
| **S68** | **Secondary mist billboard quality** - spray/foam soft pass can use camera-facing billboard disks, improving mist readability without increasing render cost. | done |
| **S69** | **Secondary mist alpha falloff** - billboard mist disks now use concentric radial alpha falloff materials to soften circular edges while preserving QA. | done |
| **S70** | **Secondary mist falloff tuning** - mist billboard falloff uses lower outer alpha, smaller max radius, and stronger inner emission while preserving QA. | done |
| **S71** | **Secondary mist texture falloff** - mist billboards can use UV-driven radial shader alpha falloff while preserving QA and render-cost targets. | done |
| **S72** | **Secondary velocity streak pass** - Blender rendering can add velocity-aligned spray/foam streak quads from secondary particle velocities, making contact particles read as moving spray. | done |
| **S73** | **Secondary streak tuning** - velocity streaks are tuned stronger and report actual per-frame streak counts, exposing that current foam remains in the soft-pass path. | done |
| **S74** | **Impact framing gate** - `dam_break_impact_framing` inherits the contact preset with higher target/FOV camera motion so the active spray band stays visible longer. | done |
| **S75** | **Active secondary framing QA** - Blender bridge projects spray/foam particles into camera space and gates inside-frame ratio plus vertical band placement. | done |
| **S76** | **Surface contact foam pass** - Blender rendering adds flattened foam patches near the water surface so secondary foam connects back to the water body. | done |
| **S77** | **Contact foam flow lines** - `dam_break_contact_foam_flow` renders flow-aligned surface foam strokes so contact foam reads less like static horizontal patches. | done |
| **S78** | **Contact foam material fade** - `dam_break_contact_foam_fade` adds radial shader falloff to flow-aligned contact foam so strokes blend more softly into the water surface. | done |
| **S79** | **Water-surface glint flow** - `dam_break_water_glint_flow` adds subtle directional surface glint strokes so the main water body carries visible flow cues in the cinematic gate. | done |

Later specs (separate roadmaps): SPEC-2 dual adaptivity & stochastic coarsening · SPEC-3 adaptive high-contrast Poisson multigrid (§6) · SPEC-4 spray & full volumetric rendering.

> **On rendering (rough goal).** The paper's photorealism comes mostly from the *physics* (real two-phase + physical spray) plus a volumetric ray tracer with approximate multiple scattering (§7) — no post-processing or procedural textures. That exact renderer is not released. Our **rough** goal is just to make results look good: export particles, splat them into a smooth density field, and shade water volumetrically (depth/density-based color + surface highlight) instead of raw point dots. Faithful spray + ray-traced multiple scattering remain SPEC-4.

Design specs and per-phase implementation plans live in [`docs/superpowers/`](docs/superpowers/).

---

## Build & run

Requires a C++17 compiler (tested with MSVC 19.50 / Visual Studio 2026) and CMake ≥ 3.16. The doctest header is fetched once during the scaffold step (vendored in `external/`).

```powershell
# configure + build
cmake -S . -B build
cmake --build build --config Debug

# run the full test suite (unit + integration)
ctest --test-dir build -C Debug --output-on-failure

# run a 2D dam-break -> frame_###.ppm
./build/Debug/run_dambreak.exe

# run a 3D dam-break -> slice_###.ppm (mid-z slices)
./build/Debug/run_dambreak3d.exe

# run the sparse-grid dam-break (Phase A) -> sp_###.ppm with active-block overlay
cmake --build build --config Release --target run_sparse_dambreak
./build/Release/run_sparse_dambreak.exe

# run the sparse two-phase bubble tank (Phase B) -> spb_###.ppm
cmake --build build --config Release --target run_sparse_bubble
./build/Release/run_sparse_bubble.exe

# run the multires two-phase bubble tank (Phase C) -> mrb_###.ppm
cmake --build build --config Release --target run_multires_bubble
./build/Release/run_multires_bubble.exe

# run sparse 3D two-phase Rayleigh-Taylor -> sprt3_###.ppm
cmake --build build --config Release --target run_sparse_rt3d
./build/Release/run_sparse_rt3d.exe

# run sparse 3D two-phase bubble tank -> spb3_###.ppm
cmake --build build --config Release --target run_sparse_bubble3d
./build/Release/run_sparse_bubble3d.exe

# validate sparse 3D two-phase metrics, including opt-in narrow-band air
cmake --build build --config Release --target validate_sparse3d_tp
./build/Release/validate_sparse3d_tp.exe --scenario rt --steps 4 --narrow-band-air --narrow-band-radius 2
./build/Release/validate_sparse3d_tp.exe --scenario rt --steps 4 --narrow-band-air --narrow-band-radius 2 --gas-coarsening --gas-particles-per-cell 2 --gas-coarsening-seed 12345
./build/Release/validate_sparse3d_tp.exe --scenario bubble --steps 4 --narrow-band-air --narrow-band-radius 2 --gas-coarsening --gas-particles-per-cell 2 --gas-coarsening-seed 12345 --liquid-coarsening --liquid-particles-per-cell 4 --liquid-coarsening-seed 54321
./build/Release/validate_sparse3d_tp.exe --scenario bubble --steps 4 --liquid-coarsening --liquid-particles-per-cell 2 --liquid-coarsening-seed 54321 --liquid-refill --liquid-refill-particles-per-cell 4 --liquid-refill-seed 24680
./build/Release/validate_sparse3d_tp.exe --scenario bubble --steps 4 --liquid-coarsening --liquid-particles-per-cell 2 --liquid-coarsening-seed 54321 --liquid-refill --liquid-refill-particles-per-cell 4 --liquid-refill-seed 24680 --liquid-refill-max-added-per-step 160 --liquid-refill-interface-only --liquid-refill-interface-radius 1
./build/Release/validate_sparse3d_tp.exe --scenario bubble --steps 4 --secondary-lifecycle
./build/Release/validate_sparse3d_tp.exe --scenario bubble --steps 4 --secondary-lifecycle --secondary-droplet-drag 1 --secondary-bubble-drag 0.5 --secondary-droplet-gravity-scale 0.5 --secondary-reabsorb-to-primary
./build/Release/validate_sparse3d_tp.exe --physics-preset --steps 8
./build/Release/validate_sparse3d_tp.exe --long-physics-preset

# validate 3D multires two-phase bubble metrics
cmake --build build --config Release --target validate_multires3d_tp
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 6
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --narrow-band-air --narrow-band-radius 2 --gas-coarsening --gas-particles-per-cell 2 --gas-coarsening-seed 12345
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --narrow-band-air --narrow-band-radius 2 --gas-coarsening --gas-particles-per-cell 2 --gas-coarsening-seed 12345 --liquid-coarsening --liquid-particles-per-cell 4 --liquid-coarsening-seed 54321
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --liquid-coarsening --liquid-particles-per-cell 2 --liquid-coarsening-seed 54321 --liquid-refill --liquid-refill-particles-per-cell 4 --liquid-refill-seed 24680
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --liquid-coarsening --liquid-particles-per-cell 2 --liquid-coarsening-seed 54321 --liquid-refill --liquid-refill-particles-per-cell 4 --liquid-refill-seed 24680 --liquid-refill-max-added-per-step 160 --liquid-refill-interface-only --liquid-refill-interface-radius 1
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --secondary-lifecycle
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --secondary-lifecycle --secondary-droplet-drag 1 --secondary-bubble-drag 0.5 --secondary-droplet-gravity-scale 0.5 --secondary-reabsorb-to-primary
./build/Release/validate_multires3d_tp.exe --physics-preset --steps 8
./build/Release/validate_multires3d_tp.exe --long-physics-preset

# validate 3D surface-tension strength sweep metrics
cmake --build build --config Release --target validate_surface_tension3d
./build/Release/validate_surface_tension3d.exe --mode both --steps 4 --smoothing-radius 1

# export SPEC-4 pre-render JSONL cache frames
cmake --build build --config Release --target export_render_cache3d
./build/Release/export_render_cache3d.exe --kind sparse --steps 4 --every 4 --out-prefix render_cache_sparse
./build/Release/export_render_cache3d.exe --kind sparse --scene falling-water --steps 4 --every 1 --secondary-demo-particles 96 --out-prefix build/render_cache_falling
./build/Release/export_render_cache3d.exe --kind sparse --scene falling-water --steps 4 --every 1 --secondary-physical-particles 96 --out-prefix build/render_cache_falling_physical
./build/Release/export_render_cache3d.exe --kind mr --steps 4 --every 4 --out-prefix render_cache_mr
python tools/validate_render_cache.py render_cache_sparse_manifest.json
python tools/validate_render_cache.py render_cache_sparse_manifest.json --require-cinematic
python tools/convert_render_cache.py render_cache_sparse_manifest.json build/render_cache_convert --require-cinematic
python tools/reconstruct_water.py render_cache_sparse_manifest.json build/water_mesh --frames 8 --threshold 0.02
python tools/convert_render_cache.py render_cache_sparse_manifest.json build/render_cache_convert_mesh --require-cinematic --water-reconstruction build/water_mesh/water_reconstruction.json
python tools/render_bridge_blender.py --check
python tools/render_bridge_blender.py build/render_cache_convert_mesh/sequence.json build/blender_bridge --frames 8 --width 1280 --height 720
python tools/render_bridge_blender.py build/render_cache_convert_mesh/sequence.json build/blender_bridge_dry --frames 8 --dry-run
python tools/run_cinematic_shot.py --preset bubble_cinematic --out build/shots/bubble_cinematic --frames 24 --width 1280 --height 720
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/dam_break_cinematic --frames 24 --width 1280 --height 720
python tools/run_cinematic_shot.py --preset bubble_cinematic --out build/shots/s45_bubble --frames 48 --width 1280 --height 720 --samples 12 --report docs/reports/cinematic_gate_s45.md
python tools/run_cinematic_shot.py --preset bubble_cinematic --out build/shots/s46_smooth --frames 24 --width 1280 --height 720
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s47_dam_break --frames 24 --width 1280 --height 720 --report docs/reports/cinematic_gate_s47.md
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s48_secondary --frames 24 --width 1280 --height 720 --report docs/reports/cinematic_gate_s48.md
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s49_camera_motion --frames 24 --width 1280 --height 720 --report docs/reports/cinematic_gate_s49.md
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s50_water_material --frames 24 --width 1280 --height 720 --report docs/reports/cinematic_gate_s50.md
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s51_review_pack --frames 24 --width 1280 --height 720 --review-frames 6 --report docs/reports/cinematic_gate_s51.md
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s52_visual_gate_v2 --frames 36 --sim-steps 36 --width 960 --height 540 --renderer blender --samples 10 --review-frames 8 --report docs/reports/cinematic_gate_s52.md --timeout-seconds 600
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s53_surface_tetra --frames 24 --sim-steps 24 --width 640 --height 360 --renderer blender --samples 8 --review-frames 6 --report docs/reports/cinematic_gate_s53.md --timeout-seconds 600
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s54_high_detail_surface --nx 20 --ny 24 --nz 17 --frames 24 --sim-steps 24 --width 960 --height 540 --renderer blender --samples 10 --review-frames 6 --report docs/reports/cinematic_gate_s54.md --timeout-seconds 900
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s55_grid_aware_camera --nx 20 --ny 24 --nz 17 --frames 24 --sim-steps 24 --width 960 --height 540 --renderer blender --samples 10 --review-frames 6 --report docs/reports/cinematic_gate_s55.md --timeout-seconds 900
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s56_physical_secondary --nx 20 --ny 24 --nz 17 --frames 24 --sim-steps 24 --width 960 --height 540 --renderer blender --samples 10 --review-frames 6 --report docs/reports/cinematic_gate_s56.md --timeout-seconds 900
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s57_secondary_lifecycle_gate --nx 20 --ny 24 --nz 17 --frames 24 --sim-steps 24 --width 960 --height 540 --renderer blender --samples 10 --review-frames 6 --report docs/reports/cinematic_gate_s57.md --timeout-seconds 900
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s58_interface_secondary_gate --nx 24 --ny 30 --nz 20 --frames 30 --sim-steps 30 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s58.md --timeout-seconds 1200
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s59_large_water_event --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s59.md --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s60_contact_splash --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s60.md --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s61_contact_foam_surface --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s61.md --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/s62_secondary_size_pass --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s62.md --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s63_contact_closeup --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s63.md --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s64_contact_camera_stability --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s64.md --compare-review-manifest build/shots/s62_secondary_size_pass/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s65_visual_qa_metrics --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s65.md --compare-review-manifest build/shots/s62_secondary_size_pass/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s66_volumetric_spray_foam --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s66.md --compare-review-manifest build/shots/s62_secondary_size_pass/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s67_secondary_soft_perf --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s67.md --compare-review-manifest build/shots/s62_secondary_size_pass/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s68_secondary_mist_quality --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s68.md --compare-review-manifest build/shots/s62_secondary_size_pass/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s69_secondary_mist_falloff --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s69.md --compare-review-manifest build/shots/s62_secondary_size_pass/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s70_secondary_mist_falloff_tuned --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s70.md --compare-review-manifest build/shots/s62_secondary_size_pass/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s71_secondary_mist_texture_falloff --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s71.md --compare-review-manifest build/shots/s62_secondary_size_pass/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s72_secondary_velocity_streaks --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s72.md --compare-review-manifest build/shots/s62_secondary_size_pass/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_closeup --out build/shots/s73_secondary_streak_tuning --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s73.md --compare-review-manifest build/shots/s72_secondary_velocity_streaks/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_impact_framing --out build/shots/s74_impact_framing --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s74.md --compare-review-manifest build/shots/s73_secondary_streak_tuning/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_impact_framing --out build/shots/s75_active_secondary_framing_qa --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s75.md --compare-review-manifest build/shots/s74_impact_framing/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_impact_framing --out build/shots/s76_surface_foam_contact --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s76.md --compare-review-manifest build/shots/s75_active_secondary_framing_qa/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_foam_flow --out build/shots/s77_contact_foam_flow_lines --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s77.md --compare-review-manifest build/shots/s76_surface_foam_contact/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_contact_foam_fade --out build/shots/s78_contact_foam_material_fade --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s78.md --compare-review-manifest build/shots/s77_contact_foam_flow_lines/review/review_manifest.json --timeout-seconds 1500
python tools/run_cinematic_shot.py --preset dam_break_water_glint_flow --out build/shots/s79_water_surface_glint_flow --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs/reports/cinematic_gate_s79.md --compare-review-manifest build/shots/s78_contact_foam_material_fade/review/review_manifest.json --timeout-seconds 1500
python tools/cinematic_render_stub.py render_cache_sparse_manifest.json build/cinematic_preview --frames 12 --width 1280 --height 720
python tools/cinematic_render_stub.py render_cache_sparse_manifest.json build/cinematic_preview_mesh --frames 8 --width 1280 --height 720 --water-reconstruction build/water_mesh/water_reconstruction.json
python tools/cinematic_render_stub.py render_cache_sparse_manifest.json build/cinematic_preview_foam --frames 12 --width 1280 --height 720 --secondary-channel foam --min-occupancy 0
python tools/assemble_frames.py build/cinematic_preview build/cinematic_preview.gif --fps 12
python tools/render_cache_preview.py render_cache_sparse_manifest.json build/render_cache_preview 6
python tools/render_cache_preview.py render_cache_sparse_manifest.json build/render_cache_preview_foam 6 --secondary-channel foam --hide-primary-water
python tools/render_cache_preview.py render_cache_sparse_manifest.json build/render_cache_preview_age 6 --secondary-mode age
python tools/render_cache_preview.py render_cache_sparse_manifest.json build/render_cache_preview_speed 6 --secondary-mode speed --hide-primary-water

# run 3D multires two-phase bubble slices -> mrb3_###.ppm
cmake --build build --config Release --target run_multires_bubble3d
./build/Release/run_multires_bubble3d.exe --steps 60 --every 5

# compare sparse 3D and multires 3D bubble metrics
cmake --build build --config Release --target bench_multires_sparse3d_tp
./build/Release/bench_multires_sparse3d_tp.exe --steps 4
./build/Release/bench_multires_sparse3d_tp.exe --steps 4 --sparse-narrow-band-air --sparse-narrow-band-radius 2 --sparse-gas-coarsening --sparse-gas-particles-per-cell 2 --sparse-gas-coarsening-seed 12345
./build/Release/bench_multires_sparse3d_tp.exe --steps 4 --sparse-narrow-band-air --sparse-narrow-band-radius 2 --sparse-gas-coarsening --sparse-gas-particles-per-cell 2 --sparse-gas-coarsening-seed 12345 --mr-narrow-band-air --mr-narrow-band-radius 2 --mr-gas-coarsening --mr-gas-particles-per-cell 2 --mr-gas-coarsening-seed 12345
./build/Release/bench_multires_sparse3d_tp.exe --steps 4 --sparse-narrow-band-air --sparse-narrow-band-radius 2 --sparse-gas-coarsening --sparse-gas-particles-per-cell 2 --sparse-gas-coarsening-seed 12345 --sparse-liquid-coarsening --sparse-liquid-particles-per-cell 4 --sparse-liquid-coarsening-seed 54321 --mr-narrow-band-air --mr-narrow-band-radius 2 --mr-gas-coarsening --mr-gas-particles-per-cell 2 --mr-gas-coarsening-seed 12345 --mr-liquid-coarsening --mr-liquid-particles-per-cell 4 --mr-liquid-coarsening-seed 54321
./build/Release/bench_multires_sparse3d_tp.exe --steps 4 --sparse-liquid-coarsening --sparse-liquid-particles-per-cell 2 --sparse-liquid-coarsening-seed 54321 --sparse-liquid-refill --sparse-liquid-refill-particles-per-cell 4 --sparse-liquid-refill-seed 24680 --mr-liquid-coarsening --mr-liquid-particles-per-cell 2 --mr-liquid-coarsening-seed 54321 --mr-liquid-refill --mr-liquid-refill-particles-per-cell 4 --mr-liquid-refill-seed 24680
./build/Release/bench_multires_sparse3d_tp.exe --steps 4 --sparse-liquid-coarsening --sparse-liquid-particles-per-cell 2 --sparse-liquid-coarsening-seed 54321 --sparse-liquid-refill --sparse-liquid-refill-particles-per-cell 4 --sparse-liquid-refill-seed 24680 --sparse-liquid-refill-max-added-per-step 160 --sparse-liquid-refill-interface-only --sparse-liquid-refill-interface-radius 1 --mr-liquid-coarsening --mr-liquid-particles-per-cell 2 --mr-liquid-coarsening-seed 54321 --mr-liquid-refill --mr-liquid-refill-particles-per-cell 4 --mr-liquid-refill-seed 24680 --mr-liquid-refill-max-added-per-step 160 --mr-liquid-refill-interface-only --mr-liquid-refill-interface-radius 1
./build/Release/bench_multires_sparse3d_tp.exe --steps 4 --secondary-lifecycle
./build/Release/bench_multires_sparse3d_tp.exe --steps 3 --secondary-lifecycle --secondary-droplet-drag 1 --secondary-bubble-drag 0.5 --secondary-droplet-gravity-scale 0.5 --secondary-reabsorb-to-primary
./build/Release/bench_multires_sparse3d_tp.exe --physics-preset --steps 6
./build/Release/bench_multires_sparse3d_tp.exe --long-physics-preset

# write sparse/MR/adaptivity large-scale metrics to CSV
cmake --build build --config Release --target bench_large_scale3d_tp
./build/Release/bench_large_scale3d_tp.exe --nx 16 --ny 24 --nz 16 --steps 8 --solver baseline --csv build/large_scale3d_tp.csv
./build/Release/bench_large_scale3d_tp.exe --nx 16 --ny 24 --nz 16 --steps 8 --solver all --csv build/large_scale3d_tp_solvers.csv
./build/Release/bench_large_scale3d_tp.exe --nx 16 --ny 24 --nz 16 --steps 8 --solver all --mr-particle-padding 0 --mr-gas-padding 1 --mr-hysteresis 0 --csv build/large_scale3d_tp_compact_mr.csv
./build/Release/bench_large_scale3d_tp.exe --nx 16 --ny 24 --nz 16 --steps 4 --solver baseline --csv build/large_scale3d_tp_v2.csv --render-cache-prefix build/large_scale3d_tp_v2 --render-cache-every 4 --render-cache-preview-scale 4

# compare 3D multires pressure solver variants with baseline-relative summary lines
cmake --build build --config Release --target bench_multires3d_solver
./build/Release/bench_multires3d_solver.exe --steps 4 --rel-tol 1e-5 --restart-growth 10 --relax-sweeps 2 --relax-omega 0.1 --history-stride 1 --history-limit 8

# validate the 3D multires solver gate at a 1000:1 density ratio
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 6 --rho-ratio 1000 --history-stride 1 --history-limit 8
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 6 --rho-ratio 1000 --coarse-correction --coarse-sweeps 2
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 6 --rho-ratio 1000 --coarse-preconditioner
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --rho-ratio 1000 --cg-rel-tol 1e-5 --coarse-preconditioner --coarse-pre-iters 4 --coarse-pre-scale 0.5 --coarse-pre-max-work-ratio 2
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --rho-ratio 1000 --cg-rel-tol 1e-5 --coarse-preconditioner --coarse-pre-iters 4 --coarse-pre-scale 0.5 --coarse-pre-max-work-ratio 2 --coarse-pre-auto-disable --coarse-pre-auto-disable-after 1
./build/Release/bench_multires3d_solver.exe --steps 4 --rho-ratio 1000 --rel-tol 1e-5
./build/Release/bench_multires3d_solver.exe --steps 4 --rho-ratio 1000 --rel-tol 1e-5 --coarse-pre-sweep --coarse-pre-min-rz-gain 0.01 --coarse-pre-auto-disable --coarse-pre-auto-disable-after 2
```

PPM frames can be assembled into a GIF with any tool (e.g. Pillow: `Image.open('frame_000.ppm')...`).

---

## Project structure

```
src/
  math/        Vec2, Vec3
  grid/        UniformGrid2D / UniformGrid3D  (MAC staggered)
               SparseBlockGrid2D / SparseMacGrid2D  (treeless block-sparse, Phase 3/A)
               SparseBlockGrid3D / SparseMacGrid3D  (3D treeless block-sparse, Phase D)
               MRLayout2D / MRScalarGrid2D / MRMacGrid2D  (2D multires sparse grid, Phase C)
               MRLayout3D / MRScalarGrid3D / MRMacGrid3D  (3D multires sparse grid foundation, Phase E1)
  particles/   Particles2D / Particles3D
  transfer/    P2G / G2P  (bilinear/trilinear splat + FLIP/PIC blend)
  pressure/    divergence, pressure Poisson CG, projection, multires pressure
  advect/      RK2 advection, velocity extrapolation
  physics/     viscosity <-> FLIP alpha mapping (Eq. 13)
  driver/      Sim2D / Sim3D / SparseSim2D / SparseSim2DTP / SparseSim3D / SparseSim3DTP / MRSim2DTP / MRSim3DTP step loops + scenes + viz
               sparse_ops2d / sparse_ops2d_tp / sparse_ops3d / sparse_ops3d_tp / multires_ops2d_tp / multires_ops3d_tp  (P2G / pressure projection / G2P / advect)
apps/          run_dambreak, run_dambreak3d, run_rt2d, run_rt3d, dump_render, run_sparse_dambreak, run_sparse_bubble,
               run_sparse_rt3d, run_sparse_bubble3d, run_multires_bubble, run_multires_bubble3d,
               export_render_cache3d, validate_multires3d_tp, bench_multires_sparse3d_tp,
               bench_multires3d_solver, bench_large_scale3d_tp
configs/       cinematic_presets.json stores shot, scene, camera, light, material, and tone presets
tools/         rough_render.py, render_cache_preview.py, validate_render_cache.py, convert_render_cache.py,
               reconstruct_water.py, cinematic_render_stub.py, render_bridge_blender.py,
               run_cinematic_shot.py, and assemble_frames.py export/preview consumers
tests/         doctest unit + integration tests (one per module)
docs/          design specs and implementation plans
external/      vendored doctest
```

The MAC convention, fidelity contract, and validation checkpoints (Fig. 7 phase-field curve, shear-flow L2, Rayleigh-Taylor) are documented in the specs.

---

## Notes

- **Reference paper PDF is not included** in this repository — it is a copyrighted ACM publication. Place it under `ref/` locally if you have access (that directory is git-ignored).
- The eventual MSBG dependency (Phase 3) is [Apache-2.0](https://github.com/tum-pbs/MSBG).
- Development uses a TDD, fresh-subagent-per-task workflow; the git history reads one validated step at a time.
