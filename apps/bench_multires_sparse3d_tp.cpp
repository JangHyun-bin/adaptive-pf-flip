#include "driver/multires_sim3d_tp.h"
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
    if (!std::isfinite(ps.pos[i].x) ||
        !std::isfinite(ps.pos[i].y) ||
        !std::isfinite(ps.pos[i].z)) {
      return false;
    }
  }
  return true;
}

struct SparseMetrics {
  size_t particlesStart = 0;
  size_t particlesEnd = 0;
  size_t liquidStart = 0;
  size_t liquidEnd = 0;
  size_t gasCountStart = 0;
  size_t gasCountEnd = 0;
  double liquidVolumeStart = 0.0;
  double liquidVolumeEnd = 0.0;
  double gasVolumeStart = 0.0;
  double gasVolumeEnd = 0.0;
  int boundaryClampedLiquidTotal = 0;
  int boundaryClampedGasTotal = 0;
  int escapedDropletCandidatesTotal = 0;
  int escapedBubbleCandidatesTotal = 0;
  int escapedDropletsAddedTotal = 0;
  int escapedBubblesAddedTotal = 0;
  size_t escapedDropletParticles = 0;
  size_t escapedBubbleParticles = 0;
  size_t escapedDropletAges = 0;
  size_t escapedBubbleAges = 0;
  double escapedDropletVolumeAddedTotal = 0.0;
  double escapedBubbleVolumeAddedTotal = 0.0;
  int secondaryLifecycleEnabled = 0;
  int secondaryLifecycleFinite = 1;
  int secondaryDropletsAdvectedTotal = 0;
  int secondaryBubblesAdvectedTotal = 0;
  int secondaryDropletsReabsorbedTotal = 0;
  int secondaryBubblesReabsorbedTotal = 0;
  int secondaryDropletsExpiredTotal = 0;
  int secondaryBubblesExpiredTotal = 0;
  double secondaryDropletVolumeCurrent = 0.0;
  double secondaryBubbleVolumeCurrent = 0.0;
  double secondaryDropletVolumeReabsorbedTotal = 0.0;
  double secondaryBubbleVolumeReabsorbedTotal = 0.0;
  double secondaryDropletVolumeExpiredTotal = 0.0;
  double secondaryBubbleVolumeExpiredTotal = 0.0;
  double effectiveDtLast = 0.0;
  double cflLimitDtLast = 0.0;
  double maxParticleSpeedLast = 0.0;
  int adaptiveTimestepLimitedLast = 0;
  double liquidVolumeTarget = 0.0;
  double liquidVolumeCurrentLast = 0.0;
  double liquidVolumeErrorLast = 0.0;
  double cDivLast = 0.0;
  InterfaceDiagnostics3D interfaceDiagnostics;
  SurfaceTensionStats3D surfaceTensionStats;
  int liquidCoarseningRemovedStart = 0;
  int liquidCoarseningRemovedEnd = 0;
  int liquidCoarseningRemovedDuringRun = 0;
  int liquidRefillAddedStart = 0;
  int liquidRefillAddedEnd = 0;
  int liquidRefillAddedDuringRun = 0;
  double gasStart = 0.0;
  double gasEnd = 0.0;
  size_t maxBlocks = 0;
  long long elapsedMs = 0;
  bool finite = false;
};

SparseMetrics runSparseBubble(SparseSim3DTP& sim, int steps, double liquidVolumeTargetOverride) {
  sim.initBubbleTank();
  if (liquidVolumeTargetOverride >= 0.0) {
    sim.liquid_volume_target = liquidVolumeTargetOverride;
  }
  SparseMetrics metrics;
  metrics.particlesStart = sim.particles.size();
  metrics.liquidStart = countType(sim.particles, 0);
  metrics.gasCountStart = countType(sim.particles, 1);
  metrics.liquidVolumeStart = volumeType(sim.particles, 0, sim.Vp);
  metrics.gasVolumeStart = volumeType(sim.particles, 1, sim.Vp);
  metrics.liquidCoarseningRemovedStart = sim.liquid_particle_coarsening_removed_total;
  metrics.liquidRefillAddedStart = sim.liquid_particle_refill_added_total;
  metrics.gasStart = meanY(sim.particles, 1);

  auto start = std::chrono::steady_clock::now();
  for (int s = 0; s < steps; ++s) {
    sim.step();
    metrics.maxBlocks = std::max(metrics.maxBlocks, sim.grid.activeCellBlocks());
  }
  auto end = std::chrono::steady_clock::now();

  metrics.particlesEnd = sim.particles.size();
  metrics.liquidEnd = countType(sim.particles, 0);
  metrics.gasCountEnd = countType(sim.particles, 1);
  metrics.liquidVolumeEnd = volumeType(sim.particles, 0, sim.Vp);
  metrics.gasVolumeEnd = volumeType(sim.particles, 1, sim.Vp);
  metrics.boundaryClampedLiquidTotal = sim.particle_boundary_clamped_liquid_total;
  metrics.boundaryClampedGasTotal = sim.particle_boundary_clamped_gas_total;
  metrics.escapedDropletCandidatesTotal = sim.escaped_droplet_candidates_total;
  metrics.escapedBubbleCandidatesTotal = sim.escaped_bubble_candidates_total;
  metrics.escapedDropletsAddedTotal = sim.escaped_droplets_added_total;
  metrics.escapedBubblesAddedTotal = sim.escaped_bubbles_added_total;
  metrics.escapedDropletParticles = sim.escaped_droplets.size();
  metrics.escapedBubbleParticles = sim.escaped_bubbles.size();
  metrics.escapedDropletAges = sim.escaped_droplet_ages.size();
  metrics.escapedBubbleAges = sim.escaped_bubble_ages.size();
  metrics.escapedDropletVolumeAddedTotal = sim.escaped_droplet_volume_added_total;
  metrics.escapedBubbleVolumeAddedTotal = sim.escaped_bubble_volume_added_total;
  metrics.secondaryLifecycleEnabled = sim.secondary_lifecycle_stats_last.enabled;
  metrics.secondaryLifecycleFinite = sim.secondary_lifecycle_stats_last.finite;
  metrics.secondaryDropletsAdvectedTotal = sim.secondary_droplets_advected_total;
  metrics.secondaryBubblesAdvectedTotal = sim.secondary_bubbles_advected_total;
  metrics.secondaryDropletsReabsorbedTotal = sim.secondary_droplets_reabsorbed_total;
  metrics.secondaryBubblesReabsorbedTotal = sim.secondary_bubbles_reabsorbed_total;
  metrics.secondaryDropletsExpiredTotal = sim.secondary_droplets_expired_total;
  metrics.secondaryBubblesExpiredTotal = sim.secondary_bubbles_expired_total;
  metrics.secondaryDropletVolumeCurrent = sim.secondary_droplet_volume_current_last;
  metrics.secondaryBubbleVolumeCurrent = sim.secondary_bubble_volume_current_last;
  metrics.secondaryDropletVolumeReabsorbedTotal =
    sim.secondary_droplet_volume_reabsorbed_total;
  metrics.secondaryBubbleVolumeReabsorbedTotal =
    sim.secondary_bubble_volume_reabsorbed_total;
  metrics.secondaryDropletVolumeExpiredTotal =
    sim.secondary_droplet_volume_expired_total;
  metrics.secondaryBubbleVolumeExpiredTotal =
    sim.secondary_bubble_volume_expired_total;
  metrics.effectiveDtLast = sim.effective_dt_last;
  metrics.cflLimitDtLast = sim.cfl_limit_dt_last;
  metrics.maxParticleSpeedLast = sim.max_particle_speed_last;
  metrics.adaptiveTimestepLimitedLast = sim.adaptive_timestep_limited_last;
  metrics.liquidVolumeTarget = sim.liquid_volume_target;
  metrics.liquidVolumeCurrentLast = sim.liquid_volume_current_last;
  metrics.liquidVolumeErrorLast = sim.liquid_volume_error_last;
  metrics.cDivLast = sim.c_div_last;
  metrics.interfaceDiagnostics = sim.interface_diagnostics_last;
  metrics.surfaceTensionStats = sim.surface_tension_stats_last;
  metrics.liquidCoarseningRemovedEnd = sim.liquid_particle_coarsening_removed_total;
  metrics.liquidCoarseningRemovedDuringRun =
    metrics.liquidCoarseningRemovedEnd - metrics.liquidCoarseningRemovedStart;
  metrics.liquidRefillAddedEnd = sim.liquid_particle_refill_added_total;
  metrics.liquidRefillAddedDuringRun =
    metrics.liquidRefillAddedEnd - metrics.liquidRefillAddedStart;
  metrics.gasEnd = meanY(sim.particles, 1);
  metrics.finite = finiteParticles(sim.particles);
  metrics.elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
  return metrics;
}

void usage() {
  std::fprintf(stderr,
               "usage: bench_multires_sparse3d_tp [--nx N] [--ny N] [--nz N] "
               "[--steps N] [--dt DT] [--cg-iters N] [--hysteresis N] "
               "[--max-fine-leaves N] [--cg-rel-tol T] [--rho-ratio R] "
               "[--physics-preset] [--long-physics-preset] "
               "[--adaptive-timestep] [--adaptive-cfl C] [--adaptive-min-dt DT] "
               "[--advection-order 2|3] "
               "[--c-div-volume-correction] [--c-div-strength S] [--liquid-volume-target V] "
               "[--surface-tension] [--surface-tension-strength S] "
               "[--surface-tension-max-delta-speed V] "
               "[--escaped-particle-branching] "
               "[--secondary-lifecycle] [--secondary-droplet-lifetime N] "
               "[--secondary-bubble-lifetime N] [--secondary-velocity-damping D] "
               "[--secondary-reabsorb-margin C] [--secondary-bubble-buoyancy-scale S] "
               "[--require-converged] [--no-jacobi] [--flexible-cg] "
               "[--no-restart] [--restart-growth G] "
               "[--relax-sweeps N] [--relax-omega W] [--relax-min-omega W] "
               "[--history-stride N] [--history-limit N] "
               "[--sparse-narrow-band-air] [--sparse-narrow-band-radius N] "
               "[--sparse-gas-coarsening] [--sparse-gas-particles-per-cell N] "
               "[--sparse-gas-coarsening-seed N] "
               "[--sparse-liquid-coarsening] [--sparse-liquid-particles-per-cell N] "
               "[--sparse-liquid-coarsening-seed N] "
               "[--sparse-liquid-refill] [--sparse-liquid-refill-particles-per-cell N] "
               "[--sparse-liquid-refill-seed N] "
               "[--sparse-liquid-refill-max-added-per-step N] "
               "[--sparse-liquid-refill-interface-only] "
               "[--sparse-liquid-refill-interface-radius N] "
               "[--mr-narrow-band-air] [--mr-narrow-band-radius N] "
               "[--mr-gas-coarsening] [--mr-gas-particles-per-cell N] "
               "[--mr-gas-coarsening-seed N] "
               "[--mr-liquid-coarsening] [--mr-liquid-particles-per-cell N] "
               "[--mr-liquid-coarsening-seed N] "
               "[--mr-liquid-refill] [--mr-liquid-refill-particles-per-cell N] "
               "[--mr-liquid-refill-seed N] "
               "[--mr-liquid-refill-max-added-per-step N] "
               "[--mr-liquid-refill-interface-only] "
               "[--mr-liquid-refill-interface-radius N]\n");
}

} // namespace

