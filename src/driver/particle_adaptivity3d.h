#pragma once

#include "particles/particles3d_tp.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

namespace pa3d {

struct ParticleCellDomain3D {
  int nx = 0;
  int ny = 0;
  int nz = 0;
  double dx = 1.0;
  double ox = 0.0;
  double oy = 0.0;
  double oz = 0.0;

  bool inBounds(int i, int j, int k) const {
    return i >= 0 && i < nx &&
           j >= 0 && j < ny &&
           k >= 0 && k < nz;
  }

  size_t cellIndex(int i, int j, int k) const {
    return static_cast<size_t>(i) +
           static_cast<size_t>(nx) *
             (static_cast<size_t>(j) + static_cast<size_t>(ny) * static_cast<size_t>(k));
  }

  bool particleCell(const Particles3DTP& particles,
                    size_t p,
                    int& i,
                    int& j,
                    int& k) const {
    const Vec3& x = particles.pos[p];
    if (!std::isfinite(x.x) || !std::isfinite(x.y) || !std::isfinite(x.z)) {
      return false;
    }
    i = static_cast<int>((x.x - ox) / dx);
    j = static_cast<int>((x.y - oy) / dx);
    k = static_cast<int>((x.z - oz) / dx);
    return inBounds(i, j, k);
  }
};

struct NarrowBandAirResult3D {
  int removed = 0;
  int liquidCells = 0;
  int gasBefore = 0;
  int gasAfter = 0;
};

struct GasParticleCoarseningResult3D {
  int removed = 0;
  int cells = 0;
  int overfullCells = 0;
  int particlesBefore = 0;
  int particlesAfter = 0;
};

struct LiquidParticleRefillResult3D {
  int added = 0;
  int cells = 0;
  int underfullCells = 0;
  int particlesBefore = 0;
  int particlesAfter = 0;
};

inline uint32_t mix32(uint32_t x) {
  x ^= x >> 16;
  x *= 0x7feb352du;
  x ^= x >> 15;
  x *= 0x846ca68bu;
  x ^= x >> 16;
  return x;
}

inline uint32_t particleScore(const ParticleCellDomain3D& domain,
                              const Particles3DTP& particles,
                              size_t p,
                              int i,
                              int j,
                              int k,
                              uint32_t seed) {
  const Vec3& x = particles.pos[p];
  const int qx = static_cast<int>((x.x - (domain.ox + i * domain.dx)) / domain.dx * 1024.0);
  const int qy = static_cast<int>((x.y - (domain.oy + j * domain.dx)) / domain.dx * 1024.0);
  const int qz = static_cast<int>((x.z - (domain.oz + k * domain.dx)) / domain.dx * 1024.0);
  uint32_t h = seed;
  h ^= mix32(static_cast<uint32_t>(i) + 0x9e3779b9u);
  h ^= mix32(static_cast<uint32_t>(j) + 0x85ebca6bu);
  h ^= mix32(static_cast<uint32_t>(k) + 0xc2b2ae35u);
  h ^= mix32(static_cast<uint32_t>(qx & 2047) + 0x27d4eb2fu);
  h ^= mix32(static_cast<uint32_t>(qy & 2047) + 0x165667b1u);
  h ^= mix32(static_cast<uint32_t>(qz & 2047) + 0xd3a2646cu);
  return mix32(h);
}

inline uint32_t slotScore(size_t cell, int slot, uint32_t seed) {
  uint32_t h = seed;
  h ^= mix32(static_cast<uint32_t>(cell) + 0x68bc21ebu);
  h ^= mix32(static_cast<uint32_t>(slot) + 0x02e5be93u);
  return mix32(h);
}

inline NarrowBandAirResult3D applyNarrowBandAir(Particles3DTP& particles,
                                                const ParticleCellDomain3D& domain,
                                                bool enabled,
                                                int radius) {
  NarrowBandAirResult3D result;
  if (!enabled) return result;

  std::vector<unsigned char> liquidCells(static_cast<size_t>(domain.nx) *
                                           static_cast<size_t>(domain.ny) *
                                           static_cast<size_t>(domain.nz),
                                         0);

  for (size_t p = 0; p < particles.size(); ++p) {
    if (particles.type[p] != 0) continue;
    int i = 0, j = 0, k = 0;
    if (!domain.particleCell(particles, p, i, j, k)) continue;
    unsigned char& occupied = liquidCells[domain.cellIndex(i, j, k)];
    if (!occupied) {
      occupied = 1;
      ++result.liquidCells;
    }
  }
  if (result.liquidCells == 0) return result;

  radius = std::max(0, radius);
  auto gasInLiquidBand = [&](int i, int j, int k) {
    for (int dk = -radius; dk <= radius; ++dk) {
      int kk = k + dk;
      if (kk < 0 || kk >= domain.nz) continue;
      for (int dj = -radius; dj <= radius; ++dj) {
        int jj = j + dj;
        if (jj < 0 || jj >= domain.ny) continue;
        for (int di = -radius; di <= radius; ++di) {
          int ii = i + di;
          if (ii < 0 || ii >= domain.nx) continue;
          if (liquidCells[domain.cellIndex(ii, jj, kk)]) return true;
        }
      }
    }
    return false;
  };

  const size_t removed = particles.eraseIf([&](size_t p) {
    if (particles.type[p] != 1) return false;
    ++result.gasBefore;
    int i = 0, j = 0, k = 0;
    const bool keep = domain.particleCell(particles, p, i, j, k) && gasInLiquidBand(i, j, k);
    if (keep) ++result.gasAfter;
    return !keep;
  });
  result.removed = static_cast<int>(removed);
  return result;
}

inline GasParticleCoarseningResult3D applyTypedParticleCoarsening(
  Particles3DTP& particles,
  const ParticleCellDomain3D& domain,
  bool enabled,
  unsigned char particleType,
  int particlesPerCellTarget,
  uint32_t seed) {
  GasParticleCoarseningResult3D result;
  if (!enabled) return result;

  struct GasEntry {
    size_t index = 0;
    size_t cell = 0;
    uint32_t score = 0;
  };

  const int target = std::max(1, particlesPerCellTarget);
  std::vector<GasEntry> entries;
  entries.reserve(particles.size());
  std::vector<unsigned char> keep(particles.size(), 0);
  for (size_t p = 0; p < particles.size(); ++p) {
    if (particles.type[p] != particleType) continue;
    ++result.particlesBefore;
    int i = 0, j = 0, k = 0;
    if (!domain.particleCell(particles, p, i, j, k)) {
      continue;
    }
    entries.push_back(GasEntry{p,
                               domain.cellIndex(i, j, k),
                               particleScore(domain, particles, p, i, j, k, seed)});
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
    ++result.cells;
    const size_t groupCount = groupEnd - groupStart;
    if (groupCount > static_cast<size_t>(target)) {
      ++result.overfullCells;
    }
    const size_t keepCount = std::min(groupCount, static_cast<size_t>(target));
    for (size_t t = 0; t < keepCount; ++t) {
      keep[entries[groupStart + t].index] = 1;
      ++result.particlesAfter;
    }
    groupStart = groupEnd;
  }

  const size_t removed = particles.eraseIf([&](size_t p) {
    if (particles.type[p] != particleType) return false;
    return keep[p] == 0;
  });
  result.removed = static_cast<int>(removed);
  return result;
}

inline GasParticleCoarseningResult3D applyGasParticleCoarsening(
  Particles3DTP& particles,
  const ParticleCellDomain3D& domain,
  bool enabled,
  int particlesPerCellTarget,
  uint32_t seed) {
  return applyTypedParticleCoarsening(particles,
                                      domain,
                                      enabled,
                                      1,
                                      particlesPerCellTarget,
                                      seed);
}

inline LiquidParticleRefillResult3D applyLiquidParticleRefill(
  Particles3DTP& particles,
  const ParticleCellDomain3D& domain,
  bool enabled,
  int particlesPerCellTarget,
  uint32_t seed) {
  LiquidParticleRefillResult3D result;
  if (!enabled) return result;

  struct CellInfo {
    int count = 0;
    Vec3 velocitySum;
  };

  const int target = std::max(1, particlesPerCellTarget);
  std::vector<CellInfo> cells(static_cast<size_t>(domain.nx) *
                                static_cast<size_t>(domain.ny) *
                                static_cast<size_t>(domain.nz));

  for (size_t p = 0; p < particles.size(); ++p) {
    if (particles.type[p] != 0) continue;
    int i = 0, j = 0, k = 0;
    if (!domain.particleCell(particles, p, i, j, k)) continue;
    CellInfo& info = cells[domain.cellIndex(i, j, k)];
    ++info.count;
    info.velocitySum += particles.vel[p];
  }

  for (size_t cell = 0; cell < cells.size(); ++cell) {
    const int count = cells[cell].count;
    if (count <= 0) continue;
    ++result.cells;
    result.particlesBefore += count;
    result.particlesAfter += count;
    if (count >= target) continue;

    ++result.underfullCells;
    const int i = static_cast<int>(cell % static_cast<size_t>(domain.nx));
    const int j = static_cast<int>((cell / static_cast<size_t>(domain.nx)) %
                                   static_cast<size_t>(domain.ny));
    const int k = static_cast<int>(cell /
                                   (static_cast<size_t>(domain.nx) *
                                    static_cast<size_t>(domain.ny)));
    const Vec3 avgVel = cells[cell].velocitySum * (1.0 / static_cast<double>(count));

    int slots[8] = {0, 1, 2, 3, 4, 5, 6, 7};
    std::sort(slots, slots + 8, [&](int a, int b) {
      const uint32_t sa = slotScore(cell, a, seed);
      const uint32_t sb = slotScore(cell, b, seed);
      if (sa != sb) return sa < sb;
      return a < b;
    });

    const int toAdd = target - count;
    for (int a = 0; a < toAdd; ++a) {
      const int slot = slots[a & 7];
      const double sx = 0.25 + 0.5 * static_cast<double>(slot & 1);
      const double sy = 0.25 + 0.5 * static_cast<double>((slot >> 1) & 1);
      const double sz = 0.25 + 0.5 * static_cast<double>((slot >> 2) & 1);
      const Vec3 pos{domain.ox + (static_cast<double>(i) + sx) * domain.dx,
                     domain.oy + (static_cast<double>(j) + sy) * domain.dx,
                     domain.oz + (static_cast<double>(k) + sz) * domain.dx};
      particles.add(pos, avgVel, 0);
      ++result.added;
      ++result.particlesAfter;
    }
  }

  return result;
}

} // namespace pa3d
