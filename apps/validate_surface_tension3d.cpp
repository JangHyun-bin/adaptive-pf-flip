#include "driver/multires_sim3d_tp.h"
#include "driver/sparse_sim3d_tp.h"

#include <algorithm>
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

struct Config {
  int nx = 8;
  int ny = 12;
  int nz = 8;
  int steps = 4;
  int cg_iters = 20;
  int smoothing_radius = 1;
  double dt = 0.02;
  double strength_min = 0.005;
  double strength_max = 0.08;
  int strength_samples = 4;
  double max_delta_speed = 0.05;
  const char* mode = "both";
};

struct RunResult {
  const char* kind = "";
  int sample = 0;
  double strength = 0.0;
  double gas_start = 0.0;
  double gas_end = 0.0;
  bool finite = false;
  InterfaceDiagnostics3D interface_stats;
  SurfaceTensionStats3D surface_stats;
  bool ok = false;
};

bool surfaceStatsOk(const Config& cfg,
                    const InterfaceDiagnostics3D& interfaceStats,
                    const SurfaceTensionStats3D& surfaceStats) {
  if (!interfaceStats.finite || interfaceStats.sample_cells <= 0) return false;
  if (!surfaceStats.enabled || !surfaceStats.finite) return false;
  if (interfaceStats.interface_cells > 0 && surfaceStats.applied_cells <= 0) return false;
  if (cfg.max_delta_speed > 0.0 &&
      surfaceStats.max_delta_speed > cfg.max_delta_speed + 1e-12) {
    return false;
  }
  if (!surfaceStats.capillary_stable || surfaceStats.capillary_dt_limit <= 0.0) {
    return false;
  }
  if (surfaceStats.curvature_smoothing_radius != cfg.smoothing_radius) {
    return false;
  }
  if (cfg.smoothing_radius > 0 &&
      surfaceStats.smoothed_curvature_abs_max >
        surfaceStats.raw_curvature_abs_max + 1e-12) {
    return false;
  }
  return true;
}

RunResult runSparse(const Config& cfg, int sample, double strength) {
  SparseSim3DTP sim(cfg.nx, cfg.ny, cfg.nz, 1.0);
  sim.dt = cfg.dt;
  sim.cg_iters = cfg.cg_iters;
  sim.surface_tension = true;
  sim.surface_tension_strength = strength;
  sim.surface_tension_max_delta_speed = cfg.max_delta_speed;
  sim.surface_tension_curvature_smoothing_radius = cfg.smoothing_radius;
  sim.initBubbleTank();

  RunResult result;
  result.kind = "sparse";
  result.sample = sample;
  result.strength = strength;
  result.gas_start = meanY(sim.particles, 1);
  for (int i = 0; i < cfg.steps; ++i) sim.step();
  result.gas_end = meanY(sim.particles, 1);
  result.finite = finiteParticles(sim.particles);
  result.interface_stats = sim.interface_diagnostics_last;
  result.surface_stats = sim.surface_tension_stats_last;
  result.ok = result.finite &&
              result.gas_end > result.gas_start &&
              surfaceStatsOk(cfg, result.interface_stats, result.surface_stats);
  return result;
}

RunResult runMR(const Config& cfg, int sample, double strength) {
  MRSim3DTP sim(cfg.nx, cfg.ny, cfg.nz, 1.0);
  sim.dt = cfg.dt;
  sim.cg_iters = cfg.cg_iters;
  sim.surface_tension = true;
  sim.surface_tension_strength = strength;
  sim.surface_tension_max_delta_speed = cfg.max_delta_speed;
  sim.surface_tension_curvature_smoothing_radius = cfg.smoothing_radius;
  sim.initBubbleTankInterfaceBand();

  RunResult result;
  result.kind = "mr";
  result.sample = sample;
  result.strength = strength;
  result.gas_start = meanY(sim.particles, 1);
  for (int i = 0; i < cfg.steps; ++i) sim.step();
  result.gas_end = meanY(sim.particles, 1);
  result.finite = finiteParticles(sim.particles);
  result.interface_stats = sim.interface_diagnostics_last;
  result.surface_stats = sim.surface_tension_stats_last;
  result.ok = result.finite &&
              result.gas_end > result.gas_start &&
              surfaceStatsOk(cfg, result.interface_stats, result.surface_stats);
  return result;
}

