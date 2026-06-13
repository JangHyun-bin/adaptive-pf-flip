#include "driver/multires_sim3d_tp.h"

#include "driver/multires_ops3d_tp.h"
#include "pressure/multires_pressure3d.h"
#include "transfer/transfer3d_tp.h"

#include <algorithm>
#include <cmath>

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
  for (const MRFaceKey3D& f : g.vFaces()) {
    if (g.gmv(f) > 0.0f) {
      g.v(f) = g.gv(f) + static_cast<float>(dt * gravity);
    }
  }
}

void applyWallBoundary(MRMacGrid3D<4>& g) {
  for (const MRFaceKey3D& f : g.uFaces()) {
    if (f.fineX == 0 || f.fineX == 1 || f.fineX == g.layout.nx - 1 || f.fineX == g.layout.nx) {
      g.u(f) = 0.0f;
    }
  }
  for (const MRFaceKey3D& f : g.vFaces()) {
    if (f.fineY == 0 || f.fineY == 1 || f.fineY == g.layout.ny - 1 || f.fineY == g.layout.ny) {
      g.v(f) = 0.0f;
    }
  }
  for (const MRFaceKey3D& f : g.wFaces()) {
    if (f.fineZ == 0 || f.fineZ == 1 || f.fineZ == g.layout.nz - 1 || f.fineZ == g.layout.nz) {
      g.w(f) = 0.0f;
    }
  }
}

} // namespace

MRSim3DTP::MRSim3DTP(int nx, int ny, int nz, double dx)
  : layout(nx, ny, nz, dx), grid(layout) {}

void MRSim3DTP::initBubbleTankInterfaceBand() {
  particles = Particles3DTP();
  phase.rho_tilde_0 = calibrateRhoTilde0(phase, Vp);

  int waterLevel = layout.ny / 2;
  int markerBandTop = std::min(layout.ny, waterLevel + 2);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(0, 0, 0, layout.nx, markerBandTop, layout.nz);

  int cx0 = std::max(0, layout.nx / 2 - layout.nx / 4);
  int cx1 = std::min(layout.nx, layout.nx / 2 + layout.nx / 4);
  int cy0 = std::max(0, waterLevel / 4);
  int cy1 = std::min(layout.ny, waterLevel);
  int cz0 = std::max(0, layout.nz / 2 - layout.nz / 4);
  int cz1 = std::min(layout.nz, layout.nz / 2 + layout.nz / 4);
  layout.refineFineCellBox(cx0, cy0, cz0, cx1, cy1, cz1);
  layout.enforceTwoToOneBalance();
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
}

void MRSim3DTP::step() {
  markCells(grid, particles);
  mrP2G3D_tp(grid, particles, phase, Vp);
  MRMacGrid3D<4> saved = grid;

  applyGravity(grid, dt, gravity);
  applyWallBoundary(grid);
  projectMR3D(grid, phase, dt, cg_iters, cg_tol);
  mrG2P3D_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  mrAdvect3D_tp(particles, grid, dt);
}

int MRSim3DTP::activePressureCellCount() const {
  return static_cast<int>(grid.p.leafCells().size());
}
