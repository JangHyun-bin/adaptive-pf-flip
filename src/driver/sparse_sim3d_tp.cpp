#include "driver/sparse_sim3d_tp.h"
#include "driver/particle_adaptivity3d.h"
#include "driver/sparse_ops3d_tp.h"
#include "driver/timestep3d.h"
#include "transfer/transfer3d_tp.h"

#include <algorithm>
#include <cmath>

namespace {

void seedCell(Particles3DTP& ps, int i, int j, int k, double dx, unsigned char type,
              const Vec3& velocity = Vec3{0.0, 0.0, 0.0}) {
  for (int s = 0; s < 8; ++s) {
    double x = (i + 0.25 + 0.5 * (s & 1)) * dx;
    double y = (j + 0.25 + 0.5 * ((s >> 1) & 1)) * dx;
    double z = (k + 0.25 + 0.5 * ((s >> 2) & 1)) * dx;
    ps.add({x, y, z}, velocity, type);
  }
}

void markCells(SparseMacGrid3D<4>& g, const Particles3DTP& ps) {
  g.mkf.clear();
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j < g.ny; ++j) {
      g.setCell(0, j, k, 2);
      g.setCell(g.nx - 1, j, k, 2);
    }
  }
  for (int k = 0; k < g.nz; ++k) {
    for (int i = 0; i < g.nx; ++i) {
      g.setCell(i, 0, k, 2);
      g.setCell(i, g.ny - 1, k, 2);
    }
  }
  for (int j = 0; j < g.ny; ++j) {
    for (int i = 0; i < g.nx; ++i) {
      g.setCell(i, j, 0, 2);
      g.setCell(i, j, g.nz - 1, 2);
    }
  }
  for (size_t p = 0; p < ps.size(); ++p) {
    int i = (int)((ps.pos[p].x - g.ox) / g.dx);
    int j = (int)((ps.pos[p].y - g.oy) / g.dx);
    int k = (int)((ps.pos[p].z - g.oz) / g.dx);
    if (g.inBounds(i, j, k) && g.cell(i, j, k) != 2) {
      g.setCell(i, j, k, 1);
    }
  }
}

void applyGravity(SparseMacGrid3D<4>& g, double dt, double gravity) {
  for (int b : g.mvf.activeBlockIds()) {
    int bx, by, bz;
    g.mvf.blockCoords(b, bx, by, bz);
    for (int lz = 0; lz < 4; ++lz) {
      for (int ly = 0; ly < 4; ++ly) {
        for (int lx = 0; lx < 4; ++lx) {
          int i = bx * 4 + lx;
          int j = by * 4 + ly;
          int k = bz * 4 + lz;
          if (i >= g.nx || j > g.ny || k >= g.nz) continue;
          if (g.gmv(i, j, k) > 0.0f) {
            g.v(i, j, k) = g.gv(i, j, k) + (float)(dt * gravity);
          }
        }
      }
    }
  }
}

void applyWallBoundary(SparseMacGrid3D<4>& g) {
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j < g.ny; ++j) {
      g.u(0, j, k) = 0.0f;
      g.u(1, j, k) = 0.0f;
      g.u(g.nx - 1, j, k) = 0.0f;
      g.u(g.nx, j, k) = 0.0f;
    }
  }
  for (int k = 0; k < g.nz; ++k) {
    for (int i = 0; i < g.nx; ++i) {
      g.v(i, 0, k) = 0.0f;
      g.v(i, 1, k) = 0.0f;
      g.v(i, g.ny - 1, k) = 0.0f;
      g.v(i, g.ny, k) = 0.0f;
    }
  }
  for (int j = 0; j < g.ny; ++j) {
    for (int i = 0; i < g.nx; ++i) {
      g.w(i, j, 0) = 0.0f;
      g.w(i, j, 1) = 0.0f;
      g.w(i, j, g.nz - 1) = 0.0f;
      g.w(i, j, g.nz) = 0.0f;
    }
  }
}

