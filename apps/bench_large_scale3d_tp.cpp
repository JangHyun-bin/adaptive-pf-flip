#include "driver/multires_sim3d_tp.h"
#include "driver/render_cache3d.h"
#include "driver/sparse_sim3d_tp.h"
#include "physics_preset3d.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
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

double volumeType(const Particles3DTP& ps, unsigned char type, double Vp) {
  double volume = 0.0;
  for (size_t i = 0; i < ps.size(); ++i) {
    if (ps.type[i] == type) volume += ps.volume[i] * Vp;
  }
  return volume;
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
    const Vec3& p = ps.pos[i];
    if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z)) {
      return false;
    }
  }
  return true;
}

struct Config {
  int nx = 16;
  int ny = 24;
  int nz = 16;
  int steps = 8;
  int cg_iters = 160;
  double dt = 0.02;
  std::string csv = "build/large_scale3d_tp.csv";
  std::string solver = "baseline";
  bool physics_preset = false;
  int mr_particle_padding = -1;
  int mr_gas_padding = -1;
  int mr_hysteresis = -1;
  int mr_max_fine_leaves = -1;
  std::string render_cache_prefix;
  int render_cache_every = 0;
  int render_cache_preview_scale = 4;
  std::string python = "python";
  bool skip_render_cache_tools = false;
};

struct Row {
  std::string variant;
  std::string solver;
  int nx = 0;
  int ny = 0;
  int nz = 0;
  int steps = 0;
  bool adaptivity = false;
  int mr_particle_padding = -1;
  int mr_gas_padding = -1;
  int mr_hysteresis = -1;
  int mr_max_fine_leaves = -1;
  size_t particles_start = 0;
  size_t particles_end = 0;
  size_t liquid_particles_start = 0;
  size_t liquid_particles_end = 0;
  size_t gas_particles_start = 0;
  size_t gas_particles_end = 0;
  double liquid_volume_start = 0.0;
  double liquid_volume_end = 0.0;
  double gas_volume_start = 0.0;
  double gas_volume_end = 0.0;
  double gas_mean_y_start = 0.0;
  double gas_mean_y_end = 0.0;
  size_t active_pressure_cells = 0;
  size_t total_pressure_cells = 0;
  size_t active_pressure_blocks_max = 0;
  size_t total_pressure_blocks = 0;
  size_t leaf_level0 = 0;
  size_t leaf_level1 = 0;
  int u_faces = 0;
  int v_faces = 0;
  int w_faces = 0;
  size_t memory_proxy_cells = 0;
  size_t memory_proxy_faces = 0;
  size_t memory_proxy_bytes = 0;
  bool render_cache_enabled = false;
  std::string render_cache_manifest;
  int render_cache_frames = 0;
  size_t render_cache_bytes = 0;
  long long render_cache_export_ms = -1;
  long long render_cache_validate_ms = -1;
  long long render_cache_preview_ms = -1;
  std::string render_cache_tools_status = "disabled";
  size_t total_memory_proxy_bytes = 0;
  long long elapsed_ms = 0;
  double elapsed_ms_per_step = 0.0;
  int pressure_iterations = -1;
  int pressure_max_iterations = -1;
  double pressure_initial_residual = 0.0;
  double pressure_final_residual = 0.0;
  double pressure_final_over_initial = 0.0;
  std::string pressure_converged = "na";
  std::string pressure_breakdown = "na";
  bool ok = false;
};

void usage() {
  std::fprintf(stderr,
               "usage: bench_large_scale3d_tp [--nx N] [--ny N] [--nz N] "
               "[--steps N] [--dt DT] [--cg-iters N] [--csv PATH] "
               "[--solver baseline|relax|coarse_pre|all] [--physics-preset] "
               "[--mr-particle-padding N] [--mr-gas-padding N] "
               "[--mr-hysteresis N] [--mr-max-fine-leaves N] "
               "[--render-cache-prefix PATH] [--render-cache-every N] "
               "[--render-cache-preview-scale N] [--python EXE] "
               "[--skip-render-cache-tools]\n");
}

