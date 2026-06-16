#include "driver/multires_sim3d_tp.h"

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

double argDouble(int argc, char** argv, const char* key, double fallback) {
  for (int i = 1; i + 1 < argc; ++i) {
    if (std::strcmp(argv[i], key) == 0) return std::atof(argv[i + 1]);
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
    if (!std::isfinite(ps.pos[i].x) ||
        !std::isfinite(ps.pos[i].y) ||
        !std::isfinite(ps.pos[i].z)) {
      return false;
    }
  }
  return true;
}

void usage() {
  std::fprintf(stderr,
               "usage: validate_multires3d_tp [--scenario bubble] [--nx N] [--ny N] [--nz N] "
               "[--steps N] [--dt DT] [--cg-iters N] [--hysteresis N] "
               "[--max-fine-leaves N] [--cg-rel-tol T] [--rho-ratio R] "
               "[--adaptive-timestep] [--adaptive-cfl C] [--adaptive-min-dt DT] "
               "[--require-converged] [--no-jacobi] [--flexible-cg] "
               "[--no-restart] [--restart-growth G] "
               "[--relax-sweeps N] [--relax-omega W] [--relax-min-omega W] "
               "[--history-stride N] [--history-limit N] "
               "[--coarse-correction] [--coarse-iters N] [--coarse-sweeps N] "
               "[--coarse-rel-tol T] [--coarse-abs-tol T] [--coarse-min-scale S] "
               "[--coarse-preconditioner] [--coarse-pre-iters N] "
               "[--coarse-pre-rel-tol T] [--coarse-pre-abs-tol T] "
               "[--coarse-pre-scale S] [--coarse-pre-min-rz-gain G] "
               "[--coarse-pre-max-work-ratio W] "
               "[--coarse-pre-auto-disable] [--coarse-pre-auto-disable-after N] "
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
  const char* scenario = argString(argc, argv, "--scenario", "bubble");
  int nx = argInt(argc, argv, "--nx", 12);
  int ny = argInt(argc, argv, "--ny", 18);
  int nz = argInt(argc, argv, "--nz", 12);
  int steps = argInt(argc, argv, "--steps", 20);

  if (nx < 4 || ny < 4 || nz < 4 || steps < 0 || std::strcmp(scenario, "bubble") != 0) {
    usage();
    return 2;
  }

  MRSim3DTP sim(nx, ny, nz, 1.0);
  double requestedRhoRatio = argDouble(argc, argv, "--rho-ratio", 0.0);
  if (requestedRhoRatio > 0.0) {
    sim.phase.rho_l = requestedRhoRatio;
    sim.phase.rho_g = 1.0;
  }
  sim.dt = argDouble(argc, argv, "--dt", sim.dt);
  sim.adaptive_timestep = hasFlag(argc, argv, "--adaptive-timestep");
  sim.adaptive_cfl = argDouble(argc, argv, "--adaptive-cfl", sim.adaptive_cfl);
  sim.adaptive_min_dt = argDouble(argc, argv, "--adaptive-min-dt", sim.adaptive_min_dt);
  sim.cg_iters = argInt(argc, argv, "--cg-iters", sim.cg_iters);
  sim.cg_rel_tol = argDouble(argc, argv, "--cg-rel-tol", sim.cg_rel_tol);
  if (hasFlag(argc, argv, "--no-jacobi")) sim.cg_jacobi_preconditioner = false;
  if (hasFlag(argc, argv, "--flexible-cg")) sim.cg_flexible_beta = true;
  if (hasFlag(argc, argv, "--no-restart")) sim.cg_adaptive_restart = false;
  sim.cg_restart_growth = argDouble(argc, argv, "--restart-growth", sim.cg_restart_growth);
  sim.cg_relaxation_sweeps = argInt(argc, argv, "--relax-sweeps", sim.cg_relaxation_sweeps);
  sim.cg_relaxation_omega = argDouble(argc, argv, "--relax-omega", sim.cg_relaxation_omega);
  sim.cg_relaxation_min_omega = argDouble(argc, argv, "--relax-min-omega", sim.cg_relaxation_min_omega);
  sim.cg_residual_history_stride = argInt(argc, argv, "--history-stride", sim.cg_residual_history_stride);
  sim.cg_residual_history_limit = argInt(argc, argv, "--history-limit", sim.cg_residual_history_limit);
  if (hasFlag(argc, argv, "--coarse-correction")) sim.cg_coarse_correction = true;
  sim.cg_coarse_correction_iters = argInt(argc, argv, "--coarse-iters", sim.cg_coarse_correction_iters);
  sim.cg_coarse_correction_sweeps =
    argInt(argc, argv, "--coarse-sweeps", sim.cg_coarse_correction_sweeps);
  sim.cg_coarse_correction_rel_tol =
    argDouble(argc, argv, "--coarse-rel-tol", sim.cg_coarse_correction_rel_tol);
  sim.cg_coarse_correction_abs_tol =
    argDouble(argc, argv, "--coarse-abs-tol", sim.cg_coarse_correction_abs_tol);
  sim.cg_coarse_correction_min_scale =
    argDouble(argc, argv, "--coarse-min-scale", sim.cg_coarse_correction_min_scale);
  if (hasFlag(argc, argv, "--coarse-preconditioner")) sim.cg_coarse_preconditioner = true;
  sim.cg_coarse_preconditioner_iters =
    argInt(argc, argv, "--coarse-pre-iters", sim.cg_coarse_preconditioner_iters);
  sim.cg_coarse_preconditioner_rel_tol =
    argDouble(argc, argv, "--coarse-pre-rel-tol", sim.cg_coarse_preconditioner_rel_tol);
  sim.cg_coarse_preconditioner_abs_tol =
    argDouble(argc, argv, "--coarse-pre-abs-tol", sim.cg_coarse_preconditioner_abs_tol);
  sim.cg_coarse_preconditioner_scale =
    argDouble(argc, argv, "--coarse-pre-scale", sim.cg_coarse_preconditioner_scale);
  sim.cg_coarse_preconditioner_min_rz_gain =
    argDouble(argc, argv, "--coarse-pre-min-rz-gain",
              sim.cg_coarse_preconditioner_min_rz_gain);
  sim.cg_coarse_preconditioner_max_work_ratio =
    argDouble(argc, argv, "--coarse-pre-max-work-ratio",
              sim.cg_coarse_preconditioner_max_work_ratio);
  if (hasFlag(argc, argv, "--coarse-pre-auto-disable")) {
    sim.cg_coarse_preconditioner_auto_disable = true;
  }
  sim.cg_coarse_preconditioner_auto_disable_after =
    argInt(argc, argv,
           "--coarse-pre-auto-disable-after",
           sim.cg_coarse_preconditioner_auto_disable_after);
  sim.narrow_band_air = hasFlag(argc, argv, "--narrow-band-air");
  sim.narrow_band_air_radius =
    argInt(argc, argv, "--narrow-band-radius", sim.narrow_band_air_radius);
  sim.gas_particle_coarsening = hasFlag(argc, argv, "--gas-coarsening");
  sim.gas_particles_per_cell_target =
    argInt(argc, argv, "--gas-particles-per-cell", sim.gas_particles_per_cell_target);
  sim.gas_particle_coarsening_seed =
    argUInt(argc, argv, "--gas-coarsening-seed", sim.gas_particle_coarsening_seed);
  sim.liquid_particle_coarsening = hasFlag(argc, argv, "--liquid-coarsening");
  sim.liquid_particles_per_cell_target =
    argInt(argc, argv, "--liquid-particles-per-cell", sim.liquid_particles_per_cell_target);
  sim.liquid_particle_coarsening_seed =
    argUInt(argc, argv, "--liquid-coarsening-seed", sim.liquid_particle_coarsening_seed);
  sim.liquid_particle_refill = hasFlag(argc, argv, "--liquid-refill");
  sim.liquid_refill_particles_per_cell_target =
    argInt(argc, argv, "--liquid-refill-particles-per-cell",
           sim.liquid_refill_particles_per_cell_target);
  sim.liquid_particle_refill_seed =
    argUInt(argc, argv, "--liquid-refill-seed", sim.liquid_particle_refill_seed);
  sim.liquid_particle_refill_max_added_per_step =
    argInt(argc, argv, "--liquid-refill-max-added-per-step",
           sim.liquid_particle_refill_max_added_per_step);
  sim.liquid_particle_refill_interface_only =
    hasFlag(argc, argv, "--liquid-refill-interface-only");
  sim.liquid_particle_refill_interface_radius =
    argInt(argc, argv, "--liquid-refill-interface-radius",
           sim.liquid_particle_refill_interface_radius);
  sim.dynamic_hysteresis_cells = argInt(argc, argv, "--hysteresis", sim.dynamic_hysteresis_cells);
  sim.dynamic_max_fine_leaves = argInt(argc, argv, "--max-fine-leaves", sim.dynamic_max_fine_leaves);
  if (requestedRhoRatio < 0.0 ||
      sim.phase.rho_l <= 0.0 ||
      sim.phase.rho_g <= 0.0 ||
      sim.cg_restart_growth < 0.0 ||
      sim.cg_relaxation_sweeps < 0 ||
      sim.cg_relaxation_omega < 0.0 ||
      sim.cg_relaxation_min_omega < 0.0 ||
      sim.cg_residual_history_stride < 0 ||
      sim.cg_residual_history_limit < 0 ||
      sim.cg_coarse_correction_iters < 0 ||
      sim.cg_coarse_correction_sweeps < 0 ||
      sim.cg_coarse_correction_rel_tol < 0.0 ||
      sim.cg_coarse_correction_abs_tol < 0.0 ||
      sim.cg_coarse_correction_min_scale <= 0.0 ||
      sim.cg_coarse_correction_min_scale > 1.0 ||
      sim.cg_coarse_preconditioner_iters < 0 ||
      sim.cg_coarse_preconditioner_rel_tol < 0.0 ||
      sim.cg_coarse_preconditioner_abs_tol < 0.0 ||
      sim.cg_coarse_preconditioner_scale < 0.0 ||
      sim.cg_coarse_preconditioner_min_rz_gain < 0.0 ||
      sim.cg_coarse_preconditioner_max_work_ratio < 0.0 ||
      sim.cg_coarse_preconditioner_auto_disable_after < 0 ||
      sim.adaptive_cfl <= 0.0 ||
      sim.adaptive_min_dt < 0.0 ||
      sim.narrow_band_air_radius < 0 ||
      sim.gas_particles_per_cell_target <= 0 ||
      sim.liquid_particles_per_cell_target <= 0 ||
      sim.liquid_refill_particles_per_cell_target <= 0 ||
      sim.liquid_particle_refill_max_added_per_step < 0 ||
      sim.liquid_particle_refill_interface_radius < 0) {
    usage();
    return 2;
  }
  const double activeRhoRatio = sim.phase.rho_l / sim.phase.rho_g;
  const bool highDensityRatio = activeRhoRatio >= 1000.0;
  const bool requireConverged = hasFlag(argc, argv, "--require-converged") || highDensityRatio;
  sim.initBubbleTankInterfaceBand();

  size_t n0 = sim.particles.size();
  size_t liquidCount0 = countType(sim.particles, 0);
  size_t gasCount0 = countType(sim.particles, 1);
  double liquidVolume0 = volumeType(sim.particles, 0, sim.Vp);
  double gasVolume0 = volumeType(sim.particles, 1, sim.Vp);
  int liquidCoarseningRemoved0 = sim.liquid_particle_coarsening_removed_total;
  int liquidRefillAdded0 = sim.liquid_particle_refill_added_total;
  double gas0 = meanY(sim.particles, 1);
  int pressureCells = sim.activePressureCellCount();
  int fineCells = nx * ny * nz;
  int uFaces = sim.uFaceCount();
  int vFaces = sim.vFaceCount();
  int wFaces = sim.wFaceCount();
  size_t leaf0Start = sim.layout.countLevel(0);
  size_t leaf1Start = sim.layout.countLevel(1);

  auto start = std::chrono::steady_clock::now();
  for (int s = 0; s < steps; ++s) {
    sim.step();
  }
  auto end = std::chrono::steady_clock::now();

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
  int pressureCellsEnd = sim.activePressureCellCount();
  long long elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
  double elapsedPerStep = steps > 0 ? static_cast<double>(elapsedMs) / static_cast<double>(steps) : 0.0;
  const MRPressureSolveStats3D& st = sim.last_pressure_stats;
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

  std::printf("scenario=%s\n", scenario);
  std::printf("dims=%d,%d,%d\n", nx, ny, nz);
  std::printf("steps=%d\n", steps);
  std::printf("dt=%.9g\n", sim.dt);
  std::printf("adaptive_timestep=%s\n", sim.adaptive_timestep ? "true" : "false");
  std::printf("adaptive_cfl=%.9g\n", sim.adaptive_cfl);
  std::printf("adaptive_min_dt=%.9g\n", sim.adaptive_min_dt);
  std::printf("effective_dt_last=%.9g\n", sim.effective_dt_last);
  std::printf("cfl_limit_dt_last=%.9g\n", sim.cfl_limit_dt_last);
  std::printf("max_particle_speed_last=%.9g\n", sim.max_particle_speed_last);
  std::printf("adaptive_timestep_limited_last=%d\n", sim.adaptive_timestep_limited_last);
  std::printf("rho_l=%.9g\n", sim.phase.rho_l);
  std::printf("rho_g=%.9g\n", sim.phase.rho_g);
  std::printf("rho_ratio=%.9g\n", activeRhoRatio);
  std::printf("high_density_ratio=%s\n", highDensityRatio ? "true" : "false");
  std::printf("require_converged=%s\n", requireConverged ? "true" : "false");
  std::printf("cg_iters=%d\n", sim.cg_iters);
  std::printf("cg_tol=%.9g\n", sim.cg_tol);
  std::printf("cg_rel_tol=%.9g\n", sim.cg_rel_tol);
  std::printf("cg_jacobi_preconditioner=%s\n", sim.cg_jacobi_preconditioner ? "true" : "false");
  std::printf("cg_flexible_beta=%s\n", sim.cg_flexible_beta ? "true" : "false");
  std::printf("cg_adaptive_restart=%s\n", sim.cg_adaptive_restart ? "true" : "false");
  std::printf("cg_restart_growth=%.9g\n", sim.cg_restart_growth);
  std::printf("cg_relaxation_sweeps=%d\n", sim.cg_relaxation_sweeps);
  std::printf("cg_relaxation_omega=%.9g\n", sim.cg_relaxation_omega);
  std::printf("cg_relaxation_min_omega=%.9g\n", sim.cg_relaxation_min_omega);
  std::printf("cg_residual_history_stride=%d\n", sim.cg_residual_history_stride);
  std::printf("cg_residual_history_limit=%d\n", sim.cg_residual_history_limit);
  std::printf("cg_coarse_correction=%s\n", sim.cg_coarse_correction ? "true" : "false");
  std::printf("cg_coarse_correction_iters=%d\n", sim.cg_coarse_correction_iters);
  std::printf("cg_coarse_correction_sweeps=%d\n", sim.cg_coarse_correction_sweeps);
  std::printf("cg_coarse_correction_rel_tol=%.9g\n", sim.cg_coarse_correction_rel_tol);
  std::printf("cg_coarse_correction_abs_tol=%.9g\n", sim.cg_coarse_correction_abs_tol);
  std::printf("cg_coarse_correction_min_scale=%.9g\n", sim.cg_coarse_correction_min_scale);
  std::printf("cg_coarse_preconditioner=%s\n", sim.cg_coarse_preconditioner ? "true" : "false");
  std::printf("cg_coarse_preconditioner_iters=%d\n", sim.cg_coarse_preconditioner_iters);
  std::printf("cg_coarse_preconditioner_rel_tol=%.9g\n", sim.cg_coarse_preconditioner_rel_tol);
  std::printf("cg_coarse_preconditioner_abs_tol=%.9g\n", sim.cg_coarse_preconditioner_abs_tol);
  std::printf("cg_coarse_preconditioner_scale=%.9g\n", sim.cg_coarse_preconditioner_scale);
  std::printf("cg_coarse_preconditioner_min_rz_gain=%.9g\n",
              sim.cg_coarse_preconditioner_min_rz_gain);
  std::printf("cg_coarse_preconditioner_max_work_ratio=%.9g\n",
              sim.cg_coarse_preconditioner_max_work_ratio);
  std::printf("cg_coarse_preconditioner_auto_disable=%s\n",
              sim.cg_coarse_preconditioner_auto_disable ? "true" : "false");
  std::printf("cg_coarse_preconditioner_auto_disable_after=%d\n",
              sim.cg_coarse_preconditioner_auto_disable_after);
  std::printf("narrow_band_air=%s\n", sim.narrow_band_air ? "true" : "false");
  std::printf("narrow_band_radius=%d\n", sim.narrow_band_air_radius);
  std::printf("gas_particle_coarsening=%s\n",
              sim.gas_particle_coarsening ? "true" : "false");
  std::printf("gas_particles_per_cell_target=%d\n", sim.gas_particles_per_cell_target);
  std::printf("gas_particle_coarsening_seed=%u\n", sim.gas_particle_coarsening_seed);
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
  std::printf("narrow_band_air_removed_last=%d\n", sim.narrow_band_air_removed_last);
  std::printf("narrow_band_air_removed_total=%d\n", sim.narrow_band_air_removed_total);
  std::printf("narrow_band_air_liquid_cells_last=%d\n", sim.narrow_band_air_liquid_cells_last);
  std::printf("narrow_band_air_gas_particles_before_last=%d\n",
              sim.narrow_band_air_gas_particles_before_last);
  std::printf("narrow_band_air_gas_particles_after_last=%d\n",
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
  std::printf("gas_mean_y_start=%.9g\n", gas0);
  std::printf("gas_mean_y_end=%.9g\n", gas1);
  std::printf("dynamic_refinement=%s\n", sim.dynamic_refinement ? "true" : "false");
  std::printf("dynamic_hysteresis_cells=%d\n", sim.dynamic_hysteresis_cells);
  std::printf("dynamic_max_fine_leaves=%d\n", sim.dynamic_max_fine_leaves);
  std::printf("dynamic_budget_limited=%s\n", sim.dynamic_budget_limited ? "true" : "false");
  std::printf("dynamic_last_fine_leaves=%d\n", sim.dynamic_last_fine_leaves);
  std::printf("dynamic_retained_box=%d,%d,%d,%d,%d,%d\n",
              sim.dynamic_retained_x0, sim.dynamic_retained_y0, sim.dynamic_retained_z0,
              sim.dynamic_retained_x1, sim.dynamic_retained_y1, sim.dynamic_retained_z1);
  std::printf("pressure_active_cells=%d\n", sim.last_pressure_stats.active_cells);
  std::printf("pressure_pinned_cell=%d\n", sim.last_pressure_stats.pinned_cell);
  std::printf("pressure_iterations=%d\n", sim.last_pressure_stats.iterations);
  std::printf("pressure_max_iterations=%d\n", sim.last_pressure_stats.max_iterations);
  std::printf("pressure_initial_residual=%.9g\n", sim.last_pressure_stats.initial_residual);
  std::printf("pressure_final_residual=%.9g\n", sim.last_pressure_stats.final_residual);
  std::printf("pressure_final_over_initial=%.9g\n", finalOverInitial);
  std::printf("pressure_min_residual=%.9g\n", sim.last_pressure_stats.min_residual);
  std::printf("pressure_max_residual=%.9g\n", sim.last_pressure_stats.max_residual);
  std::printf("pressure_effective_tolerance=%.9g\n", sim.last_pressure_stats.effective_tolerance);
  std::printf("pressure_relative_tolerance=%.9g\n", sim.last_pressure_stats.relative_tolerance);
  std::printf("pressure_min_positive_diag=%.9g\n", sim.last_pressure_stats.min_positive_diag);
  std::printf("pressure_max_diag=%.9g\n", sim.last_pressure_stats.max_diag);
  std::printf("pressure_diag_finite=%s\n", pressureDiagFinite ? "true" : "false");
  std::printf("pressure_jacobi_preconditioner=%s\n",
              sim.last_pressure_stats.used_jacobi_preconditioner ? "true" : "false");
  std::printf("pressure_flexible_cg_beta=%s\n",
              sim.last_pressure_stats.used_flexible_cg_beta ? "true" : "false");
  std::printf("pressure_beta_resets=%d\n", sim.last_pressure_stats.beta_resets);
  std::printf("pressure_adaptive_restart=%s\n",
              sim.last_pressure_stats.adaptive_restart ? "true" : "false");
  std::printf("pressure_restart_growth=%.9g\n",
              sim.last_pressure_stats.restart_growth_threshold);
  std::printf("pressure_restarts=%d\n", sim.last_pressure_stats.restarts);
  std::printf("pressure_relaxation_sweeps=%d\n",
              sim.last_pressure_stats.relaxation_sweeps);
  std::printf("pressure_relaxation_accepted=%d\n",
              sim.last_pressure_stats.relaxation_accepted);
  std::printf("pressure_relaxation_rejected=%d\n",
              sim.last_pressure_stats.relaxation_rejected);
  std::printf("pressure_relaxation_omega=%.9g\n",
              sim.last_pressure_stats.relaxation_omega);
  std::printf("pressure_relaxation_min_omega=%.9g\n",
              sim.last_pressure_stats.relaxation_min_omega);
  std::printf("pressure_relaxation_final_omega=%.9g\n",
              sim.last_pressure_stats.relaxation_final_omega);
  std::printf("pressure_residual_history_stride=%d\n",
              sim.last_pressure_stats.residual_history_stride);
  std::printf("pressure_residual_history_limit=%d\n",
              sim.last_pressure_stats.residual_history_limit);
  std::printf("pressure_residual_history_count=%zu\n",
              sim.last_pressure_stats.residual_history.size());
  std::printf("pressure_residual_history_truncated=%s\n",
              sim.last_pressure_stats.residual_history_truncated ? "true" : "false");
  std::printf("pressure_residual_history_first=%.9g\n",
              sim.last_pressure_stats.residual_history.empty() ? 0.0 : sim.last_pressure_stats.residual_history.front());
  std::printf("pressure_residual_history_last=%.9g\n",
              sim.last_pressure_stats.residual_history.empty() ? 0.0 : sim.last_pressure_stats.residual_history.back());
  std::printf("pressure_coarse_correction_used=%s\n",
              sim.last_pressure_stats.used_coarse_correction ? "true" : "false");
  std::printf("pressure_coarse_correction_accepted=%s\n",
              sim.last_pressure_stats.coarse_correction_accepted ? "true" : "false");
  std::printf("pressure_coarse_correction_converged=%s\n",
              sim.last_pressure_stats.coarse_correction_converged ? "true" : "false");
  std::printf("pressure_coarse_correction_breakdown=%s\n",
              sim.last_pressure_stats.coarse_correction_breakdown ? "true" : "false");
  std::printf("pressure_coarse_correction_cells=%d\n",
              sim.last_pressure_stats.coarse_correction_cells);
  std::printf("pressure_coarse_correction_iterations=%d\n",
              sim.last_pressure_stats.coarse_correction_iterations);
  std::printf("pressure_coarse_correction_max_iterations=%d\n",
              sim.last_pressure_stats.coarse_correction_max_iterations);
  std::printf("pressure_coarse_correction_sweeps=%d\n",
              sim.last_pressure_stats.coarse_correction_sweeps);
  std::printf("pressure_coarse_correction_accepted_sweeps=%d\n",
              sim.last_pressure_stats.coarse_correction_accepted_sweeps);
  std::printf("pressure_coarse_correction_rejected_sweeps=%d\n",
              sim.last_pressure_stats.coarse_correction_rejected_sweeps);
  std::printf("pressure_coarse_correction_initial_residual=%.9g\n",
              sim.last_pressure_stats.coarse_correction_initial_residual);
  std::printf("pressure_coarse_correction_final_residual=%.9g\n",
              sim.last_pressure_stats.coarse_correction_final_residual);
  std::printf("pressure_coarse_correction_min_scale=%.9g\n",
              sim.last_pressure_stats.coarse_correction_min_scale);
  std::printf("pressure_coarse_correction_last_scale=%.9g\n",
              sim.last_pressure_stats.coarse_correction_last_scale);
  std::printf("pressure_coarse_preconditioner_used=%s\n",
              sim.last_pressure_stats.used_coarse_preconditioner ? "true" : "false");
  std::printf("pressure_coarse_preconditioner_breakdown=%s\n",
              sim.last_pressure_stats.coarse_preconditioner_breakdown ? "true" : "false");
  std::printf("pressure_coarse_preconditioner_cells=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_cells);
  std::printf("pressure_coarse_preconditioner_applications=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_applications);
  std::printf("pressure_coarse_preconditioner_accepted_applications=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_accepted_applications);
  std::printf("pressure_coarse_preconditioner_rejected_applications=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_rejected_applications);
  std::printf("pressure_coarse_preconditioner_skipped_applications=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_skipped_applications);
  std::printf("pressure_coarse_preconditioner_budget_limited_applications=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_budget_limited_applications);
  std::printf("pressure_coarse_preconditioner_iterations=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_iterations);
  std::printf("pressure_coarse_preconditioner_max_iterations=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_max_iterations);
  std::printf("pressure_coarse_preconditioner_effective_tolerance=%.9g\n",
              sim.last_pressure_stats.coarse_preconditioner_effective_tolerance);
  std::printf("pressure_coarse_preconditioner_scale=%.9g\n",
              sim.last_pressure_stats.coarse_preconditioner_scale);
  std::printf("pressure_coarse_preconditioner_min_rz_gain=%.9g\n",
              sim.last_pressure_stats.coarse_preconditioner_min_rz_gain);
  std::printf("pressure_coarse_preconditioner_last_rz_gain=%.9g\n",
              sim.last_pressure_stats.coarse_preconditioner_last_rz_gain);
  std::printf("pressure_coarse_preconditioner_max_work_ratio=%.9g\n",
              sim.last_pressure_stats.coarse_preconditioner_max_work_ratio);
  std::printf("pressure_coarse_preconditioner_budget_exhausted=%s\n",
              sim.last_pressure_stats.coarse_preconditioner_budget_exhausted ? "true" : "false");
  std::printf("pressure_coarse_preconditioner_auto_disable=%s\n",
              sim.last_pressure_stats.coarse_preconditioner_auto_disable ? "true" : "false");
  std::printf("pressure_coarse_preconditioner_auto_disabled=%s\n",
              sim.last_pressure_stats.coarse_preconditioner_auto_disabled ? "true" : "false");
  std::printf("pressure_coarse_preconditioner_auto_disable_after=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_auto_disable_after);
  std::printf("pressure_coarse_preconditioner_auto_disable_iteration=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_auto_disable_iteration);
  std::printf("pressure_coarse_preconditioner_auto_disable_wasted_streak=%d\n",
              sim.last_pressure_stats.coarse_preconditioner_auto_disable_wasted_streak);
  std::printf("pressure_converged=%s\n", sim.last_pressure_stats.converged ? "true" : "false");
  std::printf("pressure_convergence_ok=%s\n", convergenceOk ? "true" : "false");
  std::printf("pressure_breakdown=%s\n", sim.last_pressure_stats.breakdown ? "true" : "false");
  std::printf("active_pressure_cells=%d\n", pressureCells);
  std::printf("active_pressure_cells_end=%d\n", pressureCellsEnd);
  std::printf("fine_pressure_cells=%d\n", fineCells);
  std::printf("u_faces=%d\n", uFaces);
  std::printf("v_faces=%d\n", vFaces);
  std::printf("w_faces=%d\n", wFaces);
  std::printf("leaf_level0_start=%zu\n", leaf0Start);
  std::printf("leaf_level1_start=%zu\n", leaf1Start);
  std::printf("leaf_level0=%zu\n", sim.layout.countLevel(0));
  std::printf("leaf_level1=%zu\n", sim.layout.countLevel(1));
  std::printf("elapsed_ms=%lld\n", elapsedMs);
  std::printf("elapsed_ms_per_step=%.9g\n", elapsedPerStep);

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
  if (!(gas1 > gas0)) ok = false;
  if (!(pressureCellsEnd < fineCells)) ok = false;
  if (steps > 0 && sim.last_pressure_stats.breakdown) ok = false;
  if (steps > 0 && !std::isfinite(sim.last_pressure_stats.final_residual)) ok = false;
  if (steps > 0 && sim.last_pressure_stats.final_residual > sim.last_pressure_stats.initial_residual) ok = false;
  if (steps > 0 && !convergenceOk) ok = false;
  if (steps > 0 && highDensityRatio && !pressureDiagFinite) ok = false;

  std::printf("status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
