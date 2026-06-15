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
  bool gas_particle_coarsening = false;
  int gas_particles_per_cell_target = 4;
  unsigned int gas_particle_coarsening_seed = 0x9e3779b9u;
  int gas_particle_coarsening_removed_last = 0;
  int gas_particle_coarsening_removed_total = 0;
  int gas_particle_coarsening_cells_last = 0;
  int gas_particle_coarsening_overfull_cells_last = 0;
  int gas_particle_coarsening_before_last = 0;
  int gas_particle_coarsening_after_last = 0;
  bool liquid_particle_coarsening = false;
  int liquid_particles_per_cell_target = 4;
  unsigned int liquid_particle_coarsening_seed = 0x7f4a7c15u;
  int liquid_particle_coarsening_removed_last = 0;
  int liquid_particle_coarsening_removed_total = 0;
  int liquid_particle_coarsening_cells_last = 0;
  int liquid_particle_coarsening_overfull_cells_last = 0;
  int liquid_particle_coarsening_before_last = 0;
  int liquid_particle_coarsening_after_last = 0;
  bool liquid_particle_refill = false;
  bool liquid_particle_refill_interface_only = false;
  int liquid_particle_refill_interface_radius = 1;
  int liquid_particle_refill_max_added_per_step = 0;
  int liquid_refill_particles_per_cell_target = 4;
  unsigned int liquid_particle_refill_seed = 0x6a09e667u;
  int liquid_particle_refill_added_last = 0;
  int liquid_particle_refill_added_total = 0;
  int liquid_particle_refill_cells_last = 0;
  int liquid_particle_refill_interface_cells_last = 0;
  int liquid_particle_refill_underfull_cells_last = 0;
  int liquid_particle_refill_budget_limited_last = 0;
  int liquid_particle_refill_before_last = 0;
  int liquid_particle_refill_after_last = 0;
  int particle_boundary_clamped_liquid_last = 0;
  int particle_boundary_clamped_gas_last = 0;
  int particle_boundary_clamped_liquid_total = 0;
  int particle_boundary_clamped_gas_total = 0;
  int particle_boundary_clamped_x_lo_last = 0;
  int particle_boundary_clamped_x_hi_last = 0;
  int particle_boundary_clamped_y_lo_last = 0;
  int particle_boundary_clamped_y_hi_last = 0;
  int particle_boundary_clamped_z_lo_last = 0;
  int particle_boundary_clamped_z_hi_last = 0;

  SparseSim3DTP(int nx, int ny, int nz, double dx) : grid(nx, ny, nz, dx) {}
  void initTwoPhaseDamBreak();
  void initRayleighTaylor();
  void initBubbleTank();
  void applyNarrowBandAir();
  void applyGasParticleCoarsening();
  void applyLiquidParticleCoarsening();
  void applyLiquidParticleRefill();
  void applyParticleAdaptivity();
  void step();
};
