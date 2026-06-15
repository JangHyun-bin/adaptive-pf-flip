#include "driver/multires_sim3d_tp.h"

#include "driver/multires_ops3d_tp.h"
#include "pressure/multires_pressure3d.h"
#include "transfer/transfer3d_tp.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

namespace {

void seedCell(Particles3DTP& ps, int i, int j, int k, double dx, unsigned char t) {
  for (int s = 0; s < 8; ++s) {
    double x = (i + 0.25 + 0.5 * (s & 1)) * dx;
    double y = (j + 0.25 + 0.5 * ((s >> 1) & 1)) * dx;
    double z = (k + 0.25 + 0.5 * ((s >> 2) & 1)) * dx;
    ps.add({x, y, z}, {0.0, 0.0, 0.0}, t);
  }
}

void setCell(MRMacGrid3D<4>& g, int i, int j, int k, int value) {
  MRCellKey3D c = g.marker.cellAtFineCell(i, j, k);
  if (c.block.level >= 0) {
    g.marker.ref(c) = static_cast<float>(value);
  }
}

int cell(const MRMacGrid3D<4>& g, int i, int j, int k) {
  if (i < 0 || i >= g.layout.nx ||
      j < 0 || j >= g.layout.ny ||
      k < 0 || k >= g.layout.nz) {
    return 2;
  }
  MRCellKey3D c = g.marker.cellAtFineCell(i, j, k);
  return static_cast<int>(g.marker.get(c) + 0.5f);
}

void markCells(MRMacGrid3D<4>& g, const Particles3DTP& ps) {
  g.marker.blocks.clear();

  for (int k = 0; k < g.layout.nz; ++k) {
    for (int j = 0; j < g.layout.ny; ++j) {
      setCell(g, 0, j, k, 2);
      setCell(g, g.layout.nx - 1, j, k, 2);
    }
  }
  for (int k = 0; k < g.layout.nz; ++k) {
    for (int i = 0; i < g.layout.nx; ++i) {
      setCell(g, i, 0, k, 2);
      setCell(g, i, g.layout.ny - 1, k, 2);
    }
  }
  for (int j = 0; j < g.layout.ny; ++j) {
    for (int i = 0; i < g.layout.nx; ++i) {
      setCell(g, i, j, 0, 2);
      setCell(g, i, j, g.layout.nz - 1, 2);
    }
  }

  for (size_t p = 0; p < ps.size(); ++p) {
    int i = static_cast<int>(ps.pos[p].x / g.layout.dx);
    int j = static_cast<int>(ps.pos[p].y / g.layout.dx);
    int k = static_cast<int>(ps.pos[p].z / g.layout.dx);
    if (i >= 0 && i < g.layout.nx &&
        j >= 0 && j < g.layout.ny &&
        k >= 0 && k < g.layout.nz &&
        cell(g, i, j, k) != 2) {
      setCell(g, i, j, k, 1);
    }
  }
}

void applyGravity(MRMacGrid3D<4>& g, double dt, double gravity) {
  for (const MRFaceKey3D& f : g.vFaceRefs()) {
    if (g.gmv(f) > 0.0f) {
      g.v(f) = g.gv(f) + static_cast<float>(dt * gravity);
    }
  }
}

void applyWallBoundary(MRMacGrid3D<4>& g) {
  for (const MRFaceKey3D& f : g.uFaceRefs()) {
    if (f.fineX == 0 || f.fineX == 1 || f.fineX == g.layout.nx - 1 || f.fineX == g.layout.nx) {
      g.u(f) = 0.0f;
    }
  }
  for (const MRFaceKey3D& f : g.vFaceRefs()) {
    if (f.fineY == 0 || f.fineY == 1 || f.fineY == g.layout.ny - 1 || f.fineY == g.layout.ny) {
      g.v(f) = 0.0f;
    }
  }
  for (const MRFaceKey3D& f : g.wFaceRefs()) {
    if (f.fineZ == 0 || f.fineZ == 1 || f.fineZ == g.layout.nz - 1 || f.fineZ == g.layout.nz) {
      g.w(f) = 0.0f;
    }
  }
}

bool inBounds(const MRLayout3D<4>& layout, int i, int j, int k) {
  return i >= 0 && i < layout.nx &&
         j >= 0 && j < layout.ny &&
         k >= 0 && k < layout.nz;
}

size_t cellIndex(const MRLayout3D<4>& layout, int i, int j, int k) {
  return static_cast<size_t>(i) +
         static_cast<size_t>(layout.nx) *
           (static_cast<size_t>(j) + static_cast<size_t>(layout.ny) * static_cast<size_t>(k));
}

bool particleCell(const MRLayout3D<4>& layout,
                  const Particles3DTP& particles,
                  size_t p,
                  int& i,
                  int& j,
                  int& k) {
  const Vec3& x = particles.pos[p];
  if (!std::isfinite(x.x) || !std::isfinite(x.y) || !std::isfinite(x.z)) {
    return false;
  }
  i = static_cast<int>(x.x / layout.dx);
  j = static_cast<int>(x.y / layout.dx);
  k = static_cast<int>(x.z / layout.dx);
  return inBounds(layout, i, j, k);
}

uint32_t mix32(uint32_t x) {
  x ^= x >> 16;
  x *= 0x7feb352du;
  x ^= x >> 15;
  x *= 0x846ca68bu;
  x ^= x >> 16;
  return x;
}

uint32_t particleScore(const MRLayout3D<4>& layout,
                       const Particles3DTP& particles,
                       size_t p,
                       int i,
                       int j,
                       int k,
                       uint32_t seed) {
  const Vec3& x = particles.pos[p];
  const int qx = static_cast<int>((x.x - i * layout.dx) / layout.dx * 1024.0);
  const int qy = static_cast<int>((x.y - j * layout.dx) / layout.dx * 1024.0);
  const int qz = static_cast<int>((x.z - k * layout.dx) / layout.dx * 1024.0);
  uint32_t h = seed;
  h ^= mix32(static_cast<uint32_t>(i) + 0x9e3779b9u);
  h ^= mix32(static_cast<uint32_t>(j) + 0x85ebca6bu);
  h ^= mix32(static_cast<uint32_t>(k) + 0xc2b2ae35u);
  h ^= mix32(static_cast<uint32_t>(qx & 2047) + 0x27d4eb2fu);
  h ^= mix32(static_cast<uint32_t>(qy & 2047) + 0x165667b1u);
  h ^= mix32(static_cast<uint32_t>(qz & 2047) + 0xd3a2646cu);
  return mix32(h);
}

bool sameLeaves(const MRLayout3D<4>& a, const MRLayout3D<4>& b) {
  return a.nx == b.nx &&
         a.ny == b.ny &&
         a.nz == b.nz &&
         a.dx == b.dx &&
         a.leaves() == b.leaves();
}

struct Box3I {
  int x0 = 0;
  int y0 = 0;
  int z0 = 0;
  int x1 = 0;
  int y1 = 0;
  int z1 = 0;
  bool valid = false;
};

void includeBox(Box3I& box, int x0, int y0, int z0, int x1, int y1, int z1) {
  if (x0 >= x1 || y0 >= y1 || z0 >= z1) return;
  if (!box.valid) {
    box = Box3I{x0, y0, z0, x1, y1, z1, true};
    return;
  }
  box.x0 = std::min(box.x0, x0);
  box.y0 = std::min(box.y0, y0);
  box.z0 = std::min(box.z0, z0);
  box.x1 = std::max(box.x1, x1);
  box.y1 = std::max(box.y1, y1);
  box.z1 = std::max(box.z1, z1);
}

Box3I clampBox(const MRLayout3D<4>& layout, Box3I box) {
  if (!box.valid) return box;
  box.x0 = std::max(0, std::min(layout.nx, box.x0));
  box.y0 = std::max(0, std::min(layout.ny, box.y0));
  box.z0 = std::max(0, std::min(layout.nz, box.z0));
  box.x1 = std::max(0, std::min(layout.nx, box.x1));
  box.y1 = std::max(0, std::min(layout.ny, box.y1));
  box.z1 = std::max(0, std::min(layout.nz, box.z1));
  box.valid = box.x0 < box.x1 && box.y0 < box.y1 && box.z0 < box.z1;
  return box;
}

Box3I expandBox(const MRLayout3D<4>& layout, const Box3I& box, int pad) {
  if (!box.valid) return box;
  pad = std::max(0, pad);
  return clampBox(layout, Box3I{box.x0 - pad, box.y0 - pad, box.z0 - pad,
                                box.x1 + pad, box.y1 + pad, box.z1 + pad, true});
}

bool containsBox(const Box3I& outer, const Box3I& inner) {
  return outer.valid && inner.valid &&
         outer.x0 <= inner.x0 && outer.y0 <= inner.y0 && outer.z0 <= inner.z0 &&
         outer.x1 >= inner.x1 && outer.y1 >= inner.y1 && outer.z1 >= inner.z1;
}

void refineBox(MRLayout3D<4>& layout,
               int x0, int y0, int z0,
               int x1, int y1, int z1) {
  x0 = std::max(0, std::min(layout.nx, x0));
  y0 = std::max(0, std::min(layout.ny, y0));
  z0 = std::max(0, std::min(layout.nz, z0));
  x1 = std::max(0, std::min(layout.nx, x1));
  y1 = std::max(0, std::min(layout.ny, y1));
  z1 = std::max(0, std::min(layout.nz, z1));
  if (x0 < x1 && y0 < y1 && z0 < z1) {
    layout.refineFineCellBox(x0, y0, z0, x1, y1, z1);
  }
}

MRLayout3D<4> layoutWithFineBox(const MRLayout3D<4>& base, const Box3I& box) {
  MRLayout3D<4> next(base.nx, base.ny, base.nz, base.dx);
  next.setCoarseEverywhere(1);
  if (box.valid) {
    refineBox(next, box.x0, box.y0, box.z0, box.x1, box.y1, box.z1);
  }
  next.enforceTwoToOneBalance();
  return next;
}

size_t fineLeafCountForBox(const MRLayout3D<4>& base, const Box3I& box) {
  return layoutWithFineBox(base, box).countLevel(0);
}

int boxExtent(const Box3I& box, int axis) {
  if (axis == 0) return box.x1 - box.x0;
  if (axis == 1) return box.y1 - box.y0;
  return box.z1 - box.z0;
}

bool shrinkLargestAxis(Box3I& box, double cx, double cy, double cz) {
  int axis = 0;
  if (boxExtent(box, 1) > boxExtent(box, axis)) axis = 1;
  if (boxExtent(box, 2) > boxExtent(box, axis)) axis = 2;
  if (boxExtent(box, axis) <= 1) return false;

  if (axis == 0) {
    if ((box.x1 - cx) >= (cx - box.x0)) --box.x1;
    else ++box.x0;
  } else if (axis == 1) {
    if ((box.y1 - cy) >= (cy - box.y0)) --box.y1;
    else ++box.y0;
  } else {
    if ((box.z1 - cz) >= (cz - box.z0)) --box.z1;
    else ++box.z0;
  }
  box.valid = box.x0 < box.x1 && box.y0 < box.y1 && box.z0 < box.z1;
  return box.valid;
}

Box3I fitBoxToFineLeafBudget(const MRLayout3D<4>& base, Box3I box, int maxFineLeaves, bool& limited) {
  limited = false;
  if (!box.valid || maxFineLeaves <= 0) return box;

  const size_t budget = static_cast<size_t>(maxFineLeaves);
  if (fineLeafCountForBox(base, box) <= budget) return box;

  limited = true;
  double cx = 0.5 * static_cast<double>(box.x0 + box.x1);
  double cy = 0.5 * static_cast<double>(box.y0 + box.y1);
  double cz = 0.5 * static_cast<double>(box.z0 + box.z1);
  while (fineLeafCountForBox(base, box) > budget) {
    if (!shrinkLargestAxis(box, cx, cy, cz)) break;
  }
  return box;
}

void refineBubbleStaticBand(MRLayout3D<4>& layout) {
  int waterLevel = layout.ny / 2;
  int markerBandTop = std::min(layout.ny, waterLevel + 2);
  refineBox(layout, 0, 0, 0, layout.nx, markerBandTop, layout.nz);

  int cx0 = std::max(0, layout.nx / 2 - layout.nx / 4);
  int cx1 = std::min(layout.nx, layout.nx / 2 + layout.nx / 4);
  int cy0 = std::max(0, waterLevel / 4);
  int cy1 = std::min(layout.ny, waterLevel);
  int cz0 = std::max(0, layout.nz / 2 - layout.nz / 4);
  int cz1 = std::min(layout.nz, layout.nz / 2 + layout.nz / 4);
  refineBox(layout, cx0, cy0, cz0, cx1, cy1, cz1);
  layout.enforceTwoToOneBalance();
}

} // namespace

