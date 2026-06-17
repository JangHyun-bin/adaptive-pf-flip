#include "driver/sparse_sim3d_tp.h"
#include "physics_preset3d.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace {

int argInt(int argc, char** argv, const char* key, int fallback) {
  for (int i = 1; i + 1 < argc; ++i) {
    if (std::strcmp(argv[i], key) == 0) return std::atoi(argv[i + 1]);
  }
  return fallback;
}

unsigned int argUInt(int argc, char** argv, const char* key, unsigned int fallback) {
  for (int i = 1; i + 1 < argc; ++i) {
    if (std::strcmp(argv[i], key) == 0) {
      return static_cast<unsigned int>(std::strtoul(argv[i + 1], nullptr, 10));
    }
  }
  return fallback;
}

double argDouble(int argc, char** argv, const char* key, double fallback) {
  for (int i = 1; i + 1 < argc; ++i) {
    if (std::strcmp(argv[i], key) == 0) return std::atof(argv[i + 1]);
  }
  return fallback;
}

bool hasFlag(int argc, char** argv, const char* key) {
  for (int i = 1; i < argc; ++i) {
    if (std::strcmp(argv[i], key) == 0) return true;
  }
  return false;
}

const char* argString(int argc, char** argv, const char* key, const char* fallback) {
  for (int i = 1; i + 1 < argc; ++i) {
    if (std::strcmp(argv[i], key) == 0) return argv[i + 1];
  }
  return fallback;
}

double meanY(const Particles3DTP& ps, unsigned char type) {
  double sum = 0.0;
  int count = 0;
  for (size_t i = 0; i < ps.size(); ++i) {
    if (ps.type[i] == type) {
      sum += ps.pos[i].y;
      ++count;
    }
  }
  return count ? sum / count : 0.0;
}

size_t countType(const Particles3DTP& ps, unsigned char type) {
  size_t count = 0;
  for (size_t i = 0; i < ps.size(); ++i) {
    if (ps.type[i] == type) ++count;
  }
  return count;
}

double volumeType(const Particles3DTP& ps, unsigned char type, double Vp) {
  double volume = 0.0;
  for (size_t i = 0; i < ps.size(); ++i) {
    if (ps.type[i] == type) volume += ps.volume[i] * Vp;
  }
  return volume;
}

bool finiteParticles(const Particles3DTP& ps) {
  for (size_t i = 0; i < ps.size(); ++i) {
    if (!std::isfinite(ps.pos[i].x) || !std::isfinite(ps.pos[i].y) || !std::isfinite(ps.pos[i].z)) {
      return false;
    }
  }
  return true;
}

void usage() {
  std::fprintf(stderr,
               "usage: validate_sparse3d_tp [--scenario rt|bubble] [--nx N] [--ny N] [--nz N] "
               "[--steps N] [--dt DT] [--cg-iters N] "
               "[--physics-preset] [--long-physics-preset] "
               "[--adaptive-timestep] [--adaptive-cfl C] [--adaptive-min-dt DT] "
               "[--advection-order 2|3] "
               "[--c-div-volume-correction] [--c-div-strength S] [--liquid-volume-target V] "
               "[--surface-tension] [--surface-tension-strength S] "
               "[--surface-tension-max-delta-speed V] "
               "[--surface-tension-curvature-smoothing-radius N] "
               "[--escaped-particle-branching] "
               "[--secondary-lifecycle] [--secondary-droplet-lifetime N] "
               "[--secondary-bubble-lifetime N] [--secondary-velocity-damping D] "
               "[--secondary-reabsorb-margin C] [--secondary-bubble-buoyancy-scale S] "
               "[--narrow-band-air] [--narrow-band-radius N] "
               "[--gas-coarsening] [--gas-particles-per-cell N] "
               "[--gas-coarsening-seed N] "
               "[--liquid-coarsening] [--liquid-particles-per-cell N] "
               "[--liquid-coarsening-seed N] "
               "[--liquid-refill] [--liquid-refill-particles-per-cell N] "
               "[--liquid-refill-seed N] "
               "[--liquid-refill-max-added-per-step N] "
               "[--liquid-refill-interface-only] [--liquid-refill-interface-radius N]\n");
}

} // namespace

