#include "doctest.h"
#include "driver/multires_ops3d_tp.h"
#include "grid/multires_mac_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"

#include <set>
#include <vector>

namespace {

double totalUMomentum(const MRMacGrid3D<4>& g) {
  double mx = 0.0;
  for (const MRFaceKey3D& f : g.uFaces()) {
    mx += static_cast<double>(g.gu(f)) * static_cast<double>(g.gmu(f));
  }
  return mx;
}

double totalVMomentum(const MRMacGrid3D<4>& g) {
  double my = 0.0;
  for (const MRFaceKey3D& f : g.vFaces()) {
    my += static_cast<double>(g.gv(f)) * static_cast<double>(g.gmv(f));
  }
  return my;
}

double totalWMomentum(const MRMacGrid3D<4>& g) {
  double mz = 0.0;
  for (const MRFaceKey3D& f : g.wFaces()) {
    mz += static_cast<double>(g.gw(f)) * static_cast<double>(g.gmw(f));
  }
  return mz;
}

} // namespace

TEST_CASE("multires 3D tp p2g: momentum conserved across a coarse-fine boundary") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 8, 12, 12);
  layout.enforceTwoToOneBalance();
  MRMacGrid3D<4> g(layout);

  PhaseParams pp;
  const double Vp = 1.0;
  Particles3DTP ps;
  ps.add({7.75, 6.5, 6.5}, {4.0, 1.0, -2.0}, 0);

  mrP2G3D_tp(g, ps, pp, Vp);

  CHECK(totalUMomentum(g) == doctest::Approx(pp.rho_l * Vp * 4.0).epsilon(1e-6));
  CHECK(totalVMomentum(g) == doctest::Approx(pp.rho_l * Vp * 1.0).epsilon(1e-6));
  CHECK(totalWMomentum(g) == doctest::Approx(pp.rho_l * Vp * -2.0).epsilon(1e-6));
}

TEST_CASE("multires 3D tp p2g: gas momentum uses gas density") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);

  PhaseParams pp;
  const double Vp = 2.0;
  Particles3DTP ps;
  ps.add({5.0, 4.5, 6.5}, {-6.0, 3.0, 2.0}, 1);

  mrP2G3D_tp(g, ps, pp, Vp);

  CHECK(totalUMomentum(g) == doctest::Approx(pp.rho_g * Vp * -6.0).epsilon(1e-6));
  CHECK(totalVMomentum(g) == doctest::Approx(pp.rho_g * Vp * 3.0).epsilon(1e-6));
  CHECK(totalWMomentum(g) == doctest::Approx(pp.rho_g * Vp * 2.0).epsilon(1e-6));
}

TEST_CASE("multires 3D tp p2g: dx converts physical particle position to fine coordinates") {
  MRLayout3D<4> layout(16, 16, 16, 0.5);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);

  PhaseParams pp;
  const double Vp = 1.25;
  Particles3DTP ps;
  ps.add({6.0, 2.75, 3.25}, {3.0, -2.0, 5.0}, 0);

  mrP2G3D_tp(g, ps, pp, Vp);

  CHECK(totalUMomentum(g) == doctest::Approx(pp.rho_l * Vp * 3.0).epsilon(1e-6));
  CHECK(totalVMomentum(g) == doctest::Approx(pp.rho_l * Vp * -2.0).epsilon(1e-6));
  CHECK(totalWMomentum(g) == doctest::Approx(pp.rho_l * Vp * 5.0).epsilon(1e-6));
  CHECK(g.gmu(MRFaceKey3D{0, 12, 5, 6, 1, 1}) > 0.0f);
}

TEST_CASE("multires 3D tp g2p: typed alpha still blends FLIP and PIC") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  MRMacGrid3D<4> saved(layout);

  for (const MRFaceKey3D& f : g.uFaces()) {
    g.u(f) = 5.0f;
    saved.u(f) = 2.0f;
  }

  Particles3DTP ps;
  ps.add({6.5, 6.5, 6.5}, {10.0, 0.0, 0.0}, 0);
  ps.add({6.5, 6.5, 6.5}, {10.0, 0.0, 0.0}, 1);

  mrG2P3D_tp(g, ps, saved, 1.0, 0.0);

  CHECK(ps.vel[0].x == doctest::Approx(13.0).epsilon(1e-6));
  CHECK(ps.vel[1].x == doctest::Approx(5.0).epsilon(1e-6));
}