void resetParticleBoundaryStats(SparseSim3DTP& sim) {
  sim.particle_boundary_clamped_liquid_last = 0;
  sim.particle_boundary_clamped_gas_last = 0;
  sim.particle_boundary_clamped_liquid_total = 0;
  sim.particle_boundary_clamped_gas_total = 0;
  sim.particle_boundary_clamped_x_lo_last = 0;
  sim.particle_boundary_clamped_x_hi_last = 0;
  sim.particle_boundary_clamped_y_lo_last = 0;
  sim.particle_boundary_clamped_y_hi_last = 0;
  sim.particle_boundary_clamped_z_lo_last = 0;
  sim.particle_boundary_clamped_z_hi_last = 0;
  sim.escaped_droplet_candidates_last = 0;
  sim.escaped_bubble_candidates_last = 0;
  sim.escaped_droplet_candidates_total = 0;
  sim.escaped_bubble_candidates_total = 0;
}

void storeParticleBoundaryStats(SparseSim3DTP& sim, const ParticleEscapeStats3D& stats) {
  sim.particle_boundary_clamped_liquid_last = stats.clamped_liquid;
  sim.particle_boundary_clamped_gas_last = stats.clamped_gas;
  sim.particle_boundary_clamped_liquid_total += stats.clamped_liquid;
  sim.particle_boundary_clamped_gas_total += stats.clamped_gas;
  sim.particle_boundary_clamped_x_lo_last = stats.clamped_x_lo;
  sim.particle_boundary_clamped_x_hi_last = stats.clamped_x_hi;
  sim.particle_boundary_clamped_y_lo_last = stats.clamped_y_lo;
  sim.particle_boundary_clamped_y_hi_last = stats.clamped_y_hi;
  sim.particle_boundary_clamped_z_lo_last = stats.clamped_z_lo;
  sim.particle_boundary_clamped_z_hi_last = stats.clamped_z_hi;
  sim.escaped_droplet_candidates_last = stats.droplet_candidates();
  sim.escaped_bubble_candidates_last = stats.bubble_candidates();
  sim.escaped_droplet_candidates_total += sim.escaped_droplet_candidates_last;
  sim.escaped_bubble_candidates_total += sim.escaped_bubble_candidates_last;
}

void resetEscapedParticleBranching(SparseSim3DTP& sim) {
  sim.escaped_droplets = Particles3DTP();
  sim.escaped_bubbles = Particles3DTP();
  sim.escaped_droplet_ages.clear();
  sim.escaped_bubble_ages.clear();
  sim.escaped_droplets_added_last = 0;
  sim.escaped_bubbles_added_last = 0;
  sim.escaped_droplets_added_total = 0;
  sim.escaped_bubbles_added_total = 0;
  sim.escaped_droplet_volume_added_last = 0.0;
  sim.escaped_bubble_volume_added_last = 0.0;
  sim.escaped_droplet_volume_added_total = 0.0;
  sim.escaped_bubble_volume_added_total = 0.0;
  sim.secondary_lifecycle_stats_last = SecondaryParticleLifecycleStats3D();
  sim.secondary_droplets_advected_total = 0;
  sim.secondary_bubbles_advected_total = 0;
  sim.secondary_droplets_reabsorbed_total = 0;
  sim.secondary_bubbles_reabsorbed_total = 0;
  sim.secondary_droplets_expired_total = 0;
  sim.secondary_bubbles_expired_total = 0;
  sim.secondary_droplets_dragged_total = 0;
  sim.secondary_bubbles_dragged_total = 0;
  sim.secondary_droplets_reabsorbed_to_primary_total = 0;
  sim.secondary_bubbles_reabsorbed_to_primary_total = 0;
  sim.secondary_droplet_volume_current_last = 0.0;
  sim.secondary_bubble_volume_current_last = 0.0;
  sim.secondary_droplet_volume_reabsorbed_total = 0.0;
  sim.secondary_bubble_volume_reabsorbed_total = 0.0;
  sim.secondary_droplet_volume_expired_total = 0.0;
  sim.secondary_bubble_volume_expired_total = 0.0;
  sim.secondary_droplet_volume_reabsorbed_to_primary_total = 0.0;
  sim.secondary_bubble_volume_reabsorbed_to_primary_total = 0.0;
  sim.secondary_spray_emission_step_index = 0;
  sim.secondary_spray_emission_stats_last = SecondarySprayEmissionStats3D();
  sim.secondary_spray_effective_requested_last = 0;
  sim.secondary_spray_interface_gate_passed_last = 0;
  sim.secondary_spray_interface_cells_last = 0;
  sim.secondary_spray_candidates_last = 0;
  sim.secondary_spray_impact_candidates_last = 0;
  sim.secondary_spray_foam_ready_droplets_last = 0;
  sim.secondary_spray_emitted_droplets_last = 0;
  sim.secondary_spray_emitted_bubbles_last = 0;
  sim.secondary_spray_interface_grad_max_last = 0.0;
  sim.secondary_spray_interface_curvature_abs_max_last = 0.0;
  sim.secondary_spray_emitted_droplets_total = 0;
  sim.secondary_spray_emitted_bubbles_total = 0;
  sim.secondary_spray_emitted_droplet_volume_last = 0.0;
  sim.secondary_spray_emitted_bubble_volume_last = 0.0;
  sim.secondary_spray_emitted_droplet_volume_total = 0.0;
  sim.secondary_spray_emitted_bubble_volume_total = 0.0;
}

