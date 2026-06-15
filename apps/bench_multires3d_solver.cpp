#include "driver/multires_sim3d_tp.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

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
               "[--history-stride N] [--history-limit N] "
               "[--coarse-iters N] [--coarse-sweeps N] "
               "[--coarse-rel-tol T] [--coarse-abs-tol T] [--coarse-min-scale S] "
               "[--coarse-pre-iters N] [--coarse-pre-rel-tol T] "
               "[--coarse-pre-abs-tol T] [--coarse-pre-scale S] "
               "[--coarse-pre-min-rz-gain G] "
               "[--coarse-pre-sweep]\n");
}

struct Variant {
  std::string name;
  bool jacobi = true;
  bool flexibleBeta = false;
  bool coarseCorrection = false;
  bool coarsePreconditioner = false;
  double relTol = 0.0;
  int coarsePreItersOverride = -1;
  double coarsePreScaleOverride = -1.0;
  double coarsePreMinRzGainOverride = -1.0;
};

struct RunResult {
  std::string name;
  bool ok = false;
  int iterations = 0;
  int maxIterations = 0;
  long long elapsedMs = 0;
  double initialResidual = 0.0;
  double finalResidual = 0.0;
  double effectiveTolerance = 0.0;
  int coarseCorrectionIterations = 0;
  int coarsePreconditionerIterations = 0;
  int coarsePreconditionerApplications = 0;
  int coarsePreconditionerAcceptedApplications = 0;
  int coarsePreconditionerRejectedApplications = 0;
  double coarsePreconditionerScale = 0.0;
  double coarsePreconditionerMinRzGain = 0.0;
  double coarsePreconditionerLastRzGain = 0.0;
  bool converged = false;
  bool breakdown = false;
};

int coarseWork(const RunResult& result) {
  return result.coarseCorrectionIterations +
         result.coarsePreconditionerIterations;
}

int totalWork(const RunResult& result) {
  return result.iterations + coarseWork(result);
}

void printSummary(const std::vector<RunResult>& results) {
  if (results.empty()) return;

  const RunResult* baseline = &results.front();
  for (const RunResult& result : results) {
    if (result.name == "jacobi_rel") {
      baseline = &result;
      break;
    }
  }

  const int baselineIterations = baseline->iterations;
  const long long baselineElapsedMs = baseline->elapsedMs;
  const int baselineWork = totalWork(*baseline);

  std::printf("summary_baseline=%s baseline_iters=%d baseline_elapsed_ms=%lld "
              "baseline_work=%d\n",
              baseline->name.c_str(),
              baselineIterations,
              baselineElapsedMs,
              baselineWork);

  for (const RunResult& result : results) {
    const int resultCoarseWork = coarseWork(result);
    const int resultTotalWork = totalWork(result);
    const double finalOverTol =
      (result.effectiveTolerance > 0.0 && std::isfinite(result.finalResidual))
        ? result.finalResidual / result.effectiveTolerance
        : 0.0;

    std::printf("summary variant=%s status=%s iters=%d iter_delta=%+d "
                "elapsed_ms=%lld elapsed_delta_ms=%+lld coarse_work=%d "
                "total_work=%d work_delta=%+d final_over_tol=%.9g "
                "converged=%s breakdown=%s coarse_pre_apps=%d "
                "coarse_pre_accepted=%d coarse_pre_rejected=%d "
                "coarse_pre_scale=%.9g coarse_pre_min_rz_gain=%.9g "
                "coarse_pre_last_rz_gain=%.9g\n",
                result.name.c_str(),
                result.ok ? "ok" : "fail",
                result.iterations,
                result.iterations - baselineIterations,
                result.elapsedMs,
                result.elapsedMs - baselineElapsedMs,
                resultCoarseWork,
                resultTotalWork,
                resultTotalWork - baselineWork,
                finalOverTol,
                result.converged ? "true" : "false",
                result.breakdown ? "true" : "false",
                result.coarsePreconditionerApplications,
                result.coarsePreconditionerAcceptedApplications,
                result.coarsePreconditionerRejectedApplications,
                result.coarsePreconditionerScale,
                result.coarsePreconditionerMinRzGain,
                result.coarsePreconditionerLastRzGain);
  }
}

