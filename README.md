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

---

## Roadmap

This is **SPEC-1** (the faithful core), decomposed into phases. Each phase produces working, tested software on its own.

| Phase | Adds | Status |
|---|---|---|
| **0** | 2D MAC FLIP/PIC, pressure CG, RK2 advect, dam-break | ✅ done |
| **1** | **3D** extension, viscosity (Eq. 13), velocity extrapolation | ✅ done |
| **2** ★ | **Two-phase phase field** (Eq. 7), variable-coefficient β=1/ρ Poisson (Eq. 8), cubic kernel (Eq. 6) — validated by Rayleigh-Taylor | ✅ done — *the paper's identity* (2D; droplet/bubble conversion → Phase 2b) |
| **3** | [MSBG](https://github.com/tum-pbs/MSBG) treeless sparse multiresolution grid integration | ⬜ |

Later specs (separate roadmaps): SPEC-2 dual adaptivity & stochastic coarsening · SPEC-3 adaptive high-contrast Poisson multigrid (§6) · SPEC-4 spray & volumetric rendering.

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
```

PPM frames can be assembled into a GIF with any tool (e.g. Pillow: `Image.open('frame_000.ppm')...`).

---

## Project structure

```
src/
  math/        Vec2, Vec3
  grid/        UniformGrid2D / UniformGrid3D  (MAC staggered)
  particles/   Particles2D / Particles3D
  transfer/    P2G / G2P  (bilinear/trilinear splat + FLIP/PIC blend)
  pressure/    divergence, pressure Poisson CG, projection
  advect/      RK2 advection, velocity extrapolation
  physics/     viscosity <-> FLIP alpha mapping (Eq. 13)
  driver/      Sim2D / Sim3D step loop + dam-break scenes + viz
apps/          run_dambreak, run_dambreak3d
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
