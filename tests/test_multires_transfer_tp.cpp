#include "doctest.h"
#include "driver/multires_ops2d_tp.h"
#include "grid/multires_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"

#include <set>

TEST_CASE("multires tp p2g: momentum conserved across a coarse-fine boundary") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  PhaseParams pp;
  const double Vp = 1.0;
  Particles2DTP ps;
  ps.add({15.75, 12.5}, {4.0, 1.0}, 0);

  mrP2G_tp(g, ps, pp, Vp);

  double mx = 0.0;
  for (const MRFaceKey& f : g.uFaces()) {
    mx += static_cast<double>(g.gu(f)) * static_cast<double>(g.gmu(f));
  }
  CHECK(mx == doctest::Approx(pp.rho_l * Vp * 4.0).epsilon(1e-6));

  double my = 0.0;
  for (const MRFaceKey& f : g.vFaces()) {
    my += static_cast<double>(g.gv(f)) * static_cast<double>(g.gmv(f));
  }
  CHECK(my == doctest::Approx(pp.rho_l * Vp * 1.0).epsilon(1e-6));
}

TEST_CASE("multires tp g2p: typed alpha still blends FLIP and PIC") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid2D<8> g(layout);
  MRMacGrid2D<8> saved(layout);

  for (const MRFaceKey& f : g.uFaces()) {
    g.u(f) = 5.0f;
    saved.u(f) = 2.0f;
  }

  Particles2DTP ps;
  ps.add({12.5, 12.5}, {10.0, 0.0}, 0);
  ps.add({12.5, 12.5}, {10.0, 0.0}, 1);

  mrG2P_tp(g, ps, saved, 1.0, 0.0);

  CHECK(ps.vel[0].x == doctest::Approx(13.0).epsilon(1e-6));
  CHECK(ps.vel[1].x == doctest::Approx(5.0).epsilon(1e-6));
}

TEST_CASE("multires tp p2g: odd boundary writes only enumerated face keys") {
  MRLayout2D<8> layout(29, 31, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(7, 5, 19, 23);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  std::vector<MRFaceKey> ufaces = g.uFaces();
  std::vector<MRFaceKey> vfaces = g.vFaces();
  std::set<MRFaceKey> ukeys(ufaces.begin(), ufaces.end());
  std::set<MRFaceKey> vkeys(vfaces.begin(), vfaces.end());

  PhaseParams pp;
  Particles2DTP ps;
  ps.add({18.75, 17.25}, {2.0, -3.0}, 0);
  ps.add({7.25, 5.5}, {-1.0, 4.0}, 1);

  mrP2G_tp(g, ps, pp, 1.0);

  for (const auto& kv : g.ufield) {
    CHECK(ukeys.count(kv.first) == 1);
  }
  for (const auto& kv : g.mu) {
    CHECK(ukeys.count(kv.first) == 1);
  }
  for (const auto& kv : g.vfield) {
    CHECK(vkeys.count(kv.first) == 1);
  }
  for (const auto& kv : g.mv) {
    CHECK(vkeys.count(kv.first) == 1);
  }

  CHECK(g.mu.count(MRFaceKey{0, 30, 17, 1}) == 0);
  CHECK(g.mv.count(MRFaceKey{1, 18, 32, 1}) == 0);
}
