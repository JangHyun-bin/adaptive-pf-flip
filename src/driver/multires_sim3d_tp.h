#pragma once

#include "grid/multires_mac_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"

struct MRSim3DTP {
  MRLayout3D<4> layout;
  MRMacGrid3D<4> grid;
  Particles3DTP particles;
  PhaseParams phase;
  double dt = 0.02;
  double gravity = -9.81;
  double Vp = 1.0;
  double alpha_liquid = 0.95;
  double alpha_gas = 0.95;
  int cg_iters = 160;
  double cg_tol = 1e-7;

  MRSim3DTP(int nx, int ny, int nz, double dx);
  void initBubbleTankInterfaceBand();
  void step();
  int activePressureCellCount() const;
};