void writeHeader(std::ostream& out) {
  out << "variant,solver,nx,ny,nz,steps,adaptivity,mr_particle_padding,"
      << "mr_gas_padding,mr_hysteresis,mr_max_fine_leaves,particles_start,particles_end,"
      << "liquid_particles_start,liquid_particles_end,gas_particles_start,gas_particles_end,"
      << "liquid_volume_start,liquid_volume_end,gas_volume_start,gas_volume_end,"
      << "gas_mean_y_start,gas_mean_y_end,active_pressure_cells,total_pressure_cells,"
      << "active_pressure_blocks_max,total_pressure_blocks,leaf_level0,leaf_level1,"
      << "u_faces,v_faces,w_faces,memory_proxy_cells,memory_proxy_faces,"
      << "memory_proxy_bytes,render_cache_enabled,render_cache_manifest,"
      << "render_cache_frames,render_cache_bytes,render_cache_export_ms,"
      << "render_cache_validate_ms,render_cache_preview_ms,render_cache_tools_status,"
      << "total_memory_proxy_bytes,elapsed_ms,elapsed_ms_per_step,pressure_iterations,"
      << "pressure_max_iterations,pressure_initial_residual,pressure_final_residual,"
      << "pressure_final_over_initial,pressure_converged,pressure_breakdown,status\n";
}

void writeRow(std::ostream& out, const Row& r) {
  out << r.variant << ","
      << r.solver << ","
      << r.nx << ","
      << r.ny << ","
      << r.nz << ","
      << r.steps << ","
      << (r.adaptivity ? "true" : "false") << ","
      << r.mr_particle_padding << ","
      << r.mr_gas_padding << ","
      << r.mr_hysteresis << ","
      << r.mr_max_fine_leaves << ","
      << r.particles_start << ","
      << r.particles_end << ","
      << r.liquid_particles_start << ","
      << r.liquid_particles_end << ","
      << r.gas_particles_start << ","
      << r.gas_particles_end << ","
      << r.liquid_volume_start << ","
      << r.liquid_volume_end << ","
      << r.gas_volume_start << ","
      << r.gas_volume_end << ","
      << r.gas_mean_y_start << ","
      << r.gas_mean_y_end << ","
      << r.active_pressure_cells << ","
      << r.total_pressure_cells << ","
      << r.active_pressure_blocks_max << ","
      << r.total_pressure_blocks << ","
      << r.leaf_level0 << ","
      << r.leaf_level1 << ","
      << r.u_faces << ","
      << r.v_faces << ","
      << r.w_faces << ","
      << r.memory_proxy_cells << ","
      << r.memory_proxy_faces << ","
      << r.memory_proxy_bytes << ","
      << (r.render_cache_enabled ? "true" : "false") << ","
      << r.render_cache_manifest << ","
      << r.render_cache_frames << ","
      << r.render_cache_bytes << ","
      << r.render_cache_export_ms << ","
      << r.render_cache_validate_ms << ","
      << r.render_cache_preview_ms << ","
      << r.render_cache_tools_status << ","
      << r.total_memory_proxy_bytes << ","
      << r.elapsed_ms << ","
      << r.elapsed_ms_per_step << ","
      << r.pressure_iterations << ","
      << r.pressure_max_iterations << ","
      << r.pressure_initial_residual << ","
      << r.pressure_final_residual << ","
      << r.pressure_final_over_initial << ","
      << r.pressure_converged << ","
      << r.pressure_breakdown << ","
      << (r.ok ? "ok" : "fail") << "\n";
}

const Row* findRow(const std::vector<Row>& rows,
                   const std::string& variant,
                   const std::string& solver) {
  for (const Row& row : rows) {
    if (row.variant == variant && row.solver == solver) return &row;
  }
  return nullptr;
}

double ratio(double numerator, double denominator) {
  return denominator > 0.0 ? numerator / denominator : 0.0;
}

