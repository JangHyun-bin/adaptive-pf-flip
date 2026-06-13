#include "doctest.h"
#include "driver/multires_sim3d_tp.h"
#include "driver/viz_multires3d_tp.h"

#include <cmath>
#include <cstdio>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

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

std::vector<unsigned char> readP6(const std::string& path, int& W, int& H) {
  std::ifstream f(path, std::ios::binary);
  std::string magic;
  int maxv = 0;
  f >> magic >> W >> H >> maxv;
  f.get();
  std::vector<unsigned char> img(static_cast<size_t>(W * H * 3));
  f.read(reinterpret_cast<char*>(img.data()), static_cast<std::streamsize>(img.size()));
  return img;
}

} // namespace

TEST_CASE("multires 3D viz validates output settings and writes") {
  MRSim3DTP sim(4, 4, 4, 1.0);
  sim.layout.setCoarseEverywhere(1);

  CHECK_THROWS_AS(writeMR3DTPPM(sim, "test_mr3_invalid_scale.ppm", 0), std::invalid_argument);
  CHECK_THROWS_AS(writeMR3DTPPM(sim, "", 2), std::runtime_error);
}

TEST_CASE("multires 3D viz skips negative and out-of-slice particles") {
  const char* path = "test_mr3_slice_skip.ppm";
  std::remove(path);

  MRSim3DTP sim(4, 4, 4, 1.0);
  sim.layout.setCoarseEverywhere(1);
  sim.particles.add({-0.1, 0.5, 2.0}, {0.0, 0.0, 0.0}, 0);
  sim.particles.add({1.5, 1.5, 0.0}, {0.0, 0.0, 0.0}, 1);

  writeMR3DTPPM(sim, path, 2, 0.1);

  int W = 0, H = 0;
  std::vector<unsigned char> img = readP6(path, W, H);
  std::remove(path);

  REQUIRE(W == 8);
  REQUIRE(H == 8);
  int o = (0 + W * 6) * 3;
  CHECK(img[o] == 28);
  CHECK(img[o + 1] == 32);
  CHECK(img[o + 2] == 48);
}

TEST_CASE("multires 3D viz writes in-slice liquid and gas particles") {
  const char* path = "test_mr3_slice_particles.ppm";
  std::remove(path);

  MRSim3DTP sim(4, 4, 4, 1.0);
  sim.layout.setCoarseEverywhere(0);
  sim.particles.add({1.5, 1.5, 2.0}, {0.0, 0.0, 0.0}, 0);
  sim.particles.add({2.5, 1.5, 2.0}, {0.0, 0.0, 0.0}, 1);

  writeMR3DTPPM(sim, path, 2, 0.1);

  int W = 0, H = 0;
  std::vector<unsigned char> img = readP6(path, W, H);
  std::remove(path);

  REQUIRE(W == 8);
  REQUIRE(H == 8);
  int liquid = (3 + W * 4) * 3;
  int gas = (5 + W * 4) * 3;
  CHECK(img[liquid] == 60);
  CHECK(img[liquid + 1] == 140);
  CHECK(img[liquid + 2] == 230);
  CHECK(img[gas] == 235);
  CHECK(img[gas + 1] == 160);
  CHECK(img[gas + 2] == 60);
}

TEST_CASE("multires 3D bubble tank initializes refined lower band and coarse headspace") {
  MRSim3DTP sim(8, 12, 8, 1.0);
  sim.initBubbleTankInterfaceBand();

  CHECK(sim.layout.countLevel(0) > 0);
  CHECK(sim.layout.countLevel(1) > 0);
  CHECK(sim.particles.size() > 0);
  CHECK(meanY(sim, 1) > 0.0);
  CHECK(sim.activePressureCellCount() < 8 * 12 * 8);
  CHECK(sim.uFaceCount() > 0);
  CHECK(sim.vFaceCount() > 0);
  CHECK(sim.wFaceCount() > 0);
}

TEST_CASE("multires 3D dynamic refinement follows particle occupancy") {
  MRSim3DTP sim(16, 16, 16, 1.0);
  sim.dynamic_particle_padding = 0;
  sim.dynamic_gas_padding = 1;
  sim.particles.add({2.5, 2.5, 2.5}, {0.0, 0.0, 0.0}, 0);
  sim.particles.add({3.5, 2.5, 2.5}, {0.0, 0.0, 0.0}, 1);

  sim.updateDynamicRefinement();

  CHECK(sim.layout.leafAtFineCell(2, 2, 2).level == 0);
  CHECK(sim.layout.leafAtFineCell(14, 14, 14).level == 1);
  CHECK(sim.grid.layout.leaves() == sim.layout.leaves());

  sim.particles.pos[0] = {13.5, 13.5, 13.5};
  sim.particles.pos[1] = {12.5, 13.5, 13.5};
  sim.updateDynamicRefinement();

  CHECK(sim.layout.leafAtFineCell(13, 13, 13).level == 0);
  CHECK(sim.layout.leafAtFineCell(2, 2, 2).level == 1);
  CHECK(sim.grid.layout.leaves() == sim.layout.leaves());
}

TEST_CASE("multires 3D dynamic refinement hysteresis retains small moves") {
  MRSim3DTP sim(16, 16, 16, 1.0);
  sim.dynamic_particle_padding = 0;
  sim.dynamic_gas_padding = 0;
  sim.dynamic_hysteresis_cells = 2;
  sim.particles.add({2.5, 2.5, 2.5}, {0.0, 0.0, 0.0}, 0);

  sim.updateDynamicRefinement();
  size_t initialLeaves = sim.layout.countLevel(0);

  sim.particles.pos[0] = {4.5, 2.5, 2.5};
  sim.updateDynamicRefinement();

  CHECK(sim.dynamic_retained_box_valid);
  CHECK(sim.layout.countLevel(0) == initialLeaves);
  CHECK(sim.layout.leafAtFineCell(2, 2, 2).level == 0);
  CHECK(sim.layout.leafAtFineCell(4, 2, 2).level == 0);
}

TEST_CASE("multires 3D dynamic refinement respects fine leaf budget") {
  MRSim3DTP sim(32, 32, 32, 1.0);
  sim.dynamic_particle_padding = 8;
  sim.dynamic_gas_padding = 0;
  sim.dynamic_hysteresis_cells = 0;
  sim.dynamic_max_fine_leaves = 8;
  sim.particles.add({2.5, 2.5, 2.5}, {0.0, 0.0, 0.0}, 0);
  sim.particles.add({29.5, 29.5, 29.5}, {0.0, 0.0, 0.0}, 0);

  sim.updateDynamicRefinement();

  CHECK(sim.dynamic_budget_limited);
  CHECK(sim.dynamic_last_fine_leaves == static_cast<int>(sim.layout.countLevel(0)));
  CHECK(sim.layout.countLevel(0) <= static_cast<size_t>(sim.dynamic_max_fine_leaves));
  CHECK(sim.grid.layout.leaves() == sim.layout.leaves());
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