int main(int argc, char** argv) {
  const bool physicsPreset = hasFlag(argc, argv, "--physics-preset") ||
                             hasFlag(argc, argv, "--long-physics-preset");
  const bool longPhysicsPreset = hasFlag(argc, argv, "--long-physics-preset");
  int nx = argInt(argc, argv, "--nx", 12);
  int ny = argInt(argc, argv, "--ny", 18);
  int nz = argInt(argc, argv, "--nz", 12);
  const int defaultSteps = longPhysicsPreset
    ? kLongPhysicsPresetBenchSteps3D
    : (physicsPreset ? kPhysicsPresetBenchSteps3D : 4);
  int steps = argInt(argc, argv, "--steps", defaultSteps);

  if (nx < 4 || ny < 4 || nz < 4 || steps < 0) {
    usage();
    return 2;
  }

  SparseSim3DTP sparse(nx, ny, nz, 1.0);
  SparseSim3DTP sparseAdaptive(nx, ny, nz, 1.0);
  MRSim3DTP mr(nx, ny, nz, 1.0);
  if (physicsPreset) {
    applyCorePhysicsPreset3D(sparse);
    applyFullPhysicsPreset3D(sparseAdaptive);
    applyCorePhysicsPreset3D(mr);
  }
  double requestedRhoRatio = argDouble(argc, argv, "--rho-ratio", 0.0);
  if (requestedRhoRatio > 0.0) {
    sparse.phase.rho_l = requestedRhoRatio;
    sparse.phase.rho_g = 1.0;
    sparseAdaptive.phase.rho_l = requestedRhoRatio;
    sparseAdaptive.phase.rho_g = 1.0;
    mr.phase.rho_l = requestedRhoRatio;
    mr.phase.rho_g = 1.0;
  }
  double dt = argDouble(argc, argv, "--dt", mr.dt);
  int cgIters = argInt(argc, argv, "--cg-iters", mr.cg_iters);
  sparse.dt = dt;
  sparseAdaptive.dt = dt;
  mr.dt = dt;
  const bool adaptiveTimestep =
    sparse.adaptive_timestep || hasFlag(argc, argv, "--adaptive-timestep");
  const double adaptiveCfl = argDouble(argc, argv, "--adaptive-cfl", mr.adaptive_cfl);
  const double adaptiveMinDt = argDouble(argc, argv, "--adaptive-min-dt", mr.adaptive_min_dt);
  const int advectionOrder = argInt(argc, argv, "--advection-order", mr.advection_order);
  const bool cDivVolumeCorrection =
    sparse.c_div_volume_correction || hasFlag(argc, argv, "--c-div-volume-correction");
  const double cDivStrength = argDouble(argc, argv, "--c-div-strength", mr.c_div_strength);
  const double liquidVolumeTargetOverride =
    argDouble(argc, argv, "--liquid-volume-target", -0.25);
  const bool surfaceTension =
    sparse.surface_tension || hasFlag(argc, argv, "--surface-tension");
  const double surfaceTensionStrength =
    argDouble(argc, argv, "--surface-tension-strength", mr.surface_tension_strength);
  const double surfaceTensionMaxDeltaSpeed =
    argDouble(argc, argv, "--surface-tension-max-delta-speed",
              mr.surface_tension_max_delta_speed);
  const bool secondaryLifecycle =
    sparse.secondary_particle_lifecycle || hasFlag(argc, argv, "--secondary-lifecycle");
  const int secondaryDropletLifetime =
    argInt(argc, argv, "--secondary-droplet-lifetime",
           sparse.secondary_droplet_lifetime_steps);
  const int secondaryBubbleLifetime =
    argInt(argc, argv, "--secondary-bubble-lifetime",
           sparse.secondary_bubble_lifetime_steps);
  const double secondaryVelocityDamping =
    argDouble(argc, argv, "--secondary-velocity-damping",
              sparse.secondary_velocity_damping);
  const double secondaryReabsorbMargin =
    argDouble(argc, argv, "--secondary-reabsorb-margin",
              sparse.secondary_reabsorb_margin_cells);
  const double secondaryBubbleBuoyancyScale =
    argDouble(argc, argv, "--secondary-bubble-buoyancy-scale",
              sparse.secondary_bubble_buoyancy_scale);
  const bool escapedParticleBranching =
    sparse.escaped_particle_branching ||
    hasFlag(argc, argv, "--escaped-particle-branching") ||
    secondaryLifecycle;
  sparse.adaptive_timestep = adaptiveTimestep;
  sparseAdaptive.adaptive_timestep = adaptiveTimestep;
  mr.adaptive_timestep = adaptiveTimestep;
  sparse.c_div_volume_correction = cDivVolumeCorrection;
  sparseAdaptive.c_div_volume_correction = cDivVolumeCorrection;
  mr.c_div_volume_correction = cDivVolumeCorrection;
  sparse.c_div_strength = cDivStrength;
  sparseAdaptive.c_div_strength = cDivStrength;
  mr.c_div_strength = cDivStrength;
  sparse.surface_tension = surfaceTension;
  sparseAdaptive.surface_tension = surfaceTension;
  mr.surface_tension = surfaceTension;
  sparse.surface_tension_strength = surfaceTensionStrength;
  sparseAdaptive.surface_tension_strength = surfaceTensionStrength;
  mr.surface_tension_strength = surfaceTensionStrength;
  sparse.surface_tension_max_delta_speed = surfaceTensionMaxDeltaSpeed;
  sparseAdaptive.surface_tension_max_delta_speed = surfaceTensionMaxDeltaSpeed;
  mr.surface_tension_max_delta_speed = surfaceTensionMaxDeltaSpeed;
  sparse.escaped_particle_branching = escapedParticleBranching;
  sparseAdaptive.escaped_particle_branching = escapedParticleBranching;
  mr.escaped_particle_branching = escapedParticleBranching;
  sparse.secondary_particle_lifecycle = secondaryLifecycle;
  sparseAdaptive.secondary_particle_lifecycle = secondaryLifecycle;
  mr.secondary_particle_lifecycle = secondaryLifecycle;
  sparse.secondary_droplet_lifetime_steps = secondaryDropletLifetime;
  sparseAdaptive.secondary_droplet_lifetime_steps = secondaryDropletLifetime;
  mr.secondary_droplet_lifetime_steps = secondaryDropletLifetime;
  sparse.secondary_bubble_lifetime_steps = secondaryBubbleLifetime;
  sparseAdaptive.secondary_bubble_lifetime_steps = secondaryBubbleLifetime;
  mr.secondary_bubble_lifetime_steps = secondaryBubbleLifetime;
  sparse.secondary_velocity_damping = secondaryVelocityDamping;
  sparseAdaptive.secondary_velocity_damping = secondaryVelocityDamping;
  mr.secondary_velocity_damping = secondaryVelocityDamping;
  sparse.secondary_reabsorb_margin_cells = secondaryReabsorbMargin;
  sparseAdaptive.secondary_reabsorb_margin_cells = secondaryReabsorbMargin;
  mr.secondary_reabsorb_margin_cells = secondaryReabsorbMargin;
  sparse.secondary_bubble_buoyancy_scale = secondaryBubbleBuoyancyScale;
  sparseAdaptive.secondary_bubble_buoyancy_scale = secondaryBubbleBuoyancyScale;
  mr.secondary_bubble_buoyancy_scale = secondaryBubbleBuoyancyScale;
  sparse.advection_order = advectionOrder;
  sparseAdaptive.advection_order = advectionOrder;
  mr.advection_order = advectionOrder;
  sparse.adaptive_cfl = adaptiveCfl;
  sparseAdaptive.adaptive_cfl = adaptiveCfl;
  mr.adaptive_cfl = adaptiveCfl;
  sparse.adaptive_min_dt = adaptiveMinDt;
  sparseAdaptive.adaptive_min_dt = adaptiveMinDt;
  mr.adaptive_min_dt = adaptiveMinDt;
  sparse.cg_iters = cgIters;
  sparseAdaptive.cg_iters = cgIters;
  mr.cg_iters = cgIters;
  sparseAdaptive.narrow_band_air = sparseAdaptive.narrow_band_air ||
                                   hasFlag(argc, argv, "--sparse-narrow-band-air");
  sparseAdaptive.narrow_band_air_radius =
    argInt(argc, argv, "--sparse-narrow-band-radius",
           sparseAdaptive.narrow_band_air_radius);
  sparseAdaptive.gas_particle_coarsening =
    sparseAdaptive.gas_particle_coarsening ||
    hasFlag(argc, argv, "--sparse-gas-coarsening");
  sparseAdaptive.gas_particles_per_cell_target =
    argInt(argc, argv, "--sparse-gas-particles-per-cell",
           sparseAdaptive.gas_particles_per_cell_target);
  sparseAdaptive.gas_particle_coarsening_seed =
    argUInt(argc, argv, "--sparse-gas-coarsening-seed",
            sparseAdaptive.gas_particle_coarsening_seed);
  sparseAdaptive.liquid_particle_coarsening =
    sparseAdaptive.liquid_particle_coarsening ||
    hasFlag(argc, argv, "--sparse-liquid-coarsening");
  sparseAdaptive.liquid_particles_per_cell_target =
    argInt(argc, argv, "--sparse-liquid-particles-per-cell",
           sparseAdaptive.liquid_particles_per_cell_target);
  sparseAdaptive.liquid_particle_coarsening_seed =
    argUInt(argc, argv, "--sparse-liquid-coarsening-seed",
            sparseAdaptive.liquid_particle_coarsening_seed);
  sparseAdaptive.liquid_particle_refill =
    sparseAdaptive.liquid_particle_refill ||
    hasFlag(argc, argv, "--sparse-liquid-refill");
  sparseAdaptive.liquid_refill_particles_per_cell_target =
    argInt(argc, argv, "--sparse-liquid-refill-particles-per-cell",
           sparseAdaptive.liquid_refill_particles_per_cell_target);
  sparseAdaptive.liquid_particle_refill_seed =
    argUInt(argc, argv, "--sparse-liquid-refill-seed",
            sparseAdaptive.liquid_particle_refill_seed);
  sparseAdaptive.liquid_particle_refill_max_added_per_step =
    argInt(argc, argv, "--sparse-liquid-refill-max-added-per-step",
           sparseAdaptive.liquid_particle_refill_max_added_per_step);
  sparseAdaptive.liquid_particle_refill_interface_only =
    sparseAdaptive.liquid_particle_refill_interface_only ||
    hasFlag(argc, argv, "--sparse-liquid-refill-interface-only");
  sparseAdaptive.liquid_particle_refill_interface_radius =
    argInt(argc, argv, "--sparse-liquid-refill-interface-radius",
           sparseAdaptive.liquid_particle_refill_interface_radius);
  const bool sparseGasAdaptivity =
    sparseAdaptive.narrow_band_air || sparseAdaptive.gas_particle_coarsening;
  const bool sparseLiquidRefill = sparseAdaptive.liquid_particle_refill;
  const bool sparseLiquidAdaptivity =
    sparseAdaptive.liquid_particle_coarsening || sparseLiquidRefill;
  const bool sparseAdaptivity =
    sparseGasAdaptivity || sparseLiquidAdaptivity;
  mr.cg_rel_tol = argDouble(argc, argv, "--cg-rel-tol", mr.cg_rel_tol);
  if (hasFlag(argc, argv, "--no-jacobi")) mr.cg_jacobi_preconditioner = false;
  if (hasFlag(argc, argv, "--flexible-cg")) mr.cg_flexible_beta = true;
  if (hasFlag(argc, argv, "--no-restart")) mr.cg_adaptive_restart = false;
  mr.cg_restart_growth = argDouble(argc, argv, "--restart-growth", mr.cg_restart_growth);
  mr.cg_relaxation_sweeps = argInt(argc, argv, "--relax-sweeps", mr.cg_relaxation_sweeps);
  mr.cg_relaxation_omega = argDouble(argc, argv, "--relax-omega", mr.cg_relaxation_omega);
  mr.cg_relaxation_min_omega = argDouble(argc, argv, "--relax-min-omega", mr.cg_relaxation_min_omega);
  mr.cg_residual_history_stride = argInt(argc, argv, "--history-stride", mr.cg_residual_history_stride);
  mr.cg_residual_history_limit = argInt(argc, argv, "--history-limit", mr.cg_residual_history_limit);
  mr.dynamic_hysteresis_cells = argInt(argc, argv, "--hysteresis", mr.dynamic_hysteresis_cells);
  mr.dynamic_max_fine_leaves = argInt(argc, argv, "--max-fine-leaves", mr.dynamic_max_fine_leaves);
  MRSim3DTP mrAdaptive = mr;
  if (physicsPreset) {
    applyFullPhysicsPreset3D(mrAdaptive);
  }
  mrAdaptive.adaptive_timestep = adaptiveTimestep;
  mrAdaptive.adaptive_cfl = adaptiveCfl;
  mrAdaptive.adaptive_min_dt = adaptiveMinDt;
  mrAdaptive.advection_order = advectionOrder;
  mrAdaptive.c_div_volume_correction = cDivVolumeCorrection;
  mrAdaptive.c_div_strength = cDivStrength;
  mrAdaptive.surface_tension = surfaceTension;
  mrAdaptive.surface_tension_strength = surfaceTensionStrength;
  mrAdaptive.surface_tension_max_delta_speed = surfaceTensionMaxDeltaSpeed;
  mrAdaptive.escaped_particle_branching = escapedParticleBranching;
  mrAdaptive.secondary_particle_lifecycle = secondaryLifecycle;
  mrAdaptive.secondary_droplet_lifetime_steps = secondaryDropletLifetime;
  mrAdaptive.secondary_bubble_lifetime_steps = secondaryBubbleLifetime;
  mrAdaptive.secondary_velocity_damping = secondaryVelocityDamping;
  mrAdaptive.secondary_reabsorb_margin_cells = secondaryReabsorbMargin;
  mrAdaptive.secondary_bubble_buoyancy_scale = secondaryBubbleBuoyancyScale;
  mrAdaptive.narrow_band_air = mrAdaptive.narrow_band_air ||
                               hasFlag(argc, argv, "--mr-narrow-band-air");
  mrAdaptive.narrow_band_air_radius =
    argInt(argc, argv, "--mr-narrow-band-radius",
           mrAdaptive.narrow_band_air_radius);
  mrAdaptive.gas_particle_coarsening =
    mrAdaptive.gas_particle_coarsening ||
    hasFlag(argc, argv, "--mr-gas-coarsening");
  mrAdaptive.gas_particles_per_cell_target =
    argInt(argc, argv, "--mr-gas-particles-per-cell",
           mrAdaptive.gas_particles_per_cell_target);
  mrAdaptive.gas_particle_coarsening_seed =
    argUInt(argc, argv, "--mr-gas-coarsening-seed",
            mrAdaptive.gas_particle_coarsening_seed);
  mrAdaptive.liquid_particle_coarsening =
    mrAdaptive.liquid_particle_coarsening ||
    hasFlag(argc, argv, "--mr-liquid-coarsening");
  mrAdaptive.liquid_particles_per_cell_target =
    argInt(argc, argv, "--mr-liquid-particles-per-cell",
           mrAdaptive.liquid_particles_per_cell_target);
  mrAdaptive.liquid_particle_coarsening_seed =
    argUInt(argc, argv, "--mr-liquid-coarsening-seed",
            mrAdaptive.liquid_particle_coarsening_seed);
  mrAdaptive.liquid_particle_refill =
    mrAdaptive.liquid_particle_refill ||
    hasFlag(argc, argv, "--mr-liquid-refill");
  mrAdaptive.liquid_refill_particles_per_cell_target =
    argInt(argc, argv, "--mr-liquid-refill-particles-per-cell",
           mrAdaptive.liquid_refill_particles_per_cell_target);
  mrAdaptive.liquid_particle_refill_seed =
    argUInt(argc, argv, "--mr-liquid-refill-seed",
            mrAdaptive.liquid_particle_refill_seed);
  mrAdaptive.liquid_particle_refill_max_added_per_step =
    argInt(argc, argv, "--mr-liquid-refill-max-added-per-step",
           mrAdaptive.liquid_particle_refill_max_added_per_step);
  mrAdaptive.liquid_particle_refill_interface_only =
    mrAdaptive.liquid_particle_refill_interface_only ||
    hasFlag(argc, argv, "--mr-liquid-refill-interface-only");
  mrAdaptive.liquid_particle_refill_interface_radius =
    argInt(argc, argv, "--mr-liquid-refill-interface-radius",
           mrAdaptive.liquid_particle_refill_interface_radius);
  const bool mrGasAdaptivity =
    mrAdaptive.narrow_band_air || mrAdaptive.gas_particle_coarsening;
  const bool mrLiquidRefill = mrAdaptive.liquid_particle_refill;
  const bool mrLiquidAdaptivity =
    mrAdaptive.liquid_particle_coarsening || mrLiquidRefill;
  const bool mrAdaptivity =
    mrGasAdaptivity || mrLiquidAdaptivity;
  if (requestedRhoRatio < 0.0 ||
      sparse.phase.rho_l <= 0.0 ||
      sparse.phase.rho_g <= 0.0 ||
      mr.phase.rho_l <= 0.0 ||
      mr.phase.rho_g <= 0.0 ||
      adaptiveCfl <= 0.0 ||
      adaptiveMinDt < 0.0 ||
      (advectionOrder != 2 && advectionOrder != 3) ||
      cDivStrength < 0.0 ||
      surfaceTensionStrength < 0.0 ||
      surfaceTensionMaxDeltaSpeed < 0.0 ||
      secondaryDropletLifetime < 0 ||
      secondaryBubbleLifetime < 0 ||
      secondaryVelocityDamping < 0.0 ||
      secondaryVelocityDamping > 1.0 ||
      secondaryReabsorbMargin < 0.0 ||
      secondaryBubbleBuoyancyScale < 0.0 ||
      liquidVolumeTargetOverride < -0.5 ||
      sparseAdaptive.narrow_band_air_radius < 0 ||
      sparseAdaptive.gas_particles_per_cell_target <= 0 ||
      sparseAdaptive.liquid_particles_per_cell_target <= 0 ||
      sparseAdaptive.liquid_refill_particles_per_cell_target <= 0 ||
      sparseAdaptive.liquid_particle_refill_max_added_per_step < 0 ||
      sparseAdaptive.liquid_particle_refill_interface_radius < 0 ||
      mrAdaptive.narrow_band_air_radius < 0 ||
      mrAdaptive.gas_particles_per_cell_target <= 0 ||
      mrAdaptive.liquid_particles_per_cell_target <= 0 ||
      mrAdaptive.liquid_refill_particles_per_cell_target <= 0 ||
      mrAdaptive.liquid_particle_refill_max_added_per_step < 0 ||
      mrAdaptive.liquid_particle_refill_interface_radius < 0 ||
      mr.cg_restart_growth < 0.0 ||
      mr.cg_relaxation_sweeps < 0 ||
      mr.cg_relaxation_omega < 0.0 ||
      mr.cg_relaxation_min_omega < 0.0 ||
      mr.cg_residual_history_stride < 0 ||
      mr.cg_residual_history_limit < 0) {
    usage();
    return 2;
  }
  const double activeRhoRatio = mr.phase.rho_l / mr.phase.rho_g;
  const bool highDensityRatio = activeRhoRatio >= 1000.0;
  const bool requireConverged = hasFlag(argc, argv, "--require-converged") || highDensityRatio;

  SparseMetrics sparseMetrics = runSparseBubble(sparse, steps, liquidVolumeTargetOverride);
  SparseMetrics adaptiveMetrics;
  if (sparseAdaptivity) {
    adaptiveMetrics = runSparseBubble(sparseAdaptive, steps, liquidVolumeTargetOverride);
  } else {
    adaptiveMetrics = sparseMetrics;
  }

  mr.initBubbleTankInterfaceBand();
  if (liquidVolumeTargetOverride >= 0.0) {
    mr.liquid_volume_target = liquidVolumeTargetOverride;
  }

  size_t mrN0 = mr.particles.size();
  size_t mrLiquid0 = countType(mr.particles, 0);
  size_t mrGasCount0 = countType(mr.particles, 1);
  double mrLiquidVolume0 = volumeType(mr.particles, 0, mr.Vp);
  double mrGasVolume0 = volumeType(mr.particles, 1, mr.Vp);
  double mrGas0 = meanY(mr.particles, 1);

  auto mrStart = std::chrono::steady_clock::now();
  for (int s = 0; s < steps; ++s) {
    mr.step();
  }
  auto mrEnd = std::chrono::steady_clock::now();

  double mrGas1 = meanY(mr.particles, 1);
  size_t mrLiquid1 = countType(mr.particles, 0);
  size_t mrGasCount1 = countType(mr.particles, 1);
  double mrLiquidVolume1 = volumeType(mr.particles, 0, mr.Vp);
  double mrGasVolume1 = volumeType(mr.particles, 1, mr.Vp);
  int mrBoundaryClampedLiquidTotal = mr.particle_boundary_clamped_liquid_total;
  int mrBoundaryClampedGasTotal = mr.particle_boundary_clamped_gas_total;
  int mrEscapedDropletCandidatesTotal = mr.escaped_droplet_candidates_total;
  int mrEscapedBubbleCandidatesTotal = mr.escaped_bubble_candidates_total;
  int mrEscapedDropletsAddedTotal = mr.escaped_droplets_added_total;
  int mrEscapedBubblesAddedTotal = mr.escaped_bubbles_added_total;
  size_t mrEscapedDropletParticles = mr.escaped_droplets.size();
  size_t mrEscapedBubbleParticles = mr.escaped_bubbles.size();
  size_t mrEscapedDropletAges = mr.escaped_droplet_ages.size();
  size_t mrEscapedBubbleAges = mr.escaped_bubble_ages.size();
  double mrEscapedDropletVolumeAddedTotal = mr.escaped_droplet_volume_added_total;
  double mrEscapedBubbleVolumeAddedTotal = mr.escaped_bubble_volume_added_total;
  int mrSecondaryLifecycleEnabled = mr.secondary_lifecycle_stats_last.enabled;
  int mrSecondaryLifecycleFinite = mr.secondary_lifecycle_stats_last.finite;
  int mrSecondaryDropletsAdvectedTotal = mr.secondary_droplets_advected_total;
  int mrSecondaryBubblesAdvectedTotal = mr.secondary_bubbles_advected_total;
  int mrSecondaryDropletsReabsorbedTotal = mr.secondary_droplets_reabsorbed_total;
  int mrSecondaryBubblesReabsorbedTotal = mr.secondary_bubbles_reabsorbed_total;
  int mrSecondaryDropletsExpiredTotal = mr.secondary_droplets_expired_total;
  int mrSecondaryBubblesExpiredTotal = mr.secondary_bubbles_expired_total;
  double mrSecondaryDropletVolumeCurrent = mr.secondary_droplet_volume_current_last;
  double mrSecondaryBubbleVolumeCurrent = mr.secondary_bubble_volume_current_last;
  double mrSecondaryDropletVolumeReabsorbedTotal =
    mr.secondary_droplet_volume_reabsorbed_total;
  double mrSecondaryBubbleVolumeReabsorbedTotal =
    mr.secondary_bubble_volume_reabsorbed_total;
  double mrSecondaryDropletVolumeExpiredTotal =
    mr.secondary_droplet_volume_expired_total;
  double mrSecondaryBubbleVolumeExpiredTotal =
    mr.secondary_bubble_volume_expired_total;
  double mrEffectiveDtLast = mr.effective_dt_last;
  double mrCflLimitDtLast = mr.cfl_limit_dt_last;
  double mrMaxParticleSpeedLast = mr.max_particle_speed_last;
  int mrAdaptiveTimestepLimitedLast = mr.adaptive_timestep_limited_last;
  double mrLiquidVolumeTarget = mr.liquid_volume_target;
  double mrLiquidVolumeCurrentLast = mr.liquid_volume_current_last;
  double mrLiquidVolumeErrorLast = mr.liquid_volume_error_last;
  double mrCDivLast = mr.c_div_last;
  InterfaceDiagnostics3D mrInterfaceDiagnostics = mr.interface_diagnostics_last;
  SurfaceTensionStats3D mrSurfaceTensionStats = mr.surface_tension_stats_last;
  bool mrFinite = finiteParticles(mr.particles);
  int mrPressureCells = mr.activePressureCellCount();
  long long mrMs = std::chrono::duration_cast<std::chrono::milliseconds>(mrEnd - mrStart).count();
  size_t adaptiveMrN0 = mrN0;
  size_t adaptiveMrN1 = mr.particles.size();
  size_t adaptiveMrLiquid0 = mrLiquid0;
  size_t adaptiveMrLiquid1 = mrLiquid1;
  size_t adaptiveMrGasCount0 = mrGasCount0;
  size_t adaptiveMrGasCount1 = mrGasCount1;
  double adaptiveMrLiquidVolume0 = mrLiquidVolume0;
  double adaptiveMrLiquidVolume1 = mrLiquidVolume1;
  double adaptiveMrGasVolume0 = mrGasVolume0;
  double adaptiveMrGasVolume1 = mrGasVolume1;
  int adaptiveMrBoundaryClampedLiquidTotal = mrBoundaryClampedLiquidTotal;
  int adaptiveMrBoundaryClampedGasTotal = mrBoundaryClampedGasTotal;
  int adaptiveMrEscapedDropletCandidatesTotal = mrEscapedDropletCandidatesTotal;
  int adaptiveMrEscapedBubbleCandidatesTotal = mrEscapedBubbleCandidatesTotal;
  int adaptiveMrEscapedDropletsAddedTotal = mrEscapedDropletsAddedTotal;
  int adaptiveMrEscapedBubblesAddedTotal = mrEscapedBubblesAddedTotal;
  size_t adaptiveMrEscapedDropletParticles = mrEscapedDropletParticles;
  size_t adaptiveMrEscapedBubbleParticles = mrEscapedBubbleParticles;
  size_t adaptiveMrEscapedDropletAges = mrEscapedDropletAges;
  size_t adaptiveMrEscapedBubbleAges = mrEscapedBubbleAges;
  double adaptiveMrEscapedDropletVolumeAddedTotal =
    mrEscapedDropletVolumeAddedTotal;
  double adaptiveMrEscapedBubbleVolumeAddedTotal =
    mrEscapedBubbleVolumeAddedTotal;
  int adaptiveMrSecondaryLifecycleEnabled = mrSecondaryLifecycleEnabled;
  int adaptiveMrSecondaryLifecycleFinite = mrSecondaryLifecycleFinite;
  int adaptiveMrSecondaryDropletsAdvectedTotal =
    mrSecondaryDropletsAdvectedTotal;
  int adaptiveMrSecondaryBubblesAdvectedTotal =
    mrSecondaryBubblesAdvectedTotal;
  int adaptiveMrSecondaryDropletsReabsorbedTotal =
    mrSecondaryDropletsReabsorbedTotal;
  int adaptiveMrSecondaryBubblesReabsorbedTotal =
    mrSecondaryBubblesReabsorbedTotal;
  int adaptiveMrSecondaryDropletsExpiredTotal = mrSecondaryDropletsExpiredTotal;
  int adaptiveMrSecondaryBubblesExpiredTotal = mrSecondaryBubblesExpiredTotal;
  double adaptiveMrSecondaryDropletVolumeCurrent =
    mrSecondaryDropletVolumeCurrent;
  double adaptiveMrSecondaryBubbleVolumeCurrent = mrSecondaryBubbleVolumeCurrent;
  double adaptiveMrSecondaryDropletVolumeReabsorbedTotal =
    mrSecondaryDropletVolumeReabsorbedTotal;
  double adaptiveMrSecondaryBubbleVolumeReabsorbedTotal =
    mrSecondaryBubbleVolumeReabsorbedTotal;
  double adaptiveMrSecondaryDropletVolumeExpiredTotal =
    mrSecondaryDropletVolumeExpiredTotal;
  double adaptiveMrSecondaryBubbleVolumeExpiredTotal =
    mrSecondaryBubbleVolumeExpiredTotal;
  double adaptiveMrEffectiveDtLast = mrEffectiveDtLast;
  double adaptiveMrCflLimitDtLast = mrCflLimitDtLast;
  double adaptiveMrMaxParticleSpeedLast = mrMaxParticleSpeedLast;
  int adaptiveMrAdaptiveTimestepLimitedLast = mrAdaptiveTimestepLimitedLast;
  double adaptiveMrLiquidVolumeTarget = mrLiquidVolumeTarget;
  double adaptiveMrLiquidVolumeCurrentLast = mrLiquidVolumeCurrentLast;
  double adaptiveMrLiquidVolumeErrorLast = mrLiquidVolumeErrorLast;
  double adaptiveMrCDivLast = mrCDivLast;
  InterfaceDiagnostics3D adaptiveMrInterfaceDiagnostics = mrInterfaceDiagnostics;
  SurfaceTensionStats3D adaptiveMrSurfaceTensionStats = mrSurfaceTensionStats;
  int adaptiveMrLiquidRefillAdded0 = mr.liquid_particle_refill_added_total;
  int adaptiveMrLiquidRefillAdded1 = mr.liquid_particle_refill_added_total;
  int adaptiveMrLiquidRefillAddedDuringRun = 0;
  int adaptiveMrLiquidCoarseningRemoved0 = mr.liquid_particle_coarsening_removed_total;
  int adaptiveMrLiquidCoarseningRemoved1 = mr.liquid_particle_coarsening_removed_total;
  int adaptiveMrLiquidCoarseningRemovedDuringRun = 0;
  double adaptiveMrGas0 = mrGas0;
  double adaptiveMrGas1 = mrGas1;
  bool adaptiveMrFinite = mrFinite;
  int adaptiveMrPressureCells = mrPressureCells;
  long long adaptiveMrMs = mrMs;
  if (mrAdaptivity) {
    mrAdaptive.initBubbleTankInterfaceBand();
    if (liquidVolumeTargetOverride >= 0.0) {
      mrAdaptive.liquid_volume_target = liquidVolumeTargetOverride;
    }
    adaptiveMrN0 = mrAdaptive.particles.size();
    adaptiveMrLiquid0 = countType(mrAdaptive.particles, 0);
    adaptiveMrGasCount0 = countType(mrAdaptive.particles, 1);
    adaptiveMrLiquidVolume0 = volumeType(mrAdaptive.particles, 0, mrAdaptive.Vp);
    adaptiveMrGasVolume0 = volumeType(mrAdaptive.particles, 1, mrAdaptive.Vp);
    adaptiveMrLiquidCoarseningRemoved0 = mrAdaptive.liquid_particle_coarsening_removed_total;
    adaptiveMrLiquidRefillAdded0 = mrAdaptive.liquid_particle_refill_added_total;
    adaptiveMrGas0 = meanY(mrAdaptive.particles, 1);

    auto adaptiveMrStart = std::chrono::steady_clock::now();
    for (int s = 0; s < steps; ++s) {
      mrAdaptive.step();
    }
    auto adaptiveMrEnd = std::chrono::steady_clock::now();

    adaptiveMrN1 = mrAdaptive.particles.size();
    adaptiveMrLiquid1 = countType(mrAdaptive.particles, 0);
    adaptiveMrGasCount1 = countType(mrAdaptive.particles, 1);
    adaptiveMrLiquidVolume1 = volumeType(mrAdaptive.particles, 0, mrAdaptive.Vp);
    adaptiveMrGasVolume1 = volumeType(mrAdaptive.particles, 1, mrAdaptive.Vp);
    adaptiveMrBoundaryClampedLiquidTotal =
      mrAdaptive.particle_boundary_clamped_liquid_total;
    adaptiveMrBoundaryClampedGasTotal =
      mrAdaptive.particle_boundary_clamped_gas_total;
    adaptiveMrEscapedDropletCandidatesTotal =
      mrAdaptive.escaped_droplet_candidates_total;
    adaptiveMrEscapedBubbleCandidatesTotal =
      mrAdaptive.escaped_bubble_candidates_total;
    adaptiveMrEscapedDropletsAddedTotal =
      mrAdaptive.escaped_droplets_added_total;
    adaptiveMrEscapedBubblesAddedTotal =
      mrAdaptive.escaped_bubbles_added_total;
    adaptiveMrEscapedDropletParticles = mrAdaptive.escaped_droplets.size();
    adaptiveMrEscapedBubbleParticles = mrAdaptive.escaped_bubbles.size();
    adaptiveMrEscapedDropletAges = mrAdaptive.escaped_droplet_ages.size();
    adaptiveMrEscapedBubbleAges = mrAdaptive.escaped_bubble_ages.size();
    adaptiveMrEscapedDropletVolumeAddedTotal =
      mrAdaptive.escaped_droplet_volume_added_total;
    adaptiveMrEscapedBubbleVolumeAddedTotal =
      mrAdaptive.escaped_bubble_volume_added_total;
    adaptiveMrSecondaryLifecycleEnabled =
      mrAdaptive.secondary_lifecycle_stats_last.enabled;
    adaptiveMrSecondaryLifecycleFinite =
      mrAdaptive.secondary_lifecycle_stats_last.finite;
    adaptiveMrSecondaryDropletsAdvectedTotal =
      mrAdaptive.secondary_droplets_advected_total;
    adaptiveMrSecondaryBubblesAdvectedTotal =
      mrAdaptive.secondary_bubbles_advected_total;
    adaptiveMrSecondaryDropletsReabsorbedTotal =
      mrAdaptive.secondary_droplets_reabsorbed_total;
    adaptiveMrSecondaryBubblesReabsorbedTotal =
      mrAdaptive.secondary_bubbles_reabsorbed_total;
    adaptiveMrSecondaryDropletsExpiredTotal =
      mrAdaptive.secondary_droplets_expired_total;
    adaptiveMrSecondaryBubblesExpiredTotal =
      mrAdaptive.secondary_bubbles_expired_total;
    adaptiveMrSecondaryDropletVolumeCurrent =
      mrAdaptive.secondary_droplet_volume_current_last;
    adaptiveMrSecondaryBubbleVolumeCurrent =
      mrAdaptive.secondary_bubble_volume_current_last;
    adaptiveMrSecondaryDropletVolumeReabsorbedTotal =
      mrAdaptive.secondary_droplet_volume_reabsorbed_total;
    adaptiveMrSecondaryBubbleVolumeReabsorbedTotal =
      mrAdaptive.secondary_bubble_volume_reabsorbed_total;
    adaptiveMrSecondaryDropletVolumeExpiredTotal =
      mrAdaptive.secondary_droplet_volume_expired_total;
    adaptiveMrSecondaryBubbleVolumeExpiredTotal =
      mrAdaptive.secondary_bubble_volume_expired_total;
    adaptiveMrEffectiveDtLast = mrAdaptive.effective_dt_last;
    adaptiveMrCflLimitDtLast = mrAdaptive.cfl_limit_dt_last;
    adaptiveMrMaxParticleSpeedLast = mrAdaptive.max_particle_speed_last;
    adaptiveMrAdaptiveTimestepLimitedLast =
      mrAdaptive.adaptive_timestep_limited_last;
    adaptiveMrLiquidVolumeTarget = mrAdaptive.liquid_volume_target;
    adaptiveMrLiquidVolumeCurrentLast = mrAdaptive.liquid_volume_current_last;
    adaptiveMrLiquidVolumeErrorLast = mrAdaptive.liquid_volume_error_last;
    adaptiveMrCDivLast = mrAdaptive.c_div_last;
    adaptiveMrInterfaceDiagnostics = mrAdaptive.interface_diagnostics_last;
    adaptiveMrSurfaceTensionStats = mrAdaptive.surface_tension_stats_last;
    adaptiveMrLiquidCoarseningRemoved1 = mrAdaptive.liquid_particle_coarsening_removed_total;
    adaptiveMrLiquidCoarseningRemovedDuringRun =
      adaptiveMrLiquidCoarseningRemoved1 - adaptiveMrLiquidCoarseningRemoved0;
    adaptiveMrLiquidRefillAdded1 = mrAdaptive.liquid_particle_refill_added_total;
    adaptiveMrLiquidRefillAddedDuringRun =
      adaptiveMrLiquidRefillAdded1 - adaptiveMrLiquidRefillAdded0;
    adaptiveMrGas1 = meanY(mrAdaptive.particles, 1);
    adaptiveMrFinite = finiteParticles(mrAdaptive.particles);
    adaptiveMrPressureCells = mrAdaptive.activePressureCellCount();
    adaptiveMrMs = std::chrono::duration_cast<std::chrono::milliseconds>(
      adaptiveMrEnd - adaptiveMrStart).count();
  }
  int finePressureCells = nx * ny * nz;
  double pressureRatio = finePressureCells > 0 ? static_cast<double>(mrPressureCells) / finePressureCells : 0.0;
  double pressureReduction = 1.0 - pressureRatio;
  double sparseRise = sparseMetrics.gasEnd - sparseMetrics.gasStart;
  double adaptiveRise = adaptiveMetrics.gasEnd - adaptiveMetrics.gasStart;
  double mrRise = mrGas1 - mrGas0;
  double adaptiveMrRise = adaptiveMrGas1 - adaptiveMrGas0;
  double riseDelta = std::abs(mrRise - sparseRise);
  double allowedRiseDelta = std::max(0.35, std::abs(sparseRise) * 3.0);
  double adaptiveRiseDelta = sparseAdaptivity ? std::abs(adaptiveRise - sparseRise) : 0.0;
  double allowedAdaptiveRiseDelta =
    sparseAdaptivity ? std::max(0.35, std::abs(sparseRise) * 4.0) : 0.0;
  double adaptiveMrRiseDelta = mrAdaptivity ? std::abs(adaptiveMrRise - mrRise) : 0.0;
  double allowedAdaptiveMrRiseDelta =
    mrAdaptivity ? std::max(0.35, std::abs(mrRise) * 4.0) : 0.0;
  const MRPressureSolveStats3D& st = mr.last_pressure_stats;
  const double finalOverInitial = st.initial_residual > 0.0
    ? st.final_residual / st.initial_residual
    : 0.0;
  const bool pressureDiagFinite =
    std::isfinite(st.min_positive_diag) &&
    std::isfinite(st.max_diag) &&
    st.min_positive_diag > 0.0 &&
    st.max_diag >= st.min_positive_diag;
  const bool convergenceOk =
    !requireConverged ||
    steps == 0 ||
    (st.converged && st.final_residual <= st.effective_tolerance);
  const MRPressureSolveStats3D& adaptiveMrStats =
    mrAdaptivity ? mrAdaptive.last_pressure_stats : mr.last_pressure_stats;
  const bool adaptiveMrPressureDiagFinite =
    std::isfinite(adaptiveMrStats.min_positive_diag) &&
    std::isfinite(adaptiveMrStats.max_diag) &&
    adaptiveMrStats.min_positive_diag > 0.0 &&
    adaptiveMrStats.max_diag >= adaptiveMrStats.min_positive_diag;
  const bool adaptiveMrConvergenceOk =
    !requireConverged ||
    steps == 0 ||
    (adaptiveMrStats.converged &&
     adaptiveMrStats.final_residual <= adaptiveMrStats.effective_tolerance);

  std::printf("dims=%d,%d,%d\n", nx, ny, nz);
  std::printf("steps=%d\n", steps);
  std::printf("physics_preset=%s\n", physicsPreset ? "true" : "false");
  std::printf("long_physics_preset=%s\n", longPhysicsPreset ? "true" : "false");
  std::printf("dt=%.9g\n", dt);
  std::printf("adaptive_timestep=%s\n", adaptiveTimestep ? "true" : "false");
  std::printf("adaptive_cfl=%.9g\n", adaptiveCfl);
  std::printf("adaptive_min_dt=%.9g\n", adaptiveMinDt);
  std::printf("advection_order=%d\n", advectionOrder);
  std::printf("c_div_volume_correction=%s\n",
              cDivVolumeCorrection ? "true" : "false");
  std::printf("c_div_strength=%.9g\n", cDivStrength);
  std::printf("liquid_volume_target_override=%.9g\n", liquidVolumeTargetOverride);
  std::printf("surface_tension=%s\n", surfaceTension ? "true" : "false");
  std::printf("surface_tension_strength=%.9g\n", surfaceTensionStrength);
  std::printf("surface_tension_max_delta_speed=%.9g\n",
              surfaceTensionMaxDeltaSpeed);
  std::printf("escaped_particle_branching=%s\n",
              escapedParticleBranching ? "true" : "false");
  std::printf("secondary_particle_lifecycle=%s\n",
              secondaryLifecycle ? "true" : "false");
  std::printf("secondary_droplet_lifetime_steps=%d\n",
              secondaryDropletLifetime);
  std::printf("secondary_bubble_lifetime_steps=%d\n",
              secondaryBubbleLifetime);
  std::printf("secondary_velocity_damping=%.9g\n",
              secondaryVelocityDamping);
  std::printf("secondary_reabsorb_margin_cells=%.9g\n",
              secondaryReabsorbMargin);
  std::printf("secondary_bubble_buoyancy_scale=%.9g\n",
              secondaryBubbleBuoyancyScale);
  std::printf("rho_l=%.9g\n", mr.phase.rho_l);
  std::printf("rho_g=%.9g\n", mr.phase.rho_g);
  std::printf("rho_ratio=%.9g\n", activeRhoRatio);
  std::printf("high_density_ratio=%s\n", highDensityRatio ? "true" : "false");
  std::printf("require_converged=%s\n", requireConverged ? "true" : "false");
  std::printf("cg_iters=%d\n", cgIters);
  std::printf("sparse_adaptivity=%s\n", sparseAdaptivity ? "true" : "false");
  std::printf("sparse_narrow_band_air=%s\n",
              sparseAdaptive.narrow_band_air ? "true" : "false");
  std::printf("sparse_narrow_band_radius=%d\n",
              sparseAdaptive.narrow_band_air_radius);
  std::printf("sparse_gas_coarsening=%s\n",
              sparseAdaptive.gas_particle_coarsening ? "true" : "false");
  std::printf("sparse_gas_particles_per_cell=%d\n",
              sparseAdaptive.gas_particles_per_cell_target);
  std::printf("sparse_gas_coarsening_seed=%u\n",
              sparseAdaptive.gas_particle_coarsening_seed);
  std::printf("sparse_liquid_coarsening=%s\n",
              sparseAdaptive.liquid_particle_coarsening ? "true" : "false");
  std::printf("sparse_liquid_particles_per_cell=%d\n",
              sparseAdaptive.liquid_particles_per_cell_target);
  std::printf("sparse_liquid_coarsening_seed=%u\n",
              sparseAdaptive.liquid_particle_coarsening_seed);
  std::printf("sparse_liquid_refill=%s\n",
              sparseAdaptive.liquid_particle_refill ? "true" : "false");
  std::printf("sparse_liquid_refill_particles_per_cell=%d\n",
              sparseAdaptive.liquid_refill_particles_per_cell_target);
  std::printf("sparse_liquid_refill_seed=%u\n",
              sparseAdaptive.liquid_particle_refill_seed);
  std::printf("sparse_liquid_refill_max_added_per_step=%d\n",
              sparseAdaptive.liquid_particle_refill_max_added_per_step);
  std::printf("sparse_liquid_refill_interface_only=%s\n",
              sparseAdaptive.liquid_particle_refill_interface_only ? "true" : "false");
  std::printf("sparse_liquid_refill_interface_radius=%d\n",
              sparseAdaptive.liquid_particle_refill_interface_radius);
  std::printf("mr_adaptivity=%s\n", mrAdaptivity ? "true" : "false");
  std::printf("mr_narrow_band_air=%s\n",
              mrAdaptive.narrow_band_air ? "true" : "false");
  std::printf("mr_narrow_band_radius=%d\n",
              mrAdaptive.narrow_band_air_radius);
  std::printf("mr_gas_coarsening=%s\n",
              mrAdaptive.gas_particle_coarsening ? "true" : "false");
  std::printf("mr_gas_particles_per_cell=%d\n",
              mrAdaptive.gas_particles_per_cell_target);
  std::printf("mr_gas_coarsening_seed=%u\n",
              mrAdaptive.gas_particle_coarsening_seed);
  std::printf("mr_liquid_coarsening=%s\n",
              mrAdaptive.liquid_particle_coarsening ? "true" : "false");
  std::printf("mr_liquid_particles_per_cell=%d\n",
              mrAdaptive.liquid_particles_per_cell_target);
  std::printf("mr_liquid_coarsening_seed=%u\n",
              mrAdaptive.liquid_particle_coarsening_seed);
  std::printf("mr_liquid_refill=%s\n",
              mrAdaptive.liquid_particle_refill ? "true" : "false");
  std::printf("mr_liquid_refill_particles_per_cell=%d\n",
              mrAdaptive.liquid_refill_particles_per_cell_target);
  std::printf("mr_liquid_refill_seed=%u\n",
              mrAdaptive.liquid_particle_refill_seed);
  std::printf("mr_liquid_refill_max_added_per_step=%d\n",
              mrAdaptive.liquid_particle_refill_max_added_per_step);
  std::printf("mr_liquid_refill_interface_only=%s\n",
              mrAdaptive.liquid_particle_refill_interface_only ? "true" : "false");
  std::printf("mr_liquid_refill_interface_radius=%d\n",
              mrAdaptive.liquid_particle_refill_interface_radius);
  std::printf("mr_cg_tol=%.9g\n", mr.cg_tol);
  std::printf("mr_cg_rel_tol=%.9g\n", mr.cg_rel_tol);
  std::printf("mr_cg_jacobi_preconditioner=%s\n", mr.cg_jacobi_preconditioner ? "true" : "false");
  std::printf("mr_cg_flexible_beta=%s\n", mr.cg_flexible_beta ? "true" : "false");
  std::printf("mr_cg_adaptive_restart=%s\n", mr.cg_adaptive_restart ? "true" : "false");
  std::printf("mr_cg_restart_growth=%.9g\n", mr.cg_restart_growth);
  std::printf("mr_cg_relaxation_sweeps=%d\n", mr.cg_relaxation_sweeps);
  std::printf("mr_cg_relaxation_omega=%.9g\n", mr.cg_relaxation_omega);
  std::printf("mr_cg_relaxation_min_omega=%.9g\n", mr.cg_relaxation_min_omega);
  std::printf("mr_cg_residual_history_stride=%d\n", mr.cg_residual_history_stride);
  std::printf("mr_cg_residual_history_limit=%d\n", mr.cg_residual_history_limit);
  std::printf("sparse_particles_start=%zu\n", sparseMetrics.particlesStart);
  std::printf("sparse_particles_end=%zu\n", sparseMetrics.particlesEnd);
  std::printf("adaptive_sparse_particles_start=%zu\n", adaptiveMetrics.particlesStart);
  std::printf("adaptive_sparse_particles_end=%zu\n", adaptiveMetrics.particlesEnd);
  std::printf("mr_particles_start=%zu\n", mrN0);
  std::printf("mr_particles_end=%zu\n", mr.particles.size());
  std::printf("adaptive_mr_particles_start=%zu\n", adaptiveMrN0);
  std::printf("adaptive_mr_particles_end=%zu\n", adaptiveMrN1);
  std::printf("sparse_liquid_particles_start=%zu\n", sparseMetrics.liquidStart);
  std::printf("sparse_liquid_particles_end=%zu\n", sparseMetrics.liquidEnd);
  std::printf("sparse_gas_particles_start=%zu\n", sparseMetrics.gasCountStart);
  std::printf("sparse_gas_particles_end=%zu\n", sparseMetrics.gasCountEnd);
  std::printf("adaptive_sparse_liquid_particles_start=%zu\n", adaptiveMetrics.liquidStart);
  std::printf("adaptive_sparse_liquid_particles_end=%zu\n", adaptiveMetrics.liquidEnd);
  std::printf("adaptive_sparse_gas_particles_start=%zu\n", adaptiveMetrics.gasCountStart);
  std::printf("adaptive_sparse_gas_particles_end=%zu\n", adaptiveMetrics.gasCountEnd);
  std::printf("sparse_liquid_volume_start=%.9g\n", sparseMetrics.liquidVolumeStart);
  std::printf("sparse_liquid_volume_end=%.9g\n", sparseMetrics.liquidVolumeEnd);
  std::printf("sparse_gas_volume_start=%.9g\n", sparseMetrics.gasVolumeStart);
  std::printf("sparse_gas_volume_end=%.9g\n", sparseMetrics.gasVolumeEnd);
  std::printf("adaptive_sparse_liquid_volume_start=%.9g\n", adaptiveMetrics.liquidVolumeStart);
  std::printf("adaptive_sparse_liquid_volume_end=%.9g\n", adaptiveMetrics.liquidVolumeEnd);
  std::printf("adaptive_sparse_gas_volume_start=%.9g\n", adaptiveMetrics.gasVolumeStart);
  std::printf("adaptive_sparse_gas_volume_end=%.9g\n", adaptiveMetrics.gasVolumeEnd);
  std::printf("sparse_boundary_clamped_liquid_total=%d\n",
              sparseMetrics.boundaryClampedLiquidTotal);
  std::printf("sparse_boundary_clamped_gas_total=%d\n",
              sparseMetrics.boundaryClampedGasTotal);
  std::printf("adaptive_sparse_boundary_clamped_liquid_total=%d\n",
              adaptiveMetrics.boundaryClampedLiquidTotal);
  std::printf("adaptive_sparse_boundary_clamped_gas_total=%d\n",
              adaptiveMetrics.boundaryClampedGasTotal);
  std::printf("sparse_escaped_droplet_candidates_total=%d\n",
              sparseMetrics.escapedDropletCandidatesTotal);
  std::printf("sparse_escaped_bubble_candidates_total=%d\n",
              sparseMetrics.escapedBubbleCandidatesTotal);
  std::printf("adaptive_sparse_escaped_droplet_candidates_total=%d\n",
              adaptiveMetrics.escapedDropletCandidatesTotal);
  std::printf("adaptive_sparse_escaped_bubble_candidates_total=%d\n",
              adaptiveMetrics.escapedBubbleCandidatesTotal);
  std::printf("sparse_escaped_droplets_added_total=%d\n",
              sparseMetrics.escapedDropletsAddedTotal);
  std::printf("sparse_escaped_bubbles_added_total=%d\n",
              sparseMetrics.escapedBubblesAddedTotal);
  std::printf("sparse_escaped_droplet_particles=%zu\n",
              sparseMetrics.escapedDropletParticles);
  std::printf("sparse_escaped_bubble_particles=%zu\n",
              sparseMetrics.escapedBubbleParticles);
  std::printf("sparse_escaped_droplet_ages=%zu\n",
              sparseMetrics.escapedDropletAges);
  std::printf("sparse_escaped_bubble_ages=%zu\n",
              sparseMetrics.escapedBubbleAges);
  std::printf("sparse_escaped_droplet_volume_added_total=%.9g\n",
              sparseMetrics.escapedDropletVolumeAddedTotal);
  std::printf("sparse_escaped_bubble_volume_added_total=%.9g\n",
              sparseMetrics.escapedBubbleVolumeAddedTotal);
  std::printf("sparse_secondary_lifecycle_enabled=%s\n",
              sparseMetrics.secondaryLifecycleEnabled ? "true" : "false");
  std::printf("sparse_secondary_lifecycle_finite=%s\n",
              sparseMetrics.secondaryLifecycleFinite ? "true" : "false");
  std::printf("sparse_secondary_droplets_advected_total=%d\n",
              sparseMetrics.secondaryDropletsAdvectedTotal);
  std::printf("sparse_secondary_bubbles_advected_total=%d\n",
              sparseMetrics.secondaryBubblesAdvectedTotal);
  std::printf("sparse_secondary_droplets_reabsorbed_total=%d\n",
              sparseMetrics.secondaryDropletsReabsorbedTotal);
  std::printf("sparse_secondary_bubbles_reabsorbed_total=%d\n",
              sparseMetrics.secondaryBubblesReabsorbedTotal);
  std::printf("sparse_secondary_droplets_expired_total=%d\n",
              sparseMetrics.secondaryDropletsExpiredTotal);
  std::printf("sparse_secondary_bubbles_expired_total=%d\n",
              sparseMetrics.secondaryBubblesExpiredTotal);
  std::printf("sparse_secondary_droplet_volume_current=%.9g\n",
              sparseMetrics.secondaryDropletVolumeCurrent);
  std::printf("sparse_secondary_bubble_volume_current=%.9g\n",
              sparseMetrics.secondaryBubbleVolumeCurrent);
  std::printf("sparse_secondary_droplet_volume_reabsorbed_total=%.9g\n",
              sparseMetrics.secondaryDropletVolumeReabsorbedTotal);
  std::printf("sparse_secondary_bubble_volume_reabsorbed_total=%.9g\n",
              sparseMetrics.secondaryBubbleVolumeReabsorbedTotal);
  std::printf("sparse_secondary_droplet_volume_expired_total=%.9g\n",
              sparseMetrics.secondaryDropletVolumeExpiredTotal);
  std::printf("sparse_secondary_bubble_volume_expired_total=%.9g\n",
              sparseMetrics.secondaryBubbleVolumeExpiredTotal);
  std::printf("adaptive_sparse_escaped_droplets_added_total=%d\n",
              adaptiveMetrics.escapedDropletsAddedTotal);
  std::printf("adaptive_sparse_escaped_bubbles_added_total=%d\n",
              adaptiveMetrics.escapedBubblesAddedTotal);
  std::printf("adaptive_sparse_escaped_droplet_particles=%zu\n",
              adaptiveMetrics.escapedDropletParticles);
  std::printf("adaptive_sparse_escaped_bubble_particles=%zu\n",
              adaptiveMetrics.escapedBubbleParticles);
  std::printf("adaptive_sparse_escaped_droplet_ages=%zu\n",
              adaptiveMetrics.escapedDropletAges);
  std::printf("adaptive_sparse_escaped_bubble_ages=%zu\n",
              adaptiveMetrics.escapedBubbleAges);
  std::printf("adaptive_sparse_escaped_droplet_volume_added_total=%.9g\n",
              adaptiveMetrics.escapedDropletVolumeAddedTotal);
  std::printf("adaptive_sparse_escaped_bubble_volume_added_total=%.9g\n",
              adaptiveMetrics.escapedBubbleVolumeAddedTotal);
  std::printf("adaptive_sparse_secondary_lifecycle_enabled=%s\n",
              adaptiveMetrics.secondaryLifecycleEnabled ? "true" : "false");
  std::printf("adaptive_sparse_secondary_lifecycle_finite=%s\n",
              adaptiveMetrics.secondaryLifecycleFinite ? "true" : "false");
  std::printf("adaptive_sparse_secondary_droplets_advected_total=%d\n",
              adaptiveMetrics.secondaryDropletsAdvectedTotal);
  std::printf("adaptive_sparse_secondary_bubbles_advected_total=%d\n",
              adaptiveMetrics.secondaryBubblesAdvectedTotal);
  std::printf("adaptive_sparse_secondary_droplets_reabsorbed_total=%d\n",
              adaptiveMetrics.secondaryDropletsReabsorbedTotal);
  std::printf("adaptive_sparse_secondary_bubbles_reabsorbed_total=%d\n",
              adaptiveMetrics.secondaryBubblesReabsorbedTotal);
  std::printf("adaptive_sparse_secondary_droplets_expired_total=%d\n",
              adaptiveMetrics.secondaryDropletsExpiredTotal);
  std::printf("adaptive_sparse_secondary_bubbles_expired_total=%d\n",
              adaptiveMetrics.secondaryBubblesExpiredTotal);
  std::printf("adaptive_sparse_secondary_droplet_volume_current=%.9g\n",
              adaptiveMetrics.secondaryDropletVolumeCurrent);
  std::printf("adaptive_sparse_secondary_bubble_volume_current=%.9g\n",
              adaptiveMetrics.secondaryBubbleVolumeCurrent);
  std::printf("adaptive_sparse_secondary_droplet_volume_reabsorbed_total=%.9g\n",
              adaptiveMetrics.secondaryDropletVolumeReabsorbedTotal);
  std::printf("adaptive_sparse_secondary_bubble_volume_reabsorbed_total=%.9g\n",
              adaptiveMetrics.secondaryBubbleVolumeReabsorbedTotal);
  std::printf("adaptive_sparse_secondary_droplet_volume_expired_total=%.9g\n",
              adaptiveMetrics.secondaryDropletVolumeExpiredTotal);
  std::printf("adaptive_sparse_secondary_bubble_volume_expired_total=%.9g\n",
              adaptiveMetrics.secondaryBubbleVolumeExpiredTotal);
  std::printf("sparse_effective_dt_last=%.9g\n", sparseMetrics.effectiveDtLast);
  std::printf("sparse_cfl_limit_dt_last=%.9g\n", sparseMetrics.cflLimitDtLast);
  std::printf("sparse_max_particle_speed_last=%.9g\n",
              sparseMetrics.maxParticleSpeedLast);
  std::printf("sparse_adaptive_timestep_limited_last=%d\n",
              sparseMetrics.adaptiveTimestepLimitedLast);
  std::printf("adaptive_sparse_effective_dt_last=%.9g\n",
              adaptiveMetrics.effectiveDtLast);
  std::printf("adaptive_sparse_cfl_limit_dt_last=%.9g\n",
              adaptiveMetrics.cflLimitDtLast);
  std::printf("adaptive_sparse_max_particle_speed_last=%.9g\n",
              adaptiveMetrics.maxParticleSpeedLast);
  std::printf("adaptive_sparse_adaptive_timestep_limited_last=%d\n",
              adaptiveMetrics.adaptiveTimestepLimitedLast);
  std::printf("sparse_liquid_volume_target=%.9g\n", sparseMetrics.liquidVolumeTarget);
  std::printf("sparse_liquid_volume_current_last=%.9g\n",
              sparseMetrics.liquidVolumeCurrentLast);
  std::printf("sparse_liquid_volume_error_last=%.9g\n",
              sparseMetrics.liquidVolumeErrorLast);
  std::printf("sparse_c_div_last=%.9g\n", sparseMetrics.cDivLast);
  std::printf("adaptive_sparse_liquid_volume_target=%.9g\n",
              adaptiveMetrics.liquidVolumeTarget);
  std::printf("adaptive_sparse_liquid_volume_current_last=%.9g\n",
              adaptiveMetrics.liquidVolumeCurrentLast);
  std::printf("adaptive_sparse_liquid_volume_error_last=%.9g\n",
              adaptiveMetrics.liquidVolumeErrorLast);
  std::printf("adaptive_sparse_c_div_last=%.9g\n", adaptiveMetrics.cDivLast);
  std::printf("sparse_interface_sample_cells=%d\n",
              sparseMetrics.interfaceDiagnostics.sample_cells);
  std::printf("sparse_interface_cells=%d\n",
              sparseMetrics.interfaceDiagnostics.interface_cells);
  std::printf("sparse_interface_grad_max=%.9g\n",
              sparseMetrics.interfaceDiagnostics.grad_max);
  std::printf("sparse_interface_curvature_abs_max=%.9g\n",
              sparseMetrics.interfaceDiagnostics.curvature_abs_max);
  std::printf("sparse_interface_diagnostics_finite=%s\n",
              sparseMetrics.interfaceDiagnostics.finite ? "true" : "false");
  std::printf("sparse_surface_tension_candidate=%s\n",
              sparseMetrics.interfaceDiagnostics.surface_tension_candidate ? "true" : "false");
  std::printf("adaptive_sparse_interface_sample_cells=%d\n",
              adaptiveMetrics.interfaceDiagnostics.sample_cells);
  std::printf("adaptive_sparse_interface_cells=%d\n",
              adaptiveMetrics.interfaceDiagnostics.interface_cells);
  std::printf("adaptive_sparse_interface_grad_max=%.9g\n",
              adaptiveMetrics.interfaceDiagnostics.grad_max);
  std::printf("adaptive_sparse_interface_curvature_abs_max=%.9g\n",
              adaptiveMetrics.interfaceDiagnostics.curvature_abs_max);
  std::printf("adaptive_sparse_interface_diagnostics_finite=%s\n",
              adaptiveMetrics.interfaceDiagnostics.finite ? "true" : "false");
  std::printf("adaptive_sparse_surface_tension_candidate=%s\n",
              adaptiveMetrics.interfaceDiagnostics.surface_tension_candidate ? "true" : "false");
  std::printf("sparse_surface_tension_enabled=%s\n",
              sparseMetrics.surfaceTensionStats.enabled ? "true" : "false");
  std::printf("sparse_surface_tension_applied_cells=%d\n",
              sparseMetrics.surfaceTensionStats.applied_cells);
  std::printf("sparse_surface_tension_force_finite=%s\n",
              sparseMetrics.surfaceTensionStats.finite ? "true" : "false");
  std::printf("sparse_surface_tension_max_delta_speed_last=%.9g\n",
              sparseMetrics.surfaceTensionStats.max_delta_speed);
  std::printf("adaptive_sparse_surface_tension_enabled=%s\n",
              adaptiveMetrics.surfaceTensionStats.enabled ? "true" : "false");
  std::printf("adaptive_sparse_surface_tension_applied_cells=%d\n",
              adaptiveMetrics.surfaceTensionStats.applied_cells);
  std::printf("adaptive_sparse_surface_tension_force_finite=%s\n",
              adaptiveMetrics.surfaceTensionStats.finite ? "true" : "false");
  std::printf("adaptive_sparse_surface_tension_max_delta_speed_last=%.9g\n",
              adaptiveMetrics.surfaceTensionStats.max_delta_speed);
  std::printf("mr_liquid_particles_start=%zu\n", mrLiquid0);
  std::printf("mr_liquid_particles_end=%zu\n", mrLiquid1);
  std::printf("mr_gas_particles_start=%zu\n", mrGasCount0);
  std::printf("mr_gas_particles_end=%zu\n", mrGasCount1);
  std::printf("adaptive_mr_liquid_particles_start=%zu\n", adaptiveMrLiquid0);
  std::printf("adaptive_mr_liquid_particles_end=%zu\n", adaptiveMrLiquid1);
  std::printf("adaptive_mr_gas_particles_start=%zu\n", adaptiveMrGasCount0);
  std::printf("adaptive_mr_gas_particles_end=%zu\n", adaptiveMrGasCount1);
  std::printf("mr_liquid_volume_start=%.9g\n", mrLiquidVolume0);
  std::printf("mr_liquid_volume_end=%.9g\n", mrLiquidVolume1);
  std::printf("mr_gas_volume_start=%.9g\n", mrGasVolume0);
  std::printf("mr_gas_volume_end=%.9g\n", mrGasVolume1);
  std::printf("adaptive_mr_liquid_volume_start=%.9g\n", adaptiveMrLiquidVolume0);
  std::printf("adaptive_mr_liquid_volume_end=%.9g\n", adaptiveMrLiquidVolume1);
  std::printf("adaptive_mr_gas_volume_start=%.9g\n", adaptiveMrGasVolume0);
  std::printf("adaptive_mr_gas_volume_end=%.9g\n", adaptiveMrGasVolume1);
  std::printf("mr_boundary_clamped_liquid_total=%d\n",
              mrBoundaryClampedLiquidTotal);
  std::printf("mr_boundary_clamped_gas_total=%d\n",
              mrBoundaryClampedGasTotal);
  std::printf("adaptive_mr_boundary_clamped_liquid_total=%d\n",
              adaptiveMrBoundaryClampedLiquidTotal);
  std::printf("adaptive_mr_boundary_clamped_gas_total=%d\n",
              adaptiveMrBoundaryClampedGasTotal);
  std::printf("mr_escaped_droplet_candidates_total=%d\n",
              mrEscapedDropletCandidatesTotal);
  std::printf("mr_escaped_bubble_candidates_total=%d\n",
              mrEscapedBubbleCandidatesTotal);
  std::printf("adaptive_mr_escaped_droplet_candidates_total=%d\n",
              adaptiveMrEscapedDropletCandidatesTotal);
  std::printf("adaptive_mr_escaped_bubble_candidates_total=%d\n",
              adaptiveMrEscapedBubbleCandidatesTotal);
  std::printf("mr_escaped_droplets_added_total=%d\n",
              mrEscapedDropletsAddedTotal);
  std::printf("mr_escaped_bubbles_added_total=%d\n",
              mrEscapedBubblesAddedTotal);
  std::printf("mr_escaped_droplet_particles=%zu\n",
              mrEscapedDropletParticles);
  std::printf("mr_escaped_bubble_particles=%zu\n",
              mrEscapedBubbleParticles);
  std::printf("mr_escaped_droplet_ages=%zu\n", mrEscapedDropletAges);
  std::printf("mr_escaped_bubble_ages=%zu\n", mrEscapedBubbleAges);
  std::printf("mr_escaped_droplet_volume_added_total=%.9g\n",
              mrEscapedDropletVolumeAddedTotal);
  std::printf("mr_escaped_bubble_volume_added_total=%.9g\n",
              mrEscapedBubbleVolumeAddedTotal);
  std::printf("mr_secondary_lifecycle_enabled=%s\n",
              mrSecondaryLifecycleEnabled ? "true" : "false");
  std::printf("mr_secondary_lifecycle_finite=%s\n",
              mrSecondaryLifecycleFinite ? "true" : "false");
  std::printf("mr_secondary_droplets_advected_total=%d\n",
              mrSecondaryDropletsAdvectedTotal);
  std::printf("mr_secondary_bubbles_advected_total=%d\n",
              mrSecondaryBubblesAdvectedTotal);
  std::printf("mr_secondary_droplets_reabsorbed_total=%d\n",
              mrSecondaryDropletsReabsorbedTotal);
  std::printf("mr_secondary_bubbles_reabsorbed_total=%d\n",
              mrSecondaryBubblesReabsorbedTotal);
  std::printf("mr_secondary_droplets_expired_total=%d\n",
              mrSecondaryDropletsExpiredTotal);
  std::printf("mr_secondary_bubbles_expired_total=%d\n",
              mrSecondaryBubblesExpiredTotal);
  std::printf("mr_secondary_droplet_volume_current=%.9g\n",
              mrSecondaryDropletVolumeCurrent);
  std::printf("mr_secondary_bubble_volume_current=%.9g\n",
              mrSecondaryBubbleVolumeCurrent);
  std::printf("mr_secondary_droplet_volume_reabsorbed_total=%.9g\n",
              mrSecondaryDropletVolumeReabsorbedTotal);
  std::printf("mr_secondary_bubble_volume_reabsorbed_total=%.9g\n",
              mrSecondaryBubbleVolumeReabsorbedTotal);
  std::printf("mr_secondary_droplet_volume_expired_total=%.9g\n",
              mrSecondaryDropletVolumeExpiredTotal);
  std::printf("mr_secondary_bubble_volume_expired_total=%.9g\n",
              mrSecondaryBubbleVolumeExpiredTotal);
  std::printf("adaptive_mr_escaped_droplets_added_total=%d\n",
              adaptiveMrEscapedDropletsAddedTotal);
  std::printf("adaptive_mr_escaped_bubbles_added_total=%d\n",
              adaptiveMrEscapedBubblesAddedTotal);
  std::printf("adaptive_mr_escaped_droplet_particles=%zu\n",
              adaptiveMrEscapedDropletParticles);
  std::printf("adaptive_mr_escaped_bubble_particles=%zu\n",
              adaptiveMrEscapedBubbleParticles);
  std::printf("adaptive_mr_escaped_droplet_ages=%zu\n",
              adaptiveMrEscapedDropletAges);
  std::printf("adaptive_mr_escaped_bubble_ages=%zu\n",
              adaptiveMrEscapedBubbleAges);
  std::printf("adaptive_mr_escaped_droplet_volume_added_total=%.9g\n",
              adaptiveMrEscapedDropletVolumeAddedTotal);
  std::printf("adaptive_mr_escaped_bubble_volume_added_total=%.9g\n",
              adaptiveMrEscapedBubbleVolumeAddedTotal);
  std::printf("adaptive_mr_secondary_lifecycle_enabled=%s\n",
              adaptiveMrSecondaryLifecycleEnabled ? "true" : "false");
  std::printf("adaptive_mr_secondary_lifecycle_finite=%s\n",
              adaptiveMrSecondaryLifecycleFinite ? "true" : "false");
  std::printf("adaptive_mr_secondary_droplets_advected_total=%d\n",
              adaptiveMrSecondaryDropletsAdvectedTotal);
  std::printf("adaptive_mr_secondary_bubbles_advected_total=%d\n",
              adaptiveMrSecondaryBubblesAdvectedTotal);
  std::printf("adaptive_mr_secondary_droplets_reabsorbed_total=%d\n",
              adaptiveMrSecondaryDropletsReabsorbedTotal);
  std::printf("adaptive_mr_secondary_bubbles_reabsorbed_total=%d\n",
              adaptiveMrSecondaryBubblesReabsorbedTotal);
  std::printf("adaptive_mr_secondary_droplets_expired_total=%d\n",
              adaptiveMrSecondaryDropletsExpiredTotal);
  std::printf("adaptive_mr_secondary_bubbles_expired_total=%d\n",
              adaptiveMrSecondaryBubblesExpiredTotal);
  std::printf("adaptive_mr_secondary_droplet_volume_current=%.9g\n",
              adaptiveMrSecondaryDropletVolumeCurrent);
  std::printf("adaptive_mr_secondary_bubble_volume_current=%.9g\n",
              adaptiveMrSecondaryBubbleVolumeCurrent);
  std::printf("adaptive_mr_secondary_droplet_volume_reabsorbed_total=%.9g\n",
              adaptiveMrSecondaryDropletVolumeReabsorbedTotal);
  std::printf("adaptive_mr_secondary_bubble_volume_reabsorbed_total=%.9g\n",
              adaptiveMrSecondaryBubbleVolumeReabsorbedTotal);
  std::printf("adaptive_mr_secondary_droplet_volume_expired_total=%.9g\n",
              adaptiveMrSecondaryDropletVolumeExpiredTotal);
  std::printf("adaptive_mr_secondary_bubble_volume_expired_total=%.9g\n",
              adaptiveMrSecondaryBubbleVolumeExpiredTotal);
  std::printf("mr_effective_dt_last=%.9g\n", mrEffectiveDtLast);
  std::printf("mr_cfl_limit_dt_last=%.9g\n", mrCflLimitDtLast);
  std::printf("mr_max_particle_speed_last=%.9g\n", mrMaxParticleSpeedLast);
  std::printf("mr_adaptive_timestep_limited_last=%d\n",
              mrAdaptiveTimestepLimitedLast);
  std::printf("adaptive_mr_effective_dt_last=%.9g\n", adaptiveMrEffectiveDtLast);
  std::printf("adaptive_mr_cfl_limit_dt_last=%.9g\n", adaptiveMrCflLimitDtLast);
  std::printf("adaptive_mr_max_particle_speed_last=%.9g\n",
              adaptiveMrMaxParticleSpeedLast);
  std::printf("adaptive_mr_adaptive_timestep_limited_last=%d\n",
              adaptiveMrAdaptiveTimestepLimitedLast);
  std::printf("mr_liquid_volume_target=%.9g\n", mrLiquidVolumeTarget);
  std::printf("mr_liquid_volume_current_last=%.9g\n", mrLiquidVolumeCurrentLast);
  std::printf("mr_liquid_volume_error_last=%.9g\n", mrLiquidVolumeErrorLast);
  std::printf("mr_c_div_last=%.9g\n", mrCDivLast);
  std::printf("adaptive_mr_liquid_volume_target=%.9g\n",
              adaptiveMrLiquidVolumeTarget);
  std::printf("adaptive_mr_liquid_volume_current_last=%.9g\n",
              adaptiveMrLiquidVolumeCurrentLast);
  std::printf("adaptive_mr_liquid_volume_error_last=%.9g\n",
              adaptiveMrLiquidVolumeErrorLast);
  std::printf("adaptive_mr_c_div_last=%.9g\n", adaptiveMrCDivLast);
  std::printf("mr_interface_sample_cells=%d\n",
              mrInterfaceDiagnostics.sample_cells);
  std::printf("mr_interface_cells=%d\n",
              mrInterfaceDiagnostics.interface_cells);
  std::printf("mr_interface_grad_max=%.9g\n",
              mrInterfaceDiagnostics.grad_max);
  std::printf("mr_interface_curvature_abs_max=%.9g\n",
              mrInterfaceDiagnostics.curvature_abs_max);
  std::printf("mr_interface_diagnostics_finite=%s\n",
              mrInterfaceDiagnostics.finite ? "true" : "false");
  std::printf("mr_surface_tension_candidate=%s\n",
              mrInterfaceDiagnostics.surface_tension_candidate ? "true" : "false");
  std::printf("adaptive_mr_interface_sample_cells=%d\n",
              adaptiveMrInterfaceDiagnostics.sample_cells);
  std::printf("adaptive_mr_interface_cells=%d\n",
              adaptiveMrInterfaceDiagnostics.interface_cells);
  std::printf("adaptive_mr_interface_grad_max=%.9g\n",
              adaptiveMrInterfaceDiagnostics.grad_max);
  std::printf("adaptive_mr_interface_curvature_abs_max=%.9g\n",
              adaptiveMrInterfaceDiagnostics.curvature_abs_max);
  std::printf("adaptive_mr_interface_diagnostics_finite=%s\n",
              adaptiveMrInterfaceDiagnostics.finite ? "true" : "false");
  std::printf("adaptive_mr_surface_tension_candidate=%s\n",
              adaptiveMrInterfaceDiagnostics.surface_tension_candidate ? "true" : "false");
  std::printf("mr_surface_tension_enabled=%s\n",
              mrSurfaceTensionStats.enabled ? "true" : "false");
  std::printf("mr_surface_tension_applied_cells=%d\n",
              mrSurfaceTensionStats.applied_cells);
  std::printf("mr_surface_tension_force_finite=%s\n",
              mrSurfaceTensionStats.finite ? "true" : "false");
  std::printf("mr_surface_tension_max_delta_speed_last=%.9g\n",
              mrSurfaceTensionStats.max_delta_speed);
  std::printf("adaptive_mr_surface_tension_enabled=%s\n",
              adaptiveMrSurfaceTensionStats.enabled ? "true" : "false");
  std::printf("adaptive_mr_surface_tension_applied_cells=%d\n",
              adaptiveMrSurfaceTensionStats.applied_cells);
  std::printf("adaptive_mr_surface_tension_force_finite=%s\n",
              adaptiveMrSurfaceTensionStats.finite ? "true" : "false");
  std::printf("adaptive_mr_surface_tension_max_delta_speed_last=%.9g\n",
              adaptiveMrSurfaceTensionStats.max_delta_speed);
  std::printf("sparse_finite=%s\n", sparseMetrics.finite ? "true" : "false");
  std::printf("adaptive_sparse_finite=%s\n",
              adaptiveMetrics.finite ? "true" : "false");
  std::printf("mr_finite=%s\n", mrFinite ? "true" : "false");
  std::printf("adaptive_mr_finite=%s\n", adaptiveMrFinite ? "true" : "false");
  std::printf("sparse_gas_mean_y_start=%.9g\n", sparseMetrics.gasStart);
  std::printf("sparse_gas_mean_y_end=%.9g\n", sparseMetrics.gasEnd);
  std::printf("adaptive_sparse_gas_mean_y_start=%.9g\n", adaptiveMetrics.gasStart);
  std::printf("adaptive_sparse_gas_mean_y_end=%.9g\n", adaptiveMetrics.gasEnd);
  std::printf("mr_gas_mean_y_start=%.9g\n", mrGas0);
  std::printf("mr_gas_mean_y_end=%.9g\n", mrGas1);
  std::printf("adaptive_mr_gas_mean_y_start=%.9g\n", adaptiveMrGas0);
  std::printf("adaptive_mr_gas_mean_y_end=%.9g\n", adaptiveMrGas1);
  std::printf("sparse_active_pressure_blocks_max=%zu\n", sparseMetrics.maxBlocks);
  std::printf("adaptive_sparse_active_pressure_blocks_max=%zu\n",
              adaptiveMetrics.maxBlocks);
  std::printf("sparse_total_pressure_blocks=%zu\n", sparse.grid.totalCellBlocks());
  std::printf("adaptive_sparse_total_pressure_blocks=%zu\n",
              sparseAdaptive.grid.totalCellBlocks());
  std::printf("adaptive_sparse_narrow_band_removed_total=%d\n",
              sparseAdaptive.narrow_band_air_removed_total);
  std::printf("adaptive_sparse_gas_coarsening_removed_total=%d\n",
              sparseAdaptive.gas_particle_coarsening_removed_total);
  std::printf("adaptive_sparse_gas_coarsening_cells_last=%d\n",
              sparseAdaptive.gas_particle_coarsening_cells_last);
  std::printf("adaptive_sparse_gas_coarsening_overfull_cells_last=%d\n",
              sparseAdaptive.gas_particle_coarsening_overfull_cells_last);
  std::printf("adaptive_sparse_liquid_coarsening_removed_total=%d\n",
              sparseAdaptive.liquid_particle_coarsening_removed_total);
  std::printf("adaptive_sparse_liquid_coarsening_removed_during_run=%d\n",
              adaptiveMetrics.liquidCoarseningRemovedDuringRun);
  std::printf("adaptive_sparse_liquid_coarsening_cells_last=%d\n",
              sparseAdaptive.liquid_particle_coarsening_cells_last);
  std::printf("adaptive_sparse_liquid_coarsening_overfull_cells_last=%d\n",
              sparseAdaptive.liquid_particle_coarsening_overfull_cells_last);
  std::printf("adaptive_sparse_liquid_refill_added_total=%d\n",
              sparseAdaptive.liquid_particle_refill_added_total);
  std::printf("adaptive_sparse_liquid_refill_added_during_run=%d\n",
              adaptiveMetrics.liquidRefillAddedDuringRun);
  std::printf("adaptive_sparse_liquid_refill_cells_last=%d\n",
              sparseAdaptive.liquid_particle_refill_cells_last);
  std::printf("adaptive_sparse_liquid_refill_interface_cells_last=%d\n",
              sparseAdaptive.liquid_particle_refill_interface_cells_last);
  std::printf("adaptive_sparse_liquid_refill_underfull_cells_last=%d\n",
              sparseAdaptive.liquid_particle_refill_underfull_cells_last);
  std::printf("adaptive_sparse_liquid_refill_budget_limited_last=%d\n",
              sparseAdaptive.liquid_particle_refill_budget_limited_last);
  std::printf("adaptive_mr_narrow_band_removed_total=%d\n",
              mrAdaptivity ? mrAdaptive.narrow_band_air_removed_total : 0);
  std::printf("adaptive_mr_gas_coarsening_removed_total=%d\n",
              mrAdaptivity ? mrAdaptive.gas_particle_coarsening_removed_total : 0);
  std::printf("adaptive_mr_gas_coarsening_cells_last=%d\n",
              mrAdaptivity ? mrAdaptive.gas_particle_coarsening_cells_last : 0);
  std::printf("adaptive_mr_gas_coarsening_overfull_cells_last=%d\n",
              mrAdaptivity ? mrAdaptive.gas_particle_coarsening_overfull_cells_last : 0);
  std::printf("adaptive_mr_liquid_coarsening_removed_total=%d\n",
              mrAdaptivity ? mrAdaptive.liquid_particle_coarsening_removed_total : 0);
  std::printf("adaptive_mr_liquid_coarsening_removed_during_run=%d\n",
              mrAdaptivity ? adaptiveMrLiquidCoarseningRemovedDuringRun : 0);
  std::printf("adaptive_mr_liquid_coarsening_cells_last=%d\n",
              mrAdaptivity ? mrAdaptive.liquid_particle_coarsening_cells_last : 0);
  std::printf("adaptive_mr_liquid_coarsening_overfull_cells_last=%d\n",
              mrAdaptivity ? mrAdaptive.liquid_particle_coarsening_overfull_cells_last : 0);
  std::printf("adaptive_mr_liquid_refill_added_total=%d\n",
              mrAdaptivity ? mrAdaptive.liquid_particle_refill_added_total : 0);
  std::printf("adaptive_mr_liquid_refill_added_during_run=%d\n",
              mrAdaptivity ? adaptiveMrLiquidRefillAddedDuringRun : 0);
  std::printf("adaptive_mr_liquid_refill_cells_last=%d\n",
              mrAdaptivity ? mrAdaptive.liquid_particle_refill_cells_last : 0);
  std::printf("adaptive_mr_liquid_refill_interface_cells_last=%d\n",
              mrAdaptivity ? mrAdaptive.liquid_particle_refill_interface_cells_last : 0);
  std::printf("adaptive_mr_liquid_refill_underfull_cells_last=%d\n",
              mrAdaptivity ? mrAdaptive.liquid_particle_refill_underfull_cells_last : 0);
  std::printf("adaptive_mr_liquid_refill_budget_limited_last=%d\n",
              mrAdaptivity ? mrAdaptive.liquid_particle_refill_budget_limited_last : 0);
  std::printf("mr_dynamic_refinement=%s\n", mr.dynamic_refinement ? "true" : "false");
  std::printf("mr_dynamic_hysteresis_cells=%d\n", mr.dynamic_hysteresis_cells);
  std::printf("mr_dynamic_max_fine_leaves=%d\n", mr.dynamic_max_fine_leaves);
  std::printf("mr_dynamic_budget_limited=%s\n", mr.dynamic_budget_limited ? "true" : "false");
  std::printf("mr_dynamic_last_fine_leaves=%d\n", mr.dynamic_last_fine_leaves);
  std::printf("mr_pressure_iterations=%d\n", mr.last_pressure_stats.iterations);
  std::printf("mr_pressure_max_iterations=%d\n", mr.last_pressure_stats.max_iterations);
  std::printf("mr_pressure_initial_residual=%.9g\n", mr.last_pressure_stats.initial_residual);
  std::printf("mr_pressure_final_residual=%.9g\n", mr.last_pressure_stats.final_residual);
  std::printf("mr_pressure_final_over_initial=%.9g\n", finalOverInitial);
  std::printf("mr_pressure_min_residual=%.9g\n", mr.last_pressure_stats.min_residual);
  std::printf("mr_pressure_max_residual=%.9g\n", mr.last_pressure_stats.max_residual);
  std::printf("mr_pressure_effective_tolerance=%.9g\n", mr.last_pressure_stats.effective_tolerance);
  std::printf("mr_pressure_relative_tolerance=%.9g\n", mr.last_pressure_stats.relative_tolerance);
  std::printf("mr_pressure_min_positive_diag=%.9g\n", mr.last_pressure_stats.min_positive_diag);
  std::printf("mr_pressure_max_diag=%.9g\n", mr.last_pressure_stats.max_diag);
  std::printf("mr_pressure_diag_finite=%s\n", pressureDiagFinite ? "true" : "false");
  std::printf("mr_pressure_jacobi_preconditioner=%s\n",
              mr.last_pressure_stats.used_jacobi_preconditioner ? "true" : "false");
  std::printf("mr_pressure_flexible_cg_beta=%s\n",
              mr.last_pressure_stats.used_flexible_cg_beta ? "true" : "false");
  std::printf("mr_pressure_beta_resets=%d\n", mr.last_pressure_stats.beta_resets);
  std::printf("mr_pressure_adaptive_restart=%s\n",
              mr.last_pressure_stats.adaptive_restart ? "true" : "false");
  std::printf("mr_pressure_restart_growth=%.9g\n",
              mr.last_pressure_stats.restart_growth_threshold);
  std::printf("mr_pressure_restarts=%d\n", mr.last_pressure_stats.restarts);
  std::printf("mr_pressure_relaxation_sweeps=%d\n",
              mr.last_pressure_stats.relaxation_sweeps);
  std::printf("mr_pressure_relaxation_accepted=%d\n",
              mr.last_pressure_stats.relaxation_accepted);
  std::printf("mr_pressure_relaxation_rejected=%d\n",
              mr.last_pressure_stats.relaxation_rejected);
  std::printf("mr_pressure_relaxation_omega=%.9g\n",
              mr.last_pressure_stats.relaxation_omega);
  std::printf("mr_pressure_relaxation_min_omega=%.9g\n",
              mr.last_pressure_stats.relaxation_min_omega);
  std::printf("mr_pressure_relaxation_final_omega=%.9g\n",
              mr.last_pressure_stats.relaxation_final_omega);
  std::printf("mr_pressure_residual_history_stride=%d\n",
              mr.last_pressure_stats.residual_history_stride);
  std::printf("mr_pressure_residual_history_limit=%d\n",
              mr.last_pressure_stats.residual_history_limit);
  std::printf("mr_pressure_residual_history_count=%zu\n",
              mr.last_pressure_stats.residual_history.size());
  std::printf("mr_pressure_residual_history_truncated=%s\n",
              mr.last_pressure_stats.residual_history_truncated ? "true" : "false");
  std::printf("mr_pressure_residual_history_first=%.9g\n",
              mr.last_pressure_stats.residual_history.empty() ? 0.0 : mr.last_pressure_stats.residual_history.front());
  std::printf("mr_pressure_residual_history_last=%.9g\n",
              mr.last_pressure_stats.residual_history.empty() ? 0.0 : mr.last_pressure_stats.residual_history.back());
  std::printf("mr_pressure_converged=%s\n", mr.last_pressure_stats.converged ? "true" : "false");
  std::printf("mr_pressure_convergence_ok=%s\n", convergenceOk ? "true" : "false");
  std::printf("mr_pressure_breakdown=%s\n", mr.last_pressure_stats.breakdown ? "true" : "false");
  std::printf("mr_leaf_level0=%zu\n", mr.layout.countLevel(0));
  std::printf("mr_leaf_level1=%zu\n", mr.layout.countLevel(1));
  std::printf("mr_pressure_cells=%d\n", mrPressureCells);
  std::printf("adaptive_mr_pressure_cells=%d\n", adaptiveMrPressureCells);
  std::printf("fine_pressure_cells=%d\n", finePressureCells);
  std::printf("mr_u_faces=%d\n", mr.uFaceCount());
  std::printf("mr_v_faces=%d\n", mr.vFaceCount());
  std::printf("mr_w_faces=%d\n", mr.wFaceCount());
  std::printf("mr_pressure_cell_ratio=%.9g\n", pressureRatio);
  std::printf("mr_pressure_cell_reduction=%.9g\n", pressureReduction);
  std::printf("sparse_elapsed_ms=%lld\n", sparseMetrics.elapsedMs);
  std::printf("adaptive_sparse_elapsed_ms=%lld\n", adaptiveMetrics.elapsedMs);
  std::printf("mr_elapsed_ms=%lld\n", mrMs);
  std::printf("adaptive_mr_elapsed_ms=%lld\n", adaptiveMrMs);
  std::printf("rise_delta=%.9g\n", riseDelta);
  std::printf("allowed_rise_delta=%.9g\n", allowedRiseDelta);
  std::printf("adaptive_rise_delta=%.9g\n", adaptiveRiseDelta);
  std::printf("allowed_adaptive_rise_delta=%.9g\n", allowedAdaptiveRiseDelta);
  std::printf("adaptive_mr_rise_delta=%.9g\n", adaptiveMrRiseDelta);
  std::printf("allowed_adaptive_mr_rise_delta=%.9g\n", allowedAdaptiveMrRiseDelta);
  std::printf("adaptive_mr_pressure_convergence_ok=%s\n",
              adaptiveMrConvergenceOk ? "true" : "false");
  std::printf("adaptive_mr_pressure_diag_finite=%s\n",
              adaptiveMrPressureDiagFinite ? "true" : "false");

  bool ok = true;
  const double sparseLiquidVolumeTol =
    std::max(1e-9, std::abs(sparseMetrics.liquidVolumeStart) * 1e-9);
  const double sparseGasVolumeTol =
    std::max(1e-9, std::abs(sparseMetrics.gasVolumeStart) * 1e-9);
  const double mrLiquidVolumeTol =
    std::max(1e-9, std::abs(mrLiquidVolume0) * 1e-9);
  const double mrGasVolumeTol =
    std::max(1e-9, std::abs(mrGasVolume0) * 1e-9);
  if (!sparseMetrics.finite || !mrFinite) ok = false;
  if (std::abs(sparseMetrics.liquidVolumeEnd - sparseMetrics.liquidVolumeStart) >
        sparseLiquidVolumeTol ||
      std::abs(sparseMetrics.gasVolumeEnd - sparseMetrics.gasVolumeStart) >
        sparseGasVolumeTol ||
      std::abs(mrLiquidVolume1 - mrLiquidVolume0) > mrLiquidVolumeTol ||
      std::abs(mrGasVolume1 - mrGasVolume0) > mrGasVolumeTol) {
    ok = false;
  }
  if (sparseMetrics.particlesEnd != sparseMetrics.particlesStart ||
      mr.particles.size() != mrN0) ok = false;
  if (sparseMetrics.particlesStart != mrN0 ||
      sparseMetrics.particlesEnd != mr.particles.size()) ok = false;
  if (sparseMetrics.liquidEnd != sparseMetrics.liquidStart ||
      sparseMetrics.gasCountEnd != sparseMetrics.gasCountStart ||
      mrLiquid1 != mrLiquid0 ||
      mrGasCount1 != mrGasCount0) {
    ok = false;
  }
  auto interfaceDiagnosticsOk = [&](const InterfaceDiagnostics3D& diagnostics) {
    return steps == 0 ||
           (diagnostics.finite && diagnostics.sample_cells > 0);
  };
  auto surfaceTensionOk = [&](const InterfaceDiagnostics3D& diagnostics,
                              const SurfaceTensionStats3D& stats) {
    if (surfaceTension) {
      if (!stats.enabled || !stats.finite) return false;
      if (steps > 0 && diagnostics.interface_cells > 0 && stats.applied_cells <= 0) {
        return false;
      }
      if (surfaceTensionMaxDeltaSpeed > 0.0 &&
          stats.max_delta_speed > surfaceTensionMaxDeltaSpeed + 1e-12) {
        return false;
      }
      return true;
    }
    return !stats.enabled && stats.applied_cells == 0;
  };
  if (!interfaceDiagnosticsOk(sparseMetrics.interfaceDiagnostics)) ok = false;
  if (!interfaceDiagnosticsOk(mrInterfaceDiagnostics)) ok = false;
  if (!surfaceTensionOk(sparseMetrics.interfaceDiagnostics,
                        sparseMetrics.surfaceTensionStats)) {
    ok = false;
  }
  if (!surfaceTensionOk(mrInterfaceDiagnostics, mrSurfaceTensionStats)) {
    ok = false;
  }
  auto secondaryOk = [&](int dropletCandidates,
                         int bubbleCandidates,
                         int dropletsAdded,
                         int bubblesAdded,
                         size_t dropletParticles,
                         size_t bubbleParticles,
                         size_t dropletAges,
                         size_t bubbleAges,
                         int lifecycleEnabled,
                         int lifecycleFinite,
                         int dropletsReabsorbed,
                         int bubblesReabsorbed,
                         int dropletsExpired,
                         int bubblesExpired,
                         double dropletVolumeAdded,
                         double bubbleVolumeAdded,
                         double dropletVolumeCurrent,
                         double bubbleVolumeCurrent,
                         double dropletVolumeReabsorbed,
                         double bubbleVolumeReabsorbed,
                         double dropletVolumeExpired,
                         double bubbleVolumeExpired) {
    auto volumeBalanceOk = [](double added,
                              double current,
                              double reabsorbed,
                              double expired) {
      const double lhs = current + reabsorbed + expired;
      const double tol = std::max(1e-9, std::abs(added) * 1e-9);
      return std::abs(lhs - added) <= tol;
    };
    if (dropletAges != dropletParticles || bubbleAges != bubbleParticles) {
      return false;
    }
    if (secondaryLifecycle) {
      if (!lifecycleEnabled || !lifecycleFinite) return false;
    } else if (lifecycleEnabled || !lifecycleFinite) {
      return false;
    }
    if (!volumeBalanceOk(dropletVolumeAdded,
                         dropletVolumeCurrent,
                         dropletVolumeReabsorbed,
                         dropletVolumeExpired)) {
      return false;
    }
    if (!volumeBalanceOk(bubbleVolumeAdded,
                         bubbleVolumeCurrent,
                         bubbleVolumeReabsorbed,
                         bubbleVolumeExpired)) {
      return false;
    }
    if (escapedParticleBranching) {
      if (dropletsAdded != dropletCandidates ||
          bubblesAdded != bubbleCandidates) {
        return false;
      }
      if (secondaryLifecycle) {
        return dropletParticles +
                 static_cast<size_t>(dropletsReabsorbed + dropletsExpired) ==
                 static_cast<size_t>(dropletsAdded) &&
               bubbleParticles +
                 static_cast<size_t>(bubblesReabsorbed + bubblesExpired) ==
                 static_cast<size_t>(bubblesAdded);
      }
      return dropletParticles == static_cast<size_t>(dropletsAdded) &&
             bubbleParticles == static_cast<size_t>(bubblesAdded) &&
             dropletsReabsorbed == 0 &&
             bubblesReabsorbed == 0 &&
             dropletsExpired == 0 &&
             bubblesExpired == 0;
    }
    return dropletsAdded == 0 &&
           bubblesAdded == 0 &&
           dropletParticles == 0 &&
           bubbleParticles == 0 &&
           dropletsReabsorbed == 0 &&
           bubblesReabsorbed == 0 &&
           dropletsExpired == 0 &&
           bubblesExpired == 0;
  };
  if (!secondaryOk(sparseMetrics.escapedDropletCandidatesTotal,
                   sparseMetrics.escapedBubbleCandidatesTotal,
                   sparseMetrics.escapedDropletsAddedTotal,
                   sparseMetrics.escapedBubblesAddedTotal,
                   sparseMetrics.escapedDropletParticles,
                   sparseMetrics.escapedBubbleParticles,
                   sparseMetrics.escapedDropletAges,
                   sparseMetrics.escapedBubbleAges,
                   sparseMetrics.secondaryLifecycleEnabled,
                   sparseMetrics.secondaryLifecycleFinite,
                   sparseMetrics.secondaryDropletsReabsorbedTotal,
                   sparseMetrics.secondaryBubblesReabsorbedTotal,
                   sparseMetrics.secondaryDropletsExpiredTotal,
                   sparseMetrics.secondaryBubblesExpiredTotal,
                   sparseMetrics.escapedDropletVolumeAddedTotal,
                   sparseMetrics.escapedBubbleVolumeAddedTotal,
                   sparseMetrics.secondaryDropletVolumeCurrent,
                   sparseMetrics.secondaryBubbleVolumeCurrent,
                   sparseMetrics.secondaryDropletVolumeReabsorbedTotal,
                   sparseMetrics.secondaryBubbleVolumeReabsorbedTotal,
                   sparseMetrics.secondaryDropletVolumeExpiredTotal,
                   sparseMetrics.secondaryBubbleVolumeExpiredTotal)) {
    ok = false;
  }
  if (!secondaryOk(mrEscapedDropletCandidatesTotal,
                   mrEscapedBubbleCandidatesTotal,
                   mrEscapedDropletsAddedTotal,
                   mrEscapedBubblesAddedTotal,
                   mrEscapedDropletParticles,
                   mrEscapedBubbleParticles,
                   mrEscapedDropletAges,
                   mrEscapedBubbleAges,
                   mrSecondaryLifecycleEnabled,
                   mrSecondaryLifecycleFinite,
                   mrSecondaryDropletsReabsorbedTotal,
                   mrSecondaryBubblesReabsorbedTotal,
                   mrSecondaryDropletsExpiredTotal,
                   mrSecondaryBubblesExpiredTotal,
                   mrEscapedDropletVolumeAddedTotal,
                   mrEscapedBubbleVolumeAddedTotal,
                   mrSecondaryDropletVolumeCurrent,
                   mrSecondaryBubbleVolumeCurrent,
                   mrSecondaryDropletVolumeReabsorbedTotal,
                   mrSecondaryBubbleVolumeReabsorbedTotal,
                   mrSecondaryDropletVolumeExpiredTotal,
                   mrSecondaryBubbleVolumeExpiredTotal)) {
    ok = false;
  }
  if (physicsPreset) {
    if (!corePhysicsPresetActive3D(sparse) ||
        !fullPhysicsPresetActive3D(sparseAdaptive) ||
        !corePhysicsPresetActive3D(mr) ||
        !fullPhysicsPresetActive3D(mrAdaptive)) {
      ok = false;
    }
  }
  if (!(sparseRise > 0.0) || !(mrRise > 0.0)) ok = false;
  if (sparseAdaptivity) {
    if (!adaptiveMetrics.finite) ok = false;
    const double adaptiveSparseLiquidVolumeTol =
      std::max(1e-9, std::abs(adaptiveMetrics.liquidVolumeStart) * 1e-9);
    const double adaptiveSparseGasVolumeTol =
      std::max(1e-9, std::abs(adaptiveMetrics.gasVolumeStart) * 1e-9);
    if (std::abs(adaptiveMetrics.liquidVolumeEnd - adaptiveMetrics.liquidVolumeStart) >
        adaptiveSparseLiquidVolumeTol) {
      ok = false;
    }
    if (sparseAdaptive.narrow_band_air) {
      if (adaptiveMetrics.gasVolumeEnd >
          adaptiveMetrics.gasVolumeStart + adaptiveSparseGasVolumeTol) {
        ok = false;
      }
    } else if (std::abs(adaptiveMetrics.gasVolumeEnd - adaptiveMetrics.gasVolumeStart) >
               adaptiveSparseGasVolumeTol) {
      ok = false;
    }
    const size_t maxAdaptiveSparseParticles = adaptiveMetrics.particlesStart +
      static_cast<size_t>(std::max(0, adaptiveMetrics.liquidRefillAddedDuringRun));
    if (adaptiveMetrics.particlesEnd > maxAdaptiveSparseParticles) ok = false;
    if (sparseLiquidRefill) {
      const size_t maxAdaptiveSparseLiquid = adaptiveMetrics.liquidStart +
        static_cast<size_t>(std::max(0, adaptiveMetrics.liquidRefillAddedDuringRun));
      if (adaptiveMetrics.liquidEnd > maxAdaptiveSparseLiquid) ok = false;
      if (sparseAdaptive.liquid_particle_refill_interface_only &&
          sparseAdaptive.liquid_particle_refill_underfull_cells_last >
            sparseAdaptive.liquid_particle_refill_interface_cells_last) {
        ok = false;
      }
      if (sparseAdaptive.liquid_particle_refill_max_added_per_step > 0) {
        const int cap = sparseAdaptive.liquid_particle_refill_max_added_per_step;
        if (sparseAdaptive.liquid_particle_refill_added_last > cap) ok = false;
        if (adaptiveMetrics.liquidRefillAddedDuringRun > steps * cap) ok = false;
      }
      if (sparseAdaptive.liquid_particle_coarsening &&
          adaptiveMetrics.liquidRefillAddedDuringRun >
            adaptiveMetrics.liquidCoarseningRemovedDuringRun) {
        ok = false;
      }
      if (!sparseAdaptive.liquid_particle_coarsening &&
          adaptiveMetrics.liquidEnd != maxAdaptiveSparseLiquid) {
        ok = false;
      }
    } else if (sparseLiquidAdaptivity) {
      if (adaptiveMetrics.liquidEnd > adaptiveMetrics.liquidStart) ok = false;
    } else if (adaptiveMetrics.liquidEnd != adaptiveMetrics.liquidStart) {
      ok = false;
    }
    if (sparseGasAdaptivity) {
      if (adaptiveMetrics.gasCountEnd > adaptiveMetrics.gasCountStart) ok = false;
    } else if (adaptiveMetrics.gasCountEnd != adaptiveMetrics.gasCountStart) {
      ok = false;
    }
    if (!interfaceDiagnosticsOk(adaptiveMetrics.interfaceDiagnostics)) ok = false;
    if (!surfaceTensionOk(adaptiveMetrics.interfaceDiagnostics,
                          adaptiveMetrics.surfaceTensionStats)) {
      ok = false;
    }
    if (!secondaryOk(adaptiveMetrics.escapedDropletCandidatesTotal,
                     adaptiveMetrics.escapedBubbleCandidatesTotal,
                     adaptiveMetrics.escapedDropletsAddedTotal,
                     adaptiveMetrics.escapedBubblesAddedTotal,
                     adaptiveMetrics.escapedDropletParticles,
                     adaptiveMetrics.escapedBubbleParticles,
                     adaptiveMetrics.escapedDropletAges,
                     adaptiveMetrics.escapedBubbleAges,
                     adaptiveMetrics.secondaryLifecycleEnabled,
                     adaptiveMetrics.secondaryLifecycleFinite,
                     adaptiveMetrics.secondaryDropletsReabsorbedTotal,
                     adaptiveMetrics.secondaryBubblesReabsorbedTotal,
                     adaptiveMetrics.secondaryDropletsExpiredTotal,
                     adaptiveMetrics.secondaryBubblesExpiredTotal,
                     adaptiveMetrics.escapedDropletVolumeAddedTotal,
                     adaptiveMetrics.escapedBubbleVolumeAddedTotal,
                     adaptiveMetrics.secondaryDropletVolumeCurrent,
                     adaptiveMetrics.secondaryBubbleVolumeCurrent,
                     adaptiveMetrics.secondaryDropletVolumeReabsorbedTotal,
                     adaptiveMetrics.secondaryBubbleVolumeReabsorbedTotal,
                     adaptiveMetrics.secondaryDropletVolumeExpiredTotal,
                     adaptiveMetrics.secondaryBubbleVolumeExpiredTotal)) {
      ok = false;
    }
    if (!(adaptiveRise > 0.0)) ok = false;
    if (!(adaptiveRiseDelta <= allowedAdaptiveRiseDelta)) ok = false;
  }
  if (mrAdaptivity) {
    if (!adaptiveMrFinite) ok = false;
    const double adaptiveMrLiquidVolumeTol =
      std::max(1e-9, std::abs(adaptiveMrLiquidVolume0) * 1e-9);
    const double adaptiveMrGasVolumeTol =
      std::max(1e-9, std::abs(adaptiveMrGasVolume0) * 1e-9);
    if (std::abs(adaptiveMrLiquidVolume1 - adaptiveMrLiquidVolume0) >
        adaptiveMrLiquidVolumeTol) {
      ok = false;
    }
    if (mrAdaptive.narrow_band_air) {
      if (adaptiveMrGasVolume1 > adaptiveMrGasVolume0 + adaptiveMrGasVolumeTol) {
        ok = false;
      }
    } else if (std::abs(adaptiveMrGasVolume1 - adaptiveMrGasVolume0) >
               adaptiveMrGasVolumeTol) {
      ok = false;
    }
    const size_t maxAdaptiveMrParticles = adaptiveMrN0 +
      static_cast<size_t>(std::max(0, adaptiveMrLiquidRefillAddedDuringRun));
    if (adaptiveMrN1 > maxAdaptiveMrParticles) ok = false;
    if (mrLiquidRefill) {
      const size_t maxAdaptiveMrLiquid = adaptiveMrLiquid0 +
        static_cast<size_t>(std::max(0, adaptiveMrLiquidRefillAddedDuringRun));
      if (adaptiveMrLiquid1 > maxAdaptiveMrLiquid) ok = false;
      if (mrAdaptive.liquid_particle_refill_interface_only &&
          mrAdaptive.liquid_particle_refill_underfull_cells_last >
            mrAdaptive.liquid_particle_refill_interface_cells_last) {
        ok = false;
      }
      if (mrAdaptive.liquid_particle_refill_max_added_per_step > 0) {
        const int cap = mrAdaptive.liquid_particle_refill_max_added_per_step;
        if (mrAdaptive.liquid_particle_refill_added_last > cap) ok = false;
        if (adaptiveMrLiquidRefillAddedDuringRun > steps * cap) ok = false;
      }
      if (mrAdaptive.liquid_particle_coarsening &&
          adaptiveMrLiquidRefillAddedDuringRun >
            adaptiveMrLiquidCoarseningRemovedDuringRun) {
        ok = false;
      }
      if (!mrAdaptive.liquid_particle_coarsening &&
          adaptiveMrLiquid1 != maxAdaptiveMrLiquid) {
        ok = false;
      }
    } else if (mrLiquidAdaptivity) {
      if (adaptiveMrLiquid1 > adaptiveMrLiquid0) ok = false;
    } else if (adaptiveMrLiquid1 != adaptiveMrLiquid0) {
      ok = false;
    }
    if (mrGasAdaptivity) {
      if (adaptiveMrGasCount1 > adaptiveMrGasCount0) ok = false;
    } else if (adaptiveMrGasCount1 != adaptiveMrGasCount0) {
      ok = false;
    }
    if (!interfaceDiagnosticsOk(adaptiveMrInterfaceDiagnostics)) ok = false;
    if (!surfaceTensionOk(adaptiveMrInterfaceDiagnostics,
                          adaptiveMrSurfaceTensionStats)) {
      ok = false;
    }
    if (!secondaryOk(adaptiveMrEscapedDropletCandidatesTotal,
                     adaptiveMrEscapedBubbleCandidatesTotal,
                     adaptiveMrEscapedDropletsAddedTotal,
                     adaptiveMrEscapedBubblesAddedTotal,
                     adaptiveMrEscapedDropletParticles,
                     adaptiveMrEscapedBubbleParticles,
                     adaptiveMrEscapedDropletAges,
                     adaptiveMrEscapedBubbleAges,
                     adaptiveMrSecondaryLifecycleEnabled,
                     adaptiveMrSecondaryLifecycleFinite,
                     adaptiveMrSecondaryDropletsReabsorbedTotal,
                     adaptiveMrSecondaryBubblesReabsorbedTotal,
                     adaptiveMrSecondaryDropletsExpiredTotal,
                     adaptiveMrSecondaryBubblesExpiredTotal,
                     adaptiveMrEscapedDropletVolumeAddedTotal,
                     adaptiveMrEscapedBubbleVolumeAddedTotal,
                     adaptiveMrSecondaryDropletVolumeCurrent,
                     adaptiveMrSecondaryBubbleVolumeCurrent,
                     adaptiveMrSecondaryDropletVolumeReabsorbedTotal,
                     adaptiveMrSecondaryBubbleVolumeReabsorbedTotal,
                     adaptiveMrSecondaryDropletVolumeExpiredTotal,
                     adaptiveMrSecondaryBubbleVolumeExpiredTotal)) {
      ok = false;
    }
    if (!(adaptiveMrRise > 0.0)) ok = false;
    if (!(adaptiveMrRiseDelta <= allowedAdaptiveMrRiseDelta)) ok = false;
    if (!(adaptiveMrPressureCells < finePressureCells)) ok = false;
    if (steps > 0 && adaptiveMrStats.breakdown) ok = false;
    if (steps > 0 && !std::isfinite(adaptiveMrStats.final_residual)) ok = false;
    if (steps > 0 && adaptiveMrStats.final_residual > adaptiveMrStats.initial_residual) ok = false;
    if (steps > 0 && !adaptiveMrConvergenceOk) ok = false;
    if (steps > 0 && highDensityRatio && !adaptiveMrPressureDiagFinite) ok = false;
  }
  if (!(mrPressureCells < finePressureCells)) ok = false;
  if (!(riseDelta <= allowedRiseDelta)) ok = false;
  if (steps > 0 && mr.last_pressure_stats.breakdown) ok = false;
  if (steps > 0 && !std::isfinite(mr.last_pressure_stats.final_residual)) ok = false;
  if (steps > 0 && mr.last_pressure_stats.final_residual > mr.last_pressure_stats.initial_residual) ok = false;
  if (steps > 0 && !convergenceOk) ok = false;
  if (steps > 0 && highDensityRatio && !pressureDiagFinite) ok = false;

  std::printf("status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
