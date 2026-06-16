#include "doctest.h"
#include "driver/sparse_ops3d_tp.h"
#include "grid/sparse_mac_grid3d.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"
#include "transfer/transfer3d_tp.h"
#include <algorithm>
#include <cmath>

TEST_CASE("sparse 3D tp p2g conserves normalized cubic momentum") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0);
  PhaseParams pp;
  double Vp = 1.0;
  Particles3DTP ps;
  ps.add({3.0, 2.5, 2.5}, {4.0, 3.0, 2.0}, 0);

  spP2G3D_tp(g, ps, pp, Vp);

  double momU = 0.0;
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j < g.ny; ++j) {
      for (int i = 0; i <= g.nx; ++i) momU += g.gu(i, j, k) * g.gmu(i, j, k);
    }
  }
  CHECK(momU == doctest::Approx(4.0).epsilon(1e-6));
  CHECK(g.muf.activeBlockCount() > 0);
  CHECK(g.muf.activeBlockCount() < g.muf.totalBlocks());
}

TEST_CASE("sparse 3D tp p2g separates liquid and gas phases") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0);
  PhaseParams pp;
  double Vp = 1.0;
  Particles3DTP ps;
  auto seed = [&](int i, int j, int k, unsigned char t) {
    for (int s = 0; s < 8; ++s) {
      double x = i + 0.25 + 0.5 * (s & 1);
      double y = j + 0.25 + 0.5 * ((s >> 1) & 1);
      double z = k + 0.25 + 0.5 * ((s >> 2) & 1);
      ps.add({x, y, z}, {0.0, 0.0, 0.0}, t);
    }
  };
  for (int k = 1; k < 7; ++k) {
    for (int j = 1; j < 4; ++j) {
      for (int i = 1; i < 7; ++i) seed(i, j, k, 0);
    }
    for (int j = 4; j < 7; ++j) {
      for (int i = 1; i < 7; ++i) seed(i, j, k, 1);
    }
  }
  pp.rho_tilde_0 = calibrateRhoTilde0(pp, Vp);

  spP2G3D_tp(g, ps, pp, Vp);

  CHECK(phiFromRawDensity(g.gmu(4, 2, 3), pp) > 0.8);
  CHECK(phiFromRawDensity(g.gmu(4, 5, 3), pp) < 0.2);
}

TEST_CASE("sparse 3D tp g2p uses phase-specific FLIP alpha") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0), saved(8, 8, 8, 1.0);
  for (int k = 1; k <= 2; ++k) {
    for (int j = 1; j <= 2; ++j) {
      for (int i = 2; i <= 3; ++i) {
        g.u(i, j, k) = 5.0f;
        saved.u(i, j, k) = 2.0f;
      }
    }
  }
  Particles3DTP ps;
  ps.add({2.0, 2.0, 2.0}, {10.0, 0.0, 0.0}, 0);
  ps.add({2.0, 2.0, 2.0}, {10.0, 0.0, 0.0}, 1);

  spG2P3D_tp(g, ps, saved, 1.0, 0.0);

  CHECK(ps.vel[0].x == doctest::Approx(13.0));
  CHECK(ps.vel[1].x == doctest::Approx(5.0));
}

TEST_CASE("sparse 3D tp p2g matches uniform transfer on touched faces") {
  UniformGrid3D dense(8, 8, 8, 1.0);
  SparseMacGrid3D<4> sparse(8, 8, 8, 1.0);
  PhaseParams pp;
  double Vp = 1.0;
  Particles3DTP ps;
  ps.add({3.0, 2.5, 2.5}, {4.0, 3.0, 2.0}, 0);
  ps.add({4.25, 4.0, 3.75}, {-1.0, 0.5, -2.0}, 1);

  p2g_tp(dense, ps, pp, Vp);
  spP2G3D_tp(sparse, ps, pp, Vp);

  double maxMassDiff = 0.0;
  double maxVelDiff = 0.0;
  for (int k = 0; k < sparse.nz; ++k) {
    for (int j = 0; j < sparse.ny; ++j) {
      for (int i = 0; i <= sparse.nx; ++i) {
        maxMassDiff = std::max(maxMassDiff, std::abs(dense.mu[dense.uidx(i, j, k)] - sparse.gmu(i, j, k)));
        maxVelDiff = std::max(maxVelDiff, std::abs(dense.u(i, j, k) - sparse.gu(i, j, k)));
      }
    }
  }
  for (int k = 0; k < sparse.nz; ++k) {
    for (int j = 0; j <= sparse.ny; ++j) {
      for (int i = 0; i < sparse.nx; ++i) {
        maxMassDiff = std::max(maxMassDiff, std::abs(dense.mv[dense.vidx(i, j, k)] - sparse.gmv(i, j, k)));
        maxVelDiff = std::max(maxVelDiff, std::abs(dense.v(i, j, k) - sparse.gv(i, j, k)));
      }
    }
  }
  for (int k = 0; k <= sparse.nz; ++k) {
    for (int j = 0; j < sparse.ny; ++j) {
      for (int i = 0; i < sparse.nx; ++i) {
        maxMassDiff = std::max(maxMassDiff, std::abs(dense.mw[dense.widx(i, j, k)] - sparse.gmw(i, j, k)));
        maxVelDiff = std::max(maxVelDiff, std::abs(dense.w(i, j, k) - sparse.gw(i, j, k)));
      }
    }
  }

  CHECK(maxMassDiff < 1e-6);
  CHECK(maxVelDiff < 1e-6);
}

TEST_CASE("sparse 3D tp advect reports phase boundary clamps") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0);
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j < g.ny; ++j) {
      for (int i = 0; i <= g.nx; ++i) g.u(i, j, k) = 10.0f;
    }
  }
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j <= g.ny; ++j) {
      for (int i = 0; i < g.nx; ++i) g.v(i, j, k) = -10.0f;
    }
  }

  Particles3DTP ps;
  ps.add({7.45, 4.0, 4.0}, {0.0, 0.0, 0.0}, 0);
  ps.add({4.0, 0.55, 4.0}, {0.0, 0.0, 0.0}, 1);

  ParticleEscapeStats3D stats;
  spAdvect3D_tp(ps, g, 0.1, &stats);

  CHECK(ps.pos[0].x == doctest::Approx(7.5).epsilon(1e-12));
  CHECK(ps.pos[1].y == doctest::Approx(0.5).epsilon(1e-12));
  CHECK(stats.clamped_liquid == 1);
  CHECK(stats.clamped_gas == 1);
  CHECK(stats.clamped_x_hi == 1);
  CHECK(stats.clamped_y_lo == 1);
  CHECK(stats.clamped_total() == 2);
}

TEST_CASE("sparse 3D tp advect RK3 follows a linear velocity field") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0);
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j < g.ny; ++j) {
      for (int i = 0; i <= g.nx; ++i) g.u(i, j, k) = static_cast<float>(i);
    }
  }

  Particles3DTP ps;
  ps.add({2.0, 4.0, 4.0}, {0.0, 0.0, 0.0}, 0);

  spAdvect3D_tp(ps, g, 0.1, nullptr, 3);

  const double expected = 2.0 + 0.1 / 6.0 * (2.0 + 4.0 * 2.1 + 2.22);
  CHECK(ps.pos[0].x == doctest::Approx(expected).epsilon(1e-6));
  CHECK(ps.pos[0].y == doctest::Approx(4.0).epsilon(1e-12));
  CHECK(ps.pos[0].z == doctest::Approx(4.0).epsilon(1e-12));
}
