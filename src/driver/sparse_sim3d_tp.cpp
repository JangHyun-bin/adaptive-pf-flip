#include "driver/sparse_sim3d_tp.h"
#include "driver/sparse_ops3d_tp.h"
#include "transfer/transfer3d_tp.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

namespace {

void seedCell(Particles3DTP& ps, int i, int j, int k, double dx, unsigned char type) {
  for (int s = 0; s < 8; ++s) {
    double x = (i + 0.25 + 0.5 * (s & 1)) * dx;
    double y = (j + 0.25 + 0.5 * ((s >> 1) & 1)) * dx;
    double z = (k + 0.25 + 0.5 * ((s >> 2) & 1)) * dx;
    ps.add({x, y, z}, {0.0, 0.0, 0.0}, type);
  }
}

void markCells(SparseMacGrid3D<4>& g, const Particles3DTP& ps) {
  g.mkf.clear();
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j < g.ny; ++j) {
      g.setCell(0, j, k, 2);
      g.setCell(g.nx - 1, j, k, 2);
    }
  }
  for (int k = 0; k < g.nz; ++k) {
    for (int i = 0; i < g.nx; ++i) {
      g.setCell(i, 0, k, 2);
      g.setCell(i, g.ny - 1, k, 2);
    }
  }
  for (int j = 0; j < g.ny; ++j) {
    for (int i = 0; i < g.nx; ++i) {
      g.setCell(i, j, 0, 2);
      g.setCell(i, j, g.nz - 1, 2);
    }
  }
  for (size_t p = 0; p < ps.size(); ++p) {
    int i = (int)((ps.pos[p].x - g.ox) / g.dx);
    int j = (int)((ps.pos[p].y - g.oy) / g.dx);
    int k = (int)((ps.pos[p].z - g.oz) / g.dx);
    if (g.inBounds(i, j, k) && g.cell(i, j, k) != 2) {
      g.setCell(i, j, k, 1);
    }
  }
}

void applyGravity(SparseMacGrid3D<4>& g, double dt, double gravity) {
  for (int b : g.mvf.activeBlockIds()) {
    int bx, by, bz;
    g.mvf.blockCoords(b, bx, by, bz);
    for (int lz = 0; lz < 4; ++lz) {
      for (int ly = 0; ly < 4; ++ly) {
        for (int lx = 0; lx < 4; ++lx) {
          int i = bx * 4 + lx;
          int j = by * 4 + ly;
          int k = bz * 4 + lz;
          if (i >= g.nx || j > g.ny || k >= g.nz) continue;
          if (g.gmv(i, j, k) > 0.0f) {
            g.v(i, j, k) = g.gv(i, j, k) + (float)(dt * gravity);
          }
        }
      }
    }
  }
}

void applyWallBoundary(SparseMacGrid3D<4>& g) {
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j < g.ny; ++j) {
      g.u(0, j, k) = 0.0f;
      g.u(1, j, k) = 0.0f;
      g.u(g.nx - 1, j, k) = 0.0f;
      g.u(g.nx, j, k) = 0.0f;
    }
  }
  for (int k = 0; k < g.nz; ++k) {
    for (int i = 0; i < g.nx; ++i) {
      g.v(i, 0, k) = 0.0f;
      g.v(i, 1, k) = 0.0f;
      g.v(i, g.ny - 1, k) = 0.0f;
      g.v(i, g.ny, k) = 0.0f;
    }
  }
  for (int j = 0; j < g.ny; ++j) {
    for (int i = 0; i < g.nx; ++i) {
      g.w(i, j, 0) = 0.0f;
      g.w(i, j, 1) = 0.0f;
      g.w(i, j, g.nz - 1) = 0.0f;
      g.w(i, j, g.nz) = 0.0f;
    }
  }
}

size_t cellIndex(const SparseMacGrid3D<4>& g, int i, int j, int k) {
  return static_cast<size_t>(i) +
         static_cast<size_t>(g.nx) *
           (static_cast<size_t>(j) + static_cast<size_t>(g.ny) * static_cast<size_t>(k));
}

bool particleCell(const SparseMacGrid3D<4>& g,
                  const Particles3DTP& particles,
                  size_t p,
                  int& i,
                  int& j,
                  int& k) {
  const Vec3& x = particles.pos[p];
  if (!std::isfinite(x.x) || !std::isfinite(x.y) || !std::isfinite(x.z)) {
    return false;
  }
  i = static_cast<int>((x.x - g.ox) / g.dx);
  j = static_cast<int>((x.y - g.oy) / g.dx);
  k = static_cast<int>((x.z - g.oz) / g.dx);
  return g.inBounds(i, j, k);
}

uint32_t mix32(uint32_t x) {
  x ^= x >> 16;
  x *= 0x7feb352du;
  x ^= x >> 15;
  x *= 0x846ca68bu;
  x ^= x >> 16;
  return x;
}

