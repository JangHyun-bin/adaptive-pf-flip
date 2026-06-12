#include "doctest.h"
#include "driver/sparse_sim3d_tp.h"
#include <algorithm>
#include <cmath>

TEST_CASE("sparse 3D two-phase RT step stays stable") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.03;
  sim.initRayleighTaylor();
  size_t n0 = sim.particles.size();
  CHECK(n0 > 0);

  auto meanY = [&](unsigned char type) {
    double sum = 0.0;
    int count = 0;
    for (size_t i = 0; i < sim.particles.size(); ++i) {
      if (sim.particles.type[i] == type) {
        sum += sim.particles.pos[i].y;
        ++count;
      }
    }
    return count ? sum / count : 0.0;
  };
  double heavy0 = meanY(0);
  double gas0 = meanY(1);
  CHECK(heavy0 > gas0);

  size_t maxActive = 0;
  for (int step = 0; step < 12; ++step) {
    sim.step();
    maxActive = std::max(maxActive, sim.grid.activeCellBlocks());
  }

  CHECK(sim.particles.size() == n0);
  bool finite = true;
  for (size_t i = 0; i < sim.particles.size(); ++i) {
    const auto& p = sim.particles.pos[i];
    finite = finite && std::isfinite(p.x) && std::isfinite(p.y) && std::isfinite(p.z);
  }
  CHECK(finite);
  CHECK(meanY(0) < heavy0);
  CHECK(std::isfinite(meanY(1)));
  CHECK(maxActive > 0);
}

TEST_CASE("sparse 3D two-phase bubble tank rises and keeps headspace sparse") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.03;
  sim.initBubbleTank();
  size_t n0 = sim.particles.size();
  CHECK(n0 > 0);

  auto meanY = [&](unsigned char type) {
    double sum = 0.0;
    int count = 0;
    for (size_t i = 0; i < sim.particles.size(); ++i) {
      if (sim.particles.type[i] == type) {
        sum += sim.particles.pos[i].y;
        ++count;
      }
    }
    return count ? sum / count : 0.0;
  };
  double gas0 = meanY(1);
  CHECK(gas0 > 0.0);

  size_t maxActive = 0;
  for (int step = 0; step < 24; ++step) {
    sim.step();
    maxActive = std::max(maxActive, sim.grid.activeCellBlocks());
  }

  CHECK(sim.particles.size() == n0);
  bool finite = true;
  for (size_t i = 0; i < sim.particles.size(); ++i) {
    const auto& p = sim.particles.pos[i];
    finite = finite && std::isfinite(p.x) && std::isfinite(p.y) && std::isfinite(p.z);
  }
  CHECK(finite);
  CHECK(meanY(1) > gas0 + 0.2);
  CHECK(maxActive > 0);
  CHECK(maxActive < sim.grid.totalCellBlocks());
}
