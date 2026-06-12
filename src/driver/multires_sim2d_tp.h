#pragma once

#include "grid/multires_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"

struct MRSim2DTP {
  MRLayout2D<8> layout;
  MRMacGrid2D<8> grid;
  Particles2DTP particles;
  PhaseParams phase;
  double dt = 0.02;
  double gravity = -9.81;
  double Vp = 1.0;
  double alpha_liquid = 0.95;
  double alpha_gas = 0.95;
  int cg_iters = 400;
  double cg_tol = 1e-7;

  MRSim2DTP(int nx, int ny, double dx);
  void initBubbleTankInterfaceBand();
  void step();
  int activePressureCellCount() const;
};