void updateSecondaryCurrentVolumes(SparseSim3DTP& sim) {
  sim.secondary_droplet_volume_current_last =
    secondaryVolumeSum3D(sim.escaped_droplets, sim.Vp);
  sim.secondary_bubble_volume_current_last =
    secondaryVolumeSum3D(sim.escaped_bubbles, sim.Vp);
}

void storeEscapedParticles(SparseSim3DTP& sim, const ParticleEscapeBuffer3D& buffer) {
  sim.escaped_droplets_added_last = 0;
  sim.escaped_bubbles_added_last = 0;
  sim.escaped_droplet_volume_added_last = 0.0;
  sim.escaped_bubble_volume_added_last = 0.0;
  if (!sim.escaped_particle_branching) {
    updateSecondaryCurrentVolumes(sim);
    return;
  }

  for (const EscapedParticleRecord3D& r : buffer.records) {
    if (r.type == 0) {
      sim.escaped_droplets.add(r.pos, r.vel, 0, r.volume);
      sim.escaped_droplet_ages.push_back(0);
      ++sim.escaped_droplets_added_last;
      sim.escaped_droplet_volume_added_last += r.volume * sim.Vp;
    } else if (r.type == 1) {
      sim.escaped_bubbles.add(r.pos, r.vel, 1, r.volume);
      sim.escaped_bubble_ages.push_back(0);
      ++sim.escaped_bubbles_added_last;
      sim.escaped_bubble_volume_added_last += r.volume * sim.Vp;
    }
  }
  sim.escaped_droplets_added_total += sim.escaped_droplets_added_last;
  sim.escaped_bubbles_added_total += sim.escaped_bubbles_added_last;
  sim.escaped_droplet_volume_added_total += sim.escaped_droplet_volume_added_last;
  sim.escaped_bubble_volume_added_total += sim.escaped_bubble_volume_added_last;
  updateSecondaryCurrentVolumes(sim);
}

void appendSecondaryToPrimary(Particles3DTP& primary, const Particles3DTP& secondary) {
  for (size_t i = 0; i < secondary.size(); ++i) {
    primary.add(secondary.pos[i], secondary.vel[i], secondary.type[i], secondary.volume[i]);
  }
}

