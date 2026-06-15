#pragma once
#include "grid/sparse_mac_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"

struct SparseSim3DTP {
  SparseMacGrid3D<4> grid;
  Particles3DTP particles;
  PhaseParams phase;
  double dt = 0.02, gravity = -9.81, Vp = 1.0, alpha_liquid = 0.95, alpha_gas = 0.95;
  int cg_iters = 600;
  double cg_tol = 1e-7;
  bool narrow_band_air = false;
  int narrow_band_air_radius = 2;
  int narrow_band_air_removed_last = 0;
  int narrow_band_air_removed_total = 0;
  int narrow_band_air_liquid_cells_last = 0;
  int narrow_band_air_gas_particles_before_last = 0;
  int narrow_band_air_gas_particles_after_last = 0;

  SparseSim3DTP(int nx, int ny, int nz, double dx) : grid(nx, ny, nz, dx) {}
  void initTwoPhaseDamBreak();
  void initRayleighTaylor();
  void initBubbleTank();
  void applyNarrowBandAir();
  void step();
};
