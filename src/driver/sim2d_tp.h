#pragma once
#include "grid/uniform_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
struct Sim2DTP {
  UniformGrid2D grid;
  Particles2DTP particles;
  PhaseParams phase;
  double dt=0.02, gravity=-9.81, Vp=1.0;
  double alpha_liquid=0.95, alpha_gas=0.95;
  int cg_iters=400; double cg_tol=1e-7;
  Sim2DTP(int nx,int ny,double dx) : grid(nx,ny,dx) {}
  void initTwoPhaseDamBreak();
  void initRayleighTaylor();
  void step();
};
