#pragma once
#include "grid/sparse_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
struct SparseSim2DTP {
  SparseMacGrid2D<8> grid; Particles2DTP particles; PhaseParams phase;
  double dt=0.02, gravity=-9.81, Vp=1.0;
  double alpha_liquid=0.95, alpha_gas=0.95;
  int cg_iters=400; double cg_tol=1e-7;
  SparseSim2DTP(int nx,int ny,double dx) : grid(nx,ny,dx) {}
  void initRayleighTaylor();
  void initBubbleTank();
  void step();
};
