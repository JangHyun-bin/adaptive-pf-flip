#include "doctest.h"
#include "driver/multires_sim2d_tp.h"
#include "driver/viz_multires_tp.h"
#include "driver/sparse_sim2d_tp.h"

#include <cstdio>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

int markerAtFineCell(const MRSim2DTP& sim, int i, int j) {
  MRCellKey c = sim.grid.marker.cellAtFineCell(i, j);
  return static_cast<int>(sim.grid.marker.get(c) + 0.5f);
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

TEST_CASE("multires viz skips negative particles before pixel cast") {
  const char* path = "test_multires_negative_particle.ppm";
  std::remove(path);

  MRSim2DTP mr(4, 4, 1.0);
  mr.layout.setCoarseEverywhere(1);
  mr.particles.add({-0.1, 0.5}, {0.0, 0.0}, 0);

  writeMRTPPM(mr, path, 2);

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

TEST_CASE("multires viz validates output settings and writes") {
  MRSim2DTP mr(4, 4, 1.0);
  mr.layout.setCoarseEverywhere(1);

  CHECK_THROWS_AS(writeMRTPPM(mr, "test_multires_invalid_scale.ppm", 0), std::invalid_argument);
  CHECK_THROWS_AS(writeMRTPPM(mr, "", 2), std::runtime_error);
}

TEST_CASE("multires bubble tank: boundary-adjacent fluid marker remains fine") {
  MRSim2DTP mr(64, 64, 1.0);
  mr.initBubbleTankInterfaceBand();

  CHECK(mr.layout.leafAtFineCell(63, 1).level == 0);
  CHECK(mr.layout.leafAtFineCell(62, 1).level == 0);
  CHECK(mr.layout.leafAtFineCell(62, 0).level == 0);

  mr.step();

  CHECK(markerAtFineCell(mr, 63, 1) == 2);
  CHECK(markerAtFineCell(mr, 62, 0) == 2);
  CHECK(markerAtFineCell(mr, 62, 1) == 1);
  CHECK(mr.activePressureCellCount() < 64 * 64);
}

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
