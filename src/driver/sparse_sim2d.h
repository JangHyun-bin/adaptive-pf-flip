#pragma once
#include "grid/sparse_mac_grid2d.h"
#include "particles/particles2d.h"
struct SparseSim2D {
  SparseMacGrid2D<8> grid; Particles2D particles;
  double dt=0.05, alpha=0.95, gravity=-9.81; int cg_iters=200; double cg_tol=1e-6;
  SparseSim2D(int nx,int ny,double dx) : grid(nx,ny,dx) {}
  void initDamBreak();
  void step();
};
