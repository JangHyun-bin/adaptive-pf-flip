#pragma once
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
struct Sim3D {
  UniformGrid3D grid;
  Particles3D particles;
  double dt=0.05, rho=1.0, gravity=-9.81;
  double target_nu=0.0;
  int cg_iters=300; double cg_tol=1e-6; int extrap_sweeps=3;
  Sim3D(int nx,int ny,int nz,double dx) : grid(nx,ny,nz,dx) {}
  void initDamBreak();
  void step();
};