RunResult runVariant(const Variant& variant,
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
                     int historyLimit,
                     int coarseIters,
                     int coarseSweeps,
                     double coarseRelTol,
                     double coarseAbsTol,
                     double coarseMinScale,
                     int coarsePreIters,
                     double coarsePreRelTol,
                     double coarsePreAbsTol,
                     double coarsePreScale,
                     double coarsePreMinRzGain) {
  const int actualCoarsePreIters =
    variant.coarsePreItersOverride >= 0 ? variant.coarsePreItersOverride : coarsePreIters;
  const double actualCoarsePreScale =
    variant.coarsePreScaleOverride >= 0.0 ? variant.coarsePreScaleOverride : coarsePreScale;
  const double actualCoarsePreMinRzGain =
    variant.coarsePreMinRzGainOverride >= 0.0
      ? variant.coarsePreMinRzGainOverride
      : coarsePreMinRzGain;

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
  sim.cg_coarse_correction = variant.coarseCorrection;
  sim.cg_coarse_correction_iters = coarseIters;
  sim.cg_coarse_correction_sweeps = coarseSweeps;
  sim.cg_coarse_correction_rel_tol = coarseRelTol;
  sim.cg_coarse_correction_abs_tol = coarseAbsTol;
  sim.cg_coarse_correction_min_scale = coarseMinScale;
  sim.cg_coarse_preconditioner = variant.coarsePreconditioner;
  sim.cg_coarse_preconditioner_iters = actualCoarsePreIters;
  sim.cg_coarse_preconditioner_rel_tol = coarsePreRelTol;
  sim.cg_coarse_preconditioner_abs_tol = coarsePreAbsTol;
  sim.cg_coarse_preconditioner_scale = actualCoarsePreScale;
  sim.cg_coarse_preconditioner_min_rz_gain = actualCoarsePreMinRzGain;
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

  RunResult result;
  result.name = variant.name;
  result.ok = ok;
  result.iterations = st.iterations;
  result.maxIterations = st.max_iterations;
  result.elapsedMs = elapsedMs;
  result.initialResidual = st.initial_residual;
  result.finalResidual = st.final_residual;
  result.effectiveTolerance = st.effective_tolerance;
  result.coarseCorrectionIterations = st.coarse_correction_iterations;
  result.coarsePreconditionerIterations = st.coarse_preconditioner_iterations;
  result.coarsePreconditionerApplications = st.coarse_preconditioner_applications;
  result.coarsePreconditionerAcceptedApplications =
    st.coarse_preconditioner_accepted_applications;
  result.coarsePreconditionerRejectedApplications =
    st.coarse_preconditioner_rejected_applications;
  result.coarsePreconditionerScale = st.coarse_preconditioner_scale;
  result.coarsePreconditionerMinRzGain = st.coarse_preconditioner_min_rz_gain;
  result.coarsePreconditionerLastRzGain = st.coarse_preconditioner_last_rz_gain;
  result.converged = st.converged;
  result.breakdown = st.breakdown;

  std::printf("result variant=%s jacobi=%s flexible_beta=%s coarse_correction=%s "
              "coarse_preconditioner=%s "
              "rel_tol=%.9g abs_tol=%.9g "
              "adaptive_restart=%s restart_growth=%.9g "
              "steps=%d elapsed_ms=%lld particles=%zu stable_particles=%s finite=%s "
              "gas_rise=%.9g active_cells=%d pressure_ratio=%.9g "
              "require_converged=%s convergence_ok=%s "
              "iters=%d max_iters=%d initial_residual=%.9g final_residual=%.9g "
              "min_residual=%.9g max_residual=%.9g effective_tol=%.9g "
              "restarts=%d beta_resets=%d relax_sweeps=%d relax_accepted=%d relax_rejected=%d "
              "relax_final_omega=%.9g history_count=%zu history_first=%.9g history_last=%.9g "
              "coarse_cells=%d coarse_iters=%d coarse_sweeps=%d coarse_accepted_sweeps=%d "
              "coarse_rejected_sweeps=%d coarse_last_scale=%.9g coarse_accepted=%s "
              "coarse_converged=%s coarse_breakdown=%s coarse_initial=%.9g coarse_final=%.9g "
              "coarse_pre_apps=%d coarse_pre_accepted=%d coarse_pre_rejected=%d "
              "coarse_pre_iters=%d coarse_pre_breakdown=%s coarse_pre_scale=%.9g "
              "coarse_pre_min_rz_gain=%.9g coarse_pre_last_rz_gain=%.9g "
              "history_truncated=%s converged=%s breakdown=%s "
              "fine_leaves=%zu coarse_leaves=%zu status=%s\n",
              variant.name.c_str(),
              variant.jacobi ? "true" : "false",
              variant.flexibleBeta ? "true" : "false",
              variant.coarseCorrection ? "true" : "false",
              variant.coarsePreconditioner ? "true" : "false",
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
              st.coarse_correction_cells,
              st.coarse_correction_iterations,
              st.coarse_correction_sweeps,
              st.coarse_correction_accepted_sweeps,
              st.coarse_correction_rejected_sweeps,
              st.coarse_correction_last_scale,
              st.coarse_correction_accepted ? "true" : "false",
              st.coarse_correction_converged ? "true" : "false",
              st.coarse_correction_breakdown ? "true" : "false",
              st.coarse_correction_initial_residual,
              st.coarse_correction_final_residual,
              st.coarse_preconditioner_applications,
              st.coarse_preconditioner_accepted_applications,
              st.coarse_preconditioner_rejected_applications,
              st.coarse_preconditioner_iterations,
              st.coarse_preconditioner_breakdown ? "true" : "false",
              st.coarse_preconditioner_scale,
              st.coarse_preconditioner_min_rz_gain,
              st.coarse_preconditioner_last_rz_gain,
              st.residual_history_truncated ? "true" : "false",
              st.converged ? "true" : "false",
              st.breakdown ? "true" : "false",
              sim.layout.countLevel(0),
              sim.layout.countLevel(1),
              ok ? "ok" : "fail");
  return result;
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
  int coarseIters = argInt(argc, argv, "--coarse-iters", defaults.cg_coarse_correction_iters);
  int coarseSweeps = argInt(argc, argv, "--coarse-sweeps", defaults.cg_coarse_correction_sweeps);
  double coarseRelTol = argDouble(argc, argv, "--coarse-rel-tol", defaults.cg_coarse_correction_rel_tol);
  double coarseAbsTol = argDouble(argc, argv, "--coarse-abs-tol", defaults.cg_coarse_correction_abs_tol);
  double coarseMinScale = argDouble(argc, argv, "--coarse-min-scale", defaults.cg_coarse_correction_min_scale);
  int coarsePreIters =
    argInt(argc, argv, "--coarse-pre-iters", defaults.cg_coarse_preconditioner_iters);
  double coarsePreRelTol =
    argDouble(argc, argv, "--coarse-pre-rel-tol", defaults.cg_coarse_preconditioner_rel_tol);
  double coarsePreAbsTol =
    argDouble(argc, argv, "--coarse-pre-abs-tol", defaults.cg_coarse_preconditioner_abs_tol);
  double coarsePreScale =
    argDouble(argc, argv, "--coarse-pre-scale", defaults.cg_coarse_preconditioner_scale);
  double coarsePreMinRzGain =
    argDouble(argc, argv, "--coarse-pre-min-rz-gain",
              defaults.cg_coarse_preconditioner_min_rz_gain);
  bool coarsePreSweep = hasFlag(argc, argv, "--coarse-pre-sweep");

  if (nx < 4 || ny < 4 || nz < 4 || steps < 0 ||
      cgIters < 0 || absTol < 0.0 || relTol < 0.0 || rhoRatio < 0.0 ||
      hysteresis < 0 || maxFineLeaves < 0 || restartGrowth < 0.0 ||
      relaxSweeps < 0 || relaxOmega < 0.0 || relaxMinOmega < 0.0 ||
      historyStride < 0 || historyLimit < 0 ||
      coarseIters < 0 || coarseSweeps < 0 ||
      coarseRelTol < 0.0 || coarseAbsTol < 0.0 ||
      coarseMinScale <= 0.0 || coarseMinScale > 1.0 ||
      coarsePreIters < 0 || coarsePreRelTol < 0.0 ||
      coarsePreAbsTol < 0.0 || coarsePreScale < 0.0 ||
      coarsePreMinRzGain < 0.0) {
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
  std::printf("coarse_iters=%d\n", coarseIters);
  std::printf("coarse_sweeps=%d\n", coarseSweeps);
  std::printf("coarse_rel_tol=%.9g\n", coarseRelTol);
  std::printf("coarse_abs_tol=%.9g\n", coarseAbsTol);
  std::printf("coarse_min_scale=%.9g\n", coarseMinScale);
  std::printf("coarse_pre_iters=%d\n", coarsePreIters);
  std::printf("coarse_pre_rel_tol=%.9g\n", coarsePreRelTol);
  std::printf("coarse_pre_abs_tol=%.9g\n", coarsePreAbsTol);
  std::printf("coarse_pre_scale=%.9g\n", coarsePreScale);
  std::printf("coarse_pre_min_rz_gain=%.9g\n", coarsePreMinRzGain);
  std::printf("coarse_pre_sweep=%s\n", coarsePreSweep ? "true" : "false");

  std::vector<Variant> variants = {
    {"jacobi_abs", true, false, false, false, 0.0},
    {"jacobi_rel", true, false, false, false, relTol},
    {"coarse_jacobi_rel", true, false, true, false, relTol},
    {"coarse_pre_jacobi_rel", true, false, false, true, relTol},
    {"flex_jacobi_rel", true, true, false, false, relTol},
    {"no_jacobi_rel", false, false, false, false, relTol},
  };
  if (coarsePreSweep) {
    variants.push_back({"coarse_pre_i2_s025", true, false, false, true, relTol, 2, 0.25});
    variants.push_back({"coarse_pre_i2_s05", true, false, false, true, relTol, 2, 0.5});
    variants.push_back({"coarse_pre_i4_s025", true, false, false, true, relTol, 4, 0.25});
    variants.push_back({"coarse_pre_i4_s05", true, false, false, true, relTol, 4, 0.5});
    variants.push_back({"coarse_pre_i8_s05", true, false, false, true, relTol, 8, 0.5});
    variants.push_back({"coarse_pre_i8_s1", true, false, false, true, relTol, 8, 1.0});
    variants.push_back({"coarse_pre_i4_s05_g01", true, false, false, true, relTol, 4, 0.5, 0.01});
    variants.push_back({"coarse_pre_i4_s05_g05", true, false, false, true, relTol, 4, 0.5, 0.05});
    variants.push_back({"coarse_pre_i8_s1_g01", true, false, false, true, relTol, 8, 1.0, 0.01});
    variants.push_back({"coarse_pre_i8_s1_g05", true, false, false, true, relTol, 8, 1.0, 0.05});
  }

  bool ok = true;
  std::vector<RunResult> results;
  results.reserve(variants.size());
  for (const Variant& variant : variants) {
    RunResult result = runVariant(variant, nx, ny, nz, steps, dt, cgIters, absTol,
                                  rhoRatio, hysteresis, maxFineLeaves,
                                  requireConverged,
                                  adaptiveRestart, restartGrowth,
                                  relaxSweeps, relaxOmega, relaxMinOmega,
                                  historyStride, historyLimit,
                                  coarseIters, coarseSweeps,
                                  coarseRelTol, coarseAbsTol, coarseMinScale,
                                  coarsePreIters, coarsePreRelTol,
                                  coarsePreAbsTol, coarsePreScale,
                                  coarsePreMinRzGain);
    ok = result.ok && ok;
    results.push_back(result);
  }

  printSummary(results);
  std::printf("overall_status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
