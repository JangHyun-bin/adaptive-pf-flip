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

SparseMetrics runSparseBubble(SparseSim3DTP& sim, int steps) {
  sim.initBubbleTank();
  SparseMetrics metrics;
  metrics.particlesStart = sim.particles.size();
  metrics.liquidStart = countType(sim.particles, 0);
  metrics.gasCountStart = countType(sim.particles, 1);
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
  int nx = argInt(argc, argv, "--nx", 12);
  int ny = argInt(argc, argv, "--ny", 18);
  int nz = argInt(argc, argv, "--nz", 12);
  int steps = argInt(argc, argv, "--steps", 4);

  if (nx < 4 || ny < 4 || nz < 4 || steps < 0) {
    usage();
    return 2;
  }

  SparseSim3DTP sparse(nx, ny, nz, 1.0);
  SparseSim3DTP sparseAdaptive(nx, ny, nz, 1.0);
  MRSim3DTP mr(nx, ny, nz, 1.0);
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
  sparse.cg_iters = cgIters;
  sparseAdaptive.cg_iters = cgIters;
  mr.cg_iters = cgIters;
  sparseAdaptive.narrow_band_air = hasFlag(argc, argv, "--sparse-narrow-band-air");
  sparseAdaptive.narrow_band_air_radius =
    argInt(argc, argv, "--sparse-narrow-band-radius",
           sparseAdaptive.narrow_band_air_radius);
  sparseAdaptive.gas_particle_coarsening =
    hasFlag(argc, argv, "--sparse-gas-coarsening");
  sparseAdaptive.gas_particles_per_cell_target =
    argInt(argc, argv, "--sparse-gas-particles-per-cell",
           sparseAdaptive.gas_particles_per_cell_target);
  sparseAdaptive.gas_particle_coarsening_seed =
    argUInt(argc, argv, "--sparse-gas-coarsening-seed",
            sparseAdaptive.gas_particle_coarsening_seed);
  sparseAdaptive.liquid_particle_coarsening =
    hasFlag(argc, argv, "--sparse-liquid-coarsening");
  sparseAdaptive.liquid_particles_per_cell_target =
    argInt(argc, argv, "--sparse-liquid-particles-per-cell",
           sparseAdaptive.liquid_particles_per_cell_target);
  sparseAdaptive.liquid_particle_coarsening_seed =
    argUInt(argc, argv, "--sparse-liquid-coarsening-seed",
            sparseAdaptive.liquid_particle_coarsening_seed);
  sparseAdaptive.liquid_particle_refill =
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
  mrAdaptive.narrow_band_air = hasFlag(argc, argv, "--mr-narrow-band-air");
  mrAdaptive.narrow_band_air_radius =
    argInt(argc, argv, "--mr-narrow-band-radius",
           mrAdaptive.narrow_band_air_radius);
  mrAdaptive.gas_particle_coarsening =
    hasFlag(argc, argv, "--mr-gas-coarsening");
  mrAdaptive.gas_particles_per_cell_target =
    argInt(argc, argv, "--mr-gas-particles-per-cell",
           mrAdaptive.gas_particles_per_cell_target);
  mrAdaptive.gas_particle_coarsening_seed =
    argUInt(argc, argv, "--mr-gas-coarsening-seed",
            mrAdaptive.gas_particle_coarsening_seed);
  mrAdaptive.liquid_particle_coarsening =
    hasFlag(argc, argv, "--mr-liquid-coarsening");
  mrAdaptive.liquid_particles_per_cell_target =
    argInt(argc, argv, "--mr-liquid-particles-per-cell",
           mrAdaptive.liquid_particles_per_cell_target);
  mrAdaptive.liquid_particle_coarsening_seed =
    argUInt(argc, argv, "--mr-liquid-coarsening-seed",
            mrAdaptive.liquid_particle_coarsening_seed);
  mrAdaptive.liquid_particle_refill =
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

  SparseMetrics sparseMetrics = runSparseBubble(sparse, steps);
  SparseMetrics adaptiveMetrics;
  if (sparseAdaptivity) {
    adaptiveMetrics = runSparseBubble(sparseAdaptive, steps);
  } else {
    adaptiveMetrics = sparseMetrics;
  }

  mr.initBubbleTankInterfaceBand();

  size_t mrN0 = mr.particles.size();
  size_t mrLiquid0 = countType(mr.particles, 0);
  size_t mrGasCount0 = countType(mr.particles, 1);
  double mrGas0 = meanY(mr.particles, 1);

  auto mrStart = std::chrono::steady_clock::now();
  for (int s = 0; s < steps; ++s) {
    mr.step();
  }
  auto mrEnd = std::chrono::steady_clock::now();

  double mrGas1 = meanY(mr.particles, 1);
  size_t mrLiquid1 = countType(mr.particles, 0);
  size_t mrGasCount1 = countType(mr.particles, 1);
  bool mrFinite = finiteParticles(mr.particles);
  int mrPressureCells = mr.activePressureCellCount();
  long long mrMs = std::chrono::duration_cast<std::chrono::milliseconds>(mrEnd - mrStart).count();
  size_t adaptiveMrN0 = mrN0;
  size_t adaptiveMrN1 = mr.particles.size();
  size_t adaptiveMrLiquid0 = mrLiquid0;
  size_t adaptiveMrLiquid1 = mrLiquid1;
  size_t adaptiveMrGasCount0 = mrGasCount0;
  size_t adaptiveMrGasCount1 = mrGasCount1;
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
    adaptiveMrN0 = mrAdaptive.particles.size();
    adaptiveMrLiquid0 = countType(mrAdaptive.particles, 0);
    adaptiveMrGasCount0 = countType(mrAdaptive.particles, 1);
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
  std::printf("dt=%.9g\n", dt);
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
  std::printf("mr_liquid_particles_start=%zu\n", mrLiquid0);
  std::printf("mr_liquid_particles_end=%zu\n", mrLiquid1);
  std::printf("mr_gas_particles_start=%zu\n", mrGasCount0);
  std::printf("mr_gas_particles_end=%zu\n", mrGasCount1);
  std::printf("adaptive_mr_liquid_particles_start=%zu\n", adaptiveMrLiquid0);
  std::printf("adaptive_mr_liquid_particles_end=%zu\n", adaptiveMrLiquid1);
  std::printf("adaptive_mr_gas_particles_start=%zu\n", adaptiveMrGasCount0);
  std::printf("adaptive_mr_gas_particles_end=%zu\n", adaptiveMrGasCount1);
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
  if (!sparseMetrics.finite || !mrFinite) ok = false;
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
  if (!(sparseRise > 0.0) || !(mrRise > 0.0)) ok = false;
  if (sparseAdaptivity) {
    if (!adaptiveMetrics.finite) ok = false;
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
    if (!(adaptiveRise > 0.0)) ok = false;
    if (!(adaptiveRiseDelta <= allowedAdaptiveRiseDelta)) ok = false;
  }
  if (mrAdaptivity) {
    if (!adaptiveMrFinite) ok = false;
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
