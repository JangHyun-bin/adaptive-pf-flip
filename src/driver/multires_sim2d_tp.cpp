#include "driver/multires_sim2d_tp.h"

#include "driver/multires_ops2d_tp.h"
#include "pressure/multires_pressure2d.h"
#include "transfer/transfer2d_tp.h"

#include <algorithm>
#include <cmath>

namespace {

void seedCell(Particles2DTP& ps, int i, int j, double dx, unsigned char t) {
  for (int s = 0; s < 4; ++s) {
    double x = (i + 0.25 + 0.5 * (s % 2)) * dx;
    double y = (j + 0.25 + 0.5 * (s / 2)) * dx;
    ps.add({x, y}, {0.0, 0.0}, t);
  }
}

void setCell(MRMacGrid2D<8>& g, int i, int j, int value) {
  MRCellKey c = g.marker.cellAtFineCell(i, j);
  if (c.block.level >= 0) {
    g.marker.ref(c) = static_cast<float>(value);
  }
}

int cell(const MRMacGrid2D<8>& g, int i, int j) {
  if (i < 0 || i >= g.layout.nx || j < 0 || j >= g.layout.ny) {
    return 2;
  }
  MRCellKey c = g.marker.cellAtFineCell(i, j);
  return static_cast<int>(g.marker.get(c) + 0.5f);
}

void markCells(MRMacGrid2D<8>& g, const Particles2DTP& ps) {
  g.marker.blocks.clear();

  for (int j = 0; j < g.layout.ny; ++j) {
    setCell(g, 0, j, 2);
    setCell(g, g.layout.nx - 1, j, 2);
  }
  for (int i = 0; i < g.layout.nx; ++i) {
    setCell(g, i, 0, 2);
    setCell(g, i, g.layout.ny - 1, 2);
  }

  for (size_t k = 0; k < ps.size(); ++k) {
    int i = static_cast<int>(ps.pos[k].x / g.layout.dx);
    int j = static_cast<int>(ps.pos[k].y / g.layout.dx);
    if (i >= 0 && i < g.layout.nx && j >= 0 && j < g.layout.ny && cell(g, i, j) != 2) {
      setCell(g, i, j, 1);
    }
  }
}

void applyBoundaryVelocities(MRMacGrid2D<8>& g) {
  for (const MRFaceKey& f : g.uFaces()) {
    if (f.fineX == 0 || f.fineX == 1 || f.fineX == g.layout.nx - 1 || f.fineX == g.layout.nx) {
      g.u(f) = 0.0f;
    }
  }
  for (const MRFaceKey& f : g.vFaces()) {
    if (f.fineY == 0 || f.fineY == 1 || f.fineY == g.layout.ny - 1 || f.fineY == g.layout.ny) {
      g.v(f) = 0.0f;
    }
  }
}

} // namespace

MRSim2DTP::MRSim2DTP(int nx, int ny, double dx)
  : layout(nx, ny, dx), grid(layout) {}

void MRSim2DTP::initBubbleTankInterfaceBand() {
  particles = Particles2DTP();
  phase.rho_tilde_0 = calibrateRhoTilde0_2d(phase, Vp);

  int wl = layout.ny / 2;
  int markerBandTop = std::min(layout.ny, wl + 4);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(0, 0, layout.nx, markerBandTop);
  layout.refineFineCellBox(12, 4, 36, 28);
  layout.enforceTwoToOneBalance();
  grid = MRMacGrid2D<8>(layout);

  double cx = layout.nx * 0.5;
  double cy = wl * 0.375;
  double r = layout.nx * 0.09375;
  for (int j = 1; j < wl; ++j) {
    for (int i = 1; i < layout.nx - 1; ++i) {
      double dxc = (i + 0.5) - cx;
      double dyc = (j + 0.5) - cy;
      bool gas = (dxc * dxc + dyc * dyc) < r * r;
      seedCell(particles, i, j, layout.dx, gas ? 1 : 0);
    }
  }
}

void MRSim2DTP::step() {
  markCells(grid, particles);
  mrP2G_tp(grid, particles, phase, Vp);
  MRMacGrid2D<8> saved = grid;

  for (const MRFaceKey& f : grid.vFaces()) {
    if (grid.gmv(f) > 0.0f) {
      grid.v(f) = grid.gv(f) + static_cast<float>(dt * gravity);
    }
  }

  applyBoundaryVelocities(grid);
  projectMR(grid, phase, dt, cg_iters, cg_tol);
  mrG2P_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  mrAdvect_tp(particles, grid, dt);
}

int MRSim2DTP::activePressureCellCount() const {
  return static_cast<int>(grid.p.leafCells().size());
}
