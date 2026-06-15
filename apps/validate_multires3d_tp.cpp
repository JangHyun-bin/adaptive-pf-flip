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
               "[--require-converged] [--no-jacobi] [--flexible-cg] "
               "[--no-restart] [--restart-growth G] "
               "[--relax-sweeps N] [--relax-omega W] [--relax-min-omega W] "
               "[--history-stride N] [--history-limit N] "
               "[--coarse-correction] [--coarse-iters N] [--coarse-sweeps N] "
               "[--coarse-rel-tol T] [--coarse-abs-tol T] [--coarse-min-scale S]\n");
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
      sim.cg_coarse_correction_min_scale > 1.0) {
    usage();
    return 2;
  }
  const double activeRhoRatio = sim.phase.rho_l / sim.phase.rho_g;
  const bool highDensityRatio = activeRhoRatio >= 1000.0;
  const bool requireConverged = hasFlag(argc, argv, "--require-converged") || highDensityRatio;
  sim.initBubbleTankInterfaceBand();

  size_t n0 = sim.particles.size();
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
  std::printf("particles_start=%zu\n", n0);
  std::printf("particles_end=%zu\n", sim.particles.size());
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
  if (!finite) ok = false;
  if (sim.particles.size() != n0) ok = false;
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