void advanceSecondaryLifecycle(SparseSim3DTP& sim, double stepDt) {
  const SecondaryParticleDomain3D domain{
    sim.grid.nx, sim.grid.ny, sim.grid.nz, sim.grid.dx,
    sim.grid.ox, sim.grid.oy, sim.grid.oz};
  const SecondaryParticleLifecycleConfig3D config{
    sim.secondary_particle_lifecycle,
    sim.secondary_droplet_lifetime_steps,
    sim.secondary_bubble_lifetime_steps,
    sim.secondary_velocity_damping,
    sim.secondary_reabsorb_margin_cells,
    sim.gravity,
    sim.secondary_droplet_gravity_scale,
    sim.secondary_bubble_buoyancy_scale,
    sim.secondary_droplet_drag,
    sim.secondary_bubble_drag,
    sim.Vp};
  Particles3DTP reabsorbedDroplets;
  Particles3DTP reabsorbedBubbles;
  const SecondaryParticleLifecycleStats3D stats =
    advanceSecondaryParticles3D(sim.escaped_droplets,
                                sim.escaped_bubbles,
                                sim.escaped_droplet_ages,
                                sim.escaped_bubble_ages,
                                domain,
                                config,
                                stepDt,
                                sim.secondary_reabsorb_to_primary ? &reabsorbedDroplets : nullptr,
                                sim.secondary_reabsorb_to_primary ? &reabsorbedBubbles : nullptr);
  if (sim.secondary_reabsorb_to_primary) {
    appendSecondaryToPrimary(sim.particles, reabsorbedDroplets);
    appendSecondaryToPrimary(sim.particles, reabsorbedBubbles);
  }
  sim.secondary_lifecycle_stats_last = stats;
  sim.secondary_droplets_advected_total += stats.advected_droplets;
  sim.secondary_bubbles_advected_total += stats.advected_bubbles;
  sim.secondary_droplets_reabsorbed_total += stats.reabsorbed_droplets;
  sim.secondary_bubbles_reabsorbed_total += stats.reabsorbed_bubbles;
  sim.secondary_droplets_expired_total += stats.expired_droplets;
  sim.secondary_bubbles_expired_total += stats.expired_bubbles;
  sim.secondary_droplets_dragged_total += stats.dragged_droplets;
  sim.secondary_bubbles_dragged_total += stats.dragged_bubbles;
  sim.secondary_droplets_reabsorbed_to_primary_total += stats.reabsorbed_droplets_to_primary;
  sim.secondary_bubbles_reabsorbed_to_primary_total += stats.reabsorbed_bubbles_to_primary;
  sim.secondary_droplet_volume_current_last = stats.current_droplet_volume;
  sim.secondary_bubble_volume_current_last = stats.current_bubble_volume;
  sim.secondary_droplet_volume_reabsorbed_total += stats.reabsorbed_droplet_volume;
  sim.secondary_bubble_volume_reabsorbed_total += stats.reabsorbed_bubble_volume;
  sim.secondary_droplet_volume_expired_total += stats.expired_droplet_volume;
  sim.secondary_bubble_volume_expired_total += stats.expired_bubble_volume;
  sim.secondary_droplet_volume_reabsorbed_to_primary_total +=
    stats.reabsorbed_droplet_volume_to_primary;
  sim.secondary_bubble_volume_reabsorbed_to_primary_total +=
    stats.reabsorbed_bubble_volume_to_primary;
}

