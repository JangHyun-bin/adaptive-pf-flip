#include "doctest.h"
#include "driver/sparse_ops3d_tp.h"
#include "grid/sparse_mac_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"
#include "transfer/transfer3d_tp.h"

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
