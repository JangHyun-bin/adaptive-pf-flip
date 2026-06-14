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
               "usage: bench_multires3d_solver [--nx N] [--ny N] [--nz N] "
               "[--steps N] [--dt DT] [--cg-iters N] [--abs-tol T] "
               "[--rel-tol T] [--rho-ratio R] [--hysteresis N] "
               "[--require-converged] "
               "[--max-fine-leaves N] [--no-restart] [--restart-growth G] "
               "[--relax-sweeps N] [--relax-omega W] [--relax-min-omega W] "
               "[--history-stride N] [--history-limit N]\n");
}

struct Variant {
  const char* name = "";
  bool jacobi = true;
  bool flexibleBeta = false;
  double relTol = 0.0;
};

bool runVariant(const Variant& variant,
                int nx,
                int ny,
                int nz,
                int steps,
                double dt,
                int cgIters,
                double absTol,
                double rhoRatio,
                int hysteresis,
                int maxFineLeaves,
                bool requireConverged,
                bool adaptiveRestart,
                double restartGrowth,
                int relaxSweeps,
                double relaxOmega,
                double relaxMinOmega,
                int historyStride,
                int historyLimit) {
  MRSim3DTP sim(nx, ny, nz, 1.0);
  if (rhoRatio > 0.0) {
    sim.phase.rho_l = rhoRatio;
    sim.phase.rho_g = 1.0;
  }
  sim.dt = dt;
  sim.cg_iters = cgIters;
  sim.cg_tol = absTol;
  sim.cg_rel_tol = variant.relTol;
  sim.cg_jacobi_preconditioner = variant.jacobi;
  sim.cg_flexible_beta = variant.flexibleBeta;
  sim.cg_adaptive_restart = adaptiveRestart;
  sim.cg_restart_growth = restartGrowth;
  sim.cg_relaxation_sweeps = relaxSweeps;
  sim.cg_relaxation_omega = relaxOmega;
  sim.cg_relaxation_min_omega = relaxMinOmega;
  sim.cg_residual_history_stride = historyStride;
  sim.cg_residual_history_limit = historyLimit;
  sim.dynamic_hysteresis_cells = hysteresis;
  sim.dynamic_max_fine_leaves = maxFineLeaves;
  sim.initBubbleTankInterfaceBand();

  const size_t n0 = sim.particles.size();
  const double gas0 = meanY(sim.particles, 1);

  auto start = std::chrono::steady_clock::now();
  for (int s = 0; s < steps; ++s) {
    sim.step();
  }
  auto end = std::chrono::steady_clock::now();

  const double gas1 = meanY(sim.particles, 1);
  const bool finite = finiteParticles(sim.particles);
  const bool stableCount = sim.particles.size() == n0;
  const long long elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
  const MRPressureSolveStats3D& st = sim.last_pressure_stats;
  const bool residualFinite = std::isfinite(st.initial_residual) && std::isfinite(st.final_residual);
  const bool convergenceOk =
    !requireConverged ||
    steps == 0 ||
    (st.converged && st.final_residual <= st.effective_tolerance);
  const bool ok = finite && stableCount && residualFinite && !st.breakdown && convergenceOk;
  const double rise = gas1 - gas0;
  const double pressureRatio = (nx * ny * nz) > 0
    ? static_cast<double>(sim.activePressureCellCount()) / static_cast<double>(nx * ny * nz)
    : 0.0;

  std::printf("result variant=%s jacobi=%s flexible_beta=%s rel_tol=%.9g abs_tol=%.9g "
              "adaptive_restart=%s restart_growth=%.9g "
              "steps=%d elapsed_ms=%lld particles=%zu stable_particles=%s finite=%s "
              "gas_rise=%.9g active_cells=%d pressure_ratio=%.9g "
              "require_converged=%s convergence_ok=%s "
              "iters=%d max_iters=%d initial_residual=%.9g final_residual=%.9g "
              "min_residual=%.9g max_residual=%.9g effective_tol=%.9g "
              "restarts=%d beta_resets=%d relax_sweeps=%d relax_accepted=%d relax_rejected=%d "
              "relax_final_omega=%.9g history_count=%zu history_first=%.9g history_last=%.9g "
              "history_truncated=%s converged=%s breakdown=%s "
              "fine_leaves=%zu coarse_leaves=%zu status=%s\n",
              variant.name,
              variant.jacobi ? "true" : "false",
              variant.flexibleBeta ? "true" : "false",
              variant.relTol,
              absTol,
              st.adaptive_restart ? "true" : "false",
              st.restart_growth_threshold,
              steps,
              elapsedMs,
              sim.particles.size(),
              stableCount ? "true" : "false",
              finite ? "true" : "false",
              rise,
              st.active_cells,
              pressureRatio,
              requireConverged ? "true" : "false",
              convergenceOk ? "true" : "false",
              st.iterations,
              st.max_iterations,
              st.initial_residual,
              st.final_residual,
              st.min_residual,
              st.max_residual,
              st.effective_tolerance,
              st.restarts,
              st.beta_resets,
              st.relaxation_sweeps,
              st.relaxation_accepted,
              st.relaxation_rejected,
              st.relaxation_final_omega,
              st.residual_history.size(),
              st.residual_history.empty() ? 0.0 : st.residual_history.front(),
              st.residual_history.empty() ? 0.0 : st.residual_history.back(),
              st.residual_history_truncated ? "true" : "false",
              st.converged ? "true" : "false",
              st.breakdown ? "true" : "false",
              sim.layout.countLevel(0),
              sim.layout.countLevel(1),
              ok ? "ok" : "fail");
  return ok;
}

} // namespace