uint32_t particleScore(const SparseMacGrid3D<4>& g,
                       const Particles3DTP& particles,
                       size_t p,
                       int i,
                       int j,
                       int k,
                       uint32_t seed) {
  const Vec3& x = particles.pos[p];
  const int qx = static_cast<int>((x.x - (g.ox + i * g.dx)) / g.dx * 1024.0);
  const int qy = static_cast<int>((x.y - (g.oy + j * g.dx)) / g.dx * 1024.0);
  const int qz = static_cast<int>((x.z - (g.oz + k * g.dx)) / g.dx * 1024.0);
  uint32_t h = seed;
  h ^= mix32(static_cast<uint32_t>(i) + 0x9e3779b9u);
  h ^= mix32(static_cast<uint32_t>(j) + 0x85ebca6bu);
  h ^= mix32(static_cast<uint32_t>(k) + 0xc2b2ae35u);
  h ^= mix32(static_cast<uint32_t>(qx & 2047) + 0x27d4eb2fu);
  h ^= mix32(static_cast<uint32_t>(qy & 2047) + 0x165667b1u);
  h ^= mix32(static_cast<uint32_t>(qz & 2047) + 0xd3a2646cu);
  return mix32(h);
}

} // namespace

void SparseSim3DTP::initTwoPhaseDamBreak() {
  particles = Particles3DTP();
  narrow_band_air_removed_last = 0;
  narrow_band_air_removed_total = 0;
  gas_particle_coarsening_removed_last = 0;
  gas_particle_coarsening_removed_total = 0;
  phase.rho_tilde_0 = calibrateRhoTilde0(phase, Vp);
  int wx = grid.nx * 4 / 10;
  int hy = grid.ny * 7 / 10;
  for (int k = 1; k < grid.nz - 1; ++k) {
    for (int j = 1; j < grid.ny - 1; ++j) {
      for (int i = 1; i < grid.nx - 1; ++i) {
        bool liquid = (i < wx && j < hy);
        seedCell(particles, i, j, k, grid.dx, liquid ? 0 : 1);
      }
    }
  }
  applyParticleAdaptivity();
}

void SparseSim3DTP::initRayleighTaylor() {
  particles = Particles3DTP();
  narrow_band_air_removed_last = 0;
  narrow_band_air_removed_total = 0;
  gas_particle_coarsening_removed_last = 0;
  gas_particle_coarsening_removed_total = 0;
  phase.rho_tilde_0 = calibrateRhoTilde0(phase, Vp);
  int mid = grid.ny / 2;
  constexpr double pi = 3.14159265358979323846;
  for (int k = 1; k < grid.nz - 1; ++k) {
    for (int j = 1; j < grid.ny - 1; ++j) {
      for (int i = 1; i < grid.nx - 1; ++i) {
        double pert = std::cos(2.0 * pi * i / grid.nx) * std::cos(2.0 * pi * k / grid.nz);
        bool heavy = (double)j > (mid + pert);
        seedCell(particles, i, j, k, grid.dx, heavy ? 0 : 1);
      }
    }
  }
  applyParticleAdaptivity();
}

void SparseSim3DTP::initBubbleTank() {
  particles = Particles3DTP();
  narrow_band_air_removed_last = 0;
  narrow_band_air_removed_total = 0;
  gas_particle_coarsening_removed_last = 0;
  gas_particle_coarsening_removed_total = 0;
  phase.rho_tilde_0 = calibrateRhoTilde0(phase, Vp);
  int waterLevel = grid.ny / 2;
  double cx = grid.nx * 0.5;
  double cy = waterLevel * 0.375;
  double cz = grid.nz * 0.5;
  double r = std::max(1.25, std::min(grid.nx, grid.nz) * 0.1875);
  for (int k = 1; k < grid.nz - 1; ++k) {
    for (int j = 1; j < waterLevel; ++j) {
      for (int i = 1; i < grid.nx - 1; ++i) {
        double dx = (i + 0.5) - cx;
        double dy = (j + 0.5) - cy;
        double dz = (k + 0.5) - cz;
        bool gas = dx * dx + dy * dy + dz * dz < r * r;
        seedCell(particles, i, j, k, grid.dx, gas ? 1 : 0);
      }
    }
  }
  applyParticleAdaptivity();
}

