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

# validate 3D multires two-phase bubble metrics
cmake --build build --config Release --target validate_multires3d_tp
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 6
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --narrow-band-air --narrow-band-radius 2 --gas-coarsening --gas-particles-per-cell 2 --gas-coarsening-seed 12345
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --narrow-band-air --narrow-band-radius 2 --gas-coarsening --gas-particles-per-cell 2 --gas-coarsening-seed 12345 --liquid-coarsening --liquid-particles-per-cell 4 --liquid-coarsening-seed 54321
./build/Release/validate_multires3d_tp.exe --scenario bubble --steps 4 --liquid-coarsening --liquid-particles-per-cell 2 --liquid-coarsening-seed 54321 --liquid-refill --liquid-refill-particles-per-cell 4 --liquid-refill-seed 24680

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
               validate_multires3d_tp, bench_multires_sparse3d_tp, bench_multires3d_solver
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
