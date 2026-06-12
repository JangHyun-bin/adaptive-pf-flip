#pragma once
#include "grid/sparse_mac_grid3d.h"
#include "particles/particles3d.h"

struct SparseSim3D {
  SparseMacGrid3D<4> grid;
  Particles3D particles;
  double dt = 0.05, alpha = 0.95, gravity = -9.81;
  int cg_iters = 300;
  double cg_tol = 1e-6;

  SparseSim3D(int nx, int ny, int nz, double dx) : grid(nx, ny, nz, dx) {}
  void initDamBreak();
  void step();
};