int main(int argc, char** argv) {
  int nx = argInt(argc, argv, "--nx", 12);
  int ny = argInt(argc, argv, "--ny", 18);
  int nz = argInt(argc, argv, "--nz", 12);
  int steps = argInt(argc, argv, "--steps", 4);

  MRSim3DTP defaults(nx, ny, nz, 1.0);
  double dt = argDouble(argc, argv, "--dt", defaults.dt);
  int cgIters = argInt(argc, argv, "--cg-iters", defaults.cg_iters);
  double absTol = argDouble(argc, argv, "--abs-tol", defaults.cg_tol);
  double relTol = argDouble(argc, argv, "--rel-tol", 1e-5);
  double rhoRatio = argDouble(argc, argv, "--rho-ratio", 0.0);
  int hysteresis = argInt(argc, argv, "--hysteresis", defaults.dynamic_hysteresis_cells);
  int maxFineLeaves = argInt(argc, argv, "--max-fine-leaves", defaults.dynamic_max_fine_leaves);
  bool adaptiveRestart = !hasFlag(argc, argv, "--no-restart");
  double restartGrowth = argDouble(argc, argv, "--restart-growth", defaults.cg_restart_growth);
  int relaxSweeps = argInt(argc, argv, "--relax-sweeps", defaults.cg_relaxation_sweeps);
  double relaxOmega = argDouble(argc, argv, "--relax-omega", defaults.cg_relaxation_omega);
  double relaxMinOmega = argDouble(argc, argv, "--relax-min-omega", defaults.cg_relaxation_min_omega);
  int historyStride = argInt(argc, argv, "--history-stride", defaults.cg_residual_history_stride);
  int historyLimit = argInt(argc, argv, "--history-limit", defaults.cg_residual_history_limit);

  if (nx < 4 || ny < 4 || nz < 4 || steps < 0 ||
      cgIters < 0 || absTol < 0.0 || relTol < 0.0 || rhoRatio < 0.0 ||
      hysteresis < 0 || maxFineLeaves < 0 || restartGrowth < 0.0 ||
      relaxSweeps < 0 || relaxOmega < 0.0 || relaxMinOmega < 0.0 ||
      historyStride < 0 || historyLimit < 0) {
    usage();
    return 2;
  }
  const bool highDensityRatio = rhoRatio >= 1000.0;
  const bool requireConverged = hasFlag(argc, argv, "--require-converged") || highDensityRatio;

  std::printf("dims=%d,%d,%d\n", nx, ny, nz);
  std::printf("steps=%d\n", steps);
  std::printf("dt=%.9g\n", dt);
  std::printf("cg_iters=%d\n", cgIters);
  std::printf("abs_tol=%.9g\n", absTol);
  std::printf("rel_tol=%.9g\n", relTol);
  std::printf("rho_ratio=%.9g\n", rhoRatio);
  std::printf("high_density_ratio=%s\n", highDensityRatio ? "true" : "false");
  std::printf("require_converged=%s\n", requireConverged ? "true" : "false");
  std::printf("hysteresis=%d\n", hysteresis);
  std::printf("max_fine_leaves=%d\n", maxFineLeaves);
  std::printf("adaptive_restart=%s\n", adaptiveRestart ? "true" : "false");
  std::printf("restart_growth=%.9g\n", restartGrowth);
  std::printf("relax_sweeps=%d\n", relaxSweeps);
  std::printf("relax_omega=%.9g\n", relaxOmega);
  std::printf("relax_min_omega=%.9g\n", relaxMinOmega);
  std::printf("history_stride=%d\n", historyStride);
  std::printf("history_limit=%d\n", historyLimit);

  Variant variants[] = {
    {"jacobi_abs", true, false, 0.0},
    {"jacobi_rel", true, false, relTol},
    {"flex_jacobi_rel", true, true, relTol},
    {"no_jacobi_rel", false, false, relTol},
  };

  bool ok = true;
  for (const Variant& variant : variants) {
    ok = runVariant(variant, nx, ny, nz, steps, dt, cgIters, absTol,
                    rhoRatio, hysteresis, maxFineLeaves,
                    requireConverged,
                    adaptiveRestart, restartGrowth,
                    relaxSweeps, relaxOmega, relaxMinOmega,
                    historyStride, historyLimit) && ok;
  }

  std::printf("overall_status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
