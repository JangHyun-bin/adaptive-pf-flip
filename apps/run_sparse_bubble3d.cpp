#include "driver/sparse_sim3d_tp.h"
#include "driver/viz_phase3d.h"

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace {
int argInt(int argc, char** argv, const char* key, int fallback) {
  for (int i = 1; i + 1 < argc; ++i) if (std::strcmp(argv[i], key) == 0) return std::atoi(argv[i + 1]);
  return fallback;
}
}

int main(int argc, char** argv) {
  int steps = argInt(argc, argv, "--steps", 220);
  int every = std::max(1, argInt(argc, argv, "--every", 5));
  int scale = std::max(1, argInt(argc, argv, "--scale", 6));

  SparseSim3DTP sim(32, 48, 32, 1.0);
  sim.cg_iters = 900;
  sim.initBubbleTank();
  size_t maxActive = 0;
  for (int s = 0; s < steps; ++s) {
    sim.step();
    maxActive = std::max(maxActive, sim.grid.activeCellBlocks());
    if (s % every == 0) {
      char name[80];
      std::snprintf(name, sizeof(name), "spb3_%03d.ppm", s / every);
      writePhaseSlice(sim, name, scale);
    }
  }
  std::printf("done: %zu particles, max active blocks %zu/%zu\n",
              sim.particles.size(), maxActive, sim.grid.totalCellBlocks());
  return 0;
}