void emitSecondarySpray(SparseSim3DTP& sim) {
  const SecondarySprayEmissionConfig3D config{
    sim.secondary_spray_emission,
    sim.secondary_spray_particles_per_step,
    sim.secondary_spray_droplet_fraction,
    sim.secondary_spray_droplet_volume,
    sim.secondary_spray_bubble_volume,
    sim.Vp,
    sim.secondary_spray_interface_gate,
    sim.interface_diagnostics_last.interface_cells,
    sim.interface_diagnostics_last.grad_max,
    sim.interface_diagnostics_last.curvature_abs_max,
    sim.secondary_spray_min_interface_cells,
    sim.secondary_spray_min_interface_grad_max,
    sim.secondary_spray_min_interface_curvature_abs_max,
    sim.secondary_spray_impact_candidates,
    sim.secondary_spray_impact_region_fraction,
    sim.secondary_spray_impact_downward_speed_min,
    sim.secondary_spray_impact_foam_fraction};
  const SecondarySprayEmissionStats3D stats =
    emitSecondarySpraySeeds3D(sim.particles,
                              sim.escaped_droplets,
                              sim.escaped_bubbles,
                              sim.escaped_droplet_ages,
                              sim.escaped_bubble_ages,
                              config,
                              sim.secondary_spray_emission_step_index);
  ++sim.secondary_spray_emission_step_index;
  sim.secondary_spray_emission_stats_last = stats;
  sim.secondary_spray_effective_requested_last = stats.effective_requested_particles;
  sim.secondary_spray_interface_gate_passed_last = stats.interface_gate_passed;
  sim.secondary_spray_interface_cells_last = stats.interface_cells;
  sim.secondary_spray_candidates_last = stats.candidate_liquid_particles;
  sim.secondary_spray_impact_candidates_last = stats.impact_candidate_liquid_particles;
  sim.secondary_spray_foam_ready_droplets_last = stats.foam_ready_droplets;
  sim.secondary_spray_emitted_droplets_last = stats.emitted_droplets;
  sim.secondary_spray_emitted_bubbles_last = stats.emitted_bubbles;
  sim.secondary_spray_interface_grad_max_last = stats.interface_grad_max;
  sim.secondary_spray_interface_curvature_abs_max_last = stats.interface_curvature_abs_max;
  sim.secondary_spray_emitted_droplet_volume_last = stats.emitted_droplet_volume;
  sim.secondary_spray_emitted_bubble_volume_last = stats.emitted_bubble_volume;
  sim.secondary_spray_emitted_droplets_total += stats.emitted_droplets;
  sim.secondary_spray_emitted_bubbles_total += stats.emitted_bubbles;
  sim.secondary_spray_emitted_droplet_volume_total += stats.emitted_droplet_volume;
  sim.secondary_spray_emitted_bubble_volume_total += stats.emitted_bubble_volume;
  sim.escaped_droplets_added_last += stats.emitted_droplets;
  sim.escaped_bubbles_added_last += stats.emitted_bubbles;
  sim.escaped_droplet_volume_added_last += stats.emitted_droplet_volume;
  sim.escaped_bubble_volume_added_last += stats.emitted_bubble_volume;
  sim.escaped_droplets_added_total += stats.emitted_droplets;
  sim.escaped_bubbles_added_total += stats.emitted_bubbles;
  sim.escaped_droplet_volume_added_total += stats.emitted_droplet_volume;
  sim.escaped_bubble_volume_added_total += stats.emitted_bubble_volume;
  updateSecondaryCurrentVolumes(sim);
}

void resetTimestepStats(SparseSim3DTP& sim) {
  sim.effective_dt_last = sim.dt;
  sim.max_particle_speed_last = 0.0;
  sim.cfl_limit_dt_last = sim.dt;
  sim.adaptive_timestep_limited_last = 0;
}

void storeTimestepStats(SparseSim3DTP& sim, const TimestepStats3D& stats) {
  sim.effective_dt_last = stats.effective_dt;
  sim.max_particle_speed_last = stats.max_particle_speed;
  sim.cfl_limit_dt_last = stats.cfl_limit_dt;
  sim.adaptive_timestep_limited_last = stats.limited;
}

double liquidVolume(const Particles3DTP& particles, double Vp) {
  double volume = 0.0;
  for (size_t p = 0; p < particles.size(); ++p) {
    if (particles.type[p] == 0) volume += particles.volume[p] * Vp;
  }
  return volume;
}

void resetVolumeCorrectionStats(SparseSim3DTP& sim) {
  sim.liquid_volume_current_last = liquidVolume(sim.particles, sim.Vp);
  sim.liquid_volume_target = sim.liquid_volume_current_last;
  sim.liquid_volume_error_last = 0.0;
  sim.c_div_last = 0.0;
}

void updateVolumeCorrectionStats(SparseSim3DTP& sim, double stepDt) {
  sim.liquid_volume_current_last = liquidVolume(sim.particles, sim.Vp);
  sim.liquid_volume_error_last = sim.liquid_volume_target - sim.liquid_volume_current_last;
  sim.c_div_last = 0.0;
  if (sim.c_div_volume_correction &&
      sim.c_div_strength > 0.0 &&
      sim.liquid_volume_target > 0.0 &&
      stepDt > 0.0) {
    sim.c_div_last =
      sim.c_div_strength * sim.liquid_volume_error_last / (stepDt * sim.liquid_volume_target);
  }
}