MRSim3DTP::MRSim3DTP(int nx, int ny, int nz, double dx)
  : layout(nx, ny, nz, dx), grid(layout) {}

void MRSim3DTP::initBubbleTankInterfaceBand() {
  particles = Particles3DTP();
  phase.rho_tilde_0 = calibrateRhoTilde0(phase, Vp);
  dynamic_budget_limited = false;
  dynamic_last_fine_leaves = 0;
  dynamic_retained_box_valid = false;
  narrow_band_air_removed_last = 0;
  narrow_band_air_removed_total = 0;
  gas_particle_coarsening_removed_last = 0;
  gas_particle_coarsening_removed_total = 0;

  int waterLevel = layout.ny / 2;
  layout.setCoarseEverywhere(1);
  refineBubbleStaticBand(layout);
  grid = MRMacGrid3D<4>(layout);

  double cx = layout.nx * 0.5;
  double cy = waterLevel * 0.375;
  double cz = layout.nz * 0.5;
  double r = std::max(1.25, std::min(layout.nx, layout.nz) * 0.1875);
  for (int k = 1; k < layout.nz - 1; ++k) {
    for (int j = 1; j < waterLevel; ++j) {
      for (int i = 1; i < layout.nx - 1; ++i) {
        double dx = (i + 0.5) - cx;
        double dy = (j + 0.5) - cy;
        double dz = (k + 0.5) - cz;
        bool gas = dx * dx + dy * dy + dz * dz < r * r;
        seedCell(particles, i, j, k, layout.dx, gas ? 1 : 0);
      }
    }
  }

  applyParticleAdaptivity();
  if (dynamic_refinement) {
    updateDynamicRefinement();
  }
}