void SparseSim3DTP::applyNarrowBandAir() {
  narrow_band_air_removed_last = 0;
  narrow_band_air_liquid_cells_last = 0;
  narrow_band_air_gas_particles_before_last = 0;
  narrow_band_air_gas_particles_after_last = 0;
  if (!narrow_band_air) return;

  std::vector<unsigned char> liquidCells(static_cast<size_t>(grid.nx) *
                                           static_cast<size_t>(grid.ny) *
                                           static_cast<size_t>(grid.nz),
                                         0);

  for (size_t p = 0; p < particles.size(); ++p) {
    if (particles.type[p] != 0) continue;
    int i = 0, j = 0, k = 0;
    if (!particleCell(grid, particles, p, i, j, k)) continue;
    unsigned char& occupied = liquidCells[cellIndex(grid, i, j, k)];
    if (!occupied) {
      occupied = 1;
      ++narrow_band_air_liquid_cells_last;
    }
  }
  if (narrow_band_air_liquid_cells_last == 0) return;

  const int radius = std::max(0, narrow_band_air_radius);
  auto gasInLiquidBand = [&](int i, int j, int k) {
    for (int dk = -radius; dk <= radius; ++dk) {
      int kk = k + dk;
      if (kk < 0 || kk >= grid.nz) continue;
      for (int dj = -radius; dj <= radius; ++dj) {
        int jj = j + dj;
        if (jj < 0 || jj >= grid.ny) continue;
        for (int di = -radius; di <= radius; ++di) {
          int ii = i + di;
          if (ii < 0 || ii >= grid.nx) continue;
          if (liquidCells[cellIndex(grid, ii, jj, kk)]) return true;
        }
      }
    }
    return false;
  };

  const size_t removed = particles.eraseIf([&](size_t p) {
    if (particles.type[p] != 1) return false;
    ++narrow_band_air_gas_particles_before_last;
    int i = 0, j = 0, k = 0;
    const bool keep = particleCell(grid, particles, p, i, j, k) && gasInLiquidBand(i, j, k);
    if (keep) ++narrow_band_air_gas_particles_after_last;
    return !keep;
  });
  narrow_band_air_removed_last = static_cast<int>(removed);
  narrow_band_air_removed_total += narrow_band_air_removed_last;
}

void SparseSim3DTP::applyGasParticleCoarsening() {
  gas_particle_coarsening_removed_last = 0;
  gas_particle_coarsening_cells_last = 0;
  gas_particle_coarsening_overfull_cells_last = 0;
  gas_particle_coarsening_before_last = 0;
  gas_particle_coarsening_after_last = 0;
  if (!gas_particle_coarsening) return;

  struct GasEntry {
    size_t index = 0;
    size_t cell = 0;
    uint32_t score = 0;
  };

  const int target = std::max(1, gas_particles_per_cell_target);
  std::vector<GasEntry> entries;
  entries.reserve(particles.size());
  std::vector<unsigned char> keep(particles.size(), 0);
  for (size_t p = 0; p < particles.size(); ++p) {
    if (particles.type[p] != 1) continue;
    ++gas_particle_coarsening_before_last;
    int i = 0, j = 0, k = 0;
    if (!particleCell(grid, particles, p, i, j, k)) {
      continue;
    }
    entries.push_back(GasEntry{p,
                               cellIndex(grid, i, j, k),
                               particleScore(grid,
                                             particles,
                                             p,
                                             i,
                                             j,
                                             k,
                                             gas_particle_coarsening_seed)});
  }
  std::sort(entries.begin(), entries.end(), [](const GasEntry& a, const GasEntry& b) {
    if (a.cell != b.cell) return a.cell < b.cell;
    if (a.score != b.score) return a.score < b.score;
    return a.index < b.index;
  });

  size_t groupStart = 0;
  while (groupStart < entries.size()) {
    size_t groupEnd = groupStart + 1;
    while (groupEnd < entries.size() && entries[groupEnd].cell == entries[groupStart].cell) {
      ++groupEnd;
    }
    ++gas_particle_coarsening_cells_last;
    const size_t groupCount = groupEnd - groupStart;
    if (groupCount > static_cast<size_t>(target)) {
      ++gas_particle_coarsening_overfull_cells_last;
    }
    const size_t keepCount = std::min(groupCount, static_cast<size_t>(target));
    for (size_t t = 0; t < keepCount; ++t) {
      keep[entries[groupStart + t].index] = 1;
      ++gas_particle_coarsening_after_last;
    }
    groupStart = groupEnd;
  }

  const size_t removed = particles.eraseIf([&](size_t p) {
    if (particles.type[p] != 1) return false;
    return keep[p] == 0;
  });
  gas_particle_coarsening_removed_last = static_cast<int>(removed);
  gas_particle_coarsening_removed_total += gas_particle_coarsening_removed_last;
}

void SparseSim3DTP::applyParticleAdaptivity() {
  applyNarrowBandAir();
  applyGasParticleCoarsening();
}

void SparseSim3DTP::step() {
  applyParticleAdaptivity();
  markCells(grid, particles);
  spP2G3D_tp(grid, particles, phase, Vp);
  SparseMacGrid3D<4> saved = grid;
  applyGravity(grid, dt, gravity);
  applyWallBoundary(grid);
  spProjectStepVC3D(grid, phase, dt, cg_iters, cg_tol);
  spG2P3D_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  spAdvect3D_tp(particles, grid, dt);
}
