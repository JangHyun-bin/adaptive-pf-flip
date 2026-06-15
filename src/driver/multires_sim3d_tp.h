#pragma once

#include "grid/multires_mac_grid3d.h"
#include "particles/particles3d_tp.h"
#include "pressure/multires_pressure3d.h"
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
  double cg_rel_tol = 1e-6;
  bool cg_jacobi_preconditioner = true;
  bool cg_flexible_beta = false;
  bool cg_adaptive_restart = true;
  double cg_restart_growth = 10.0;
  int cg_relaxation_sweeps = 0;
  double cg_relaxation_omega = 0.67;
  double cg_relaxation_min_omega = 0.05;
  int cg_residual_history_stride = 0;
  int cg_residual_history_limit = 64;
  bool cg_coarse_correction = false;
  int cg_coarse_correction_iters = 32;
  double cg_coarse_correction_abs_tol = 0.0;
  double cg_coarse_correction_rel_tol = 1e-3;
  bool dynamic_refinement = true;
  int dynamic_particle_padding = 1;
  int dynamic_gas_padding = 2;
  int dynamic_hysteresis_cells = 1;
  int dynamic_max_fine_leaves = 0;
  bool dynamic_budget_limited = false;
  int dynamic_last_fine_leaves = 0;
  bool dynamic_retained_box_valid = false;
  int dynamic_retained_x0 = 0;
  int dynamic_retained_y0 = 0;
  int dynamic_retained_z0 = 0;
  int dynamic_retained_x1 = 0;
  int dynamic_retained_y1 = 0;
  int dynamic_retained_z1 = 0;
  MRPressureSolveStats3D last_pressure_stats;

  MRSim3DTP(int nx, int ny, int nz, double dx);
  void initBubbleTankInterfaceBand();
  void updateDynamicRefinement();
  void step();
  int activePressureCellCount() const;
  int uFaceCount() const;
  int vFaceCount() const;
  int wFaceCount() const;
};