void MRSim3DTP::applyNarrowBandAir() {
  narrow_band_air_removed_last = 0;
  narrow_band_air_liquid_cells_last = 0;
  narrow_band_air_gas_particles_before_last = 0;
  narrow_band_air_gas_particles_after_last = 0;
  if (!narrow_band_air) return;

  std::vector<unsigned char> liquidCells(static_cast<size_t>(layout.nx) *
                                           static_cast<size_t>(layout.ny) *
                                           static_cast<size_t>(layout.nz),
                                         0);

  for (size_t p = 0; p < particles.size(); ++p) {
    if (particles.type[p] != 0) continue;
    int i = 0, j = 0, k = 0;
    if (!particleCell(layout, particles, p, i, j, k)) continue;
    unsigned char& occupied = liquidCells[cellIndex(layout, i, j, k)];
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
      if (kk < 0 || kk >= layout.nz) continue;
      for (int dj = -radius; dj <= radius; ++dj) {
        int jj = j + dj;
        if (jj < 0 || jj >= layout.ny) continue;
        for (int di = -radius; di <= radius; ++di) {
          int ii = i + di;
          if (ii < 0 || ii >= layout.nx) continue;
          if (liquidCells[cellIndex(layout, ii, jj, kk)]) return true;
        }
      }
    }
    return false;
  };

  const size_t removed = particles.eraseIf([&](size_t p) {
    if (particles.type[p] != 1) return false;
    ++narrow_band_air_gas_particles_before_last;
    int i = 0, j = 0, k = 0;
    const bool keep = particleCell(layout, particles, p, i, j, k) && gasInLiquidBand(i, j, k);
    if (keep) ++narrow_band_air_gas_particles_after_last;
    return !keep;
  });
  narrow_band_air_removed_last = static_cast<int>(removed);
  narrow_band_air_removed_total += narrow_band_air_removed_last;
}

