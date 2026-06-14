#include "driver/multires_sim3d_tp.h"
#include "driver/sparse_sim3d_tp.h"

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
               "usage: bench_multires_sparse3d_tp [--nx N] [--ny N] [--nz N] "
               "[--steps N] [--dt DT] [--cg-iters N] [--hysteresis N] "
               "[--max-fine-leaves N] [--cg-rel-tol T] [--rho-ratio R] "
               "[--require-converged] [--no-jacobi] [--flexible-cg] "
               "[--no-restart] [--restart-growth G] "
               "[--relax-sweeps N] [--relax-omega W] [--relax-min-omega W] "
               "[--history-stride N] [--history-limit N]\n");
}

} // namespace

int main(int argc, char** argv) {
  int nx = argInt(argc, argv, "--nx", 12);
  int ny = argInt(argc, argv, "--ny", 18);
  int nz = argInt(argc, argv, "--nz", 12);
  int steps = argInt(argc, argv, "--steps", 4);

  if (nx < 4 || ny < 4 || nz < 4 || steps < 0) {
    usage();
    return 2;
  }

  SparseSim3DTP sparse(nx, ny, nz, 1.0);
  MRSim3DTP mr(nx, ny, nz, 1.0);
  double requestedRhoRatio = argDouble(argc, argv, "--rho-ratio", 0.0);
  if (requestedRhoRatio > 0.0) {
    sparse.phase.rho_l = requestedRhoRatio;
    sparse.phase.rho_g = 1.0;
    mr.phase.rho_l = requestedRhoRatio;
    mr.phase.rho_g = 1.0;
  }
  double dt = argDouble(argc, argv, "--dt", mr.dt);
  int cgIters = argInt(argc, argv, "--cg-iters", mr.cg_iters);
  sparse.dt = dt;
  mr.dt = dt;
  sparse.cg_iters = cgIters;
  mr.cg_iters = cgIters;
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
  if (requestedRhoRatio < 0.0 ||
      sparse.phase.rho_l <= 0.0 ||
      sparse.phase.rho_g <= 0.0 ||
      mr.phase.rho_l <= 0.0 ||
      mr.phase.rho_g <= 0.0 ||
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

  sparse.initBubbleTank();
  mr.initBubbleTankInterfaceBand();

  size_t sparseN0 = sparse.particles.size();
  size_t mrN0 = mr.particles.size();
  double sparseGas0 = meanY(sparse.particles, 1);
  double mrGas0 = meanY(mr.particles, 1);
  size_t sparseMaxBlocks = 0;

  auto sparseStart = std::chrono::steady_clock::now();
  for (int s = 0; s < steps; ++s) {
    sparse.step();
    sparseMaxBlocks = std::max(sparseMaxBlocks, sparse.grid.activeCellBlocks());
  }
  auto sparseEnd = std::chrono::steady_clock::now();

  auto mrStart = std::chrono::steady_clock::now();
  for (int s = 0; s < steps; ++s) {
    mr.step();
  }
  auto mrEnd = std::chrono::steady_clock::now();

  double sparseGas1 = meanY(sparse.particles, 1);
  double mrGas1 = meanY(mr.particles, 1);
  bool sparseFinite = finiteParticles(sparse.particles);
  bool mrFinite = finiteParticles(mr.particles);
  int mrPressureCells = mr.activePressureCellCount();
  int finePressureCells = nx * ny * nz;
  double pressureRatio = finePressureCells > 0 ? static_cast<double>(mrPressureCells) / finePressureCells : 0.0;
  double pressureReduction = 1.0 - pressureRatio;
  long long sparseMs = std::chrono::duration_cast<std::chrono::milliseconds>(sparseEnd - sparseStart).count();
  long long mrMs = std::chrono::duration_cast<std::chrono::milliseconds>(mrEnd - mrStart).count();
  double sparseRise = sparseGas1 - sparseGas0;
  double mrRise = mrGas1 - mrGas0;
  double riseDelta = std::abs(mrRise - sparseRise);
  double allowedRiseDelta = std::max(0.35, std::abs(sparseRise) * 3.0);
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

  std::printf("dims=%d,%d,%d\n", nx, ny, nz);
  std::printf("steps=%d\n", steps);
  std::printf("dt=%.9g\n", dt);
  std::printf("rho_l=%.9g\n", mr.phase.rho_l);
  std::printf("rho_g=%.9g\n", mr.phase.rho_g);
  std::printf("rho_ratio=%.9g\n", activeRhoRatio);
  std::printf("high_density_ratio=%s\n", highDensityRatio ? "true" : "false");
  std::printf("require_converged=%s\n", requireConverged ? "true" : "false");
  std::printf("cg_iters=%d\n", cgIters);
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
  std::printf("sparse_particles_start=%zu\n", sparseN0);
  std::printf("sparse_particles_end=%zu\n", sparse.particles.size());
  std::printf("mr_particles_start=%zu\n", mrN0);
  std::printf("mr_particles_end=%zu\n", mr.particles.size());
  std::printf("sparse_finite=%s\n", sparseFinite ? "true" : "false");
  std::printf("mr_finite=%s\n", mrFinite ? "true" : "false");
  std::printf("sparse_gas_mean_y_start=%.9g\n", sparseGas0);
  std::printf("sparse_gas_mean_y_end=%.9g\n", sparseGas1);
  std::printf("mr_gas_mean_y_start=%.9g\n", mrGas0);
  std::printf("mr_gas_mean_y_end=%.9g\n", mrGas1);
  std::printf("sparse_active_pressure_blocks_max=%zu\n", sparseMaxBlocks);
  std::printf("sparse_total_pressure_blocks=%zu\n", sparse.grid.totalCellBlocks());
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
  std::printf("fine_pressure_cells=%d\n", finePressureCells);
  std::printf("mr_u_faces=%d\n", mr.uFaceCount());
  std::printf("mr_v_faces=%d\n", mr.vFaceCount());
  std::printf("mr_w_faces=%d\n", mr.wFaceCount());
  std::printf("mr_pressure_cell_ratio=%.9g\n", pressureRatio);
  std::printf("mr_pressure_cell_reduction=%.9g\n", pressureReduction);
  std::printf("sparse_elapsed_ms=%lld\n", sparseMs);
  std::printf("mr_elapsed_ms=%lld\n", mrMs);
  std::printf("rise_delta=%.9g\n", riseDelta);
  std::printf("allowed_rise_delta=%.9g\n", allowedRiseDelta);

  bool ok = true;
  if (!sparseFinite || !mrFinite) ok = false;
  if (sparse.particles.size() != sparseN0 || mr.particles.size() != mrN0) ok = false;
  if (sparseN0 != mrN0 || sparse.particles.size() != mr.particles.size()) ok = false;
  if (!(sparseRise > 0.0) || !(mrRise > 0.0)) ok = false;
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
