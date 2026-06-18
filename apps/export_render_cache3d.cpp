#include "driver/multires_sim3d_tp.h"
#include "driver/render_cache3d.h"
#include "driver/sparse_sim3d_tp.h"
#include "physics_preset3d.h"

#include <algorithm>
#include <cmath>
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
               "usage: export_render_cache3d [--kind sparse|mr] [--scene bubble|dam-break|falling-water] "
               "[--nx N] [--ny N] [--nz N] "
               "[--steps N] [--every N] [--dt DT] [--cg-iters N] "
               "[--out-prefix NAME] [--manifest PATH] [--physics-preset] "
               "[--secondary-demo-particles N]\n");
}

bool sceneIsBubble(const char* scene) {
  return std::strcmp(scene, "bubble") == 0;
}

bool sceneIsDamBreak(const char* scene) {
  return std::strcmp(scene, "dam-break") == 0 ||
         std::strcmp(scene, "dambreak") == 0;
}

bool sceneIsFallingWater(const char* scene) {
  return std::strcmp(scene, "falling-water") == 0 ||
         std::strcmp(scene, "falling") == 0;
}

const char* canonicalScene(const char* scene) {
  if (sceneIsFallingWater(scene)) return "falling-water";
  return sceneIsDamBreak(scene) ? "dam-break" : "bubble";
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

struct ParticleBounds3D {
  Vec3 min{0.0, 0.0, 0.0};
  Vec3 max{0.0, 0.0, 0.0};
  bool valid = false;
};

void includeParticle(ParticleBounds3D& bounds, const Vec3& p) {
  if (!bounds.valid) {
    bounds.min = p;
    bounds.max = p;
    bounds.valid = true;
    return;
  }
  bounds.min.x = std::min(bounds.min.x, p.x);
  bounds.min.y = std::min(bounds.min.y, p.y);
  bounds.min.z = std::min(bounds.min.z, p.z);
  bounds.max.x = std::max(bounds.max.x, p.x);
  bounds.max.y = std::max(bounds.max.y, p.y);
  bounds.max.z = std::max(bounds.max.z, p.z);
}

ParticleBounds3D liquidParticleBounds(const Particles3DTP& particles) {
  ParticleBounds3D bounds;
  for (size_t i = 0; i < particles.size(); ++i) {
    if (particles.type[i] == 0) includeParticle(bounds, particles.pos[i]);
  }
  return bounds;
}

template <typename Sim>
void seedCinematicSecondaries(Sim& sim, int frameIndex, int requestedParticles) {
  if (requestedParticles <= 0) return;
  sim.escaped_droplets = Particles3DTP();
  sim.escaped_bubbles = Particles3DTP();
  sim.escaped_droplet_ages.clear();
  sim.escaped_bubble_ages.clear();

  const ParticleBounds3D bounds = liquidParticleBounds(sim.particles);
  if (!bounds.valid) return;

  constexpr double pi = 3.14159265358979323846;
  const int dropletCount = std::max(0, requestedParticles * 3 / 4);
  const int bubbleCount = std::max(0, requestedParticles - dropletCount);
  const double cx = 0.5 * (bounds.min.x + bounds.max.x);
  const double cz = 0.5 * (bounds.min.z + bounds.max.z);
  const double rx = std::max(0.6, 0.62 * (bounds.max.x - bounds.min.x + 1.0));
  const double rz = std::max(0.6, 0.62 * (bounds.max.z - bounds.min.z + 1.0));
  const double baseY = bounds.min.y + 0.18;
  const double phase = 0.37 * static_cast<double>(frameIndex);

  for (int n = 0; n < dropletCount; ++n) {
    const double a = 2.0 * pi * (static_cast<double>(n) / std::max(1, dropletCount)) + phase;
    const double ring = 0.55 + 0.45 * static_cast<double>((n % 5) + 1) / 5.0;
    const Vec3 pos{
      cx + std::cos(a) * rx * ring,
      baseY + 0.08 * static_cast<double>(n % 7),
      cz + std::sin(a) * rz * ring
    };
    const int channelSlot = n % 3;
    const int age = channelSlot == 0 ? 0 : (channelSlot == 1 ? 2 : 6);
    const double speed = channelSlot == 2 ? 0.18 : (channelSlot == 1 ? 0.72 : 1.65);
    const double lift = channelSlot == 2 ? 0.08 : 0.35 + 0.12 * (n % 4);
    const Vec3 vel{std::cos(a) * speed, lift, std::sin(a) * speed};
    sim.escaped_droplets.add(pos, vel, 0, 1.0);
    sim.escaped_droplet_ages.push_back(age);
  }

  for (int n = 0; n < bubbleCount; ++n) {
    const double a = 2.0 * pi * (static_cast<double>(n) / std::max(1, bubbleCount)) - phase;
    const Vec3 pos{
      cx + std::cos(a) * rx * 0.28,
      bounds.min.y + 0.25 + 0.12 * static_cast<double>(n % 6),
      cz + std::sin(a) * rz * 0.28
    };
    sim.escaped_bubbles.add(pos, Vec3{0.0, 0.22, 0.0}, 1, 0.75);
    sim.escaped_bubble_ages.push_back(0);
  }
}

} // namespace