void printPairSummary(const char* label, const Row* base, const Row* adaptive) {
  if (!base || !adaptive) return;
  const double speedup = ratio(static_cast<double>(base->elapsed_ms),
                               static_cast<double>(adaptive->elapsed_ms));
  const double memoryRatio = ratio(static_cast<double>(adaptive->memory_proxy_bytes),
                                   static_cast<double>(base->memory_proxy_bytes));
  std::printf("summary pair=%s base_elapsed_ms=%lld adaptive_elapsed_ms=%lld "
              "adaptive_speedup=%.6g base_memory_proxy_bytes=%zu "
              "adaptive_memory_proxy_bytes=%zu adaptive_memory_ratio=%.6g\n",
              label,
              base->elapsed_ms,
              adaptive->elapsed_ms,
              speedup,
              base->memory_proxy_bytes,
              adaptive->memory_proxy_bytes,
              memoryRatio);
}

void printBenchmarkSummary(const std::vector<Row>& rows) {
  const Row* bestElapsed = nullptr;
  const Row* bestMemory = nullptr;
  for (const Row& row : rows) {
    if (!row.ok) continue;
    if (!bestElapsed || row.elapsed_ms < bestElapsed->elapsed_ms) {
      bestElapsed = &row;
    }
    if (!bestMemory || row.memory_proxy_bytes < bestMemory->memory_proxy_bytes) {
      bestMemory = &row;
    }
  }

  printPairSummary("sparse", findRow(rows, "sparse_base", "na"),
                   findRow(rows, "sparse_adaptive", "na"));
  for (const std::string& solver : {"baseline", "relax", "coarse_pre"}) {
    printPairSummary(("mr_" + solver).c_str(),
                     findRow(rows, "mr_base", solver),
                     findRow(rows, "mr_adaptive", solver));
  }

  if (bestElapsed) {
    std::printf("summary_best_elapsed variant=%s solver=%s elapsed_ms=%lld "
                "memory_proxy_bytes=%zu\n",
                bestElapsed->variant.c_str(),
                bestElapsed->solver.c_str(),
                bestElapsed->elapsed_ms,
                bestElapsed->memory_proxy_bytes);
  }
  if (bestMemory) {
    std::printf("summary_best_memory variant=%s solver=%s elapsed_ms=%lld "
                "memory_proxy_bytes=%zu\n",
                bestMemory->variant.c_str(),
                bestMemory->solver.c_str(),
                bestMemory->elapsed_ms,
                bestMemory->memory_proxy_bytes);
  }
}

bool volumeStable(double start, double end) {
  const double tol = std::max(1e-9, std::abs(start) * 1e-9);
  return std::abs(start - end) <= tol;
}

void applySolverMode(MRSim3DTP& sim, const std::string& solver) {
  if (solver == "relax") {
    sim.cg_relaxation_sweeps = 2;
    sim.cg_relaxation_omega = 0.1;
    sim.cg_residual_history_stride = 1;
    sim.cg_residual_history_limit = 16;
  } else if (solver == "coarse_pre") {
    sim.cg_coarse_preconditioner = true;
    sim.cg_coarse_preconditioner_iters = 4;
    sim.cg_coarse_preconditioner_scale = 0.5;
    sim.cg_coarse_preconditioner_max_work_ratio = 2.0;
    sim.cg_coarse_preconditioner_auto_disable = true;
    sim.cg_coarse_preconditioner_auto_disable_after = 1;
  }
}

std::vector<std::string> solverModes(const std::string& requested) {
  if (requested == "all") return {"baseline", "relax", "coarse_pre"};
  return {requested};
}

bool renderCacheEnabled(const Config& cfg) {
  return !cfg.render_cache_prefix.empty();
}

std::string zeroPaddedFrame(int frame) {
  char suffix[32];
  std::snprintf(suffix, sizeof(suffix), "%03d", frame);
  return suffix;
}

std::string rowCacheBase(const Config& cfg, const Row& row) {
  return cfg.render_cache_prefix + "_" + row.variant + "_" + row.solver;
}

bool isPathSep(char c) {
  return c == '/' || c == '\\';
}

std::string dirName(const std::string& path) {
  const size_t pos = path.find_last_of("/\\");
  return pos == std::string::npos ? std::string() : path.substr(0, pos);
}

void ensureParentDir(const std::string& path) {
  const std::filesystem::path parent = std::filesystem::path(path).parent_path();
  if (!parent.empty()) std::filesystem::create_directories(parent);
}

