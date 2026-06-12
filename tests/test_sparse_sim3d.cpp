#include "doctest.h"
#include "driver/sparse_sim3d.h"
#include <algorithm>
#include <cmath>

TEST_CASE("sparse 3D dam-break: stable, count conserved, falls, and stays sparse") {
  SparseSim3D sim(16, 16, 16, 1.0);
  sim.initDamBreak();
  size_t n0 = sim.particles.size();
  CHECK(n0 > 0);

  double my0 = 0.0;
  for (size_t i = 0; i < n0; ++i) my0 += sim.particles.pos[i].y;
  my0 /= n0;

  size_t maxActive = 0;
  for (int step = 0; step < 20; ++step) {
    sim.step();
    maxActive = std::max(maxActive, sim.grid.activeCellBlocks());
  }

  CHECK(sim.particles.size() == n0);
  bool finite = true;
  double my1 = 0.0;
  for (size_t i = 0; i < sim.particles.size(); ++i) {
    const auto& p = sim.particles.pos[i];
    finite = finite && std::isfinite(p.x) && std::isfinite(p.y) && std::isfinite(p.z);
    my1 += p.y;
  }
  my1 /= sim.particles.size();

  CHECK(finite);
  CHECK(my1 < my0);
  CHECK(maxActive > 0);
  CHECK(maxActive < sim.grid.totalCellBlocks());
}