TEST_CASE("multires 3D tp g2p: samples velocity at particle position") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  MRMacGrid3D<4> saved(layout);

  for (const MRFaceKey3D& f : g.uFaces()) {
    g.u(f) = (f.fineX < 8) ? 2.0f : 10.0f;
    saved.u(f) = g.gu(f);
  }

  Particles3DTP ps;
  ps.add({2.5, 6.5, 6.5}, {0.0, 0.0, 0.0}, 0);
  ps.add({13.5, 6.5, 6.5}, {0.0, 0.0, 0.0}, 0);

  mrG2P3D_tp(g, ps, saved, 0.0, 0.0);

  CHECK(ps.vel[0].x == doctest::Approx(2.0).epsilon(1e-6));
  CHECK(ps.vel[1].x == doctest::Approx(10.0).epsilon(1e-6));
}

TEST_CASE("multires 3D tp p2g: odd boundary writes only enumerated face keys") {
  MRLayout3D<4> layout(17, 10, 9, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 3, 2, 13, 9, 8);
  layout.enforceTwoToOneBalance();
  MRMacGrid3D<4> g(layout);

  std::vector<MRFaceKey3D> ufaces = g.uFaces();
  std::vector<MRFaceKey3D> vfaces = g.vFaces();
  std::vector<MRFaceKey3D> wfaces = g.wFaces();
  std::set<MRFaceKey3D> ukeys(ufaces.begin(), ufaces.end());
  std::set<MRFaceKey3D> vkeys(vfaces.begin(), vfaces.end());
  std::set<MRFaceKey3D> wkeys(wfaces.begin(), wfaces.end());

  PhaseParams pp;
  Particles3DTP ps;
  ps.add({12.75, 8.25, 7.25}, {2.0, -3.0, 1.0}, 0);
  ps.add({4.25, 3.5, 2.5}, {-1.0, 4.0, -2.0}, 1);

  mrP2G3D_tp(g, ps, pp, 1.0);

  for (const auto& kv : g.ufield) CHECK(ukeys.count(kv.first) == 1);
  for (const auto& kv : g.mu) CHECK(ukeys.count(kv.first) == 1);
  for (const auto& kv : g.vfield) CHECK(vkeys.count(kv.first) == 1);
  for (const auto& kv : g.mv) CHECK(vkeys.count(kv.first) == 1);
  for (const auto& kv : g.wfield) CHECK(wkeys.count(kv.first) == 1);
  for (const auto& kv : g.mw) CHECK(wkeys.count(kv.first) == 1);

  CHECK(g.mu.count(MRFaceKey3D{0, 18, 8, 7, 1, 1}) == 0);
  CHECK(g.mv.count(MRFaceKey3D{1, 12, 11, 7, 1, 1}) == 0);
  CHECK(g.mw.count(MRFaceKey3D{2, 12, 8, 10, 1, 1}) == 0);
}

TEST_CASE("multires 3D tp advect: dx scales physical clamp bounds") {
  MRLayout3D<4> layout(16, 16, 16, 0.5);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);

  for (const MRFaceKey3D& f : g.uFaces()) g.u(f) = 10.0f;
  for (const MRFaceKey3D& f : g.vFaces()) g.v(f) = 10.0f;
  for (const MRFaceKey3D& f : g.wFaces()) g.w(f) = 10.0f;

  Particles3DTP ps;
  ps.add({7.70, 7.70, 7.70}, {0.0, 0.0, 0.0}, 0);

  mrAdvect3D_tp(ps, g, 0.1);

  CHECK(ps.pos[0].x == doctest::Approx((layout.nx - 0.5) * layout.dx).epsilon(1e-12));
  CHECK(ps.pos[0].y == doctest::Approx((layout.ny - 0.5) * layout.dx).epsilon(1e-12));
  CHECK(ps.pos[0].z == doctest::Approx((layout.nz - 0.5) * layout.dx).epsilon(1e-12));
}