std::string manifestFramePath(const std::string& framePath,
                              const std::string& manifestPath) {
  std::string dir = dirName(manifestPath);
  if (dir.empty()) return framePath;
  if (framePath.size() > dir.size() &&
      framePath.compare(0, dir.size(), dir) == 0 &&
      isPathSep(framePath[dir.size()])) {
    return framePath.substr(dir.size() + 1);
  }
  return framePath;
}

long long fileSizeBytes(const std::string& path) {
  std::ifstream in(path, std::ios::binary | std::ios::ate);
  if (!in) return 0;
  return static_cast<long long>(in.tellg());
}

std::string quoteCommandArg(const std::string& arg) {
  std::string quoted = "\"";
  for (char c : arg) {
    if (c == '"') quoted += "\\\"";
    else quoted += c;
  }
  quoted += "\"";
  return quoted;
}

std::string quoteExecutableArg(const std::string& arg) {
  if (arg.find_first_of(" \t\"") == std::string::npos) return arg;
  return quoteCommandArg(arg);
}

int timedSystem(const std::string& command, long long& elapsedMs) {
  auto start = std::chrono::steady_clock::now();
  const int rc = std::system(command.c_str());
  auto end = std::chrono::steady_clock::now();
  elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
  return rc;
}

struct RenderCacheBenchState {
  bool enabled = false;
  std::string base;
  std::string manifest;
  std::string preview_dir;
  std::vector<RenderCacheManifestFrame3D> frames;
  long long export_ms = 0;
  size_t bytes = 0;
  bool ok = true;
};

RenderCacheBenchState beginRenderCacheBench(const Config& cfg, const Row& row) {
  RenderCacheBenchState state;
  state.enabled = renderCacheEnabled(cfg);
  if (!state.enabled) return state;
  state.base = rowCacheBase(cfg, row);
  state.manifest = state.base + "_manifest.json";
  state.preview_dir = state.base + "_preview";
  ensureParentDir(state.base + "_000.jsonl");
  ensureParentDir(state.manifest);
  std::filesystem::create_directories(state.preview_dir);
  return state;
}

bool shouldWriteRenderCacheFrame(const Config& cfg, int step) {
  if (!renderCacheEnabled(cfg)) return false;
  return step == cfg.steps || (cfg.render_cache_every > 0 && step % cfg.render_cache_every == 0);
}

template <typename WriteFrame>
void writeRenderCacheFrame(RenderCacheBenchState& state,
                           int step,
                           double time,
                           WriteFrame writeFrame) {
  if (!state.enabled || !state.ok) return;
  const int frame = static_cast<int>(state.frames.size());
  const std::string path = state.base + "_" + zeroPaddedFrame(frame) + ".jsonl";
  try {
    auto start = std::chrono::steady_clock::now();
    writeFrame(path, frame, time);
    auto end = std::chrono::steady_clock::now();
    state.export_ms += std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    const long long bytes = fileSizeBytes(path);
    state.bytes += static_cast<size_t>(std::max<long long>(0, bytes));
    state.frames.push_back(RenderCacheManifestFrame3D{
      frame, step, time, manifestFramePath(path, state.manifest), bytes
    });
  } catch (...) {
    state.ok = false;
  }
}