void MRSim3DTP::applyGasParticleCoarsening() {
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
    if (!particleCell(layout, particles, p, i, j, k)) {
      continue;
    }
    entries.push_back(GasEntry{p,
                               cellIndex(layout, i, j, k),
                               particleScore(layout,
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

void MRSim3DTP::applyParticleAdaptivity() {
  applyNarrowBandAir();
  applyGasParticleCoarsening();
}

void MRSim3DTP::updateDynamicRefinement() {
  if (!dynamic_refinement) return;

  int minX = layout.nx;
  int minY = layout.ny;
  int minZ = layout.nz;
  int maxX = -1;
  int maxY = -1;
  int maxZ = -1;
  int gasMinX = layout.nx;
  int gasMinY = layout.ny;
  int gasMinZ = layout.nz;
  int gasMaxX = -1;
  int gasMaxY = -1;
  int gasMaxZ = -1;

  for (size_t p = 0; p < particles.size(); ++p) {
    const Vec3& pos = particles.pos[p];
    if (!std::isfinite(pos.x) || !std::isfinite(pos.y) || !std::isfinite(pos.z)) {
      continue;
    }

    int i = static_cast<int>(pos.x / layout.dx);
    int j = static_cast<int>(pos.y / layout.dx);
    int k = static_cast<int>(pos.z / layout.dx);
    if (i < 0 || i >= layout.nx ||
        j < 0 || j >= layout.ny ||
        k < 0 || k >= layout.nz) {
      continue;
    }

    minX = std::min(minX, i);
    minY = std::min(minY, j);
    minZ = std::min(minZ, k);
    maxX = std::max(maxX, i);
    maxY = std::max(maxY, j);
    maxZ = std::max(maxZ, k);

    if (particles.type[p] == 1) {
      gasMinX = std::min(gasMinX, i);
      gasMinY = std::min(gasMinY, j);
      gasMinZ = std::min(gasMinZ, k);
      gasMaxX = std::max(gasMaxX, i);
      gasMaxY = std::max(gasMaxY, j);
      gasMaxZ = std::max(gasMaxZ, k);
    }
  }

  Box3I desired;
  if (maxX >= 0) {
    int pad = std::max(0, dynamic_particle_padding);
    includeBox(desired,
               minX - pad, minY - pad, minZ - pad,
               maxX + pad + 1, maxY + pad + 1, maxZ + pad + 1);
  }

  if (gasMaxX >= 0) {
    int pad = std::max(0, dynamic_gas_padding);
    includeBox(desired,
               gasMinX - pad, gasMinY - pad, gasMinZ - pad,
               gasMaxX + pad + 1, gasMaxY + pad + 1, gasMaxZ + pad + 1);
  }

  desired = clampBox(layout, desired);
  Box3I target;
  dynamic_budget_limited = false;
  if (desired.valid) {
    Box3I retained{dynamic_retained_x0, dynamic_retained_y0, dynamic_retained_z0,
                   dynamic_retained_x1, dynamic_retained_y1, dynamic_retained_z1,
                   dynamic_retained_box_valid};
    target = containsBox(retained, desired)
      ? retained
      : expandBox(layout, desired, dynamic_hysteresis_cells);
    target = fitBoxToFineLeafBudget(layout, target, dynamic_max_fine_leaves, dynamic_budget_limited);
  }

  dynamic_retained_box_valid = target.valid;
  if (target.valid) {
    dynamic_retained_x0 = target.x0;
    dynamic_retained_y0 = target.y0;
    dynamic_retained_z0 = target.z0;
    dynamic_retained_x1 = target.x1;
    dynamic_retained_y1 = target.y1;
    dynamic_retained_z1 = target.z1;
  }

  MRLayout3D<4> next = layoutWithFineBox(layout, target);
  dynamic_last_fine_leaves = static_cast<int>(next.countLevel(0));
  if (!sameLeaves(layout, next) || !sameLeaves(grid.layout, next)) {
    layout = next;
    grid = MRMacGrid3D<4>(layout);
  }
}

void MRSim3DTP::step() {
  applyParticleAdaptivity();
  updateDynamicRefinement();
  markCells(grid, particles);
  mrP2G3D_tp(grid, particles, phase, Vp);
  MRMacGrid3D<4> saved = grid;

  applyGravity(grid, dt, gravity);
  applyWallBoundary(grid);
  MRPressureSolveConfig3D pressureConfig;
  pressureConfig.max_iterations = cg_iters;
  pressureConfig.absolute_tolerance = cg_tol;
  pressureConfig.relative_tolerance = cg_rel_tol;
  pressureConfig.use_jacobi_preconditioner = cg_jacobi_preconditioner;
  pressureConfig.use_flexible_cg_beta = cg_flexible_beta;
  pressureConfig.adaptive_restart = cg_adaptive_restart;
  pressureConfig.restart_growth_threshold = cg_restart_growth;
  pressureConfig.relaxation_sweeps = cg_relaxation_sweeps;
  pressureConfig.relaxation_omega = cg_relaxation_omega;
  pressureConfig.relaxation_min_omega = cg_relaxation_min_omega;
  pressureConfig.residual_history_stride = cg_residual_history_stride;
  pressureConfig.residual_history_limit = cg_residual_history_limit;
  pressureConfig.use_coarse_correction = cg_coarse_correction;
  pressureConfig.coarse_correction_iterations = cg_coarse_correction_iters;
  pressureConfig.coarse_correction_sweeps = cg_coarse_correction_sweeps;
  pressureConfig.coarse_correction_absolute_tolerance = cg_coarse_correction_abs_tol;
  pressureConfig.coarse_correction_relative_tolerance = cg_coarse_correction_rel_tol;
  pressureConfig.coarse_correction_min_scale = cg_coarse_correction_min_scale;
  pressureConfig.use_coarse_preconditioner = cg_coarse_preconditioner;
  pressureConfig.coarse_preconditioner_iterations = cg_coarse_preconditioner_iters;
  pressureConfig.coarse_preconditioner_absolute_tolerance = cg_coarse_preconditioner_abs_tol;
  pressureConfig.coarse_preconditioner_relative_tolerance = cg_coarse_preconditioner_rel_tol;
  pressureConfig.coarse_preconditioner_scale = cg_coarse_preconditioner_scale;
  pressureConfig.coarse_preconditioner_min_rz_gain = cg_coarse_preconditioner_min_rz_gain;
  pressureConfig.coarse_preconditioner_max_work_ratio =
    cg_coarse_preconditioner_max_work_ratio;
  pressureConfig.coarse_preconditioner_auto_disable =
    cg_coarse_preconditioner_auto_disable;
  pressureConfig.coarse_preconditioner_auto_disable_after =
    cg_coarse_preconditioner_auto_disable_after;
  projectMR3D(grid, phase, dt, pressureConfig, &last_pressure_stats);
  mrG2P3D_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  mrAdvect3D_tp(particles, grid, dt);
}

int MRSim3DTP::activePressureCellCount() const {
  return static_cast<int>(grid.p.leafCells().size());
}

int MRSim3DTP::uFaceCount() const {
  return static_cast<int>(grid.uFaceRefs().size());
}

int MRSim3DTP::vFaceCount() const {
  return static_cast<int>(grid.vFaceRefs().size());
}

int MRSim3DTP::wFaceCount() const {
  return static_cast<int>(grid.wFaceRefs().size());
}
