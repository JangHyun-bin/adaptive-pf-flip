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
               "[--max-fine-leaves N]\n");
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
  double dt = argDouble(argc, argv, "--dt", mr.dt);
  int cgIters = argInt(argc, argv, "--cg-iters", mr.cg_iters);
  sparse.dt = dt;
  mr.dt = dt;
  sparse.cg_iters = cgIters;
  mr.cg_iters = cgIters;
  mr.dynamic_hysteresis_cells = argInt(argc, argv, "--hysteresis", mr.dynamic_hysteresis_cells);
  mr.dynamic_max_fine_leaves = argInt(argc, argv, "--max-fine-leaves", mr.dynamic_max_fine_leaves);

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

  std::printf("dims=%d,%d,%d\n", nx, ny, nz);
  std::printf("steps=%d\n", steps);
  std::printf("dt=%.9g\n", dt);
  std::printf("cg_iters=%d\n", cgIters);
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

  std::printf("status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