void finishRenderCacheBench(RenderCacheBenchState& state,
                            const Config& cfg,
                            const char* simKind,
                            int nx,
                            int ny,
                            int nz,
                            double dx,
                            Row& row) {
  row.render_cache_enabled = state.enabled;
  if (!state.enabled) {
    row.render_cache_tools_status = "disabled";
    row.total_memory_proxy_bytes = row.memory_proxy_bytes;
    return;
  }

  row.render_cache_manifest = state.manifest;
  row.render_cache_frames = static_cast<int>(state.frames.size());
  row.render_cache_export_ms = state.export_ms;
  row.render_cache_tools_status = cfg.skip_render_cache_tools ? "skipped" : "ok";

  if (!state.ok || state.frames.empty()) {
    row.render_cache_tools_status = "fail";
    row.render_cache_bytes = state.bytes;
    row.total_memory_proxy_bytes = row.memory_proxy_bytes + row.render_cache_bytes;
    row.ok = false;
    return;
  }

  try {
    auto start = std::chrono::steady_clock::now();
    writeRenderCacheManifest3D(state.manifest, simKind, nx, ny, nz, dx, state.frames);
    auto end = std::chrono::steady_clock::now();
    row.render_cache_export_ms +=
      std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    const long long manifestBytes = fileSizeBytes(state.manifest);
    state.bytes += static_cast<size_t>(std::max<long long>(0, manifestBytes));
  } catch (...) {
    row.render_cache_tools_status = "fail";
    row.render_cache_bytes = state.bytes;
    row.total_memory_proxy_bytes = row.memory_proxy_bytes + row.render_cache_bytes;
    row.ok = false;
    return;
  }

  row.render_cache_bytes = state.bytes;
  row.total_memory_proxy_bytes = row.memory_proxy_bytes + row.render_cache_bytes;
  if (cfg.skip_render_cache_tools) return;

  const std::string validateCommand =
    quoteExecutableArg(cfg.python) + " tools\\validate_render_cache.py " +
    quoteCommandArg(state.manifest) + " --allow-empty-secondary";
  const int validateRc = timedSystem(validateCommand, row.render_cache_validate_ms);

  const std::string previewCommand =
    quoteExecutableArg(cfg.python) + " tools\\render_cache_preview.py " +
    quoteCommandArg(state.manifest) + " " +
    quoteCommandArg(state.preview_dir) + " " +
    std::to_string(cfg.render_cache_preview_scale);
  const int previewRc = timedSystem(previewCommand, row.render_cache_preview_ms);

  if (validateRc != 0 || previewRc != 0) {
    row.render_cache_tools_status = "fail";
    row.ok = false;
  }
}

Row runSparse(const Config& cfg, bool adaptivity) {
  SparseSim3DTP sim(cfg.nx, cfg.ny, cfg.nz, 1.0);
  if (cfg.physics_preset) applyCorePhysicsPreset3D(sim);
  if (adaptivity) applyParticleAdaptivityPreset3D(sim);
  sim.dt = cfg.dt;
  sim.cg_iters = cfg.cg_iters;
  sim.initBubbleTank();

  Row r;
  r.variant = adaptivity ? "sparse_adaptive" : "sparse_base";
  r.solver = "na";
  r.nx = cfg.nx;
  r.ny = cfg.ny;
  r.nz = cfg.nz;
  r.steps = cfg.steps;
  r.adaptivity = adaptivity;
  r.particles_start = sim.particles.size();
  r.liquid_particles_start = countType(sim.particles, 0);
  r.gas_particles_start = countType(sim.particles, 1);
  r.liquid_volume_start = volumeType(sim.particles, 0, sim.Vp);
  r.gas_volume_start = volumeType(sim.particles, 1, sim.Vp);
  r.gas_mean_y_start = meanY(sim.particles, 1);

  RenderCacheBenchState cacheState = beginRenderCacheBench(cfg, r);
  const RenderCacheCamera3D camera =
    defaultRenderCacheCamera3D(sim.grid.nx, sim.grid.ny, sim.grid.nz, sim.grid.dx);
  double simTime = 0.0;
  for (int s = 0; s < cfg.steps; ++s) {
    auto stepStart = std::chrono::steady_clock::now();
    sim.step();
    auto stepEnd = std::chrono::steady_clock::now();
    r.elapsed_ms +=
      std::chrono::duration_cast<std::chrono::milliseconds>(stepEnd - stepStart).count();
    simTime += sim.effective_dt_last;
    r.active_pressure_blocks_max =
      std::max(r.active_pressure_blocks_max, sim.grid.activeCellBlocks());
    const int step = s + 1;
    if (shouldWriteRenderCacheFrame(cfg, step)) {
      writeRenderCacheFrame(cacheState, step, simTime,
                            [&](const std::string& path, int frame, double time) {
                              writeSparseRenderCache3D(sim, path, frame, time, camera);
                            });
    }
  }

  r.elapsed_ms_per_step = cfg.steps > 0 ? static_cast<double>(r.elapsed_ms) / cfg.steps : 0.0;
  r.particles_end = sim.particles.size();
  r.liquid_particles_end = countType(sim.particles, 0);
  r.gas_particles_end = countType(sim.particles, 1);
  r.liquid_volume_end = volumeType(sim.particles, 0, sim.Vp);
  r.gas_volume_end = volumeType(sim.particles, 1, sim.Vp);
  r.gas_mean_y_end = meanY(sim.particles, 1);
  r.total_pressure_blocks = sim.grid.totalCellBlocks();
  r.active_pressure_cells = r.active_pressure_blocks_max * 64;
  r.total_pressure_cells = static_cast<size_t>(cfg.nx) * cfg.ny * cfg.nz;
  r.memory_proxy_cells = r.active_pressure_cells;
  r.memory_proxy_faces = 0;
  r.memory_proxy_bytes = r.particles_end * 64 + r.memory_proxy_cells * 8 * sizeof(float);
  r.total_memory_proxy_bytes = r.memory_proxy_bytes;

  const bool finite = finiteParticles(sim.particles);
  const bool gasVolumeOk = adaptivity
    ? r.gas_volume_end <= r.gas_volume_start + std::max(1e-9, r.gas_volume_start * 1e-9)
    : volumeStable(r.gas_volume_start, r.gas_volume_end);
  r.ok = finite &&
         volumeStable(r.liquid_volume_start, r.liquid_volume_end) &&
         gasVolumeOk &&
         r.gas_mean_y_end > r.gas_mean_y_start &&
         r.active_pressure_blocks_max < r.total_pressure_blocks;
  finishRenderCacheBench(cacheState, cfg, "sparse3d_tp",
                         sim.grid.nx, sim.grid.ny, sim.grid.nz, sim.grid.dx, r);
  return r;
}