void resetSceneState(SparseSim3DTP& sim) {
  sim.particles = Particles3DTP();
  sim.narrow_band_air_removed_last = 0;
  sim.narrow_band_air_removed_total = 0;
  sim.gas_particle_coarsening_removed_last = 0;
  sim.gas_particle_coarsening_removed_total = 0;
  sim.liquid_particle_coarsening_removed_last = 0;
  sim.liquid_particle_coarsening_removed_total = 0;
  sim.liquid_particle_refill_added_last = 0;
  sim.liquid_particle_refill_added_total = 0;
  resetParticleBoundaryStats(sim);
  resetEscapedParticleBranching(sim);
  resetTimestepStats(sim);
  sim.interface_diagnostics_last = InterfaceDiagnostics3D();
  sim.surface_tension_stats_last = SurfaceTensionStats3D();
  sim.phase.rho_tilde_0 = calibrateRhoTilde0(sim.phase, sim.Vp);
}

} // namespace

void SparseSim3DTP::initTwoPhaseDamBreak() {
  resetSceneState(*this);
  int wx = grid.nx * 4 / 10;
  int hy = grid.ny * 7 / 10;
  for (int k = 1; k < grid.nz - 1; ++k) {
    for (int j = 1; j < grid.ny - 1; ++j) {
      for (int i = 1; i < grid.nx - 1; ++i) {
        bool liquid = (i < wx && j < hy);
        seedCell(particles, i, j, k, grid.dx, liquid ? 0 : 1);
      }
    }
  }
  applyParticleAdaptivity();
  resetVolumeCorrectionStats(*this);
}

void SparseSim3DTP::initFallingWaterColumn() {
  resetSceneState(*this);
  const int x0 = std::max(1, grid.nx * 5 / 16);
  const int x1 = std::min(grid.nx - 1, std::max(x0 + 2, grid.nx * 11 / 16));
  const int y0 = std::max(1, grid.ny * 11 / 20);
  const int y1 = std::min(grid.ny - 1, std::max(y0 + 2, grid.ny * 17 / 20));
  const int z0 = std::max(1, grid.nz * 5 / 16);
  const int z1 = std::min(grid.nz - 1, std::max(z0 + 2, grid.nz * 11 / 16));
  const Vec3 initialFall{0.0, -8.0, 0.0};
  for (int k = 1; k < grid.nz - 1; ++k) {
    for (int j = 1; j < grid.ny - 1; ++j) {
      for (int i = 1; i < grid.nx - 1; ++i) {
        const bool liquid = (i >= x0 && i < x1 &&
                             j >= y0 && j < y1 &&
                             k >= z0 && k < z1);
        seedCell(particles, i, j, k, grid.dx, liquid ? 0 : 1,
                 liquid ? initialFall : Vec3{0.0, 0.0, 0.0});
      }
    }
  }
  applyParticleAdaptivity();
  resetVolumeCorrectionStats(*this);
}

void SparseSim3DTP::initLargeWaterEvent() {
  resetSceneState(*this);
  const int sheetX0 = std::max(1, grid.nx / 8);
  const int sheetX1 = std::min(grid.nx - 1, std::max(sheetX0 + 3, grid.nx * 7 / 8));
  const int sheetY0 = std::max(2, grid.ny * 8 / 20);
  const int sheetY1 = std::min(grid.ny - 1, std::max(sheetY0 + 3, grid.ny * 15 / 20));
  const int sheetZ0 = std::max(1, grid.nz * 3 / 10);
  const int sheetZ1 = std::min(grid.nz - 1, std::max(sheetZ0 + 2, grid.nz * 7 / 10));
  const int poolX0 = std::max(1, grid.nx / 7);
  const int poolX1 = std::min(grid.nx - 1, std::max(poolX0 + 4, grid.nx * 6 / 7));
  const int poolY1 = std::min(grid.ny - 1, std::max(3, grid.ny / 6));
  const int poolZ0 = std::max(1, grid.nz / 6);
  const int poolZ1 = std::min(grid.nz - 1, std::max(poolZ0 + 4, grid.nz * 5 / 6));
  const double cx = 0.5 * static_cast<double>(sheetX0 + sheetX1);
  const double cz = 0.5 * static_cast<double>(sheetZ0 + sheetZ1);
  for (int k = 1; k < grid.nz - 1; ++k) {
    for (int j = 1; j < grid.ny - 1; ++j) {
      for (int i = 1; i < grid.nx - 1; ++i) {
        const bool fallingSheet =
          i >= sheetX0 && i < sheetX1 &&
          j >= sheetY0 && j < sheetY1 &&
          k >= sheetZ0 && k < sheetZ1;
        const bool impactPool =
          i >= poolX0 && i < poolX1 &&
          j < poolY1 &&
          k >= poolZ0 && k < poolZ1;
        const bool liquid = fallingSheet || impactPool;
        Vec3 velocity{0.0, 0.0, 0.0};
        if (fallingSheet) {
          velocity = {
            0.12 * ((static_cast<double>(i) + 0.5) - cx),
            -13.5,
            0.07 * ((static_cast<double>(k) + 0.5) - cz)
          };
        }
        seedCell(particles, i, j, k, grid.dx, liquid ? 0 : 1, velocity);
      }
    }
  }
  applyParticleAdaptivity();
  resetVolumeCorrectionStats(*this);
}

