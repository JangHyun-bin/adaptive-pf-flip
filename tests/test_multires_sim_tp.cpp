#include "doctest.h"
#include "driver/multires_sim2d_tp.h"
#include "driver/sparse_sim2d_tp.h"

TEST_CASE("multires bubble tank: matches fine sparse rise with fewer pressure cells") {
  SparseSim2DTP fine(48, 48, 1.0);
  fine.initBubbleTank();

  MRSim2DTP mr(48, 48, 1.0);
  mr.initBubbleTankInterfaceBand();

  auto gasMeanYFine = [&]() {
    double s = 0.0;
    int n = 0;
    for (size_t k = 0; k < fine.particles.size(); ++k) {
      if (fine.particles.type[k] == 1) {
        s += fine.particles.pos[k].y;
        ++n;
      }
    }
    return n ? s / n : 0.0;
  };

  auto gasMeanYMR = [&]() {
    double s = 0.0;
    int n = 0;
    for (size_t k = 0; k < mr.particles.size(); ++k) {
      if (mr.particles.type[k] == 1) {
        s += mr.particles.pos[k].y;
        ++n;
      }
    }
    return n ? s / n : 0.0;
  };

  for (int s = 0; s < 30; ++s) {
    fine.step();
    mr.step();
  }

  CHECK(mr.particles.size() == fine.particles.size());
  CHECK(gasMeanYMR() == doctest::Approx(gasMeanYFine()).epsilon(0.15));
  CHECK(mr.activePressureCellCount() < 48 * 48);
}
