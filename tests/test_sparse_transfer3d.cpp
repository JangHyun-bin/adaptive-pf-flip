#include "doctest.h"
#include "driver/sparse_ops3d.h"
#include "grid/sparse_mac_grid3d.h"
#include "particles/particles3d.h"

TEST_CASE("sparse p2g3d single particle at u-node gives vx") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0);
  Particles3D ps;
  ps.add({2.0, 1.5, 1.5}, {3.0, -7.0, 2.0});

  spP2G3D(g, ps);

  CHECK(g.gu(2, 1, 1) == doctest::Approx(3.0));
  CHECK(g.gmu(2, 1, 1) == doctest::Approx(1.0));
  CHECK(g.uf.activeBlockCount() < g.uf.totalBlocks());
}

TEST_CASE("sparse p2g3d conserves x-momentum across split") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0);
  Particles3D ps;
  ps.add({2.5, 1.5, 1.5}, {4.0, 0.0, 0.0});

  spP2G3D(g, ps);

  double mom = g.gu(2, 1, 1) * g.gmu(2, 1, 1) + g.gu(3, 1, 1) * g.gmu(3, 1, 1);
  CHECK(mom == doctest::Approx(4.0));
}

TEST_CASE("sparse g2p3d supports PIC and FLIP blend") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0), saved(8, 8, 8, 1.0);
  for (int k = 1; k <= 2; ++k) {
    for (int j = 1; j <= 2; ++j) {
      for (int i = 2; i <= 3; ++i) {
        g.u(i, j, k) = 5.0f;
        saved.u(i, j, k) = 2.0f;
      }
    }
  }
  Particles3D ps;
  ps.add({2.0, 2.0, 2.0}, {10.0, 0.0, 0.0});

  spG2P3D(g, ps, saved, 1.0);
  CHECK(ps.vel[0].x == doctest::Approx(13.0));

  ps.vel[0] = {10.0, 0.0, 0.0};
  spG2P3D(g, ps, saved, 0.0);
  CHECK(ps.vel[0].x == doctest::Approx(5.0));
}