void printResult(const RunResult& r) {
  std::printf("surface_tension_sweep sample=%d kind=%s strength=%.9g "
              "gas_mean_y_start=%.9g gas_mean_y_end=%.9g rise_delta=%.9g "
              "interface_cells=%d applied_cells=%d finite=%s "
              "raw_curvature_abs_max=%.9g smoothed_curvature_abs_max=%.9g "
              "max_delta_speed=%.9g capillary_dt_limit=%.9g capillary_stable=%s "
              "status=%s\n",
              r.sample,
              r.kind,
              r.strength,
              r.gas_start,
              r.gas_end,
              r.gas_end - r.gas_start,
              r.interface_stats.interface_cells,
              r.surface_stats.applied_cells,
              r.finite ? "true" : "false",
              r.surface_stats.raw_curvature_abs_max,
              r.surface_stats.smoothed_curvature_abs_max,
              r.surface_stats.max_delta_speed,
              r.surface_stats.capillary_dt_limit,
              r.surface_stats.capillary_stable ? "true" : "false",
              r.ok ? "ok" : "fail");
}

void usage() {
  std::fprintf(stderr,
               "usage: validate_surface_tension3d [--mode sparse|mr|both] "
               "[--nx N] [--ny N] [--nz N] [--steps N] [--dt DT] "
               "[--cg-iters N] [--strength-min S] [--strength-max S] "
               "[--strength-samples N] [--max-delta-speed V] "
               "[--smoothing-radius N]\n");
}

} // namespace

int main(int argc, char** argv) {
  Config cfg;
  cfg.mode = argString(argc, argv, "--mode", cfg.mode);
  cfg.nx = argInt(argc, argv, "--nx", cfg.nx);
  cfg.ny = argInt(argc, argv, "--ny", cfg.ny);
  cfg.nz = argInt(argc, argv, "--nz", cfg.nz);
  cfg.steps = argInt(argc, argv, "--steps", cfg.steps);
  cfg.dt = argDouble(argc, argv, "--dt", cfg.dt);
  cfg.cg_iters = argInt(argc, argv, "--cg-iters", cfg.cg_iters);
  cfg.strength_min = argDouble(argc, argv, "--strength-min", cfg.strength_min);
  cfg.strength_max = argDouble(argc, argv, "--strength-max", cfg.strength_max);
  cfg.strength_samples = argInt(argc, argv, "--strength-samples", cfg.strength_samples);
  cfg.max_delta_speed = argDouble(argc, argv, "--max-delta-speed", cfg.max_delta_speed);
  cfg.smoothing_radius = argInt(argc, argv, "--smoothing-radius", cfg.smoothing_radius);

  const bool runSparseMode =
    std::strcmp(cfg.mode, "sparse") == 0 || std::strcmp(cfg.mode, "both") == 0;
  const bool runMRMode =
    std::strcmp(cfg.mode, "mr") == 0 || std::strcmp(cfg.mode, "both") == 0;
  if (!runSparseMode && !runMRMode) {
    usage();
    return 2;
  }
  if (cfg.nx < 4 || cfg.ny < 4 || cfg.nz < 4 ||
      cfg.steps <= 0 ||
      cfg.dt <= 0.0 ||
      cfg.cg_iters < 0 ||
      cfg.strength_min < 0.0 ||
      cfg.strength_max < cfg.strength_min ||
      cfg.strength_samples <= 0 ||
      cfg.max_delta_speed < 0.0 ||
      cfg.smoothing_radius < 0 ||
      cfg.smoothing_radius > 3) {
    usage();
    return 2;
  }

  std::printf("mode=%s\n", cfg.mode);
  std::printf("dims=%d,%d,%d\n", cfg.nx, cfg.ny, cfg.nz);
  std::printf("steps=%d\n", cfg.steps);
  std::printf("dt=%.9g\n", cfg.dt);
  std::printf("cg_iters=%d\n", cfg.cg_iters);
  std::printf("strength_min=%.9g\n", cfg.strength_min);
  std::printf("strength_max=%.9g\n", cfg.strength_max);
  std::printf("strength_samples=%d\n", cfg.strength_samples);
  std::printf("max_delta_speed=%.9g\n", cfg.max_delta_speed);
  std::printf("smoothing_radius=%d\n", cfg.smoothing_radius);

  bool ok = true;
  for (int i = 0; i < cfg.strength_samples; ++i) {
    const double t = cfg.strength_samples == 1
      ? 0.0
      : static_cast<double>(i) / static_cast<double>(cfg.strength_samples - 1);
    const double strength =
      cfg.strength_min + t * (cfg.strength_max - cfg.strength_min);
    if (runSparseMode) {
      const RunResult r = runSparse(cfg, i, strength);
      printResult(r);
      if (!r.ok) ok = false;
    }
    if (runMRMode) {
      const RunResult r = runMR(cfg, i, strength);
      printResult(r);
      if (!r.ok) ok = false;
    }
  }

  std::printf("status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
