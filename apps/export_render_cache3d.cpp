#include "driver/multires_sim3d_tp.h"
#include "driver/render_cache3d.h"
#include "driver/sparse_sim3d_tp.h"
#include "physics_preset3d.h"

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
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

void usage() {
  std::fprintf(stderr,
               "usage: export_render_cache3d [--kind sparse|mr] [--nx N] [--ny N] [--nz N] "
               "[--steps N] [--every N] [--dt DT] [--cg-iters N] "
               "[--out-prefix NAME] [--manifest PATH] [--physics-preset]\n");
}

std::string framePath(const std::string& prefix, int frame) {
  char suffix[64];
  std::snprintf(suffix, sizeof(suffix), "_%03d.jsonl", frame);
  return prefix + suffix;
}

bool isPathSep(char c) {
  return c == '/' || c == '\\';
}

std::string dirName(const std::string& path) {
  const size_t pos = path.find_last_of("/\\");
  return pos == std::string::npos ? std::string() : path.substr(0, pos);
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

} // namespace

int main(int argc, char** argv) {
  const char* kind = argString(argc, argv, "--kind", "sparse");
  const bool sparseKind = std::strcmp(kind, "sparse") == 0;
  const bool mrKind = std::strcmp(kind, "mr") == 0;
  int nx = argInt(argc, argv, "--nx", 12);
  int ny = argInt(argc, argv, "--ny", 18);
  int nz = argInt(argc, argv, "--nz", 12);
  int steps = argInt(argc, argv, "--steps", 4);
  int every = std::max(1, argInt(argc, argv, "--every", steps));
  double dt = argDouble(argc, argv, "--dt", 0.02);
  int cgIters = argInt(argc, argv, "--cg-iters", sparseKind ? 600 : 160);
  const char* prefix = argString(argc, argv, "--out-prefix", "render_cache3d");
  const std::string defaultManifestPath = std::string(prefix) + "_manifest.json";
  const char* manifestArg = argString(argc, argv, "--manifest", nullptr);
  const std::string manifestPath = manifestArg ? manifestArg : defaultManifestPath;
  const bool physicsPreset = hasFlag(argc, argv, "--physics-preset");

  if ((!sparseKind && !mrKind) ||
      nx < 4 || ny < 4 || nz < 4 ||
      steps <= 0 || every <= 0 ||
      dt <= 0.0 || cgIters < 0 ||
      std::strlen(prefix) == 0 ||
      manifestPath.empty()) {
    usage();
    return 2;
  }

  int frameCount = 0;
  std::vector<RenderCacheManifestFrame3D> manifestFrames;
  if (sparseKind) {
    SparseSim3DTP sim(nx, ny, nz, 1.0);
    if (physicsPreset) applyFullPhysicsPreset3D(sim);
    sim.dt = dt;
    sim.cg_iters = cgIters;
    sim.initBubbleTank();
    const RenderCacheCamera3D camera =
      defaultRenderCacheCamera3D(sim.grid.nx, sim.grid.ny, sim.grid.nz, sim.grid.dx);
    double simTime = 0.0;
    for (int s = 0; s < steps; ++s) {
      sim.step();
      simTime += sim.effective_dt_last;
      if (s % every == 0 || s == steps - 1) {
        const int frameIndex = frameCount;
        const std::string path = framePath(prefix, frameIndex);
        writeSparseRenderCache3D(sim, path, frameIndex, simTime, camera);
        std::printf("wrote=%s\n", path.c_str());
        manifestFrames.push_back(RenderCacheManifestFrame3D{
          frameIndex, s + 1, simTime, manifestFramePath(path, manifestPath), fileSizeBytes(path)
        });
        ++frameCount;
      }
    }
    writeRenderCacheManifest3D(manifestPath, "sparse3d_tp",
                               sim.grid.nx, sim.grid.ny, sim.grid.nz,
                               sim.grid.dx, manifestFrames);
    std::printf("manifest=%s\n", manifestPath.c_str());
    std::printf("kind=sparse\n");
    std::printf("particles=%zu\n", sim.particles.size());
    std::printf("secondary_droplets=%zu\n", sim.escaped_droplets.size());
    std::printf("secondary_bubbles=%zu\n", sim.escaped_bubbles.size());
  } else {
    MRSim3DTP sim(nx, ny, nz, 1.0);
    if (physicsPreset) applyFullPhysicsPreset3D(sim);
    sim.dt = dt;
    sim.cg_iters = cgIters;
    sim.initBubbleTankInterfaceBand();
    const RenderCacheCamera3D camera =
      defaultRenderCacheCamera3D(sim.layout.nx, sim.layout.ny, sim.layout.nz, sim.layout.dx);
    double simTime = 0.0;
    for (int s = 0; s < steps; ++s) {
      sim.step();
      simTime += sim.effective_dt_last;
      if (s % every == 0 || s == steps - 1) {
        const int frameIndex = frameCount;
        const std::string path = framePath(prefix, frameIndex);
        writeMRRenderCache3D(sim, path, frameIndex, simTime, camera);
        std::printf("wrote=%s\n", path.c_str());
        manifestFrames.push_back(RenderCacheManifestFrame3D{
          frameIndex, s + 1, simTime, manifestFramePath(path, manifestPath), fileSizeBytes(path)
        });
        ++frameCount;
      }
    }
    writeRenderCacheManifest3D(manifestPath, "multires3d_tp",
                               sim.layout.nx, sim.layout.ny, sim.layout.nz,
                               sim.layout.dx, manifestFrames);
    std::printf("manifest=%s\n", manifestPath.c_str());
    std::printf("kind=mr\n");
    std::printf("particles=%zu\n", sim.particles.size());
    std::printf("secondary_droplets=%zu\n", sim.escaped_droplets.size());
    std::printf("secondary_bubbles=%zu\n", sim.escaped_bubbles.size());
  }

  std::printf("frames=%d\n", frameCount);
  std::printf("status=ok\n");
  return 0;
}