Row runMR(const Config& cfg, bool adaptivity, const std::string& solver) {
  MRSim3DTP sim(cfg.nx, cfg.ny, cfg.nz, 1.0);
  if (cfg.physics_preset) applyCorePhysicsPreset3D(sim);
  if (adaptivity) applyParticleAdaptivityPreset3D(sim);
  if (cfg.mr_particle_padding >= 0) sim.dynamic_particle_padding = cfg.mr_particle_padding;
  if (cfg.mr_gas_padding >= 0) sim.dynamic_gas_padding = cfg.mr_gas_padding;
  if (cfg.mr_hysteresis >= 0) sim.dynamic_hysteresis_cells = cfg.mr_hysteresis;
  if (cfg.mr_max_fine_leaves >= 0) sim.dynamic_max_fine_leaves = cfg.mr_max_fine_leaves;
  sim.dt = cfg.dt;
  sim.cg_iters = cfg.cg_iters;
  applySolverMode(sim, solver);
  sim.initBubbleTankInterfaceBand();

  Row r;
  r.variant = adaptivity ? "mr_adaptive" : "mr_base";
  r.solver = solver;
  r.nx = cfg.nx;
  r.ny = cfg.ny;
  r.nz = cfg.nz;
  r.steps = cfg.steps;
  r.adaptivity = adaptivity;
  r.mr_particle_padding = sim.dynamic_particle_padding;
  r.mr_gas_padding = sim.dynamic_gas_padding;
  r.mr_hysteresis = sim.dynamic_hysteresis_cells;
  r.mr_max_fine_leaves = sim.dynamic_max_fine_leaves;
  r.particles_start = sim.particles.size();
  r.liquid_particles_start = countType(sim.particles, 0);
  r.gas_particles_start = countType(sim.particles, 1);
  r.liquid_volume_start = volumeType(sim.particles, 0, sim.Vp);
  r.gas_volume_start = volumeType(sim.particles, 1, sim.Vp);
  r.gas_mean_y_start = meanY(sim.particles, 1);

  RenderCacheBenchState cacheState = beginRenderCacheBench(cfg, r);
  const RenderCacheCamera3D camera =
    defaultRenderCacheCamera3D(sim.layout.nx, sim.layout.ny, sim.layout.nz, sim.layout.dx);
  double simTime = 0.0;
  for (int s = 0; s < cfg.steps; ++s) {
    auto stepStart = std::chrono::steady_clock::now();
    sim.step();
    auto stepEnd = std::chrono::steady_clock::now();
    r.elapsed_ms +=
      std::chrono::duration_cast<std::chrono::milliseconds>(stepEnd - stepStart).count();
    simTime += sim.effective_dt_last;
    const int step = s + 1;
    if (shouldWriteRenderCacheFrame(cfg, step)) {
      writeRenderCacheFrame(cacheState, step, simTime,
                            [&](const std::string& path, int frame, double time) {
                              writeMRRenderCache3D(sim, path, frame, time, camera);
                            });
    }
  }

  r.elapsed_ms_per_step = cfg.steps > 0 ? static_cast<double>(r.elapsed_ms) / cfg.steps : 0.0;
  r.particles_end = sim.particles.size();
  r.liquid_particles_end = countType(sim.particles, 0);
  r.gas_particles_end = countType(sim.particles, 1);
  r.liquid_volume_end = volumeType(sim.particles, 0, sim.Vp);
  r.gas_volume_end = volumeType(sim.particles, 1, sim.Vp);
  r.gas_mean_y_end = meanY(sim.particles, 1);
  r.active_pressure_cells = static_cast<size_t>(sim.activePressureCellCount());
  r.total_pressure_cells = static_cast<size_t>(cfg.nx) * cfg.ny * cfg.nz;
  r.leaf_level0 = sim.layout.countLevel(0);
  r.leaf_level1 = sim.layout.countLevel(1);
  r.u_faces = sim.uFaceCount();
  r.v_faces = sim.vFaceCount();
  r.w_faces = sim.wFaceCount();
  r.memory_proxy_cells = r.active_pressure_cells;
  r.memory_proxy_faces = static_cast<size_t>(r.u_faces + r.v_faces + r.w_faces);
  r.memory_proxy_bytes =
    r.particles_end * 64 + (r.memory_proxy_cells + r.memory_proxy_faces) * 8 * sizeof(float);
  r.total_memory_proxy_bytes = r.memory_proxy_bytes;

  const MRPressureSolveStats3D& st = sim.last_pressure_stats;
  r.pressure_iterations = st.iterations;
  r.pressure_max_iterations = st.max_iterations;
  r.pressure_initial_residual = st.initial_residual;
  r.pressure_final_residual = st.final_residual;
  r.pressure_final_over_initial =
    st.initial_residual > 0.0 ? st.final_residual / st.initial_residual : 0.0;
  r.pressure_converged = st.converged ? "true" : "false";
  r.pressure_breakdown = st.breakdown ? "true" : "false";

  const bool finite = finiteParticles(sim.particles);
  const bool pressureFinite = std::isfinite(st.initial_residual) &&
                              std::isfinite(st.final_residual);
  const bool gasVolumeOk = adaptivity
    ? r.gas_volume_end <= r.gas_volume_start + std::max(1e-9, r.gas_volume_start * 1e-9)
    : volumeStable(r.gas_volume_start, r.gas_volume_end);
  r.ok = finite &&
         volumeStable(r.liquid_volume_start, r.liquid_volume_end) &&
         gasVolumeOk &&
         r.gas_mean_y_end > r.gas_mean_y_start &&
         r.active_pressure_cells < r.total_pressure_cells &&
         pressureFinite &&
         !st.breakdown &&
         st.final_residual <= st.initial_residual;
  finishRenderCacheBench(cacheState, cfg, "multires3d_tp",
                         sim.layout.nx, sim.layout.ny, sim.layout.nz, sim.layout.dx, r);
  return r;
}

} // namespace