void SparseSim3DTP::initRayleighTaylor() {
  resetSceneState(*this);
  int mid = grid.ny / 2;
  constexpr double pi = 3.14159265358979323846;
  for (int k = 1; k < grid.nz - 1; ++k) {
    for (int j = 1; j < grid.ny - 1; ++j) {
      for (int i = 1; i < grid.nx - 1; ++i) {
        double pert = std::cos(2.0 * pi * i / grid.nx) * std::cos(2.0 * pi * k / grid.nz);
        bool heavy = (double)j > (mid + pert);
        seedCell(particles, i, j, k, grid.dx, heavy ? 0 : 1);
      }
    }
  }
  applyParticleAdaptivity();
  resetVolumeCorrectionStats(*this);
}

void SparseSim3DTP::initBubbleTank() {
  resetSceneState(*this);
  int waterLevel = grid.ny / 2;
  double cx = grid.nx * 0.5;
  double cy = waterLevel * 0.375;
  double cz = grid.nz * 0.5;
  double r = std::max(1.25, std::min(grid.nx, grid.nz) * 0.1875);
  for (int k = 1; k < grid.nz - 1; ++k) {
    for (int j = 1; j < waterLevel; ++j) {
      for (int i = 1; i < grid.nx - 1; ++i) {
        double dx = (i + 0.5) - cx;
        double dy = (j + 0.5) - cy;
        double dz = (k + 0.5) - cz;
        bool gas = dx * dx + dy * dy + dz * dz < r * r;
        seedCell(particles, i, j, k, grid.dx, gas ? 1 : 0);
      }
    }
  }
  applyParticleAdaptivity();
  resetVolumeCorrectionStats(*this);
}

void SparseSim3DTP::applyNarrowBandAir() {
  const pa3d::ParticleCellDomain3D domain{grid.nx, grid.ny, grid.nz, grid.dx,
                                          grid.ox, grid.oy, grid.oz};
  const pa3d::NarrowBandAirResult3D result =
    pa3d::applyNarrowBandAir(particles, domain, narrow_band_air, narrow_band_air_radius);
  narrow_band_air_removed_last = result.removed;
  narrow_band_air_liquid_cells_last = result.liquidCells;
  narrow_band_air_gas_particles_before_last = result.gasBefore;
  narrow_band_air_gas_particles_after_last = result.gasAfter;
  narrow_band_air_removed_total += narrow_band_air_removed_last;
}

void SparseSim3DTP::applyGasParticleCoarsening() {
  const pa3d::ParticleCellDomain3D domain{grid.nx, grid.ny, grid.nz, grid.dx,
                                          grid.ox, grid.oy, grid.oz};
  const pa3d::GasParticleCoarseningResult3D result =
    pa3d::applyGasParticleCoarsening(particles,
                                     domain,
                                     gas_particle_coarsening,
                                     gas_particles_per_cell_target,
                                     gas_particle_coarsening_seed);
  gas_particle_coarsening_removed_last = result.removed;
  gas_particle_coarsening_cells_last = result.cells;
  gas_particle_coarsening_overfull_cells_last = result.overfullCells;
  gas_particle_coarsening_before_last = result.particlesBefore;
  gas_particle_coarsening_after_last = result.particlesAfter;
  gas_particle_coarsening_removed_total += gas_particle_coarsening_removed_last;
}

