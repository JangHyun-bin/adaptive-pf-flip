#include "driver/multires_sim3d_tp.h"
#include "driver/viz_multires3d_tp.h"

#include <algorithm>
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

} // namespace

int main(int argc, char** argv) {
  int steps = argInt(argc, argv, "--steps", 120);
  int every = std::max(1, argInt(argc, argv, "--every", 5));
  int scale = std::max(1, argInt(argc, argv, "--scale", 6));

  MRSim3DTP sim(12, 18, 12, 1.0);
  sim.initBubbleTankInterfaceBand();
  for (int s = 0; s < steps; ++s) {
    sim.step();
    if (s % every == 0) {
      char name[80];
      std::snprintf(name, sizeof(name), "mrb3_%03d.ppm", s / every);
      writeMR3DTPPM(sim, name, scale);
    }
  }
  std::printf("done: %zu particles, pressure cells %d/%d\n",
              sim.particles.size(), sim.activePressureCellCount(), sim.layout.nx * sim.layout.ny * sim.layout.nz);
  return 0;
}
