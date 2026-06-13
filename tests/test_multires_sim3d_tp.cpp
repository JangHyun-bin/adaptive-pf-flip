#include "doctest.h"
#include "driver/multires_sim3d_tp.h"

#include <cmath>

namespace {

double meanY(const MRSim3DTP& sim, unsigned char type) {
  double sum = 0.0;
  int count = 0;
  for (size_t i = 0; i < sim.particles.size(); ++i) {
    if (sim.particles.type[i] == type) {
      sum += sim.particles.pos[i].y;
      ++count;
    }
  }
  return count ? sum / count : 0.0;
}

bool finiteParticles(const MRSim3DTP& sim) {
  for (size_t i = 0; i < sim.particles.size(); ++i) {
    const auto& p = sim.particles.pos[i];
    if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z)) {
      return false;
    }
  }
  return true;
}

} // namespace

TEST_CASE("multires 3D bubble tank initializes refined lower band and coarse headspace") {
  MRSim3DTP sim(8, 12, 8, 1.0);
  sim.initBubbleTankInterfaceBand();

  CHECK(sim.layout.countLevel(0) > 0);
  CHECK(sim.layout.countLevel(1) > 0);
  CHECK(sim.particles.size() > 0);
  CHECK(meanY(sim, 1) > 0.0);
  CHECK(sim.activePressureCellCount() < 8 * 12 * 8);
}

TEST_CASE("multires 3D bubble tank step conserves particles and stays finite") {
  MRSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.02;
  sim.cg_iters = 120;
  sim.initBubbleTankInterfaceBand();
  size_t n0 = sim.particles.size();
  double gas0 = meanY(sim, 1);

  for (int step = 0; step < 4; ++step) {
    sim.step();
  }

  CHECK(sim.particles.size() == n0);
  CHECK(finiteParticles(sim));
  CHECK(std::isfinite(meanY(sim, 1)));
  CHECK(meanY(sim, 1) >= gas0 - 0.05);
  CHECK(sim.activePressureCellCount() < 8 * 12 * 8);
}