int main(int argc, char** argv) {
  const char* kind = argString(argc, argv, "--kind", "sparse");
  const char* scene = argString(argc, argv, "--scene", "bubble");
  const bool sparseKind = std::strcmp(kind, "sparse") == 0;
  const bool mrKind = std::strcmp(kind, "mr") == 0;
  const bool bubbleScene = sceneIsBubble(scene);
  const bool damBreakScene = sceneIsDamBreak(scene);
  const bool fallingWaterScene = sceneIsFallingWater(scene);
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
  const int secondaryDemoParticles = argInt(argc, argv, "--secondary-demo-particles", 0);

  if ((!sparseKind && !mrKind) ||
      (!bubbleScene && !damBreakScene && !fallingWaterScene) ||
      nx < 4 || ny < 4 || nz < 4 ||
      steps <= 0 || every <= 0 ||
      dt <= 0.0 || cgIters < 0 ||
      secondaryDemoParticles < 0 ||
      std::strlen(prefix) == 0 ||
      manifestPath.empty()) {
    usage();
    return 2;
  }
  if (mrKind && !bubbleScene) {
    std::fprintf(stderr, "export_render_cache3d: --kind mr currently supports only --scene bubble\n");
    return 2;
  }

  int frameCount = 0;
  std::vector<RenderCacheManifestFrame3D> manifestFrames;
  if (sparseKind) {
    SparseSim3DTP sim(nx, ny, nz, 1.0);
    if (physicsPreset) applyFullPhysicsPreset3D(sim);
    sim.dt = dt;
    sim.cg_iters = cgIters;
    if (fallingWaterScene) {
      sim.initFallingWaterColumn();
    } else if (damBreakScene) {
      sim.initTwoPhaseDamBreak();
    } else {
      sim.initBubbleTank();
    }
    const RenderCacheCamera3D camera =
      defaultRenderCacheCamera3D(sim.grid.nx, sim.grid.ny, sim.grid.nz, sim.grid.dx);
    double simTime = 0.0;
    for (int s = 0; s < steps; ++s) {
      sim.step();
      simTime += sim.effective_dt_last;
      if (s % every == 0 || s == steps - 1) {
        const int frameIndex = frameCount;
        const std::string path = framePath(prefix, frameIndex);
        seedCinematicSecondaries(sim, frameIndex, secondaryDemoParticles);
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
    std::printf("scene=%s\n", canonicalScene(scene));
    std::printf("particles=%zu\n", sim.particles.size());
    std::printf("secondary_droplets=%zu\n", sim.escaped_droplets.size());
    std::printf("secondary_bubbles=%zu\n", sim.escaped_bubbles.size());
    std::printf("secondary_demo_particles=%d\n", secondaryDemoParticles);
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
        seedCinematicSecondaries(sim, frameIndex, secondaryDemoParticles);
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
    std::printf("scene=%s\n", canonicalScene(scene));
    std::printf("particles=%zu\n", sim.particles.size());
    std::printf("secondary_droplets=%zu\n", sim.escaped_droplets.size());
    std::printf("secondary_bubbles=%zu\n", sim.escaped_bubbles.size());
    std::printf("secondary_demo_particles=%d\n", secondaryDemoParticles);
  }

  std::printf("frames=%d\n", frameCount);
  std::printf("status=ok\n");
  return 0;
}