void SparseSim3DTP::applyLiquidParticleCoarsening() {
  const pa3d::ParticleCellDomain3D domain{grid.nx, grid.ny, grid.nz, grid.dx,
                                          grid.ox, grid.oy, grid.oz};
  const pa3d::GasParticleCoarseningResult3D result =
    pa3d::applyTypedParticleCoarsening(particles,
                                       domain,
                                       liquid_particle_coarsening,
                                       0,
                                       liquid_particles_per_cell_target,
                                       liquid_particle_coarsening_seed);
  liquid_particle_coarsening_removed_last = result.removed;
  liquid_particle_coarsening_cells_last = result.cells;
  liquid_particle_coarsening_overfull_cells_last = result.overfullCells;
  liquid_particle_coarsening_before_last = result.particlesBefore;
  liquid_particle_coarsening_after_last = result.particlesAfter;
  liquid_particle_coarsening_removed_total += liquid_particle_coarsening_removed_last;
}

void SparseSim3DTP::applyLiquidParticleRefill() {
  const pa3d::ParticleCellDomain3D domain{grid.nx, grid.ny, grid.nz, grid.dx,
                                          grid.ox, grid.oy, grid.oz};
  const pa3d::LiquidParticleRefillResult3D result =
    pa3d::applyLiquidParticleRefill(particles,
                                    domain,
                                    liquid_particle_refill,
                                    liquid_refill_particles_per_cell_target,
                                    liquid_particle_refill_seed,
                                    liquid_particle_refill_interface_only,
                                    liquid_particle_refill_interface_radius,
                                    liquid_particle_refill_max_added_per_step);
  liquid_particle_refill_added_last = result.added;
  liquid_particle_refill_cells_last = result.cells;
  liquid_particle_refill_interface_cells_last = result.interfaceCells;
  liquid_particle_refill_underfull_cells_last = result.underfullCells;
  liquid_particle_refill_budget_limited_last = result.budgetLimited;
  liquid_particle_refill_before_last = result.particlesBefore;
  liquid_particle_refill_after_last = result.particlesAfter;
  liquid_particle_refill_added_total += liquid_particle_refill_added_last;
}

void SparseSim3DTP::applyParticleAdaptivity() {
  applyNarrowBandAir();
  applyGasParticleCoarsening();
  applyLiquidParticleCoarsening();
  applyLiquidParticleRefill();
}

void SparseSim3DTP::step() {
  applyParticleAdaptivity();
  const TimestepStats3D timestep =
    computeAdaptiveParticleTimestep3D(particles, grid.dx, dt,
                                      adaptive_timestep, adaptive_cfl, adaptive_min_dt);
  storeTimestepStats(*this, timestep);
  const double stepDt = timestep.effective_dt;
  advanceSecondaryLifecycle(*this, stepDt);
  updateVolumeCorrectionStats(*this, stepDt);
  markCells(grid, particles);
  spP2G3D_tp(grid, particles, phase, Vp);
  interface_diagnostics_last = diagnoseSparseInterface3D(grid, phase);
  SparseMacGrid3D<4> saved = grid;
  applyGravity(grid, stepDt, gravity);
  surface_tension_stats_last = surface_tension
    ? applySparseSurfaceTension3D(grid, phase, stepDt,
                                  surface_tension_strength,
                                  surface_tension_max_delta_speed,
                                  surface_tension_curvature_smoothing_radius)
    : SurfaceTensionStats3D();
  applyWallBoundary(grid);
  spProjectStepVC3D(grid, phase, stepDt, cg_iters, cg_tol, c_div_last);
  spG2P3D_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  ParticleEscapeStats3D escapeStats;
  ParticleEscapeBuffer3D escapeBuffer;
  spAdvect3D_tp(particles, grid, stepDt, &escapeStats, advection_order,
                escaped_particle_branching ? &escapeBuffer : nullptr);
  storeParticleBoundaryStats(*this, escapeStats);
  storeEscapedParticles(*this, escapeBuffer);
  emitSecondarySpray(*this);
}