int main(int argc, char** argv) {
  Config cfg;
  cfg.nx = argInt(argc, argv, "--nx", cfg.nx);
  cfg.ny = argInt(argc, argv, "--ny", cfg.ny);
  cfg.nz = argInt(argc, argv, "--nz", cfg.nz);
  cfg.steps = argInt(argc, argv, "--steps", cfg.steps);
  cfg.dt = argDouble(argc, argv, "--dt", cfg.dt);
  cfg.cg_iters = argInt(argc, argv, "--cg-iters", cfg.cg_iters);
  cfg.csv = argString(argc, argv, "--csv", cfg.csv.c_str());
  cfg.solver = argString(argc, argv, "--solver", cfg.solver.c_str());
  cfg.physics_preset = hasFlag(argc, argv, "--physics-preset");
  cfg.mr_particle_padding = argInt(argc, argv, "--mr-particle-padding",
                                   cfg.mr_particle_padding);
  cfg.mr_gas_padding = argInt(argc, argv, "--mr-gas-padding",
                              cfg.mr_gas_padding);
  cfg.mr_hysteresis = argInt(argc, argv, "--mr-hysteresis", cfg.mr_hysteresis);
  cfg.mr_max_fine_leaves = argInt(argc, argv, "--mr-max-fine-leaves",
                                  cfg.mr_max_fine_leaves);
  cfg.render_cache_prefix =
    argString(argc, argv, "--render-cache-prefix", cfg.render_cache_prefix.c_str());
  cfg.render_cache_every =
    argInt(argc, argv, "--render-cache-every", cfg.render_cache_every);
  cfg.render_cache_preview_scale =
    argInt(argc, argv, "--render-cache-preview-scale", cfg.render_cache_preview_scale);
  cfg.python = argString(argc, argv, "--python", cfg.python.c_str());
  cfg.skip_render_cache_tools = hasFlag(argc, argv, "--skip-render-cache-tools");
  if (renderCacheEnabled(cfg) && cfg.render_cache_every == 0) {
    cfg.render_cache_every = cfg.steps;
  }

  if (cfg.nx < 4 || cfg.ny < 4 || cfg.nz < 4 ||
      cfg.steps <= 0 || cfg.dt <= 0.0 || cfg.cg_iters < 0 ||
      cfg.mr_particle_padding < -1 ||
      cfg.mr_gas_padding < -1 ||
      cfg.mr_hysteresis < -1 ||
      cfg.mr_max_fine_leaves < -1 ||
      cfg.render_cache_every < 0 ||
      (renderCacheEnabled(cfg) && cfg.render_cache_every <= 0) ||
      cfg.render_cache_preview_scale <= 0 ||
      cfg.python.empty() ||
      cfg.csv.empty() ||
      (cfg.solver != "baseline" && cfg.solver != "relax" &&
       cfg.solver != "coarse_pre" && cfg.solver != "all")) {
    usage();
    return 2;
  }

  std::vector<Row> rows;
  rows.push_back(runSparse(cfg, false));
  rows.push_back(runSparse(cfg, true));
  for (const std::string& solver : solverModes(cfg.solver)) {
    rows.push_back(runMR(cfg, false, solver));
    rows.push_back(runMR(cfg, true, solver));
  }

  std::ofstream csv(cfg.csv);
  if (!csv) {
    std::fprintf(stderr, "failed to open csv: %s\n", cfg.csv.c_str());
    return 2;
  }
  writeHeader(csv);
  for (const Row& row : rows) writeRow(csv, row);
  if (!csv) {
    std::fprintf(stderr, "failed to write csv: %s\n", cfg.csv.c_str());
    return 2;
  }

  bool ok = true;
  for (const Row& row : rows) {
    std::printf("row variant=%s solver=%s status=%s elapsed_ms=%lld "
                "memory_proxy_bytes=%zu render_cache_bytes=%zu "
                "render_cache_tools_status=%s\n",
                row.variant.c_str(), row.solver.c_str(), row.ok ? "ok" : "fail",
                row.elapsed_ms, row.memory_proxy_bytes, row.render_cache_bytes,
                row.render_cache_tools_status.c_str());
    if (!row.ok) ok = false;
  }
  printBenchmarkSummary(rows);
  std::printf("csv=%s\n", cfg.csv.c_str());
  std::printf("rows=%zu\n", rows.size());
  std::printf("status=%s\n", ok ? "ok" : "fail");
  return ok ? 0 : 1;
}
