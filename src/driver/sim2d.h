#pragma once
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
struct Sim2D {
  UniformGrid2D grid;
  Particles2D particles;
  double dt=0.05, rho=1.0, alpha=0.95, gravity=-9.81;
  int cg_iters=200; double cg_tol=1e-6;
  Sim2D(int nx, int ny, double dx) : grid(nx,ny,dx) {}
  void initDamBreak();
  void step();
};
