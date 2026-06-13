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
               "[--steps N] [--dt DT] [--cg-iters N]\n");
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
  sim.dt = argDouble(argc, argv, "--dt", sim.dt);
  sim.cg_iters = argInt(argc, argv, "--cg-iters", sim.cg_iters);
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

  std::printf("scenario=%s\n", scenario);
  std::printf("dims=%d,%d,%d\n", nx, ny, nz);
  std::printf("steps=%d\n", steps);
  std::printf("dt=%.9g\n", sim.dt);
  std::printf("cg_iters=%d\n", sim.cg_iters);
  std::printf("particles_start=%zu\n", n0);
  std::printf("particles_end=%zu\n", sim.particles.size());
  std::printf("finite=%s\n", finite ? "true" : "false");
  std::printf("gas_mean_y_start=%.9g\n", gas0);
  std::printf("gas_mean_y_end=%.9g\n", gas1);
  std::printf("dynamic_refinement=%s\n", sim.dynamic_refinement ? "true" : "false");
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

  std::printf("status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