int main(int argc, char** argv) {
  const bool physicsPreset = hasFlag(argc, argv, "--physics-preset") ||
                             hasFlag(argc, argv, "--long-physics-preset");
  const bool longPhysicsPreset = hasFlag(argc, argv, "--long-physics-preset");
  const char* scenario =
    argString(argc, argv, "--scenario", physicsPreset ? "bubble" : "rt");
  int nx = argInt(argc, argv, "--nx", 12);
  int ny = argInt(argc, argv, "--ny", 18);
  int nz = argInt(argc, argv, "--nz", 12);
  const int defaultSteps = longPhysicsPreset
    ? kLongPhysicsPresetSteps3D
    : (physicsPreset ? kPhysicsPresetSteps3D : 40);
  int steps = argInt(argc, argv, "--steps", defaultSteps);

  if (nx < 4 || ny < 4 || nz < 4 || steps < 0) {
    usage();
    return 2;
  }
  if (std::strcmp(scenario, "rt") != 0 && std::strcmp(scenario, "bubble") != 0) {
    usage();
    return 2;
  }

  SparseSim3DTP sim(nx, ny, nz, 1.0);
  if (physicsPreset) {
    applyFullPhysicsPreset3D(sim);
  }
  sim.dt = argDouble(argc, argv, "--dt", sim.dt);
  sim.cg_iters = argInt(argc, argv, "--cg-iters", sim.cg_iters);
  sim.adaptive_timestep = sim.adaptive_timestep ||
                          hasFlag(argc, argv, "--adaptive-timestep");
  sim.adaptive_cfl = argDouble(argc, argv, "--adaptive-cfl", sim.adaptive_cfl);
  sim.adaptive_min_dt = argDouble(argc, argv, "--adaptive-min-dt", sim.adaptive_min_dt);
  sim.advection_order = argInt(argc, argv, "--advection-order", sim.advection_order);
  sim.c_div_volume_correction = sim.c_div_volume_correction ||
                                hasFlag(argc, argv, "--c-div-volume-correction");
  sim.c_div_strength = argDouble(argc, argv, "--c-div-strength", sim.c_div_strength);
  sim.surface_tension = sim.surface_tension ||
                        hasFlag(argc, argv, "--surface-tension");
  sim.surface_tension_strength =
    argDouble(argc, argv, "--surface-tension-strength", sim.surface_tension_strength);
  sim.surface_tension_max_delta_speed =
    argDouble(argc, argv, "--surface-tension-max-delta-speed",
              sim.surface_tension_max_delta_speed);
  sim.surface_tension_curvature_smoothing_radius =
    argInt(argc, argv, "--surface-tension-curvature-smoothing-radius",
           sim.surface_tension_curvature_smoothing_radius);
  sim.escaped_particle_branching = sim.escaped_particle_branching ||
                                   hasFlag(argc, argv, "--escaped-particle-branching");
  sim.secondary_particle_lifecycle = sim.secondary_particle_lifecycle ||
                                     hasFlag(argc, argv, "--secondary-lifecycle");
  if (sim.secondary_particle_lifecycle) {
    sim.escaped_particle_branching = true;
  }
  sim.secondary_droplet_lifetime_steps =
    argInt(argc, argv, "--secondary-droplet-lifetime",
           sim.secondary_droplet_lifetime_steps);
  sim.secondary_bubble_lifetime_steps =
    argInt(argc, argv, "--secondary-bubble-lifetime",
           sim.secondary_bubble_lifetime_steps);
  sim.secondary_velocity_damping =
    argDouble(argc, argv, "--secondary-velocity-damping",
              sim.secondary_velocity_damping);
  sim.secondary_reabsorb_margin_cells =
    argDouble(argc, argv, "--secondary-reabsorb-margin",
              sim.secondary_reabsorb_margin_cells);
  sim.secondary_bubble_buoyancy_scale =
    argDouble(argc, argv, "--secondary-bubble-buoyancy-scale",
              sim.secondary_bubble_buoyancy_scale);
  const double liquidVolumeTargetOverride =
    argDouble(argc, argv, "--liquid-volume-target", -0.25);
  sim.narrow_band_air = sim.narrow_band_air ||
                        hasFlag(argc, argv, "--narrow-band-air");
  sim.narrow_band_air_radius =
    argInt(argc, argv, "--narrow-band-radius", sim.narrow_band_air_radius);
  sim.gas_particle_coarsening = sim.gas_particle_coarsening ||
                                hasFlag(argc, argv, "--gas-coarsening");
  sim.gas_particles_per_cell_target =
    argInt(argc, argv, "--gas-particles-per-cell", sim.gas_particles_per_cell_target);
  sim.gas_particle_coarsening_seed =
    argUInt(argc, argv, "--gas-coarsening-seed", sim.gas_particle_coarsening_seed);
  sim.liquid_particle_coarsening = sim.liquid_particle_coarsening ||
                                   hasFlag(argc, argv, "--liquid-coarsening");
  sim.liquid_particles_per_cell_target =
    argInt(argc, argv, "--liquid-particles-per-cell", sim.liquid_particles_per_cell_target);
  sim.liquid_particle_coarsening_seed =
    argUInt(argc, argv, "--liquid-coarsening-seed", sim.liquid_particle_coarsening_seed);
  sim.liquid_particle_refill = sim.liquid_particle_refill ||
                               hasFlag(argc, argv, "--liquid-refill");
  sim.liquid_refill_particles_per_cell_target =
    argInt(argc, argv, "--liquid-refill-particles-per-cell",
           sim.liquid_refill_particles_per_cell_target);
  sim.liquid_particle_refill_seed =
    argUInt(argc, argv, "--liquid-refill-seed", sim.liquid_particle_refill_seed);
  sim.liquid_particle_refill_max_added_per_step =
    argInt(argc, argv, "--liquid-refill-max-added-per-step",
           sim.liquid_particle_refill_max_added_per_step);
  sim.liquid_particle_refill_interface_only =
    sim.liquid_particle_refill_interface_only ||
    hasFlag(argc, argv, "--liquid-refill-interface-only");
  sim.liquid_particle_refill_interface_radius =
    argInt(argc, argv, "--liquid-refill-interface-radius",
           sim.liquid_particle_refill_interface_radius);
  if (sim.narrow_band_air_radius < 0 ||
      sim.gas_particles_per_cell_target <= 0 ||
      sim.liquid_particles_per_cell_target <= 0 ||
      sim.liquid_refill_particles_per_cell_target <= 0 ||
      sim.liquid_particle_refill_max_added_per_step < 0 ||
      sim.liquid_particle_refill_interface_radius < 0 ||
      sim.adaptive_cfl <= 0.0 ||
      sim.adaptive_min_dt < 0.0 ||
      (sim.advection_order != 2 && sim.advection_order != 3) ||
      sim.c_div_strength < 0.0 ||
      sim.surface_tension_strength < 0.0 ||
      sim.surface_tension_max_delta_speed < 0.0 ||
      sim.surface_tension_curvature_smoothing_radius < 0 ||
      sim.surface_tension_curvature_smoothing_radius > 3 ||
      sim.secondary_droplet_lifetime_steps < 0 ||
      sim.secondary_bubble_lifetime_steps < 0 ||
      sim.secondary_velocity_damping < 0.0 ||
      sim.secondary_velocity_damping > 1.0 ||
      sim.secondary_reabsorb_margin_cells < 0.0 ||
      sim.secondary_bubble_buoyancy_scale < 0.0 ||
      liquidVolumeTargetOverride < -0.5) {
    usage();
    return 2;
  }

  if (std::strcmp(scenario, "rt") == 0) {
    sim.initRayleighTaylor();
  } else {
    sim.initBubbleTank();
  }
  if (liquidVolumeTargetOverride >= 0.0) {
    sim.liquid_volume_target = liquidVolumeTargetOverride;
  }

  size_t n0 = sim.particles.size();
  size_t liquidCount0 = countType(sim.particles, 0);
  size_t gasCount0 = countType(sim.particles, 1);
  double liquidVolume0 = volumeType(sim.particles, 0, sim.Vp);
  double gasVolume0 = volumeType(sim.particles, 1, sim.Vp);
  int liquidCoarseningRemoved0 = sim.liquid_particle_coarsening_removed_total;
  int liquidRefillAdded0 = sim.liquid_particle_refill_added_total;
  double heavy0 = meanY(sim.particles, 0);
  double gas0 = meanY(sim.particles, 1);
  size_t maxActive = 0;

  auto start = std::chrono::steady_clock::now();
  for (int s = 0; s < steps; ++s) {
    sim.step();
    maxActive = std::max(maxActive, sim.grid.activeCellBlocks());
  }
  auto end = std::chrono::steady_clock::now();

  double heavy1 = meanY(sim.particles, 0);
  double gas1 = meanY(sim.particles, 1);
  size_t liquidCount1 = countType(sim.particles, 0);
  size_t gasCount1 = countType(sim.particles, 1);
  double liquidVolume1 = volumeType(sim.particles, 0, sim.Vp);
  double gasVolume1 = volumeType(sim.particles, 1, sim.Vp);
  int liquidCoarseningRemovedDuringRun =
    sim.liquid_particle_coarsening_removed_total - liquidCoarseningRemoved0;
  int liquidRefillAddedDuringRun =
    sim.liquid_particle_refill_added_total - liquidRefillAdded0;
  bool finite = finiteParticles(sim.particles);
  size_t totalBlocks = sim.grid.totalCellBlocks();
  long long elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

  std::printf("scenario=%s\n", scenario);
  std::printf("physics_preset=%s\n", physicsPreset ? "true" : "false");
  std::printf("long_physics_preset=%s\n", longPhysicsPreset ? "true" : "false");
  std::printf("dims=%d,%d,%d\n", nx, ny, nz);
  std::printf("steps=%d\n", steps);
  std::printf("dt=%.9g\n", sim.dt);
  std::printf("cg_iters=%d\n", sim.cg_iters);
  std::printf("adaptive_timestep=%s\n", sim.adaptive_timestep ? "true" : "false");
  std::printf("adaptive_cfl=%.9g\n", sim.adaptive_cfl);
  std::printf("adaptive_min_dt=%.9g\n", sim.adaptive_min_dt);
  std::printf("advection_order=%d\n", sim.advection_order);
  std::printf("c_div_volume_correction=%s\n",
              sim.c_div_volume_correction ? "true" : "false");
  std::printf("c_div_strength=%.9g\n", sim.c_div_strength);
  std::printf("surface_tension=%s\n", sim.surface_tension ? "true" : "false");
  std::printf("surface_tension_strength=%.9g\n", sim.surface_tension_strength);
  std::printf("surface_tension_max_delta_speed=%.9g\n",
              sim.surface_tension_max_delta_speed);
  std::printf("surface_tension_curvature_smoothing_radius=%d\n",
              sim.surface_tension_curvature_smoothing_radius);
  std::printf("escaped_particle_branching=%s\n",
              sim.escaped_particle_branching ? "true" : "false");
  std::printf("secondary_particle_lifecycle=%s\n",
              sim.secondary_particle_lifecycle ? "true" : "false");
  std::printf("secondary_droplet_lifetime_steps=%d\n",
              sim.secondary_droplet_lifetime_steps);
  std::printf("secondary_bubble_lifetime_steps=%d\n",
              sim.secondary_bubble_lifetime_steps);
  std::printf("secondary_velocity_damping=%.9g\n",
              sim.secondary_velocity_damping);
  std::printf("secondary_reabsorb_margin_cells=%.9g\n",
              sim.secondary_reabsorb_margin_cells);
  std::printf("secondary_bubble_buoyancy_scale=%.9g\n",
              sim.secondary_bubble_buoyancy_scale);
  std::printf("liquid_volume_target=%.9g\n", sim.liquid_volume_target);
  std::printf("liquid_volume_current_last=%.9g\n", sim.liquid_volume_current_last);
  std::printf("liquid_volume_error_last=%.9g\n", sim.liquid_volume_error_last);
  std::printf("c_div_last=%.9g\n", sim.c_div_last);
  std::printf("interface_sample_cells=%d\n",
              sim.interface_diagnostics_last.sample_cells);
  std::printf("interface_cells=%d\n",
              sim.interface_diagnostics_last.interface_cells);
  std::printf("interface_phi_min=%.9g\n",
              sim.interface_diagnostics_last.phi_min);
  std::printf("interface_phi_max=%.9g\n",
              sim.interface_diagnostics_last.phi_max);
  std::printf("interface_phi_mean=%.9g\n",
              sim.interface_diagnostics_last.phi_mean);
  std::printf("interface_grad_mean=%.9g\n",
              sim.interface_diagnostics_last.grad_mean);
  std::printf("interface_grad_max=%.9g\n",
              sim.interface_diagnostics_last.grad_max);
  std::printf("interface_curvature_abs_mean=%.9g\n",
              sim.interface_diagnostics_last.curvature_abs_mean);
  std::printf("interface_curvature_abs_max=%.9g\n",
              sim.interface_diagnostics_last.curvature_abs_max);
  std::printf("interface_diagnostics_finite=%s\n",
              sim.interface_diagnostics_last.finite ? "true" : "false");
  std::printf("surface_tension_candidate=%s\n",
              sim.interface_diagnostics_last.surface_tension_candidate ? "true" : "false");
  std::printf("surface_tension_enabled=%s\n",
              sim.surface_tension_stats_last.enabled ? "true" : "false");
  std::printf("surface_tension_applied_cells=%d\n",
              sim.surface_tension_stats_last.applied_cells);
  std::printf("surface_tension_force_finite=%s\n",
              sim.surface_tension_stats_last.finite ? "true" : "false");
  std::printf("surface_tension_mean_delta_speed=%.9g\n",
              sim.surface_tension_stats_last.mean_delta_speed);
  std::printf("surface_tension_max_delta_speed_last=%.9g\n",
              sim.surface_tension_stats_last.max_delta_speed);
  std::printf("surface_tension_curvature_smoothing_radius_last=%d\n",
              sim.surface_tension_stats_last.curvature_smoothing_radius);
  std::printf("surface_tension_raw_curvature_abs_mean=%.9g\n",
              sim.surface_tension_stats_last.raw_curvature_abs_mean);
  std::printf("surface_tension_raw_curvature_abs_max=%.9g\n",
              sim.surface_tension_stats_last.raw_curvature_abs_max);
  std::printf("surface_tension_smoothed_curvature_abs_mean=%.9g\n",
              sim.surface_tension_stats_last.smoothed_curvature_abs_mean);
  std::printf("surface_tension_smoothed_curvature_abs_max=%.9g\n",
              sim.surface_tension_stats_last.smoothed_curvature_abs_max);
  std::printf("surface_tension_capillary_dt_limit=%.9g\n",
              sim.surface_tension_stats_last.capillary_dt_limit);
  std::printf("surface_tension_capillary_stable=%s\n",
              sim.surface_tension_stats_last.capillary_stable ? "true" : "false");
  std::printf("effective_dt_last=%.9g\n", sim.effective_dt_last);
  std::printf("cfl_limit_dt_last=%.9g\n", sim.cfl_limit_dt_last);
  std::printf("max_particle_speed_last=%.9g\n", sim.max_particle_speed_last);
  std::printf("adaptive_timestep_limited_last=%d\n", sim.adaptive_timestep_limited_last);
  std::printf("narrow_band_air=%s\n", sim.narrow_band_air ? "true" : "false");
  std::printf("narrow_band_radius=%d\n", sim.narrow_band_air_radius);
  std::printf("gas_particle_coarsening=%s\n",
              sim.gas_particle_coarsening ? "true" : "false");
  std::printf("gas_particles_per_cell_target=%d\n",
              sim.gas_particles_per_cell_target);
  std::printf("gas_particle_coarsening_seed=%u\n",
              sim.gas_particle_coarsening_seed);
  std::printf("liquid_particle_coarsening=%s\n",
              sim.liquid_particle_coarsening ? "true" : "false");
  std::printf("liquid_particles_per_cell_target=%d\n",
              sim.liquid_particles_per_cell_target);
  std::printf("liquid_particle_coarsening_seed=%u\n",
              sim.liquid_particle_coarsening_seed);
  std::printf("liquid_particle_refill=%s\n",
              sim.liquid_particle_refill ? "true" : "false");
  std::printf("liquid_refill_particles_per_cell_target=%d\n",
              sim.liquid_refill_particles_per_cell_target);
  std::printf("liquid_particle_refill_seed=%u\n",
              sim.liquid_particle_refill_seed);
  std::printf("liquid_particle_refill_max_added_per_step=%d\n",
              sim.liquid_particle_refill_max_added_per_step);
  std::printf("liquid_particle_refill_interface_only=%s\n",
              sim.liquid_particle_refill_interface_only ? "true" : "false");
  std::printf("liquid_particle_refill_interface_radius=%d\n",
              sim.liquid_particle_refill_interface_radius);
  std::printf("particles_start=%zu\n", n0);
  std::printf("particles_end=%zu\n", sim.particles.size());
  std::printf("liquid_particles_start=%zu\n", liquidCount0);
  std::printf("liquid_particles_end=%zu\n", liquidCount1);
  std::printf("gas_particles_start=%zu\n", gasCount0);
  std::printf("gas_particles_end=%zu\n", gasCount1);
  std::printf("particle_boundary_clamped_liquid_last=%d\n",
              sim.particle_boundary_clamped_liquid_last);
  std::printf("particle_boundary_clamped_gas_last=%d\n",
              sim.particle_boundary_clamped_gas_last);
  std::printf("particle_boundary_clamped_liquid_total=%d\n",
              sim.particle_boundary_clamped_liquid_total);
  std::printf("particle_boundary_clamped_gas_total=%d\n",
              sim.particle_boundary_clamped_gas_total);
  std::printf("escaped_droplet_candidates_last=%d\n",
              sim.escaped_droplet_candidates_last);
  std::printf("escaped_bubble_candidates_last=%d\n",
              sim.escaped_bubble_candidates_last);
  std::printf("escaped_droplet_candidates_total=%d\n",
              sim.escaped_droplet_candidates_total);
  std::printf("escaped_bubble_candidates_total=%d\n",
              sim.escaped_bubble_candidates_total);
  std::printf("escaped_droplets_added_last=%d\n",
              sim.escaped_droplets_added_last);
  std::printf("escaped_bubbles_added_last=%d\n",
              sim.escaped_bubbles_added_last);
  std::printf("escaped_droplets_added_total=%d\n",
              sim.escaped_droplets_added_total);
  std::printf("escaped_bubbles_added_total=%d\n",
              sim.escaped_bubbles_added_total);
  std::printf("escaped_droplet_particles=%zu\n", sim.escaped_droplets.size());
  std::printf("escaped_bubble_particles=%zu\n", sim.escaped_bubbles.size());
  std::printf("escaped_droplet_ages=%zu\n", sim.escaped_droplet_ages.size());
  std::printf("escaped_bubble_ages=%zu\n", sim.escaped_bubble_ages.size());
  std::printf("escaped_droplet_volume_added_last=%.9g\n",
              sim.escaped_droplet_volume_added_last);
  std::printf("escaped_bubble_volume_added_last=%.9g\n",
              sim.escaped_bubble_volume_added_last);
  std::printf("escaped_droplet_volume_added_total=%.9g\n",
              sim.escaped_droplet_volume_added_total);
  std::printf("escaped_bubble_volume_added_total=%.9g\n",
              sim.escaped_bubble_volume_added_total);
  std::printf("secondary_lifecycle_enabled=%s\n",
              sim.secondary_lifecycle_stats_last.enabled ? "true" : "false");
  std::printf("secondary_lifecycle_finite=%s\n",
              sim.secondary_lifecycle_stats_last.finite ? "true" : "false");
  std::printf("secondary_droplets_advected_last=%d\n",
              sim.secondary_lifecycle_stats_last.advected_droplets);
  std::printf("secondary_bubbles_advected_last=%d\n",
              sim.secondary_lifecycle_stats_last.advected_bubbles);
  std::printf("secondary_droplets_advected_total=%d\n",
              sim.secondary_droplets_advected_total);
  std::printf("secondary_bubbles_advected_total=%d\n",
              sim.secondary_bubbles_advected_total);
  std::printf("secondary_droplets_reabsorbed_last=%d\n",
              sim.secondary_lifecycle_stats_last.reabsorbed_droplets);
  std::printf("secondary_bubbles_reabsorbed_last=%d\n",
              sim.secondary_lifecycle_stats_last.reabsorbed_bubbles);
  std::printf("secondary_droplets_reabsorbed_total=%d\n",
              sim.secondary_droplets_reabsorbed_total);
  std::printf("secondary_bubbles_reabsorbed_total=%d\n",
              sim.secondary_bubbles_reabsorbed_total);
  std::printf("secondary_droplets_expired_last=%d\n",
              sim.secondary_lifecycle_stats_last.expired_droplets);
  std::printf("secondary_bubbles_expired_last=%d\n",
              sim.secondary_lifecycle_stats_last.expired_bubbles);
  std::printf("secondary_droplets_expired_total=%d\n",
              sim.secondary_droplets_expired_total);
  std::printf("secondary_bubbles_expired_total=%d\n",
              sim.secondary_bubbles_expired_total);
  std::printf("secondary_droplet_volume_current=%.9g\n",
              sim.secondary_droplet_volume_current_last);
  std::printf("secondary_bubble_volume_current=%.9g\n",
              sim.secondary_bubble_volume_current_last);
  std::printf("secondary_droplet_volume_reabsorbed_total=%.9g\n",
              sim.secondary_droplet_volume_reabsorbed_total);
  std::printf("secondary_bubble_volume_reabsorbed_total=%.9g\n",
              sim.secondary_bubble_volume_reabsorbed_total);
  std::printf("secondary_droplet_volume_expired_total=%.9g\n",
              sim.secondary_droplet_volume_expired_total);
  std::printf("secondary_bubble_volume_expired_total=%.9g\n",
              sim.secondary_bubble_volume_expired_total);
  std::printf("particle_boundary_clamped_x_lo_last=%d\n",
              sim.particle_boundary_clamped_x_lo_last);
  std::printf("particle_boundary_clamped_x_hi_last=%d\n",
              sim.particle_boundary_clamped_x_hi_last);
  std::printf("particle_boundary_clamped_y_lo_last=%d\n",
              sim.particle_boundary_clamped_y_lo_last);
  std::printf("particle_boundary_clamped_y_hi_last=%d\n",
              sim.particle_boundary_clamped_y_hi_last);
  std::printf("particle_boundary_clamped_z_lo_last=%d\n",
              sim.particle_boundary_clamped_z_lo_last);
  std::printf("particle_boundary_clamped_z_hi_last=%d\n",
              sim.particle_boundary_clamped_z_hi_last);
  std::printf("liquid_volume_start=%.9g\n", liquidVolume0);
  std::printf("liquid_volume_end=%.9g\n", liquidVolume1);
  std::printf("liquid_mass_start=%.9g\n", liquidVolume0 * sim.phase.rho_l);
  std::printf("liquid_mass_end=%.9g\n", liquidVolume1 * sim.phase.rho_l);
  std::printf("gas_volume_start=%.9g\n", gasVolume0);
  std::printf("gas_volume_end=%.9g\n", gasVolume1);
  std::printf("gas_mass_start=%.9g\n", gasVolume0 * sim.phase.rho_g);
  std::printf("gas_mass_end=%.9g\n", gasVolume1 * sim.phase.rho_g);
  std::printf("narrow_band_removed_last=%d\n", sim.narrow_band_air_removed_last);
  std::printf("narrow_band_removed_total=%d\n", sim.narrow_band_air_removed_total);
  std::printf("narrow_band_liquid_cells_last=%d\n", sim.narrow_band_air_liquid_cells_last);
  std::printf("narrow_band_gas_particles_before_last=%d\n",
              sim.narrow_band_air_gas_particles_before_last);
  std::printf("narrow_band_gas_particles_after_last=%d\n",
              sim.narrow_band_air_gas_particles_after_last);
  std::printf("gas_particle_coarsening_removed_last=%d\n",
              sim.gas_particle_coarsening_removed_last);
  std::printf("gas_particle_coarsening_removed_total=%d\n",
              sim.gas_particle_coarsening_removed_total);
  std::printf("gas_particle_coarsening_cells_last=%d\n",
              sim.gas_particle_coarsening_cells_last);
  std::printf("gas_particle_coarsening_overfull_cells_last=%d\n",
              sim.gas_particle_coarsening_overfull_cells_last);
  std::printf("gas_particle_coarsening_before_last=%d\n",
              sim.gas_particle_coarsening_before_last);
  std::printf("gas_particle_coarsening_after_last=%d\n",
              sim.gas_particle_coarsening_after_last);
  std::printf("liquid_particle_coarsening_removed_last=%d\n",
              sim.liquid_particle_coarsening_removed_last);
  std::printf("liquid_particle_coarsening_removed_total=%d\n",
              sim.liquid_particle_coarsening_removed_total);
  std::printf("liquid_particle_coarsening_removed_during_run=%d\n",
              liquidCoarseningRemovedDuringRun);
  std::printf("liquid_particle_coarsening_cells_last=%d\n",
              sim.liquid_particle_coarsening_cells_last);
  std::printf("liquid_particle_coarsening_overfull_cells_last=%d\n",
              sim.liquid_particle_coarsening_overfull_cells_last);
  std::printf("liquid_particle_coarsening_before_last=%d\n",
              sim.liquid_particle_coarsening_before_last);
  std::printf("liquid_particle_coarsening_after_last=%d\n",
              sim.liquid_particle_coarsening_after_last);
  std::printf("liquid_particle_refill_added_last=%d\n",
              sim.liquid_particle_refill_added_last);
  std::printf("liquid_particle_refill_added_total=%d\n",
              sim.liquid_particle_refill_added_total);
  std::printf("liquid_particle_refill_added_during_run=%d\n",
              liquidRefillAddedDuringRun);
  std::printf("liquid_particle_refill_cells_last=%d\n",
              sim.liquid_particle_refill_cells_last);
  std::printf("liquid_particle_refill_interface_cells_last=%d\n",
              sim.liquid_particle_refill_interface_cells_last);
  std::printf("liquid_particle_refill_underfull_cells_last=%d\n",
              sim.liquid_particle_refill_underfull_cells_last);
  std::printf("liquid_particle_refill_budget_limited_last=%d\n",
              sim.liquid_particle_refill_budget_limited_last);
  std::printf("liquid_particle_refill_before_last=%d\n",
              sim.liquid_particle_refill_before_last);
  std::printf("liquid_particle_refill_after_last=%d\n",
              sim.liquid_particle_refill_after_last);
  std::printf("finite=%s\n", finite ? "true" : "false");
  std::printf("active_pressure_blocks_max=%zu\n", maxActive);
  std::printf("active_pressure_blocks_total=%zu\n", totalBlocks);
  std::printf("heavy_mean_y_start=%.9g\n", heavy0);
  std::printf("heavy_mean_y_end=%.9g\n", heavy1);
  std::printf("gas_mean_y_start=%.9g\n", gas0);
  std::printf("gas_mean_y_end=%.9g\n", gas1);
  std::printf("elapsed_ms=%lld\n", elapsedMs);

  bool ok = true;
  const bool gasAdaptivity = sim.narrow_band_air || sim.gas_particle_coarsening;
  const bool liquidAdaptivity = sim.liquid_particle_coarsening || sim.liquid_particle_refill;
  const double liquidVolumeTol = std::max(1e-9, std::abs(liquidVolume0) * 1e-9);
  const double gasVolumeTol = std::max(1e-9, std::abs(gasVolume0) * 1e-9);
  if (!finite) ok = false;
  if (std::abs(liquidVolume1 - liquidVolume0) > liquidVolumeTol) ok = false;
  if (sim.narrow_band_air) {
    if (gasVolume1 > gasVolume0 + gasVolumeTol) ok = false;
  } else if (std::abs(gasVolume1 - gasVolume0) > gasVolumeTol) {
    ok = false;
  }
  if (sim.narrow_band_air || sim.gas_particle_coarsening || liquidAdaptivity) {
    const size_t maxParticles = n0 +
      static_cast<size_t>(std::max(0, liquidRefillAddedDuringRun));
    if (sim.particles.size() > maxParticles) ok = false;
  } else if (sim.particles.size() != n0) {
    ok = false;
  }
  if (sim.liquid_particle_refill) {
    const size_t maxLiquid = liquidCount0 +
      static_cast<size_t>(std::max(0, liquidRefillAddedDuringRun));
    if (liquidCount1 > maxLiquid) ok = false;
    if (sim.liquid_particle_refill_interface_only &&
        sim.liquid_particle_refill_underfull_cells_last >
          sim.liquid_particle_refill_interface_cells_last) {
      ok = false;
    }
    if (sim.liquid_particle_refill_max_added_per_step > 0) {
      const int cap = sim.liquid_particle_refill_max_added_per_step;
      if (sim.liquid_particle_refill_added_last > cap) ok = false;
      if (liquidRefillAddedDuringRun > steps * cap) ok = false;
    }
    if (sim.liquid_particle_coarsening &&
        liquidRefillAddedDuringRun > liquidCoarseningRemovedDuringRun) {
      ok = false;
    }
    if (!sim.liquid_particle_coarsening &&
        liquidCount1 != maxLiquid) {
      ok = false;
    }
  } else if (sim.liquid_particle_coarsening) {
    if (liquidCount1 > liquidCount0) ok = false;
  } else if (liquidCount1 != liquidCount0) {
    ok = false;
  }
  if (gasAdaptivity) {
    if (gasCount1 > gasCount0) ok = false;
  } else if (gasCount1 != gasCount0) {
    ok = false;
  }
  if (steps > 0) {
    if (!sim.interface_diagnostics_last.finite) ok = false;
    if (sim.interface_diagnostics_last.sample_cells <= 0) ok = false;
  }
  if (sim.surface_tension) {
    if (!sim.surface_tension_stats_last.enabled) ok = false;
    if (!sim.surface_tension_stats_last.finite) ok = false;
    if (steps > 0 && sim.interface_diagnostics_last.interface_cells > 0 &&
        sim.surface_tension_stats_last.applied_cells <= 0) {
      ok = false;
    }
    if (sim.surface_tension_max_delta_speed > 0.0 &&
        sim.surface_tension_stats_last.max_delta_speed >
          sim.surface_tension_max_delta_speed + 1e-12) {
      ok = false;
    }
    if (!sim.surface_tension_stats_last.capillary_stable) ok = false;
    if (sim.surface_tension_stats_last.capillary_dt_limit <= 0.0) ok = false;
    if (sim.surface_tension_stats_last.curvature_smoothing_radius !=
        sim.surface_tension_curvature_smoothing_radius) {
      ok = false;
    }
  } else if (sim.surface_tension_stats_last.enabled ||
             sim.surface_tension_stats_last.applied_cells != 0) {
    ok = false;
  }
  if (sim.escaped_particle_branching) {
    if (sim.escaped_droplets_added_total != sim.escaped_droplet_candidates_total) ok = false;
    if (sim.escaped_bubbles_added_total != sim.escaped_bubble_candidates_total) ok = false;
    if (sim.secondary_particle_lifecycle) {
      if (sim.escaped_droplets.size() +
            static_cast<size_t>(sim.secondary_droplets_reabsorbed_total +
                                sim.secondary_droplets_expired_total) !=
          static_cast<size_t>(sim.escaped_droplets_added_total)) {
        ok = false;
      }
      if (sim.escaped_bubbles.size() +
            static_cast<size_t>(sim.secondary_bubbles_reabsorbed_total +
                                sim.secondary_bubbles_expired_total) !=
          static_cast<size_t>(sim.escaped_bubbles_added_total)) {
        ok = false;
      }
    } else {
      if (sim.escaped_droplets.size() != static_cast<size_t>(sim.escaped_droplets_added_total)) ok = false;
      if (sim.escaped_bubbles.size() != static_cast<size_t>(sim.escaped_bubbles_added_total)) ok = false;
    }
  } else {
    if (sim.escaped_droplets_added_total != 0) ok = false;
    if (sim.escaped_bubbles_added_total != 0) ok = false;
    if (sim.escaped_droplets.size() != 0) ok = false;
    if (sim.escaped_bubbles.size() != 0) ok = false;
  }
  if (sim.escaped_droplet_ages.size() != sim.escaped_droplets.size()) ok = false;
  if (sim.escaped_bubble_ages.size() != sim.escaped_bubbles.size()) ok = false;
  if (sim.secondary_particle_lifecycle) {
    if (!sim.secondary_lifecycle_stats_last.enabled) ok = false;
  } else if (sim.secondary_lifecycle_stats_last.enabled) {
    ok = false;
  }
  if (!sim.secondary_lifecycle_stats_last.finite) ok = false;
  auto secondaryVolumeBalanceOk = [](double added,
                                     double current,
                                     double reabsorbed,
                                     double expired) {
    const double lhs = current + reabsorbed + expired;
    const double tol = std::max(1e-9, std::abs(added) * 1e-9);
    return std::abs(lhs - added) <= tol;
  };
  if (!secondaryVolumeBalanceOk(sim.escaped_droplet_volume_added_total,
                                sim.secondary_droplet_volume_current_last,
                                sim.secondary_droplet_volume_reabsorbed_total,
                                sim.secondary_droplet_volume_expired_total)) {
    ok = false;
  }
  if (!secondaryVolumeBalanceOk(sim.escaped_bubble_volume_added_total,
                                sim.secondary_bubble_volume_current_last,
                                sim.secondary_bubble_volume_reabsorbed_total,
                                sim.secondary_bubble_volume_expired_total)) {
    ok = false;
  }
  if (physicsPreset && !fullPhysicsPresetActive3D(sim)) ok = false;
  if (std::strcmp(scenario, "rt") == 0 && !(heavy1 < heavy0)) ok = false;
  if (std::strcmp(scenario, "bubble") == 0) {
    if (!(gas1 > gas0)) ok = false;
    if (!(maxActive < totalBlocks)) ok = false;
  }

  std::printf("status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
