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
               "[--narrow-band-air] [--narrow-band-radius N] "
               "[--gas-coarsening] [--gas-particles-per-cell N] "
               "[--gas-coarsening-seed N] "
               "[--liquid-coarsening] [--liquid-particles-per-cell N] "
               "[--liquid-coarsening-seed N]\n");
}

} // namespace

int main(int argc, char** argv) {
  const char* scenario = argString(argc, argv, "--scenario", "rt");
  int nx = argInt(argc, argv, "--nx", 12);
  int ny = argInt(argc, argv, "--ny", 18);
  int nz = argInt(argc, argv, "--nz", 12);
  int steps = argInt(argc, argv, "--steps", 40);

  if (nx < 4 || ny < 4 || nz < 4 || steps < 0) {
    usage();
    return 2;
  }
  if (std::strcmp(scenario, "rt") != 0 && std::strcmp(scenario, "bubble") != 0) {
    usage();
    return 2;
  }

  SparseSim3DTP sim(nx, ny, nz, 1.0);
  sim.dt = argDouble(argc, argv, "--dt", sim.dt);
  sim.cg_iters = argInt(argc, argv, "--cg-iters", sim.cg_iters);
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
  if (sim.narrow_band_air_radius < 0 ||
      sim.gas_particles_per_cell_target <= 0 ||
      sim.liquid_particles_per_cell_target <= 0) {
    usage();
    return 2;
  }

  if (std::strcmp(scenario, "rt") == 0) {
    sim.initRayleighTaylor();
  } else {
    sim.initBubbleTank();
  }

  size_t n0 = sim.particles.size();
  size_t liquidCount0 = countType(sim.particles, 0);
  size_t gasCount0 = countType(sim.particles, 1);
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
  bool finite = finiteParticles(sim.particles);
  size_t totalBlocks = sim.grid.totalCellBlocks();
  long long elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

  std::printf("scenario=%s\n", scenario);
  std::printf("dims=%d,%d,%d\n", nx, ny, nz);
  std::printf("steps=%d\n", steps);
  std::printf("dt=%.9g\n", sim.dt);
  std::printf("cg_iters=%d\n", sim.cg_iters);
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
  std::printf("particles_start=%zu\n", n0);
  std::printf("particles_end=%zu\n", sim.particles.size());
  std::printf("liquid_particles_start=%zu\n", liquidCount0);
  std::printf("liquid_particles_end=%zu\n", liquidCount1);
  std::printf("gas_particles_start=%zu\n", gasCount0);
  std::printf("gas_particles_end=%zu\n", gasCount1);
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
  std::printf("liquid_particle_coarsening_cells_last=%d\n",
              sim.liquid_particle_coarsening_cells_last);
  std::printf("liquid_particle_coarsening_overfull_cells_last=%d\n",
              sim.liquid_particle_coarsening_overfull_cells_last);
  std::printf("liquid_particle_coarsening_before_last=%d\n",
              sim.liquid_particle_coarsening_before_last);
  std::printf("liquid_particle_coarsening_after_last=%d\n",
              sim.liquid_particle_coarsening_after_last);
  std::printf("finite=%s\n", finite ? "true" : "false");
  std::printf("active_pressure_blocks_max=%zu\n", maxActive);
  std::printf("active_pressure_blocks_total=%zu\n", totalBlocks);
  std::printf("heavy_mean_y_start=%.9g\n", heavy0);
  std::printf("heavy_mean_y_end=%.9g\n", heavy1);
  std::printf("gas_mean_y_start=%.9g\n", gas0);
  std::printf("gas_mean_y_end=%.9g\n", gas1);
  std::printf("elapsed_ms=%lld\n", elapsedMs);

  bool ok = true;
  if (!finite) ok = false;
  if (sim.narrow_band_air || sim.gas_particle_coarsening || sim.liquid_particle_coarsening) {
    if (sim.particles.size() > n0) ok = false;
  } else if (sim.particles.size() != n0) {
    ok = false;
  }
  if (std::strcmp(scenario, "rt") == 0 && !(heavy1 < heavy0)) ok = false;
  if (std::strcmp(scenario, "bubble") == 0) {
    if (!(gas1 > gas0)) ok = false;
    if (!(maxActive < totalBlocks)) ok = false;
  }

  std::printf("status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
